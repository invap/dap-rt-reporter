# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later


import unittest

from dap_rt_reporter.connection_wrapper import ConnectionWrapper
from dap_rt_reporter.reporter import Reporter
from dap_rt_reporter.listener import Listener


class TestCheckpointReached(unittest.TestCase):
    def test_checkpoint(self):
        self.connection = ConnectionWrapper()
        self.listener = Listener()
        self.reporter = Reporter(self.connection, self.listener)

        # Set main binary as executable, log file is not used
        self.reporter.add_executable(
                "tests/integration/resources/simple_test/target/debug/simple_test", 
                "resources/main_log_file.log"
                )
        
        # Set checkpoints
        self.reporter.set_checkpoint(
            "tests/integration/resources/simple_test/src/main.rs",
            4, 'B', 'Print'
            )
        
        self.reporter.set_checkpoint(
            "tests/integration/resources/simple_test/src/main.rs",
            5, 'B', 'Print after'
            )
        
        response = self.reporter.execute()

        print(response)

        self.connection.close_connection()


if __name__ == "__main__":
    unittest.main()
