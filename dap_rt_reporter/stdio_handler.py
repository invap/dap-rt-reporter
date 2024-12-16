# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import subprocess
import fcntl
import os

DEFAULT_LAUNCH_COMMAND = ["gdb", "-i=dap", "-quiet"]


class STDIOHandler:
    """STDIO handles the connection to the debugger using standard input-output."""

    def __init__(
        self, executable_name: str, launch_command: list[str] = DEFAULT_LAUNCH_COMMAND
    ) -> None:
        self.launch_command = launch_command

        self.debugger_subprocess = subprocess.Popen(
            self.launch_command + [executable_name],
            shell=False,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Make pipes non blocking
        if (
            self.debugger_subprocess.stdout is not None
            and self.debugger_subprocess.stderr is not None
        ):
            fcntl.fcntl(self.debugger_subprocess.stdout, fcntl.F_SETFL, os.O_NONBLOCK)
            fcntl.fcntl(self.debugger_subprocess.stderr, fcntl.F_SETFL, os.O_NONBLOCK)
        else:
            raise RuntimeError("Invalid state debugger subprocess stdout/stderr is None")

    def write(self, command: bytes, timeout: float = 1):
        if self.debugger_subprocess is not None and self.debugger_subprocess.stdin is not None:
            self.debugger_subprocess.stdin.write(command)
            self.debugger_subprocess.stdin.flush()
            return self._read(timeout)
        else:
            raise RuntimeError("Invalid state debugger subprocess is None")

    def _read(self, timeout: float = 1) -> bytes:
        """Reads from stdout pipe.

        Returns encoded response.
        """
        if self.debugger_subprocess.stdout is None:
            raise RuntimeError("Invalid state debugger subprocess is None")

        # timeout_timer = time.time() + timeout

        debugger_response = []

        # TODO: Replace fixed wait time with smart detection of the encoded output.
        # e.g. reading the end of line of the message or any other frame detection technique
        #
        # Read from pipe until timeout
        # while timeout_timer - time.time() > 0:
        self.debugger_subprocess.stdout.flush()
        encoded_output = self.debugger_subprocess.stdout.read()

        if encoded_output:
            debugger_response.append(encoded_output)

        # TODO: Check for alternative solution
        # Convert responses to single response
        response = "".encode()
        for r in debugger_response:
            response += r

        return response

    def close(self):
        if self.debugger_subprocess.stdout is not None:
            self.debugger_subprocess.stdout.close()

        if self.debugger_subprocess.stdin is not None:
            self.debugger_subprocess.stdin.close()
        if self.debugger_subprocess.stderr is not None:
            self.debugger_subprocess.stderr.close()

        self.debugger_subprocess.terminate()
        self.debugger_subprocess.wait()
