import nginx
import os

from genesis.api import *
from genesis.com import *
from genesis import apis
from genesis.plugins.users.backend import *
from genesis.plugins.webapps.backend import WebappControl
from genesis.utils import shell_cs, hashpw


class JitsiControl(Plugin):
    setup_complete = False

    def is_installed(self):
        pass

    def setup(self, addr, port):
        pass
