from paver.easy import *
from paver.setuputils import setup, find_package_data, find_packages

setup(
    name="moksha.menus",
    version="0.1",
    url="http://moksha.fedorahosted.org",
    description="Moksha Menus App",
    author="Luke Macken",
    author_email="lmacken@redhat.com",
    packages=find_packages(),
    package_data=find_package_data(),
    namespace_packages=['moksha'],
    install_requires=["Moksha"],
    entry_points="""

    [moksha.menu]
    default_menu = moksha.apps.menus:MokshaDefaultMenu

    [moksha.application]
    menu = moksha.apps.menus.controllers:MokshaMenuController

    """,
)

@task
def rpm():
    sh('rm -fr dist')
    sh('paver sdist')
    sh('mv dist/* ~/rpmbuild/SOURCES/')
    sh('cp *.spec ~/rpmbuild/SPECS/')
    sh('rpmbuild -ba ~/rpmbuild/SPECS/moksha-menus.spec')

@task
@needs(['rpm'])
def reinstall():
    sh('sudo rpm -ivh --replacefiles --replacepkgs ~/rpmbuild/RPMS/noarch/moksha-menus-0.1-1.noarch.rpm')
