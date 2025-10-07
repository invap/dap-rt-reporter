# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging

import dap

from dap_rt_reporter.connection.connection_wrapper import ConnectionWrapper
from dap_rt_reporter.connection.stdio_handler import STDIOHandler

logger = logging.getLogger(__name__)


class LLDBConnection(ConnectionWrapper):
    """Wrapper for the connection between the DAP client and debugger."""

    def __init__(self, executable: str, executable_args: str) -> None:
        super().__init__(executable, executable_args)
        self.alive = True

        self.launch_command = ["lldb-dap-19"]

        self.stdio_handler = STDIOHandler(self.launch_command)
        self.dap_client = dap.Client("DAP Client")

        self.response_buffer = b""
        self.receive_message_count = 0
        self.send_message_count = 0

    def _send(self):
        """Clears the DAP client buffer and writes the commands to the stdio pipe."""

        command = self.dap_client.send()
        self.stdio_handler.write(command)
        self.send_message_count += 1

    def get_response(self) -> bytes:
        """Gets next response from buffer or debugger. If not alive return empty response."""

        while self.alive:
            if b"\r\n\r\n{" in self.response_buffer:
                length, _ = self.response_buffer.split(b"\r\n\r\n", 1)
                length = int(length.split(b":")[1]) + len(length + b"\r\n\r\n")

                if length <= len(self.response_buffer):
                    response = self.response_buffer[:length]
                    self.response_buffer = self.response_buffer[length:]
                    self.receive_message_count += 1
                    return response

            partial_response = self.stdio_handler.read()
            if partial_response:
                self.response_buffer += partial_response

        return b""

    def initialize(self):
        """Send initialize request."""

        # Client already loads the request so only send is needed
        self._send()

    def launch(self):
        """Sends launch request to debugger."""

        # Custom request for lldb
        self.dap_client.send_request(
            command="launch",
            arguments={
                "program": self.executable,
                "disableASLR": False,
                "initCommands": ["settings set target.disable-aslr false"],
            },
        )
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

        self.dap_client.evaluate(expression=expression, frame_id=frame_id)
        self._send()

    def stack_trace(self, thread_id):
        """Send stack trace request"""

        self.dap_client.stack_trace(thread_id=thread_id, start_frame=0, levels=1)
        self._send()

    def close(self):
        """Kill debugger subprocess."""

        self.stdio_handler.close()
        logger.info("Messages received: %s", self.receive_message_count)
        logger.info("Messages sent: %s", self.send_message_count)
