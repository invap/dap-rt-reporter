# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import dap
from gdb_handler import GDBHandler


class Reporter:
    """Connects DAP client and GDB then uses output to report
    program behaviour.
    """

    def __init__(self) -> None:
        self.gdb_handler = None
        self.dap_client = None

    def add_executable(self,
                      executable_path: str,
                      execution_trace_log_path: str
                      ):
        """Saves executable and log files. 
        Sends initialize request to gdb.

        Returns the response from GDB.
        """

        self.executable_path = executable_path
        self.execution_trace_log_path = execution_trace_log_path

        #TODO: Revise this section, check alternatives to declare GDBHandler and dap.Client
        #Create gdb subprocess and DAP client
        self.gdb_handler = GDBHandler(["gdb", self.executable_path,"-i=dap", "-quiet"])
        self.dap_client = dap.Client("GDB")

        self.dap_client.

        #Send initialize request to gdb
        command = self.dap_client.send()
        response = self.gdb_handler.write(command)

        return response

    def execute(self):
        """Sends launch request to GDB, begins program execution."""

        self.dap_client.launch()
        command = self.dap_client.send()
        response = self.gdb_handler.write(command)

        return response
