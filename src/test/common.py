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


def find_name_with_prefix(main_name, folder):
    """
    Read the folder and look for a file with name
    %d_%s % (n, main_name) for some n.

    :param main_name: Name to look for
    :param folder: Folder to look into
    :return:
    """
    filenames = os.listdir(folder)
    actual_name = None
    for i in range(len(filenames) + 1):
        possible_name = "%d_%s" % (i, main_name)
        if possible_name in filenames:
            actual_name = possible_name
            break
    return actual_name


class Common(unittest.TestCase):

    def assertArrayEquals(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for el in expected:
            self.assertTrue(el in actual)

    def assertDuplicates(self, duplicates_folder, main_file, *duplicates):
        # Find the expected folder name
        expected_folder_name = find_name_with_prefix(main_file, duplicates_folder)
        if expected_folder_name is None:
            self.fail("File %s not marked as best file" % main_file)
        folder_path = os.path.join(duplicates_folder, expected_folder_name)
        # Check all the duplicates and the info file are in the folder
        actual_duplicates = os.listdir(folder_path)
        self.assertEqual(len(actual_duplicates), len(duplicates) + 2)
        # - Check the info file
        self.assertTrue("info.json" in actual_duplicates)
        # - Check the link
        self.assertTrue("0_%s" % main_file in actual_duplicates)
        # - Check all the duplicates
        for name in duplicates:
            expected_name = find_name_with_prefix(name, folder_path)
            if expected_name is None:
                self.fail("File %s not found" % name)
