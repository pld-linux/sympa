%include	/usr/lib/rpm/macros.perl
Summary:	Sympa is a powerful multilingual List Manager - LDAP and SQL features
Summary(fr):	Sympa est un gestionnaire de listes électroniques
Summary(pl):	Sympa jest u¿ytecznym wielojêzycznym zarz±dc± list - obs³uguje LDAP i SQL
Name:		sympa
Version:	3.3.5
Release:	0.2
License:	GPL
Group:		Applications/Mail
Source0:	http://listes.cru.fr/sympa/distribution/%{name}-%{version}.tar.gz
Source1:	%{name}-pl-3.3.5-020515.tar.bz2
Source2:	%{name}.init
Source3:	%{name}.sysconfig
URL:		http://listes.cru.fr/sympa/
Patch0:		%{name}-Makefile.patch
Patch1:		sympa-wwslib-pl.patch
Requires:	perl 		   >= 5.6.0
Requires:	perl-MailTools     >= 1.14
Requires:	perl-MIME-Base64   >= 1.0
Requires:	perl-IO-stringy    >= 1.0
Requires:	perl-Locale-Msgcat >= 1.03
Requires:	perl-MIME-tools    >= 5.209
Requires:	perl-CGI-modules   >= 2.52
Requires:	perl-DBI	   >= 1.06
Requires:	perl-ldap          >= 0.10
## Also requires a DBD for the DBMS
## (perl-DBD-Pg or Perl- Msql-Mysql-modules)
Requires:	perl-FCGI          >= 0.48
Requires:	MHonArc 	   >= 2.4.5
Requires:	perl-Digest-MD5
Requires:	apache
Requires:	openssl 	   >= 0.9.5a
Requires(pre):	/usr/bin/getgid
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/useradd
Requires(pre):	/usr/sbin/groupadd
Requires(post,preun):	/sbin/chkconfig
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
Sympa jest skalowalnym i wysoko konfigurowalnym zarz±dc± pocztowych
list dyskusyjnych. Radzi sobie z du¿ymi listami (100 000
subskrybentów) i przychodzi z pe³nym (u¿ytkownika i administratora)
interfejsem WWW. Jest zlokalizowany, obs³uguje jêzyki us, fr, de, es,
it, fi, zh. Jêzyk skryptowy pozwala na rozszerzanie komend. Sympa mo¿e
obs³ugiwaæ katalog LDAP lub relacyjne bazy danych do tworzenia
dynamicznych list. Obs³uguje autentykacjê i szyfrowanie oprarte o
S/MIME.

%prep
%setup -q -a1
%patch0 -p1
%patch1 -p1

%build

aclocal
%{__autoconf}
%{__automake}
%configure
%{__make} DIR=%{home_s} CONFIG=%{_sysconfdir}/sympa/sympa.conf sources languages

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/sysconfig

%{__make} \
	INITDIR=/etc/rc.d/init.d \
	HOST=MYHOST \
	DIR=%{home_s} \
	MANDIR=%{_mandir} \
	ICONSDIR=/home/httpd/icons/sympa \
	LIBDIR=%{home_s}/lib \
	BINDIR=%{home_s}/bin \
	CGIDIR=%{home_s}/sbin \
	MAILERPROGDIR=%{home_s}/bin \
	SBINDIR=%{home_s}/sbin \
	EXPL_DIR=%{home_s}/expl \
	ETCBINDIR=%{home_s}/bin/etc \
	CONFDIR=%{_sysconfdir}/sympa \
	DESTDIR=$RPM_BUILD_ROOT install

install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/sympa
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/sympa

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
	/usr/sbin/useradd -u 71 -r -d /home/sympa -s /bin/false -c "sympa" -g sympa sympa 1>&2
fi

# Setup log facility for Sympa
if [ -f /etc/syslog.conf ] ;then
  if [ `grep -c sympa /etc/syslog.conf` -eq 0 ] ;then
    typeset -i cntlog
    cntlog=0
    while [ `grep -c local${cntlog} /etc/syslog.conf` -gt 0 ];do cntlog=${cntlog}+1;done
    if [ ${cntlog} -le 9 ];then
      echo "# added by sympa-3.0 rpm $(date)" >> /etc/syslog.conf
      echo "local${cntlog}.*       /var/log/sympa" >> /etc/syslog.conf
    fi
  fi
fi

# try to add some sample entries in /etc/aliases for sympa
for a_file in /etc/aliases /etc/postfix/aliases; do
  if [ -f ${a_file} ]; then
    if [ `grep -c sympa ${a_file}` -eq 0 ]; then
      cp -f ${a_file} ${a_file}.rpmorig
      echo >> ${a_file}
      echo "# added by sympa-3.0 rpm "$(date) >> ${a_file}
      if [ `grep -c listmaster ${a_file}` -eq 0 ]; then
        echo "# listmaster:root" >> ${a_file}
      fi
      echo "# sympa:\"|/home/sympa/bin/queue 0 sympa\"" >> ${a_file}
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
    ln -s %{home_s}/bin/queue /etc/smrsh/queue
  fi
fi

%post
/sbin/chkconfig --add sympa
perl -pi -e "s|MYHOST|${HOSTNAME}|g" /etc/sympa/sympa.conf /etc/sympa/wwsympa.conf

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
%defattr(0755,sympa,sympa)
%doc [ACKNR]*

%dir %{home_s}
%dir %{home_s}/bin
%dir %{home_s}/lib/Marc
%dir %{home_s}/bin/etc
%dir %{home_s}/sample
%dir %{home_s}/expl
%dir %{home_s}/spool
%dir %{home_s}/nls
%dir %{home_s}/etc

%defattr(0744,sympa,sympa)
%dir %{home_s}/spool/*

# needs fixing - don't use defattr(-)!
%defattr(-,sympa,sympa)
%{home_s}/sample/*
%{home_s}/lib/Marc/*
%{home_s}/bin/etc/*
%{home_s}/expl/*

%attr(0755,root,root)%dir /home/httpd/icons/sympa
%attr(0644,root,root) /home/httpd/icons/sympa/*

%defattr(-,sympa,sympa)
%{home_s}/bin/*.pl
%{home_s}/lib/*.pm
%{home_s}/lib/*.pl
%{home_s}/bin/create_db.*
%{home_s}/sbin/*.pl
%{home_s}/sbin/wwsympa.fcgi

%attr(4755,sympa,sympa) %{home_s}/bin/queue
%attr(4755,sympa,sympa) %{home_s}/bin/bouncequeue
%attr(4755,sympa,sympa) %{home_s}/bin/*wrapper

%{home_s}/nls/*.cat

%attr(640,root,sympa) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/sympa/*.conf
%attr(640,root,root)  %config(noreplace) %verify(not mtime md5 size) /etc/sysconfig/sympa
%attr(754,root,root)  /etc/rc.d/init.d/sympa
%{_mandir}/man[58]/*

%clean
rm -rf $RPM_BUILD_ROOT
