from __future__ import annotations

import urwid
import threading
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
    # broadcasting_box -                                                                          #
    #---------------------------------------------------------------------------------------------#
    def broadcasting_box(self) -> None:
        globals.run_flag = RunFlag()
        globals.run_flag.running = True  # Start scanning
        followed_sensors = globals.settings['followed_sensors']

        # Save the current UI so we can restore it later
        original_widget = globals.loop.widget

        # Text widgets for live updates
        count_text = urwid.Text(('info', "Broadcasting..."), align='center')
        sensors_text = urwid.Text(('body', ""), align='center')

        #---------------------------------------------------------------------#
        # on_ok_clicked - OK button callback                                  #
        #---------------------------------------------------------------------#
        def on_ok_clicked(button):
            globals.run_flag.running = False  # Stop scanning
            globals.loop.widget = original_widget  # Restore main UI
            globals.settings['broadcasting'] = False

            try:
                with open(SETTINGS_PATH, 'w') as f:
                    json.dump(globals.settings, f, indent=4)
            except IOError:
                print(f"[bold red]{SETTINGS_PATH}: Could not write file. Please check if you have write permissions.")
                exit(1)

        #---------------------------------------------------------------------#
        # refresh_user_token - Refreshes the user's token                     #
        #---------------------------------------------------------------------#
        def refresh_user_token():
            try:
                tokens = globals.auth.refresh(globals.settings['refresh_token'])
                globals.settings['id_token'] = tokens['idToken']
                globals.settings['refresh_token'] = tokens['refreshToken']
                globals.settings['token_expiration_time'] = int(time.time()) + 3600 # 3600 seconds = 1 hour
            except Exception as e:
                print("Error refreshing token: ", e)

            try:
                with open(SETTINGS_PATH, 'w') as f:
                    json.dump(globals.settings, f, indent=4)
            except IOError:
                print(f"[bold red]{SETTINGS_PATH}: Could not create or write file")
                exit()

        #---------------------------------------------------------------------#
        # send_sensor_data - Callback function for sending Ruuvi data         #
        #---------------------------------------------------------------------#
        def send_sensor_data(found_data):
            TOKEN_UPDATE_DURATION = 1800    # 1800 seconds = 30 minutes
            mac_address, sensor_data = found_data

            if sensor_data['data_format'] < 5:
                return
            
            
            current_time = time.time()

            # Check if the token has to be refreshed
            if (globals.settings['token_expiration_time'] - int(current_time)) <= TOKEN_UPDATE_DURATION:
                refresh_user_token()

            if globals.time_stamps.get(mac_address) is None or (current_time - globals.time_stamps[mac_address]) >= globals.settings['time_interval'] * 60:
                globals.time_stamps[mac_address] = current_time

                utc_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

                push = globals.db.child("users").child(globals.settings['user_uid']).child("devices").child(globals.settings['device_uuid']).child(mac_address).push(
                    {
                        'utc_timestamp': utc_timestamp,
                        'temperature': sensor_data['temperature'], 
                        'humidity': sensor_data['humidity'], 
                        'pressure': sensor_data['pressure'], 
                        'rssi': sensor_data['rssi'],
                        'battery': sensor_data['battery']
                    }, 
                    token=globals.settings['id_token']
                )

                globals.db.child("users").child(globals.settings['user_uid']).child("devices").child(globals.settings['device_uuid']).child("new_values").child(mac_address).update(
                    {
                        'utc_timestamp': utc_timestamp,
                        'temperature': sensor_data['temperature'], 
                        'humidity': sensor_data['humidity'], 
                        'pressure': sensor_data['pressure'], 
                        'rssi': sensor_data['rssi'],
                        'battery': sensor_data['battery']
                    }, 
                    token=globals.settings['id_token']
                )

        #---------------------------------------------------------------------#
        # send_sensor_data_thread - Thread for sending Ruuvi-data             #
        #---------------------------------------------------------------------#
        def send_sensor_data_thread():
            if len(globals.settings['followed_sensors']) == 0: 
                RuuviTagSensor.get_data(send_sensor_data, None, globals.run_flag)
            else:
                RuuviTagSensor.get_data(send_sensor_data, globals.settings['followed_sensors'], globals.run_flag)
        #----------------------------------------------------------------------

        ok_button = CustomButton("Stop", on_ok_clicked)
        ok_button = urwid.Padding(ok_button, align='center', width=10)

        # Layout: messages + button
        pile = urwid.Pile([urwid.Divider(), count_text, urwid.Divider(), ok_button])
        filler = urwid.Filler(pile)

        # Overlay box
        box = urwid.LineBox(
            filler,
            title="",
            tlcorner=urwid.LineBox.Symbols.LIGHT.TOP_LEFT_ROUNDED,
            trcorner=urwid.LineBox.Symbols.LIGHT.TOP_RIGHT_ROUNDED,
            blcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_LEFT_ROUNDED,
            brcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_RIGHT_ROUNDED,
        )

        overlay = urwid.Overlay(
            box, original_widget,
            align='center', width=('relative', 50),
            valign='middle', height=('pack'),
            min_width=20, min_height=5
        )

        # Show overlay
        globals.loop.widget = overlay

        thread = threading.Thread(target=send_sensor_data_thread)
        thread.start()


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

        self.broadcasting_box()
    
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
