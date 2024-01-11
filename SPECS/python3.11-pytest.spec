%global __python3 /usr/bin/python3.11
%global python3_pkgversion 3.11

%global pkgname pytest

Name:           python%{python3_pkgversion}-pytest
%global base_version 7.2.0
#global prerelease ...
Version:        %{base_version}%{?prerelease:~%{prerelease}}
Release:        1%{?dist}
Summary:        Simple powerful testing with Python
License:        MIT
URL:            https://pytest.org
# see https://github.com/pytest-dev/pytest/issues/10042#issuecomment-1237132867
Patch:          pytest-7.1.3-fix-xfails.patch
Source0:        %{pypi_source pytest %{base_version}%{?prerelease}}

# RHEL: Disabled due to missing dependencies
%bcond_with tests

# Only disabling the optional tests is a more complex but careful approach
# Pytest will skip the related tests, so we only conditionalize the BRs
# This bcond is ignored when tests are disabled
%bcond_without optional_tests

# To run the tests in %%check we use pytest-timeout
# When building pytest for the first time with new Python version
# that is not possible as it depends on pytest
# The bcond is ignored when tests are disabled
%bcond_without timeout

BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-rpm-macros
BuildRequires:  python%{python3_pkgversion}-setuptools

# Those are also runtime deps, needed for tests
# We keep them unconditionally, so we don't accidentally build pytest
# before them and get broken dependencies
BuildRequires:  python%{python3_pkgversion}-attrs >= 19.2
BuildRequires:  python%{python3_pkgversion}-packaging
BuildRequires:  python%{python3_pkgversion}-iniconfig
BuildRequires:  python%{python3_pkgversion}-pluggy >= 0.12

Requires:  python%{python3_pkgversion}dist(attrs) >= 19.2
Requires:  python%{python3_pkgversion}dist(packaging)
Requires:  python%{python3_pkgversion}dist(iniconfig)
Requires:  python%{python3_pkgversion}dist(pluggy) >= 0.12

%if %{with tests}
BuildRequires:  python%{python3_pkgversion}-hypothesis >= 3.56
BuildRequires:  python%{python3_pkgversion}-pygments >= 2.7.2
BuildRequires:  python%{python3_pkgversion}-xmlschema
%if %{with optional_tests}
BuildRequires:  python%{python3_pkgversion}-argcomplete
#BuildRequires:  python%{python3_pkgversion}-asynctest -- not packaged in Fedora
BuildRequires:  python%{python3_pkgversion}-decorator
BuildRequires:  python%{python3_pkgversion}-jinja2
BuildRequires:  python%{python3_pkgversion}-mock
BuildRequires:  python%{python3_pkgversion}-nose
BuildRequires:  python%{python3_pkgversion}-numpy
BuildRequires:  python%{python3_pkgversion}-pexpect
BuildRequires:  python%{python3_pkgversion}-pytest-xdist
BuildRequires:  python%{python3_pkgversion}-twisted
BuildRequires:  /usr/bin/lsof
%endif
%if %{with timeout}
BuildRequires:  python%{python3_pkgversion}-pytest-timeout
%endif
%endif

BuildRequires:  %{_bindir}/rst2html

BuildArch:      noarch

%description
The pytest framework makes it easy to write small tests, yet scales to support
complex functional testing for applications and libraries.

%prep
%autosetup -p1 -n %{pkgname}-%{base_version}%{?prerelease}


# remove setuptools_scm dependency since we don't have it in RHEL
sed -i '/setuptools-scm/d' setup.cfg

# since setuptools_scm is not available we need to sed out it's usage from setup.py and set the correct version
sed -i 's/setup()/setup(version="%{version}")/g' setup.py




%build
%py3_build

for f in README CHANGELOG CONTRIBUTING ; do
  rst2html ${f}.rst > ${f}.html
done

%install
%py3_install
mv %{buildroot}%{_bindir}/pytest %{buildroot}%{_bindir}/pytest-%{python3_version}
mv %{buildroot}%{_bindir}/py.test %{buildroot}%{_bindir}/py.test-%{python3_version}


# remove shebangs from all scripts
find %{buildroot}%{python3_sitelib} \
     -name '*.py' \
     -exec sed -i -e '1{/^#!/d}' {} \;

%if %{with tests}
%check
%global __pytest %{buildroot}%{_bindir}/pytest
# optional_tests deps contain pytest-xdist, so we can use it to run tests faster
%pytest testing %{?with_timeout:--timeout=30} %{?with_optional_tests:-n auto} -rs
%endif
export PYTHONPATH=%{buildroot}%{python3_sitelib}
test "$(%{python3} -c 'import pytest; print(pytest.__version__)')" == "%{version}"

%files -n python%{python3_pkgversion}-%{pkgname}
%doc CHANGELOG.html
%doc README.html
%doc CONTRIBUTING.html
%license LICENSE
%{_bindir}/pytest-%{python3_version}
%{_bindir}/py.test-%{python3_version}
%{python3_sitelib}/pytest-*.egg-info/
%{python3_sitelib}/_pytest/
%{python3_sitelib}/pytest/
%pycached %{python3_sitelib}/py.py

%changelog
* Wed Oct 19 2022 Charalampos Stratakis <cstratak@redhat.com> - 7.2.0-1
- Initial package
- Fedora contributions by:
      Charalampos Stratakis <cstratak@redhat.com>
      David Malcolm <dmalcolm@redhat.com>
      Dennis Gilmore <dennis@ausil.us>
      Gwyn Ciesla <limburgher@gmail.com>
      Igor Gnatenko <ignatenkobrain@fedoraproject.org>
      Lumir Balhar <lbalhar@redhat.com>
      Miro Hrončok <miro@hroncok.cz>
      Nils Philippsen <nils@redhat.com>
      Orion Poplawski <orion@cora.nwra.com>
      Peter Robinson <pbrobinson@gmail.com>
      Petr Viktorin <pviktori@redhat.com>
      Richard Shaw <hobbes1069@gmail.com>
      Robert Kuska <rkuska@redhat.com>
      Thomas Moschny <thm@fedoraproject.org>
