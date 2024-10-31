# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
import dap_rt_reporter.listener_functions
from dap_rt_reporter.constants import DAPMessage, DAPEvent

class Listener:
    def __init__(self) -> None:
        self.events = {}

    def handle_response(self, timestamp, response, report_file, debugger_connection):
        """Listens to responses from debugger and gives instructions to reporter."""

        csv_writter = csv.writer(report_file, delimiter=',')

        id = response['body']['hitBreakpointIds'][0]

        # Before events
        for event in self.events[id]['b']:
            for func in event['functions']:
                    func(timestamp, event, csv_writter)

        # After events
        if len(self.events[id]['a']):
            debugger_connection.next()
            
            for event in self.events[id]['a']:
                for func in event['functions']:
                    func(timestamp, event, csv_writter)


    def add_event(self, breakpoint_id, event):
        """Adds event to listen list, uses breakpoint id as identifier."""

        if breakpoint_id in self.events:
            if event['before']:
                self.events[breakpoint_id]['b'].append(event)
            else:
                self.events[breakpoint_id]['a'].append(event)
        else:
            self.events[breakpoint_id] = {}
            if event['before']:
                self.events[breakpoint_id]['b'] = [event]
                self.events[breakpoint_id]['a'] = []
            else:
                self.events[breakpoint_id]['b'] = []
                self.events[breakpoint_id]['a'] = [event]