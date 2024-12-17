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
        self.reporter = Reporter(
            executable_path="tests/integration/resources/simple_test/target/debug/simple_test",
            execution_trace_log_path="execute.log"
            )

        terminate = self.reporter.execute()
        self.reporter.close()

        # Checks if response contains a terminated event
        self.assertTrue(terminate)

if __name__ == "__main__":
    unittest.main()

