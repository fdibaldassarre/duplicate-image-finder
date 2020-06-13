#!/usr/bin/env python3

import imagehash
import os
import shutil
from PIL import Image
from sklearn.neighbors import BallTree
import numpy as np

from .Common import write_info_file
from .Common import write_restore_info
from .Common import iter_folder
from .Common import iter_recursive
from .Common import open_shelve_db


class _open_image:
    """
    Open a PIL Image, if possible. Return None if the given path
    is not a valid image.

    """
    def __init__(self, path):
        self.path = path
        self.resource = None

    def __enter__(self):
        if not os.path.isfile(self.path):
            self.resource = None
        else:
            try:
                self.resource = Image.open(self.path)
            except Exception as e:
                self.resource = None
        return self.resource

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.resource is not None:
            self.resource.close()


def _load_false_positives(db_path):
    """
    Load false positives in memory
    :param db_path: false positives db path
    :return: a map from path to list of false positives
    """
    false_positives_map = {}
    if db_path is None or not os.path.exists(db_path):
        return false_positives_map
    with open_shelve_db(db_path, flag='r') as db:
        for path in db:
            false_positives_map[path] = [false_path for false_path in db.get(path)]
    return false_positives_map


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


def index_folder(folder, db_path, recursive=True):
    """
    Save all the image hashes on a database.

    :param folder:
    :param db_path:
    :param recursive:
    :return:
    """
    with open_shelve_db(db_path, flag='c', writeback=True) as db:
        iterator = iter_recursive(folder) if recursive else iter_folder(folder)
        for path in iterator:
            with _open_image(path) as image:
                if image is None:
                    continue
                db[path] = str(imagehash.whash(image))


def _get_all_hashes(folder, db_path=None, db_flag='c', recursive=True):
    with open_shelve_db(db_path, flag=db_flag, writeback=True) as db:
        paths = []
        hashes_matrix = []
        hash_to_file = dict()  # Map from hash to list of files with that hash
        # Add hashes from the folder
        iterator = iter_recursive(folder) if recursive else iter_folder(folder)
        for path in iterator:
            hash_str = db.get(path)
            if hash_str is None:
                # Re-compute the image hash
                with _open_image(path) as image:
                    if image is None:
                        # Not an image file
                        continue
                    hash = imagehash.whash(image)
                hash_str = str(hash)
                if db_path is not None:
                    # Save on DB
                    db[path] = hash_str
            else:
                hash = imagehash.hex_to_hash(hash_str)
            # Check If I already have this hash
            if hash_str not in hash_to_file:
                # New hash!
                hash_to_file[hash_str] = [path]
                # Add to hash_matrix
                paths.append(path)
                # Add internal hash (numpy array) with shape (0, n_features)
                hashes_matrix.append(hash.hash.reshape(1, -1))
            else:
                # Old hash
                hash_to_file[hash_str].append(path)
    hashes_matrix = np.concatenate(hashes_matrix)  # final shape should be (n_samples, n_features)
    return paths, hashes_matrix, hash_to_file


def _build_tree(hashes_matrix):
    return BallTree(hashes_matrix, metric='hamming')


def _find_similar_hashes(hash, tree, threshold):
    needle = hash.reshape(1, -1)
    result = tree.query_radius(needle, threshold)
    return result[0]


def find_similar(folder, recursive=True, threshold=0.1, db_path=None,
                 false_positives_db_path=None, print_result=False, duplicates_folder=None):
    """
    Find duplicate images in a folder

    :param folder: Folder to look for images
    :param recursive: true if should look under subfolders recursively
    :param threshold: threshold under which images are considered duplicates
    :param db_path: db to load hashes from (instead of recalculating)
    :param false_positives_db_path: db to load the false positives from
    :param print_result: True if I should print the result to screen
    :param duplicates_folder: folder where the duplicate files will be moved to
    :return:
    """
    result = dict()
    # Save restore info
    if duplicates_folder is not None:
        write_restore_info(duplicates_folder, false_positives_db_path)
    # Read the false positives
    FALSE_POSITIVES = _load_false_positives(false_positives_db_path)
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
        # Get the false positives from this path
        path_false_positives = []
        if path in FALSE_POSITIVES:
            path_false_positives = FALSE_POSITIVES[path]
        hash = hashes_matrix[i]
        all_duplicates = []
        # Find similar hashes
        similar = _find_similar_hashes(hash, ball_tree, threshold=threshold)
        for index in similar:
            # Add the paths for every matched hash
            dup_hash = hashes_matrix[index]
            dup_hash_str = _numpy_hash_to_str(dup_hash)
            for match in hash_to_file[dup_hash_str]:
                if match != path and match not in path_false_positives:
                    all_duplicates.append(match)
                    marked_duplicates[match] = True
        # Print the results
        if len(all_duplicates) > 0:
            all_duplicates = sorted(all_duplicates)
            result[path] = all_duplicates
            if duplicates_folder is not None:
                # Keep the file with higher size
                # and move the other to duplicates
                # Also save a file with original paths
                _move_to_duplicates_folder(len(result), duplicates_folder, path, *all_duplicates)
            elif print_result:
                print("Duplicates found for %s" % path)
                for dup in all_duplicates:
                    print(dup)
                print("========================")
    return result


def _move_to_duplicates_folder(id, folder, *all_paths):
    """
    Keep the best image where it is and move all the others
    to a subfolder. Save a file with the original paths.

    :param id: unique id for the folder, used to avoid name clashing
    :param folder: folder where to move the files
    :param all_paths: duplicate files, will move everything except the best file
    :return: best path
    """
    # Consider a file only if it was not moved before
    # Note: a file can be considered a duplicate of 2 different files
    # i.e. a file can belong to two different clusters of duplicates
    paths = list(filter(lambda path: os.path.exists(path), all_paths))
    if len(paths) < 2:
        return paths[0]
    # Find the best image
    best = _get_best_image(paths)
    # Create target folder and move the duplicates (except the best image)
    best_name = os.path.basename(best)
    subfolder_name = "%d_%s" % (id, best_name)
    target_folder = os.path.join(folder, subfolder_name)
    os.makedirs(target_folder, exist_ok=True)
    # Create symlink to best image (use abs path)
    best_link = os.path.join(target_folder, "0_%s" % best_name)
    best_abspath = os.path.abspath(best)
    os.symlink(best_abspath, best_link)
    # Move files
    duplicates = []
    fileid = 1
    for path in paths:
        if path != best:
            basename = os.path.basename(path)
            target_name = "%d_%s" % (fileid, basename)
            target_path = os.path.join(target_folder, target_name)
            duplicates.append((target_name, path))
            shutil.move(path, target_path)
            fileid += 1
    write_info_file(target_folder, best_abspath, duplicates)
    return best


def _get_best_image(paths):
    """
    Return the best image.
    We will return the image with the highest resolution, a PNG in case of a tie.

    :param paths:
    :return: path of the best image
    """
    best = None
    best_res = None
    for path in paths:
        with Image.open(path) as image:
            _, resolution = image.size
            if best is None or resolution > best_res or (resolution == best_res and image.format == 'PNG'):
                best = path
                best_res = resolution
    return best
