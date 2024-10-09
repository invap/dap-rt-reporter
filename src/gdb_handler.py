# Copyright (C) <2024>  INVAP S.E.

import subprocess
import fcntl
import os
import time

DEFAULT_LAUNCH_COMMAND = ["gdb", "-i=dap", "-quiet"]

class GDBHandler:
    """GDBHandler handles the connection between GDB and the Reporter.
    Can be used as standalone to send commands to gdb.
    """
    def __init__(self, 
                 launch_command: str = DEFAULT_LAUNCH_COMMAND
                 ) -> None:
        self.launch_command = launch_command
        self.create_gdb_subprocess()

    def create_gdb_subprocess(self) -> int:
        """Used to create and connect a GDB instance."""

        self.gdb_subprocess = subprocess.Popen(
            self.launch_command,
            shell=False,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        #Make pipes non blocking
        fcntl.fcntl(self.gdb_subprocess.stdout, 
                    fcntl.F_SETFL, 
                    os.O_NONBLOCK
                    )
        fcntl.fcntl(self.gdb_subprocess.stderr, 
                    fcntl.F_SETFL, 
                    os.O_NONBLOCK
                    )
        
        return self.gdb_subprocess.pid
    
    def write(self, command: bytes, timeout: float = 1):
        self.gdb_subprocess.stdin.write(command)
        self.gdb_subprocess.stdin.flush()

        return self._read(timeout)

    def _read(self, timeout: float = 1) -> bytes:
        """Reads from stdout pipe.
        
        Returns encoded response.
        """

        timeout_timer = time.time() + timeout

        gdb_response = []

        #Read from pipe until timeout
        while (timeout_timer - time.time() > 0):
            self.gdb_subprocess.stdout.flush()
            encoded_output = self.gdb_subprocess.stdout.read()

            if encoded_output:
                gdb_response.append(encoded_output)

        #TODO: Check for alternative solution
        #Convert responses to single response
        response = ''.encode()
        for r in gdb_response:
            response += r

        return response