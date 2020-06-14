#!/usr/bin/env python3

import os
import shutil
import tempfile

from .. import Matcher
from .. import Restore

from .common import Common
from .common import AT_DATA_FOLDER
from .common import find_name_with_prefix


class MoveDuplicatesAT(Common):

    def setUp(self):
        """
        Set the folders for the test.

        Structure:
            data/
            duplicates/
        """
        self._test_main_folder = tempfile.mkdtemp(suffix="dif_mark_false_positives")
        self.test_folder = os.path.join(self._test_main_folder, "data")
        test_data = os.path.join(AT_DATA_FOLDER, "recursive")
        shutil.copytree(test_data, self.test_folder, dirs_exist_ok=True)
        self.duplicates_folder = os.path.join(self._test_main_folder, "duplicates")

    def tearDown(self):
        shutil.rmtree(self._test_main_folder)

    def testDuplicatesAreMoved(self):
        # When the duplicates are moved
        Matcher.find_similar(self.test_folder, recursive=True, duplicates_folder=self.duplicates_folder, quiet=True)
        # Then the duplicates folder contains the duplicate files and info
        duplicates_folders = os.listdir(self.duplicates_folder)
        self.assertTrue(len(duplicates_folders), 2)
        self.assertDuplicates(self.duplicates_folder, "cat_best.png", "cat_duplicate1.jpg", "cat_duplicate2.jpg")
        self.assertDuplicates(self.duplicates_folder, "house_best.png", "house_duplicate.jpg")
        # And the unique files are still in the original folder
        cat_unique = os.path.join(self.test_folder, "cats/cat_best.png")
        house_unique = os.path.join(self.test_folder, "house_best.png")
        tree_unique = os.path.join(self.test_folder, "misc/tree.jpg")
        for path in [cat_unique, house_unique, tree_unique]:
            self.assertTrue(os.path.exists(path))

    def testRestore(self):
        # When the duplicates are moved
        Matcher.find_similar(self.test_folder, recursive=True, duplicates_folder=self.duplicates_folder, quiet=True)
        # Then the duplicates are no longer in the source folder
        cat_duplicate = os.path.join(self.test_folder, "cat_duplicate1.jpg")
        cat_duplicate2 = os.path.join(self.test_folder, "cats/cat_duplicate2.jpg")
        house_duplicate = os.path.join(self.test_folder, "misc/house_duplicate.jpg")
        for path in [cat_duplicate, cat_duplicate2, house_duplicate]:
            self.assertFalse(os.path.exists(path))
        # and the user removes an actual duplicate
        expected_cat_name = find_name_with_prefix("cat_best.png", self.duplicates_folder)
        if expected_cat_name is None:
            self.fail("Cat duplicates folder not found")
        cat_duplicates_folder = os.path.join(self.duplicates_folder, expected_cat_name)
        self._removeDuplicate("cat_duplicate1.jpg", cat_duplicates_folder)
        # and then restores the files
        Restore.restore(self.duplicates_folder)
        # Then the files are restored
        for path in [cat_duplicate2, house_duplicate]:
            self.assertTrue(os.path.exists(path))
        # And the duplicates folder is clear
        self.assertEqual(len(os.listdir(self.duplicates_folder)), 0)

    def _removeDuplicate(self, name, folder):
        # Find the actual name
        duplicate_name = find_name_with_prefix(name, folder)
        if duplicate_name is None:
            self.fail("File %s not found in %s" % (name, folder))
        path = os.path.join(folder, duplicate_name)
        os.remove(path)
