#!/usr/bin/env python3

import os
import shutil
import tempfile

from .. import Matcher
from .. import Restore

from .common import Common
from .common import to_relpath
from .common import AT_DATA_FOLDER


class MoveDuplicatesAT(Common):

    def setUp(self):
        self.test_folder = tempfile.mkdtemp(suffix="data")
        test_data = os.path.join(AT_DATA_FOLDER, "recursive")
        shutil.copytree(test_data, self.test_folder, dirs_exist_ok=True)
        self.duplicates_folder = tempfile.mkdtemp(suffix="duplicates")

    def tearDown(self):
        shutil.rmtree(self.test_folder)
        shutil.rmtree(self.duplicates_folder)

    def testDuplicatesAreMoved(self):
        # When the duplicates are moved
        Matcher.find_similar(self.test_folder, recursive=True, duplicates_folder=self.duplicates_folder)
        # Then the duplicates folder contains the duplicate files and info
        duplicates_folders = os.listdir(self.duplicates_folder)
        self.assertArrayEquals(duplicates_folders, ["1_005.png", "2_002.png"])
        # Verify the cat duplicates
        duplicates_cat = os.listdir(os.path.join(self.duplicates_folder, "1_005.png"))
        self.assertArrayEquals(duplicates_cat, ["0_005.png", "1_001.jpg", "2_003.jpg", "original_locations.txt"])
        # Verify the house duplicates
        house_duplicates = os.listdir(os.path.join(self.duplicates_folder, "2_002.png"))
        self.assertArrayEquals(house_duplicates, ["0_002.png", "1_006.jpg", "original_locations.txt"])
        # And the unique files are still in the original folder
        cat_unique = os.path.join(self.test_folder, "folder1/005.png")
        house_unique = os.path.join(self.test_folder, "002.png")
        tree_unique = os.path.join(self.test_folder, "folder2/004.jpg")
        for path in [cat_unique, house_unique, tree_unique]:
            self.assertTrue(os.path.exists(path))

    def testRestore(self):
        # When the duplicates are moved
        Matcher.find_similar(self.test_folder, recursive=True, duplicates_folder=self.duplicates_folder)
        # Then the duplicates are not longer in the source folder
        cat_duplicate = os.path.join(self.test_folder, "001.jpg")
        cat_duplicate2 = os.path.join(self.test_folder, "folder1/003.jpg")
        house_duplicate = os.path.join(self.test_folder, "folder2/006.jpg")
        for path in [cat_duplicate, cat_duplicate2, house_duplicate]:
            self.assertFalse(os.path.exists(path))
        # and the user removes an actual duplicate
        actual_duplicate = os.path.join(self.duplicates_folder, "1_005.png/1_001.jpg")
        os.remove(actual_duplicate)
        # and then restores the files
        Restore.restore(self.duplicates_folder)
        # Then the files are restored
        for path in [cat_duplicate2, house_duplicate]:
            self.assertTrue(os.path.exists(path))
        # And the duplicates folder is clear
        self.assertEqual(len(os.listdir(self.duplicates_folder)), 0)
