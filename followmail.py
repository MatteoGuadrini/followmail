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


# endregion

# region globals
__version__ = "0.0.1"

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
        action="store",
    )

    args = parser.parse_args()

    return args


def print_verbose(verbosity: bool, *messages: str):
    """Print verbose messages

    :param verbosity: boolean to activate verbose print
    """
    if verbosity:
        print("debug:", *messages)


# region scripts
def main():
    """Main function"""

    # Define global for a script
    args = get_args()
    verbose = args.verbose
    print_verbose(verbose, "start followmail")
    # Define filters
    to = args.to
    print_verbose(verbose, f"add {to} into filters")


# endregion

if __name__ == "__main__":
    main()

# endregion
