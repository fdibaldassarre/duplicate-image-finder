#!/usr/bin/env python3

import os
import unittest

path = os.path.abspath(__file__)
AT_FOLDER = os.path.dirname(path)
SRC_FOLDER = os.path.dirname(AT_FOLDER)
MAIN_FOLDER = os.path.dirname(SRC_FOLDER)
AT_DATA_FOLDER = os.path.join(MAIN_FOLDER, "at")


def to_relpath(result, folder):
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


class Common(unittest.TestCase):

    def assertArrayEquals(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for el in expected:
            self.assertTrue(el in actual)
