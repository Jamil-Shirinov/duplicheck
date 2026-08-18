"""Reads the cmd line and runs the 3 steps: scan, group, print."""

import argparse
import os
import sys
from . import grouper, report, scanner

DEFAULT_THRESHOLD = 0.65



def build_parser():
    parser = argparse.ArgumentParser(prog = "near-duplicates", description = "Find files that look like" \
    "versions of each other. " "Nothing is hashed and no file is opened, so this " "catches repeats that a normal duplicate finder misses.")

    parser.add_argument(
        "folder", nargs = "?", default = ".", help = "folder to look through (default: the current one)")

    parser.add_argument("-r", "--recursive", action="store_true", help = "look inside subfolders too")

    parser.add_argument("-t", "--threshold", type = float, default=  DEFAULT_THRESHOLD,
                        help = "how sure to be before grouping two files, 0 to 1 "
                        "(default: %(default)s -- lower finds more and guesses more)")

    parser.add_argument("--min-size", type = int, default = 1, metavar = "BYTES",
                        help = "ignore files smaller than this (default: %(default)s)")
    
    return parser



def main(argv = None):
    args = build_parser().parse_args(argv)

    folder = os.path.expanduser(args.folder)

    if not os.path.isdir(folder):
        print("No such folder found.", file = sys.stderr)
        return 1
    
    if not 0 < args.threshold <= 1:
        print("The threshold has to be between 0 and 1.", file = sys.stderr)
        return 1

    files = scanner.scan(folder, args.recursive, args.min_size)
    groups = grouper.group_files(files, args.threshold)
    report.print_report(groups, len(files), folder)
    return 0
