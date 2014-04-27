# TODO
# - rm -rf libsqlite and build with system sqlite
#
# Conditional build:
%bcond_without	tests		# build without tests

%if 0
# To create tarball:
svn co http://svn.php.net/repository/pecl/sqlite/trunk sqlite
tar --exclude-vcs -cjf sqlite-r$(cd sqlite && svnversion).tar.bz2 sqlite
%endif

%define		rel		0.1
%define		svnrev	r333433
%define		php_name	php%{?php_suffix}
%define		modname	sqlite
Summary:	SQLite extension module for PHP
Summary(pl.UTF-8):	Moduł SQLite dla PHP
Name:		%{php_name}-pecl-%{modname}
Version:	2.0
Release:	0.%{svnrev}.%{rel}
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	%{modname}-%{svnrev}.tar.bz2
# Source0-md5:	5f5e08b404f5ba2e0b87d473c3c94eb7
#Source0:	http://pecl.php.net/get/%{modname}-%{version}.tgz
URL:		http://www.php.net/manual/en/book.sqlite.php
BuildRequires:	%{php_name}-devel
BuildRequires:	rpmbuild(macros) >= 1.666
BuildRequires:	sqlite-devel
%if %{with tests}
BuildRequires:	%{php_name}-cli
BuildRequires:	%{php_name}-pdo
BuildRequires:	%{php_name}-spl
%endif
%{?requires_php_extension}
Provides:	php(sqlite) = %{version}
Obsoletes:	php-sqlite < 4:5.4.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		sqlitever	%{version}-dev

%description
SQLite is a C library that implements an embeddable SQL database
engine. Programs that link with the SQLite library can have SQL
database access without running a separate RDBMS process.

SQLite is not a client library used to connect to a big database
server. SQLite is the server. The SQLite library reads and writes
directly to and from the database files on disk.

%description -l pl.UTF-8
SQLite jest napisaną w C biblioteką implementującą osadzalny silnik
bazodanowy SQL. Program linkujący się z biblioteką SQLite może mieć
dostęp do bazy SQL bez potrzeby uruchamiania dodatkowego procesu
RDBMS.

SQLite to nie klient baz danych - biblioteka nie łączy się z serwerami
baz danych. SQLite sam jest serwerem. Biblioteka SQLite czyta i
zapisuje dane bezpośrednio z/do plików baz danych znajdujących się na
dysku.

%prep
%setup -qc
mv sqlite/* .

%build
ver=$(awk '/#define PHP_SQLITE_MODULE_VERSION/ {print $3}' sqlite.c | xargs)
if test "$ver" != "%{sqlitever}"; then
	: Error: Upstream Sqlite version is now ${ver}, expecting %{sqlitever}.
	: Update the sqlitever macro and rebuild.
	exit 1
fi

phpize
%configure \
	--with-sqlite=shared,/usr \
	--enable-sqlite-utf8
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{php_extensiondir}/spl.so \
	-d extension=%{php_extensiondir}/pdo.so \
	-d extension=%{modname}.so \
	-m > modules.log
grep -i %{modname} modules.log

export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
%{__make} test \
	PHP_EXECUTABLE=%{__php}
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc README TODO CREDITS
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
