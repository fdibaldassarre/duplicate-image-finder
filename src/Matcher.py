#!/usr/bin/env python3

import imagehash
import os
import shelve
from PIL import Image
from sklearn.neighbors import BallTree
import numpy as np


def get_image(path):
    if not os.path.isfile(path):
        return None
    try:
        return Image.open(path)
    except Exception as e:
        return None


def numpy_hash_to_str(arr):
    """
    This function is a copy of _binary_array_to_hex
    in imagehash
    :param arr:
    :return:
    """
    bit_string = ''.join(str(b) for b in 1 * arr.flatten())
    width = int(np.ceil(len(bit_string) / 4))
    return '{:0>{width}x}'.format(int(bit_string, 2), width=width)


def iter_folder(folder):
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        image = get_image(path)
        if image is not None:
            yield (path, image)


def iter_recursive(folder):
    for dirpath, dirnames, filenames in os.walk(folder):
        for name in filenames:
            path = os.path.join(dirpath, name)
            image = get_image(path)
            if image is not None:
                yield(path, image)


def index_folder(folder, db_path, recursive=True):
    with shelve.open(db_path, flag='c', writeback=True) as db:
        iterator = iter_recursive(folder) if recursive else iter_folder(folder)
        for path, image in iterator:
            hash = str(imagehash.whash(image))
            dup_path = db.get(hash)
            if dup_path is not None:
                print("Duplicate image found: %s vs %s" % (path, dup_path))
            else:
                db[hash] = path


def match_image(path, db_path):
    db_name, _ = os.path.splitext(db_path)
    with shelve.open(db_name, flag='r') as db:
        image = get_image(path)
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
    db_name, _ = os.path.splitext(db_path)
    with shelve.open(db_name, flag='r') as db:
        image = get_image(path)
        if image is None:
            print("Invalid image")
            return
        hash = imagehash.whash(image)
        for hex in db:
            dhash = imagehash.hex_to_hash(hex)
            if hash - dhash < threshold:
                path = db.get(hex)
                print("Duplicate %s" % path)


def get_all_hashes(folder, db_path, recursive=True):
    db_name, _ = os.path.splitext(db_path)
    with shelve.open(db_name, flag='n') as db:
        paths = []
        hashes_matrix = []
        perfect_matches = dict()
        iterator = iter_recursive(folder) if recursive else iter_folder(folder)
        for path, image in iterator:
            hash = imagehash.whash(image)
            hash_str = str(hash)
            dup_path = db.get(hash_str)
            if dup_path is not None:
                # Add to duplicates list
                if hash_str not in perfect_matches:
                    perfect_matches[hash_str] = []
                perfect_matches[hash_str].append(path)
            else:
                # Save on DB
                db[hash_str] = path
                # Add to hash_matrix
                paths.append(path)
                # Add internal hash (numpy array) with shape (0, n_features)
                hashes_matrix.append(hash.hash.reshape(1, -1))
    hashes_matrix = np.concatenate(hashes_matrix)  # final shape should be (n_samples, n_features)
    return paths, hashes_matrix, perfect_matches


def get_all_hashes_from_db(db_path):
    paths = []
    hashes_matrix = []
    db_name, _ = os.path.splitext(db_path)
    with shelve.open(db_name, flag='r') as db:
        for hash_str in db:
            hash = imagehash.hex_to_hash(hash_str)
            path = db.get(hash_str)
            paths.append(path)
            hashes_matrix.append(hash.hash.reshape(1, -1))
    hashes_matrix = np.concatenate(hashes_matrix)
    return paths, hashes_matrix, []


def build_tree(hashes_matrix):
    return BallTree(hashes_matrix, metric='hamming')


def find_similar_hashes(hash, tree, threshold):
    needle = hash.reshape(1, -1)
    result = tree.query_radius(needle, threshold)
    return result[0]


def find_similar(db_path, folder=None, recursive=True, threshold=0.3):
    if folder is None:
        paths, hashes_matrix, perfect_matches = get_all_hashes_from_db(db_path)
    else:
        paths, hashes_matrix, perfect_matches = get_all_hashes(folder, db_path, recursive=recursive)
    # Build the tree
    ball_tree = build_tree(hashes_matrix)
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
        similar = find_similar_hashes(hash, ball_tree, threshold=threshold)
        for el in similar:
            # Add the perfect hash matches
            dup_hash = hashes_matrix[el]
            dup_hash_str = numpy_hash_to_str(dup_hash)
            if dup_hash_str in perfect_matches:
                all_duplicates.extend(perfect_matches[dup_hash_str])
            if el == i:  # Remove the image itself from results
                continue
            dup_path = paths[el]
            all_duplicates.append(dup_path)
            marked_duplicates[dup_path] = True
        # Print the results
        if len(all_duplicates) > 0:
            print("Duplicates found for %s" % path)
            all_duplicates = sorted(all_duplicates)
            for dup in all_duplicates:
                print(dup)
            print("========================")

