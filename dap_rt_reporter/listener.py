# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
import dap_rt_reporter.listener_functions
from dap_rt_reporter.constants import DAPMessage, Actions, DAPEvent

class Listener:
    def __init__(self) -> None:
        self.events = {}

    def handle_response(self, response, report_file):
        """Listens to responses from debugger and gives instructions to reporter."""

        csv_writter = csv.writer(report_file, delimiter=',')

        id = response['body']['hitBreakpointIds'][0]
        if id in self.events:
            for event in self.events[id]:
                for func in event['functions']:
                    func(csv_writter, event)

    def add_event(self, breakpoint_id, event):
        """Adds event to listen list, uses breakpoint id as identifier."""

        if breakpoint_id not in self.events:
            self.events[breakpoint_id] = [event]
        else:
            self.events[breakpoint_id].append(event)