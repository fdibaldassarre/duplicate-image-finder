#!/usr/bin/env python3

import os
import json
import shelve

INFO_FILE_NAME = "info.json"


class open_shelve_db:
    """
    Open a shelve db. Will automatically remove the file extension.
    Allows empty db_path, in that case the returned db will be a
    dictionary.
    """

    def __init__(self, db_path, **kwargs):
        self.db_path = db_path
        self.kwargs = kwargs

    def __enter__(self):
        if self.db_path is None:
            self.db = dict()
            self.close_db = False
        else:
            db_name, _ = os.path.splitext(self.db_path)
            self.db = shelve.open(db_name, **self.kwargs)
            self.close_db = True
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.close_db:
            self.db.close()


def iter_folder(folder):
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        yield os.path.abspath(path)


def iter_recursive(folder):
    for dirpath, dirnames, filenames in os.walk(folder):
        for name in filenames:
            path = os.path.join(dirpath, name)
            yield os.path.abspath(path)


def write_info_file(folder, basepath, duplicates):
    """
    Write the info file in the duplicates folder.

    :param folder: Folder with the duplicates file
    :param basepath: Best duplicate file (symlinked in the duplicates folder)
    :param duplicates: List of 2-ples (name of the file in the duplicates folder, original path)
    :return:
    """
    duplicates_structured = list(map(lambda duplicate: {'name': duplicate[0], 'path': duplicate[1]}, duplicates))
    data = {
        'basefile': basepath,
        'duplicates': duplicates_structured
    }
    path = os.path.join(folder, INFO_FILE_NAME)
    with open(path, "w") as hand:
        json.dump(data, hand)


def read_info_file(folder):
    """
    Read the info file

    :param folder:
    :return: basefile, duplicates
    """
    path = os.path.join(folder, INFO_FILE_NAME)
    if not os.path.exists(path):
        return None
    with open(path, "r") as hand:
        data = json.load(hand)
    duplicates = []
    for element in data['duplicates']:
        duplicates.append((element['name'], element['path']))
    return data['basefile'], duplicates


def remove_info_file(folder):
    path = os.path.join(folder, INFO_FILE_NAME)
    if os.path.exists(path):
        os.remove(path)


def write_restore_info(folder, false_positives_db_path):
    """
    Save the informations needed by the restore command

    :param folder: Duplicates folder
    :param false_positives_db_path: Path to the false positives database
    :return:
    """
    false_positives_db_path = os.path.abspath(false_positives_db_path)
    data = {
        'false_positives_db': false_positives_db_path
    }
    path = os.path.join(folder, INFO_FILE_NAME)
    with open(path, "w") as hand:
        json.dump(data, hand)


def read_restore_info(folder):
    path = os.path.join(folder, INFO_FILE_NAME)
    if not os.path.exists(path):
        return None
    with open(path, "r") as hand:
        data = json.load(hand)
    return data['false_positives_db']

