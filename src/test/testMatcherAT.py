#!/usr/bin/env python3

import os

from .. import Matcher
from .common import Common
from .common import to_relpath
from .common import AT_DATA_FOLDER


class MatcherAT(Common):

    def setUp(self):
        pass

    def testFindSameHashes(self):
        # Given a folder with files with the same hash
        folder = os.path.join(AT_DATA_FOLDER, "same-hashes")
        # When the user checks for exact duplicates (i.e. threshold = 0)
        result = Matcher.find_similar(folder, threshold=0, print_result=False, quiet=True)
        # Then the files with the same hash are marked as duplicates
        result = to_relpath(result, folder=folder)
        self.assertEqual(len(result.keys()), 1)
        self.assertTrue("001.jpg" in result or "003.jpg" in result)
        if "001.jpg" in result:
            actual = result["001.jpg"]
            expected = ["003.jpg"]
        else:
            actual = result["003.jpg"]
            expected = ["001.jpg"]
        self.assertArrayEquals(actual, expected)

    def testFindRecursive(self):
        # Given a folder with subfolders
        folder = os.path.join(AT_DATA_FOLDER, "recursive")
        # When the user checks for duplicates recursively
        result = Matcher.find_similar(folder, recursive=True, threshold=0.1, print_result=False, quiet=True)
        # Then all the files in all the subfolders are checked
        result = to_relpath(result, folder=folder)
        self.assertArrayEquals(result.keys(), ["001.jpg", "002.png"])
        # Check result content
        self.assertArrayEquals(result["001.jpg"], ["folder1/003.jpg", "folder1/005.png"])
        self.assertArrayEquals(result["002.png"], ["folder2/006.jpg"])

