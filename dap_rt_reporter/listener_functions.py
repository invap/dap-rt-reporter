# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
from dap_rt_reporter.types import DAPMessage


def write_checkpoint_reached(timestamp, event, csv_writer, debugger_connection):
    csv_writer.writerow([timestamp, event["type"], event["sub_type"], event["name"]])


def parse_dap_response(response: bytes):
    """Converts DAP response to dictionary form.
    Assumes complete message.
    """
    response_list = []
    if response is not None:
        while b"\r\n\r\n" in response:
            length, response = response.split(b"\r\n\r\n", 1)

            length = int(length.split(b":")[1])
            response_list.append(json.loads(response[:length]))
            response = response[length:]

    return response_list


def write_variable_value_assign(timestamp, event, csv_writer, debugger_connection):
    result = None
    encoded_response = debugger_connection.evaluate(event["args"]["variable"])
    #encoded_response = debugger_connection.evaluate("_x")
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

    csv_writer.writerow(
        [timestamp, event["type"], event["sub_type"], event["name"], result]
    )
