#
# Condtional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_with	verbose		# verbose build (V=1)
#
%define _rel	0.3
Summary:	Block device driver to share storage to many machines over a network
Summary(pl.UTF-8):	Sterownik urządzenia blokowego do współdzielenia przestrzeni między wieloma maszynami w sieci
Name:		kernel%{_alt_kernel}-block-gnbd
Version:	2.00.00
Release:	%{_rel}@%{_kernel_ver_str}
Epoch:		0
License:	GPL v2
Group:		Base/Kernel
Source0:	ftp://sources.redhat.com/pub/cluster/releases/cluster-%{version}.tar.gz
# Source0-md5:	2ef3f4ba9d3c87b50adfc9b406171085
URL:		http://sources.redhat.com/cluster/gnbd/
BuildRequires:	perl-base
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
%{?with_dist_kernel:%requires_releq_kernel}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel%{_alt_kernel}}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The global network block device (GNBD) driver is similar to other
network block device drivers. Devices exported by GNBD servers can be
used by multiple clients making it suitable for use by a group of GFS
nodes.

%description -l pl.UTF-8
Sterownik globalnego sieciowego urządzenia blokowego (GNBD - global
network block device) jest podobny do innych sterowników urządzeń
blokowych. Urządzenia eksportowane przez serwery GNBD mogą być używane
przez wielu klientów, co czyni je odpowiednimi do używania przez grupy
węzłów GFS.

%prep
%setup -q -n cluster-%{version}

cat > gnbd-kernel/src/Makefile << EOF
obj-m += gnbd.o
lock_gnbd-objs := gnbd.c
%{?debug:CFLAGS += -DCONFIG_MODULE_NAME_DEBUG=1}
EOF

%build
cd gnbd-kernel
./configure \
	--kernel_src=%{_kernelsrcdir}
%build_kernel_modules -C src -m gnbd

%install
rm -rf $RPM_BUILD_ROOT
cd gnbd-kernel/src
%install_kernel_modules -m gnbd -d block

%clean
rm -rf $RPM_BUILD_ROOT

%post
%depmod %{_kernel_ver}

%postun
%depmod %{_kernel_ver}

%files
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/block/gnbd.ko.*
