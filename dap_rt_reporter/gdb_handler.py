# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import subprocess
import fcntl
import os
import time

DEFAULT_LAUNCH_COMMAND = ["gdb", "-i=dap", "-quiet"]


class GDBHandler:
    """GDBHandler handles the connection to GDB.
    Can be used as standalone to send commands to gdb.
    """

    def __init__(
        self, executable_name: str, launch_command: list[str] = DEFAULT_LAUNCH_COMMAND
    ) -> None:
        self.launch_command = launch_command

        self.gdb_subprocess = subprocess.Popen(
            self.launch_command + [executable_name],
            shell=False,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Make pipes non blocking
        if (
            self.gdb_subprocess.stdout is not None
            and self.gdb_subprocess.stderr is not None
        ):
            fcntl.fcntl(self.gdb_subprocess.stdout, fcntl.F_SETFL, os.O_NONBLOCK)
            fcntl.fcntl(self.gdb_subprocess.stderr, fcntl.F_SETFL, os.O_NONBLOCK)
        else:
            raise RuntimeError("Invalid state gdb subprocess stdout/stderr  is None")

    def write(self, command: bytes, timeout: float = 1):
        if self.gdb_subprocess is not None and self.gdb_subprocess.stdin is not None:
            self.gdb_subprocess.stdin.write(command)
            self.gdb_subprocess.stdin.flush()
            return self._read(timeout)
        else:
            raise RuntimeError("Invalid state gdb subprocess is None")

    def _read(self, timeout: float = 1) -> bytes:
        """Reads from stdout pipe.

        Returns encoded response.
        """
        if self.gdb_subprocess.stdout is None:
            raise RuntimeError("Invalid state gdb subprocess is None")

        timeout_timer = time.time() + timeout

        gdb_response = []

        # Read from pipe until timeout
        while timeout_timer - time.time() > 0:
            self.gdb_subprocess.stdout.flush()
            encoded_output = self.gdb_subprocess.stdout.read()

            if encoded_output:
                gdb_response.append(encoded_output)

        # TODO: Check for alternative solution
        # Convert responses to single response
        response = "".encode()
        for r in gdb_response:
            response += r

        return response

    def close(self):
        if self.gdb_subprocess.stdout is not None:
            self.gdb_subprocess.stdout.close()

        if self.gdb_subprocess.stdin is not None:
            self.gdb_subprocess.stdin.close()
        if self.gdb_subprocess.stderr is not None:
            self.gdb_subprocess.stderr.close()

        self.gdb_subprocess.terminate()
        self.gdb_subprocess.wait()
