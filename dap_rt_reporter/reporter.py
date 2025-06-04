# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
import time

from dap_rt_reporter.connection_wrapper.connection_wrapper import ConnectionWrapper
from dap_rt_reporter.types import DAPEvent, DAPMessage
from dap_rt_reporter.listener import Listener
from dap_rt_reporter.event.event import Event


class Reporter:
    """Connects DAP client and GDB then uses output to report
    program behavior.
    """

    def __init__(
        self,
        execution_trace_log_path: str,
        connection: ConnectionWrapper,
    ) -> None:
        self.debugger_connection = connection
        self.listener = Listener()

        self.execution_trace_log_path = execution_trace_log_path

        # Used for saving events
        self.events = []

    def execute(self):
        """Begins program execution and report."""

        print("Starting...")

        # Open file writer
        report_file = open(self.execution_trace_log_path, "w")
        csv_writer = csv.writer(report_file, delimiter=",")

        self.debugger_connection.set_up(self._set_up)

        # Start execution
        terminated = False
        while not terminated:
            response = self.debugger_connection.get_response()
            response = Event.parse_dap_response(response)

            # Logic to control program execution
            if response["type"] == DAPMessage.EVENT:
                if response["event"] == DAPEvent.STOPPED:
                    if response["body"]["reason"] == "breakpoint":
                        self.listener.handle_response(
                            int(1e6 * time.time()),
                            response,
                            csv_writer,
                            self.debugger_connection,
                            True,
                        )
                        self.debugger_connection.continue_execution()
                elif response["event"] == DAPEvent.TERMINATED:
                    terminated = True
            elif response["type"] == DAPMessage.RESPONSE:
                pass

        report_file.close()

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
            self.debugger_connection.set_breakpoints_source(
                source_dap_form, lines_dap_form
            )

            # Check breakpoints verification
            # Read all responses until verification is confirmed
            breakpoint_verification = False
            while not breakpoint_verification:
                response = self.debugger_connection.get_response()
                response = Event.parse_dap_response(response)

                if (
                    response["type"] == DAPMessage.RESPONSE
                    and response["command"] == "setBreakpoints"
                ):
                    for breakpoint in response["body"]["breakpoints"]:
                        if not breakpoint["verified"]:
                            raise RuntimeError(
                                f"""Breakpoint verification failed: \n
                                    Source: {breakpoint_id_table[str(breakpoint["id"])]["source_path"]} \n
                                    Line: {breakpoint_id_table[str(breakpoint["id"])]["line"]}"""
                            )
                    breakpoint_verification = True

    def set_event(self, event: Event):
        """Set new event to report."""

        self.events.append(event)

    def close(self):
        self.debugger_connection.close()
