# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import dap
from dap_rt_reporter.gdb_handler import GDBHandler

class ConnectionWrapper:
    """Wrapper for the connection between the DAP client and GDB."""

    def __init__(self) -> None:
        self.gdb_handler = GDBHandler(["gdb", "-i=dap", "-quiet"])
        self.dap_client = dap.Client("DAP Client")

    def start(self, executable: str) -> bytes:
        """Start DAP-GDB connection."""
        self.gdb_handler.create_gdb_subprocess(executable)

        command = self.dap_client.send()
        response = self.gdb_handler.write(command)

        return response
    
    def launch(self) -> bytes:
        """Sends launch request to GDB, begins program execution."""

        # Custom request to specify program in gdb launch
        #self.dap_client.send_request(
        #    command="launch", arguments={"program": executable_path}
        #)
        self.dap_client.launch()
        command = self.dap_client.send()
        response = self.gdb_handler.write(command)

        return response
    
    def set_breakpoints_source(self, source, breakpoints):
        """Sends set breakpoints in source request, clears all past breakpoints."""

        self.dap_client.set_breakpoints(source=source, breakpoints=breakpoints)
        command = self.dap_client.send()
        response = self.gdb_handler.write(command)

        return response
    
    def continue_execution(self):
        self.dap_client.continue_(0)
        command = self.dap_client.send()
        response = self.gdb_handler.write(command)
        
        return response
    
    def idle(self):
        response = self.gdb_handler._read()

        return response

    def close_connection(self):
        """Kill GDB subprocess."""

        self.gdb_handler.close()