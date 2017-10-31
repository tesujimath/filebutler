Name:           filebutler
Version:        0.1.1
Release:        1%{?dist}
Summary:        Utility for managing old files in large directory structures.

License:        GPLv3
URL:            https://github.com/tesujimath/filebutler
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  python-devel
#Requires:
BuildArch:      noarch

%description
Filebutler is a utility for managing large directory structures.  It is focused
on finding and removing old files.  The motivation is that find is far too slow
on directory trees with several million files.  Even using the cache output of find
can be rather slow for interactive queries.  Filebutler improves on this by
structuring filelists by age, and by user.

%define debug_package %{nil}

%prep
%setup -q

%build
%{__python} setup.py build
make

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --skip-build --root %{buildroot}
make install DESTDIR=%{buildroot}

%files
%doc LICENSE README.md
%{_bindir}/*
%{_mandir}/man1/*
%{python_sitelib}/*

%changelog
* Tue Oct 31 2017 Simon Guest <simon.guest@tesujimath.org> 0.1.0-1
- first packaging
