#!/usr/bin/env python3
"""Generates a fake downloads for testing purposes."""

import os
import time

FOLDER = "demo_downloads"

# name, size in bytes, age in days
FILES = [
    ("resume.pdf", 93000, 44),
    ("resume (1).pdf", 93000, 41),
    ("resume-final.pdf", 101500, 37),
    ("resume-final2.pdf", 104200, 36),
    ("resume-new.pdf", 104900, 30),

    ("bio essay.docx", 24000, 20),
    ("bio essay draft.docx", 21000, 22),
    ("bio essay FINAL.docx", 26500, 18),

    ("IMG_2201.jpg", 2400000, 12),
    ("IMG_2201 (1).jpg", 2400000, 12),

    # Ungrouped
    ("chemistry notes.txt", 8000, 60),
    ("bank statement march.pdf", 62000, 55),
    ("song.mp3", 5100000, 9),
    ("setup.exe", 8800000, 5),
    ("resume.mp3", 4000000, 40),
]



def main():
    os.makedirs(FOLDER, exist_ok = True)
    now = time.time()

    for name, size, days_ago in FILES:
        path = os.path.join(FOLDER, name)
        with open(path, "wb") as handle:
            handle.write(b"\0" * size)

        when = now - days_ago * 86400
        os.utime(path, (when, when))


    print(f"Made {len(FILES)} files in {FOLDER}/")
    print(f"Now try: python near_duplicates.py {FOLDER}")



if __name__ == "__main__":
    main()
