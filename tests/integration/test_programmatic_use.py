# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Test file for programmatic use, this is used in the readme as an example.

import unittest
import csv

from dap_rt_reporter.reporter import Reporter
from dap_rt_reporter.event.checkpoint_reached_event import CheckpointReachedEvent
from dap_rt_reporter.event.variable_value_assigned_event import (
    VariableValueAssignedEvent,
)
from dap_rt_reporter.types import ReportEvent, ReportEventType


class TestProgrammaticUse(unittest.TestCase):
    def test_programmatic_example(self):
        # Binary, log paths and source
        sut_path = "tests/integration/resources/simple_test/target/debug/simple_test"
        execution_log = "tests/integration/programmatic.log"
        source_path = "tests/integration/resources/simple_test/src/main.rs"

        # Initialize reporter
        reporter = Reporter(
            executable_path=sut_path, execution_trace_log_path=execution_log
        )

        # Set checkpoint event on line 12
        reporter.set_event(
            CheckpointReachedEvent(
                source_path=source_path,
                line=12,
                before=True,
                name="test_checkpoint",
            )
        )

        # Set variable value assign event on line 17, reads the value of 'x'
        reporter.set_event(
            VariableValueAssignedEvent(
                source_path=source_path,
                line=17,
                before=True,
                name="var_x",
                expression="x",
            )
        )

        # Start program execution and reporting
        terminated = reporter.execute()
        reporter.close()

        # Build expected log
        events = []
        events.append(
            [
                ReportEventType.PROCESS_EVENT,
                ReportEvent.CHECKPOINT_REACHED,
                "test_checkpoint",
            ]
        )

        for i in range(10):
            events.append(
                [
                    ReportEventType.STATE_EVENT,
                    ReportEvent.VARIABLE_VALUE_ASSIGNED,
                    "var_x",
                    str(2**(i + 1)),
                ]
            )

        # Test if log matches
        with open(execution_log) as log:
            csv_reader = csv.reader(log)

            for row, event in zip(csv_reader, events):
                self.assertTrue(row[1:] == event)

        self.assertTrue(terminated)


if __name__ == "__main__":
    unittest.main()
