# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Test file for add_executable and execute methods.
# Doesn't check if initialize is succesuful
# Should print launch sequence and end with terminate

import unittest

from dap_rt_reporter.connection_wrapper import ConnectionWrapper
from dap_rt_reporter.reporter import Reporter
from dap_rt_reporter.listener import Listener

class TestExecuteProgram(unittest.TestCase):
    def test_start(self):
        self.connection = ConnectionWrapper()
        self.listener = Listener()
        self.reporter = Reporter(self.connection, self.listener)

        # Set main binary as executable, log file is not used
        self.reporter.add_executable(
            "tests/integration/resources/simple_test/target/debug/simple_test", 
            "main_log_file.log"
            )

        response = self.reporter.execute()
        self.connection.close_connection()

        # Checks if response contains a terminated event
        self.assertTrue(response)

if __name__ == "__main__":
    unittest.main()

