# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from dap_rt_reporter.event.event import Event
from dap_rt_reporter.connection.connection_wrapper import ConnectionWrapper
from csv import writer


class Listener:
    def __init__(self) -> None:

        # Events dictionary
        self.events = {}

        # RabbitMQ connection
        self.rabbitmq_connection = None

    def handle_response(
        self,
        timestamp: int,
        response: dict,
        csv_writer: writer,
        debugger_connection: ConnectionWrapper,
        before: bool,
    ):
        """Handle breakpoint responses."""

        before = "b" if before else "a"

        breakpoint_id = response["body"]["hitBreakpointIds"][0]
        thread_id = response["body"]["threadId"]
        for event in self.events[breakpoint_id][before]:
            report = event.report(timestamp, debugger_connection, thread_id)

            csv_writer.writerow(report)

            if self.rabbitmq_connection:
                self.rabbitmq_connection.publish_event(report)

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

    def set_rabbitmq_connection(self, rabbitmq_connection):
        self.rabbitmq_connection = rabbitmq_connection