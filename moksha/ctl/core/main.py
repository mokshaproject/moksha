#!/usr/bin/env python
""" This command is used to manage the moksha development configuration.

Example:
    $ ./moksha-ctl.py bootstrap
    $ ./moksha-ctl.py rebuild
    $ ./moksha-ctl.py start
    $ ./moksha-ctl.py wtf
    $ ./moksha-ctl.py logs

Passing arguments:
    You can also pass arguments to particular commands like start, restart, and
    stop, and install_app.

    $ ./moksha-ctl.py restart:moksha-hub

Virtual Environments:
    Virtualenvs are managed for you by way of virtualenvwrapper.  Check in
    ~/.virtualenvs for the actual directory structure.  You can also specify
    what environment to use with the -E or --environment=some_env options."""

import moksha.ctl.core.ctl as ctl
import optparse
import types
import sys

def main(entry_point=True):
    usage = "usage: %prog [options] command1 [command2, command3, ...]"
    usage += "\n\n" + __doc__ + "\n\nCommands:\n"
    cmd_usage_template = "{cmd:>15}  {help}"

    if entry_point:
        usage = usage.replace('./moksha-ctl.py', 'moksha-ctl')

    # First, extract all non-hidden functions from the core module
    funcs = [f for f in dir(ctl) if (
        f[0] != '_' and isinstance(getattr(ctl, f), types.FunctionType)
    )]

    # Construct a nice usage string
    usage = usage + '\n'.join([
        cmd_usage_template.format(
            cmd=func, help=getattr(ctl, func).__doc__)
        for func in funcs
    ])

    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-E', '--environment', dest='venv', default=None,
                      help='name of the virtualenv to use')

    opts, args = parser.parse_args()
    arguments = []
    for arg in args:
        items = arg.split(':')
        arguments.append({'cmd':items[0], 'args':items[1:]})

    if len(args) == 0:
        parser.print_usage()
        sys.exit(0)

    failed = [arg['cmd'] for arg in arguments if not arg['cmd'] in funcs]
    if failed:
        for fail in failed:
            print " * %s is not a command" % fail
        print
        parser.print_usage()
        sys.exit(0)

    if opts.venv:
        ctl.ctl_config['venv'] = opts.venv

    # Render the moksha logo.  Haters gonna hate.
    try:
        from fabulous import image
        print image.Image("website/img/moksha-logo.png", width=80)
    except Exception as e:
        pass  # Oh well.

    # Actually execute the commands
    for arg in arguments:
        getattr(ctl, arg['cmd'])(*arg['args'])
