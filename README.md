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

It is possible to save the computed hashes using the --db flag

```sh
./findDuplicates.py /path/to/some/folder --db data
```
which will save a data.db file.
