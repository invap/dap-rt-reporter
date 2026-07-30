# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
import os
import unittest
from typing import override

from dap_rt_reporter.event.checkpoint_reached_event import (
    CheckpointReachedEvent,
)
from dap_rt_reporter.rt_reporter import RTReporterBuilder


class TestCheckpointReached(unittest.TestCase):
    """Run a test that uses three random checkpoints"""

    def test_checkpoint(self):
        sut = (
            "tests/integration/resources/simple_test/target/debug/simple_test"
        )
        execution_log = "tests/integration/checkpoints.log"

        reporter = (
            RTReporterBuilder()
            .with_gdb(sut)
            .with_file_writer(execution_log)
            .build()
        )

        # Set checkpoints
        reporter.set_event(
            CheckpointReachedEvent(
                source_path="main.rs", line=12, before=True, name="chk_0"
            )
        )

        reporter.set_event(
            CheckpointReachedEvent(
                source_path="main.rs", line=16, before=True, name="chk_1"
            )
        )
        reporter.set_event(
            CheckpointReachedEvent(
                source_path="main.rs", line=25, before=True, name="chk_2"
            )
        )

        assert(reporter.execute())
        reporter.close()

        # Test if log matches
        current_output: list[list[str]] = []

        with open(execution_log) as log:
            current_output = list(csv.reader(log))

        correct_output: list[list[str]] = []
        with open(
            "tests/integration/resources/test_checkpoint_reached.csv"
        ) as log:
            csv_reader = csv.reader(log)

            for row in csv_reader:
                correct_output.append(row)

        # Asserts
        self.assertEqual(len(current_output), len(correct_output))

        for _, (row_a, row_b) in enumerate(
            zip(current_output, correct_output)
        ):
            self.assertEqual(
                row_a[1:],
                row_b[1:],
            )

    @override
    def tearDown(self):
        try:
            os.remove("tests/integration/checkpoints.log")
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    _ = unittest.main()
