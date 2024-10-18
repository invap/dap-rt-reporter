# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Test file for add_executable and execute methods.
# Doesn't check if initialize is succesuful
# Should print launch sequence and end with terminate

import unittest

from dap_rt_reporter.connection_wrapper import ConnectionWrapper
from dap_rt_reporter.reporter import Reporter

class TestExecuteProgram(unittest.TestCase):
    def test_start(self):
        self.connection = ConnectionWrapper()
        self.reporter = Reporter(self.connection)

        # Set main binary as executable, log file is not used
        self.reporter.add_executable(
            "tests/integration/resources/simple_test/target/debug/simple_test", 
            "resources/main_log_file.log"
            )

        response = self.reporter.execute()
        response = response.decode()

        self.connection.close_connection()

        # Checks if response contains a terminated event
        self.assertIn(
            "{\"type\": \"event\", \"event\": \"exited\", \"body\": {\"exitCode\": 0}, ", response
            )

if __name__ == "__main__":
    unittest.main()

