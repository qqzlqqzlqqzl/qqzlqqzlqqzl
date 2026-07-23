#!/usr/bin/env python3
"""Stable entrypoint for the progress-observable V2 crawler."""
from __future__ import annotations

import json
import os
from pathlib import Path

import v2_progress


def fixed_pr_number() -> int | None:
    explicit = os.environ.get("PR_NUMBER", "").strip()
    if explicit.isdigit():
        return int(explicit)
    path = os.environ.get("GITHUB_EVENT_PATH", "")
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8")) if path else {}
    except Exception:
        payload = {}
    value = payload.get("number") or payload.get("pull_request", {}).get("number")
    try:
        return int(value) if value is not None else None
    except Exception:
        return None


v2_progress.pr_number = fixed_pr_number
explicit_comment_id = os.environ.get("PROGRESS_COMMENT_ID", "").strip()
if explicit_comment_id.isdigit():
    v2_progress.COMMENT_ID = int(explicit_comment_id)

raise SystemExit(v2_progress.main())
