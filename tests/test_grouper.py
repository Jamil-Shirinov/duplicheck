import time
import unittest
from neardupes import grouper
from neardupes.scanner import FileInfo, newest_first

NOW = time.time()
THRESHOLD = 0.65


# Synthetic file generator
def make(name, size = 90000, days_ago = 0, origin = None):
    return FileInfo(name, size, NOW - days_ago * 86400, origin)



class ScoreTest(unittest.TestCase):

    def test_versions_of_one_file_score_high(self):
        pair = grouper.score(make("resume.pdf", days_ago = 10),
                             make("resume-final2.pdf", size = 95000, days_ago = 6))
        self.assertGreaterEqual(pair, THRESHOLD)

    def test_different_file_types_never_match(self):
        self.assertEqual(grouper.score(make("resume.pdf"), make("resume.mp3")), 0.0)

    def test_extension_aliases_do_match(self):
        self.assertGreater(grouper.score(make("photo.jpg"), make("photo (1).jpeg")), 0.0)

    def test_unrelated_names_score_zero_even_when_everything_else_lines_up(self):
        # Same size, same day, same type. Only the name says otherwise.
        self.assertEqual(grouper.score(make("resume.pdf"), make("six seven.pdf")), 0.0)

    def test_a_long_gap_costs_points(self):
        close = grouper.score(make("notes.txt", days_ago = 1), make("notes-new.txt"))
        far = grouper.score(make("notes.txt", days_ago = 200), make("notes-new.txt"))
        self.assertGreater(close, far)

    def test_matching_download_site_helps(self):
        plain = grouper.score(make("form.pdf"), make("form-v2.pdf", size = 70000))
        sourced = grouper.score(make("form.pdf", origin = "irs.gov"),
                                make("form-v2.pdf", size = 70000, origin = "irs.gov"))
        self.assertGreater(sourced, plain)


class ScoreHelpersTest(unittest.TestCase):

    def test_size_score(self):
        self.assertEqual(grouper.size_score(100, 100), 1.0)
        self.assertEqual(grouper.size_score(50, 100), 0.5)
        self.assertEqual(grouper.size_score(0, 0), 1.0)

    def test_time_score_runs_out_after_the_window(self):
        day = grouper.SECONDS_PER_DAY
        self.assertEqual(grouper.time_score(0, 0), 1.0)
        self.assertEqual(grouper.time_score(0, day *365), 0.0)


class LimitTest(unittest.TestCase):

    def test_keeps_the_newest_and_drops_the_rest(self):
        files = [make(f"file{n}.pdf", days_ago = n) for n in range(10)]
        kept = newest_first(files, 3)
        self.assertEqual([f.name for f in kept], ["file0.pdf", "file1.pdf", "file2.pdf"])

    def test_limit_of_zero_keeps_everything(self):
        files = [make(f"file{n}.pdf", days_ago = n) for n in range(10)]
        self.assertEqual(len(newest_first(files, 0)), 10)

    def test_limit_bigger_than_the_folder_is_fine(self):
        files = [make("a.pdf"), make("b.pdf")]
        self.assertEqual(len(newest_first(files, 500)), 2)



class GroupTest(unittest.TestCase):

    def test_a_whole_version_history_lands_in_one_group(self):
        files = [make("resume.pdf", days_ago = 44),
                 make("resume (1).pdf", days_ago = 41),
                 make("resume-final.pdf", size = 101000, days_ago = 37),
                 make("resume-final2.pdf", size = 104000, days_ago = 36)]
        groups = grouper.group_files(files, THRESHOLD)
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]), 4)

        # Since you're here, here's a dad joke: There are three kinds of people in the world:
        # Those who can count, and those who can't
    def test_lone_files_are_not_reported(self):
        files = [make("resume.pdf"), make("tax return.pdf"), make("song.mp3")]
        self.assertEqual(grouper.group_files(files, THRESHOLD), [])

    def test_newest_is_the_most_recent_file(self):
        old = make("essay.docx", days_ago = 9)
        new = make("essay-final.docx", days_ago = 2)
        self.assertIs(grouper.newest([old, new]), new)

    def test_tie_on_time_goes_to_bigger(self):
        small = make("essay.docx", size = 1000, days_ago = 3)
        big = make("essay (1).docx", size = 4000, days_ago = 3)
        self.assertIs(grouper.newest([small, big]), big)

    def test_identical_twins_fall_back_to_the_plain_name(self):
        original = make("IMG_2201.jpg", days_ago = 3)
        twin = make("IMG_2201 (1).jpg", days_ago = 3)
        self.assertIs(grouper.newest([twin, original]), original)

    def test_group_is_listed_oldest_first(self):
        files = [make("essay-final.docx", days_ago = 1), make("essay.docx", days_ago = 8)]
        names = [info.name for info in grouper.by_date(files)]
        self.assertEqual(names, ["essay.docx", "essay-final.docx"])


if __name__ == "__main__":
    unittest.main()
