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
import traceback
import argparse
import gzip
import os
import re

from collections import namedtuple

from tablib import Dataset

# endregion

# region globals
__version__ = "1.1.0"
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
        "--pattern-log",
        "-p",
        help="regular expression log line pattern",
        action="store",
        type=str,
        default=r"(^[A-Za-z]{3}\s\s?\d{1,2})\s(\d{2}:\d{2}:\d{2})\s(\w+)\s(.*/.*\[\d+]):\s(\w{10,15}):\s(.*)",
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
    parser.add_argument(
        "-m",
        "--max-lines",
        type=int,
        help="max lines to print",
    )
    group_sort = parser.add_mutually_exclusive_group()
    group_sort.add_argument(
        "-D",
        "--sortby-date",
        help="sort lines by date",
        action="store_true",
    )
    group_sort.add_argument(
        "-Q",
        "--sortby-queue",
        help="sort lines by queue",
        action="store_true",
    )
    group_sort.add_argument(
        "-S",
        "--sortby-server",
        help="sort lines by server",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--csv",
        help="print in csv format",
        action="store_true",
    )
    parser.add_argument(
        "-j",
        "--json",
        help="print in json format",
        action="store_true",
    )
    parser.add_argument(
        "-x",
        "--explain-error",
        help="Explain error with traceback",
        action="store_true",
    )

    args = parser.parse_args()
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    # Check if max lines is less than one
    if args.max_lines is not None and args.max_lines <= 0:
        parser.error("max lines is must greater than zero")

    # Check maillog file exists
    if not os.path.isfile(args.maillog):
        parser.error(f'maillog file "{args.maillog}" does not exists')

    # Check flags
    if not args.to and not args.from_:
        parser.error('unspecified filter "--to" or "--from"')

    # Validate email address
    if args.to and not re.findall(email_pattern, args.to):
        parser.error("specified a valid email address in 'to' field")

    if args.from_ and not re.findall(email_pattern, args.from_):
        parser.error("specified a valid email address in 'from' field")

    return args


def print_verbose(verbosity: bool, *messages: str):
    """Print verbose messages

    :param verbosity: boolean to activate verbose print
    """
    if verbosity:
        print("debug:", *messages)


def report_issue(exc, tb=False):
    """Report issue

    :param: exc: Exception object
    :param: tb: print traceback
    """
    print(
        "followmail: error: {0} on line {1}, with error {2}".format(
            type(exc).__name__, exc.__traceback__.tb_lineno, str(exc)
        )
    )
    if tb:
        traceback.print_exc()
    exit(1)


def open_log(log: str):
    """Open maillog file

    :param log: maillog file path
    :return: opened log
    """
    # Define function to open log
    open_method = gzip.open if log.endswith("gz") else open

    return open_method(log, "rt")


def make_logline(line: str, pattern: re.Pattern):
    """Make LogLine object from string

    :param line: maillog line
    :param pattern: regexp pattern object
    :return: LogLine
    """
    # Split line into single variable
    line = re.findall(pattern, line)

    # Skip line if not in pattern
    if line:
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

        return logline


def search_by_smtpid(smtpid: str, log: str, pattern: re.Pattern):
    """Search log lines by smtp id

    :param smtpid: string of smtp is
    :param log: opened log file
    :param pattern: regexp pattern
    :return: List[tuple]
    """
    rows = list()

    # Process log file
    with open_log(log) as maillog_file:
        for line in maillog_file:
            logline = make_logline(line, pattern)

            if logline:
                # Match smtp id
                if smtpid == logline.smtpid:
                    rows.append(logline)

                    # End of flow
                    if "removed" in logline.message:
                        break

    return rows


def print_data(data: Dataset, csv: bool = False, json: bool = False):
    """Print Dataset to stdout

    :param data: Dataset object
    :param csv: print to csv format, defaults to False
    :param json: print to json format, defaults to False
    """
    # Check if data is not empty...
    if not data:
        print("no data found")
        return

    # ...everything else, print!
    if csv:
        print(data.export("csv"))
    elif json:
        print(data.export("json"))
    else:
        print(data)


# region scripts
def main():
    """Main function"""

    # Define global for a script
    verbose = args.verbose
    # Empty Dataset
    data = Dataset(headers=("date", "time", "server", "queue", "smtpid", "message"))
    print_verbose(verbose, "start followmail")
    # Define filters
    to = args.to
    if to:
        print_verbose(verbose, f"add {to} into 'to' filters")
    from_ = args.from_
    if from_:
        print_verbose(verbose, f"add {from_} into 'from' filters")
    maillog = args.maillog
    print_verbose(verbose, f"add {maillog} into filters")
    queue = args.queue
    print_verbose(verbose, f"add {queue} into filters")

    # Define pattern regexp
    pattern = re.compile(args.pattern_log)

    # Process log file
    with open_log(maillog) as maillog_file:
        for line in maillog_file:
            logline = make_logline(line, pattern)

            if logline:
                # Filter queue
                if queue not in logline.queue:
                    continue

                # Filter to and from
                if (
                    f"to=<{to}>" not in logline.message
                    and f"from=<{from_}>" not in logline.message
                ):
                    continue

                print_verbose(verbose, f"found a log line {logline}")

                # Find lines through smtp id
                lines = search_by_smtpid(logline.smtpid, maillog, pattern)

                # Add logline into Dataset
                data.extend(lines)

    # Sort by field
    if args.sortby_date:
        data.sort("date")
    elif args.sortby_queue:
        data.sort("queue")
    elif args.sortby_server:
        data.sort("server")
    else:
        data.sort("smtpid")

    if args.max_lines:
        limited_data = data[: args.max_lines]
        # Create a new empty Dataset
        data = Dataset(headers=("date", "time", "server", "queue", "smtpid", "message"))
        # Extend dataset with limited data
        data.extend(limited_data)

    # Print data
    print_data(data, csv=args.csv, json=args.json)


# endregion

if __name__ == "__main__":
    args = get_args()
    try:
        main()
    except Exception as err:
        report_issue(err, args.explain_error)

# endregion
