# Duplicate Image Finder

A Python script to find duplicate images.

## Installation

Python version: 3.13

```sh
uv sync
```

## Usage

Run
```sh
./findDuplicates.py /path/to/some/folder --move-duplicates /path/to/duplicates/folder --persist
```
to find the duplicates in a folder and move them in the folder specified by `--move-duplicates.

Once the duplicates have been removed from the duplicates folder run
```sh
./restore.py /path/to/duplicates/folder
```
to restore the false positives. They are not moved again when running `findDuplicates.py` again.

## Library - Build

To build the wheel run
``
uv build
``

