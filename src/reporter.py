# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

class Reporter:
    """Connects DAP client and GDB then uses output to report
    program behaviour.
    """

    # TODO: Add dap wrapper as parameter
    def __init__(self, debugger_connection) -> None:
        self.debugger_connection = debugger_connection

    def add_executable(
            self, executable_path: str, execution_trace_log_path: str
            ) -> None:
        """Saves executable and log files."""

        self.executable_path = executable_path
        self.execution_trace_log_path = execution_trace_log_path

    def execute(self) -> bytes:
        """Sends launch request to GDB, begins program execution."""

        return self.debugger_connection.launch(self.executable_path)
    
    def set_up(self):
        pass

    def set_checkpoint(self):
        pass
