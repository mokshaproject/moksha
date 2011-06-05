#!/usr/bin/env python

import types
import moksha.ctl.core.ctl as ctl

funcs = [f for f in dir(ctl) if (
    f[0] != '_' and isinstance(getattr(ctl, f), types.FunctionType)
)]

# TODO -- use optparse to make a nice help message/execute pattern here
import pprint
pprint.pprint(funcs)

#ctl.bootstrap()
ctl.rebuild()
