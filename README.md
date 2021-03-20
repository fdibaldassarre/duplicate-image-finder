# Duplicate Image Finder

A Python script to find duplicate images.

## Installation

Python version: 3.9

```sh
pip install -r requirements.txt
```

## Usage

Run
```sh
./findDuplicates.py /path/to/some/folder --move-duplicates /path/to/duplicates/folder --persist
```
to find the duplicates in a folder and move them in a duplicates folder.

Once the duplicates have been removed from the duplicates folder run
```sh
./restore.py /path/to/duplicates/folder
```
to restore the false positives.

The program stores false positives and they are not moved again on successive runs.
