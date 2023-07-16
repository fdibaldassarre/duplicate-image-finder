#!/usr/bin/env python3

from src.dupimage.Matcher import find_similar
import argparse
import os


parser = argparse.ArgumentParser(description="Find duplicate images")
parser.add_argument("folder", help="Folder to look in")
parser.add_argument("--recursive", action="store_true", default=True,
                    help="True if should index the folder recursively")
parser.add_argument("--threshold", type=float, default=0.1, help="Similarity threshold")
parser.add_argument("--move-duplicates", dest="duplicates_folder", type=str, default=None,
                    help="Folder to move duplicates to")
parser.add_argument("--persist", action="store_true", help="Persist the image hashses and false duplicates")

args = parser.parse_args()
folder = args.folder
recursive = args.recursive
threshold = args.threshold
duplicates_folder = args.duplicates_folder
persistence = args.persist

db_path = None
false_positives_db_path = None
if persistence:
    persistence_folder = os.path.join(folder, ".duplicate-image-finder")
    if not os.path.exists(persistence_folder):
        os.mkdir(persistence_folder)
    db_path = os.path.join(persistence_folder, "hashes.db")
    false_positives_db_path = os.path.join(persistence_folder, "false-positives.db")

print_result = duplicates_folder is None

if duplicates_folder is not None:
    if not os.path.exists(duplicates_folder):
        os.makedirs(duplicates_folder)

find_similar(folder, recursive=recursive, threshold=threshold, db_path=db_path,
             false_positives_db_path=false_positives_db_path, print_result=print_result,
             duplicates_folder=duplicates_folder)
