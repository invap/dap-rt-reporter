# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
from typing import Any, Literal

from dap_rt_reporter.connection.connection_wrapper import ConnectionWrapper
from dap_rt_reporter.event.event import Event
from dap_rt_reporter.event_writer.event_writer import EventWriter

logger = logging.getLogger(__name__)


class Listener:
    def __init__(self, event_writer: EventWriter) -> None:
        self.event_writer: EventWriter = event_writer

        # Events dictionary
        self.events: dict[str, dict[str, list[Event]]] = {}

    def handle_response(
        self,
        timestamp: int,
        response: dict[str, Any],
        debugger_connection: ConnectionWrapper,
        before: bool,
    ) -> int:
        """Handle breakpoint responses.

        Returns:
            str: Return the values of the breakpoint id
            for the breakpoint associated.
        """

        # Set before or after key
        before_key: Literal["b", "a"] = "b" if before else "a"

        # Get breakpoint and thread id from response
        breakpoint_id: str = str(response["body"]["hitBreakpointIds"][0])
        thread_id: int = int(response["body"]["threadId"])

        # Report each event in event list
        for event in self.events[breakpoint_id][before_key]:
            report = event.report(timestamp, debugger_connection, thread_id)

            logger.debug("Reporting event: %s", report)

            # Write event
            self.event_writer.write(report)

        return int(breakpoint_id)

    def is_after(self, id: int) -> int:
        return len(self.events[str(id)]["a"])

    def get_source_from_id(self, id: int) -> str:
        source = ""

        if len(self.events[str(id)]["b"]):
            source = self.events[str(id)]["b"][0].source_path
        elif len(self.events[str(id)]["a"]):
            source = self.events[str(id)]["a"][0].source_path

        return source

    def get_line_from_id(self, id: int) -> int:
        line = -1

        if len(self.events[str(id)]["b"]):
            line = self.events[str(id)]["b"][0].line
        elif len(self.events[str(id)]["a"]):
            line = self.events[str(id)]["a"][0].line

        return line

    def add_event(self, breakpoint_id: int, event: Event) -> None:
        """Adds event to listen list, uses breakpoint id as identifier."""

        id = str(breakpoint_id)

        # Store event in events dict
        # ID already exists, for events in the same line and source
        if id in self.events:
            # Store event as before or after
            if event.before:
                self.events[id]["b"].append(event)
            else:
                self.events[id]["a"].append(event)
        else:
            # Create structure for new ID
            self.events[id] = {}
            # Store event as before or after
            if event.before:
                self.events[id]["b"] = [event]
                self.events[id]["a"] = []
            else:
                self.events[id]["b"] = []
                self.events[id]["a"] = [event]

    def close(self):
        self.event_writer.close()
