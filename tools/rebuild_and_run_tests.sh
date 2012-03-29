#!/usr/bin/env zsh
#
# Useful for 'git bisect run'
#   Ralph Bean <rbean@redhat.com>

source ~/.zshrc
source ~/.zshrc.local

./moksha-ctl.py rebuild
workon moksha
python setup.py test
deactivate
