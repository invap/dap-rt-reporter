# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import unittest
from dap_rt_reporter.reporter import Reporter


class TestCheckpointReached(unittest.TestCase):
    def test_checkpoint(self):
        sut = "../rs-rt-mon-dummy-sut/target/debug/deps/checkpoint_init_ok-fdea0cb5f6d80ebc"
        log_path = "checkpoint_init_log_file.log"

        self.reporter = Reporter(
            sut,
            log_path,
        )

        # Set checkpoints
        self.reporter.set_checkpoint(
            source_path="checkpoint_init_ok.rs",
            line=16,
            before=True,
            checkpoint_name="init_chk",
        )

        self.reporter.set_checkpoint(
            source_path="checkpoint_init_ok.rs",
            line=23,
            before=False,
            checkpoint_name="stop_chk",
        )

        print("---------")
        self.reporter.execute()
        self.reporter.stop()


if __name__ == "__main__":
    unittest.main()
