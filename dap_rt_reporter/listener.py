# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
import sys
from typing import Literal

from pika import BasicProperties
from rt_rabbitmq_wrapper.rabbitmq_utility import RabbitMQError

from dap_rt_reporter.connection.connection_wrapper import ConnectionWrapper
from dap_rt_reporter.event.event import Event
from dap_rt_reporter.rabbitmq_connection.rabbitmq_server_connections import (
    rabbitmq_event_server_connection,
)


class Listener:
    def __init__(self, use_rabbitmq: bool = False) -> None:
        self.use_rabbitmq: bool = use_rabbitmq

        # Events dictionary
        self.events: dict[str, dict[str, list[Event]]] = {}

    def handle_response(
        self,
        timestamp: int,
        response: dict,
        csv_writer,
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

            logging.debug("Reporting event: %s", report)

            # Write event
            csv_writer.writerow(report)

            if self.use_rabbitmq:
                self.publish_event(report)

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

    def publish_event(self, event: list):
        """Publish an event to a RabbitMQ server."""

        # Convert event to string
        event_string: str = ""

        for item in event[:-1]:
            event_string += str(item)
            event_string += ","
        event_string += event[-1]

        logging.debug("Publishing event: %s", event_string)

        # Publish event
        try:
            rabbitmq_event_server_connection.publish_message(
                body=event_string,
                properties=BasicProperties(delivery_mode=2),
            )
        except RabbitMQError:
            logging.critical("Error while publishing event: %s", event_string)
            sys.exit(-2)

    def publish_termination(self) -> None:
        """Publish a blank message with the termination header, closes
        connection with monitor.
        """

        try:
            rabbitmq_event_server_connection.publish_message(
                body="",
                properties=BasicProperties(
                    delivery_mode=2, headers={"termination": True}
                ),
            )
        except RabbitMQError:
            logging.critical(
                "Error while publishing the termination message."
            )
            sys.exit(-2)
