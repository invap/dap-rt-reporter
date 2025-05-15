# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Test file for event testing.
# Run the example program using every type of event.
# Check if output file is consistent with the events.

import csv
import subprocess
import unittest

from dap_rt_reporter.types import ReportEvent, ReportEventType


class TestCheckAllEvents(unittest.TestCase):
    def test_events(self):
        executable_path = (
            "tests/integration/resources/simple_test/target/debug/simple_test"
        )
        conf_file = "tests/integration/resources/simple_test_config.csv"
        execution_log = "tests/integration/all_events.log"

        # Run dap-rt-reporter
        subprocess.run(
            [
                "pipx",
                "run",
                "poetry",
                "run",
                "python",
                "-m",
                "dap_rt_reporter",
                "--sut",
                executable_path,
                "--desc",
                conf_file,
                "--log",
                execution_log,
                "-f",
            ]
        )

        # Build expected log
        events = []

        x = 1
        y = 1
        events.append(
            [
                ReportEventType.STATE_EVENT,
                ReportEvent.VARIABLE_VALUE_ASSIGNED,
                "var_x",
                str(x),
            ]
        )
        events.append(
            [
                ReportEventType.STATE_EVENT,
                ReportEvent.VARIABLE_VALUE_ASSIGNED,
                "var_y",
                str(y),
            ]
        )
        events.append(
            [ReportEventType.TIMED_EVENT, ReportEvent.CLOCK_START, "sleep_clk"]
        )
        events.append(
            [ReportEventType.TIMED_EVENT, ReportEvent.CLOCK_PAUSE, "sleep_clk"]
        )
        for i in range(10):
            events.append(
                [
                    ReportEventType.STATE_EVENT,
                    ReportEvent.VARIABLE_VALUE_ASSIGNED,
                    "var_i",
                    str(i),
                ]
            )
            events.append(
                [ReportEventType.PROCESS_EVENT, ReportEvent.TASK_STARTED, "loop"]
            )
            x *= 2
            y *= 3
            events.append(
                [
                    ReportEventType.STATE_EVENT,
                    ReportEvent.VARIABLE_VALUE_ASSIGNED,
                    "var_x",
                    str(x),
                ]
            )
            events.append(
                [
                    ReportEventType.STATE_EVENT,
                    ReportEvent.VARIABLE_VALUE_ASSIGNED,
                    "var_y",
                    str(y),
                ]
            )
            events.append(
                [
                    ReportEventType.PROCESS_EVENT,
                    ReportEvent.CHECKPOINT_REACHED,
                    "loop_inv_chk",
                ]
            )
            events.append(
                [
                    ReportEventType.COMPONENT_EVENT,
                    "component",
                    "component_func",
                    str(x),
                    str(y),
                ]
            )
            events.append(
                [ReportEventType.PROCESS_EVENT, ReportEvent.TASK_FINISHED, "loop"]
            )
            events.append(
                [ReportEventType.TIMED_EVENT, ReportEvent.CLOCK_RESET, "sleep_clk"]
            )
            events.append(
                [ReportEventType.TIMED_EVENT, ReportEvent.CLOCK_PAUSE, "sleep_clk"]
            )
            events.append(
                [
                    ReportEventType.PROCESS_EVENT,
                    ReportEvent.CHECKPOINT_REACHED,
                    "chk",
                ]
            )

        # Test if log matches
        with open(execution_log) as log:
            csv_reader = csv.reader(log)

            for row, event in zip(csv_reader, events):
                self.assertTrue(row[1:] == event)


if __name__ == "__main__":
    unittest.main()
