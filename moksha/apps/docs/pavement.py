from paver.easy import *
from paver.setuputils import setup

setup(
    name="moksha.docs",
    version="1.0",
    url="http://moksha.fedorahosted.org",
    description="Moksha Docs App",
    author="Luke Macken",
    author_email="lmacken@redhat.com",
    packages=[],
    install_requires=["Moksha"],
    entry_points="""

    [moksha.application]
    docs = moksha.apps.docs.docs:docs

    """,
)
