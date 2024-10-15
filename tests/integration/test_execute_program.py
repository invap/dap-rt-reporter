# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Test file for add_executable and execute methods.
# Doesn't check if initialize is succesuful
# Should print launch sequence and end with terminate

import unittest

from src.connection_wrapper import ConnectionWrapper
from src.reporter import Reporter

class TestExecuteProgram(unittest.TestCase):
    def test_start(self):
        self.connection = ConnectionWrapper()
        self.reporter = Reporter(self.connection)

        # Set main binary as executable, log file is not used
        self.reporter.add_executable("resources/main", "resources/main_log_file.log")

        response = self.reporter.execute()
        response = response.decode()

        self.connection.close_connection()

        #Checks if response contains a terminated event
        self.assertIn("{\"type\": \"event\", \"event\": \"terminated\"", response)

if __name__ == "__main__":
    unittest.main()
