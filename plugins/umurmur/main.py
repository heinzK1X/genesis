from genesis.ui import *
from genesis.api import *
from genesis import apis
import backend


class UMurmurPlugin(apis.services.ServiceControlPlugin):
    text = 'Mumble Server'
    iconfont = 'gen-phone'
    folder = 'servers'

    def on_init(self):
        self._config = backend.UMurmurConfig(self.app)
        self._config.load()

    def on_session_start(self):
        self._tab = 0
        self._open_dialog = None
        self._open_dialog_info = None
        self.update_services()

    def get_main_ui(self):
        ui = self.app.inflate('umurmur:main')
        ui.find('tabs').set('active', 'tab' + str(self._tab))
        cfg = self._config.config

        if not hasattr(cfg, "channels") and 'Root' in cfg.channels:
            ui.remove('dlg_add_chan')
            ui.remove('dlg_add_chan_lnk')
            ui.append("container_settings", UI.Label(
                text="uMurmur settings file unavailable or damaged."
                     "Please reinstall uMurmur",
                size=3)
            )
            return ui

        # Tab 0: General Server Settings
        content = UI.FormBox(
            UI.FormLine(
                UI.TextInput(
                    name="welcometext",
                    value=cfg.get("welcometext", ""),
                ),
                text="Welcome text"
            ),
            UI.FormLine(
                UI.TextInput(
                    name="password",
                    value=cfg.get("password", ""),
                    password=True
                ),
                text="Server password"
            ),
            UI.FormLine(
                UI.TextInput(
                    name="admin_password",
                    value=cfg.get("admin_password", ""),
                    password=True
                ),
                text="Admin password",
                help="More info: https://code.google.com/p/umurmur/wiki/Admin",
            ),
            UI.FormLine(
                UI.TextInput(
                    name="max_bandwidth",
                    value=cfg.get("max_bandwidth", 48000),
                ),
                text="Max. bandwidth",
                help="In bits/second/user",
            ),
            UI.FormLine(
                UI.TextInput(
                    name="max_users",
                    value=cfg.get("max_users", 10),
                ),
                text="Max. users"
            ),
            id="form_server"
        )
        ui.append("container_settings", content)

        # channels
        channels = dict((c.name, c) for c in cfg.channels)
        channel_names = sorted(channels.keys())
        channel_names.remove("Root")
        channel_leaves = list()

        def recursive_add_row(chan, depth):
            children = list(
                channels[c] for c in channel_names
                if channels[c].parent == chan.name
            )
            edit_button = UI.Label(text="-")
            delete_button = UI.Label(text="-")
            if chan.name != 'Root':
                edit_button = UI.TipIcon(
                    iconfont='gen-pencil-2',
                    text='Edit',
                    id='dlg_editChan/%s' % chan.name,
                )
                if not children:
                    channel_leaves.append(chan.name)
                    delete_button = UI.TipIcon(  # only leaves can be deleted
                        iconfont='gen-cancel-circle',
                        text='Delete',
                        warning='Delete channel "%s"' % chan.name,
                        id='deleteChan/%s' % chan.name
                    )

            row = UI.DTR(
                UI.Label(text=". . "*depth + (" %s" % chan.name)),
                UI.Label(text=chan.description),
                UI.Label(text=("Yes" if chan.get("password") else "No")),
                UI.Label(text=("Yes" if chan.get("silent") else "No")),
                edit_button,
                delete_button,
            )
            ui.append('table_channels', row)
            if children:
                for c in children:
                    recursive_add_row(c, depth+1)
        recursive_add_row(channels["Root"], 0)

        # channel links
        for lnk in cfg.channel_links:
            src_dest = (lnk.source, lnk.destination)
            row = UI.DTR(
                UI.Label(text=lnk.source),
                UI.Label(text="=>"),
                UI.Label(text=lnk.destination),
                UI.TipIcon(
                    iconfont='gen-cancel-circle',
                    text='Delete',
                    warning='Delete channel link "%s => %s"' % src_dest,
                    id='deleteChanLnk/%s/%s' % src_dest
                )
            )
            ui.append('table_channel_links', row)

        # form: default channel
        def_chan = cfg.default_channel
        content = UI.FormBox(
            UI.FormLine(
                UI.SelectInput(*list(
                    UI.SelectOption(text=c, value=c, selected=(c == def_chan))
                    for c in channel_names if c != "Root"
                ), name="default_channel"),
                text="Default channel",
            ),
            id="form_def_chan"
        )
        ui.append("container_default_channel", content)

        # Dialogs
        if self._open_dialog == 'dlg_add_channel':
            content = UI.SimpleForm(
                UI.FormLine(
                    UI.TextInput(
                        name="chan_name",
                        value=""
                    ),
                    text="Name"
                ),
                UI.FormLine(
                    UI.TextInput(
                        name="chan_descr",
                        value=""
                    ),
                    text="Description"
                ),
                UI.FormLine(
                    UI.TextInput(
                        name="chan_pass",
                        value="",
                        password=True
                    ),
                    text="Password",
                    help="Passwords must be set as access tokens in the "
                         "client (checkout the server menu in Mumble).",
                ),
                UI.FormLine(
                    UI.SelectInput(*list(
                        UI.SelectOption(text=c, value=c)
                        for c in (["Root"] + channel_names),
                    ), name="chan_parent"),
                    text="Parent channel"
                ),
                UI.FormLine(
                    UI.CheckBox(
                        name="chan_silent",
                        text="Silent",
                        checked=False,
                    ),
                    checkbox=True
                    #TODO: help="" (checkout silent mode before... )
                ),
                id="dialog_add_channel"
            )
            box = UI.DialogBox(
                content,
                id="dlg_add_chan",
                title='Add channel'
            )
            ui.append("dialog_container", box)

        if self._open_dialog == 'dlg_editChan':
            chan = channels[self._open_dialog_info]
            content = UI.SimpleForm(
                UI.FormLine(
                    UI.TextInput(
                        name="chan_name",
                        value=chan.name,
                        disabled=True,
                    ),
                    text="Name"
                ),
                UI.FormLine(
                    UI.TextInput(
                        name="chan_descr",
                        value=chan.description
                    ),
                    text="Description"
                ),
                UI.FormLine(
                    UI.TextInput(
                        name="chan_pass",
                        value=chan.get('password', ''),
                        password=True
                    ),
                    text="Password",
                    help="Passwords must be set as access tokens in the "
                         "client (checkout the server menu in Mumble).",
                ),
                UI.FormLine(
                    UI.CheckBox(
                        name="chan_silent",
                        text="Silent",
                        checked=bool(chan.get('silent', False)),
                    ),
                    checkbox=True
                ),
                id="dialog_edit_channel"
            )
            box = UI.DialogBox(
                content,
                id="dlg_edit_chan",
                title='Edit channel "%s"' % chan.name
            )
            ui.append("dialog_container", box)

        if self._open_dialog == 'dlg_add_channel_link':
            content = UI.SimpleForm(
                UI.HContainer(
                    UI.SelectInput(*list(
                        UI.SelectOption(text=c, value=c)
                        for c in channel_names,
                    ), name="chan_src"),
                    UI.Label(text=" => "),
                    UI.SelectInput(*list(
                        UI.SelectOption(text=c, value=c)
                        for c in channel_names,
                    ), name="chan_dest"),
                    width="100%"
                ),
                id="dialog_add_channel_link"
            )
            box = UI.DialogBox(
                content,
                id="dlg_add_chan_lnk",
                title='Add channel link'
            )
            ui.append("dialog_container", box)

        self._open_dialog = None
        return ui

    @event('button/click')
    def on_click(self, event, params, vars=None):
        cfg = self._config.config
        if params[0].startswith("dlg_"):
            self._open_dialog = params[0]

        if params[0] == "dlg_editChan":
            self._open_dialog_info = params[1]

        if params[0] == "deleteChan":
            self._tab = 1
            del_chan = params[1]
            for chan in cfg.channels[:]:
                if del_chan == chan.name:
                    cfg.channels.remove(chan)
                    break
            for lnk in cfg.channel_links[:]:
                if del_chan in (lnk.source, lnk.destination):
                    cfg.channel_links.remove(lnk)
            self._config.save()

        if params[0] == 'deleteChanLnk':
            self._tab = 1
            src, dest = params[1:3]
            for lnk in cfg.channel_links[:]:
                if src == lnk.source and dest == lnk.destination:
                    cfg.channel_links.remove(lnk)
            self._config.save()

    @event('form/submit')
    def on_submit(self, event, params, vars=None):
        cfg = self._config.config

        # server settings
        if params[0] == 'form_server':
            self._tab = 0
            if vars.getvalue('action', '') == 'OK':
                cfg.set(
                    "welcometext",
                    vars.getvalue("welcometext", "")
                )
                cfg.set(
                    "password",
                    vars.getvalue("password", "")
                )
                cfg.set(
                    "admin_password",
                    vars.getvalue("admin_password", "")
                )
                try:
                    cfg.set(
                        "max_bandwidth",
                        int(vars.getvalue("max_bandwidth", ""))
                    )
                except ValueError:
                    self.put_message(
                        'warn', '"Max. bandwidth" must be an integer value.'
                    )
                try:
                    cfg.set(
                        "max_users",
                        int(vars.getvalue("max_users", ""))
                    )
                except ValueError:
                    self.put_message(
                        'warn', '"Max. users" must be an integer value.'
                    )
                self._config.save()

        # channel settings
        if params[0] == 'form_def_chan':
            self._tab = 1
            if vars.getvalue('action', '') == 'OK':
                cfg.set("default_channel", vars.getvalue("default_channel"))
                self._config.save()

        if vars.getvalue('action', '') == 'Cancel':
            self._config.load()

    @event('dialog/submit')
    def on_submit_dlg(self, event, params, vars=None):
        if vars.getvalue('action', '') != 'OK':
            return

        cfg = self._config.config
        if params[0] == 'dlg_add_chan':
            chan_name = vars.getvalue('chan_name')
            if not chan_name:
                self.put_message('warn', 'Channel name cannot be empty.')
                return

            if chan_name.lower() in (n.name.lower() for n in cfg.channels):
                self.put_message('warn', 'Channel name already exists.')
                return

            new_chan = backend.pylibconfig2.ConfGroup()
            new_chan.name = chan_name
            new_chan.description = vars.getvalue('chan_descr')
            new_chan.parent = vars.getvalue('chan_parent')
            if int(vars.getvalue('chan_silent')):
                new_chan.silent = True
            chan_pass = vars.getvalue('chan_pass')
            if chan_pass:
                new_chan.password = chan_pass
            cfg.channels.append(new_chan)
            self._config.save()
            self._tab = 1

        if params[0] == 'dlg_edit_chan':
            name = self._open_dialog_info
            chan = next(c for c in cfg.channels if c.name == name)
            chan.description = vars.getvalue('chan_descr')
            if int(vars.getvalue('chan_silent')):
                chan.silent = True
            elif hasattr(chan, 'silent'):
                del chan.silent
            chan_pass = vars.getvalue('chan_pass')
            if chan_pass:
                chan.password = chan_pass
            elif hasattr(chan, 'password'):
                del chan.password
            self._config.save()
            self._open_dialog_info = None
            self._tab = 1

        if params[0] == 'dlg_add_chan_lnk':
            chan_src = vars.getvalue('chan_src')
            chan_dest = vars.getvalue('chan_dest')
            if chan_src == chan_dest:
                self.put_message(
                    'warn', "Nope. I won't make a link with src == dest."
                )
                return
            if (chan_src, chan_dest) in (
                    (lnk.source, lnk.destination) for lnk in cfg.channel_links
            ):
                self.put_message(
                    'warn', "Nope. This channel link exists."
                )
                return
            new_lnk = backend.pylibconfig2.ConfGroup()
            setattr(new_lnk, "source", chan_src)
            setattr(new_lnk, "destination", chan_dest)
            cfg.channel_links.append(new_lnk)
            self._config.save()
            self._tab = 1

# TODO: check input for all submits
# TODO: Warning message if no cert assigned
# TODO: Move website content from here to layout file