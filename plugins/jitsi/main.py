import os

from genesis.ui import *
from genesis.api import *
from genesis import apis
from genesis.plugins.network.backend import IHostnameManager
from genesis.plugins.webapps.backend import WebappControl
from genesis.plugins.webapps.api import Webapp

import backend


class JitsiPlugin(apis.services.ServiceControlPlugin):
    text = 'Jitsi'
    iconfont = 'fa fa-video-camera'
    folder = 'servers'

    def on_session_start(self):
        self._wa = apis.webapps(self.app)
        self._rc = backend.JitsiControl(self.app)

    def on_init(self):
        pass

    def get_main_ui(self):
        pass

    #@event('button/click')
    def on_click(self, event, params, vars = None):
        pass

    #@event('dialog/submit')
    #@event('form/submit')
    def on_submit(self, event, params, vars=None):
        pass
