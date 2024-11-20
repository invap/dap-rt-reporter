# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
import argparse
import os

from dap_rt_reporter.types import ReportEvent
from dap_rt_reporter.reporter import Reporter

# Parser arguments
parser = argparse.ArgumentParser(
    prog="dap_reporter",
    description="Tool to to configure, execute the SUT and then report the execution trace report",
    usage="python3 dap_rt_reporter/dap_reporter.py --sut path_to_sut --desc path_to_desc --log path_to_log",
)

parser.add_argument("--sut", help="binary of the program to report", required=True)
parser.add_argument("--desc", help="configuration file", required=True)
parser.add_argument("--log", help="log file to store report", required=True)
parser.add_argument("-f", help="force log rewrite", action="store_true")

args = parser.parse_args()

sut = args.sut
config_file = args.desc
log_path = args.log
force = args.f

# Checks
if not os.path.isfile(sut):
    raise RuntimeError(f"No file named {sut} exists.")
if not os.path.isfile(config_file):
    raise RuntimeError(f"No file named {config_file} exists.")
if os.path.isfile(log_path) and not force:
    raise RuntimeError(f"Warning: {log_path} already exists, use -f to force rewrite.")

reporter = Reporter(sut, log_path)

# Read each line and add corresponding events
with open(config_file, "r") as workflow_file:
    workflow_reader = csv.reader(workflow_file, delimiter=",")

    for row in workflow_reader:
        # Split the breakpoint descriptor
        source_path, line, before = row[0].split(":")
        before = before == "b"

        event_type = row[1]
        event_name = row[2]

        args = []
        if len(row) > 3:
            args = row[3:]
        match event_type:
            case ReportEvent.CHECKPOINT_REACHED:
                reporter.set_checkpoint(
                    source_path=source_path,
                    line=int(line),
                    before=before,
                    checkpoint_name=event_name,
                )
            case ReportEvent.TASK_STARTED:
                reporter.set_task_started(
                    source_path=source_path,
                    line=int(line),
                    before=before,
                    ts_name=event_name
                )
            case ReportEvent.VARIABLE_VALUE_ASSIGN:
                reporter.set_variable_value_assign(
                    source_path=source_path,
                    line=int(line),
                    before=before,
                    vva_name=event_name,
                    variable=args[0],
                )

reporter.execute()

reporter.stop()
