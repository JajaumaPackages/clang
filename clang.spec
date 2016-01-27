Name:		clang
Version:	3.7.1
Release:	1%{?dist}
Summary:	A C language family front-end for LLVM

License:	NCSA
URL:		http://llvm.org
Source0:	http://llvm.org/releases/%{version}/cfe-%{version}.src.tar.xz

Source100:	clang-config.h

Patch1:		patch-headers.patch
BuildRequires:	cmake
BuildRequires:	llvm-devel = %{version}
BuildRequires:	libxml2-devel

Requires:	%{name}-libs%{?_isa} = %{version}-%{release}

# clang requires gcc, clang++ requires libstdc++-devel
# - https://bugzilla.redhat.com/show_bug.cgi?id=1021645
# - https://bugzilla.redhat.com/show_bug.cgi?id=1158594
Requires:	libstdc++-devel
Requires:	gcc-c++


%description
clang: noun
    1. A loud, resonant, metallic sound.
    2. The strident call of a crane or goose.
    3. C-language family front-end toolkit.

The goal of the Clang project is to create a new C, C++, Objective C
and Objective C++ front-end for the LLVM compiler. Its tools are built
as libraries and designed to be loosely-coupled and extensible.

%package libs
Summary: Runtime library for clang

%description libs
Runtime library for clang.

%package devel
Summary: Development header files for clang.
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
Development header files for clang.

%package analyzer
Summary:	A source code analysis framework
License:	NCSA and MIT
BuildArch:	noarch
Requires:	%{name} = %{version}-%{release}
# not picked up automatically since files are currently not installed in
# standard Python hierarchies yet
Requires:	python

%description analyzer
The Clang Static Analyzer consists of both a source code analysis
framework and a standalone tool that finds bugs in C and Objective-C
programs. The standalone tool is invoked from the command-line, and is
intended to run in tandem with a build of a project or code base.

%prep
%setup -q -n cfe-%{version}.src
%patch1 -p1 -b .fix-header
%build
mkdir -p _build
cd _build
%cmake .. \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DLLVM_CONFIG:FILEPATH=/usr/bin/llvm-config-%{__isa_bits} \
	\
	-DCLANG_ENABLE_ARCMT:BOOL=ON \
	-DCLANG_ENABLE_STATIC_ANALYZER:BOOL=ON \
	-DCLANG_INCLUDE_DOCS:BOOL=ON \
	-DCLANG_INCLUDE_TESTS:BOOL=ON \
	-DCLANG_PLUGIN_SUPPORT:BOOL=ON \
	\
	-DCLANG_BUILD_EXAMPLES:BOOL=OFF

make %{?_smp_mflags}

%install
cd _build
make install DESTDIR=%{buildroot}

# multilib fix
mv -v %{buildroot}%{_includedir}/clang/Config/config{,-%{__isa_bits}}.h
install -m 0644 %{SOURCE100} %{buildroot}%{_includedir}/clang/Config/config.h

# remove git integration
rm -vf %{buildroot}%{_bindir}/git-clang-format
# remove editor integrations (bbedit, sublime, emacs, vim)
rm -vf %{buildroot}%{_datadir}/clang/clang-format-bbedit.applescript
rm -vf %{buildroot}%{_datadir}/clang/clang-format-sublime.py*
rm -vf %{buildroot}%{_datadir}/clang/clang-format.el
rm -vf %{buildroot}%{_datadir}/clang/clang-format.py*
# remove diff reformatter
rm -vf %{buildroot}%{_datadir}/clang/clang-format-diff.py*

# install static-analyzer
# http://clang-analyzer.llvm.org/installation#OtherPlatforms
mkdir -p %{buildroot}%{_libexecdir}/clang-analyzer/
cp -vpr ../tools/scan-view %{buildroot}%{_libexecdir}/clang-analyzer/
cp -vpr ../tools/scan-build %{buildroot}%{_libexecdir}/clang-analyzer/
# remove non-Linux scripts
rm -vf %{_buildroot}%{_libexecdir}/clang-analyzer/scan-build/*.bat
rm -vf %{_buildroot}%{_libexecdir}/clang-analyzer/scan-build/set-xcode-analyzer
# fix manual page location
mkdir -p %{buildroot}%{_mandir}/man1/
mv -v %{buildroot}%{_libexecdir}/clang-analyzer/scan-build/scan-build.1 %{buildroot}%{_mandir}/man1/
# launchers in /bin
for tool in scan-{build,view}; do
  ln -vs ../../%{_libexecdir}/clang-analyzer/$tool/$tool %{buildroot}%{_bindir}/$tool
done

%check
# requires lit.py from LLVM utilities
#cd _build
#make check-all

%files
%{_prefix}/lib/clang
%{_bindir}/clang*

%files libs
%{_libdir}/*.so.*

%files devel
%{_includedir}/clang/
%{_includedir}/clang-c/
%{_libdir}/*.so
%dir %{_datadir}/clang/
%{_datadir}/clang/cmake/

%files analyzer
%{_bindir}/scan-view
%{_bindir}/scan-build
%{_libexecdir}/clang-analyzer
%{_mandir}/man1/scan-build.1.*

%changelog
* Tue Oct 06 2015 Jan Vcelak <jvcelak@fedoraproject.org> 3.7.0-100
- initial version using cmake build system