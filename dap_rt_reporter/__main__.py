# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import argparse
import csv
import logging
import os
import signal

from dap_rt_reporter.event.checkpoint_reached_event import (
    CheckpointReachedEvent,
)
from dap_rt_reporter.event.clock_pause import ClockPauseEvent
from dap_rt_reporter.event.clock_reset import ClockResetEvent
from dap_rt_reporter.event.clock_resume import ClockResumeEvent
from dap_rt_reporter.event.clock_start import ClockStartEvent
from dap_rt_reporter.event.component_event import ComponentEvent
from dap_rt_reporter.event.task_finished_event import TaskFinishedEvent
from dap_rt_reporter.event.task_started_event import TaskStartedEvent
from dap_rt_reporter.event.variable_value_assigned_event import (
    VariableValueAssignedEvent,
)
from dap_rt_reporter.rabbitmq_connection import rabbitmq_server_connections
from dap_rt_reporter.reporter import Reporter
from dap_rt_reporter.rt_reporter import RTReporterBuilder
from dap_rt_reporter.types import ReportEventSubType

logger = logging.getLogger("dap_rt_reporter")


def dap_rt_reporter_runner(
    sut: str,
    report_file: str,
    sut_args: str,
    debugger_selection: str,
    use_rabbitmq: bool,
    config_file: str,
):
    """Run Reporter with given configuration.

    Args:
        sut (str): Program to report.
        report_file (str): Path to the file to store the event trace.
        sut_args (str): Arguments for the SUT.
        debugger_selection (str): Debugger selection for reporting.
        use_rabbitmq (bool): Flag to turn the use of RabbitMQ to send the event trace.
        config_file (str): Event configuration file.
    """

    # Set SIGINT handler to handle closing during execution
    def sigint_handler(signum, frame):
        logger.debug("Received SIGINT signal: %s and segnum %d", frame, signum)
        reporter.kill()

    signal.signal(signal.SIGINT, sigint_handler)

    # Create and configure reporter builder
    reporter_builder = RTReporterBuilder()

    match debugger_selection:
        case "gdb":
            reporter_builder.with_gdb(sut, sut_args)
        case "lldb":
            reporter_builder.with_lldb(sut, sut_args)

    if use_rabbitmq:
        reporter_builder.with_rabbitmq_writer()
    else:
        reporter_builder.with_file_writer(report_file)

    # Create reporter
    reporter = reporter_builder.build()

    parse_configuration_file(reporter, config_file)

    # Execute SUT with breakpoints
    reporter.execute()

    # Close reporter
    reporter.close()


def parse_configuration_file(reporter: Reporter, config_file: str):
    """Parse configuration file and set events.

    Args:
        reporter (Reporter): Reporter.
        config_file (str): Event configuration file.

    Raises:
        RuntimeError: _description_
    """
    logger.info("Reading configuration file")
    # Read each line and add corresponding events
    with open(config_file, "r", encoding="utf8") as events_file:
        events_reader = csv.reader(events_file, delimiter=",")

        for row in events_reader:
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


def main():
    # Parser arguments
    parser = argparse.ArgumentParser(
        prog="dap_reporter",
        description="""Tool to configure, execute the SUT and
        then report the execution trace report""",
        usage="""
            python3 -m dap_reporter.py --sut SUT --configuration-file CONFIG_FILE --report-file REPORT_FILE
            If the log file already exists you can force rewrite with -f flag.
            To pass arguments to the executable use --sut-args, for example --sut-args "-p 1234".
            """,
        allow_abbrev=False,
    )

    parser.add_argument(
        "-s",
        "--sut",
        help="path to the binary of the program to report",
        required=True,
    )
    parser.add_argument(
        "--configuration-file",
        "--cf",
        help="path to the events configuration file",
        required=True,
    )
    parser.add_argument(
        "--report-file",
        "--rf",
        help="path to the file to store report",
        default="execution.csv",
    )
    parser.add_argument(
        "--rabbitmq-config-file",
        "--rcf",
        help="path to the TOML file with the RabbitMQ server configuration.",
        default="",
    )
    parser.add_argument(
        "-f", "--force", help="force report file rewrite", action="store_true"
    )
    parser.add_argument("--sut-args", help="add argument for SUT", nargs="+")
    parser.add_argument(
        "-d",
        "--debugger",
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
    parser.add_argument(
        "--log-file",
        help="select where to display logs, defaults to console",
        required=False,
    )

    args = parser.parse_args()

    sut = args.sut
    config_file = args.configuration_file
    report_file = args.report_file
    force = args.force
    sut_args = " ".join(args.sut_args) if args.sut_args else ""
    debugger_selection = args.debugger

    # Checks
    if not os.path.isfile(sut):
        raise RuntimeError(f"No file named {sut} exists.")
    if not os.path.isfile(config_file):
        raise RuntimeError(f"No file named {config_file} exists.")
    if os.path.isfile(report_file) and not force:
        raise RuntimeError(
            f"Warning: {report_file} already exists, use -f to force rewrite."
        )

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
            raise RuntimeError(
                f"Level {args.log_level} is not a valid option."
            )

    # Logger configuration
    logging.basicConfig(
        encoding="utf-8",
        level=logging_level,
        format="%(asctime)s : [%(name)s:%(levelname)s] - %(message)s",
    )

    formatter = logging.Formatter(
        "%(asctime)s : [%(name)s:%(levelname)s] - %(message)s"
    )

    logging.getLogger().handlers.clear()
    if args.log_file is None:
        handler = logging.StreamHandler()
    else:
        handler = logging.FileHandler(args.log_file)

    handler.setLevel(logging_level)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    # RabbitMQ configuration
    USE_RABBITMQ = False
    if os.path.isfile(args.rabbitmq_config_file):
        USE_RABBITMQ = True
        rabbitmq_server_connections.build_rabbitmq_connection_from_toml(
            args.rabbitmq_config_file
        )
        logger.info(
            "RabbitMQ connection established, writing results to exchange."
        )
    else:
        logger.info(
            "No valid RabbitMQ configuration file, saving results to file."
        )

    dap_rt_reporter_runner(
        sut,
        report_file,
        sut_args,
        debugger_selection,
        USE_RABBITMQ,
        config_file,
    )

    if USE_RABBITMQ:
        rabbitmq_server_connections.rabbitmq_event_server_connection.close()


if __name__ == "__main__":
    main()
