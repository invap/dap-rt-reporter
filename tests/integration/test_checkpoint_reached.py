# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import unittest
import csv

from dap_rt_reporter.reporter import Reporter
from dap_rt_reporter.event.checkpoint_reached_event import CheckpointReachedEvent
from dap_rt_reporter.types import ReportEvent, ReportEventType


class TestCheckpointReached(unittest.TestCase):
    def test_checkpoint(self):
        sut = "tests/integration/resources/simple_test/target/debug/simple_test"
        execution_log = "tests/integration/main_log_file.log"

        self.reporter = Reporter(sut, execution_log)

        # Set checkpoints
        self.reporter.set_event(
            CheckpointReachedEvent(
                source_path="main.rs", line=12, before=True, name="chk_0"
            )
        )

        self.reporter.set_event(
            CheckpointReachedEvent(
                source_path="main.rs", line=16, before=False, name="chk_1"
            )
        )
        self.reporter.set_event(
            CheckpointReachedEvent(
                source_path="main.rs", line=25, before=False, name="chk_2"
            )
        )

        self.reporter.execute()
        self.reporter.close()

        # Build expected log
        events = []

        events.append(
            [ReportEventType.PROCESS_EVENT, ReportEvent.CHECKPOINT_REACHED, "chk_0"]
        )

        for i in range(10):
            events.append(
                [ReportEventType.PROCESS_EVENT, ReportEvent.CHECKPOINT_REACHED, "chk_1"]
            )

        events.append(
            [ReportEventType.PROCESS_EVENT, ReportEvent.CHECKPOINT_REACHED, "chk_2"]
        )

        # Test if log matches
        with open(execution_log) as log:
            csv_reader = csv.reader(log)

            for row, event in zip(csv_reader, events):
                self.assertTrue(row[1:] == event)


if __name__ == "__main__":
    unittest.main()
