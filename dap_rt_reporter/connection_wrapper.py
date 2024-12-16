# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import dap
from dap_rt_reporter.stdio_handler import STDIOHandler


class ConnectionWrapper:
    """Wrapper for the connection between the DAP client and debugger."""

    def __init__(self, executable: str, timeout=1.0) -> None:
        self.timeout = timeout

        self.gdb_handler = STDIOHandler(executable, ["gdb", "-i=dap", "-quiet"])
        self.dap_client = dap.Client("DAP Client")

    def _send(self):
        command = self.dap_client.send()
        response = self.gdb_handler.write(command, self.timeout)

        return response

    def start(self) -> bytes:
        """Start DAP-Debugger connection."""

        return self._send()

    def launch(self) -> bytes:
        """Sends launch request to debugger, begins program execution."""

        # Custom request to specify program in gdb launch
        # self.dap_client.send_request(
        #    command="launch", arguments={"program": executable_path}
        # )
        self.dap_client.launch()
        return self._send()

    def set_breakpoints_source(self, source, breakpoints):
        """Sends set breakpoints in source request, clears all past breakpoints."""

        self.dap_client.set_breakpoints(source=source, breakpoints=breakpoints)
        return self._send()

    def continue_execution(self):
        """Sends continue command at thread id 0."""

        self.dap_client.continue_(thread_id=0, single_thread=False)
        return self._send()

    def next(self):
        """Sends next command to thread id 0."""

        self.dap_client.next(thread_id=0)
        return self._send()

    def idle(self):
        """Reads from buffer."""

        response = self.gdb_handler._read()
        return response

    def evaluate(self, expression):
        """Sends evaluate command with given expression in current frame."""
        self.dap_client.stack_trace(0)
        self.dap_client.evaluate(expression=expression, frame_id=0)
        return self._send()

    def close_connection(self):
        """Kill GDB subprocess."""
        self.gdb_handler.close()
