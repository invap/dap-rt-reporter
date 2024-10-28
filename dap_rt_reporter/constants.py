# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from enum import StrEnum

class DAPMessage(StrEnum):
    EVENT = 'event'
    RESPONSE = 'response'
    REQUEST = 'request'

class DAPEvent(StrEnum):
    STOPPED = 'stopped'
    TERMINATED = 'terminated'
    OUTPUT = 'output'

class Actions(StrEnum):
    CONTINUE = 'continue'
    NEXT = 'next'
    IDLE = 'idle'
    EVALUATE = 'evaluate'
    TERMINATE = 'terminate'
    ERROR = 'error'

class ReportEvent(StrEnum):
    CHECKPOINT_REACHED = 'checkpoint_reached'