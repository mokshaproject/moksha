import os
from paver.easy import *

@task
def rpm():
    specfile = '%s.spec' % options.rpm_name
    if not os.path.isfile(specfile):
        spec_file = file('%s.spec' % options.rpm_name, 'w')
        spec_file.write("""\
%%{!?python_sitelib: %%define python_sitelib %%(%%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%%{!?pyver: %%define pyver %%(%%{__python} -c "import sys ; print sys.version[:3]")}

%%global modname %(name)s

Name:           %(rpm_name)s
Version:        %(version)s
Release:        %(release)s%%{?dist}
Summary:        %(description)s
Group:          Applications/Internet
License:        %(license)s
URL:            %(url)s
Source0:        %%{modname}-%%{version}.tar.bz2
BuildRoot:      %%{_tmppath}/%%{name}-%%{version}-%%{release}-root-%%(%%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python-setuptools-devel
BuildRequires:  python-paver
BuildRequires:  moksha
Requires:       moksha

%%description
%(long_description)s

%%prep
%%setup -q -n %%{modname}-%%{version}

%%build
rm -rf %%{buildroot}
paver build

%%install
%%{__rm} -rf %%{buildroot}
paver install -O1 --skip-build --root %%{buildroot}

%%clean
%%{__rm} -rf %%{buildroot}

%%files
%%defattr(-,root,root,-)
%%config(noreplace) %%{_sysconfdir}/moksha/conf.d/%%{modname}/
%%{python_sitelib}/%%{modname}-%%{version}-py%%{pyver}-nspkg.pth
%%{python_sitelib}/%%{modname}-%%{version}-py%%{pyver}.egg-info/
%%{python_sitelib}/moksha/apps/*
        """ % {'name': options.name, 'version': options.version,
               'release': options.release, 'description': options.description,
               'long_description': options.long_description, 'license': options.license,
               'url': options.url, 'rpm_name': options.rpm_name})
        spec_file.close()

    sh('paver sdist --format=bztar')
    sh('mv dist/* ~/rpmbuild/SOURCES/')
    sh('cp %s.spec ~/rpmbuild/SPECS/' % options.rpm_name)
    sh('rpmbuild -ba ~/rpmbuild/SPECS/%s.spec' % options.rpm_name)

@task
@needs(['rpm'])
def reinstall():
    sh('sudo rpm -e %s' % options.rpm_name, ignore_error=True)
    sh('sudo rpm -ivh ~/rpmbuild/RPMS/noarch/%s-%s-%s.*noarch.rpm' % (
        options.rpm_name, options.version, options.release))

@task
@needs('setuptools.command.install')
def install():
    """Overrides install to make sure that our setup.py is generated."""
    conf_d = path('etc') / 'moksha' / 'conf.d' / options.name
    os.makedirs(path(options.install.root) / conf_d)
    for cfg in path('.').glob('*.ini'):
        if os.path.exists(cfg):
            dest = path(options.install.root) / conf_d / cfg[2:]
            sh('cp %s %s' % (cfg, dest))
