#!/usr/bin/env python3

import shutil
import os

from .Common import read_info_file
from .Common import read_restore_info
from .Common import remove_info_file
from .Common import iter_folder
from .Common import open_shelve_db
from .Common import INFO_FILE_NAME


def _save_false_positives(false_positives_db, false_positives_map):
    with open_shelve_db(false_positives_db, writeback=True) as db:
        for path in false_positives_map:
            elements = db.get(path)
            if elements is None:
                elements = []
                db[path] = elements
            for false_positive in false_positives_map[path]:
                if false_positive not in elements:
                    elements.append(false_positive)


def _get_original_symlink(path):
    original_symlink = None
    for filename in os.listdir(path):
        if filename.startswith("0_"):
            original_symlink = os.path.join(path, filename)
            break
    return original_symlink


def _append_false_positives(false_positives_map, paths):
    """
    Append to the false_positives_map
    :param false_positives_map:
    :param paths:
    :return:
    """
    # Must have at least 2 elements
    if len(paths) <= 1:
        return
    for path in paths:
        false_positives_map[path] = []
        for false_path in paths:
            if false_path != path:
                false_positives_map[path].append(false_path)


def restore(duplicates_path):
    false_positives_map = {}
    empty_folders = []
    for path in iter_folder(duplicates_path):
        if not os.path.isdir(path):
            continue
        info_file = read_info_file(path)
        if info_file is None:
            continue
        basefile, duplicates = info_file
        false_positives = [basefile]
        for name, dest_path in duplicates:
            src_path = os.path.join(path, name)
            if not os.path.exists(src_path):
                continue
            shutil.move(src_path, dest_path)
            false_positives.append(dest_path)
        # Save the false positives
        _append_false_positives(false_positives_map, false_positives)
        # Remove original locations file
        remove_info_file(path)
        # Remove original symlink
        original_symlink = _get_original_symlink(path)
        if original_symlink is not None:
            os.remove(original_symlink)
        if len(os.listdir(path)) == 0:
            empty_folders.append(path)
    # Remove the empty folders
    for path in empty_folders:
        os.rmdir(path)
    # Store the false positives if possible
    restore_info = read_restore_info(duplicates_path)
    if restore_info is not None and len(false_positives_map) > 0:
        false_positives_db_path = restore_info
        _save_false_positives(false_positives_db_path, false_positives_map)
    # Cleanup
    rem_files = list(iter_folder(duplicates_path))
    if len(rem_files) == 1 and os.path.isfile(rem_files[0]):
        info_file = rem_files[0]
        if os.path.basename(info_file) == INFO_FILE_NAME:
            os.remove(info_file)
            os.rmdir(duplicates_path)


