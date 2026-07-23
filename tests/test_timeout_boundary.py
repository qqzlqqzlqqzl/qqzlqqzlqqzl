from __future__ import annotations

import signal
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "crawler"))

import v2_progress_git as target  # noqa: E402


class SourceTimeoutBoundaryTests(unittest.TestCase):
    def test_sentinel_is_not_swallowed_by_exception_handlers(self) -> None:
        def nested_parser() -> None:
            try:
                raise target.SourceHardTimeout("timeout")
            except Exception:  # pragma: no cover - must not catch the sentinel
                self.fail("SourceHardTimeout was swallowed by except Exception")

        with self.assertRaises(target.SourceHardTimeout):
            nested_parser()

    def test_wrapper_converts_sentinel_at_source_boundary(self) -> None:
        def timed_out_source() -> list[object]:
            raise target.SourceHardTimeout("single source exceeded 12 minute hard timeout")

        wrapped = target.strict_wrap_source("test-source", timed_out_source)
        with (
            mock.patch.object(target.signal, "signal", return_value=signal.SIG_DFL),
            mock.patch.object(target.signal, "alarm") as alarm,
            mock.patch.object(target.v2_progress, "set_stage"),
            mock.patch.object(target.v2_progress, "append_warning") as warning,
        ):
            with self.assertRaisesRegex(RuntimeError, "12 minute hard timeout"):
                wrapped()

        alarm.assert_any_call(12 * 60)
        alarm.assert_called_with(0)
        warning.assert_called_once()

    def test_wrapper_preserves_successful_results(self) -> None:
        expected: list[object] = [object(), object()]
        wrapped = target.strict_wrap_source("test-source", lambda: expected)
        with (
            mock.patch.object(target.signal, "signal", return_value=signal.SIG_DFL),
            mock.patch.object(target.signal, "alarm"),
            mock.patch.object(target.v2_progress, "set_stage"),
            mock.patch.object(target.v2_progress, "complete_source") as complete,
        ):
            actual = wrapped()

        self.assertIs(actual, expected)
        complete.assert_called_once()


if __name__ == "__main__":
    unittest.main()
