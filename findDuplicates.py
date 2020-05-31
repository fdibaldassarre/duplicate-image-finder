#!/usr/bin/env python3

from src.Matcher import find_similar
import argparse


parser = argparse.ArgumentParser(description="Find duplicate images")
parser.add_argument("folder", help="Folder to look in")
parser.add_argument("--recursive", action="store_true", default=True, help="True if should index the folder recursively")
parser.add_argument("--db", help="Database to store the hash to")
parser.add_argument("--threshold", type=float, default=0.1, help="Similarity threshold")

args = parser.parse_args()
folder = args.folder
recursive = args.recursive
db_path = args.db
threshold = args.threshold

find_similar(folder, recursive=recursive, threshold=threshold, db_path=db_path)
