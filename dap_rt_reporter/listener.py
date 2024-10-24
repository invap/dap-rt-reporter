# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
import csv

class Listener:
    def __init__(self) -> None:
        self.events = {}

    def listen(self, response: bytes, report_file):
        """Listens to responses from debugger and gives instructions to reporter."""

        csv_writter = csv.writer(report_file, delimiter=',')

        #print(self.events)
        response_list = self.parse_dap_response(response)
        for message in response_list:
            if message['type'] == 'event':
                if message['event'] == 'stopped':
                    if message['body']['hitBreakpointIds'][0] in self.events:
                        id = message['body']['hitBreakpointIds'][0]
                        for event in self.events[id]:
                            csv_writter.writerow(['timestamp', event['event_type'], event['event_name']])
                        return 'continue'
                    else:
                        # TODO: Add exception
                        print("Breakpoint hit not associated with any event.")
            elif message['type'] == 'response':
                pass
        return None

    def parse_dap_response(self, response: bytes):
        """Converts DAP response to dictionary form.
        Assumes complete message.
        """

        response_list = []
        while b'\r\n\r\n' in  response:
            length, response = response.split(b'\r\n\r\n', 1)

            length = int(length.split(b':')[1])
            response_list.append(json.loads(response[:length]))
            response = response[length:]

        return response_list

    def add_event(self, breakpoint_id, source_path, line, position, event_type, event_name, *kwargs):

        if breakpoint_id not in self.events:
            self.events[breakpoint_id] = [{'event_type': event_type, 'event_name': event_name, 'position': position}]
            # TODO: Add kwargs handling
        else:
            self.events[breakpoint_id].append({'event_type': event_type, 'event_name': event_name, 'position': position})