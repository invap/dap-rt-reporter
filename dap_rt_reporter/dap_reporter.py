# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
import argparse

from dap_rt_reporter.constants import ReportEvent
from dap_rt_reporter.reporter import Reporter

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="dap_reporter",
                                     description="")
    
    parser.add_argument('sut', help="binary of the program to report")
    parser.add_argument('--desc', help="configuration file")
    parser.add_argument('--log', help="log file to store report")

    args = parser.parse_args()
    
    sut = args.sut
    config_file = args.desc
    log_path = args.log

    #sut = "tests/integration/resources/simple_test/target/debug/simple_test"
    #log_path = "checkpoint_init_log_file.log"
    #config_file = "tests/integration/resources/simple_test_config.csv"

    reporter = Reporter(sut, log_path)

    # Read each line and add corresponding events
    with open(config_file, "r") as workflow_file:
        workflow_reader = csv.reader(workflow_file, delimiter=",")

        for row in workflow_reader:
            event_type = row[1]
            event_name = row[2]

            # Split the breakpoint descriptor
            source_path, line, before = row[0].split(":")
            before = before == "b"

            match event_type:
                case ReportEvent.CHECKPOINT_REACHED:
                    reporter.set_checkpoint(
                        source_path=source_path,
                        line=line,
                        before=before,
                        checkpoint_name=event_name,
                    )

    reporter.execute()

    reporter.stop()
