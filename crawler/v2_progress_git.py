#!/usr/bin/env python3
"""GitHub-persistent entrypoint for the observable V2 crawler.

In addition to stdout and local progress.json, this entrypoint atomically
updates progress/live.json on the dedicated ``progress`` branch every
heartbeat. It also installs a source timeout that cannot be silently swallowed
by broad ``except Exception`` blocks in detail parsers.
"""
from __future__ import annotations

import base64
import json
import os
import signal
import time
from pathlib import Path
from typing import Any, Callable

import requests

import v2_progress


ORIGINAL_WRITE_CHECKPOINT = v2_progress.write_checkpoint


class SourceHardTimeout(BaseException):
    """Escape broad Exception handlers and terminate only the active source."""


def hard_timeout_handler(signum, frame):  # type: ignore[no-untyped-def]
    raise SourceHardTimeout("single source exceeded 12 minute hard timeout")


def strict_wrap_source(
    name: str,
    function: Callable[..., list[v2_progress.base.Record]],
) -> Callable[..., list[v2_progress.base.Record]]:
    """Wrap one source and convert the hard-timeout sentinel at its boundary."""

    def wrapped(*args: Any, **kwargs: Any) -> list[v2_progress.base.Record]:
        v2_progress.set_stage(name, "来源采集开始")
        started = time.time()
        previous = signal.signal(signal.SIGALRM, hard_timeout_handler)
        signal.alarm(12 * 60)
        try:
            rows = function(*args, **kwargs)
            v2_progress.complete_source(name, len(rows), time.time() - started)
            return rows
        except SourceHardTimeout as exc:
            v2_progress.append_warning(f"{name}超时，已跳过：{exc}")
            # v2.run_source catches Exception and records this source as failed,
            # allowing the rest of the crawl to continue.
            raise RuntimeError(str(exc)) from exc
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous)

    return wrapped


def install_strict_instrumentation() -> None:
    """Replace V2 source collectors with hard-timeout-aware wrappers."""

    base = v2_progress.base
    v2 = v2_progress.v2

    base.fetch_oshwa = strict_wrap_source("OSHWA认证目录", base.fetch_oshwa)
    base.fetch_hackclub = strict_wrap_source("Hack Club项目库", base.fetch_hackclub)
    base.fetch_github = strict_wrap_source("GitHub", base.fetch_github)
    base.fetch_gitlab = strict_wrap_source("GitLab", base.fetch_gitlab)

    original = v2_progress.instrumented_fast_source

    def wrapped_fast(source: v2.FastSource) -> list[base.Record]:
        started = time.time()
        previous = signal.signal(signal.SIGALRM, hard_timeout_handler)
        signal.alarm(12 * 60)
        try:
            rows = original(source)
            v2_progress.complete_source(source.name, len(rows), time.time() - started)
            return rows
        except SourceHardTimeout as exc:
            v2_progress.append_warning(f"{source.name}超时，已跳过：{exc}")
            raise RuntimeError(str(exc)) from exc
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous)

    v2.fetch_fast_source = wrapped_fast


def github_headers() -> dict[str, str]:
    token = os.environ.get("GITHUB_TOKEN", "")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def publish_progress_branch() -> None:
    token = os.environ.get("GITHUB_TOKEN", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not token or not repo:
        print("[progress-branch] missing token or repository", flush=True)
        return

    state = v2_progress.snapshot()
    state["heartbeat_schema"] = 1
    state["repository"] = repo
    state["run_id"] = os.environ.get("GITHUB_RUN_ID", "")
    state["run_number"] = os.environ.get("GITHUB_RUN_NUMBER", "")
    state["head_sha"] = os.environ.get("GITHUB_SHA", "")
    payload_bytes = json.dumps(state, ensure_ascii=False, indent=2).encode("utf-8")

    api = f"https://api.github.com/repos/{repo}/contents/progress/live.json"
    headers = github_headers()
    sha = None
    try:
        current = requests.get(api, headers=headers, params={"ref": "progress"}, timeout=20)
        if current.ok:
            sha = current.json().get("sha")
        elif current.status_code != 404:
            print(f"[progress-branch] read HTTP {current.status_code}: {current.text[:200]}", flush=True)
            return

        body: dict[str, Any] = {
            "message": f"progress: heartbeat run {state['run_number']}",
            "content": base64.b64encode(payload_bytes).decode("ascii"),
            "branch": "progress",
        }
        if sha:
            body["sha"] = sha
        response = requests.put(api, headers=headers, json=body, timeout=25)
        if response.status_code >= 400:
            print(f"[progress-branch] write HTTP {response.status_code}: {response.text[:300]}", flush=True)
        else:
            print(
                f"[progress-branch] updated stage={state.get('current_stage')} "
                f"rows={state.get('completed_rows', 0)} candidates={state.get('candidates_found', 0)}",
                flush=True,
            )
    except Exception as exc:
        print(f"[progress-branch] failed: {type(exc).__name__}: {exc}", flush=True)


def durable_write_checkpoint() -> None:
    ORIGINAL_WRITE_CHECKPOINT()
    publish_progress_branch()


def main() -> int:
    """Install GitHub persistence and start the observable crawler."""

    v2_progress.install_instrumentation = install_strict_instrumentation
    v2_progress.write_checkpoint = durable_write_checkpoint

    # Manual workflow runs have no PR context. The progress branch is the
    # durable status channel, so historical PR comments are intentionally not
    # patched on future runs.
    Path("output_v2").mkdir(parents=True, exist_ok=True)
    publish_progress_branch()
    return v2_progress.main()


if __name__ == "__main__":
    raise SystemExit(main())
