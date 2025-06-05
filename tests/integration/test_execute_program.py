# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Test file for add_executable and execute methods.
# Doesn't check if initialize is succesuful
# Should print launch sequence and end with terminate

import unittest

from dap_rt_reporter.reporter import Reporter
from dap_rt_reporter.connection_wrapper.gdb_connection import GDBConnection


class TestExecuteProgram(unittest.TestCase):
    def test_start(self):
        self.connection = GDBConnection(
            "tests/integration/resources/simple_test/target/debug/simple_test"
        )
        self.reporter = Reporter(
            execution_trace_log_path="execute.log", connection=self.connection
        )

        terminate = self.reporter.execute()
        self.reporter.close()

        # Checks if response contains a terminated event
        self.assertTrue(terminate)


if __name__ == "__main__":
    unittest.main()
