# Duplicate Image Finder

A Python script to find duplicate images.

## Installation

```sh
pip install -r requirements.txt
```

## Usage

```sh
./findDuplicates.py /path/to/some/folder
```
will output the list of duplicate files.

To move the duplicates in a dedicated folder use the `--move-duplicates` flag

```sh
./findDuplicates.py /path/to/some/folder --move-duplicates /path/to/duplicates/folder
```

It is possible to read and save the computed hashes using the `--db` flag

```sh
./findDuplicates.py /path/to/some/folder --db data
```
Storing the hashes in a database reduces execution time if the script is run multiple times on the same files.
