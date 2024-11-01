# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from dap_rt_reporter.connection_wrapper import ConnectionWrapper
from dap_rt_reporter.listener import Listener
from dap_rt_reporter.constants import ReportEvent, DAPMessage, DAPEvent
from dap_rt_reporter.listener_functions import write_checkpoint_reached
import json
import time
import csv


class Reporter:
    """Connects DAP client and GDB then uses output to report
    program behaviour.
    """

    def __init__(
        self,
        executable_path: str,
        execution_trace_log_path: str,
    ) -> None:
        self.debugger_connection = ConnectionWrapper(executable_path)
        self.listener = Listener()

        self.executable_path = executable_path
        self.execution_trace_log_path = execution_trace_log_path

        # Used for saving events
        self.events = []

    def execute(self):
        """Begins program execution and report."""

        report_file = open(self.execution_trace_log_path, "w")
        csv_writer = csv.writer(report_file, delimiter=",")

        self.debugger_connection.start()
        self._set_up()

        # Start execution
        encoded_response = self.debugger_connection.launch()
        terminated = False
        while not terminated:
            # print(encoded_response)
            response_list = self.parse_dap_response(encoded_response)
            encoded_response = None

            # Logic to control program execution
            for response in response_list:
                if response["type"] == DAPMessage.EVENT:
                    if response["event"] == DAPEvent.STOPPED:
                        if response["body"]["reason"] == "breakpoint":
                            self.listener.handle_response(
                                1e6 * time.time(),
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

            if encoded_response is None:
                encoded_response = self.debugger_connection.idle()

        report_file.close()

        return terminated

    def parse_dap_response(self, response: bytes):
        """Converts DAP response to dictionary form.
        Assumes complete message.
        """

        response_list = []
        if response is not None:
            while b"\r\n\r\n" in response:
                length, response = response.split(b"\r\n\r\n", 1)

                length = int(length.split(b":")[1])
                response_list.append(json.loads(response[:length]))
                response = response[length:]

        return response_list

    def _set_up(self):
        """Sets breakpoints and gives the events to listener."""

        # Create breakpoint locations
        breakpoint_locations = {}
        for event in self.events:
            event_values = {
                "before": event["before"],
                "name": event["name"],
                "type": event["type"],
                "args": event["args"],
                "functions": event["functions"],
            }
            line = event["line"]
            source_path = event["source_path"]
            if source_path not in breakpoint_locations:
                breakpoint_locations[source_path] = {str(line): [event_values]}
            else:
                if line not in breakpoint_locations[source_path]:
                    breakpoint_locations[source_path][line] = [event_values]
                else:
                    breakpoint_locations[source_path][line].append([event_values])

        breakpoint_id = 1
        # Set breakpoints for each source
        for source_path in breakpoint_locations:
            # Convert the source and lines to DAP format
            lines_dap_form = []
            for line in breakpoint_locations[source_path]:
                lines_dap_form.append({"line": int(line)})

                # Add events to listener
                for event in breakpoint_locations[source_path][line]:
                    self.listener.add_event(breakpoint_id, event)
                    breakpoint_id += 1

            source = source_path[source_path.rfind("/") + 1 :]
            source_dap_form = {"name": source, "path": source_path}

            encoded_response = self.debugger_connection.set_breakpoints_source(
                source_dap_form, lines_dap_form
            )
            response_list = self.parse_dap_response(encoded_response)

            # print(response_list)
            # Check breakpoints verification
            breakpoint_initialize_fail = False
            output_buffer = []
            for response in response_list:
                if (
                    response["type"] == DAPMessage.RESPONSE
                    and response["command"] == "setBreakpoints"
                ):
                    for breakpoint in response["body"]["breakpoints"]:
                        if not breakpoint["verified"]:
                            breakpoint_initialize_fail = True
                elif (
                    response["type"] == DAPMessage.EVENT
                    and response["event"] == DAPEvent.OUTPUT
                ):
                    output_buffer.append(response["body"]["output"])

            if breakpoint_initialize_fail:
                raise RuntimeError("Breakpoint failed verification: ", output_buffer)

    def set_checkpoint(
        self, source_path: str, line: int, before: bool, checkpoint_name: str
    ) -> None:
        new_checkpoint = {
            "source_path": source_path,
            "line": line,
            "before": before,
            "name": checkpoint_name,
            "type": ReportEvent.CHECKPOINT_REACHED,
            "args": {},
            "functions": [write_checkpoint_reached],
        }
        self.events.append(new_checkpoint)

    def stop(self):
        self.debugger_connection.close_connection()
