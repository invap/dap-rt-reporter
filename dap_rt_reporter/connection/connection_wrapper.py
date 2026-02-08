# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from abc import ABC, abstractmethod


class ConnectionWrapper(ABC):
    """Abstract class for debugger connections. The reporter can interact with any
    connection that follows this class.
    """

    def __init__(self, executable: str, executable_args: str):
        super().__init__()

        self.executable = executable
        self.executable_args = executable_args

        self.alive = True

    def get_alive(self) -> bool:
        """Get if the connection is alive.

        Returns:
            bool: If connection is alive.
        """

        return self.alive

    def set_alive(self, state: bool):
        """Set if the connection is alive.

        Args:
            state (bool): If the connection is alive.
        """

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
