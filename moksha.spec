%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?pyver: %define pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

Name:           moksha
Version:        0.4.0
Release:        1%{?dist}
Summary:        A flexable platform for creating live collaborative web applications
Group:          Applications/Internet
License:        AGPLv3
URL:            https://fedorahosted.org/moksha
Source0:        moksha-%{version}.tar.bz2

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

BuildRequires: python-setuptools 
BuildRequires: python-setuptools-devel
BuildRequires: python-devel
BuildRequires: python-pygments
BuildRequires: python-paver
BuildRequires: python-sphinx
BuildRequires: python-paste
BuildRequires: python-nose

Requires: TurboGears2
Requires: python-toscawidgets >= 0.9.1
Requires: python-zope-sqlalchemy 
Requires: python-shove
Requires: python-feedcache
Requires: python-feedparser
Requires: python-tw-jquery >= 0.9.4.1
#Requires: python-repoze-squeeze
#Requires: python-repoze-profile
Requires: orbited
Requires: python-sphinx
Requires: python-paver
Requires: python-tw-forms
Requires: python-morbid
Requires: pytz
Requires: pyevent
Requires: python-repoze-who-testutil

%description
Moksha is a platform for creating real-time collaborative web applications.  It 
provides a set of Python and JavaScript API's that make it simple to create 
rich applications that can acquire, manipulate, and visualize data from 
external services. It is a unified framework build using the best available 
open source technologies such as TurboGears2, jQuery, AMQP, and Orbited.  More 
information can be found on the Moksha Project Page at 

%package docs
Summary: Developer documentation for Moksha
Group: Documentation
Requires: %{name} = %{version}-%{release}

%description docs
This package contains developer documentation for Moksha along with
other supporting documentation

%package server
Summary: mod_wsgi Moksha server
Group: Applications/Internet
Requires: %{name} = %{version}-%{release}
Requires: mod_wsgi httpd

%description server
This package contains an Apache mod_wsgi configuration for Moksha.

%package hub
Summary: Moksha Hub
Group: Applications/Internet
Requires: %{name} = %{version}-%{release}
Requires: python-twisted
Requires: python-stomper

%description hub
This package contains the Moksha Hub.

%prep
%setup -q

%build
%{__rm} -fr moksha/tests
%{__python} setup.py build

%{__sed} -i -e 's/$VERSION/%{version}/g' docs/conf.py
make -C docs html

%install
%{__rm} -rf %{buildroot}

%{__python} setup.py install -O1 --skip-build \
    --install-data=%{_datadir} --root %{buildroot}

%{__mkdir_p} %{buildroot}%{_datadir}/%{name}/production/apache
%{__mkdir_p} %{buildroot}%{_datadir}/%{name}/production/nginx
%{__mkdir_p} %{buildroot}%{_datadir}/%{name}/production/rabbitmq
%{__mkdir_p} -m 0700 %{buildroot}/%{_localstatedir}/cache/%{name}
%{__mkdir_p} -m 0700 %{buildroot}/%{_localstatedir}/lib/%{name}
%{__mkdir_p} -m 0755 %{buildroot}%{_sysconfdir}/httpd/conf.d
%{__mkdir_p} -m 0755 %{buildroot}/%{_sysconfdir}/%{name}/
%{__mkdir_p} -m 0755 %{buildroot}/%{_sysconfdir}/%{name}/conf.d
%{__mkdir_p} -m 0755 %{buildroot}/%{_sysconfdir}/init.d/

%{__install} production/*.* %{buildroot}%{_datadir}/%{name}/production/
%{__install} production/apache/* %{buildroot}%{_datadir}/%{name}/production/apache
%{__install} production/apache/moksha.conf %{buildroot}%{_sysconfdir}/httpd/conf.d/
%{__install} production/nginx/* %{buildroot}%{_datadir}/%{name}/production/nginx
%{__install} production/rabbitmq/* %{buildroot}%{_datadir}/%{name}/production/rabbitmq
%{__cp} production/sample-production.ini %{buildroot}%{_sysconfdir}/%{name}/production.ini
%{__sed} -i -e 's/$VERSION/%{version}/g' %{buildroot}%{_sysconfdir}/%{name}/production.ini
%{__cp} orbited.cfg %{buildroot}%{_sysconfdir}/%{name}/orbited.cfg

%{__install} production/moksha-hub %{buildroot}%{_bindir}/moksha-hub
%{__install} production/moksha-hub.init %{buildroot}%{_sysconfdir}/init.d/moksha-hub

%post server
semanage fcontext -a -t httpd_cache_t '/var/cache/moksha(/.*)?'
restorecon -Rv /var/cache/moksha


%clean
%{__rm} -rf %{buildroot}


%files 
%defattr(-,root,root,-)
%doc README AUTHORS LICENSE COPYING
%{python_sitelib}/%{name}/
%{python_sitelib}/%{name}-%{version}-py%{pyver}.egg-info/
%attr(-,apache,apache) %dir %{_localstatedir}/lib/%{name}

%files server
%attr(-,apache,root) %{_datadir}/%{name}
%config(noreplace) %{_sysconfdir}/httpd/conf.d/moksha.conf
%config(noreplace) %{_sysconfdir}/%{name}/production.ini
%config(noreplace) %{_sysconfdir}/%{name}/orbited.cfg
%attr(-,apache,apache) %dir %{_localstatedir}/cache/%{name}/

%files hub
%defattr(-,root,root,-)
%{_bindir}/moksha-hub
%{_sysconfdir}/init.d/moksha-hub

%files docs
%defattr(-,root,root)
%doc docs/_build/html

%changelog
* Thu Sep 24 2009 Luke Macken <lmacken@redhat.com> - 0.4.0-1
- 0.4.0 release

* Tue Sep 22 2009 Luke Macken <lmacken@redhat.com> - 0.3.5-1
- 0.3.5

* Sat Aug 29 2009 Luke Macken <lmacken@redhat.com> - 0.3.4-1
- Add a moksha-hub subpackage

* Mon Aug 24 2009 Luke Macken <lmacken@redhat.com> - 0.3.3-1
- Include our orbited configuration file in the moksha-server subpackage
- Create a /etc/moksha/conf.d for our app configs

* Sat Aug 22 2009 Luke Macken <lmacken@redhat.com> - 0.3.2-1
- Update to 0.3.2

* Sat Aug 15 2009 Luke Macken <lmacken@redhat.com> - 0.3.1-2
- Break out the mod_wsgi configuration into a moksha-server subpackage.

* Fri Aug 14 2009 Luke Macken <lmacken@redhat.com> - 0.3.1-1
- 0.3.1

* Mon Aug 03 2009 Luke Macken <lmacken@redhat.com> - 0.3-1
- 0.3, bugfix release

* Wed Jun 03 2009 Luke Macken <lmacken@redhat.com> - 0.2-1
- Add nose to the build requirements

* Wed May 27 2009 John (J5) Palmieri <johnp@redhat.com> - 0.1-0.1
- first package

