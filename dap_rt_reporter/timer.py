# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import time

class Timer:
    def __init__(self) -> None:
        self.timer = 0
        self.difference = 0
        self.reference = 0

    def start(self):
        self.difference = 0

    def stop(self):
        self.timer = 1e6*(time.time() - self.difference)
        self.reference = time.time()

    def continue_(self):
        self.difference += time.time() - self.reference