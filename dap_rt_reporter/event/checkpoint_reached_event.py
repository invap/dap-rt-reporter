# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from dap_rt_reporter.event.process_event import ProcessEvent
from dap_rt_reporter.types import ReportEventSubType


class CheckpointReachedEvent(ProcessEvent):
    """Checkpoint reached event."""

    def __init__(
        self, source_path: str, line: int, before: bool, name: str
    ) -> None:
        """Initialize new checkpoint reached event.

        Args:
            source_path (str): Source path asociated with the event.
            line (int): Line asociated with the event.
            before (bool): Select if event should report before a line is executed.
            name (str): Name for the event.
        """

        super().__init__(source_path, line, before, name)
        self._set_sub_type(ReportEventSubType.CHECKPOINT_REACHED)
