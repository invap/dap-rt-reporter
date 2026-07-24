# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import override

from dap_rt_reporter.connection.connection_wrapper import ConnectionWrapper
from dap_rt_reporter.event.event import Event
from dap_rt_reporter.types import ReportEventSubType, ReportEventType


class ComponentEvent(Event):
    def __init__(self, source_path: str, line: int, before: bool, name: str, function_name: str, function_params: list[str]):
        super().__init__(source_path, line, before, name)
        self._set_type(ReportEventType.COMPONENT_EVENT)
        self._set_sub_type(ReportEventSubType.COMPONENT_EVENT)
        self.function_name: str = function_name
        self.function_params: list[str] = function_params

    @override
    def report(self, timestamp: float, debugger_connection: ConnectionWrapper, thread_id: int):
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
