%include	/usr/lib/rpm/macros.perl
Summary:	Sympa is a powerful multilingual List Manager - LDAP and SQL features
Summary(fr):	Sympa est un gestionnaire de listes �lectroniques
Summary(pl):	Sympa jest u�ytecznym wieloj�zycznym zarz�dc� list - obs�uguje LDAP i SQL
Name:		sympa
Version:	3.3.5
Release:	1
License:	GPL
Group:		Applications/Mail
Source0:	http://listes.cru.fr/sympa/distribution/%{name}-%{version}.tar.gz
Source1:	%{name}-pl-3.3.5-020515.tar.bz2
Source2:	%{name}.init
Source3:	%{name}.sysconfig
Source4:	%{name}.conf
Source5:	%{name}-www.conf
Patch0:		%{name}-Makefile.patch
Patch1:		%{name}-wwslib-pl.patch
Patch2:		%{name}-compare.patch
URL:		http://listes.cru.fr/sympa/
BuildRequires:	autoconf
BuildRequires:	automake
PreReq:		rc-scripts
Requires(pre):	/usr/bin/getgid
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/useradd
Requires(pre):	/usr/sbin/groupadd
Requires(post,preun):	/sbin/chkconfig
Requires(post):	fileutils
Requires(post):	grep
Requires:	MHonArc 	   >= 2.4.5
Requires:	apache
Requires:	perl 		   >= 5.6.0
Requires:	perl-MailTools     >= 1.14
Requires:	perl-MIME-Base64   >= 1.0
Requires:	perl-IO-stringy    >= 1.0
Requires:	perl-Locale-Msgcat >= 1.03
Requires:	perl-MIME-tools    >= 5.209
Requires:	perl-CGI-modules   >= 2.52
Requires:	perl-DBI	   >= 1.06
Requires:	perl-ldap          >= 0.10
Requires:	perl-DB_File	   >= 1.805
Requires:	perl-CGI	   >= 2.85
## Also requires a DBD for the DBMS
## (perl-DBD-Pg or Perl- Msql-Mysql-modules)
Requires:	perl-FCGI          >= 0.48
Requires:	perl-Digest-MD5
Requires:	openssl 	   >= 0.9.7
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define home_s  /var/lib/sympa

%description
Sympa is scalable and highly customizable mailing list manager. It can
cope with big lists (100,000 subscribers) and comes with a complete
(user and admin) Web interface. It is internationalized, and supports
the us, fr, de, es, it, fi, and chinese locales. A scripting language
allows you to extend the behavior of commands. Sympa can be linked to
an LDAP directory or an RDBMS to create dynamic mailing lists. Sympa
provides S/MIME-based authentication and encryption.

Documentation is available under HTML and Latex (source) formats.

%description -l pl
Sympa jest skalowalnym i wysoko konfigurowalnym zarz�dc� pocztowych
list dyskusyjnych. Radzi sobie z du�ymi listami (100 000
subskrybent�w) i przychodzi z pe�nym (u�ytkownika i administratora)
interfejsem WWW. Jest zlokalizowany, obs�uguje j�zyki us, fr, de, es,
it, fi, zh. J�zyk skryptowy pozwala na rozszerzanie komend. Sympa mo�e
obs�ugiwa� katalog LDAP lub relacyjne bazy danych do tworzenia
dynamicznych list. Obs�uguje autentykacj� i szyfrowanie oprarte o
S/MIME.

%prep
%setup -q -a1
%patch0 -p1
%patch1 -p1
%patch2 

%build
rm -f missing
%{__aclocal}
%{__autoconf}
%{__automake}
%configure
%{__make} DIR=%{home_s} CONFIG=%{_sysconfdir}/sympa/sympa.conf sources languages

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/sysconfig

%{__make} install \
	INITDIR=/etc/rc.d/init.d \
	HOST=MYHOST \
	DIR=%{home_s} \
	MANDIR=%{_mandir} \
	ICONSDIR=/home/services/httpd/icons/sympa \
	LIBDIR=%{home_s}/lib \
	BINDIR=%{home_s}/bin \
	CGIDIR=%{home_s}/sbin \
	MAILERPROGDIR=%{home_s}/bin \
	SBINDIR=%{home_s}/sbin \
	EXPL_DIR=%{home_s}/expl \
	ETCBINDIR=%{home_s}/etc \
	CONFDIR=%{_sysconfdir}/sympa \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/sympa
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/sympa
install %{SOURCE4} $RPM_BUILD_ROOT/%{_sysconfdir}/sympa/sympa.conf
install %{SOURCE5} $RPM_BUILD_ROOT/%{_sysconfdir}/sympa/wwsympa.conf

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`getgid sympa`" ]; then
	if [ "`getgid sympa`" != "71" ]; then
		echo "Error: group sympa doesn't have gid=71. Correct this before installing sympa." 1>&2
		exit 1
	fi
else
	/usr/sbin/groupadd -g 71 -r -f sympa
fi
if [ -n "`id -u sympa 2>/dev/null`" ]; then
	if [ "`id -u sympa`" != "71" ]; then
		echo "Error: user sympa doesn't have uid=71. Correct this before installing sympa." 1>&2
		exit 1
	fi
else
	/usr/sbin/useradd -u 71 -r -d /home/services/sympa -s /bin/false -c "sympa" -g sympa sympa 1>&2
fi

%post
/sbin/chkconfig --add sympa
perl -pi -e "s|MYHOST|${HOSTNAME}|g" /etc/sympa/sympa.conf /etc/sympa/wwsympa.conf

# Setup log facility for Sympa
if [ -f /etc/syslog.conf ] ;then
	if [ `grep -c sympa /etc/syslog.conf` -eq 0 ] ;then
		typeset -i cntlog
		cntlog=0
		while [ `grep -c local${cntlog} /etc/syslog.conf` -gt 0 ]; do
			cntlog=${cntlog}+1
		done
		if [ ${cntlog} -le 9 ];then
			echo "# added by sympa-3.0 rpm $(date)" >> /etc/syslog.conf
			echo "local${cntlog}.*       /var/log/sympa" >> /etc/syslog.conf
		fi
	fi
fi

# try to add some sample entries in /etc/aliases for sympa
for a_file in /etc/aliases /etc/postfix/aliases /etc/mail/sympa.aliases; do
	if [ -f ${a_file} ]; then
		if [ `grep -c sympa ${a_file}` -eq 0 ]; then
			cp -f ${a_file} ${a_file}.rpmorig
			echo >> ${a_file}
			echo "# added by sympa-3.0 rpm "$(date) >> ${a_file}
			if [ `grep -c listmaster ${a_file}` -eq 0 ]; then
				echo "# listmaster:root" >> ${a_file}
			fi
			echo "# sympa:\"|/home/services/sympa/bin/queue 0 sympa\"" >> ${a_file}
			echo "# sympa-request:listmaster@${HOSTNAME}" >> ${a_file}
			echo "# sympa-owner:listmaster@${HOSTNAME}" >> ${a_file}
			echo "" >> ${a_file}
#     /usr/bin/newaliases
		fi
	fi
done

# eventually, add queue to sendmail security shell
if [ -d /etc/smrsh ]; then
	if [ ! -e /etc/smrsh/queue ]; then
		ln -sf %{home_s}/bin/queue /etc/smrsh/queue
	fi
fi

%preun
if [ "$1" = "0" ]; then
	/sbin/chkconfig --del sympa
fi

%postun
if [ ! -d %{home_s} ]; then
	/usr/sbin/userdel sympa
	/usr/sbin/groupdel sympa
fi
if [ "$1" = "0" -a -d /etc/smrsh ]; then
	if [ -L /etc/smrsh/queue ]; then
		rm -f /etc/smrsh/queue
	fi
fi

%files
%attr(644,root,root,755)
%doc [ACKNR]*

# needs fixing - don't use attr(-)!
%attr(755,sympa,sympa) %dir %{home_s}
%attr(755,sympa,sympa) %dir %{home_s}/bin
%attr(  -,sympa,sympa) %{home_s}/bin/*.pl
%attr(  -,sympa,sympa) %{home_s}/bin/create_db.*
%attr(4755,sympa,sympa) %{home_s}/bin/queue
%attr(4755,sympa,sympa) %{home_s}/bin/bouncequeue
%attr(4755,sympa,sympa) %{home_s}/bin/*wrapper

%attr(755,sympa,sympa) %dir %{home_s}/etc
%attr(  -,sympa,sympa) %{home_s}/etc/*
%attr(755,sympa,sympa) %dir %{home_s}/expl
%attr(  -,sympa,sympa) %{home_s}/expl/*

%attr(755,sympa,sympa) %dir %{home_s}/lib
%attr(755,sympa,sympa) %dir %{home_s}/lib/Marc
%attr(  -,sympa,sympa) %{home_s}/lib/Marc/*
%attr(  -,sympa,sympa) %{home_s}/lib/*.pm
%attr(  -,sympa,sympa) %{home_s}/lib/*.pl

%attr(755,sympa,sympa) %dir %{home_s}/nls
%attr(  -,sympa,sympa) %{home_s}/nls/*.cat
%attr(755,sympa,sympa) %dir %{home_s}/sample
%attr(  -,sympa,sympa) %{home_s}/sample/*

%attr(755,sympa,sympa) %dir %{home_s}/sbin
%attr(  -,sympa,sympa) %{home_s}/sbin/*.pl
%attr(  -,sympa,sympa) %{home_s}/sbin/wwsympa.fcgi

%attr(755,sympa,sympa) %dir %{home_s}/spool
%attr(744,sympa,sympa) %dir %{home_s}/spool/*

%dir /home/services/httpd/icons/sympa
/home/services/httpd/icons/sympa/*

%dir %{_sysconfdir}/sympa
%attr(640,sympa,sympa) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/sympa/*.conf
%attr(640,sympa,root)  %config(noreplace) %verify(not mtime md5 size) /etc/sysconfig/sympa
%attr(754,root,root)  /etc/rc.d/init.d/sympa
%{_mandir}/man[58]/*
