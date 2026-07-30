# Copyright (C) <2026>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import _csv
import csv
from io import TextIOWrapper
from typing import Any, override

from dap_rt_reporter.event_writer.event_writer import EventWriter


class FileWriter(EventWriter):
    def __init__(self, output_file: str):
        super().__init__()

        self.output_file: str = output_file
        self.file: TextIOWrapper = open(self.output_file, "w", encoding="utf8")
        self.writer: _csv.Writer = csv.writer(self.file, delimiter=",", quotechar='"')

    @override
    def write(self, event: list[Any]):
        self.writer.writerow(event)

    @override
    def close(self):
        self.file.close()
