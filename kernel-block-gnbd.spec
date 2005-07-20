
%bcond_without  dist_kernel     # allow non-distribution kernel
%bcond_without  kernel          # don't build kernel modules
%bcond_without  smp             # don't build SMP module
%bcond_without  userspace       # don't build userspace module
%bcond_with     verbose         # verbose build (V=1)


%define		_rel	1
%define		_org_name	gnbd-kernel

Summary:	GNBD
Summary(pl):	GNBD
Name:		kernel-block-gnbd
Version:	20050719
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL
Group:		Base/Kernel
Source0:	%{_org_name}-%{version}.tar.bz2
# Source0-md5:	650046835bf5dcd47db766847b7bf35d
BuildRequires:	rpmbuild(macros) >= 1.118
%{?with_dist_kernel:BuildRequires:	kernel-module-build}
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	modutils
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description

%description -l pl

%package -n kernel-smp-block-gnbd
Summary:	GNBD
Summary(pl):	GNBD
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	modutils

%description -n kernel-smp-block-gnbd

%description -n kernel-smp-block-gnbd -l pl

%prep
%setup -q -n %{_org_name}

%build
cd src
%if %{with kernel}
#cp Makefile.kernel Makefile
# kernel module(s)
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
	touch include/config/MARKER

	cp gnbd.h include/linux/
#
#       patching/creating makefile(s) (optional)
#
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		-I./ \
		%{?with_verbose:V=1}
	
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		M=$PWD O=$PWD \
		-I./ \
		%{?with_verbose:V=1}

        mv gnbd{,-$cfg}.ko
done
%endif
																									

%install
%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/drivers/block/gnbd
cd src
install gnbd-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/block/gnbd/gnbd.ko
%if %{with smp} && %{with dist_kernel}
install gnbd-smp.ko \
$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/drivers/block/gnbd/gnbd.ko
%endif
%endif
		
%clean
rm -rf $RPM_BUILD_ROOT

%post
%depmod %{_kernel_ver}

%postun
%depmod %{_kernel_ver}

%post	-n kernel-smp-block-gnbd
%depmod %{_kernel_ver}

%postun	-n kernel-smp-block-gnbd
%depmod %{_kernel_ver}

%files
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/block/gnbd/*

%files -n kernel-smp-block-gnbd
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/drivers/block/gnbd/*
