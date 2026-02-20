# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Test file for programmatic use, this is used in the readme as an example.

import unittest
import csv
import os

from dap_rt_reporter.rt_reporter import RTReporterBuilder
from dap_rt_reporter.event.checkpoint_reached_event import (
    CheckpointReachedEvent,
)
from dap_rt_reporter.event.variable_value_assigned_event import (
    VariableValueAssignedEvent,
)


class TestProgrammaticUse(unittest.TestCase):
    """Test the programmatic example used in the README"""

    def test_programmatic_example(self):
        # Binary, log paths and source
        sut = (
            "tests/integration/resources/simple_test/target/debug/simple_test"
        )
        output_file = "tests/integration/programmatic.log"
        source_path = "tests/integration/resources/simple_test/src/main.rs"
        # Initialize reporter
        reporter = (
            RTReporterBuilder()
            .with_gdb(sut, source_path)
            .with_file_writer(output_file)
            .build()
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

        # Test if log matches
        current_output = []

        with open(output_file) as log:
            csv_reader = csv.reader(log)

            for row in csv_reader:
                current_output.append(row)

        correct_output = []
        with open(
            "tests/integration/resources/test_programmatic_use.csv"
        ) as log:
            csv_reader = csv.reader(log)

            for row in csv_reader:
                correct_output.append(row)

        # Asserts
        self.assertEqual(len(current_output), len(correct_output))

        for i, (row_a, row_b) in enumerate(
            zip(current_output, correct_output)
        ):
            self.assertEqual(
                row_a[1:],
                row_b[1:],
            )

        self.assertTrue(terminated)

    def tearDown(self):
        try:
            os.remove("tests/integration/programmatic.log")
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    unittest.main()
