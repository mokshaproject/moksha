#!/bin/bash -e

PACKAGES=${1:-common hub wsgi}

echo "Installing all packages in development mode"
for package in $PACKAGES; do
    echo "[moksha.$package] Installing"
    pushd moksha.$package
    python setup.py develop
    popd
    echo "[moksha.$package] done."
done
