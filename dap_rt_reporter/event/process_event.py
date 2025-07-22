# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from dap_rt_reporter.event.event import Event
from dap_rt_reporter.types import ReportEventType


class ProcessEvent(Event):
    """Process event template.
    All current process events use the same report structure.
    """

    def __init__(self, source_path, line, before, name):
        super().__init__(source_path, line, before, name)
        self._set_type(ReportEventType.PROCESS_EVENT)

    def report(self, timestamp, debugger_connection, thread_id):
        """Report a process event. The output format is: \n
        [timestamp],process_event,[event_sub_type],[event_name]
        """
        return [
            timestamp,
            self.type,
            self.sub_type,
            self._get_event_name(thread_id, debugger_connection),
        ]
