# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import json

class Listener:
    def __init__(self) -> None:
        self.events = {}

    def listen(self, response: bytes):
        """Listens to responses from debugger and gives instructions to reporter."""

        response_list = self.parse_dap_response(response)
        
        for message in response_list:
            if(message['type'] == 'event'):
                if(message['event'] == 'stopped'):
                    print('Checkpoint Reached')

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

    def add_event(self, source_path, line, position, event_type, event_name, *kwargs):

        location = source_path + ':' + str(line) + ':' + position
        if location not in self.events:
            self.events[location] = {'event_type': event_type, 'event_name': event_name, 'breakpoint_id': -1}

            # TODO: Add kwargs handling