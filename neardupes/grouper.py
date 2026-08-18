from . import names



# How much each clue is worth. These add up to 1.0.
NAME_WEIGHT = 0.6
SIZE_WEIGHT = 0.2
TIME_WEIGHT = 0.2

ORIGIN_BONUS = 0.05

NAME_FLOOR = 0.5

# Past this gap, timing tells us nothing either way.
TIME_WINDOW_DAYS = 90
SECONDS_PER_DAY = 86400

# Different spellings of same types of files.
EXTENSION_ALIASES = [
    {"jpg", "jpeg"},
    {"doc", "docx"},
    {"htm", "html"},
    {"tif", "tiff"},
    {"yml", "yaml"},
    {"mp3", "mpeg"},
    {"mid", "midi"},
    {"wav", "wave"},
    {"txt", "text"},
]



def kind_key(ext):
    """Which pile an extension belongs in. jpg and jpeg share one."""
    for family in EXTENSION_ALIASES:
        if ext in family:
            return min(family)
    return ext



def same_kind(ext_a, ext_b):
    if ext_a == ext_b:
        return True
    return any({ext_a, ext_b} <= pair for pair in EXTENSION_ALIASES)



def size_score(size_a, size_b):
    """1.0 for identical sizes but going to 0.0 as they diverge."""
    bigger = max(size_a, size_b)
    if bigger == 0:
        return 1.0
    return min(size_a, size_b) / bigger



def time_score(mtime_a, mtime_b):
    """1.0 for files saved at the same moment, 0.0 once they're far apart."""
    days_apart = abs(mtime_a - mtime_b) / SECONDS_PER_DAY
    if days_apart >= TIME_WINDOW_DAYS:
        return 0.0
    return 1.0 - days_apart / TIME_WINDOW_DAYS



def score(file_a, file_b):
    """Score from 0 to 1 for how likely two files are versions of each other."""
    if not same_kind(file_a.ext, file_b.ext):
        return 0.0

    name = names.similarity(file_a.stem, file_b.stem, NAME_FLOOR)
    if name < NAME_FLOOR:
        return 0.0

    total = (NAME_WEIGHT * name +
             SIZE_WEIGHT * size_score(file_a.size, file_b.size) +
             TIME_WEIGHT * time_score(file_a.mtime, file_b.mtime))

    if file_a.origin and file_a.origin == file_b.origin:
        total += ORIGIN_BONUS

    return min(total, 1.0)



def group_files(files, threshold):
    """Sort files into groups that each look like one file's history."""

    # Sorting first means the same folder always prints the exact same way
    files = sorted(files, key = lambda f: f.name.lower())

    # Files of different types can never match, so sort them into piles
    # by type and work one pile at a time. Otherwise every file gets
    # compared against every other one, which on a real Downloads folder
    # is millions of comparisons that were never going to match anyway.
    piles = {}
    for info in files:
        piles.setdefault(kind_key(info.ext), []).append(info)

    groups = []
    for pile in piles.values():
        pile_groups = []
        for curr in pile:
            for group in pile_groups:
                if any(score(curr, member) >= threshold for member in group):
                    group.append(curr)
                    break
            else:
                pile_groups.append([curr])
        groups.extend(pile_groups)

    # A group of one is just a single file
    groups = [g for g in groups if len(g) > 1]
    # Biggest groups first, then by name so the order never wobbles.
    groups.sort(key = lambda g: (-len(g), g[0].name.lower()))
    return groups



def newest(group):
    """The file in a group that looks most like the user wants to keep."""
    return max(group, key = lambda f: (f.mtime, f.size, -len(f.name)))



def by_date(group):
    return sorted(group, key = lambda f: f.mtime)
