# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
from typing import cast, override

import dap
from dap.types import Source

from dap_rt_reporter.connection.connection_wrapper import ConnectionWrapper
from dap_rt_reporter.connection.errors import (
    DAPRequestError,
    DAPResponseError,
    ReadError,
    SpawnError,
    WriteError,
)
from dap_rt_reporter.connection.stdio_handler import STDIOHandler

logger = logging.getLogger(__name__)


class GDBConnection(ConnectionWrapper):
    """Wrapper for the connection between the DAP client and GDB."""

    def __init__(self, executable: str, executable_args: str = "") -> None:
        """Initialize connection with GDB via DAP.

        Args:
            executable (str): Path to the executable file to debug.
            executable_args (str): Arguments for the executable.

        Raises:
            SpawnError: GDB could not start
        """

        super().__init__(executable, executable_args)
        self.alive: bool = True

        self.launch_command: list[str] = ["gdb", "--i=dap", "--quiet"] + [executable]

        try:
            self.stdio_handler: STDIOHandler = STDIOHandler(self.launch_command)
        except SpawnError as e:
            raise SpawnError(f"GDB spawn error for {executable}") from e

        self.dap_client: dap.Client = dap.Client("DAP Client")

        self.response_buffer: bytes = b""
        self.receive_message_count: int = 0
        self.send_message_count: int = 0

    def _send(self) -> None:
        """Clears the DAP client buffer and writes the commands
        to the stdio pipe.

        Raises:
            WriteError: Error while writing DAP command
        """

        command = self.dap_client.send()
        try:
            self.stdio_handler.write(command)
        except WriteError as e:
            raise WriteError(
                f"Could not send DAP commands number {self.send_message_count} to GDB"
            ) from e
        # TODO: Count individual requests instead of send count for more accuracy
        self.send_message_count += 1

    @override
    def get_response(self) -> bytes:
        """Gets next response from buffer or debugger. If not alive return
        empty response.

        Raises:
            DAPResponseError: Could not read DAP response

        Returns:
            bytes: Complete DAP response.
        """

        while self.alive:
            if b"\r\n\r\n{" in self.response_buffer:
                length, _ = self.response_buffer.split(b"\r\n\r\n", 1)
                length = int(length.split(b":")[1]) + len(length + b"\r\n\r\n")

                if length <= len(self.response_buffer):
                    response = self.response_buffer[:length]
                    self.response_buffer = self.response_buffer[length:]
                    self.receive_message_count += 1
                    return response

            try:
                partial_response = self.stdio_handler.read()
            except ReadError as e:
                raise DAPResponseError("Could not get response from debugger") from e

            if partial_response:
                self.response_buffer += partial_response

        return b""

    @override
    def initialize(self):
        """Send initialize request."""

        try:
            # Client already loads the request so only send is needed
            self._send()
        except ReadError as e:
            raise DAPRequestError("Initialize request could not be sent") from e

    @override
    def launch(self):
        """Sends launch request to debugger."""

        # Custom request to specify program in gdb launch
        _ = self.dap_client.send_request(
            command="launch", arguments={"args": self.executable_args}
        )
        try:
            self._send()
        except ReadError as e:
            raise DAPRequestError("Launch request could not be sent") from e

    @override
    def configuration_done(self):
        """Send configuration done request."""

        _ = self.dap_client.configuration_done()

        try:
            self._send()
        except ReadError as e:
            raise DAPRequestError("Configuration Done request could not be sent") from e

    @override
    def set_breakpoints_source(self, source: str, breakpoints):
        """Send set source breakpoints request,
        clears all past breakpoints for current source."""

        _ = self.dap_client.set_breakpoints(
            source=cast(Source, cast(object, source)), breakpoints=breakpoints
        )

        try:
            self._send()
        except ReadError as e:
            raise DAPRequestError(
                f"Set source breakpoints request could not be sent for source {source}"
            ) from e

    @override
    def continue_execution(self):
        """Send continue command to all threads"""

        _ = self.dap_client.continue_(thread_id=0, single_thread=False)

        try:
            self._send()
        except ReadError as e:
            raise DAPRequestError("Continue request could not be sent") from e

    @override
    def next(self):
        """Send next command for thread id 0."""

        _ = self.dap_client.next(thread_id=0)

        try:
            self._send()
        except ReadError as e:
            raise DAPRequestError("Next request could not be sent") from e

    @override
    def evaluate(self, expression: str, frame_id: int):
        """Sends evaluate command with given expression in current frame."""

        _ = self.dap_client.evaluate(expression=expression, frame_id=0)
        self._send()

    @override
    def stack_trace(self, thread_id: int):
        """Send stack trace request"""

        _ = self.dap_client.stack_trace(thread_id=thread_id)
        self._send()

    @override
    def close(self):
        """Kill debugger subprocess."""

        self.stdio_handler.close()
        logger.info("Messages received: %s", self.receive_message_count)
        logger.info("Messages sent: %s", self.send_message_count)
