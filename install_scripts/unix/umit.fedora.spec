Summary: Umit
%define version 0.9.5
License: GNU Public License
Group: Network
Name: Umit
Prefix: /usr
Provides: Umit
Release: 1
Source: umit-0.9.4.tar.gz
URL: http://umitproject.blogspot.com
Version: %{version}
Buildroot: /tmp/umitrpm
%define python /opt/python2.4/bin/python
%define py_compile %{python} /opt/python2.4/lib/python2.4/py_compile.py

%description
Umit is the newest network scanning frontend, and it's been developed in Python and GTK and was started with the sponsoring of Google's Summer of Code.

The project goal is to develop a network scanning frontend that is really useful for advanced users and easy to be used by newbies. With Umit, a network admin could create scan profiles for faster and easier network scanning or even compare scan results to easily see any changes. A regular user will also be able to construct powerful scans with Umit command creator wizards.


%prep
%setup -q
%build
%{py_compile} umit
%{py_compile} umitCore/*.py
%{py_compile} umitGUI/*.py
%{py_compile} higwidgets/*.py

%clean
rm -rf *.pyc
rm -rf umitCore/*.pyc
rm -rf umitGUI/*.pyc
rm -rf higwidgets/*.pyc

%install

mkdir -p $RPM_BUILD_ROOT/usr/local/umit
mkdir -p $RPM_BUILD_ROOT/usr/bin
mkdir -p $RPM_BUILD_ROOT/usr/lib/python2.4/site-packages/umitCore
mkdir -p $RPM_BUILD_ROOT/usr/lib/python2.4/site-packages/umitGUI
mkdir -p $RPM_BUILD_ROOT/usr/lib/python2.4/site-packages/higwidgets


cp umit.pyc $RPM_BUILD_ROOT/usr/bin/umit
chmod a+x $RPM_BUILD_ROOT/usr/bin/umit

cp -va umit.pyc $RPM_BUILD_ROOT/usr/local/umit
cp -va umitCore/*.pyc $RPM_BUILD_ROOT/usr/lib/python2.4/site-packages/umitCore
cp -va umitGUI/*.pyc $RPM_BUILD_ROOT/usr/lib/python2.4/site-packages/umitGUI
cp -va higwidgets/*.pyc $RPM_BUILD_ROOT/usr/lib/python2.4/site-packages/higwidgets

%files
/usr
