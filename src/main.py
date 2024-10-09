# Copyright (C) <2024>  INVAP S.E.
#
# Test file for add_executable and execute methods.
# Expected behaviour is:
# First response is capabilities from GDB
# Doesn't check if initialize is succesuful
# Second response is launch response, then start sequence, ends with exited event

from reporter import Reporter

if __name__ == "__main__":
    reporter = Reporter()

    response = reporter.add_executable("../test/main", "path")
    print(response)
    response = reporter.execute()
    print(response)