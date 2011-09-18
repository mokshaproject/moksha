%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?pyver: %define pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

Name:           moksha
Version:        0.6.1
Release:        1%{?dist}
Summary:        A platform for creating real-time web applications
Group:          Applications/Internet
License:        ASL 2.0
URL:            https://fedorahosted.org/moksha
Source0:        https://fedorahosted.org/releases/m/o/%{name}/%{name}-%{version}.tar.bz2

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

BuildRequires: python-setuptools
BuildRequires: pytz
BuildRequires: python-setuptools-devel
BuildRequires: python-devel
BuildRequires: python-pygments
BuildRequires: python-paver
BuildRequires: python-sphinx
BuildRequires: python-paste
BuildRequires: python-nose
BuildRequires: python-BeautifulSoup
BuildRequires: python-stomper
BuildRequires: python-tw-forms
BuildRequires: python-tw-jquery
BuildRequires: python-feedparser
BuildRequires: python-feedcache
BuildRequires: python-repoze-what-quickstart
BuildRequires: python-shove
BuildRequires: python-bunch
BuildRequires: TurboGears2
BuildRequires: python-daemon

BuildRequires: pyOpenSSL
BuildRequires: python-babel
BuildRequires: orbited
BuildRequires: python-repoze-who-testutil

%if 0%{?el5}
BuildRequires: python-sqlite2
BuildRequires: python-hashlib
Requires: python-sqlite2
Requires: python-hashlib
%endif

Requires: TurboGears2
Requires: python-toscawidgets >= 0.9.1
Requires: python-zope-sqlalchemy
Requires: python-shove
Requires: python-feedcache
Requires: python-feedparser
Requires: python-tw-jquery >= 0.9.4.1
Requires: python-sphinx
Requires: python-paver
Requires: python-tw-forms
Requires: python-morbid
Requires: pytz
Requires: pyevent
Requires: python-repoze-who-testutil
Requires: python-BeautifulSoup
Requires: python-twisted
Requires: python-stomper
Requires: python-daemon

Requires: pyOpenSSL
Requires: python-babel


%description
Moksha is a platform for creating real-time collaborative web applications.  It 
provides a set of Python and JavaScript API's that make it simple to create 
rich applications that can acquire, manipulate, and visualize data from 
external services. It is a unified framework build using the best available 
open source technologies such as TurboGears2, jQuery, AMQP, and Orbited.

%package doc
Summary: Developer documentation for Moksha
Group: Documentation
Requires: %{name} = %{version}-%{release}

%description doc
This package contains developer documentation for Moksha along with
other supporting documentation

%package server
Summary: mod_wsgi Moksha server
Group: Applications/Internet
Requires: %{name} = %{version}-%{release}
Requires: mod_wsgi httpd
Requires: orbited

%description server
This package contains an Apache mod_wsgi configuration for Moksha.

%prep
%setup -q

%build
%{__python} setup.py build

%{__sed} -i -e 's/$VERSION/%{version}/g' docs/conf.py
make -C docs html
#%{__rm} docs/_build/html/.buildinfo

%install
%{__rm} -rf %{buildroot}

%{__python} setup.py install -O1 --skip-build \
    --install-data=%{_datadir} --root %{buildroot}

%{__mkdir_p} %{buildroot}%{_datadir}/%{name}/production/apache
%{__mkdir_p} %{buildroot}%{_datadir}/%{name}/production/nginx
%{__mkdir_p} %{buildroot}%{_datadir}/%{name}/production/rabbitmq
%{__mkdir_p} %{buildroot}%{_sysconfdir}/logrotate.d
%{__mkdir_p} -m 0755 %{buildroot}/%{_localstatedir}/cache/%{name}
%{__mkdir_p} -m 0755 %{buildroot}/%{_localstatedir}/lib/%{name}
%{__mkdir_p} -m 0755 %{buildroot}%{_sysconfdir}/httpd/conf.d
%{__mkdir_p} -m 0755 %{buildroot}/%{_sysconfdir}/%{name}/
%{__mkdir_p} -m 0755 %{buildroot}/%{_sysconfdir}/%{name}/conf.d
%{__mkdir_p} -m 0755 %{buildroot}/%{_sysconfdir}/init.d/
%{__mkdir_p} -m 0755 %{buildroot}/%{_var}/log/%{name}

%{__install} -m 0644 production/*.* %{buildroot}%{_datadir}/%{name}/production/
%{__install} -m 0644 production/apache/* %{buildroot}%{_datadir}/%{name}/production/apache
%{__install} -m 0644 production/apache/moksha.conf %{buildroot}%{_sysconfdir}/httpd/conf.d/
%{__install} -m 0644 production/nginx/* %{buildroot}%{_datadir}/%{name}/production/nginx
%{__install} -m 0644 production/rabbitmq/*.patch %{buildroot}%{_datadir}/%{name}/production/rabbitmq
%{__install} -m 0755 production/rabbitmq/run %{buildroot}%{_datadir}/%{name}/production/rabbitmq
%{__install} -m 0644 production/logrotate/moksha %{buildroot}%{_sysconfdir}/logrotate.d/
%{__install} production/moksha-hub %{buildroot}%{_bindir}/moksha-hub
%{__install} production/moksha-hub.init %{buildroot}%{_sysconfdir}/init.d/moksha-hub
%{__install} -d -m 0755 %{buildroot}/var/run/%{name}

%{__cp} production/sample-production.ini %{buildroot}%{_sysconfdir}/%{name}/sample-production.ini
%{__cp} development.ini %{buildroot}%{_sysconfdir}/%{name}/development.ini
%{__cp} orbited.cfg %{buildroot}%{_sysconfdir}/%{name}/orbited.cfg

%{__sed} -i -e 's/$VERSION/%{version}/g' %{buildroot}%{_sysconfdir}/%{name}/sample-production.ini

%{__rm} %{buildroot}%{_datadir}/%{name}/production/moksha-hub.init


%check
PYTHONPATH=$(pwd) python run_tests.py
pushd moksha/apps/demo/MokshaJQPlotDemo/
PYTHONPATH=$(pwd):../../../../ python run_tests.py
popd

# Remove the tests
%{__rm} -r %{buildroot}%{python_sitelib}/%{name}/tests

# Remove the demo after its tests pass
%{__rm} -r %{buildroot}%{python_sitelib}/%{name}/apps/demo


%post
/sbin/chkconfig --add moksha-hub


%post server
semanage fcontext -a -t httpd_cache_t '/var/cache/moksha(/.*)?'
restorecon -Rv /var/cache/moksha

%clean
%{__rm} -rf %{buildroot}

%pre
%{_sbindir}/groupadd -r %{name} &>/dev/null || :
%{_sbindir}/useradd  -r -s /sbin/nologin -d %{_datadir}/%{name} -M \
                           -c 'Moksha' -g %{name} %{name} &>/dev/null || :


%preun
if [ $1 -eq 0 ]; then
        /sbin/service moksha-hub stop >/dev/null 2>&1
        /sbin/chkconfig --del moksha-hub
fi

%files 
%defattr(-,root,root,-)
%doc README AUTHORS COPYING
%{_bindir}/moksha
%{_bindir}/moksha-hub
%{_sysconfdir}/init.d/moksha-hub
%{python_sitelib}/%{name}/
%{python_sitelib}/%{name}-%{version}-py%{pyver}.egg-info/
%attr(-,apache,apache) %dir %{_localstatedir}/lib/%{name}
%attr(0755,root,%{name}) %dir %{_var}/log/%{name}
%ghost %attr(755, %{name}, %{name}) /var/run/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}

%files server
%defattr(-,root,root,-)
%attr(-,apache,root) %{_datadir}/%{name}
%config(noreplace) %{_sysconfdir}/httpd/conf.d/moksha.conf
%config(noreplace) %{_sysconfdir}/%{name}/*.ini
%config(noreplace) %{_sysconfdir}/%{name}/orbited.cfg
%attr(-,apache,apache) %dir %{_localstatedir}/cache/%{name}/

%files doc
%defattr(-,root,root)
%doc docs/_build/html

%changelog
* Sun Sep 18 2011 Luke Macken <lmacken@redhat.com> 0.6.1-1
- new package built with tito

* Fri Aug 19 2011 Luke Macken <lmacken@redhat.com> - 0.6.0-1
- 0.6.0 release
- Update our dependencies to finally get the test suite running
- Improve how we run our unit tests, to get them working on RHEL5

* Wed Dec 15 2010 Luke Macken <lmacken@redhat.com> - 0.5.0-4
- Add a logrotate configuration

* Tue Dec 14 2010 Luke Macken <lmacken@redhat.com> - 0.5.0-3
- Handle ghosting /var/run/moksha
- Setup a log directory
- Get the moksha-hub init script working properly
- A variety of specfile cleanups from our package review (#661902)

* Fri Dec 10 2010 Luke Macken <lmacken@redhat.com> - 0.5.0-2
- Fix our Source URL
- Fix files-attr-not-set rpmlint errors
- Fix up the description
- Remove redundant license

* Sat Sep 11 2010 Luke Macken <lmacken@redhat.com> - 0.5.0-1
- 0.5.0 release
- Run the full test suite

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

