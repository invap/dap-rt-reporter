# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from dap_rt_reporter.event.event import Event

class Listener:
    def __init__(self) -> None:
        self.events = {}

    def handle_response(self, timestamp: int, response: dict, csv_writer, debugger_connection, before: bool):
        """Listens to responses from debugger and gives instructions to reporter."""

        before = "b" if before else "a"

        breakpoint_id = response["body"]["hitBreakpointIds"][0]
        thread_id = response["body"]["threadId"]
        for event in self.events[breakpoint_id][before]:
            event.report(timestamp, csv_writer, debugger_connection, thread_id)

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
