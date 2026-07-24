# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
import re
from abc import ABC, abstractmethod
from typing import Any

from dap_rt_reporter.connection.connection_wrapper import ConnectionWrapper
from dap_rt_reporter.types import DAPMessage, DAPRequest


class Event(ABC):
    """Event template"""

    def __init__(self, source_path: str, line: int, before: bool, name: str) -> None:
        """Initialize new event.

        Args:
            source_path (str): Source path associated with the event.
            line (int): Line associated with the event.
            before (bool): Select if event should report before a line
            is executed.
            name (str): Name for the event.
        """
        self.source_path: str = source_path
        self.line: int = line
        self.before: bool = before
        self.name: str = name
        self.type: str = ""
        self.sub_type: str = ""

    @staticmethod
    def parse_dap_response(response: bytes) -> dict[str, Any]:
        """Converts DAP message to dictionary form.
        Complete message is assumed.

        Args:
            response (bytes): DAP message as bytes.

        Returns:
            dict[str, Any]: Parsed message or empty message.
        """

        if b"\r\n\r\n{" in response:
            length, response = response.split(b"\r\n\r\n", 1)
            length = int(length.split(b":")[1])
            return json.loads(response[:length])

        # Return empty message
        return {"type": None}

    def evaluate_expression(
        self,
        expression: str,
        thread_id: int,
        debugger_connection: ConnectionWrapper,
    ) -> str | None:
        """Evaluate expression in current context inside SUT.

        Args:
            expression (str): Expression to evaluate.
            thread_id (int): Thread ID to evaluate at.
            debugger_connection (ConnectionWrapper): Connection to use to make
            the request.

        Raises:
            RuntimeError: _description_

        Returns:
            Any | None: Evaluation result or None if debugger connection
            is interrupted.
        """

        # Get current frame id
        debugger_connection.stack_trace(thread_id)
        frame_id: int | None = None
        while frame_id is None:
            if debugger_connection.get_alive():
                response = debugger_connection.get_response()
                response = self.parse_dap_response(response)

                if (
                    response["type"] == DAPMessage.RESPONSE
                    and response["command"] == DAPRequest.STACKTRACE
                ):
                    frame_id = int(response["body"]["stackFrames"][0]["id"])
            else:
                return None

        # Evaluate expression
        result: str = ""
        debugger_connection.evaluate(expression, frame_id)
        while not result:
            if debugger_connection.get_alive():
                response = debugger_connection.get_response()
                response = self.parse_dap_response(response)

                if (
                    response["type"] == DAPMessage.RESPONSE
                    and response["command"] == DAPRequest.EVALUATE
                ):
                    if response["success"]:
                        result = str(response["body"]["result"])
                    else:
                        raise RuntimeError(response["message"])
            else:
                return None

        result = result.strip('"')

        return result

    def _get_event_name(self, thread_id: int, debugger_connection: ConnectionWrapper) -> str:
        """Evaluate expressions inside the event name.
        Event names with an expression between brackets {expression}
        are evaluated.

        Args:
            thread_id (_type_): Thread ID to evaluate at.
            debugger_connection (ConnectionWrapper): Connection to use to make the request.

        Returns:
            str: Event name with evaluation results.
        """

        event_name = re.sub(
            r"{(.*?)}",
            lambda match: self.evaluate_expression(
                re.findall(r"{(.*?)}", match.group())[0],
                thread_id,
                debugger_connection,
            ),
            self.name,
        )

        return event_name

    def _set_type(self, type_name: str) -> None:
        """Internal setter for event type.

        Args:
            type_name (str): Event type name.
        """

        self.type = type_name

    def _set_sub_type(self, sub_type: str) -> None:
        """Internal setter for event sub type.

        Args:
            sub_type (str): Event sub type name.
        """
        self.sub_type = sub_type

    @abstractmethod
    def report(
        self,
        timestamp: float,
        debugger_connection: ConnectionWrapper,
        thread_id: int,
    ) -> list[Any]:
        """Report event at current thread.

        Args:
            timestamp (int | float): Timestamp when event occured.
            debugger_connection (ConnectionWrapper): Connection to use to make requests.
            thread_id (int): Thread ID to evaluate at.

        Returns:
            list[Any]: List with report items.
        """
