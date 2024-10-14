# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Test file for add_executable and execute methods.
# Doesn't check if initialize is succesuful
# Should print launch sequence and end with terminate

from reporter import Reporter
from connection_wrapper import ConnectionWrapper

if __name__ == "__main__":
    # First start debugger with DAP support
    # TODO: Implement with gdb handler

    connection = ConnectionWrapper()
    reporter = Reporter(connection)

    # Load program
    # TODO: implement with the reporter
    reporter.add_executable("../test/main", "../test/main_log_file.log")

    # Configure events
    # Reporter.add_check_point_reached(path:line_number)
    #   internally should do:
    #       - Configure debugger to stop (add breackpoint)
    #       - Configure listener to recognize the event and store the trace execution.
    # TODO: implement

    # Initialize Rerporter to listen the events.
    #response = reporter.set_up()
    #print(response)
    #response = reporter.set_checkpoint(...)
    #print(response)

    # Start execution
    response = reporter.execute()
    print(response)

    # Write execution trace report Listening to Debugger stop
    # Reporter.print response print the stored trace execution.
    #ReportListener.handle_response(response)
    #print(response)
