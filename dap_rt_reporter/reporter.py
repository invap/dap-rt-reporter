# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
import logging
import time

from dap_rt_reporter.connection.gdb_connection import GDBConnection
from dap_rt_reporter.connection.lldb_connection import LLDBConnection
from dap_rt_reporter.event.event import Event
from dap_rt_reporter.listener import Listener
from dap_rt_reporter.types import DAPEvent, DAPMessage, DAPRequest
from dap_rt_reporter.errors import (
    ReporterInitError,
    ExecutionError,
    SetupError,
)
from dap_rt_reporter.connection.errors import (
    SpawnError,
    DAPRequestError,
    DAPResponseError,
)

logger = logging.getLogger(__name__)


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
        """Initializes a reporter.

        Args:
            executable_path (str): Path to the SUT executable.
            execution_trace_log_path (str): Path to the output  file.
            executable_args (str, optional): Arguments to pass to the SUT. Defaults to "".
            debugger_selection (str, optional): Select debugger to use during execution, accepted options are gdb and lldb. Defaults to "gdb".
            use_rabbitmq (bool, optional): Flag to set when using RabbitMQ server. Defaults to False.

        Raises:
            RuntimeError: _description_
        """

        # Use debugger connection gdb/lldb
        self.debugger_selection = debugger_selection
        match self.debugger_selection:
            case "gdb":
                self.debugger_connection = GDBConnection
            case "lldb":
                self.debugger_connection = LLDBConnection
            case _:
                raise ReporterInitError(
                    "Invalid debugger option, valid options are gdb and lldb"
                )

        try:
            self.debugger_connection = self.debugger_connection(
                executable_path, executable_args
            )
        except SpawnError as e:
            logger.error(
                "DAP Reporter could not initialize debugger %s",
                self.debugger_selection,
            )
            raise ReporterInitError(
                f"Debugger {self.debugger_selection} could not be initialized"
            ) from e

        # Create listener
        self.listener = Listener(use_rabbitmq)

        self.execution_trace_log_path = execution_trace_log_path
        self.use_rabbitmq = use_rabbitmq

        # Used for saving events
        self.events: list[Event] = []

    def execute(self) -> bool:
        """Begins program execution and reporting.

        Raises:
            ExecutionError: Error occurs during execution

        Returns:
            bool: Indicates program ending
        """

        init_time = time.time()
        # Open csv file and start execution
        with open(
            self.execution_trace_log_path, "w", encoding="utf8"
        ) as report_file:
            csv_writer = csv.writer(report_file, delimiter=",")

            try:
                self.debugger_connection.initialize()
            except DAPRequestError as e:
                logger.error("Initialize request could not be sent.")
                raise ExecutionError("Initialize request error") from e

            try:
                self.debugger_connection.launch()
                self._set_up()
            except DAPRequestError as e:
                logger.error("Launch request could not be sent.")
                raise ExecutionError("Launch request error") from e
            except SetupError as e:
                raise ExecutionError(
                    "Breakpoints set up was not completed successfully"
                ) from e

            # Start execution after configuration done is received
            logger.info("Starting SUT execution")

            try:
                self.debugger_connection.configuration_done()
            except DAPRequestError as e:
                logger.error("Configuration done request could not be sent.")
                raise ExecutionError("Configuration done request error") from e

            terminated = False
            while not terminated and self.debugger_connection.get_alive():
                # Get response from debugger

                try:
                    response = self.debugger_connection.get_response()
                    response = Event.parse_dap_response(response)
                except DAPResponseError as e:
                    logger.error("Could not read DAP response")
                    raise ExecutionError(
                        "DAP response was not received correctly"
                    ) from e

                logger.debug("DAP Response: %s", response)
                # Logic to control program execution
                try:
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
                except KeyError as e:
                    raise ExecutionError(
                        "Invalid DAP response was received, incorrect format"
                    ) from e

        logger.info("Closing reporter")
        logger.info("Program execution time: %s", time.time() - init_time)

        return terminated

    def _set_up(self) -> None:
        """Sets breakpoints and gives the events to listener.

        Raises:
            RuntimeError: _description_
        """

        logger.info("Setting breakpoints")
        # Create breakpoint locations
        breakpoint_locations: dict[str, dict[int, list[Event]]] = {}
        for event in self.events:
            # Save breakpoint/event relationships
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
        breakpoint_id: int = 1
        breakpoint_id_table = {}
        for source_path, event_lists in breakpoint_locations.items():
            # Convert the source and lines to DAP format
            lines_dap_form = []
            for line, event_list in event_lists.items():
                lines_dap_form.append({"line": int(line)})

                breakpoint_id_table[str(breakpoint_id)] = {
                    "source_path": source_path,
                    "line": line,
                }

                # Add events to listener
                for event in event_list:
                    self.listener.add_event(breakpoint_id, event)
                breakpoint_id += 1

            source = source_path[source_path.rfind("/") + 1]
            source_dap_form = {"name": source, "path": source_path}

            # Set breakpoints and clear previous ones
            logger.debug("Setting breakpoints for %s", source_dap_form["name"])
            self.debugger_connection.set_breakpoints_source(
                source_dap_form, lines_dap_form
            )

            # Check breakpoints verification
            # Read all responses until verification is confirmed
            breakpoint_verification = False
            while (
                not breakpoint_verification
                and self.debugger_connection.get_alive()
            ):
                try:
                    response = self.debugger_connection.get_response()
                    response = Event.parse_dap_response(response)
                except DAPResponseError as e:
                    logger.error("Could not read DAP response")
                    raise SetupError(
                        "DAP response was not received correctly"
                    ) from e

                logger.debug(
                    "Breakpoint verification DAP response: %s", response
                )
                if (
                    response["type"] == DAPMessage.RESPONSE
                    and response["command"] == DAPRequest.SETBREAKPOINTS
                ):
                    for breakpoint in response["body"]["breakpoints"]:
                        if not breakpoint["verified"]:
                            logger.error(
                                "Breakpoint verification for source %s, line %s failed",
                                breakpoint_id_table[str(breakpoint["id"])][
                                    "source_path"
                                ],
                                breakpoint_id_table[str(breakpoint["id"])][
                                    "line"
                                ],
                            )
                            raise SetupError(
                                f"Breakpoint verification failed: \nSource: {breakpoint_id_table[str(breakpoint['id'])]['source_path']} \nLine: {breakpoint_id_table[str(breakpoint['id'])]['line']}"
                            )
                    breakpoint_verification = True

    def set_event(self, event: Event) -> None:
        """Set new event to report.

        Args:
            event (Event): New event to set in the events list.
        """

        self.events.append(event)

    def kill(self) -> None:
        """Deactivate debugger connection and stop SUT execution, set up
        is allowed to finish.
        """

        self.debugger_connection.set_alive(False)

    def close(self) -> None:
        """Close reporter and send termination message to exchange if RabbitMQ
        flag was set.
        """

        logger.info("Closing debugger connection.")
        self.debugger_connection.close()

        if self.use_rabbitmq:
            self.listener.publish_termination()
