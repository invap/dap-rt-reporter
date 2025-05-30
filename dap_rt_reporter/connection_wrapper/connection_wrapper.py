# Copyright (C) <2025>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from abc import ABC, abstractmethod

class ConnectionWrapper(ABC):
    def __init__(self, executable, executable_args):
        super().__init__()

        self.executable = executable
        self.executable_args = executable_args
        
    @abstractmethod
    def get_response(self):
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
    def set_breakpoints_source(self):
        pass

    @abstractmethod
    def continue_execution(self):
        pass

    @abstractmethod
    def next(self):
        pass

    @abstractmethod
    def evaluate(self):
        pass

    @abstractmethod
    def stack_trace(self):
        pass

    @abstractmethod
    def close(self):
        pass
