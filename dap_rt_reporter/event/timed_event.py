# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import override

from dap_rt_reporter.connection.connection_wrapper import ConnectionWrapper
from dap_rt_reporter.event.event import Event
from dap_rt_reporter.types import ReportEventType


class TimedEvent(Event):
    def __init__(self, source_path: str, line: int, before: bool, name: str):
        super().__init__(source_path, line, before, name)
        self._set_type(ReportEventType.TIMED_EVENT)

    @override
    def report(self, timestamp: float, debugger_connection: ConnectionWrapper, thread_id: int):
        return [
            timestamp,
            self.type,
            self.sub_type,
            self._get_event_name(thread_id, debugger_connection),
        ]
