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
        #self.reporter.add_executable(
        #        "tests/integration/resources/simple_test/target/debug/simple_test", 
        #        "main_log_file.log"
        #        )

        self.reporter.add_executable(
            "../rs-rt-mon-dummy-sut/target/debug/deps/checkpoint_init_ok-fdea0cb5f6d80ebc", 
            "checkpoint_init_log_file.log"
            )
        
        # Set checkpoints
        self.reporter.set_checkpoint(
            source_path="checkpoint_nit_ok.rs",
            line=16, 
            before=True, 
            checkpoint_name='init_chk'
            )
        
        self.reporter.set_checkpoint(
            source_path="checkpoint_init_ok.rs",
            line=23, 
            before=False, 
            checkpoint_name='stop_chk'
            )
        
        response = self.reporter.execute()

        print("---------")

        self.connection.close_connection()


if __name__ == "__main__":
    unittest.main()
