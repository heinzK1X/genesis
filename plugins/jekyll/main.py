from genesis.api import *
from genesis.ui import *
from genesis.com import Plugin, Interface, implements
from genesis import apis
from genesis.utils import shell, download

import re
import nginx
import os


class Jekyll(Plugin):
	implements(apis.webapps.IWebapp)

	addtoblock = []

	def pre_install(self, name, vars):
		# Make sure Ruby directory is in the PATH.
		# This should work until there is a viable Ruby (RVM) plugin for Genesis
		profile = []
		f = open('/etc/profile', 'r')
		for l in f.readlines():
			if l.startswith('PATH="') and not '/usr/lib/ruby/gems/bin' in l:
				l = l.rstrip('"\n')
				l += ':/usr/lib/ruby/gems/bin"\n'
				profile.append(l)
				os.environ['PATH'] = os.environ['PATH'] + ':/usr/lib/ruby/gems/bin'
			else:
				profile.append(l)
		f.close()
		open('/etc/profile', 'w').writelines(profile)

		# Install the Jekyll and rdiscount gems required.
		if not any('jekyll' in s for s in shell('gem list').split('\n')):
			shell('gem install --no-user-install jekyll')
		if not any('rdiscount' in s for s in shell('gem list').split('\n')):
			shell('gem install --no-user-install rdiscount')

	def post_install(self, name, path, vars):
		# Make sure the webapps config points to the _site directory and generate it.
		c = nginx.loadf(os.path.join('/etc/nginx/sites-available', name))
		c.servers[0].filter('Key', 'root')[0].value = os.path.join(path, '_site')
		nginx.dumpf(c, os.path.join('/etc/nginx/sites-available', name))
		shell('jekyll build --source '+path+' --destination '+os.path.join(path, '_site'))

		# Return an explicatory message.
		return 'Jekyll has been setup, with a sample site at '+path+'. Modify these files as you like. To learn how to use Jekyll, visit http://jekyllrb.com/docs/usage. After making changes, click the Configure button next to the site, then "Regenerate Site" to bring your changes live.'

	def pre_remove(self, name, path):
		pass

	def post_remove(self, name):
		pass

	def ssl_enable(self, path, cfile, kfile):
		pass

	def ssl_disable(self, path):
		pass

	def regenerate_site(self, site):
		shell('jekyll build --source '+site.path.rstrip('_site')+' --destination '+os.path.join(site.path))
