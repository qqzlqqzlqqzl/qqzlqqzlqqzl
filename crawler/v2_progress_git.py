#!/usr/bin/env python3
"""GitHub-persistent entrypoint for the observable V2 crawler.

In addition to stdout, local progress.json and the best-effort PR comment, this
entrypoint atomically updates progress/live.json on the dedicated `progress`
branch every heartbeat. It is therefore inspectable while the main job runs.
"""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any

import requests

import v2_progress


ORIGINAL_WRITE_CHECKPOINT = v2_progress.write_checkpoint


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


v2_progress.write_checkpoint = durable_write_checkpoint

# Keep the already-created progress comment as an optional second channel.
v2_progress.COMMENT_ID = 5058787098
v2_progress.pr_number = lambda: 2

# Publish immediately, rather than waiting for the first 60-second heartbeat.
Path("output_v2").mkdir(parents=True, exist_ok=True)
publish_progress_branch()

raise SystemExit(v2_progress.main())
