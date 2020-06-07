#!/usr/bin/env python3

import shutil
import os

from .Common import iter_folder


def _iter_non_duplicates(items_file):
    current_folder = os.path.dirname(items_file)
    with open(items_file, "r") as hand:
        for line in hand:
            fname, original_path = line.strip().split(": ")
            filepath = os.path.join(current_folder, fname)
            if not os.path.exists(filepath):
                continue
            yield filepath, original_path


def _get_original_symlink(path):
    original_symlink = None
    for filename in os.listdir(path):
        if filename.startswith("0_"):
            original_symlink = os.path.join(path, filename)
            break
    return original_symlink


def restore(duplicates_path):
    empty_folders = []
    for path in iter_folder(duplicates_path):
        if not os.path.isdir(path):
            continue
        original_locations_path = os.path.join(path, "original_locations.txt")
        if not os.path.exists(original_locations_path):
            continue
        for src_path, dest_path in _iter_non_duplicates(original_locations_path):
            shutil.move(src_path, dest_path)
        # Remove original locations file
        os.remove(original_locations_path)
        # Remove original symlink
        original_symlink = _get_original_symlink(path)
        if original_symlink is not None:
            os.remove(original_symlink)
        if len(os.listdir(path)) == 0:
            empty_folders.append(path)
    for path in empty_folders:
        os.rmdir(path)
