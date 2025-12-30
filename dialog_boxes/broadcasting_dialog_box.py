import os
import urwid
import threading
import json
import time
from datetime import datetime, timezone

# NOTE: This must be set before importing ruuvitag_sensor.
os.environ["RUUVI_BLE_ADAPTER"] = "bluez"

from ruuvitag_sensor.ruuvi import RuuviTagSensor, RunFlag

import globals
from constants import *
from buttons.custom_button import CustomButton

#-------------------------------------------------------------------------------------------------#
#                                          SensorsDialog                                          #
#-------------------------------------------------------------------------------------------------#
class BroadcastingDialogBox:
    #---------------------------------------------------------------------------------------------#
    # Constructor                                                                                 #
    #---------------------------------------------------------------------------------------------#
    def __init__(self):
        globals.run_flag = RunFlag()
        globals.run_flag.running = True  # Start scanning

        # Save the current UI so we can restore it later
        self.original_widget = globals.loop.widget

        # Text widgets for live updates
        count_text = urwid.Text(('info', "Broadcasting..."), align='center')
        sensors_text = urwid.Text(('body', ""), align='center')

        ok_button = CustomButton("Stop", self.on_stop_clicked)
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
            box, self.original_widget,
            align='center', width=('relative', 50),
            valign='middle', height=('pack'),
            min_width=20, min_height=5
        )

        # Show overlay
        globals.loop.widget = overlay

        thread = threading.Thread(target=self.send_sensor_data_thread)
        thread.start()

    #---------------------------------------------------------------------#
    # on_stop_clicked - Stop broacasting button callback                  #
    #---------------------------------------------------------------------#
    def on_stop_clicked(self, button):
        globals.run_flag.running = False  # Stop scanning
        globals.loop.widget = self.original_widget  # Restore main UI
        globals.settings['broadcasting'] = False

        try:
            with open(SETTINGS_PATH, 'w') as f:
                json.dump(globals.settings, f, indent=4)
        except IOError:
            print(f"[bold red]{SETTINGS_PATH}: Could not write file. Please check if you have write permissions.")
            exit(1)

    #---------------------------------------------------------------------#
    # send_sensor_data_thread - Thread for sending Ruuvi-data             #
    #---------------------------------------------------------------------#
    def send_sensor_data_thread(self):
        if len(globals.settings['followed_sensors']) == 0: 
            RuuviTagSensor.get_data(self.send_sensor_data, None, globals.run_flag)
        else:
            RuuviTagSensor.get_data(self.send_sensor_data, globals.settings['followed_sensors'], globals.run_flag)

    #---------------------------------------------------------------------#
    # send_sensor_data - Callback function for sending Ruuvi data         #
    #---------------------------------------------------------------------#
    def send_sensor_data(self, found_data):
        TOKEN_UPDATE_DURATION = 1800    # 1800 seconds = 30 minutes
        mac_address, sensor_data = found_data

        if sensor_data['data_format'] < 5:
            return
        
        current_time = time.time()

        # Check if the token has to be refreshed
        if (globals.settings['token_expiration_time'] - int(current_time)) <= TOKEN_UPDATE_DURATION:
            self.refresh_user_token()

        if globals.time_stamps.get(mac_address) is None or (current_time - globals.time_stamps[mac_address]) >= globals.settings['time_interval'] * 60:
            globals.time_stamps[mac_address] = current_time

            utc_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            globals.db.child("users").child(globals.settings['user_uid']).child("devices").child(globals.settings['device_uuid']).child(mac_address).push(
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
    # refresh_user_token - Refreshes the user's token                     #
    #---------------------------------------------------------------------#
    def refresh_user_token(self):
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

