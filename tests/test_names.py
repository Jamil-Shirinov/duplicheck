import unittest
from neardupes import names



class NormalizeTest(unittest.TestCase):

    def test_version_markers_are_removed(self):
        for stem in ["resume", "resume (1)", "resume-final", "resume-final2", "resume-new", "Resume_FINAL", "resume v2",
                     "resume copy"]:
            self.assertEqual(names.normalize(stem), "resume", stem)

    def test_separators_become_spaces(self):
        self.assertEqual(names.normalize("bio_essay-part.one"), "bio essay part one")

    def test_date_stamps_are_removed(self):
        self.assertEqual(names.normalize("invoice 2024-01-04"), "invoice")

    def test_numbers_that_are_part_of_the_name_stay(self):
        self.assertNotEqual(names.normalize("chapter 1"), names.normalize("chapter 2"))

    def test_name_made_only_of_markers_does_not_empty_out(self):
        self.assertEqual(names.normalize("final2"), "final2")



class SimilarityTest(unittest.TestCase):

    def test_same_plain_name_scores_one(self):
        self.assertEqual(names.similarity("resume", "resume-final2"), 1.0)

    def test_unrelated_names_score_lower(self):
        self.assertLess(names.similarity("resume", "tax return"), 0.5)

    def test_added_words_still_score_high(self):
        self.assertGreaterEqual(names.similarity("essay", "essay rough outline"), 0.9)

    def test_short_names_do_not_get_the_prefix_bonus(self):
        self.assertLess(names.similarity("a", "a very long file name"), 0.9)


if __name__ == "__main__":
    unittest.main()
