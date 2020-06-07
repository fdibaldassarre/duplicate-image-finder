#!/usr/bin/env python3

import os


def iter_folder(folder):
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        yield os.path.abspath(path)


def iter_recursive(folder):
    for dirpath, dirnames, filenames in os.walk(folder):
        for name in filenames:
            path = os.path.join(dirpath, name)
            yield os.path.abspath(path)
