#!/usr/bin/env python3
"""Progress-observable wrapper for v2.py.

Posts one continuously updated PR comment every 60 seconds, writes a local
progress.json checkpoint, emits stdout heartbeats, and enforces a per-source
hard timeout so one broken platform cannot block the entire crawl indefinitely.
"""
from __future__ import annotations

import json
import os
import signal
import sys
import threading
import time
import traceback
from pathlib import Path
from typing import Any, Callable

import requests

import main as base
import v2

LOCK = threading.Lock()
STARTED = time.time()
DONE = threading.Event()
STATE: dict[str, Any] = {
    "status": "starting",
    "current_stage": "初始化",
    "stage_started_at": STARTED,
    "last_real_progress_at": STARTED,
    "stage_detail": "准备运行",
    "completed_sources": [],
    "completed_rows": 0,
    "sitemaps_processed": 0,
    "candidates_found": 0,
    "detail_pages_processed": 0,
    "warnings": [],
}
COMMENT_ID: int | None = None


def event_payload() -> dict[str, Any]:
    path = os.environ.get("GITHUB_EVENT_PATH", "")
    try:
        return json.loads(Path(path).read_text(encoding="utf-8")) if path else {}
    except Exception:
        return {}


def pr_number() -> int | None:
    value = event_payload().get("pull_request", {}).get("number")
    try:
        return int(value) if value is not None else None
    except Exception:
        return None


def run_url() -> str:
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    return f"https://github.com/{repo}/actions/runs/{run_id}" if repo and run_id else ""


def update_state(**kwargs: Any) -> None:
    with LOCK:
        STATE.update(kwargs)
        STATE["last_real_progress_at"] = time.time()


def set_stage(name: str, detail: str = "开始") -> None:
    with LOCK:
        STATE["current_stage"] = name
        STATE["stage_started_at"] = time.time()
        STATE["stage_detail"] = detail
        STATE["last_real_progress_at"] = time.time()
    print(f"[stage] {name}: {detail}", flush=True)


def append_warning(message: str) -> None:
    with LOCK:
        warnings = STATE.setdefault("warnings", [])
        warnings.append(message)
        del warnings[:-8]
        STATE["last_real_progress_at"] = time.time()
    print(f"[warning] {message}", flush=True)


def complete_source(name: str, rows: int, elapsed: float) -> None:
    with LOCK:
        completed = STATE.setdefault("completed_sources", [])
        completed.append({"name": name, "rows": rows, "elapsed_seconds": round(elapsed, 1)})
        del completed[:-18]
        STATE["completed_rows"] = int(STATE.get("completed_rows", 0)) + rows
        STATE["stage_detail"] = f"已完成，{rows}条，耗时{elapsed:.1f}秒"
        STATE["last_real_progress_at"] = time.time()
    print(f"[source-complete] {name}: {rows} rows in {elapsed:.1f}s", flush=True)


def snapshot() -> dict[str, Any]:
    with LOCK:
        state = json.loads(json.dumps(STATE, ensure_ascii=False))
    now = time.time()
    state["elapsed_seconds"] = round(now - STARTED, 1)
    state["stage_elapsed_seconds"] = round(now - float(state.get("stage_started_at", now)), 1)
    state["seconds_since_real_progress"] = round(now - float(state.get("last_real_progress_at", now)), 1)
    state["run_url"] = run_url()
    state["updated_at_epoch"] = now
    return state


def render_comment(final: bool = False) -> str:
    state = snapshot()
    status = "✅ 已完成" if final and state.get("status") == "success" else "❌ 已失败" if final else "🟡 运行中"
    stagnant = state["seconds_since_real_progress"]
    health = "正常"
    if stagnant >= 600:
        health = f"⚠️ 已{int(stagnant // 60)}分钟无真实计数变化"
    elif stagnant >= 300:
        health = f"注意：已{int(stagnant // 60)}分钟无真实计数变化"
    completed = state.get("completed_sources", [])
    rows = ["| 平台 | 条数 | 耗时 |", "|---|---:|---:|"]
    for item in completed[-12:]:
        rows.append(f"| {item['name']} | {item['rows']} | {item['elapsed_seconds']}秒 |")
    warnings = state.get("warnings", [])
    warning_text = "\n".join(f"- {item}" for item in warnings[-6:]) or "- 暂无"
    link = state.get("run_url")
    return f"""<!-- hardware-crawl-progress -->
## 10k硬件机会库实时进度

**状态：{status}**  
**健康状态：{health}**  
**当前阶段：{state.get('current_stage')}**  
**阶段详情：{state.get('stage_detail')}**  
**总耗时：{state['elapsed_seconds']:.0f}秒；当前阶段耗时：{state['stage_elapsed_seconds']:.0f}秒**  
**已完成来源累计：{len(completed)}；已完成来源原始条数：{state.get('completed_rows', 0)}**  
**已处理Sitemap：{state.get('sitemaps_processed', 0)}；已发现候选链接：{state.get('candidates_found', 0)}；已解析详情页：{state.get('detail_pages_processed', 0)}**

{chr(10).join(rows)}

### 最近警告
{warning_text}

[打开GitHub Actions运行]({link})

> 此评论每60秒自动覆盖更新；每处理一个Sitemap、每新增25条候选、每完成一个来源也会刷新内部检查点。单一来源硬超时为12分钟。
"""


def github_api(method: str, path: str, payload: dict[str, Any]) -> requests.Response | None:
    token = os.environ.get("GITHUB_TOKEN", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not token or not repo:
        return None
    url = f"https://api.github.com/repos/{repo}/{path.lstrip('/')}"
    try:
        response = requests.request(
            method,
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            json=payload,
            timeout=20,
        )
        if response.status_code >= 400:
            print(f"[progress-comment] HTTP {response.status_code}: {response.text[:300]}", flush=True)
        return response
    except Exception as exc:
        print(f"[progress-comment] failed: {exc}", flush=True)
        return None


def publish_comment(final: bool = False) -> None:
    global COMMENT_ID
    number = pr_number()
    if number is None:
        return
    body = render_comment(final=final)
    if COMMENT_ID is None:
        response = github_api("POST", f"issues/{number}/comments", {"body": body})
        if response is not None and response.ok:
            try:
                COMMENT_ID = int(response.json()["id"])
            except Exception:
                pass
    else:
        github_api("PATCH", f"issues/comments/{COMMENT_ID}", {"body": body})


def write_checkpoint() -> None:
    out = Path("output_v2")
    out.mkdir(parents=True, exist_ok=True)
    temp = out / "progress.json.tmp"
    temp.write_text(json.dumps(snapshot(), ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(out / "progress.json")


def heartbeat_loop() -> None:
    publish_comment()
    while not DONE.wait(60):
        state = snapshot()
        print(
            "[heartbeat] "
            f"elapsed={state['elapsed_seconds']:.0f}s "
            f"stage={state.get('current_stage')} "
            f"stage_elapsed={state['stage_elapsed_seconds']:.0f}s "
            f"completed_sources={len(state.get('completed_sources', []))} "
            f"rows={state.get('completed_rows', 0)} "
            f"candidates={state.get('candidates_found', 0)}",
            flush=True,
        )
        write_checkpoint()
        publish_comment()


def timeout_handler(signum, frame):  # type: ignore[no-untyped-def]
    raise TimeoutError("single source exceeded 12 minute hard timeout")


def wrap_source(name: str, function: Callable[..., list[base.Record]]) -> Callable[..., list[base.Record]]:
    def wrapped(*args: Any, **kwargs: Any) -> list[base.Record]:
        set_stage(name, "来源采集开始")
        started = time.time()
        previous = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(12 * 60)
        try:
            rows = function(*args, **kwargs)
            complete_source(name, len(rows), time.time() - started)
            return rows
        except TimeoutError as exc:
            append_warning(f"{name}超时，已跳过：{exc}")
            raise
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous)
    return wrapped


def instrumented_fast_source(source: v2.FastSource) -> list[base.Record]:
    set_stage(source.name, "读取Sitemap和列表页")
    candidates: list[str] = []
    queue = list(source.sitemaps)
    visited: set[str] = set()
    while queue and len(visited) < 36 and len(candidates) < source.quota * 5:
        sitemap = queue.pop(0)
        if sitemap in visited:
            continue
        visited.add(sitemap)
        try:
            response = base.HTTP.get(sitemap, timeout=45)
            if response.status_code < 400:
                urls, child_maps = base.xml_urls(response.content)
                queue.extend(child for child in child_maps[:24] if child not in visited)
                for url in urls:
                    normalized = base.canonical_url(url)
                    if v2.matches(source, normalized):
                        candidates.append(normalized)
        except Exception as exc:
            append_warning(f"{source.name} sitemap失败：{type(exc).__name__}")
        update_state(
            sitemaps_processed=int(STATE.get("sitemaps_processed", 0)) + 1,
            candidates_found=int(STATE.get("candidates_found", 0)) + max(0, len(candidates) - int(STATE.get("_source_candidates", 0))),
            _source_candidates=len(candidates),
            stage_detail=f"已处理{len(visited)}个Sitemap，本来源发现{len(candidates)}个候选",
        )
        if len(visited) % 3 == 0:
            print(f"[progress] {source.name}: sitemaps={len(visited)} candidates={len(candidates)}", flush=True)
    for seed in source.seeds:
        try:
            response = base.HTTP.get(seed, timeout=40)
            if response.ok:
                before = len(candidates)
                candidates.extend(base.collect_links(response.text, seed, source.patterns))
                update_state(
                    candidates_found=int(STATE.get("candidates_found", 0)) + max(0, len(candidates) - before),
                    stage_detail=f"列表页补充后，本来源候选{len(candidates)}个",
                )
        except Exception as exc:
            append_warning(f"{source.name}列表页失败：{type(exc).__name__}")

    candidates = list(dict.fromkeys(candidates))
    records: list[base.Record] = []
    set_stage(source.name, f"解析候选详情，共{min(len(candidates), source.quota * 2)}个候选")
    for index, url in enumerate(candidates[: source.quota * 2]):
        record = None
        if index < source.detail_rows:
            record = base.parse_detail(source.name, url)
            update_state(detail_pages_processed=int(STATE.get("detail_pages_processed", 0)) + 1)
        if record is None:
            record = v2.generic_record(source, url)
        records.append(record)
        if len(records) >= source.quota:
            break
        if len(records) % 25 == 0:
            update_state(stage_detail=f"已形成{len(records)}/{source.quota}条记录")
            print(f"[progress] {source.name}: records={len(records)}/{source.quota}", flush=True)
    with LOCK:
        STATE.pop("_source_candidates", None)
    return records


def install_instrumentation() -> None:
    base.fetch_oshwa = wrap_source("OSHWA认证目录", base.fetch_oshwa)
    base.fetch_hackclub = wrap_source("Hack Club项目库", base.fetch_hackclub)
    base.fetch_github = wrap_source("GitHub", base.fetch_github)
    base.fetch_gitlab = wrap_source("GitLab", base.fetch_gitlab)

    original = instrumented_fast_source

    def wrapped_fast(source: v2.FastSource) -> list[base.Record]:
        started = time.time()
        previous = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(12 * 60)
        try:
            rows = original(source)
            complete_source(source.name, len(rows), time.time() - started)
            return rows
        except TimeoutError as exc:
            append_warning(f"{source.name}超时，已跳过：{exc}")
            raise
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous)

    v2.fetch_fast_source = wrapped_fast


def main() -> int:
    install_instrumentation()
    thread = threading.Thread(target=heartbeat_loop, name="progress-heartbeat", daemon=True)
    thread.start()
    code = 1
    try:
        update_state(status="running")
        code = v2.main()
        update_state(status="success" if code == 0 else "failed", stage_detail=f"程序退出码{code}")
        return code
    except Exception as exc:
        append_warning(f"顶层异常：{type(exc).__name__}: {exc}")
        update_state(status="failed", stage_detail="顶层异常")
        traceback.print_exc()
        return 1
    finally:
        DONE.set()
        write_checkpoint()
        publish_comment(final=True)
        thread.join(timeout=3)


if __name__ == "__main__":
    raise SystemExit(main())
