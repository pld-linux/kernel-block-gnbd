#
# Condtional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	smp		# without smp packages
%bcond_with	verbose		# verbose build (V=1)
#
%define	snap	20050729
%define _rel	0.%{snap}.1
Name:		kernel-block-gnbd
Summary:	Block device driver to share storage to many machines over a network
Version:	0.1
Release:	%{_rel}@%{_kernel_ver_str}
Epoch:		0
License:	GPL v2
Group:		Base/Kernel
# taken from STABLE branch
Source0:	cluster-gnbd-%{snap}.tar.gz
# Source0-md5:	c9fa7c2b7b3fa3a4773f1f1fdf0e4f11
URL:		http://sources.redhat.com/cluster/gnbd/
BuildRequires:	perl-base
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.7}
%endif
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel}
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The global network block device (GNBD) driver is similar to other network block device drivers. Devices exported by GNBD servers can be used by multiple clients making it suitable for use by a group of GFS nodes.

%package -n kernel-smp-fs-gnbd
Summary:	kernel-smp-fs-gnbd
Summary(pl):	Block device driver to share storage to many machines over a network
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel-smp}

%description -n kernel-smp-fs-gnbd
The global network block device (GNBD) driver is similar to other network block device drivers. Devices exported by GNBD servers can be used by multiple clients making it suitable for use by a group of GFS nodes.

%prep
%setup -q -n cluster-gnbd-%{snap}

%build
./configure \
	--kernel_src=%{_kernelsrcdir}
cd src
ln -s . linux
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
    if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
	exit 1
    fi
    rm -rf include
    install -d include/{linux,config}
    ln -sf %{_kernelsrcdir}/config-$cfg .config
    ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
    ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
    %if %{without dist_kernel}
        [ ! -x %{_kernelsrcdir}/scripts/kallsyms ] || ln -sf %{_kernelsrcdir}/scripts
    %endif
    touch include/config/MARKER
    %{__make} -C %{_kernelsrcdir} clean \
	RCS_FIND_IGNORE="-name '*.ko' -o" \
	M=$PWD O=$PWD \
	%{?with_verbose:V=1}
    %{__make} -C %{_kernelsrcdir} modules \
	RCS_FIND_IGNORE="-name '*.ko' -o" \
	CC="%{__cc}" CPP="%{__cpp}" \
	M=$PWD O=$PWD \
	%{?with_verbose:V=1}

	mv gnbd.ko gnbd-$cfg.ko
done
cd -

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/drivers/block/gnbd
install src/gnbd-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/block/gnbd/gnbd.ko
%if %{with smp} && %{with dist_kernel}
install src/gnbd-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/drivers/block/gnbd/gnbd.ko
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%depmod %{_kernel_ver}

%postun
%depmod %{_kernel_ver}

%post -n kernel-smp-fs-gnbd
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-fs-gnbd
%depmod %{_kernel_ver}smp

%files
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/block/gnbd

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-fs-gnbd
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/drivers/block/gnbd
%endif
