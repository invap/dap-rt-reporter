# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import dap
import time
from gdb_handler import GDBHandler


class Reporter:
    """Connects DAP client and GDB then uses output to report
    program behaviour.
    """

    def __init__(self) -> None:
        self.gdb_handler = GDBHandler(["gdb", "-i=dap", "-quiet"])
        self.dap_client = dap.Client("GDB")

    def add_executable(self,
                      executable_path: str,
                      execution_trace_log_path: str
                      ) -> None:
        """Saves executable and log files."""

        self.executable_path = executable_path
        self.execution_trace_log_path = execution_trace_log_path

    def initialize(self) -> bytes:
        """Send initialize request to gdb"""

        command = self.dap_client.send()
        response = self.gdb_handler.write(command)

        return response

    def execute(self) -> bytes:
        """Sends launch request to GDB, begins program execution."""

        #Custom request to specify program in gdb launch
        self.dap_client.send_request(command="launch", arguments={"program": self.executable_path})
        command = self.dap_client.send()
        response = self.gdb_handler.write(command)

        return response
