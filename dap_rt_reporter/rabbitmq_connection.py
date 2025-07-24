# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import pika
import logging

class RabbitMQConnection:
    def __init__(self, host: str, port: str, user: str, password: str, exchange: str):
        """Manage the RabbitMQ server connection."""

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.exchange = exchange

        self.connection, self.channel = self.connect()

    def publish_event(self, event: list):
        """Publish an event."""

        # Convert event to string
        event_string = ""

        for item in event[:-1]:
            event_string += str(item)
            event_string += ","
        event_string += event[-1]

        logging.debug("Publishing event: %s", event_string)

        # Publish event
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key="events",
            body=event_string,
            properties=pika.BasicProperties(delivery_mode=2),
        )

    def connect(self):
        """Connect to RabbitMQ server."""

        credentials = pika.PlainCredentials(username=self.user, password=self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials,
            connection_attempts=5,
            retry_delay=3,
        )

        connection = pika.BlockingConnection(parameters)

        channel = connection.channel()

        channel.exchange_declare(
            exchange=self.exchange, exchange_type="fanout", auto_delete=True
        )

        return connection, channel

    def disconnect(self):

        # Send termination
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key="events",
            body="",
            properties=pika.BasicProperties(
                delivery_mode=2, headers={"termination": True}
            ),
        )

        # Disconnect from server
        self.connection.close()
