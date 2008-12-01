import paver.doctools
import paver.virtual
from setuptools import find_packages

options(
    sphinx=Bunch(
    ),
    virtualenv=Bunch(
    ),
    setup=Bunch(
        name='Moksha',
        version='0.0.1',
        description='TODO',
        long_description='TODO',
        classifiers=[],
        keywords='turbogears2',
        author='Luke Macken',
        author_email='lmacken@redhat.com',
        url='http://moksha.fedorahosted.org',
        license='GPLv2+',
        packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
        include_package_data=True,
        zip_safe=False,
        install_requires=[
            'Babel',
            'Pylons',
            'SQLAlchemy>=0.4',
            'ToscaWidgets>=0.9.2',
        ],
        extras_require={
            'core-testing':["nose", "TurboKid", "TurboJson"]
        },
        entry_points='''
            [paste.global_paster_command]
            tginfo = tg.commands.info:InfoCommand

            [turbogears2.command]
            tginfo = tg.commands.info:InfoCommand
            serve = paste.script.serve:ServeCommand [Config]
            shell = pylons.commands:ShellCommand
        '''
    )
)

@task
@needs(["minilib", "generate_setup", "setuptools.command.sdist"])
def sdist():
    pass

@task
@needs(["minilib", "generate_setup", "setuptools.command.bdist_egg"])
def bdist_egg():
    pass
