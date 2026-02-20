# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from abc import ABC, abstractmethod
from typing import Any


class EventWriter(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def write(self, event: list[Any]):
        pass

    @abstractmethod
    def close(self):
        pass
