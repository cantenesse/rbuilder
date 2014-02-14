rbuilder
========

rbuilder is a tool that creates RPMs from specified local directories.  

# Example
- Create a directory that will be turned into a RPM.  The following will create a directory with 10 files.  
```
mkdir /tmp/blah
cd /tmp/blah
for i in $(seq 1 10);do touch $i;done
``` 

- Create a RPM that will install those 10 files onto any server.  This will create a RPM called RPMS/noarch/blah-2.0-2.rpm:
```
python rbuilder.py -a blah -d /tmp/blah -r 'nginx httpd' -v 2.0 -R 2 -i /usr/local -x /usr/src/rpmbuild
```

Note the command line options.  The rpm created will be called 'blah-2.0-2.rpm'.  When it's installed, it will require nginx and httpd.  Yum will install those packages.  The '-a' option is the rpm name.  The '-d' option is the directory where the build resides.  The '-c' is the architecture of the RPM.  The '-r' option is the RPMs that are required for installation.  The '-v' is the version.  The '-R' is the release.  The '-i' is where the files installed by the RPM will reside.  The '-x' is the location of the rpmbuild directory structure.  The resultant RPM will end up in /<path specified with -x>/RPMS/<arch specified with -c>

All command line options are required except '-r'.  If not specified, the installation of this RPM will not install any other RPMs.

- TODO
 * Read some stuff from a config file
 * Figure out a better templating system