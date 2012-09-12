#!/bin/bash -e

# Note that 'moksha.feeds' is explicitly excluded from the list because it
# breaks everything.
echo "running all tests"
for package in moksha.{common,hub,wsgi}; do
    echo "[$package] running tests"
    pushd $package
    python setup.py test
    popd
    echo "[$package] done with tests"
done
