"""Compares file names after stripping out the "new version" clutter."""

import difflib
import functools
import re


# Most common markers
VERSION_MARKERS = [
    r"\(\s*\d+\s*\)",
    r"\bcopy\b",
    r"\bv\d+\b",
    r"\bfinal\d*\b",
    r"\bdraft\d*\b",
    r"\bnew(est)?\b",
    r"\bold(er|est)?\b",
    r"\brevised\b",
    r"\bupdated?\b",
    r"\bedit(ed)?\b",
    r"\bfixed\b",
    r"\bbackup\b",
    r"\d{4} ?\d{2} ?\d{2}",
]

MIN_PREFIX_LENGTH = 4



# Same names get compared over and over, so remember the answers.
@functools.lru_cache(maxsize = None)
def normalize(stem):
    """Simplify the file name to plain form"""

    text = stem.lower()

    # Dashes, underscores, dots
    text = re.sub(r"[_\-.]+", " ", text)

    # Markers
    for marker in VERSION_MARKERS:
        text = re.sub(marker, " ", text)

    # Remaining punctuation
    text = re.sub(r"[^a-z0-9 ]+", " ", text)

    plain = " ".join(text.split())

    if not plain:
        plain = " ".join(re.sub(r"[^a-z0-9]+", " ", stem.lower()).split())

    return plain



def similarity(stem_a, stem_b, floor = 0.0):
    """Score two file names from 0 (nothing alike) to 1 (the same).

    `floor` is the caller's give-up point. Anything scoring under it is
    getting thrown away anyway, so we're allowed to bail out early.
    """
    a = normalize(stem_a)
    b = normalize(stem_b)

    if a == b:
        return 1.0
    if not a or not b:
        return 0.0

    # People also make versions by adding words on the end so a shared beginning is better considered as well
    shorter, longer = sorted([a, b], key=len)
    is_prefix = len(shorter) >= MIN_PREFIX_LENGTH and longer.startswith(shorter)

    # difflib matches at most every letter of the shorter name, so its
    # score can never beat this. If even the perfect case is below the
    # floor, don't bother running it - that check is the slow part.
    best_possible = 2 * len(shorter) / (len(shorter) + len(longer))
    if not is_prefix and best_possible < floor:
        return 0.0

    score = difflib.SequenceMatcher(None, a, b).ratio()
    if is_prefix:
        score = max(score, 0.9)

    return score
