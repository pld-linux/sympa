# TODO:
# - SECURITY: http://securitytracker.com/alerts/2004/Aug/1011016.html
# - COMPATIBILITY: check if works with webserver != apache and update R:
# - resolve problem with apache1 or apache2 icons directory...
# - no globs for suid/sgid files
# - rc-scripts service not restarted (should explain why not)
# - $HOSTNAME not present in all shells (see %%post)
Summary:	Sympa - a powerful multilingual List Manager with LDAP and SQL features
Summary(fr.UTF-8):	Sympa est un gestionnaire de listes électroniques
Summary(pl.UTF-8):	Sympa - użyteczny, wielojęzyczny zarządca list z obsługą LDAP i SQL
Name:		sympa
Version:	6.0
Release:	0.1
License:	GPL
Group:		Applications/Mail
Source0:	http://www.sympa.org/distribution/%{name}-%{version}b.2.tar.gz
# Source0-md5:	06336a063cbdd289b3c1e893f45408b4
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

%description -l pl.UTF-8
Sympa jest skalowalnym i wysoko konfigurowalnym zarządcą pocztowych
list dyskusyjnych. Radzi sobie z dużymi listami (100 000
subskrybentów) i przychodzi z pełnym (użytkownika i administratora)
interfejsem WWW. Jest zlokalizowany, obsługuje języki us, fr, de, es,
it, fi, zh. Język skryptowy pozwala na rozszerzanie komend. Sympa może
obsługiwać katalog LDAP lub relacyjne bazy danych do tworzenia
dynamicznych list. Obsługuje uwierzytelnianie i szyfrowanie oparte o
S/MIME.

%prep
%setup -q -a1 -n sympa-6.0b.2
#%%patch0 -p1
#%%patch1 -p1
#%%patch2 -p1

%build
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
        --prefix=%{home_s} \
        --exec-prefix=%{home_s} \
	--with-bindir=%{home_s}/bin \
	--with-cgidir=%{home_s}/fcgi \
	--with-confdir=%{_sysconfdir}/sympa \
	--libexecdir=%{home_s}/bin \
	--localedir=%{_localedir} \
	--with-initdir=/etc/rc.d/init.d \
	--with-perl=%{__perl} \
	--sbindir=%{home_s}/sbin \
	--with-user=sympa \
	--with-group=sympa \
	--with-piddir=/var/run \
	--with-spooldir=/var/spool/sympa \
	--with-sendmail_aliases=/etc/mail/sympa_aliases \
	--with-virtual_aliases=/etc/mail/sympa_virtual \
        --with-modulesdir=%{_libdir}/sympa \
	--with-newaliases=%{_bindir}/newaliases \
	--sysconfdir=%{_sysconfdir}/sympa

#	--with-cgidir=%{home_s}/sbin \
#	--with-bindir=%{home_s}/bin \
#	--sbindir=%{home_s}/sbin \
#	--libexecdir=%{home_s}/bin \
#	--with-defaultdir=%{home_s}/default \
#	--datadir=%{home_s}/etc \
#	--with-expldir=%{home_s}/expl \
#	--with-postmap=%{_bindir}/postmap \
#	--mandir=%{_mandir} \
#	--with-scriptdir=%{home_s}/bin \

%{__make} \
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

exit -1

install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/sympa
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/sympa
install %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/sympa/sympa.conf
install %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/sympa/wwsympa.conf

mv $RPM_BUILD_ROOT%{home_s}/locale $RPM_BUILD_ROOT/usr/share
rm -r $RPM_BUILD_ROOT%{home_s}/share/doc

%find_lang %{name}
%find_lang web_help
cat web_help.lang >> %{name}.lang

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
# FIXME $HOSTNAME not present in all shells
# TODO: use sed
%{__perl} -pi -e "s|MYHOST|${HOSTNAME}|g" /etc/sympa/sympa.conf /etc/sympa/wwsympa.conf

# Setup log facility for Sympa
if [ -f /etc/syslog.conf ]; then
	# TODO: touch sysklogd.spec/syslog-ng/metalog.spec/..... instead
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

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc [ACKNR]*

%attr(750,root,sympa) %dir %{home_s}
%attr(750,root,sympa) %dir %{home_s}/bin
%attr(4750,root,sympa) %{home_s}/sbin/*
%attr(4750,root,sympa) %{home_s}/bin/*

%{home_s}/default
%{home_s}/static_content

%attr(755,sympa,sympa) %dir %{home_s}/expl

%dir %{_libdir}/sympa
%{_libdir}/sympa

%attr(755,root,root) %{home_s}/fcgi/*.fcgi

%attr(755,sympa,sympa) %dir /var/spool/sympa
%attr(744,sympa,sympa) %dir /var/spool/sympa/*

%dir %{_sysconfdir}/sympa
%attr(640,root,sympa) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/sympa/*.conf
%attr(640,root,sympa) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/sympa
%attr(754,root,root) /etc/rc.d/init.d/sympa
%{_mandir}/man[58]/*
