# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import dap
from dap_rt_reporter.connection_wrapper.stdio_handler import STDIOHandler
from dap_rt_reporter.connection_wrapper.connection_wrapper import ConnectionWrapper


class GDBConnection(ConnectionWrapper):
    def __init__(self, executable, executable_args):
        super().__init__(executable, executable_args)

        self.launch_command = ["gdb", "-i=dap", "-quiet"]

        self.stdio_handler = STDIOHandler(self.launch_command + [executable])
        self.dap_client = dap.Client("DAP Client")

        self.response_buffer = b""

    def _send(self):
        """Clears the DAP client buffer and writes the commands to the stdio pipe."""

        command = self.dap_client.send()
        self.stdio_handler.write(command)

    def get_response(self) -> bytes:
        while True:
            if b"\r\n\r\n{" in self.response_buffer:
                length, _ = self.response_buffer.split(b"\r\n\r\n", 1)
                length = int(length.split(b":")[1]) + len(length + b"\r\n\r\n")

                if length <= len(self.response_buffer):
                    response = self.response_buffer[:length]
                    self.response_buffer = self.response_buffer[length:]
                    return response
            
            partial_response = self.stdio_handler.read()
            if partial_response:
                self.response_buffer += partial_response

    def set_up(self, set_up):
        """GDB sequence to initiate program execution and debugging."""

        self.initialize()
        set_up()
        self.configuration_done()
        self.launch()

    def initialize(self):
        """Send initialize request."""

        # Client already loads the request so only send is needed
        self._send()

    def launch(self):
        """Send launch request to debugger, begins program execution."""

        # Custom request for gdb
        # self.dap_client.send_request(
        #   command="launch", arguments={"program": self.executable_path}
        # )
        self.dap_client.launch()
        self._send()

    def configuration_done(self):
        """Send configuration done request."""

        self.dap_client.configuration_done()
        self._send()

    def set_breakpoints_source(self, source, breakpoints):
        """Send set breakpoints in source request, clears all past breakpoints."""

        self.dap_client.set_breakpoints(source=source, breakpoints=breakpoints)
        self._send()

    def continue_execution(self):
        """Send continue command at thread id 0."""

        self.dap_client.continue_(thread_id=0, single_thread=False)
        self._send()

    def next(self):
        """Send next command to thread id 0."""

        self.dap_client.next(thread_id=0)
        self._send()

    def evaluate(self, expression, frame_id):
        """Sends evaluate command with given expression in current frame."""
        
        self.dap_client.evaluate(expression=expression, frame_id=0)
        self._send()

    def stack_trace(self, thread_id):
        """Send stack trace request"""

        self.dap_client.stack_trace(thread_id=thread_id)
        self._send()

    def close(self):
        """Kill debugger subprocess."""
        self.stdio_handler.close()
