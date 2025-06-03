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
        if b"\r\n\r\n{" in response:
            length, response = response.split(b"\r\n\r\n", 1)
            length = int(length.split(b":")[1])
            return json.loads(response[:length])
        else:
            raise RuntimeError(f"Incomplete response. \nResponse: {response}")

    def evaluate_expression(self, expression, thread_id, debugger_connection):
        """Evaluate expression in current context inside SUT."""

        debugger_connection.stack_trace(thread_id)
        frame_id = None
        while frame_id is None:
            response = debugger_connection.get_response()
            response = self.parse_dap_response(response)

            if (
                response["type"] == DAPMessage.RESPONSE
                and response["command"] == "stackTrace"
            ):
                frame_id = response["body"]["stackFrames"][0]["id"]


        result = None
        debugger_connection.evaluate(expression, frame_id)
        while result is None:
            response = debugger_connection.get_response()
            response = self.parse_dap_response(response)

            if (
                response["type"] == DAPMessage.RESPONSE
                and response["command"] == "evaluate"
            ):
                if response["success"]:
                    result = response["body"]["result"]
                else:
                    raise RuntimeError(response["message"])
        
        return result.encode("unicode-escape").decode()

    def _get_event_name(self, thread_id, debugger_connection):
        """Evaluate expressions inside the event name."""

        event_name = re.sub(
            r"{(.*?)}",
            lambda match: self.evaluate_expression(
                re.findall(r"{(.*?)}", match.group())[0], thread_id, debugger_connection
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
