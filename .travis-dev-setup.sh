#!/bin/bash -e

# Note that 'moksha.feeds' is explicitly excluded from the list because it
# breaks everything.
echo "Installing all packages in development mode"
for package in moksha.{common,hub,wsgi}; do
    echo "[$package] Installing"
    pushd $package
    python setup.py develop
    popd
    echo "[$package] done."
done
