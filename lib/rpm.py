from string import Template
import tempfile
import os
import tarfile

class RPM():
	def __init__(self, application, requires, version, release,
			   license, install_dir, arch, src_dir):
		self.application = application
		self.requires = requires
		self.version = version
		self.release = release
		self.license = license
		self.install_dir = install_dir
		self.arch = arch
		self.src_dir = src_dir

	def build(self):
		self._create_source_tar()
		spec_path = self._createspec()

	def _read_template(self):
		template_file = 'templates/spec.template'
		f = open(template_file)
		template_str = f.read()
		f.close()
	
		return template_str
	
	def _create_rpmbuild_env(self):
		t_dir = tempfile.mkdtemp()
	
		subdirs = ['RPMS', 'SPECS', 'SOURCES', 'BUILD']
		
		for dir in subdirs:
			os.makedirs("%s/%s" % (t_dir, dir))
		
		rpmbuild_env = dict(sources="%s/%s" % (t_dir, 'SOURCES'),
								 specs="%s/%s" % (t_dir, 'SPECS'))

		return rpmbuild_env

	def _clean_build_env(self):
		pass
		
	def _createspec(self):
		# Creates a spec file and returns the path
		
		template_str = self._read_template()
		build_env_path = self._create_rpmbuild_env()
	
		d = dict(application=self.application, source=self.tar_filename, 
				 requires=self.requires, version=self.version, 
				 release=self.release, license=self.license,
				 install_dir=self.install_dir, arch=self.arch)
	
		s = Template(template_str)
		
		s.safe_substitute(d)

		spec_path = "%s/SPECS/%s.spec" % (build_env_path, application)

		f = open(spec_path , 'w')
		f.write(s.safe_substitute(d))
		f.close()
	
		return spec_path

	def _create_source_tar(self):
		rpmbuild_env = self._create_rpmbuild_env()
		try:
			os.makedirs("%s/%s/" % (rpmbuild_env['sources'], self.application))
		except OSError:
			pass
	
		tar = tarfile.open("%s/%s/%s.tar.gz" % (rpmbuild_env['sources'],
    	                                        self.application,
    	                                        self.application), "w:gz")
		os.chdir("%s" % (self.src_dir))
		for root, dirs, files in os.walk("."):
			if '.git' not in root:
				for file in files:
					tar.add(join(root, file))
		tar.close()
		
		return "%s.tar.gz" % self.application


	def _create_rpm(self):
		package_name = spec_filename.split('.')
		r, w, e = popen2.popen3("rpmbuild --define '_topdir %s'\
    	                         --define '_sourcedir %s/SOURCES/%s' \
    	                         -bb SPECS/%s.spec" % (base_dir, base_dir,
    	                                               package_name[0],
    	                                               package_name[0]))
		output = r.read()
		error = e.read()
	
		return package_name[0]