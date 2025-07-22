# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import pika


class RabbitMQWriter:
    def __init__(self, host, port, user, password, exchange):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.exchange = exchange

        self.connection, self.channel = self.connect()

    def publish_event(self, event):
        event_string = ""

        self.channel.basic_publish(exchange=self.exchange, routing_key="events", body=event)

    def connect(self):
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
        self.connection.close()
