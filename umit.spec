Summary: UMIT is a nmap frontend, developed in Python and GTK
Name: umit
Version: 6.04.1
Release: 1
License: GPL
Group: Applications/System
URL: http://umit.sf.net
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Requires: higwidgets >= 0.1.0, nmap
BuildArch: noarch

%description
The project goal is to develop a nmap frontend that is really 
useful for advanced users and easy to be used by newbies. With 
UMIT, a network admin could create scan profiles for faster and 
easier network scanning or even compare scan results to easily 
see any changes. A regular user will also be able to construct
powerful scans with UMIT command creator wizards.

%prep
%setup -q
mv umit.pyw umit

%build


%install
python_version=$(python -c 'import sys; v = sys.version_info; print "python%s.%s" % (v[0], v[1])')

%{__install} -d %{buildroot}%{_bindir}
%{__install} -d %{buildroot}%{_datadir}/pixmaps
%{__install} -d %{buildroot}/usr/lib/$python_version/site-packages/umitCore
%{__install} -d %{buildroot}/usr/lib/$python_version/site-packages/umitGUI
%{__install} -d %{buildroot}%{_datadir}/locale/pt_BR/LC_MESSAGES
%{__install} umit  %{buildroot}%{_bindir}
%{__install} umitCore/* %{buildroot}/usr/lib/python2.4/site-packages/umitCore
%{__install} umitGUI/*  %{buildroot}/usr/lib/python2.4/site-packages/umitGUI
%{__install} share/pixmaps/*  %{buildroot}%{_datadir}/pixmaps
%{__install} share/locale/pt_BR/LC_MESSAGES/umit.mo %{buildroot}%{_datadir}/locale/pt_BR/LC_MESSAGES

%clean
rm -rf %{buildroot} 


%files
%defattr(-,root,root,-)
%attr(775,root,root) %{_bindir}/umit
/usr/lib/python2.4/site-packages/umitCore/*
/usr/lib/python2.4/site-packages/umitGUI/*
%{_datadir}/pixmaps/*
%{_datadir}/locale/pt_BR/LC_MESSAGES/*

%changelog
* Wed Apr 19 2006 root <root@saproad.globalred.com.br> - 
- Initial build.

