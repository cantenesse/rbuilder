from string import Template
import tempfile
import os

def _read_template():
	template_file = '../templates/spec.template'
	f = open(template_file)
	template_str = f.read()
	f.close()

	return template_str

def _create_rpmbuild_env():
	t_dir = tempfile.mkdtemp()

	subdirs = ['RPMS', 'SPECS', 'SOURCES', 'BUILD']
	
	for dir in subdirs:
		os.makedirs("%s/%s" % (t_dir, dir))
	print t_dir
	return t_dir

def createspec(tar_filename, application, requires, version,
			   release, install_dir, arch, license):
	template_str = _read_template()
	build_env_path = _create_rpmbuild_env()

	d = dict(application=application, source=tar_filename, requires=requires,
			 version=version, release=release, license=license,
			 install_dir=install_dir, arch=arch)

	s = Template(template_str)
	
	s.safe_substitute(d)
	f = open("%s/SPECS/%s.spec" % (build_env_path, application) , 'w')
	f.write(s.safe_substitute(d))
	f.close()

