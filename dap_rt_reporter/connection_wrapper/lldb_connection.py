# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import dap
from dap_rt_reporter.connection_wrapper.stdio_handler import STDIOHandler
from dap_rt_reporter.connection_wrapper.connection_wrapper import ConnectionWrapper

import subprocess


class LLDBConnection(ConnectionWrapper):
    def __init__(self, executable, executable_args):
        super().__init__(executable, executable_args)

        self.launch_command = ["lldb-dap-19"]

        # Load the scripts to imitate rust-lldb
        rustc_sysroot = (
            subprocess.run(["rustc", "--print", "sysroot"], capture_output=True)
            .stdout.decode()
            .rstrip("\n")
        )
        self.script_import = (
            f'command script import "{rustc_sysroot}/lib/rustlib/etc/lldb_lookup.py"'
        )
        self.commands_file = f"{rustc_sysroot}/lib/rustlib/etc/lldb_commands"

        self.stdio_handler = STDIOHandler(self.launch_command)
        self.dap_client = dap.Client("DAP Client")

        self.response_buffer = b""

    def _send(self):
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
        self.initialize()
        self.launch()
        set_up()
        self.configuration_done()

    def initialize(self):
        self._send()

    def launch(self):
        # Custom launch request
        self.dap_client.send_request(
            command="launch",
            arguments={
                "program": self.executable,
                "disableASLR": False,
                "initCommands": [
                    "settings set target.disable-aslr false",
                    f"command script import {self.script_import}",
                    f"command source -s 0 {self.commands_file}",
                ],
            },
        )
        self._send()

    def configuration_done(self):
        self.dap_client.configuration_done()
        self._send()

    def set_breakpoints_source(self, source, breakpoints):
        self.dap_client.set_breakpoints(source=source, breakpoints=breakpoints)
        self._send()

    def continue_execution(self):
        self.dap_client.continue_(thread_id=0, single_thread=False)
        self._send()

    def next(self):
        self.dap_client.next(thread_id=0)
        self._send()

    def evaluate(self, expression, frame_id):
        self.dap_client.evaluate(expression=expression, frame_id=frame_id)
        self._send()

    def stack_trace(self, thread_id):
        self.dap_client.stack_trace(thread_id=thread_id, start_frame=0, levels=1)
        self._send()

    def close(self):
        self.stdio_handler.close()
