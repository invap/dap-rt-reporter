# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import re
import json

from abc import ABC, abstractmethod
from dap_rt_reporter.types import DAPMessage


class Event(ABC):
    """Event template"""

    def __init__(self, source_path: str, line: int, before: bool, name: str):
        self.source_path = source_path
        self.line = line
        self.before = before
        self.name = name
        self.type = None
        self.sub_type = None

    @staticmethod
    def parse_dap_response(response: bytes):
        """Converts DAP response to dictionary form.
        Assumes complete message.
        """
        response_list = []
        if response:
            while b"\r\n\r\n{" in response:
                length, response = response.split(b"\r\n\r\n", 1)

                length = int(length.split(b":")[1])
                response_list.append(json.loads(response[:length]))
                response = response[length:]

        return response_list

    def evaluate_expression(self, expression, debugger_connection):
        """Evaluate expression in current context inside SUT."""

        result = None
        encoded_response = debugger_connection.evaluate(expression)
        # encoded_response = debugger_connection.evaluate("_x")
        while result is None:
            response_list = self.parse_dap_response(encoded_response)
            encoded_response = b""

            for response in response_list:
                if (
                    response["type"] == DAPMessage.RESPONSE
                    and response["command"] == "evaluate"
                ):
                    if response["success"]:
                        result = response["body"]["result"]
                    else:
                        raise RuntimeError(response["message"])
            if not encoded_response:
                encoded_response = debugger_connection.idle()

        return result

    def _get_event_name(self, debugger_connection):
        """Evaluate expressions inside the event name."""

        event_name = re.sub(
            r"{(.*?)}",
            lambda match: self.evaluate_expression(
                re.findall(r"{(.*?)}", match.group())[0], debugger_connection
            ),
            self.name,
        )

        return event_name

    @abstractmethod
    def report(self):
        pass

    def _set_type(self, type):
        """Setter for event type."""

        self.type = type

    def _set_sub_type(self, sub_type):
        """Setter for event sub type-"""
        self.sub_type = sub_type
