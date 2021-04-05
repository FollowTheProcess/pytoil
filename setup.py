#!/usr/bin/env python3

"""
Setuptools shim to allow editable installs.

pip install -e .
or
python setup.py develop
"""

import setuptools

if __name__ == "__main__":
    setuptools.setup()
