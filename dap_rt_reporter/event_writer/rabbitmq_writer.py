# Copyright (C) <2026>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
import logging
import sys
from typing import Any

from pika import BasicProperties
from rt_rabbitmq_wrapper.exchange_types.event.event_codec_errors import (
    EventCSVError,
    EventTypeError,
)
from rt_rabbitmq_wrapper.exchange_types.event.event_csv_codec import (
    EventCSVCoDec,
)
from rt_rabbitmq_wrapper.exchange_types.event.event_dict_codec import (
    EventDictCoDec,
)
from rt_rabbitmq_wrapper.rabbitmq_utility import RabbitMQError

from dap_rt_reporter.event_writer.event_writer import EventWriter
from dap_rt_reporter.rabbitmq_connection import rabbitmq_server_connections

logger = logging.getLogger(__name__)


class RabbitMQWriter(EventWriter):
    def __init__(self):
        super().__init__()

    def write(self, event: list[Any]):
        """Publish an event to a RabbitMQ server."""

        # Convert csv event
        event_string = ",".join(map(str, event))
        try:
            event_u = EventCSVCoDec.from_csv(event_string)
        except EventCSVError:
            logger.info("Error when parsing event csv: %s", event_string)
            sys.exit(-1)

        try:
            event_dict = EventDictCoDec.to_dict(event_u)
        except EventTypeError:
            logger.info(
                "Error building event dictionary from event: %s", event_u
            )
            sys.exit(-1)

        logger.debug("Publishing event: %s", event)

        # Publish event
        try:
            rabbitmq_server_connections.rabbitmq_event_server_connection.publish_message(
                body=json.dumps(event_dict),
                properties=BasicProperties(delivery_mode=2),
            )
        except RabbitMQError:
            logger.critical("Error while publishing event: %s", event)
            sys.exit(-2)

    def close(self) -> None:
        """Publish a blank message with the termination header, closes
        connection with monitor.
        """
        try:
            rabbitmq_server_connections.rabbitmq_event_server_connection.publish_message(
                body="",
                properties=BasicProperties(
                    delivery_mode=2, headers={"termination": True}
                ),
            )
        except RabbitMQError:
            logger.critical("Error while publishing the termination message.")
            sys.exit(-2)
