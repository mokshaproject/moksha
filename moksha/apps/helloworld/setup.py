from setuptools import setup, find_packages

setup(
    name='moksha.demo',
    version='0.1',
    description='A Hello World Moksha app',
    author='Luke Macken',
    author_email='lmacken@redhat.com',
    url='http://moksha.fedorahosted.org',
    license='GPLv3+',
    install_requires=['Moksha'],
    packages=find_packages(),
    include_package_data=True,
    test_suite='nose.collector',

    entry_points="""

    [moksha.root]
    root = demo.controllers.root:Root

    [moksha.application]
    helloworld = demo.controllers.root:Root

    [moksha.producer]
    helloworld = demo.producer:HelloWorldProducer

    [moksha.consumer]
    helloworld = demo.consumer:HelloWorldConsumer

    [moksha.widget]
    basic = demo.widgets.basic:HelloWorldWidget
    live = demo.widgets.live:HelloWorldWidget

    """
)
