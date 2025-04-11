#!/bin/bash
set -e
python3 -m pip install --upgrade build
python3 -m build
pip install --force-reinstall dist/minichemistry-0.0.9-py3-none-any.whl