# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
import argparse
import os
import signal
import logging
import tomllib

from dap_rt_reporter.rabbitmq_connection.rabbitmq_server_configs import (
    rabbitmq_server_config,
    rabbitmq_event_exchange_config,
)

from dap_rt_reporter.types import ReportEventSubType
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

# Parser arguments
parser = argparse.ArgumentParser(
    prog="dap_reporter",
    description="Tool to configure, execute the SUT and then report the execution trace report",
    usage="""
        python3 -m dap_reporter.py --sut path_to_sut --desc path_to_desc --log path_to_log
        If the log file already exists you can force rewrite with -f flag.
        To pass arguments to the executable use --sut-args, for example --sut-args "-p 1234".
        """,
)

parser.add_argument("--sut", help="binary of the program to report", required=True)
parser.add_argument("--desc", help="configuration file", required=True)
parser.add_argument("--log", help="log file to store report", default="execution.csv")
parser.add_argument("-f", help="force log rewrite", action="store_true")
parser.add_argument("--sut-args", help="add argument for SUT", nargs="+")
parser.add_argument(
    "--debugger",
    "-deb",
    help="debugger selection",
    choices=["gdb", "lldb"],
    default="gdb",
)
parser.add_argument(
    "--log-level",
    help="select logging level",
    choices=["info", "debug", "warning", "error", "critical"],
    default="info",
)

# RabbitMQ configuration arguments
parser.add_argument(
    "--rabbitmq-config-file", help="path to the rabbitmq configuration file"
)

args = parser.parse_args()

sut = args.sut
config_file = args.desc
log_path = args.log
force = args.f
sut_args = " ".join(args.sut_args) if args.sut_args else ""
debugger_selection = args.debugger

# Checks
if not os.path.isfile(sut):
    raise RuntimeError(f"No file named {sut} exists.")
if not os.path.isfile(config_file):
    raise RuntimeError(f"No file named {config_file} exists.")
if os.path.isfile(log_path) and not force:
    raise RuntimeError(f"Warning: {log_path} already exists, use -f to force rewrite.")

# Logging level
match args.log_level:
    case "info":
        logging_level = logging.INFO
    case "debug":
        logging_level = logging.DEBUG
    case "warning":
        logging_level = logging.WARNING
    case "error":
        logging_level = logging.ERROR
    case "critical":
        logging_level = logging.CRITICAL
    case _:
        raise RuntimeError(f"Level {args.log_level} is not a valid option.")

logging.basicConfig(
    encoding="utf-8", level=logging_level, format="%(levelname)s::%(message)s"
)

use_rabbitmq = False
if args.rabbitmq_config_file:
    if not os.path.isfile(args.rabbitmq_config_file):
        raise RuntimeError(f"No file named {args.rabbitmq_config_file}")
    
    # RabbitMQ configuration
    use_rabbitmq = True
    # Server configuration
    with open(args.rabbitmq_config_file, "rb") as rabbitmq_file:
        rabbitmq_config: dict = tomllib.load(rabbitmq_file)["exchange"]["events"]

    rabbitmq_server_config.host = rabbitmq_config
    rabbitmq_server_config.port = args.port
    rabbitmq_server_config.user = args.user
    rabbitmq_server_config.password = args.password
    # Exchange configuration
    rabbitmq_event_exchange_config.exchange = args.exchange

reporter = Reporter(sut, log_path, sut_args, debugger_selection, use_rabbitmq)

logging.info("Reading configuration file")
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
            case ReportEventSubType.CHECKPOINT_REACHED:
                reporter.set_event(
                    CheckpointReachedEvent(
                        source_path=source_path,
                        line=int(line),
                        before=before,
                        name=event_name,
                    )
                )
            case ReportEventSubType.TASK_STARTED:
                reporter.set_event(
                    TaskStartedEvent(
                        source_path=source_path,
                        line=int(line),
                        before=before,
                        name=event_name,
                    )
                )
            case ReportEventSubType.TASK_FINISHED:
                reporter.set_event(
                    TaskFinishedEvent(
                        source_path=source_path,
                        line=int(line),
                        before=before,
                        name=event_name,
                    )
                )
            case ReportEventSubType.VARIABLE_VALUE_ASSIGNED:
                reporter.set_event(
                    VariableValueAssignedEvent(
                        source_path=source_path,
                        line=int(line),
                        before=before,
                        name=event_name,
                        expression=args[0],
                    )
                )
            case ReportEventSubType.CLOCK_START:
                reporter.set_event(
                    ClockStartEvent(
                        source_path=source_path,
                        line=int(line),
                        before=before,
                        name=event_name,
                    )
                )
            case ReportEventSubType.CLOCK_PAUSE:
                reporter.set_event(
                    ClockPauseEvent(
                        source_path=source_path,
                        line=int(line),
                        before=before,
                        name=event_name,
                    )
                )
            case ReportEventSubType.CLOCK_RESUME:
                reporter.set_event(
                    ClockResumeEvent(
                        source_path=source_path,
                        line=int(line),
                        before=before,
                        name=event_name,
                    )
                )
            case ReportEventSubType.CLOCK_RESET:
                reporter.set_event(
                    ClockResetEvent(
                        source_path=source_path,
                        line=int(line),
                        before=before,
                        name=event_name,
                    )
                )
            case ReportEventSubType.COMPONENT_EVENT:
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

signal.signal(signal.SIGINT, reporter.kill)
reporter.execute()
reporter.close()
