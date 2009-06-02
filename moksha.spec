%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?pyver: %define pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

Name:           moksha 
Version:        0.1dev
Release:        0.1%{?dist}
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
Requires: python-twisted
Requires: python-stomper
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

%prep
%setup -q

%build
%{__python} setup.py build

%install
%{__rm} -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build \
    --install-data=%{_datadir} --root %{buildroot}

%{__mkdir_p} -m 0755 %{buildroot}/%{_localstatedir}/log/%{name}
%{__mkdir_p} -m 0700 %{buildroot}/%{_localstatedir}/cache/%{name}

%{__install} production/ %{buildroot}%{_datadir}/%{name}/production

%clean
%{__rm} -rf %{buildroot}


%files 
%defattr(-,root,root,-)
%doc README AUTHORS LICENSE COPYING
%{python_sitelib}/%{name}/
%attr(-,apache,root) %{_datadir}/%{name}
%attr(-,apache,root) %{_localstatedir}/log/%{name}
%{python_sitelib}/%{name}-%{version}-py%{pyver}.egg-info/
%attr(-,apache,apache) %dir %{_localstatedir}/cache/%{name}
%{_bindir}/moksha-hub

%changelog
* Wed May 27 2009 John (J5) Palmieri <johnp@redhat.com> - 0.1-0.1
- first package

