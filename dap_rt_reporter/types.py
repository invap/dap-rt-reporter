# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from enum import StrEnum


class DAPMessage(StrEnum):
    """Enum class contains types of DAP messages"""

    EVENT = "event"
    RESPONSE = "response"
    REQUEST = "request"


class DAPEvent(StrEnum):
    """Enum class contains a selection of DAP events"""

    STOPPED = "stopped"
    TERMINATED = "terminated"
    OUTPUT = "output"


class ReportEvent(StrEnum):
    """Enum class contains the Reporter events currently supported"""

    CHECKPOINT_REACHED = "checkpoint_reached"
    TASK_STARTED = "task_started"
    TASK_FINISHED = "task_finished"
    VARIABLE_VALUE_ASSIGN = "variable_value_assign"


class ReportEventType(StrEnum):
    """Enum class contains the Reporter event types"""

    PROCESS_EVENT = "process_event"
    STATE_EVENT = "state_event"
