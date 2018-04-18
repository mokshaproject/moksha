#!/bin/bash -e

echo "Installing all packages in development mode"
for package in moksha.{common,hub,wsgi}; do
    echo "[$package] Installing"
    pushd $package
    python setup.py develop
    popd
    echo "[$package] done."
done
