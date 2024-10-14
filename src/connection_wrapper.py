# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import dap
from gdb_handler import GDBHandler

class ConnectionWrapper:
    """Wrapper for the connection between the DAP client and GDB."""

    def __init__(self) -> None:
        self.gdb_handler = GDBHandler(["gdb", "-i=dap", "-quiet"])
        self.dap_client = dap.Client("DAP Client")

        self.debugger_specs = self.start()

    def start(self) -> bytes:
        """Start DAP-GDB connection."""

        command = self.dap_client.send()
        response = self.gdb_handler.write(command)

        return response
    
    def launch(self, executable_path) -> bytes:
        """Sends launch request to GDB, begins program execution."""

        # Custom request to specify program in gdb launch
        self.dap_client.send_request(
            command="launch", arguments={"program": executable_path}
        )
        command = self.dap_client.send()
        response = self.gdb_handler.write(command)

        return response