"""Walks a folder and writes down some basic info for each file"""

import os
from urllib.parse import urlparse

# Bunch of junk
SKIP_NAMES = {"desktop.ini", "thumbs.db", ".ds_store"}



class FileInfo:

    def __init__(self, path, size, mtime, origin = None):
        self.path = path
        self.name = os.path.basename(path)
        stem, ext = os.path.splitext(self.name)
        self.stem = stem
        self.ext = ext.lower().lstrip(".")
        self.size = size
        self.mtime = mtime
        self.origin = origin

    def __repr__(self):
        return f"FileInfo({self.name})"



def scan(folder, recursive = False, min_size = 1):
    """Return a FileInfo for every reg file in `folder`."""

    files = []
    for current, subfolders, names in os.walk(folder):
        # ##########
        # !Important! Skip hidden folders such as .git so we don't report their content.
        # ##########
        subfolders[:] = [d for d in subfolders if not d.startswith(".")]

        for name in names:
            if name.startswith(".") or name.lower() in SKIP_NAMES:
                continue
            path = os.path.join(current, name)
            info = describe(path)
            # A file can disappear between listing it and looking at it and empty files match everything so both will get dropped
            if info is not None and info.size >= min_size:
                files.append(info)

        if not recursive:
            break

    return files



def describe(path):
    """Return None if there is an OSError"""
    try:
        stats = os.stat(path)
    except OSError:
        return None
    
    return FileInfo(path, stats.st_size, stats.st_mtime, read_origin(path))



def read_origin(path):
    try:
        with open(path + ":Zone.Identifier", encoding = "utf-8", errors = "ignore") as stream:
            text = stream.read()
    except OSError:
        return None

    # The stream looks like an .ini file. HostUrl is the download link itself
    # ReferrerUrl is the page it was clicked from, so it's the weaker of the two and only used as a backup.
    host = None
    referrer = None
    for line in text.splitlines():
        key, _, value = line.partition("=")
        key = key.strip().lower()
        if key == "hosturl":
            host = value.strip()
        elif key == "referrerurl":
            referrer = value.strip()

    return host_of(host or referrer)



def host_of(url):
    if not url:
        return None
    name = urlparse(url).hostname
    if not name:
        return None
    return name.lower().removeprefix("www.")
