# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later


def write_checkpoint_reached(timestamp, event, csv_writer):
    csv_writer.writerow([timestamp, event["type"], event["name"]])

