# TODO:
# - SECURITY: http://securitytracker.com/alerts/2004/Aug/1011016.html
# - COMPATIBILITY: check if works with webserver != apache and update R:
# - resolve problem with apache1 or apache2 icons directory...
# - no globs for suid/sgid files
# - rc-scripts service not restarted (should explain why not)
%include	/usr/lib/rpm/macros.perl
Summary:	Sympa - a powerful multilingual List Manager with LDAP and SQL features
Summary(fr):	Sympa est un gestionnaire de listes électroniques
Summary(pl):	Sympa - u¿yteczny, wielojêzyczny zarz±dca list z obs³ug± LDAP i SQL
Name:		sympa
Version:	3.4.4.3
Release:	3
License:	GPL
Group:		Applications/Mail
Source0:	http://www.sympa.org/distribution/%{name}-%{version}.tar.gz
# Source0-md5:	60105b5041c61696815fc7ce4cb6f728
Source1:	%{name}-pl-3.3.5-020515.tar.bz2
# Source1-md5:	2a46fe55e877cc0a471507f8c93fbeab
Source2:	%{name}.init
Source3:	%{name}.sysconfig
Source4:	%{name}.conf
Source5:	%{name}-www.conf
Patch0:		%{name}-Makefile.patch
Patch1:		%{name}-wwslib-pl.patch
Patch2:		%{name}-wwsympa.fcgi-editsubsciber.fix.patch
URL:		http://www.sympa.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	rpm-perlprov
BuildRequires:	rpmbuild(macros) >= 1.202
Requires(post):	fileutils
Requires(post):	grep
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(pre):	/usr/sbin/usermod
Requires:	MHonArc >= 2.4.5
Requires:	perl-CGI >= 2.85
Requires:	perl-CGI-modules >= 2.52
Requires:	perl-DBI >= 1.06
Requires:	perl-DB_File >= 1.805
Requires:	perl-IO-stringy >= 1.0
Requires:	perl-Locale-Msgcat >= 1.03
Requires:	perl-MIME-Base64 >= 1.0
Requires:	perl-MIME-tools >= 5.209
Requires:	perl-MailTools >= 1.14
Requires:	perl-ldap >= 0.10
Requires:	rc-scripts
Requires:	webserver = apache
## Also requires a DBD for the DBMS
## (perl-DBD-Pg or Perl- Msql-Mysql-modules)
Requires:	openssl >= 0.9.7
Requires:	perl-Digest-MD5
Requires:	perl-FCGI >= 0.48
Provides:	group(sympa)
Provides:	user(sympa)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		home_s	/var/lib/sympa

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
dynamicznych list. Obs³uguje uwierzytelnianie i szyfrowanie oparte o
S/MIME.

%prep
%setup -q -a1
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--with-confdir=%{_sysconfdir}/sympa \
	--with-cgidir=%{home_s}/sbin \
	--with-iconsdir=/home/services/httpd/icons/sympa \
	--with-bindir=%{home_s}/bin \
	--with-sbindir=%{home_s}/sbin \
	--with-libexecdir=%{home_s}/bin \
	--with-libdir=%{home_s}/lib \
	--with-datadir=%{home_s}/etc \
	--with-expldir=%{home_s}/expl \
	--with-initdir=/etc/rc.d/init.d \
	--with-piddir=/var/run \
	--with-spooldir=/var/lib/sympa/spool \
	--with-perl=%{__perl} \
	--with-mhonarc=%{_bindir}/mhonarc \
	--with-user=sympa \
	--with-group=sympa \
	--with-sendmail_aliases=/etc/mail/sympa_aliases \
	--with-virtual_aliases=/etc/mail/sympa_virtual \
	--with-newaliases=%{_bindir}/newaliases \
	--with-postmap=%{_bindir}/postmap \
	--with-mandir=%{_mandir} \
	--with-nlsdir=/var/lib/sympa/nls \
	--with-scriptdir=%{home_s}/bin \
	--with-sampledir=/var/lib/sympa/sample \
	--with-etcdir=%{_sysconfdir}/sympa

%{__make} sources nls \
	DIR=%{home_s} \
	CONFIG=%{_sysconfdir}/sympa/sympa.conf \
	CVS2CL=%{_bindir}/cvs2cl.pl

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/sysconfig

perl -pi -e 's#chown.*root#chown \$(USER)#g' src/Makefile

%{__make} install \
	USER=$(id -u) \
	GROUP=$(id -g) \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/sympa
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/sympa
install %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/sympa/sympa.conf
install %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/sympa/wwsympa.conf

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 71 sympa
%useradd -u 71 -d %{home_s} -s /bin/false -c "sympa" -g sympa sympa

%triggerun -- %{name} <= 3.4.4.3-1
if [ `eval echo ~sympa` = /home/services/sympa ]; then
	/usr/sbin/usermod -d %{home_s} sympa ||:
fi

%post
/sbin/chkconfig --add sympa
%{__perl} -pi -e "s|MYHOST|${HOSTNAME}|g" /etc/sympa/sympa.conf /etc/sympa/wwsympa.conf

# Setup log facility for Sympa
if [ -f /etc/syslog.conf ]; then
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
			echo "# sympa:\"|%{home_s}/bin/queue 0 sympa\"" >> ${a_file}
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
if [ "$1" = "0" ]; then
	%userremove sympa
	%groupremove sympa
fi
if [ "$1" = "0" -a -d /etc/smrsh ]; then
	if [ -L /etc/smrsh/queue ]; then
		rm -f /etc/smrsh/queue
	fi
fi

%files
%defattr(644,root,root,755)
%doc [ACKNR]* doc/html

# needs fixing - don't use attr(-)!
%attr(755,sympa,sympa) %dir %{home_s}
%attr(755,sympa,sympa) %dir %{home_s}/bin
%attr(-,sympa,sympa) %{home_s}/bin/*.pl
%attr(-,sympa,sympa) %{home_s}/bin/create_db.*
%attr(4755,sympa,sympa) %{home_s}/bin/queue
%attr(4755,sympa,sympa) %{home_s}/bin/bouncequeue
%attr(4755,sympa,sympa) %{home_s}/bin/*wrapper

%attr(755,sympa,sympa) %dir %{home_s}/etc
%attr(-,sympa,sympa) %{home_s}/etc/*
%attr(755,sympa,sympa) %dir %{home_s}/expl
#%attr(  -,sympa,sympa) %{home_s}/expl/*

%attr(755,sympa,sympa) %dir %{home_s}/lib
%attr(755,sympa,sympa) %dir %{home_s}/lib/Marc
%attr(-,sympa,sympa) %{home_s}/lib/Marc/*
%attr(-,sympa,sympa) %{home_s}/lib/*.pm
%attr(-,sympa,sympa) %{home_s}/lib/*.pl

%attr(755,sympa,sympa) %dir %{home_s}/nls
%attr(-,sympa,sympa) %{home_s}/nls/*.msg
%attr(755,sympa,sympa) %dir %{home_s}/sample
%attr(-,sympa,sympa) %{home_s}/sample/*

%attr(755,sympa,sympa) %dir %{home_s}/sbin
%attr(-,sympa,sympa) %{home_s}/sbin/*.pl
%attr(-,sympa,sympa) %{home_s}/sbin/wwsympa.fcgi

%attr(755,sympa,sympa) %dir %{home_s}/spool
%attr(744,sympa,sympa) %dir %{home_s}/spool/*

%dir /home/services/httpd/icons/sympa
/home/services/httpd/icons/sympa/*

%dir %{_sysconfdir}/sympa
%attr(640,sympa,sympa) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/sympa/*.conf
%attr(640,sympa,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/sympa
%attr(754,root,root) /etc/rc.d/init.d/sympa
%{_mandir}/man[58]/*
