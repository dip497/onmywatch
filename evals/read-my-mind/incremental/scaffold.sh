#!/usr/bin/env bash
set -e
python3 "$(dirname "$0")/../fixtures.py" incremental
