# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from dap_rt_reporter.event.timed_event import TimedEvent
from dap_rt_reporter.types import ReportEventSubType


class ClockStartEvent(TimedEvent):
    def __init__(self, source_path: str, line: int, before: bool, name: str):
        super().__init__(source_path, line, before, name)
        self._set_sub_type(ReportEventSubType.CLOCK_START)
