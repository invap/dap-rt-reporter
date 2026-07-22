# Copyright (C) <2026>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
from typing import Any

from dap_rt_reporter.event_writer.event_writer import EventWriter


class FileWriter(EventWriter):
    def __init__(self, output_file: str):
        super().__init__()

        self.output_file = output_file
        self.file = open(self.output_file, "w", encoding="utf8")
        self.writer = csv.writer(self.file, delimiter=",", quotechar='"')

    def write(self, event: list[Any]):
        self.writer.writerow(event)

    def close(self):
        self.file.close()
