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

class DAPRequest(StrEnum):
    """
    Enum class contains a selection of DAP requests
    """

    STACKTRACE = "stackTrace"
    EVALUATE = "evaluate"
    SETBREAKPOINTS = "setBreakpoints"

class ReportEventSubType(StrEnum):
    """Enum class contains the Reporter events sub types currently supported"""

    CHECKPOINT_REACHED = "checkpoint_reached"
    TASK_STARTED = "task_started"
    TASK_FINISHED = "task_finished"
    VARIABLE_VALUE_ASSIGNED = "variable_value_assigned"
    COMPONENT_EVENT = "component_event"
    CLOCK_START = "clock_start"
    CLOCK_PAUSE = "clock_pause"
    CLOCK_RESUME = "clock_resume"
    CLOCK_RESET = "clock_reset"


class ReportEventType(StrEnum):
    """Enum class contains the Reporter event types"""

    PROCESS_EVENT = "process_event"
    STATE_EVENT = "state_event"
    COMPONENT_EVENT = "component_event"
    TIMED_EVENT = "timed_event"
