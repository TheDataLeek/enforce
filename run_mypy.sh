#!/bin/sh

mypy --ignore-missing-imports --follow-imports=skip \
    ./enforce/exceptions.py \
    ./enforce/nodes.py \
    ./enforce/utils.py \
    ./enforce/enforcers.py \
    ./enforce/__init__.py \
    ./enforce/decorators.py \
    ./enforce/parsers.py \
    ./enforce/validator.py \
    ./enforce/settings.py \
    ./enforce/wrappers.py
    # ./enforce/types.py   # this file causes mypy to die
