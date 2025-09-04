# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from dap_rt_reporter.event.event import Event
from dap_rt_reporter.types import ReportEventType, ReportEventSubType


class ComponentEvent(Event):
    def __init__(self, source_path, line, before, name, function_name, function_params):
        super().__init__(source_path, line, before, name)
        self._set_type(ReportEventType.COMPONENT_EVENT)
        self._set_sub_type(ReportEventSubType.COMPONENT_EVENT)
        self.function_name = function_name
        self.function_params = function_params

    def report(self, timestamp, debugger_connection, thread_id):
        return [
            timestamp,
            self.type,
            self._get_event_name(thread_id, debugger_connection),
            self.function_name,
            *[
                self.evaluate_expression(param, thread_id, debugger_connection)
                for param in self.function_params
            ],
        ]
