#
# Condtional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	smp		# without smp packages
%bcond_with	verbose		# verbose build (V=1)
#
%define _rel	0.3
Summary:	Block device driver to share storage to many machines over a network
Summary(pl.UTF-8):   Sterownik urządzenia blokowego do współdzielenia przestrzeni między wieloma maszynami w sieci
Name:		kernel%{_alt_kernel}-block-gnbd
Version:	1.03.00
Release:	%{_rel}@%{_kernel_ver_str}
Epoch:		0
License:	GPL v2
Group:		Base/Kernel
Source0:	ftp://sources.redhat.com/pub/cluster/releases/cluster-%{version}.tar.gz
# Source0-md5:	8eea23df70d2007c4fb8c234cfea49cf
URL:		http://sources.redhat.com/cluster/gnbd/
BuildRequires:	perl-base
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.308
%endif
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel%{_alt_kernel}}
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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

%package -n kernel%{_alt_kernel}-smp-block-gnbd
Summary:	Block device SMP driver to share storage to many machines over a network
Summary(pl.UTF-8):   Sterownik SMP urządzenia blokowego do współdzielenia przestrzeni między wieloma maszynami w sieci
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel%{_alt_kernel}-smp}

%description -n kernel%{_alt_kernel}-smp-block-gnbd
The global network block device (GNBD) driver is similar to other
network block device drivers. Devices exported by GNBD servers can be
used by multiple clients making it suitable for use by a group of GFS
nodes.

%description -n kernel%{_alt_kernel}-smp-block-gnbd -l pl.UTF-8
Sterownik globalnego sieciowego urządzenia blokowego (GNBD - global
network block device) jest podobny do innych sterowników urządzeń
blokowych. Urządzenia eksportowane przez serwery GNBD mogą być używane
przez wielu klientów, co czyni je odpowiednimi do używania przez grupy
węzłów GFS.

%prep
%setup -q -n cluster-%{version}

%build
cd gnbd-kernel
./configure \
	--kernel_src=%{_kernelsrcdir}
cd src
ln -s . linux
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf o
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
%if %{with dist_kernel}
	%{__make} -j1 -C %{_kernelsrcdir} O=$PWD/o prepare scripts
%else
	install -d o/include/config
	touch o/include/config/MARKER
	ln -sf %{_kernelsrcdir}/scripts o/scripts
%endif
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		USING_KBUILD=yes \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		USING_KBUILD=yes \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}

	mv gnbd.ko gnbd-$cfg.ko
done
cd -

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/drivers/block/gnbd
install gnbd-kernel/src/gnbd-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/block/gnbd/gnbd.ko
%if %{with smp} && %{with dist_kernel}
install gnbd-kernel/src/gnbd-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/drivers/block/gnbd/gnbd.ko
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%depmod %{_kernel_ver}

%postun
%depmod %{_kernel_ver}

%post -n kernel%{_alt_kernel}-smp-block-gnbd
%depmod %{_kernel_ver}smp

%postun -n kernel%{_alt_kernel}-smp-block-gnbd
%depmod %{_kernel_ver}smp

%files
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/block/gnbd

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-block-gnbd
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/drivers/block/gnbd
%endif
