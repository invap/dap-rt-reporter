# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Test file for event testing.
# Run the example program using every type of event.
# Check if output file is consistent with the events.

import unittest
import csv
import subprocess

from dap_rt_reporter.reporter import Reporter


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
            ]
        )

        events_check = True
        with open(execution_log) as log:
            csv_reader = csv.reader(log)
            for row in csv_reader:
                print(row)



if __name__ == "__main__":
    unittest.main()
