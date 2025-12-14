# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import subprocess
import fcntl
import os

from dap_rt_reporter.connection.errors import ReadError, SpawnError, WriteError


class STDIOHandler:
    """Handles the connection to the debugger using STDIO.
    """

    def __init__(self, launch_command: list[str]):
        """Spawn debugger and setup pipes for reading writing.

        Args:
            launch_command (list[str]): Commands for debugger

        Raises:
            SpawnError: Debugger could not be started
        """
        self.launch_command = launch_command

        self.debugger_subprocess = subprocess.Popen(
            self.launch_command,
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
            fcntl.fcntl(
                self.debugger_subprocess.stdout, fcntl.F_SETFL, os.O_NONBLOCK
            )
            fcntl.fcntl(
                self.debugger_subprocess.stderr, fcntl.F_SETFL, os.O_NONBLOCK
            )
        else:
            raise SpawnError(
                "Invalid debugger state subprocess stdout/stderr is None"
            )

    def write(self, command: bytes):
        """Write command to debugger STDIN.

        Args:
            command (bytes): Command for debugger

        Raises:
            WriteError: Subprocess or STDIN are None
        """
        if self.debugger_subprocess and self.debugger_subprocess.stdin:
            self.debugger_subprocess.stdin.write(command)
            self.debugger_subprocess.stdin.flush()
        else:
            raise WriteError("Invalid debugger state subprocess is None")

    def read(self) -> bytes:
        """Reads from debugger STDOUT pipe.

        Raises:
            ReadError: Debugger STDOUT is None

        Returns:
            bytes: Debugger output
        """
        if not self.debugger_subprocess.stdout:
            raise ReadError("Invalid debugger state subprocess stdout pipe is None")

        self.debugger_subprocess.stdout.flush()
        return self.debugger_subprocess.stdout.read()

    def close(self):
        """Attempt to close the debugger politely, if timeout is reached the
        process is killed.
        """
        if self.debugger_subprocess.stdout is not None:
            self.debugger_subprocess.stdout.close()
        if self.debugger_subprocess.stdin is not None:
            self.debugger_subprocess.stdin.close()
        if self.debugger_subprocess.stderr is not None:
            self.debugger_subprocess.stderr.close()

        self.debugger_subprocess.terminate()
        try:
            self.debugger_subprocess.wait(1)
        except subprocess.TimeoutExpired:
            self.debugger_subprocess.kill()
