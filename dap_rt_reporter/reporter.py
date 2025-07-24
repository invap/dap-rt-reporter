# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
import time
import logging

from dap_rt_reporter.connection.lldb_connection import LLDBConnection
from dap_rt_reporter.connection.gdb_connection import GDBConnection
from dap_rt_reporter.types import DAPEvent, DAPMessage
from dap_rt_reporter.listener import Listener
from dap_rt_reporter.event.event import Event
from dap_rt_reporter.rabbitmq_connection import RabbitMQConnection


class Reporter:
    """Connects DAP client and GDB then uses output to report
    program behavior.
    """

    def __init__(
        self,
        executable_path: str,
        execution_trace_log_path: str,
        executable_args: str = "",
        debugger_selection: str = "gdb",
    ) -> None:
        # Use debugger connection gdb/lldb
        self.debugger_selection = debugger_selection
        match self.debugger_selection:
            case "gdb":
                self.debugger_connection = GDBConnection(
                    executable_path, executable_args
                )
            case "lldb":
                self.debugger_connection = LLDBConnection(
                    executable_path, executable_args
                )
            case _:
                raise RuntimeError("Invalid debugger option.")

        # Create listener
        self.listener = Listener()

        self.execution_trace_log_path = execution_trace_log_path

        # Used for saving events
        self.events = []

    def execute(self):
        """Begins program execution and reporting."""

        with open(self.execution_trace_log_path, "w") as report_file:
            csv_writer = csv.writer(report_file, delimiter=",")

            self.debugger_connection.initialize()
            match self.debugger_selection:
                case "gdb":
                    self._set_up()
                    self.debugger_connection.launch()
                case "lldb":
                    self.debugger_connection.launch()
                    self._set_up()

            # Start execution after configuration done is received
            logging.info("Starting SUT execution")
            self.debugger_connection.configuration_done()

            terminated = False
            while not terminated and self.debugger_connection.get_alive():
                response = self.debugger_connection.get_response()
                response = Event.parse_dap_response(response)

                # Logic to control program execution
                if response["type"] == DAPMessage.EVENT:
                    if (
                        response["event"] == DAPEvent.STOPPED
                        and response["body"]["reason"] == "breakpoint"
                    ):
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

        logging.info("Closing reporter")

        return terminated

    def _set_up(self):
        """Sets breakpoints and gives the events to listener."""

        logging.info("Setting breakpoints")
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
            logging.debug("Setting breakpoints for %s", source_dap_form["name"])
            self.debugger_connection.set_breakpoints_source(
                source_dap_form, lines_dap_form
            )

            # Check breakpoints verification
            # Read all responses until verification is confirmed
            breakpoint_verification = False
            while not breakpoint_verification and self.debugger_connection.get_alive():
                response = self.debugger_connection.get_response()
                response = Event.parse_dap_response(response)

                # logging.debug("At breakpoint verification DAP response: %s", response)
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

    def connect_rabbitmq(self, host, port, user, password, exchange):
        rabbitmq_connection = RabbitMQConnection(host, port, user, password, exchange)

        self.listener.set_rabbitmq_connection(rabbitmq_connection)

    def set_event(self, event: Event):
        """Set new event to report."""

        self.events.append(event)

    def kill(self, segnum=0, frame=""):
        """Kill reporter. Stops SUT execution but allow events set up to be completed."""

        logging.debug("Killing reporter at : %s and segnum %d", frame, segnum)
        self.debugger_connection.set_alive(False)

    def close(self):
        logging.info("Closing debugger connection.")
        self.debugger_connection.close()
