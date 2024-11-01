# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import unittest

from dap_rt_reporter.reporter import Reporter


class TestCheckpointReached(unittest.TestCase):
    def test_checkpoint(self):
        sut = "tests/integration/resources/simple_test/target/debug/simple_test"
        log_path = "main_log_file.log"

        self.reporter = Reporter(sut, log_path)

        # Set checkpoints
        # self.reporter.set_checkpoint(
        #     source_path="lib.rs", line=27, before=True, checkpoint_name="init_chk"
        # )

        self.reporter.set_checkpoint(
            source_path="main.rs", line=6, before=True, checkpoint_name="stop_chk"
        )

        self.reporter.set_checkpoint(
            source_path="main.rs", line=9, before=False, checkpoint_name="chk_9"
        )
        self.reporter.set_checkpoint(
            source_path="main.rs", line=11, before=False, checkpoint_name="chk_11"
        )

        print("---------")
        print(f"Executing: {sut} output to: {log_path}")
        self.reporter.execute()
        self.reporter.stop()


if __name__ == "__main__":
    unittest.main()
