%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?pyver: %define pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

%global modname moksha.menus

Name:           moksha-menus
Version:        0.1
Release:        1%{?dist}
Summary:        A dynamic menu API for Moksha
Group:          Applications/Internet
License:        AGPLv3
URL:            https://fedorahosted.org/moksha
Source0:        moksha.menus-%{version}.tar.gz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

BuildRequires: python-setuptools-devel
BuildRequires: python-paver

Requires: moksha

%description
TODO

%prep
%setup -q -n moksha.menus-%{version}

%build
paver bdist_egg

%install
%{__rm} -rf %{buildroot}
%{__mkdir} -p %{buildroot}%{python_sitelib}
PYTHONPATH=%{buildroot}%{python_sitelib} easy_install \
    --prefix %{buildroot}%{_usr} --no-deps --always-unzip \
    dist/*.egg

# TODO: see if this is absolutely necessar!
%{__rm} %{buildroot}%{python_sitelib}/easy-install.pth

%{__rm} %{buildroot}%{python_sitelib}/site.py{,c}

%clean
%{__rm} -rf %{buildroot}


%files 
%defattr(-,root,root,-)
#%doc README AUTHORS LICENSE COPYING
%{python_sitelib}/%{modname}-%{version}-py%{pyver}.egg/

%changelog
* Thu Aug 06 2009 Luke Macken <lmacken@redhat.com> - 0.1-1
- Initial package
