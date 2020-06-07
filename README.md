# Duplicate Image Finder

A Python script to find duplicate images.

## Installation

```sh
pip install -r requirements.txt
```

## Sample usage

Run
```sh
./findDuplicates.py /path/to/some/folder
```
to print a list of possible duplicates.


## Advanced

Retrieve the duplicates and move them in a separate folder

```sh
./findDuplicates.py /path/to/some/folder --move-duplicates /path/to/duplicates/folder
```

For each duplicate the program will create a dedicate folder with the duplicates and a link to the original file.

Once the duplicates have been removed run the restore command to copy the false positives to their original location.

```sh
./restore.py /path/to/duplicates/folder
```

## Persistence

It is possible to read and save the computed hashes using the `--db` flag

```sh
./findDuplicates.py /path/to/some/folder --db data
```
Storing the hashes in a database reduces execution time if the script is run multiple times on the same files.



