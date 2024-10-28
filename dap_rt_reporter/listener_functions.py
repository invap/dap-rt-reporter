# Copyright (C) <2024>  INVAP S.E.
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv

def write_checkpoint_reached(csv_writter, event):
        csv_writter.writerow(['timestamp', event['type'], event['name']])