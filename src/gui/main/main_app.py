import json
from sys import platform, argv
from threading import Thread
from json import load
from time import time

from tkinter import *
from PIL import Image
from webbrowser import open as OpenUrl

if platform.lower() == 'win32':
    from tkinter.ttk import *

from gui.app import App
from utils.not_windows import NotWindows
from gui.main.menu_bar import MenuBar
from utils.user_settings import UserSettings
from utils.get_file import resource_path
from utils.warning_pop_up_save import confirm_save
from utils.record_file_management import RecordFileManagement
from utils.version import Version
from gui.others.new_ver_avalaible import NewVerAvailable
from hotkeys.hotkeys_manager import HotkeysManager
from macro import Macro
from pystray import Icon
from pystray import MenuItem


class MainApp(App):
    """Main windows of the application"""

    def __init__(self):
        super().__init__()
        self.attributes('-topmost', 1)
        if platform == 'win32':
            self.iconbitmap(resource_path(['assets', 'logo.ico']))

        elif platform.lower() == 'linux':
            self.tk.call('wm', 'iconphoto', self._w, PhotoImage(file=resource_path(['assets', 'logo.png'])))

        self.settings = UserSettings(self)

        self.lang = self.settings.get_config()['Language']
        with open(resource_path(['langs',  f'{self.lang}.json']), encoding='utf-8') as f:
            self.text_content = json.load(f)

        self.text_content = self.text_content['content']

        # For save message purpose
        self.macro_saved = False
        self.macro_recorded = False
        self.current_file = None
        self.prevent_record = False

        self.version = Version(self.settings.get_config(), self)

        self.menu = MenuBar(self)  # Menu Bar
        self.macro = Macro(self)

        self.validate_cmd = self.register(self.validate_input)

        self.hotkeyManager = HotkeysManager(self)

        # Main Buttons (Start record, stop record, start playback, stop playback)

        # Play Button
        self.playImg = PhotoImage(file=resource_path(['assets', 'button', 'play.png']))

        # Import record if opened with .pmr extension
        if len(argv) > 1:
            with open(argv[1], 'r') as record:
                loaded_content = load(record)

            self.macro.import_record(loaded_content)
            self.playBtn = Button(self, image=self.playImg, command=self.macro.start_playback)
            self.macro_recorded = True
            self.macro_saved = True

        else:
            self.playBtn = Button(self, image=self.playImg, state=DISABLED)

        self.playBtn.pack(side=LEFT, padx=50)

        # Record Button
        self.recordImg = PhotoImage(file=resource_path(['assets', 'button', 'record.png']))
        self.recordBtn = Button(self, image=self.recordImg, command=self.macro.start_record)
        self.recordBtn.pack(side=RIGHT, padx=50)

        # Stop Button
        self.stopImg = PhotoImage(file=resource_path(['assets', 'button', 'stop.png']))

        # Branding
        self.brandingImg = PhotoImage(file=resource_path(['assets', 'branding.png']))

        self.brandingUrl = 'https://www.o-x-l.com'
        if self.lang == 'de':
            self.brandingUrl = 'https://www.oxl.at'

        self.brandingBtn = Button(self, image=self.brandingImg, command=lambda: OpenUrl(self.brandingUrl))
        self.brandingBtn.pack(side=BOTTOM, pady=10)

        record_management = RecordFileManagement(self, self.menu)

        self.bind('<Control-Shift-S>', record_management.save_macro_as)
        self.bind('<Control-s>', record_management.save_macro)
        self.bind('<Control-l>', record_management.load_macro)
        self.bind('<Control-n>', record_management.new_macro)

        self.protocol('WM_DELETE_WINDOW', self.quit_software)
        if platform.lower() != 'darwin':
            Thread(target=self.systemTray).start()

        self.attributes('-topmost', 0)

        if platform != 'win32' and self.settings.first_time:
            NotWindows(self)

        if self.settings.get_config()['Others']['Check_update']:
            if self.version.new_version != '' and self.version.version != self.version.new_version:
                if time() > self.settings.get_config()['Others']['Remind_new_ver_at']:
                    NewVerAvailable(self, self.version.new_version)

        self.mainloop()

    def systemTray(self):
        '''Just to show little icon on system tray'''
        # todo: fix tray icon on linux
        image = Image.open(resource_path(['assets', 'logo.ico']))
        menu = (
            MenuItem('Show', action=self.deiconify, default=True),
        )
        self.icon = Icon('name', image, 'Computer Automation', menu)
        self.icon.run()

    def validate_input(self, action, value_if_allowed):
        '''Prevents from adding letters on an Entry label'''
        if action == '1':  # Insert
            try:
                float(value_if_allowed)
                return True

            except ValueError:
                return False

        return True

    def quit_software(self, force=False):
        if not self.macro_saved and self.macro_recorded and not force:
            wantToSave = confirm_save(self)
            if wantToSave:
                RecordFileManagement(self, self.menu).save_macro()

            elif wantToSave is None:
                return

        if platform.lower() != 'darwin':
            self.icon.stop()

        if platform.lower() == 'linux':
            self.destroy()

        self.quit()