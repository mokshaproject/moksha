#!/bin/bash -e

echo "running all tests"
for package in moksha.{common,hub,wsgi,feeds}; do
    echo "[$package] running tests"
    pushd $package
    python setup.py test
    popd
    echo "[$package] done with tests"
done
