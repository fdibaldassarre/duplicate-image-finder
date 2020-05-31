#!/usr/bin/env python3

from src.Matcher import find_similar
import argparse


parser = argparse.ArgumentParser(description="Find duplicate images")
parser.add_argument("db", help="Path of the database")
parser.add_argument("--folder", help="Folder to look in")
parser.add_argument("--recursive", action="store_true", default=True, help="True if should index the folder recursively")
parser.add_argument("--threshold", type=float, default=0.3, help="Similarity threshold")

args = parser.parse_args()
db_path = args.db
folder = args.folder
recursive = args.recursive
threshold = args.threshold

find_similar(db_path, folder=folder, recursive=recursive, threshold=threshold)
