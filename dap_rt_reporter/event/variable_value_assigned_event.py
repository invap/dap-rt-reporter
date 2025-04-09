# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from dap_rt_reporter.event.state_event import StateEvent
from dap_rt_reporter.types import ReportEvent

class VariableValueAssignedEvent(StateEvent):
    """Variable value assigned event class."""

    def __init__(self, source_path, line, before, name, expression):
        super().__init__(source_path, line, before, name)
        self._set_sub_type(ReportEvent.VARIABLE_VALUE_ASSIGNED)
        self.expression = expression

    def report(self, timestamp, csv_writer, debugger_connection):
        """Report a variable_value_assigned event. The output format is: \n
        [timestamp],state_event,variable_value_assigned,[event_name],[evaluated_expression]
        """

        csv_writer.writerow(
            [
                timestamp,
                self.type,
                self.sub_type,
                self._get_event_name(debugger_connection),
                self.evaluate_expression(self.expression, debugger_connection)
            ]
        )