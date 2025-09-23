import logging
import tomllib
import sys

from rt_rabbitmq_wrapper.rabbitmq_utility import (
    RabbitMQ_server_info,
    RabbitMQ_server_outgoing_connection,
    RabbitMQError,
)

rabbitmq_event_server_connection = None


def build_rabbitmq_connection_from_toml(toml_path: str):
    """Build the RabbitMQ connection from a toml configuration file.

    Args:
        toml_path (str): Path to the toml configuration file.
    """
    global rabbitmq_event_server_connection
    with open(toml_path, "rb") as f:
        rabbitmq_config = tomllib.load(f)

        host = "localhost"
        port = 5672
        user = "guest"
        password = "guest"
        connection_attempts = 5
        retry_delay = 3
        exchange = "events_exchange"
        exchange_type = "fanout"

        try:
            events_rabbitmq_config = rabbitmq_config["exchanges"]["events"]
        except KeyError:
            logging.info(
                "No events configuration in toml file, using default values."
            )
        else:
            host = (
                events_rabbitmq_config["host"]
                if "host" in events_rabbitmq_config
                else "localhost"
            )
            port = (
                events_rabbitmq_config["port"]
                if "port" in events_rabbitmq_config
                else 5672
            )
            user = (
                events_rabbitmq_config["user"]
                if "user" in events_rabbitmq_config
                else "guest"
            )
            password = (
                events_rabbitmq_config["password"]
                if "password" in events_rabbitmq_config
                else "guest"
            )
            connection_attempts = (
                events_rabbitmq_config["connection_attempts"]
                if "connection_attempts" in events_rabbitmq_config
                else 5
            )
            retry_delay = (
                events_rabbitmq_config["retry_delay"]
                if "retry_delay" in events_rabbitmq_config
                else 3
            )
            exchange = (
                events_rabbitmq_config["exchange"]
                if "exchange" in events_rabbitmq_config
                else "events_exchange"
            )
            exchange_type = (
                events_rabbitmq_config["exchange_type"]
                if "exchange_type" in events_rabbitmq_config
                else "fanout"
            )
        finally:
            server_info = RabbitMQ_server_info(host, port, user, password)
            rabbitmq_event_server_connection = (
                RabbitMQ_server_outgoing_connection(
                    server_info,
                    connection_attempts,
                    retry_delay,
                    exchange,
                    exchange_type,
                )
            )

        try:
            rabbitmq_event_server_connection.connect()
        except RabbitMQError:
            logging.error("Couldn't connect to RabbitMQ server.")
            sys.exit(-2)
