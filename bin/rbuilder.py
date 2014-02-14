#!/usr/bin/python2
import sys
import os
from os.path import join
import tarfile
import shutil
import popen2
from optparse import OptionParser

def get_options():
    optparser = OptionParser()

    optparser.add_option("-r", "--requires", action="store", type="string", nargs=1)
    optparser.add_option("-a", "--application", action="store", type="string", nargs=1)
    optparser.add_option("-d", "--build_dir", action="store", type="string", nargs=1)
    optparser.add_option("-v", "--version", action="store", type="string", nargs=1)
    optparser.add_option("-R", "--release", action="store", type="string", nargs=1)
    optparser.add_option("-i", "--install_dir", action="store", type="string", nargs=1)
    optparser.add_option("-x", "--rpmbuild_dir", action="store", type="string", nargs=1)
    optparser.add_option("-c", "--architecture", action="store", type="string", nargs=1)
    
    (options, unparsed) = optparser.parse_args()
    if unparsed:
        print("PROBLEM:"
              "Could not parse and/or understand the following arguments:")
        for arg in unparsed:
            print(" - %s" % arg)
        print()
        parser.print_help()
        sys.exit(-1)

    return (options.requires, options.application, 
            options.build_dir, options.version, 
            options.release, options.install_dir,
            options.rpmbuild_dir, options.architecture)

def build_paths(rpmbuild_dir):
    rpmbuild_source = "%s/SOURCES" % rpmbuild_dir
    rpmbuild_spec = "%s/SPECS" % rpmbuild_dir
    #rpmbuild_rpms = "%s/RPMS/x86_64" % rpmbuild_dir

    return rpmbuild_source, rpmbuild_spec

def create_spec_file(tar_filename, application, requires, 
                        base_dir, version, release, 
                        install_dir, arch):
    try:
        os.makedirs("%s/SPECS" % (base_dir))
    except OSError:
        pass

    if requires is None:
        requires_line = ""
    else:
        requires_line = "Requires: %s" % (requires)

    spec_file = """
Summary: RPM generated from %s source
Name: %s
Version: %s
Release: %s
License: GPL
Group: applications/tools
BuildRoot: %%{_tmppath}/%%{name}
Source0: %s
%s
BuildArch: %s

%%description

%%prep
%%setup -c

%%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%s/%s/
rsync -av . $RPM_BUILD_ROOT/%s/%s/

%%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%%files
%%defattr(0755,root,root)
%s/%s

%%pre

%%post

""" % (application, application, version, release, tar_filename, 
        requires_line, arch, install_dir, application,
        install_dir, application, install_dir, 
        application)
    
    spec_filename = "%s.spec" % application
    os.chdir(base_dir)
    f = open("%s/%s" % (rpmbuild_spec, spec_filename), 'w+')
    f.write(spec_file)
    f.close()
    
    return spec_filename

def create_source_tar(rpmbuild_source, application, build_dir):
    try:
        os.makedirs("%s/%s/" % (rpmbuild_source, application))
    except OSError:
        pass
        
    tar = tarfile.open("%s/%s/%s.tar.gz" % (rpmbuild_source, application, application), "w:gz")
    os.chdir("%s" % (build_dir))
    for root, dirs, files in os.walk("."):
         if '.git' not in root:
             for file in files:
                 tar.add(join(root, file))
    tar.close()
    return "%s.tar.gz" % application

def create_rpm(spec_filename, base_dir):
    package_name = spec_filename.split('.')
    r, w, e = popen2.popen3("rpmbuild --define '_topdir %s'\
                             --define '_sourcedir %s/SOURCES/%s' \
                             -bb SPECS/%s.spec" % (base_dir, base_dir, 
                                                    package_name[0],
                                                    package_name[0]))
    output = r.read()
    error = e.read()

    return package_name[0]

if __name__ == "__main__":
    # get options and build paths
    requires, application, git_repo, version, release, install_dir, rpmbuild_dir, arch = get_options()
    rpmbuild_source, rpmbuild_spec = build_paths(rpmbuild_dir)

    # create source tar, spec file and create rpm
    tar_filename = create_source_tar(rpmbuild_source, application, git_repo)
    spec_filename = create_spec_file(tar_filename, application, requires, 
                                        rpmbuild_dir, version, release, 
                                        install_dir, arch)
    package_name = create_rpm(spec_filename, rpmbuild_dir)

    # clean up the build env
    shutil.rmtree("%s/%s" % (rpmbuild_source, package_name))

    print "Package Name: %s-%s-%s.rpm" % (package_name, version, 
                                            release) 