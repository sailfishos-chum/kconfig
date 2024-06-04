%global kf5_version 5.108.0
%global framework kconfig

Name:    opt-kf5-kconfig
Version: 5.108.0
Release: 1%{?dist}
Summary: KDE Frameworks 5 Tier 1 addon with advanced configuration system

License: GPLv2+ and LGPLv2+ and MIT
URL:     https://invent.kde.org/frameworks/%{framework}

Source0: %{name}-%{version}.tar.bz2

## upstream patches

## upstreamable patches

%{?opt_kf5_default_filter}

%if 0%{?ninja}
BuildRequires:  ninja-build
%endif

BuildRequires:  opt-extra-cmake-modules >= %{kf5_version}
BuildRequires:  opt-kf5-rpm-macros >= %{kf5_version}

BuildRequires:  opt-qt5-qtbase-devel
BuildRequires:  opt-qt5-qtdeclarative-devel
BuildRequires:  opt-qt5-linguist

%if 0%{?python_bindings}
BuildRequires:  clang
BuildRequires:  clang-devel
BuildRequires:  python3-clang
BuildRequires:  python3-PyQt5-devel
%endif

Requires:       %{name}-core%{?_isa} = %{version}-%{release}
Requires:       %{name}-gui%{?_isa} = %{version}-%{release}

%description
KDE Frameworks 5 Tier 1 addon with advanced configuration system made of two
parts: KConfigCore and KConfigGui.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       opt-qt5-qtbase-devel
%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package        core
Summary:        Non-GUI part of KConfig framework
%{?opt_kf5_default_filter}
%{?_opt_qt5:Requires: %{_opt_qt5}%{?_isa} = %{_opt_qt5_version}}
%description    core
KConfigCore provides access to the configuration files themselves. It features
centralized definition and lock-down (kiosk) support.

%package        gui
Summary:        GUI part of KConfig framework
%{?opt_kf5_default_filter}
Requires:       %{name}-core%{?_isa} = %{version}-%{release}
Requires:       opt-qt5-qtdeclarative%{?_isa}
%description    gui
KConfigGui provides a way to hook widgets to the configuration so that they are
automatically initialized from the configuration and automatically propagate
their changes to their respective configuration files.

%if 0%{?docs}
%package doc
Summary: API documentation for %{name}
BuildRequires: doxygen
BuildRequires: opt-qt5-qdoc
BuildRequires: opt-qt5-qhelpgenerator
BuildRequires: opt-qt5-qtbase-doc
BuildRequires: make
BuildArch: noarch
%description doc
%{summary}.
%endif

%if 0%{?python_bindings}
%package -n python3-pykf5-%{framework}
Summary: Python3 bindings for %{framework}
Requires: %{name} = %{version}-%{release}
%description -n python3-pykf5-%{framework}
%{summary}.

%package -n pykf5-%{framework}-devel
Summary: SIP files for %{framework} Python bindings
BuildArch: noarch
%description -n pykf5-%{framework}-devel
%{summary}.
%endif


%prep
%autosetup -n %{name}-%{version}/upstream -p1


%build

export QTDIR=%{_opt_qt5_prefix}
touch .git

%if 0%{?python_bindings:1}
PYTHONPATH=%{_datadir}/ECM/python
export PYTHONPATH
%endif

%_opt_cmake_kf5 \
  %if 0%{?flatpak}
  %{?docs:-DBUILD_QCH:BOOL=OFF} \
  %else
  %{?docs:-DBUILD_QCH:BOOL=ON} \
  %endif
  %{?ninja:-G Ninja} \
  %{?tests:-DBUILD_TESTING:BOOL=ON}

%cmake_build

%install
%cmake_install

%find_lang_kf5 kconfig5_qt


%check
%if 0%{?tests}
export CTEST_OUTPUT_ON_FAILURE=1
## cant use %%ninja_test here for some reason, doesn't inherit env vars from xvfb or dbus -- rex
xvfb-run -a \
%if 0%{?ninja}
ninja test %{?_smp_mflags} -v -C redhat-linux-build ||:
%else
make test %{?_smp_mflags} -C redhat-linux-build ARGS="--output-on-failure --timeout 300" ||:
%endif
%endif


%files
%doc DESIGN README.md TODO
%license LICENSES/*.txt
%{_opt_kf5_datadir}/locale/

%post core -p /sbin/ldconfig
%postun core -p /sbin/ldconfig

%files core
%{_opt_kf5_datadir}/qlogging-categories5/%{framework}*
%{_opt_kf5_bindir}/kreadconfig5
%{_opt_kf5_bindir}/kwriteconfig5
%{_opt_kf5_libdir}/libKF5ConfigCore.so.5*
%{_opt_kf5_libdir}/libKF5ConfigQml.so.5*
%{_opt_kf5_libexecdir}/kf5/kconfig_compiler_kf5
%{_opt_kf5_libexecdir}/kf5/kconf_update

%post gui -p /sbin/ldconfig
%postun gui -p /sbin/ldconfig

%files gui
%{_opt_kf5_libdir}/libKF5ConfigGui.so.*

%files devel
%{_opt_kf5_includedir}/KF5/KConfig/
%{_opt_kf5_includedir}/KF5/KConfigCore/
%{_opt_kf5_includedir}/KF5/KConfigGui/
%{_opt_kf5_includedir}/KF5/KConfigQml/
%{_opt_kf5_libdir}/libKF5ConfigCore.so
%{_opt_kf5_libdir}/libKF5ConfigGui.so
%{_opt_kf5_libdir}/libKF5ConfigQml.so
%{_opt_kf5_libdir}/cmake/KF5Config/
%{_opt_kf5_archdatadir}/mkspecs/modules/qt_KConfigCore.pri
%{_opt_kf5_archdatadir}/mkspecs/modules/qt_KConfigGui.pri

%if 0%{?docs}
%files doc
%{_opt_qt5_docdir}/KF5Config.qch
%{_opt_qt5_docdir}/KF5Config.tags
%endif

%if 0%{?python_bindings}
%files -n python3-pykf5-%{framework}
%{python3_sitearch}/PyKF5/

%files -n pykf5-%{framework}-devel
%{_datadir}/sip/PyKF5/
%endif
