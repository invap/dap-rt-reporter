# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Test file for add_executable and execute methods.
# Doesn't check if initialize is succesuful
# Should print launch sequence and end with terminate

import os
import unittest
from typing import override

from dap_rt_reporter.rt_reporter import RTReporterBuilder


class TestExecuteProgram(unittest.TestCase):
    """Open and run reporter with no events"""

    def test_start(self):
        sut = (
            "tests/integration/resources/simple_test/target/debug/simple_test"
        )
        output_file = "tests/integration/execute.log"

        reporter = (
            RTReporterBuilder()
            .with_gdb(sut)
            .with_file_writer(output_file)
            .build()
        )

        terminate = reporter.execute()
        reporter.close()

        # Checks if response contains a terminated event
        self.assertTrue(terminate)

    @override
    def tearDown(self):
        try:
            os.remove("tests/integration/execute.log")
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    _ = unittest.main()
