# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

class Listener:
    def __init__(self) -> None:
        self.events = {}


    def add_event(self, location, event_type, event_name, *kwargs):
        if not (location in self.events):
            #self.events[]
            pass