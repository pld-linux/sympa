%include	/usr/lib/rpm/macros.perl
Summary:	Sympa is a powerful multilingual List Manager - LDAP and SQL features
Summary(fr):	Sympa est un gestionnaire de listes électroniques
Name:		sympa
Version:	3.0.3
Release:	2
License:	GPL
Group:		Aplications/Mail
Group(pl):	Aplikacje/Poczta
Source0:	http://listes.cru.fr/sympa/distribution/%{name}-%{version}.tar.gz
URL:		http://listes.cru.fr/sympa/
Patch0:		sympa-makefile.patch
Requires:	perl 		   >= 5.6.0
Requires:	perl-MailTools     >= 1.14
Requires:	perl-MIME-Base64   >= 1.0
Requires:	perl-IO-stringy    >= 1.0
Requires:	perl-Locale-Msgcat >= 1.03
Requires:	perl-MIME-tools    >= 5.209
Requires:	perl-CGI-modules   >= 2.52
Requires:	perl-DBI	   >= 1.06
#Requires:	perl-DB_File       >= 1.0  # jest juz w perl-5.6.0
Requires:	perl-ldap          >= 0.10
## Also requires a DBD for the DBMS 
## (perl-DBD-Pg or Perl- Msql-Mysql-modules)
Requires:	perl-FCGI          >= 0.48
Requires:	MHonArc 	   >= 2.4.5
Requires:	perl-Digest-MD5
Requires:	apache
Requires:	openssl 	   >= 0.9.5a
Prereq:		/usr/sbin/useradd
Prereq:		/usr/sbin/groupadd
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Sympa is scalable and highly customizable mailing list manager. It can
cope with big lists (100,000 subscribers) and comes with a complete
(user and admin) Web interface. It is internationalized, and supports
the us, fr, de, es, it, fi, and chinese locales. A scripting language
allows you to extend the behavior of commands. Sympa can be linked to
an LDAP directory or an RDBMS to create dynamic mailing lists. Sympa
provides S/MIME-based authentication and encryption.

Documentation is available under HTML and Latex (source) formats.


%prep
%setup -q
%patch0 -p1

%build

%{__make} DIR=/home/sympa sources languages

%install
rm -rf $RPM_BUILD_ROOT

%{__make} INITDIR=/etc/rc.d/init.d HOST=MYHOST DIR=/home/sympa DESTDIR=$RPM_BUILD_ROOT install

%pre
GID=71; %groupadd
UID=71; HOMEDIR=/home/sympa; COMMENT=sympa; %useradd

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
    ln -s /home/sympa/bin/queue /etc/smrsh/queue
  fi
fi

%post
%chkconfig_add
perl -pi -e "s|MYHOST|${HOSTNAME}|g" /etc/sympa/sympa.conf /etc/sympa/wwsympa.conf

%preun
%chkconfig_del

%postun
if [ ! -d /home/sympa ]; then
%userdel
%groupdel
fi
if [ $1 = 0 -a -d /etc/smrsh ]; then
  if [ -L /etc/smrsh/queue ]; then
    rm -f /etc/smrsh/queue
  fi
fi

%files
%defattr(644,root,root,755)

%defattr(0755,sympa,sympa)
%dir /home/sympa
%dir /home/sympa/bin
%dir /home/sympa/bin/Marc
%dir /home/sympa/bin%{_sysconfdir}
%dir /home/sympa/sample
%dir /home/sympa/expl
%dir /home/sympa/spool
%dir /home/sympa/nls
%dir /home/sympa%{_sysconfdir}

%defattr(0744,sympa,sympa)
%dir /home/sympa/spool/*

%defattr(-,sympa,sympa)
/home/sympa/sample/*
/home/sympa/bin/Marc/*
/home/sympa/bin%{_sysconfdir}/*
/home/sympa/expl/*

%attr(0755,root,root)%dir /home/httpd/icons
%attr(0644,root,root) /home/httpd/icons/*

%defattr(-,sympa,sympa)
/home/sympa/bin/*.pm
/home/sympa/bin/*.pl
/home/sympa/bin/create_db.*
/home/sympa/bin/wwsympa.fcgi

%attr(4755,sympa,sympa) /home/sympa/bin/queue
%attr(4755,sympa,sympa) /home/sympa/bin/bouncequeue

/home/sympa/nls/*.cat

%defattr(0640,sympa,sympa)
%config(noreplace) %{_sysconfdir}/sympa/sympa.conf
%config(noreplace) %{_sysconfdir}/sympa/wwsympa.conf
%defattr(0755,root,root)
%config(noreplace) /etc/rc.d/init.d/sympa

%defattr(-,root,root)
%doc INSTALL LICENSE README RELEASE_NOTES
%doc doc/*

%clean
rm -rf $RPM_BUILD_ROOT
