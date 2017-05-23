#!/bin/sh

mypy --ignore-missing-imports --follow-imports=skip \
    ./enforce/__init__.py \
    ./enforce/settings.py \
    ./enforce/decorators.py \
    ./enforce/validator.py \
    ./enforce/nodes.py
