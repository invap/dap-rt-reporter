# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Any

from dap_rt_reporter.event.state_event import StateEvent
from dap_rt_reporter.types import ReportEventSubType
from dap_rt_reporter.connection.connection_wrapper import ConnectionWrapper


class VariableValueAssignedEvent(StateEvent):
    """Variable value assigned event."""

    def __init__(
        self,
        source_path: str,
        line: int,
        before: bool,
        name: str,
        expression: str,
    ) -> None:
        """Initialize new variable value assigned event.

        Args:
            source_path (str): Source asociated with the event.
            line (int): Line asociated with the event.
            before (bool): Select if event should report before a line is executed.
            name (str): Name of the event.
            expression (str): Expression to evaluate when event is reported.
        """

        super().__init__(source_path, line, before, name)
        self._set_sub_type(ReportEventSubType.VARIABLE_VALUE_ASSIGNED)
        self.expression = expression

    def report(
        self,
        timestamp: int | float,
        debugger_connection: ConnectionWrapper,
        thread_id: int,
    ) -> list[Any]:
        """Report a variable_value_assigned event.
        The output format is:

        [timestamp],state_event,variable_value_assigned,[event_name],[evaluated_expression]

        Args:
            timestamp (int | float): Timestamp when event occured.
            debugger_connection (ConnectionWrapper): Connection to use to make requests.
            thread_id (int): Thread ID to evaluate at.

        Returns:
            list[Any]: List with report items.
        """

        return [
            timestamp,
            self.type,
            self.sub_type,
            self._get_event_name(thread_id, debugger_connection),
            self.evaluate_expression(
                self.expression, thread_id, debugger_connection
            ),
        ]
