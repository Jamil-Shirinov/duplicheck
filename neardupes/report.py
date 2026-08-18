import os
import time
from . import grouper



def human_size(size):
    """ Convert byte count to common units."""
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    index = 0

    while value >= 1024 and index < len(units) - 1:
        value /= 1024
        index += 1

    if index == 0:
        return f"{size} B"
    return f"{value:.1f} {units[index]}"



def short_date(mtime):
    """Format timestamp but leaving the year."""

    when = time.localtime(mtime)

    if when.tm_year == time.localtime().tm_year:
        return time.strftime("%b %d", when)
    return time.strftime("%b %d %Y", when)



def print_group(group, root, number, total):
    """Print group of files"""

    ordered = grouper.by_date(group)
    labels = [os.path.relpath(info.path, root) for info in ordered]
    width = max(len(label) for label in labels)

    print(f"  Likely versions of the same file ({number} of {total})")
    print()

    for label, info in zip(labels, ordered):
        print(
            f"  {label:<{width}} {short_date(info.mtime):<7}{human_size(info.size):>10}"
            )
    print()


    sites = {info.origin for info in group if info.origin}
    if len(sites) == 1:
        print(f"  All downloaded from: {sites.pop()}")

    best = grouper.newest(group)
    print(f"  Suggested newest: {os.path.relpath(best.path, root)}")
    print()



def print_report(groups, file_count, total_found, root):

    where = os.path.basename(os.path.abspath(root)) or root
    if file_count < total_found:
        print(f"Looked at the {file_count} newest of {total_found} files in {where}.")
        print("Use --limit 0 to check all of them.")
    else:
        print(f"Looked at {file_count} files in {where}.")
    print()

    if not groups:
        print("There appears to be no duplicates.")
        return

    for number, group in enumerate(groups, start=1):
        print_group(group, root, number, len(groups))

    covered = sum(len(group) for group in groups)
    plural = "" if len(groups) == 1 else "s"
    print(f"{len(groups)} group{plural}, {covered} files that might be repeats.")
