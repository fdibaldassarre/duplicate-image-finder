#!/usr/bin/env python3

import argparse
from src.Restore import restore

parser = argparse.ArgumentParser(description="Restore non duplicate images")
parser.add_argument("folder", help="Duplicates folder")

args = parser.parse_args()
folder = args.folder

restore(folder)
