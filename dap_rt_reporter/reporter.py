# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from dap_rt_reporter.listener import Listener
from dap_rt_reporter.constants import Actions, ReportEvent, DAPMessage, DAPEvent
from dap_rt_reporter.listener_functions import write_checkpoint_reached
import json

class Reporter:
    """Connects DAP client and GDB then uses output to report
    program behaviour.
    """

    # TODO: Add dap wrapper as parameter
    def __init__(self, debugger_connection, listener: Listener) -> None:
        self.debugger_connection = debugger_connection
        self.listener = listener

        self.executable_path = None
        self.execution_trace_log_path = None

        #Used for saving events   
        self.events = []

    def add_executable(
            self, executable_path: str, execution_trace_log_path: str
            ) -> None:
        """Saves executable and log files."""

        self.executable_path = executable_path
        self.execution_trace_log_path = execution_trace_log_path

    def execute(self) -> bytes:
        """Begins program execution and report."""

        if self.executable_path == None:
            raise AttributeError("No executable defined, see add_executable().")

        report_file = open(self.execution_trace_log_path, 'w')
        
        self.debugger_connection.start(self.executable_path)
        self._set_up()

        # Start execution
        encoded_response = self.debugger_connection.launch()
        terminated = False
        while not terminated:
            #print(encoded_response)
            if encoded_response != None:
                response_list = self.parse_dap_response(encoded_response)
                encoded_response = None

            for response in response_list:
                if response['type'] == DAPMessage.EVENT:
                    if response['event'] == DAPEvent.STOPPED:
                        if response['body']['reason'] == 'breakpoint':
                            self.listener.handle_response(response, report_file)
                            encoded_response = self.debugger_connection.continue_execution()
                    elif response['event'] == DAPEvent.TERMINATED:
                        terminated = True
                elif response['type'] == DAPMessage.RESPONSE:
                    pass

            if encoded_response == None:
                encoded_response = self.debugger_connection.idle()

            
        report_file.close()

        return terminated
            

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
    
    def _set_up(self):
        """Sets breakpoints and gives the events to listener."""

        # Create breakpoint locations
        breakpoint_locations = {}
        for event in self.events:
            event_values = {
                'before': event['before'],
                'name': event['name'],
                'type': event['type'],
                'args': event['args'],
                'functions': event['functions']
                }
            line = event['line']
            source_path = event['source_path']
            if source_path not in breakpoint_locations:
                breakpoint_locations[source_path] = {str(line): [event_values]}
            else:
                if line not in breakpoint_locations[source_path]:
                    breakpoint_locations[source_path][line] = [event_values]
                else:
                    breakpoint_locations[source_path][line].append([event_values])


        breakpoint_id = 1
        # Set breakpoints for each source
        for source_path in breakpoint_locations:
            # Convert the source and lines to DAP format
            lines_dap_form = []
            for line in breakpoint_locations[source_path]:
                lines_dap_form.append({'line': int(line)})
                
                for event in breakpoint_locations[source_path][line]:
                    # Add checkpoint reached event to listener
                    self.listener.add_event(breakpoint_id, event)
                    breakpoint_id += 1
            
            source = source_path[source_path.rfind('/')+1:]
            source_dap_form = {"name": source, "path": source_path}

            response = self.debugger_connection.set_breakpoints_source(source_dap_form, lines_dap_form)
            #print(response)


    def set_checkpoint(self, source_path: str, line: int, 
                       before: bool, checkpoint_name: str
                       ) -> None:

        new_checkpoint = {
            'source_path': source_path, 
            'line': line,
            'before': before, 
            'name': checkpoint_name, 
            'type': ReportEvent.CHECKPOINT_REACHED,
            'args': {},
            'functions': [write_checkpoint_reached]
            }
        self.events.append(new_checkpoint)
            
