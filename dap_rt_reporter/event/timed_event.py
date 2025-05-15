# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from dap_rt_reporter.event.event import Event
from dap_rt_reporter.types import ReportEventType


class TimedEvent(Event):
    def __init__(self, source_path, line, before, name):
        super().__init__(source_path, line, before, name)
        self._set_type(ReportEventType.TIMED_EVENT)

    def report(self, timestamp, csv_writer, debugger_connection):
        csv_writer.writerow(
            [
                timestamp,
                self.type,
                self.sub_type,
                self._get_event_name(debugger_connection),
            ]
        )
