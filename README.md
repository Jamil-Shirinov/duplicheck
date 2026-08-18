# duplicheck

Most duplicate finders hash every file, so they only ever report exact copies. That misses the actual mess commonly found in Downloads folders:

```
resume.pdf
resume (1).pdf
resume-final.pdf
resume-final2.pdf
resume-new.pdf
...
```

Those are five drafts of one resume. Every hash is different, so a normal duplicate finder says there's nothing there. duplicheck finds them, because it never opens the files at all.

## Running it

Only needs Python 3.

```
python make_demo.py                           # generates a sample Downloads folder to try the tool
python near_duplicates.py demo_downloads
```

```
Looked at 15 files in demo_downloads.

  Likely versions of the same file (1 of 3)

  resume.pdf        Jul 05    90.8 KB
  resume (1).pdf    Jul 08    90.8 KB
  resume-final.pdf  Jul 12    99.1 KB
  resume-final2.pdf Jul 13   101.8 KB
  resume-new.pdf    Jul 19   102.4 KB

  Suggested newest: resume-new.pdf
```

Then, if you would like to try it on a real folder:

```
python near_duplicates.py ~/<path/to/folder>
```

duplicheck only ever prints. It never renames or deletes anything.

Options:

```
-r, --recursive    include subfolders
-t, --threshold    how sure to be before grouping, 0 to 1 (default 0.65)
--min-size         skip files under this many bytes
```

## How it works

Every pair of files gets a score out of 1:

- name similarity, 60%
- file size, 20%
- timestamps, 20%
- same download site, 5% bonus

Two rules can throw a pair out before any of that:

- the extensions have to match, since a .pdf is never a version of an .mp3 (with a few exceptions like .jpg and .jpeg)
- the names have to score at least 0.5, otherwise two unrelated files that are the same size and were saved the same day get grouped

Comparing names straight off works badly, because the part that differs is exactly the part that does not matter. Therefore, duplicheck strips that first: `(1)`, `copy`, `v2`, `final`, `final2`, `new`, `draft`, date stamps and so on. All five resumes above come out as
a plain `resume` and score a 1.0. Next, the plain name is compared with difflib, which is already in the standard library.

For grouping, a file joins a group if it matches any one file already in it. `resume.pdf` and `resume-final2.pdf` are five weeks apart and don't match each other directly, but the drafts in between chain them together.

The suggested file is the newest one by date. Ties go to the bigger file, and only then to the shorter name, since a file and its `(1)` usually have the exact same content.

## Known problem

It's guessing from names, so might sometimes groups `chapter 1.txt` with `chapter 2.txt`, which are really different files. Raise `--threshold` if
that happens a lot. The output is a list to look through, but not a guarantee that all of the files in the same group are actual duplicates.

## Tests

```
python -m unittest discover -s tests -t .
```

## Files

```
near_duplicates.py   run this
make_demo.py         generates the test folder
neardupes/
  scanner.py         reads the folder, records name/size/date
  names.py           strips and compares names
  grouper.py         scores pairs and generates the groups
  report.py          prints the final report
  cli.py             command line
```

## Todo

- reading the download origin currently works only on Windows. 
- a `--deep` flag to compare contents, but only inside a group it already found,

## License

MIT. See [LICENSE](LICENSE).
