from paver.easy import *
from paver.setuputils import setup

setup(
    name="moksha.menus",
    version="1.0",
    url="http://moksha.fedorahosted.org",
    description="Moksha Menus App",
    author="Luke Macken",
    author_email="lmacken@redhat.com",
    packages=['moksha'],
    namespace_packages=['moksha'],
    install_requires=["Moksha"],
    entry_points="""

    [moksha.menu]
    default_menu = moksha.apps.menus:MokshaDefaultMenu

    [moksha.application]
    menu = moksha.apps.menus.controllers:MokshaMenuController

    """,
)
