# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from abc import ABC

from dap_rt_reporter.event.event import Event
from dap_rt_reporter.types import ReportEventType


class StateEvent(Event, ABC):
    """State event template."""

    def __init__(self, source_path: str, line: int, before: bool, name: str):
        super().__init__(source_path, line, before, name)
        self._set_type(ReportEventType.STATE_EVENT)
