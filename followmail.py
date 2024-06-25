#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: se ts=4 et syn=python:

# created by: matteoguadrini
# followmail -- followmail
#
#     Copyright (C) 2024 Matteo Guadrini <matteo.guadrini@hotmail.it>
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Main module of followmail program."""

# region imports
import argparse
import gzip
import os
import re

from collections import namedtuple

from tablib import Dataset

# endregion

# region globals
__version__ = "0.0.1"
LogLine = namedtuple(
    "LogLine", ["date", "time", "server", "queue", "smtpid", "message"]
)


# endregion


# region functions
def get_args():
    """Get command line arguments"""

    parser = argparse.ArgumentParser(
        description="postfix log parser to follow a mail addresses",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--version",
        "-V",
        help="print version",
        action="version",
        version="%(prog)s " + __version__,
    )
    parser.add_argument(
        "--verbose",
        "-v",
        help="print with verbosity",
        action="store_true",
    )
    parser.add_argument(
        "--to",
        "-t",
        help="email address into to field",
        metavar="mail_address",
        type=str,
        action="store",
    )
    parser.add_argument(
        "--from",
        "-f",
        help="email address into from field",
        dest="from_",
        metavar="mail_address",
        type=str,
        action="store",
    )
    parser.add_argument(
        "-l",
        "--maillog",
        help="input maillog file",
        metavar="path",
        type=str,
        default="/var/log/maillog",
    )
    parser.add_argument(
        "-q",
        "--queue",
        metavar="queue_name",
        help="name of postfix queue",
        default="postfix",
    )

    args = parser.parse_args()

    # Check maillog file exists
    if not os.path.isfile(args.maillog):
        parser.error(f'maillog file "{args.maillog}" does not exists')

    # Check flags
    if not args.to and not args.from_:
        parser.error('unspecified filter "--to" or "--from"')

    # Validate email address
    if args.to and "@" not in args.to:
        parser.error("specified a valid email address")

    if args.from_ and "@" not in args.from_:
        parser.error("specified a valid email address")

    return args


def print_verbose(verbosity: bool, *messages: str):
    """Print verbose messages

    :param verbosity: boolean to activate verbose print
    """
    if verbosity:
        print("debug:", *messages)


def search_by_smtpid(smtpid: str, log: str, pattern: re.Pattern):
    """Search log lines by smtp id
    
    :param smtpid: string of smtp is
    :param log: opened log file
    :param pattern: regexp pattern
    :return: List[tuple]
    """
    rows = list()

    # Define function to open log
    open_log = gzip.open if log.endswith("gz") else open

    # Process log file
    with open_log(log, "rt") as maillog_file:
        for line in maillog_file:
            # Split line into single variable
            line = re.findall(pattern, line)

            # Skip line if not in pattern
            if not line:
                continue

            line = [part for part in line[0]]
    
            # Make a LogLine object
            logline = LogLine(
                date=line[0],
                time=line[1],
                server=line[2],
                queue=line[3],
                smtpid=line[4],
                message=line[5],
            )

            # Match smtp id
            if smtpid == logline.smtpid:
                rows.append(logline)

                # End of flow
                if "status" in logline.message:
                    break

    return rows


# region scripts
def main():
    """Main function"""

    # Define global for a script
    args = get_args()
    verbose = args.verbose
    # Empty Dataset
    data = Dataset(headers=("date", "time", "server", "queue", "smtpid", "message"))
    print_verbose(verbose, "start followmail")
    # Define filters
    to = args.to
    if to:
        print_verbose(verbose, f"add {to} into filters")
    from_ = args.from_
    if from_:
        print_verbose(verbose, f"add {from_} into filters")
    maillog = args.maillog
    print_verbose(verbose, f"add {maillog} into filters")
    queue = args.queue
    print_verbose(verbose, f"add {queue} into filters")

    # Define pattern regexp
    pattern = re.compile(
        r"(^[A-Za-z]{3}\s\d{1,2})\s(\d{2}:\d{2}:\d{2})\s(\w+)\s(.*/.*\[\d+]):\s(\w{10,15}):\s(.*)"
    )
    # Define function to open log
    open_log = gzip.open if maillog.endswith("gz") else open

    # Process log file
    with open_log(maillog, "rt") as maillog_file:
        for line in maillog_file:

            # Split line into single variable
            line = re.findall(pattern, line)

            # Skip line if not in pattern
            if not line:
                continue

            line = [part for part in line[0]]

            # Make a LogLine object
            logline = LogLine(
                date=line[0],
                time=line[1],
                server=line[2],
                queue=line[3],
                smtpid=line[4],
                message=line[5],
            )

            # Filter queue
            if queue not in logline.queue:
                continue

            # Filter to and from
            if str(to) not in logline.message and str(from_) not in logline.message:
                continue

            print_verbose(verbose, f"found a log line {logline}")

            # Find lines through smtp id
            lines = search_by_smtpid(logline.smtpid, maillog, pattern)

            # Add logline into Dataset
            data.extend(lines)

            # Add separator
            data.append_separator()

    # Sort by smtpid
    data.sort("smtpid")

    # Print data
    print(data)


# endregion

if __name__ == "__main__":
    main()

# endregion
