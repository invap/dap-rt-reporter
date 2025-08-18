# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
import logging
import time

from pika import BasicProperties

from rt_rabbitmq_wrapper.rabbitmq_utility import (
    RabbitMQError,
    connect_to_channel_exchange,
    connect_to_server,
    publish_message,
)

from dap_rt_reporter.connection.gdb_connection import GDBConnection
from dap_rt_reporter.connection.lldb_connection import LLDBConnection
from dap_rt_reporter.event.event import Event
from dap_rt_reporter.listener import Listener
from dap_rt_reporter.rabbitmq_connection.rabbitmq_server_configs import (
    rabbitmq_event_exchange_config,
    rabbitmq_server_config,
)
from dap_rt_reporter.rabbitmq_connection.rabbitmq_server_connections import (
    rabbitmq_event_server_connection,
)
from dap_rt_reporter.types import DAPEvent, DAPMessage


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
        use_rabbitmq: bool = False,
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
        self.use_rabbitmq = use_rabbitmq

        # Used for saving events
        self.events = []

    def execute(self) -> bool:
        """Begins program execution and reporting."""

        if self.use_rabbitmq:
            self.connect_rabbitmq()

        # Open csv file and start execution
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
                # Get response from debugger
                response = self.debugger_connection.get_response()
                response = Event.parse_dap_response(response)

                logging.debug(f"DAP Response: {response}")
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

    def _set_up(self) -> None:
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

    def connect_rabbitmq(self) -> None:
        """Set up connection to the RabbitMQ server and channel
        """

        # Connect to the RabbitMQ server
        try:
            rabbitmq_connection = connect_to_server(rabbitmq_server_config)
        except RabbitMQError:
            logging.critical("Error setting up the connection to the RabbitMQ server.")
            exit(-2)
        # Set up events channel
        try:
            events_channel = connect_to_channel_exchange(
                rabbitmq_server_config=rabbitmq_server_config,
                rabbitmq_exchange_config=rabbitmq_event_exchange_config,
                connection=rabbitmq_connection,
            )
        except RabbitMQError:
            logging.critical("Error setting up the events channel and exchange.")
            exit(-2)

        rabbitmq_event_server_connection.connection = rabbitmq_connection
        rabbitmq_event_server_connection.channel = events_channel
        rabbitmq_event_server_connection.exchange = (
            rabbitmq_event_exchange_config.exchange
        )

    def set_event(self, event: Event) -> None:
        """Set new event to report."""

        self.events.append(event)

    def kill(self, segnum=0, frame="") -> None:
        """Kill reporter. Stops SUT execution but allow events set up to be completed."""

        logging.debug("Killing reporter at : %s and segnum %d", frame, segnum)
        self.debugger_connection.set_alive(False)

    def close(self) -> None:
        logging.info("Closing debugger connection.")
        self.debugger_connection.close()

        if self.use_rabbitmq:
            try:
                publish_message(
                    rabbitmq_server_connection=rabbitmq_event_server_connection,
                    routing_key="events",
                    body=b"",
                    properties=BasicProperties(
                        delivery_mode=2, headers={"termination": True}
                    ),
                )
            except RabbitMQError:
                logging.critical("Error while publishing the termination message.")
                exit(-2)

            rabbitmq_event_server_connection.connection.close()
