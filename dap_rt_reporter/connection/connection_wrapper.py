# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from abc import ABC, abstractmethod


class ConnectionWrapper(ABC):
    """Abstract class for connections. The reporter can interact with any
    connection that follows this class.
    """

    def __init__(self, executable, executable_args):
        super().__init__()

        self.executable = executable
        self.executable_args = executable_args

        self.alive = True

    def get_alive(self):
        return self.alive

    def set_alive(self, state: bool):
        self.alive = state

    @abstractmethod
    def get_response(self) -> bytes:
        pass

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def launch(self):
        pass

    @abstractmethod
    def configuration_done(self):
        pass

    @abstractmethod
    def set_breakpoints_source(self, source, breakpoints):
        pass

    @abstractmethod
    def continue_execution(self):
        pass

    @abstractmethod
    def next(self):
        pass

    @abstractmethod
    def evaluate(self, expression, frame_id):
        pass

    @abstractmethod
    def stack_trace(self, thread_id):
        pass

    @abstractmethod
    def close(self):
        pass
