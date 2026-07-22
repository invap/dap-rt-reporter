# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
import time
from enum import Enum, auto
from typing import Any

from dap_rt_reporter.event.event import Event
from dap_rt_reporter.listener import Listener
from dap_rt_reporter.types import DAPEvent, DAPMessage, DAPRequest
from dap_rt_reporter.errors import (
    ExecutionError,
    MessageKeyError,
    SetupError,
)
from dap_rt_reporter.connection.errors import (
    DAPRequestError,
    DAPResponseError,
)
from dap_rt_reporter.event_writer.event_writer import EventWriter
from dap_rt_reporter.connection.connection_wrapper import ConnectionWrapper

logger = logging.getLogger(__name__)


class ReporterState(Enum):
    """Reporter execution states"""

    IDLE = auto()
    BREAKPOINT = auto()
    EXIT = auto()


class BreakpointHandleState(Enum):
    """Breakpoint handling states"""

    BEFORE = auto()
    CONTINUE = auto()
    AFTER = auto()


class Reporter:
    """Reporter manages the report logic for events, handling DAP events and requests from
    debuggers.
    """

    def __init__(
        self,
        debugger_connection: ConnectionWrapper,
        event_writer: EventWriter,
    ) -> None:
        """Initializes a reporter.

        Args:
            event_writer (EventWriter): Writer used to write events to
            debugger_connection (ConnectionWrapper): Debugger connection wrapper for DAP communication

        Raises:
            RuntimeError: _description_
        """

        self.state: ReporterState = ReporterState.IDLE

        # Create listener
        self.listener = Listener(event_writer)

        self.debugger_connection = debugger_connection

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
        try:
            self.debugger_connection.initialize()
        except DAPRequestError as e:
            logger.error("Initialize request could not be sent")
            raise ExecutionError("Initialize request error") from e

        try:
            self.debugger_connection.launch()
        except DAPRequestError as e:
            logger.error("Launch request could not be sent")
            raise ExecutionError("Launch request error") from e

        try:
            self._set_up()
        except SetupError as e:
            raise ExecutionError(
                "Breakpoints set up was not completed successfully"
            ) from e

        # Start execution after configuration done is received
        logger.info("Starting SUT execution")

        terminated = False
        self.state = ReporterState.IDLE

        try:
            self.debugger_connection.configuration_done()
        except DAPRequestError as e:
            raise ExecutionError("Configuration done request could not be sent") from e

        # Logic to control program execution
        try:
            terminated = self.execution_loop()
        except KeyError as e:
            raise MessageKeyError(
                "Invalid access to DAP message"
            ) from e
        except ExecutionError as e:
            raise e


        logger.info("Closing reporter")
        logger.info("Program execution time: %s", time.time() - init_time)

        return terminated

    def execution_loop(self) -> bool:
        """Main execution and control loop"""

        response = {}

        while self.debugger_connection.get_alive():
            match self.state:
                case ReporterState.IDLE:
                    # Program is executing and waiting for breakpoints or termination
                    response = self._get_next_response()

                    if response["type"] == DAPMessage.EVENT:
                        if (
                            response["event"] == DAPEvent.STOPPED
                            and response["body"]["reason"] == "breakpoint"
                        ):
                            self.state = ReporterState.BREAKPOINT
                        elif response["event"] == DAPEvent.TERMINATED:
                            self.state = ReporterState.EXIT


                case ReporterState.BREAKPOINT:
                    # Breakpoint hit
                    self.handle_breakpoints( response)
                    self.state = ReporterState.IDLE

                case ReporterState.EXIT:
                    # Program terminates
                    return True

        return False

    def handle_breakpoints(self, initial_hit_response) -> ReporterState:
        """Loop for breakpoint handling"""

        current_state = BreakpointHandleState.BEFORE
        current_response = initial_hit_response

        breakpoint_event = current_response
        breakpoint_id = -1
        # TODO: Handle change in breakpoint source
        # if the last check in BreakpointHandleState.AFTER exits from a file
        # to another in the same line, events could be lost
        # breakpoint_source = ""
        breakpoint_line = -1

        while self.debugger_connection.get_alive():
            match current_state:
                case BreakpointHandleState.BEFORE:
                    # A breakpoint hit occured in the current line, handle all before events
                    # Save the breakpoint id, source and line to handle after events
                    breakpoint_id = self.listener.handle_response(
                        int(1e6 * time.time()),
                        breakpoint_event,
                        self.debugger_connection,
                        True,
                    )

                    # Handle the after events or continue execution
                    if self.listener.is_after(breakpoint_id):
                        breakpoint_line = self.listener.get_line_from_id(breakpoint_id)
                        current_state = BreakpointHandleState.AFTER
                    else:
                        current_state = BreakpointHandleState.CONTINUE

                case BreakpointHandleState.AFTER:
                    # A breakpoint hit occured in the current line, handle all after events

                    # Get the thread id that produced the stopped event
                    thread_id = breakpoint_event["body"]["threadId"]

                    # Do a step request
                    self.debugger_connection.next()

                    # Wait for confirmation, this step can be skipped
                    while self.debugger_connection.get_alive():
                        current_response = self._get_next_response()

                        if current_response["type"] == DAPMessage.RESPONSE:
                            if current_response["success"]:
                                break
                            else:
                                return ReporterState.EXIT

                    current_stopped_event = {}
                    # Wait for completion
                    while self.debugger_connection.get_alive():
                        current_response = self._get_next_response()

                        if current_response["type"] == DAPMessage.EVENT:
                            if current_response["event"] == DAPEvent.STOPPED:
                                # Save the current stopped event to handle if the after condition is met
                                current_stopped_event = current_response
                                break

                    # Check if the line or source has changed
                    self.debugger_connection.stack_trace(thread_id)

                    current_line: str = ""
                    while self.debugger_connection.get_alive():
                        current_response = self._get_next_response()

                        if (
                            current_response["type"] == DAPMessage.RESPONSE
                            and current_response["command"] == DAPRequest.STACKTRACE
                        ):
                            current_line = current_response["body"]["stackFrames"][0][
                                "line"
                            ]
                            break

                    # If both the line or the file changed then handle the event
                    if int(current_line) != breakpoint_line:
                        # If a breakpoint was set in the middle of this steps they are ignored

                        # Handle de after events for the previous breakpoint
                        if current_stopped_event["event"] == DAPEvent.STOPPED:
                            self.listener.handle_response(
                                int(1e6 * time.time()),
                                breakpoint_event,
                                self.debugger_connection,
                                False,
                            )

                            if current_stopped_event["body"]["reason"] == "breakpoint":
                                # If the stopped reason was breakpoint, go back to the before step and handle that event
                                breakpoint_event = current_stopped_event
                                current_state = BreakpointHandleState.BEFORE
                            elif current_stopped_event["body"]["reason"] == "step":
                                # If the stopped reason was next, continue execution because no new breakpoint was hit, finished handling
                                current_state = BreakpointHandleState.CONTINUE

                case BreakpointHandleState.CONTINUE:
                    # The current set of breakpoints was correctly handled

                    # Continue execution and wait for confirmation
                    self.debugger_connection.continue_execution()

                    while self.debugger_connection.get_alive():
                        current_response = self._get_next_response()

                        if current_response["type"] == DAPMessage.RESPONSE:
                            if current_response["success"]:
                                return ReporterState.IDLE
                            else:
                                return ReporterState.EXIT

        return ReporterState.EXIT

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

    def _get_next_response(self) -> dict[str, Any]:
        try:
            response = self.debugger_connection.get_response()
        except DAPResponseError as e:
            raise ExecutionError(
                "DAP response was not received correctly"
            ) from e

        return Event.parse_dap_response(response)

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
        self.listener.close()
