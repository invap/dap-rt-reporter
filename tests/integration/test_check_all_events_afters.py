# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Test file for event testing.
# Run the example program using every type of events and a mix of
# before and after events. This also checks the interoperability between
# the simple_test_config_afters.csv and simple_test_config.csv files
# which should produce the same results.
# Check if output file is consistent with the events.

import csv
import subprocess
import unittest
import os


class TestCheckAllEvents(unittest.TestCase):
    """Run an integration test that uses all types of events"""

    def test_events(self):
        executable_path = (
            "tests/integration/resources/simple_test/target/debug/simple_test"
        )
        conf_file = "tests/integration/resources/simple_test_config_afters.csv"
        execution_log = "tests/integration/all_events_afters.log"

        # Run dap-rt-reporter
        subprocess.run(
            [
                "python",
                "-m",
                "dap_rt_reporter",
                "--sut",
                executable_path,
                "--cf",
                conf_file,
                "--rf",
                execution_log,
                "-f",
            ]
        )

        # Test if log matches
        current_output = []

        with open(execution_log) as log:
            csv_reader = csv.reader(log)

            for row in csv_reader:
                current_output.append(row)

        correct_output = []
        with open(
            "tests/integration/resources/test_check_all_events.csv"
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

    def tearDown(self):
        try:
            os.remove("tests/integration/all_events_afters.log")
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    unittest.main()
