#!/bin/bash -e

PACKAGES=${1:-common hub wsgi}

echo "running all tests"
for package in $PACKAGES; do
    echo "[moksha.$package] running tests"
    pushd moksha.$package
    python setup.py test
    popd
    echo "[moksha.$package] done with tests"
done
