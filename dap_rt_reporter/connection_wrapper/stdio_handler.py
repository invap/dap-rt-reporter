# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import subprocess
import fcntl
import os


class STDIOHandler:
    """STDIO handles the connection to the debugger using standard input-output."""

    def __init__(self, executable_name: str, launch_command: list[str]):
        self.launch_command = launch_command

        self.debugger_subprocess = subprocess.Popen(
            self.launch_command + [executable_name],
            shell=False,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Make pipes non blocking
        if self.debugger_subprocess.stdout and self.debugger_subprocess.stderr:
            fcntl.fcntl(self.debugger_subprocess.stdout, fcntl.F_SETFL, os.O_NONBLOCK)
            fcntl.fcntl(self.debugger_subprocess.stderr, fcntl.F_SETFL, os.O_NONBLOCK)
        else:
            raise RuntimeError(
                "Invalid state debugger subprocess stdout/stderr is None"
            )

    def write(self, command: bytes):
        if self.debugger_subprocess and self.debugger_subprocess.stdin:
            self.debugger_subprocess.stdin.write(command)
            self.debugger_subprocess.stdin.flush()
        else:
            raise RuntimeError("Invalid state debugger subprocess is None")

    def read(self) -> bytes:
        """Reads from stdout pipe.

        Returns encoded response.
        """
        if not self.debugger_subprocess.stdout:
            raise RuntimeError("Invalid state debugger subprocess is None")

        self.debugger_subprocess.stdout.flush()
        return self.debugger_subprocess.stdout.read()

    def close(self):
        if self.debugger_subprocess.stdout:
            self.debugger_subprocess.stdout.close()
        if self.debugger_subprocess.stdin:
            self.debugger_subprocess.stdin.close()
        if self.debugger_subprocess.stderr:
            self.debugger_subprocess.stderr.close()

        self.debugger_subprocess.terminate()
        self.debugger_subprocess.wait()
