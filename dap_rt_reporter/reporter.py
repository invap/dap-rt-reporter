# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
import time

from dap_rt_reporter.connection_wrapper import ConnectionWrapper
from dap_rt_reporter.types import DAPEvent, DAPMessage
from dap_rt_reporter.listener import Listener
from dap_rt_reporter.event.event import Event


class Reporter:
    """Connects DAP client and GDB then uses output to report
    program behavior.
    """

    def __init__(
        self,
        executable_path: str,
        execution_trace_log_path: str,
        executable_args: str = "",
    ) -> None:
        self.debugger_connection = ConnectionWrapper(executable_path, executable_args)
        self.listener = Listener()

        self.executable_path = executable_path
        self.execution_trace_log_path = execution_trace_log_path
        self.alive = True

        # Used for saving events
        self.events = []

    def execute(self):
        """Begins program execution and report."""

        with open(self.execution_trace_log_path, "w") as report_file:
            csv_writer = csv.writer(report_file, delimiter=",")

            self.debugger_connection.start()
            self._set_up()

            # Start execution
            print("Starting SUT execution")
            encoded_response = self.debugger_connection.launch()
            terminated = False

            while not terminated and self.alive:
                response_list = Event.parse_dap_response(encoded_response)
                encoded_response = b""

                # Logic to control program execution
                for response in response_list:
                    if response["type"] == DAPMessage.EVENT:
                        if response["event"] == DAPEvent.STOPPED:
                            if response["body"]["reason"] == "breakpoint":
                                self.listener.handle_response(
                                    int(1e6 * time.time()),
                                    response,
                                    csv_writer,
                                    self.debugger_connection,
                                )
                            encoded_response = (
                                self.debugger_connection.continue_execution()
                            )
                        elif response["event"] == DAPEvent.TERMINATED:
                            terminated = True
                    elif response["type"] == DAPMessage.RESPONSE:
                        pass

                if not encoded_response:
                    encoded_response = self.debugger_connection.idle()

        print("Closing reporter.")

        return terminated

    def _set_up(self):
        """Sets breakpoints and gives the events to listener."""

        # Create breakpoint locations
        breakpoint_locations = {}
        for event in self.events:
            # Save breakpoint-event relationships
            line = event.line
            source_path = event.source_path
            if source_path in breakpoint_locations:
                if line in breakpoint_locations[source_path]:
                    breakpoint_locations[source_path][line].append(event)
                else:
                    breakpoint_locations[source_path][line] = [event]
            else:
                breakpoint_locations[source_path] = {line: [event]}

        # Set breakpoints for each source
        breakpoint_id = 1
        breakpoint_id_table = {}
        for source_path in breakpoint_locations:
            # Convert the source and lines to DAP format
            lines_dap_form = []
            for line in breakpoint_locations[source_path]:
                lines_dap_form.append({"line": int(line)})

                breakpoint_id_table[str(breakpoint_id)] = {
                    "source_path": source_path,
                    "line": line,
                }

                # Add events to listener
                for event in breakpoint_locations[source_path][line]:
                    self.listener.add_event(breakpoint_id, event)
                breakpoint_id += 1

            source = source_path[source_path.rfind("/") + 1 :]
            source_dap_form = {"name": source, "path": source_path}

            # Set breakpoints and clear previous ones
            encoded_response = self.debugger_connection.set_breakpoints_source(
                source_dap_form, lines_dap_form
            )

            # Check breakpoints verification
            # Read all responses until verification is confirmed
            breakpoint_verification = False
            while not breakpoint_verification:
                response_list = Event.parse_dap_response(encoded_response)
                for response in response_list:
                    if (
                        response["type"] == DAPMessage.RESPONSE
                        and response["command"] == "setBreakpoints"
                    ):
                        for breakpoint in response["body"]["breakpoints"]:
                            if not breakpoint["verified"]:
                                raise RuntimeError(
                                    f"Breakpoint verification failed: \nSource: {breakpoint_id_table[str(breakpoint['id'])]['source_path']} \nLine: {breakpoint_id_table[str(breakpoint['id'])]['line']}"
                                )
                        breakpoint_verification = True

                encoded_response = self.debugger_connection.idle()

    def kill(self):
        """Kill reporter. Stops SUT execution but allow events set up to be completed."""

        self.alive = False

    def set_event(self, event: Event):
        """Set new event to report."""

        self.events.append(event)

    def close(self):
        self.debugger_connection.close_connection()
