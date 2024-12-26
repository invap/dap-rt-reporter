# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
import re

from dap_rt_reporter.types import DAPMessage


def write_process_event(timestamp, event, csv_writer, debugger_connection):
    csv_writer.writerow(
        [
            timestamp,
            event["type"],
            event["sub_type"],
            get_event_name(event["name"], debugger_connection),
        ]
    )


def write_variable_value_assign(timestamp, event, csv_writer, debugger_connection):
    csv_writer.writerow(
        [
            timestamp,
            event["type"],
            event["sub_type"],
            get_event_name(event["name"], debugger_connection),
            evaluate_expression(event["args"]["variable"], debugger_connection),
        ]
    )


def evaluate_expression(expression, debugger_connection):
    """Evaluate expression in current context inside SUT."""

    if ("{" and "}") in expression:
        expression = re.findall(r"{(.*?)}", expression)[0]

    result = None
    encoded_response = debugger_connection.evaluate(expression)
    # encoded_response = debugger_connection.evaluate("_x")
    while result is None:
        response_list = parse_dap_response(encoded_response)
        encoded_response = b""

        for response in response_list:
            if (
                response["type"] == DAPMessage.RESPONSE
                and response["command"] == "evaluate"
            ):
                if response["success"]:
                    result = response["body"]["result"]
                else:
                    raise RuntimeError(response["message"])
        if not encoded_response:
            encoded_response = debugger_connection.idle()

    return result


def get_event_name(event_name_raw, debugger_connection):
    """Evaluate expressions inside the event name."""

    event_name = re.sub(
        r"{(.*?)}",
        lambda match: evaluate_expression(match.group(), debugger_connection),
        event_name_raw,
    )

    return event_name


def parse_dap_response(response: bytes):
    """Converts DAP response to dictionary form.
    Assumes complete message.
    """
    response_list = []
    if response:
        while b"\r\n\r\n{" in response:
            length, response = response.split(b"\r\n\r\n", 1)

            length = int(length.split(b":")[1])
            response_list.append(json.loads(response[:length]))
            response = response[length:]

    return response_list
