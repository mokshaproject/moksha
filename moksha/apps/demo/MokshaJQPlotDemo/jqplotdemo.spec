%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?pyver: %define pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

%global modname JQPlotDemo

Name:           jqplotdemo
Version:        0.2
Release:        1%{?dist}
Summary:        Moksha Chat App
Group:          Applications/Internet
License:        ASL 2.0
URL:            http://moksha.fedorahosted.org
Source0:        %{modname}-%{version}dev.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python-setuptools-devel
BuildRequires:  python-paver
BuildRequires:  moksha
Requires:       moksha

%description


%prep
%setup -q -n %{modname}-%{version}dev

%build
rm -rf %{buildroot}
#paver build
%{__python} setup.py build

%install
%{__rm} -rf %{buildroot}
#paver install -O1 --skip-build --root %{buildroot}
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
install -d %{buildroot}/etc/moksha/conf.d/jqplotdemo
cp production.ini %{buildroot}/etc/moksha/conf.d/jqplotdemo/production.ini

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/moksha/conf.d/%{name}/*.ini
#%{python_sitelib}/%{modname}-%{version}-py%{pyver}-nspkg.pth
%{python_sitelib}/%{modname}-%{version}dev-py%{pyver}.egg-info/
%{python_sitelib}/jqplotdemo
