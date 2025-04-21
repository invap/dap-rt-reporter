# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
import argparse
import os
import tomllib
import time

from dap_rt_reporter.types import ReportEvent
from dap_rt_reporter.reporter import Reporter
from dap_rt_reporter.event.checkpoint_reached_event import CheckpointReachedEvent
from dap_rt_reporter.event.task_started_event import TaskStartedEvent
from dap_rt_reporter.event.task_finished_event import TaskFinishedEvent
from dap_rt_reporter.event.variable_value_assigned_event import (
    VariableValueAssignedEvent,
)
from dap_rt_reporter.event.clock_start import ClockStartEvent
from dap_rt_reporter.event.clock_pause import ClockPauseEvent
from dap_rt_reporter.event.clock_reset import ClockResetEvent
from dap_rt_reporter.event.clock_resume import ClockResumeEvent
from dap_rt_reporter.event.component_event import ComponentEvent

def read_toml(toml_path):
    with open(toml_path, "rb") as file:
        reporter_config = tomllib.load(file)["dap-rt-reporter"]
        sut = reporter_config["sut"]
        config_file = reporter_config["specification"]
    
    return sut, config_file


def run_experiment(sut, config_file, log_path):
    reporter = Reporter(sut, log_path)

    # Read each line and add corresponding events
    with open(config_file, "r") as workflow_file:
        workflow_reader = csv.reader(workflow_file, delimiter=",")

        for row in workflow_reader:
            # Split the breakpoint descriptor
            source_path, line, before = row[0].split(":")
            before = before == "b"

            event = row[1]
            event_name = row[2]

            args = []
            if len(row) > 3:
                args = row[3:]
            match event:
                case ReportEvent.CHECKPOINT_REACHED:
                    reporter.set_event(
                        CheckpointReachedEvent(
                            source_path=source_path,
                            line=int(line),
                            before=before,
                            name=event_name,
                        )
                    )
                case ReportEvent.TASK_STARTED:
                    reporter.set_event(
                        TaskStartedEvent(
                            source_path=source_path,
                            line=int(line),
                            before=before,
                            name=event_name,
                        )
                    )
                case ReportEvent.TASK_FINISHED:
                    reporter.set_event(
                        TaskFinishedEvent(
                            source_path=source_path,
                            line=int(line),
                            before=before,
                            name=event_name,
                        )
                    )
                case ReportEvent.VARIABLE_VALUE_ASSIGNED:
                    reporter.set_event(
                        VariableValueAssignedEvent(
                            source_path=source_path,
                            line=int(line),
                            before=before,
                            name=event_name,
                            expression=args[0],
                        )
                    )
                case ReportEvent.CLOCK_START:
                    reporter.set_event(
                        ClockStartEvent(
                            source_path=source_path,
                            line=int(line),
                            before=before,
                            name=event_name,
                        )
                    )
                case ReportEvent.CLOCK_PAUSE:
                    reporter.set_event(
                        ClockPauseEvent(
                            source_path=source_path,
                            line=int(line),
                            before=before,
                            name=event_name,
                        )
                    )
                case ReportEvent.CLOCK_RESUME:
                    reporter.set_event(
                        ClockResumeEvent(
                            source_path=source_path,
                            line=int(line),
                            before=before,
                            name=event_name,
                        )
                    )
                case ReportEvent.CLOCK_RESET:
                    reporter.set_event(
                        ClockResetEvent(
                            source_path=source_path,
                            line=int(line),
                            before=before,
                            name=event_name,
                        )
                    )
                case ReportEvent.COMPONENT_EVENT:
                    reporter.set_event(
                        ComponentEvent(
                            source_path=source_path,
                            line=int(line),
                            before=before,
                            name=event_name,
                            function_name=args[0],
                            function_params=args[1:],
                        )
                    )
                case _:
                    raise RuntimeError(f"Event {event} is undefined.")

    reporter.execute()

    reporter.close()


# Parser arguments
parser = argparse.ArgumentParser(
    prog="dap_reporter",
    description="Tool to to configure, execute the SUT and then report the execution trace report",
    usage="python3 dap_rt_reporter/dap_reporter.py --sut path_to_sut --desc path_to_desc --log path_to_log",
)
subparsers = parser.add_subparsers(dest="command_name")

run_parser = subparsers.add_parser("run")
run_parser.add_argument("--sut", help="binary of the program to report", required=True)
run_parser.add_argument("--desc", help="configuration file", required=True)
run_parser.add_argument("--log", help="log file to store report", required=True)
run_parser.add_argument("-f", help="force log rewrite", action="store_true")

toml_parser = subparsers.add_parser("toml", help="Configure dap-rt-reporter using toml files.")
toml_parser.add_argument("toml", help="Configure all reporter options with a toml file.")

args = parser.parse_args()

# toml override
if args.command_name == "toml":
    toml_path = args.toml
    # Check if path is valid
    if not (os.path.isfile(toml_path) or os.path.isdir(toml_path)):
        raise RuntimeError(f"No file or folder named {toml_path} exists.")

    if os.path.isfile(toml_path):
        sut, config_file = read_toml(toml_path)
        log_path = "experiments/" + config_file + "/" + str(time.time()) + "/exe-report.log"
        run_experiment(sut, config_file, log_path)
    else:
        for root, dirs, files in os.walk(toml_path):
            for file in files:
                if file.endswith(".toml"):
                    sut, config_file = read_toml(file)
                    log_path = "experiments/" + config_file + "/" + str(time.time) + "/exe-report.log"
                    run_experiment(sut, config_file, log_path)
else:
    sut = args.sut
    config_file = args.desc
    log_path = args.log
    force = args.f

    if not os.path.isfile(sut):
        raise RuntimeError(f"No file named {sut} exists.")
    if not os.path.isfile(config_file):
        raise RuntimeError(f"No file named {config_file} exists.")
    if os.path.isfile(log_path) and not force:
        raise RuntimeError(f"Warning: {log_path} already exists, use -f to force rewrite.")

    run_experiment(sut, config_file, log_path)