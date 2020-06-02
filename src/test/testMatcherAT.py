#!/usr/bin/env python3

import os
import unittest

from .. import Matcher

path = os.path.abspath(__file__)
AT_FOLDER = os.path.dirname(path)
SRC_FOLDER = os.path.dirname(AT_FOLDER)
MAIN_FOLDER = os.path.dirname(SRC_FOLDER)
AT_DATA_FOLDER = os.path.join(MAIN_FOLDER, "at")


def _to_relpath(result, folder):
    """
        Replaces paths with relative paths from the given folder for easier asserts.
    :param result:
    :return:
    """
    rel_result = dict()
    for path in result:
        rel = os.path.relpath(path, start=folder)
        rel_result[rel] = list()
        for duplicate_path in result[path]:
            rel_duplicate = os.path.relpath(duplicate_path, start=folder)
            rel_result[rel].append(rel_duplicate)
    return rel_result


class MatcherAT(unittest.TestCase):

    def setUp(self):
        pass

    def _assertArrayEquals(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for el in expected:
            self.assertTrue(el in actual)

    def testFindSameHashes(self):
        folder = os.path.join(AT_DATA_FOLDER, "same-hashes")
        result = Matcher.find_similar(folder, threshold=0, print_result=False)
        result = _to_relpath(result, folder=folder)
        self.assertEqual(len(result.keys()), 1)
        self.assertTrue("001.jpg" in result or "003.jpg" in result)
        if "001.jpg" in result:
            actual = result["001.jpg"]
            expected = ["003.jpg"]
        else:
            actual = result["003.jpg"]
            expected = ["001.jpg"]
        self._assertArrayEquals(actual, expected)

    def testFindRecursive(self):
        folder = os.path.join(AT_DATA_FOLDER, "recursive")
        result = Matcher.find_similar(folder, recursive=True, threshold=0.1, print_result=False)
        result = _to_relpath(result, folder=folder)
        self._assertArrayEquals(result.keys(), ["001.jpg", "002.png"])
        # Check result content
        self._assertArrayEquals(result["001.jpg"], ["folder1/003.jpg", "folder1/005.png"])
        self._assertArrayEquals(result["002.png"], ["folder2/006.jpg"])

