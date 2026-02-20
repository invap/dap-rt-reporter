# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
from typing import Literal

from dap_rt_reporter.connection.connection_wrapper import ConnectionWrapper
from dap_rt_reporter.event.event import Event
from dap_rt_reporter.event_writer.event_writer import EventWriter

logger = logging.getLogger(__name__)


class Listener:
    def __init__(self, event_writer: EventWriter) -> None:
        self.event_writer = event_writer

        # Events dictionary
        self.events: dict[str, dict[str, list[Event]]] = {}

    def handle_response(
        self,
        timestamp: int,
        response: dict,
        debugger_connection: ConnectionWrapper,
        before: bool,
    ):
        """Handle breakpoint responses."""

        # Set before or after key
        before_key: Literal["b"] | Literal["a"] = "b" if before else "a"

        # Get breakpoint and thread id from response
        breakpoint_id = response["body"]["hitBreakpointIds"][0]
        thread_id = response["body"]["threadId"]
        # Report each event in event list
        for event in self.events[breakpoint_id][before_key]:
            report = event.report(timestamp, debugger_connection, thread_id)

            logger.debug("Reporting event: %s", report)

            # Write event
            self.event_writer.write(report)

    def add_event(self, breakpoint_id, event: Event) -> None:
        """Adds event to listen list, uses breakpoint id as identifier."""

        # Store event in events dict
        # ID already exists, for events in the same line and source
        if breakpoint_id in self.events:
            # Store event as before or after
            if event.before:
                self.events[breakpoint_id]["b"].append(event)
            else:
                self.events[breakpoint_id]["a"].append(event)
        else:
            # Create structure for new ID
            self.events[breakpoint_id] = {}
            # Store event as before or after
            if event.before:
                self.events[breakpoint_id]["b"] = [event]
                self.events[breakpoint_id]["a"] = []
            else:
                self.events[breakpoint_id]["b"] = []
                self.events[breakpoint_id]["a"] = [event]

    def close(self):
        self.event_writer.close()
