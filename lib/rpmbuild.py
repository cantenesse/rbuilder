from string import Template
import tempfile
import os
import tarfile
import popen2
import shutil


class RPM():
	def __init__(self, application, requires, version, release,
                 license, install_dir, arch, src_dir, dest_dir):
		self.application = application
		self.requires = requires
		self.version = version
		self.release = release
		self.license = license
		self.install_dir = install_dir
		self.arch = arch
		self.src_dir = src_dir
		self.dest_dir = dest_dir
		self.rpmbuild_env = self._create_rpmbuild_env()

	def build(self):
		src_tar = self._create_source_tar()
		self._createspec(src_tar)
		self._create_rpm(self.application)

	def write(self, rpm_dest_location):
		rpm_name = "%s-%s-%s.%s.rpm" % (self.application,
										self.version,
										self.release,
										self.arch)
		shutil.copyfile("%s/%s/%s" % (self.rpmbuild_env['rpms'],
									  self.arch,
									  rpm_name),
									  "%s/%s" % (rpm_dest_location,
									  			 rpm_name))
		self._clean_build_env()

	def _read_template(self):
		template_file = '/usr/local/rbuilder/templates/spec.template'
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
						 	specs="%s/%s" % (t_dir, 'SPECS'),
						 	rpms="%s/%s" % (t_dir, 'RPMS'),
						 	base_dir="%s" % t_dir)

		return rpmbuild_env

	def _clean_build_env(self):
		shutil.rmtree(self.rpmbuild_env['base_dir'])
		
	def _createspec(self, tar_filename):
		# Creates a spec file and returns the path
		
		template_str = self._read_template()
		rpmbuild_env = self._create_rpmbuild_env()

		if self.requires is None:
			requires_line = ""
		else:
			requires_line = "Requires: %s" % (self.requires)
	
		d = dict(application=self.application, source=tar_filename, 
				 requires=requires_line, version=self.version, 
				 release=self.release, license=self.license,
				 install_dir=self.install_dir, arch=self.arch)
	
		s = Template(template_str)
		
		s.safe_substitute(d)

		spec_path = "%s/%s.spec" % (self.rpmbuild_env['specs'], self.application)

		f = open(spec_path , 'w')
		f.write(s.safe_substitute(d))
		f.close()
	
		return spec_path

	def _create_source_tar(self):
		orig_dir = os.getcwd()
		try:
			os.makedirs("%s/%s/" % (self.rpmbuild_env['sources'], self.application))
		except OSError:
			pass
	
		tar = tarfile.open("%s/%s/%s.tar.gz" % (self.rpmbuild_env['sources'],
    	                                        self.application,
    	                                        self.application), "w:gz")
		os.chdir("%s" % (self.src_dir))
		for root, dirs, files in os.walk("."):
			if '.git' not in root:
				for file in files:
					tar.add("/".join([root, file]))
		tar.close()
		os.chdir(orig_dir)
		return "%s.tar.gz" % self.application


	def _create_rpm(self, application):
		r, w, e = popen2.popen3("rpmbuild --define '_topdir %s'\
    	                         --define '_sourcedir %s/%s' \
    	                         -bb %s/%s.spec" % (self.rpmbuild_env['base_dir'], 
													self.rpmbuild_env['sources'],
													application,
													self.rpmbuild_env['specs'],
													application))
		output = r.read()
		error = e.read()
