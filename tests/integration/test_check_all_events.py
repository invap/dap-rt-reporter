# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Test file for event testing.
# Run the example program using every type of event.
# Check if output file is consistent with the events.

import unittest
import csv
import subprocess

from dap_rt_reporter.types import ReportEventType, ReportEvent

class TestCheckAllEvents(unittest.TestCase):
    def test_events(self):
        executable_path = (
            "tests/integration/resources/simple_test/target/debug/simple_test"
        )
        conf_file = "tests/integration/resources/simple_test_config.csv"
        execution_log = "tests/integration/resources/all_events.log"

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
                "-f"
            ]
        )

        events = []

        x = 1
        y = 1
        events.append([ReportEventType.STATE_EVENT, ReportEvent.VARIABLE_VALUE_ASSIGNED, "var_x", str(x)])
        events.append([ReportEventType.STATE_EVENT, ReportEvent.VARIABLE_VALUE_ASSIGNED, "var_y", str(y)])
        events.append([ReportEventType.TIMED_EVENT, ReportEvent.CLOCK_START, "sleep_clk"])
        events.append([ReportEventType.TIMED_EVENT, ReportEvent.CLOCK_PAUSE, "sleep_clk"])
        for i in range(10):
            events.append([ReportEventType.PROCESS_EVENT, ReportEvent.TASK_STARTED, "loop"])
            x *= 2
            y *= 3
            events.append([ReportEventType.STATE_EVENT, ReportEvent.VARIABLE_VALUE_ASSIGNED, "var_x", str(x)])
            events.append([ReportEventType.STATE_EVENT, ReportEvent.VARIABLE_VALUE_ASSIGNED, "var_y", str(y)])
            events.append([ReportEventType.PROCESS_EVENT, ReportEvent.CHECKPOINT_REACHED, "chk_sleep"])
            events.append([ReportEventType.TIMED_EVENT, ReportEvent.CLOCK_RESET, "sleep_clk"])
            events.append([ReportEventType.TIMED_EVENT, ReportEvent.CLOCK_RESUME, "sleep_clk"])
            events.append([ReportEventType.COMPONENT_EVENT, "component", "component_func", str(x), str(y)])
            events.append([ReportEventType.TIMED_EVENT, ReportEvent.CLOCK_PAUSE, "sleep_clk"])
            events.append([ReportEventType.PROCESS_EVENT, ReportEvent.TASK_FINISHED, "loop"])

        with open(execution_log) as log:
            csv_reader = csv.reader(log)

            it = 0
            for row in csv_reader:
                self.assertTrue(row[1:] == events[it])
                it += 1

if __name__ == "__main__":
    unittest.main()
