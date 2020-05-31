#!/usr/bin/env python3

import imagehash
import os
import shelve
from PIL import Image
from sklearn.neighbors import BallTree
import numpy as np


class _open_shelve_db:
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


def _get_image(path):
    if not os.path.isfile(path):
        return None
    try:
        return Image.open(path)
    except Exception as e:
        return None


def _numpy_hash_to_str(arr):
    """
    This function is a copy of _binary_array_to_hex
    in imagehash.

    :param arr:
    :return:
    """
    bit_string = ''.join(str(b) for b in 1 * arr.flatten())
    width = int(np.ceil(len(bit_string) / 4))
    return '{:0>{width}x}'.format(int(bit_string, 2), width=width)


def _iter_folder(folder):
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        image = _get_image(path)
        if image is not None:
            yield (path, image)


def _iter_recursive(folder):
    for dirpath, dirnames, filenames in os.walk(folder):
        for name in filenames:
            path = os.path.join(dirpath, name)
            image = _get_image(path)
            if image is not None:
                yield(path, image)


def index_folder(folder, db_path, recursive=True):
    with _open_shelve_db(db_path, flag='c', writeback=True) as db:
        iterator = _iter_recursive(folder) if recursive else _iter_folder(folder)
        for path, image in iterator:
            hash = str(imagehash.whash(image))
            dup_path = db.get(hash)
            if dup_path is not None:
                print("Duplicate image found: %s vs %s" % (path, dup_path))
            else:
                db[hash] = path


def match_image(path, db_path):
    with _open_shelve_db(db_path, flag='r') as db:
        image = _get_image(path)
        if image is None:
            print("Invalid image")
            return
        hash = str(imagehash.whash(image))
        dup_path = db.get(hash)
        if dup_path is not None:
            print("Duplicate image found: %s vs %s" % (path, dup_path))
        else:
            print("No duplicate found")


def match_similar(path, db_path, threshold=5):
    with _open_shelve_db(db_path, flag='r') as db:
        image = _get_image(path)
        if image is None:
            print("Invalid image")
            return
        hash = imagehash.whash(image)
        for hex in db:
            dhash = imagehash.hex_to_hash(hex)
            if hash - dhash < threshold:
                path = db.get(hex)
                print("Duplicate %s" % path)


def _get_all_hashes(folder, db_path, db_flag='c', recursive=True):
    with _open_shelve_db(db_path, flag=db_flag) as db:
        paths = []
        hashes_matrix = []
        paths_dict = dict()  # Map from path to hash
        # Add hashes from the database itself
        for hash_str in db:
            hash = imagehash.hex_to_hash(hash_str)
            path = db.get(hash_str)
            paths.append(path)
            paths_dict[path] = hash
            hashes_matrix.append(hash.hash.reshape(1, -1))
        # Add hashes from the folder
        hash_to_file = dict()  # Map from hash to list of files with that hash
        iterator = _iter_recursive(folder) if recursive else _iter_folder(folder)
        for path, image in iterator:
            if path in paths_dict:
                # I already have this hash
                hash = paths_dict[path]
                hash_str = str(hash)
                dup_path = path
            else:
                # Re-compute the hash
                hash = imagehash.whash(image)
                hash_str = str(hash)
                dup_path = db.get(hash_str)
            if dup_path is not None:
                # Add to duplicates list
                if hash_str not in hash_to_file:
                    hash_to_file[hash_str] = []
                hash_to_file[hash_str].append(path)
            else:
                # Save on DB
                db[hash_str] = path
                # Add to hash_matrix
                paths.append(path)
                # Add internal hash (numpy array) with shape (0, n_features)
                hashes_matrix.append(hash.hash.reshape(1, -1))
    hashes_matrix = np.concatenate(hashes_matrix)  # final shape should be (n_samples, n_features)
    return paths, hashes_matrix, hash_to_file


def _build_tree(hashes_matrix):
    return BallTree(hashes_matrix, metric='hamming')


def _find_similar_hashes(hash, tree, threshold):
    needle = hash.reshape(1, -1)
    result = tree.query_radius(needle, threshold)
    return result[0]


def find_similar(folder, recursive=True, threshold=0.3, db_path=None):
    # Read data from folder and db
    paths, hashes_matrix, hash_to_file = _get_all_hashes(folder, db_path, recursive=recursive)
    # Build the tree
    ball_tree = _build_tree(hashes_matrix)
    marked_duplicates = dict()  # A list of paths already marked as duplicates
    # Find all the matches
    for i in range(len(paths)):
        path = paths[i]
        if path in marked_duplicates:
            # Path already marked as duplicate,
            # do not look for duplicates of duplicates
            continue
        hash = hashes_matrix[i]
        all_duplicates = []
        # Find similar hashes
        similar = _find_similar_hashes(hash, ball_tree, threshold=threshold)
        for el in similar:
            # Add the paths for every match
            # Every hash has a list of mat
            dup_path = paths[el]
            dup_hash = hashes_matrix[el]
            dup_hash_str = _numpy_hash_to_str(dup_hash)
            for match in hash_to_file[dup_hash_str]:
                if match != path:
                    all_duplicates.append(match)
            marked_duplicates[dup_path] = True
        # Print the results
        if len(all_duplicates) > 0:
            print("Duplicates found for %s" % path)
            all_duplicates = sorted(all_duplicates)
            for dup in all_duplicates:
                print(dup)
            print("========================")

