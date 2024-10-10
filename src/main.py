# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Test file for add_executable and execute methods.
# Expected behaviour is:
# First response is capabilities from GDB
# Doesn't check if initialize is succesuful
# Second response is launch response, then start sequence, ends with exited event

from reporter import Reporter

if __name__ == "__main__":
    # First start debugger with DAP support
    # TODO: Implement with gdb handler

    reporter = Reporter()

    # Load program
    # TODO: implemt with the reporter
    reporter.add_executable("../test/main", "path")

    # Configure events
    # Reporter.add_check_point_reached(path:line_number)
    #   internally should do:
    #       - Configure debugger to stop (add breackpoint)
    #       - Configure listener to recognize the event and store the trace execution.
    # TODO: implement

    # Initialize Rerporter to listen the events.
    response = reporter.initialize()
    print(response)

    # Start execution
    response = reporter.execute()

    # Write execution trace report Listening to Debugger stop
    # Reporter.print response print the stored trace execution.
    print(response)
