# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from dap_rt_reporter.event.event import Event

class Listener:
    def __init__(self) -> None:
        self.events = {}

    def handle_response(self, timestamp, response, csv_writer, debugger_connection):
        """Listens to responses from debugger and gives instructions to reporter."""
        breakpoint_id = response["body"]["hitBreakpointIds"][0]
        # Before events
        for event in self.events[breakpoint_id]["b"]:
            event.report(timestamp, csv_writer, debugger_connection)
        # After events
        if len(self.events[breakpoint_id]["a"]):
            encoded_response = debugger_connection.next()
            
            # Wait until step is completed
            # TODO: Check if timeout or other checks are necessary
            while b"stopped" not in encoded_response:
                encoded_response = debugger_connection.idle()

            for event in self.events[breakpoint_id]["a"]:
                event.report(timestamp, csv_writer, debugger_connection)

    def add_event(self, breakpoint_id, event: Event):
        """Adds event to listen list, uses breakpoint id as identifier."""

        if breakpoint_id in self.events:
            if event.before:
                self.events[breakpoint_id]["b"].append(event)
            else:
                self.events[breakpoint_id]["a"].append(event)
        else:
            self.events[breakpoint_id] = {}
            if event.before:
                self.events[breakpoint_id]["b"] = [event]
                self.events[breakpoint_id]["a"] = []
            else:
                self.events[breakpoint_id]["b"] = []
                self.events[breakpoint_id]["a"] = [event]
