#!/usr/bin/env python3

import os
import shutil
import tempfile

from .. import Matcher
from .. import Restore

from .common import Common
from .common import AT_DATA_FOLDER


class MarkFalsePositivesAT(Common):

    def setUp(self):
        """
        Set the folders for the test.
        Structure is
            data/
            data/.db/{hashes.db, false-positives.db}
            duplicates/
        """
        self._test_main_folder = tempfile.mkdtemp(suffix="dif_mark_false_positives")
        # Data folder
        self.test_folder = os.path.join(self._test_main_folder, "data")
        test_data = os.path.join(AT_DATA_FOLDER, "mark-duplicates")
        shutil.copytree(test_data, self.test_folder, dirs_exist_ok=True)
        db_folder = os.path.join(self.test_folder, ".db")
        os.mkdir(db_folder)
        self.db_path = os.path.join(db_folder, "hashes.db")
        self.false_positives_db_path = os.path.join(db_folder, "false-positives.db")
        # Duplicates folder
        self.duplicates_folder = os.path.join(self._test_main_folder, "duplicates")
        os.mkdir(self.duplicates_folder)

    def tearDown(self):
        shutil.rmtree(self._test_main_folder)

    def testFalsePositivesAreMarked(self):
        # Given a folder with duplicates removed
        # - Find matches
        Matcher.find_similar(self.test_folder, recursive=True, duplicates_folder=self.duplicates_folder,
                             db_path=self.db_path, false_positives_db_path=self.false_positives_db_path, quiet=True)
        # - Ensure duplicates are found
        duplicates_folders = os.listdir(self.duplicates_folder)
        self.assertArrayEquals(duplicates_folders, ["info.json", "1_cat.png"])
        duplicates_cat = os.listdir(os.path.join(self.duplicates_folder, "1_cat.png"))
        if "1_cat_duplicate.jpg" in duplicates_cat:
            self.assertArrayEquals(duplicates_cat, ["0_cat.png", "1_cat_duplicate.jpg", "2_cat_false_positive.jpg",
                                                    "info.json"])
            real_duplicate = os.path.join(self.duplicates_folder, "1_cat.png/1_cat_duplicate.jpg")
        else:
            self.assertArrayEquals(duplicates_cat, ["0_cat.png", "1_cat_false_positive.jpg", "2_cat_duplicate.jpg",
                                                    "info.json"])
            real_duplicate = os.path.join(self.duplicates_folder, "1_cat.png/2_cat_duplicate.jpg")
        # - Remove real duplicates
        os.remove(real_duplicate)
        # - Restore the false positives
        Restore.restore(self.duplicates_folder)
        # - Ensure false positive is restored
        false_positive_path = os.path.join(self.test_folder, "cat_false_positive.jpg")
        self.assertTrue(os.path.exists(false_positive_path))
        # When the duplicates are moved again
        Matcher.find_similar(self.test_folder, recursive=True, duplicates_folder=self.duplicates_folder,
                             db_path=self.db_path, false_positives_db_path=self.false_positives_db_path, quiet=True)
        # Then the false positives are not moved
        self.assertTrue(os.path.exists(false_positive_path))
        # And thus no duplicates are found
        duplicates_folders = os.listdir(self.duplicates_folder)
        self.assertArrayEquals(duplicates_folders, ["info.json"])
