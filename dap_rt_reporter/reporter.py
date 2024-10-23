# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

from dap_rt_reporter.listener import Listener

class Reporter:
    """Connects DAP client and GDB then uses output to report
    program behaviour.
    """

    # TODO: Add dap wrapper as parameter
    def __init__(self, debugger_connection, listener: Listener) -> None:
        self.debugger_connection = debugger_connection
        self.listener = listener

        self.breakpoints_locations = {}

        self.executable_path = None
        self.execution_trace_log_path = None

    def add_executable(
            self, executable_path: str, execution_trace_log_path: str
            ) -> None:
        """Saves executable and log files."""

        self.executable_path = executable_path
        self.execution_trace_log_path = execution_trace_log_path

    def execute(self) -> bytes:
        """Sends launch request to GDB, begins program execution."""

        if self.executable_path == None:
            raise AttributeError("No executable defined, see add_executable().")

        # Set breakpoints
        self._set_up()

        # Start execution
        response = self.debugger_connection.launch(self.executable_path)
        
        # TODO: Set another condition for while loop
        while response != None:
            print(response)
            actions = self.listener.listen(response)
            response = None
            
    
    def _set_up(self):

        # Add checkpoint reached event to listener
        #self.listener.add_event(source_path, line, position, 
        #                        'checkpoint_reached', checkpoint_name)


        # Set breakpoints for each source
        for source_path in self.breakpoints_locations.keys():
            # Convert the source and lines to DAP format
            lines_dap_form = []
            for line in self.breakpoints_locations[source_path]:
                lines_dap_form.append({'line': line})
            
            source = source_path[source_path.rfind('/')+1:]
            source_dap_form = {"name": source, "path": source_path}

            response = self.debugger_connection.set_breakpoints_source(source_dap_form, lines_dap_form)
            print(response)

    def set_checkpoint(self, source_path: str, line: int, 
                       position: str, checkpoint_name: str
                       ) -> None:

        # Save checkpoint event
        checkpoint_values = {'position': position, 'name': checkpoint_name, 'type': 'checkpoint_reached'}

        if source_path not in self.breakpoints_locations:
            self.breakpoints_locations[source_path] = {str(line): [checkpoint_values]}
        else:
            if line not in self.breakpoints_locations[source_path]:
                self.breakpoints_locations[source_path][line] = [checkpoint_values]
            else:
                self.breakpoints_locations[source_path][line].append([checkpoint_values])
            
