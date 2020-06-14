#!/usr/bin/env python3

import os

from .. import Matcher
from .common import Common
from .common import to_relpath
from .common import AT_DATA_FOLDER


class MatcherAT(Common):

    def setUp(self):
        pass

    def assertDuplicatesInResult(self, result, *duplicates):
        main_key = None
        for duplicate in duplicates:
            if duplicate in result:
                main_key = duplicate
                break
        if main_key is None:
            self.fail("Files are not marked as duplicates")
        expected_duplicates = list(filter(lambda dup: dup != main_key, duplicates))
        self.assertArrayEquals(result[main_key], expected_duplicates)

    def testFindSameHashes(self):
        # Given a folder with files with the same hash
        folder = os.path.join(AT_DATA_FOLDER, "same-hashes")
        # When the user checks for exact duplicates (i.e. threshold = 0)
        result = Matcher.find_similar(folder, threshold=0, print_result=False, quiet=True)
        # Then the files with the same hash are marked as duplicates
        result = to_relpath(result, folder=folder)
        self.assertEqual(len(result.keys()), 1)
        self.assertDuplicatesInResult(result, "001.jpg", "003.jpg")

    def testFindRecursive(self):
        # Given a folder with subfolders
        folder = os.path.join(AT_DATA_FOLDER, "recursive")
        # When the user checks for duplicates recursively
        result = Matcher.find_similar(folder, recursive=True, threshold=0.1, print_result=False, quiet=True)
        # Then all the files in all the subfolders are checked
        result = to_relpath(result, folder=folder)
        # Check duplicate names
        self.assertTrue(len(result.keys()), 2)
        self.assertDuplicatesInResult(result, "cat_duplicate1.jpg", "cats/cat_duplicate2.jpg", "cats/cat_best.png")
        self.assertDuplicatesInResult(result, "house_best.png", "misc/house_duplicate.jpg")
