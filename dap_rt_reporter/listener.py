# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import dap_rt_reporter.listener_functions


class Listener:
    def __init__(self) -> None:
        self.events = {}

    def handle_response(self, timestamp, response, csv_writer, debugger_connection):
        """Listens to responses from debugger and gives instructions to reporter."""
        id = response["body"]["hitBreakpointIds"][0]
        # Before events
        for event in self.events[id]["b"]:
            for func in event["functions"]:
                func(timestamp, event, csv_writer, debugger_connection)
        # After events
        if len(self.events[id]["a"]):
            encoded_response = debugger_connection.next()
            
            # Wait until step is completed
            # TODO: Check if timeout or other checks are necessary
            while b"stopped" not in encoded_response:
                encoded_response = debugger_connection.idle()

            for event in self.events[id]["a"]:
                for func in event["functions"]:
                    func(timestamp, event, csv_writer, debugger_connection)

    def add_event(self, breakpoint_id, event):
        """Adds event to listen list, uses breakpoint id as identifier."""

        if breakpoint_id in self.events:
            if event["before"]:
                self.events[breakpoint_id]["b"].append(event)
            else:
                self.events[breakpoint_id]["a"].append(event)
        else:
            self.events[breakpoint_id] = {}
            if event["before"]:
                self.events[breakpoint_id]["b"] = [event]
                self.events[breakpoint_id]["a"] = []
            else:
                self.events[breakpoint_id]["b"] = []
                self.events[breakpoint_id]["a"] = [event]
