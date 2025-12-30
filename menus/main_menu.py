from __future__ import annotations

import urwid
import json
import sys
import os
import time
from datetime import datetime, timezone

import globals
from constants import *

from menus.cascading_boxes import CascadingBoxes
from menus.menu import Menu
from menus.settings_menu import MenuButton, SettingsMenu
from dialog_boxes.sensors_dialog_box import SensorsDialogBox
from buttons.custom_button import CustomButton
from dialog_boxes.broadcasting_dialog_box import BroadcastingDialogBox

# NOTE: This must be set before importing ruuvitag_sensor.
os.environ["RUUVI_BLE_ADAPTER"] = "bluez"

from ruuvitag_sensor.ruuvi import RuuviTagSensor, RunFlag

#-------------------------------------------------------------------------------------------------#
#                                            MainMenu                                             #
#-------------------------------------------------------------------------------------------------#
class MainMenu:
    global SETTINGS_PATH
    
    #---------------------------------------------------------------------------------------------#
    # Constructor                                                                                 #
    #---------------------------------------------------------------------------------------------#
    def __init__(self, main_screen) -> None:
        self.main_screen = main_screen  # Reference to the main application screen object.

        # Create the top menu
        self.menu_top = Menu(
            "Main Menu",
            [
                MenuButton("Start broadcasting", self.start_broadcasting),
                MenuButton("Sensors", lambda *_: SensorsDialogBox(self)),
                SettingsMenu(self, globals.settings),
                MenuButton("Log out", self.logout),
                MenuButton("Quit", self.quit),
            ],
        )
        
        # Wrap the main menu in CascadingBoxes for overlay support
        self.top = CascadingBoxes(self.menu_top)

        # Give the menu access to the main loop if needed
        self.menu_top.loop = globals.loop

    #---------------------------------------------------------------------------------------------#
    # start_broadcasting -                                                                        #
    #---------------------------------------------------------------------------------------------#
    def start_broadcasting(self, *_args):
        if globals.loop is None:
            return  # Loop not ready yet
        
        if not globals.settings['broadcasting']:
            globals.settings['broadcasting'] = True

            try:
                with open(SETTINGS_PATH, 'w') as f:
                    json.dump(globals.settings, f, indent=4)
            except IOError:
                print(f"[bold red]{SETTINGS_PATH}: Could not write file. Please check if you have write permissions.")
                exit(1)

        BroadcastingDialogBox()
    
    #---------------------------------------------------------------------------------------------#
    # logout - Logs out the current user                                                          #
    #---------------------------------------------------------------------------------------------#
    def logout(self, *_args):

        # Remove User UID, ID Token and Refresh Token from the settings
        del globals.settings['user_uid']
        del globals.settings['refresh_token']
        del globals.settings['id_token']
        del globals.settings['token_expiration_time']

        # Save settings to settings-file
        try:
            with open(SETTINGS_PATH, 'w') as f:
                json.dump(globals.settings, f, indent=4)
        except IOError:
            print(f"[bold red]{SETTINGS_PATH}: Could not write file. Please check if you have write permissions.")
            sys.exit(1)

        raise urwid.ExitMainLoop()
    
    #---------------------------------------------------------------------------------------------#
    # quit - quits the program                                                                    #
    #---------------------------------------------------------------------------------------------#
    def quit(self, *_args):
        sys.exit(0)
