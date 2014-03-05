#!/usr/bin/python2
import sys
from optparse import OptionParser

sys.path.append('lib')
from rpm import RPM


def get_options():
    optparser = OptionParser()

    optparser.add_option("-r", "--requires", action="store",
                         type="string", nargs=1)
    optparser.add_option("-a", "--application", action="store",
                         type="string", nargs=1)
    optparser.add_option("-d", "--src_dir", action="store",
                         type="string", nargs=1)
    optparser.add_option("-v", "--version", action="store",
                         type="string", nargs=1)
    optparser.add_option("-R", "--release", action="store",
                         type="string", nargs=1)
    optparser.add_option("-i", "--install_dir", action="store",
                         type="string", nargs=1)
    optparser.add_option("-c", "--architecture", action="store",
                         type="string", nargs=1)
    optparser.add_option("-l", "--license", action="store",
                         type="string", nargs=1)
    optparser.add_option("-x", "--dest_dir", action="store",
                         type="string", nargs=1)

    (options, unparsed) = optparser.parse_args()

    if unparsed:
        print("PROBLEM:"
              "Could not parse and/or understand the following arguments:")
        for arg in unparsed:
            print(" - %s" % arg)
        print()
        parser.print_help()
        sys.exit(-1)

    return (options.requires, options.application, options.src_dir,
            options.version, options.release, options.install_dir,
            options.architecture, options.src_dir, options.license,
            options.dest_dir)

if __name__ == "__main__":
    # get options and build paths
    (requires, application, dir_to_rpm,
     version, release, install_dir, arch,
     src_dir, license, dest_dir) = get_options()

    rpm = RPM(application, requires, version, release,
              license, install_dir, arch, src_dir, dest_dir)

    # build the RPM, write it to dest_dir
    rpm.build()
    rpm.write(dest_dir)
