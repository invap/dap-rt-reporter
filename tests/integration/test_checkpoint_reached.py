# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import unittest

from dap_rt_reporter.reporter import Reporter
from dap_rt_reporter.event.checkpoint_reached_event import CheckpointReachedEvent


class TestCheckpointReached(unittest.TestCase):
    def test_checkpoint(self):
        sut = "tests/integration/resources/simple_test/target/debug/simple_test"
        log_path = "main_log_file.log"

        self.reporter = Reporter(sut, log_path)

        self.reporter.set_event(
            CheckpointReachedEvent(
                source_path="main.rs", line=7, before=True, name="chk_7"
            )
        )

        self.reporter.set_event(
            CheckpointReachedEvent(
                source_path="main.rs", line=9, before=False, name="chk_9"
            )
        )
        self.reporter.set_event(
            CheckpointReachedEvent(
                source_path="main.rs", line=11, before=False, name="chk_11"
            )
        )

        print("---------")
        print(f"Executing: {sut} output to: {log_path}")
        self.reporter.execute()
        self.reporter.close()


if __name__ == "__main__":
    unittest.main()
