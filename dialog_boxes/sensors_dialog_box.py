import os
import urwid
import json
import threading

# NOTE: This must be set before importing ruuvitag_sensor.
os.environ["RUUVI_BLE_ADAPTER"] = "bluez"

from ruuvitag_sensor.ruuvi import RuuviTagSensor, RunFlag

import globals
from constants import *
from buttons.custom_button import CustomButton
from buttons.sensor_button import SensorButton

#-------------------------------------------------------------------------------------------------#
#                                          SensorsDialog                                          #
#-------------------------------------------------------------------------------------------------#
class SensorsDialogBox:
    #---------------------------------------------------------------------------------------------#
    # Constructor                                                                                 #
    #---------------------------------------------------------------------------------------------#
    def __init__(self, owner, selected_sensors=[], restore_from_settings=True):
        self.owner = owner

        if restore_from_settings and globals.settings['followed_sensors']:
            # Restore selection from settings file
            self.selected_sensors = globals.settings['followed_sensors'].copy()
        else:
            # Use provided lists
            self.selected_sensors = selected_sensors.copy() if selected_sensors else []

        sensors_menu_items = []
        self.automatic_button = None
        globals.run_flag = RunFlag()
        globals.run_flag.running = False

        scan_button = CustomButton("Scan", self.scan)
        save_button = CustomButton("Save", self.save_sensors)
        cancel_button = CustomButton("Cancel", self.back)

        buttons = urwid.GridFlow(
            [
                urwid.AttrMap(scan_button, "button", "button_focused"),
                urwid.AttrMap(save_button, "button", "button_focused"),
                urwid.AttrMap(cancel_button, "button", "button_focused")
            ],
            10, 3, 1, urwid.RIGHT
        )

        # Sensors in the sensors menu...
        # Is the selected sensors empty?
        if not self.selected_sensors:
            self.automatic_button = SensorButton("Automatic", globals.settings, callback=self.automatic, selected=True)
        else:
            self.automatic_button = SensorButton("Automatic", globals.settings, callback=self.automatic, selected=False)

        sensors_menu_items.append(self.automatic_button)

        # Add sensors from discovered sensors
        for i, sensor in enumerate(globals.discovered_sensors):
            if sensor in self.selected_sensors:
                sensors_menu_items.append(
                    SensorButton(
                        sensor,
                        settings=globals.settings,
                        callback=lambda btn, cap, idx=i: self.select_sensor(btn, idx),
                        selected=True
                    )
                )
            else:
                sensors_menu_items.append(
                    SensorButton(
                        sensor,
                        settings=globals.settings,
                        callback=lambda btn, cap, idx=i: self.select_sensor(btn, idx),
                        selected=False
                    )
                )

        # Set up the sensors menu
        body = [*sensors_menu_items]
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        padded = urwid.Padding(listbox, left=1, right=1)
        sensors_menu = urwid.LineBox(
            padded,
            tlcorner=urwid.LineBox.Symbols.LIGHT.TOP_LEFT_ROUNDED,
            trcorner=urwid.LineBox.Symbols.LIGHT.TOP_RIGHT_ROUNDED,
            blcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_LEFT_ROUNDED,
            brcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_RIGHT_ROUNDED,
            title="",
            title_align="left"
        )

        sensors_menu = urwid.BoxAdapter(sensors_menu, SENSORS_MENU_HEIGHT)

        self.main_pile = urwid.Pile([sensors_menu, buttons])
        padded_pile = urwid.Padding(self.main_pile, left=1, right=1)
        filler = urwid.Filler(padded_pile, valign="top")

        box = urwid.LineBox(
            filler,
            tlcorner=urwid.LineBox.Symbols.LIGHT.TOP_LEFT_ROUNDED,
            trcorner=urwid.LineBox.Symbols.LIGHT.TOP_RIGHT_ROUNDED,
            blcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_LEFT_ROUNDED,
            brcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_RIGHT_ROUNDED,
            title="Sensors",
            title_align="left"
        )

        if self.owner.top:
            self.owner.top.open_box(box, SENSORS_DIALOG_WIDTH, SENSORS_DIALOG_HEIGHT)

    #---------------------------------------------------------------------------------------------#
    # back - Goes back to the Main Screen                                                         #
    #---------------------------------------------------------------------------------------------#    
    def back(self, *_args) -> None:
        # This is not important... It is for the UI. selected_sensors has to be initialize to it's original state. 
        self.selected_sensors = globals.settings['followed_sensors'].copy()

        if self.owner.top and self.owner.top.box_level > 1:
            self.owner.top.original_widget = self.owner.top.original_widget[0]
            self.owner.top.box_level -= 1

    #---------------------------------------------------------------------------------------------#
    # scan - Scans for Ruuvi Tag - sensors                                                        #
    #---------------------------------------------------------------------------------------------#
    def scan(self, *_args) -> None:
        new_found_sensors = []

        #---------------------------------------------------------------------#
        # on_ok_clicked -                                                     #
        #---------------------------------------------------------------------#
        def on_ok_clicked(button):
            globals.run_flag.running = False  # Stop scanning

            # Remove the current overlay / SensorDialog
            if self.owner.top and self.owner.top.box_level > 0:
                self.owner.top.original_widget = self.owner.top.original_widget[0]
                self.owner.top.box_level -= 1

            # Reopen the sensors dialog with updated sensor list
            SensorsDialogBox(self.owner, self.selected_sensors, restore_from_settings=False)

            globals.loop.widget = original_widget

        #---------------------------------------------------------------------#
        # scan_sensors - Callback function for the Ruuvi get_data             #
        #---------------------------------------------------------------------#
        def scan_sensors(found_data):
            nonlocal found_sensors
            mac_address, sensor_data = found_data

            if mac_address not in globals.discovered_sensors:
                globals.discovered_sensors.append(mac_address)
                new_found_sensors.append(mac_address)
                found_sensors += 1
                
                count_text.set_text(('info', f" Found {found_sensors} new sensors:\n"))
                # sensors_text.set_text(('body', "\n".join(globals.discovered_sensors)))
                sensors_text.set_text(('body', "\n".join(new_found_sensors)))
                globals.loop.draw_screen()  # Force redraw

        #---------------------------------------------------------------------#
        # scan_sensors_thread - Thread for scanning Ruuvi-sensors             #
        #---------------------------------------------------------------------#
        def scan_sensors_thread():
            RuuviTagSensor.get_data(scan_sensors, None, globals.run_flag)
            
        #----------------------------------------------------------------------

        # Set the RunFlag to True
        globals.run_flag.running = True

        # Save the current widget so we can restore it
        original_widget = globals.loop.widget
        found_sensors = 0

        # Create messages and OK button
        count_text = urwid.Text(('info', f" Found {found_sensors} new sensors\n"), align='center')
        sensors_text = urwid.Text(('body', ""), align='center')  # initially empty
        ok_button = CustomButton("OK", on_ok_clicked)
        ok_button = urwid.Padding(ok_button, align='center', width=10)

        # Stack message and button
        pile = urwid.Pile([urwid.Divider(), count_text, sensors_text, urwid.Divider(), ok_button])
        filler = urwid.Filler(pile)

        # Create bordered box
        box = urwid.LineBox(
                filler,
                title="Scanninng Sensors",
                tlcorner=urwid.LineBox.Symbols.LIGHT.TOP_LEFT_ROUNDED,
                trcorner=urwid.LineBox.Symbols.LIGHT.TOP_RIGHT_ROUNDED,
                blcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_LEFT_ROUNDED,
                brcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_RIGHT_ROUNDED,
            )

        # Overlay it on top of the original view
        overlay = urwid.Overlay(
            box, original_widget,
            align='center', width=('relative', 50),
            valign='middle', height=('pack'),
            min_width=20, min_height=5
        )

        globals.loop.widget = overlay

        # Create a thread for scanning Ruuvi-sensors
        thread = threading.Thread(target=scan_sensors_thread, daemon=True)
        thread.start()

    #---------------------------------------------------------------------------------------------#
    # save_sensors - Save selected sensors and goes back to the Main Screen                       #
    #---------------------------------------------------------------------------------------------#
    def save_sensors(self, button: urwid.Button):
        globals.settings['followed_sensors'] = self.selected_sensors
        
        # Save settings
        try:
            with open(SETTINGS_PATH, 'w') as f:
                json.dump(globals.settings, f, indent=4)
        except IOError:
            print(f"{SETTINGS_PATH}: Could not write file. Please check if you have write permissions.")
            exit(1)

        # Go back
        self.back()    

    #---------------------------------------------------------------------------------------------#
    # automatic - When Automatic is selected                                                      #
    #---------------------------------------------------------------------------------------------#
    def automatic(self, *_args):
        self.selected_sensors = []

        # Close current dialog...
        if self.owner.top and self.owner.top.box_level > 1:
            self.owner.top.original_widget = self.owner.top.original_widget[0]
            self.owner.top.box_level -= 1

        # Reopen WITHOUT restoring settings
        SensorsDialogBox(self.owner, self.selected_sensors, restore_from_settings=False)

    #---------------------------------------------------------------------------------------------#
    # select_sensor - When Sensor is selected from the list                                       #
    #---------------------------------------------------------------------------------------------#
    def select_sensor(self, btn, idx):
        sensor = globals.discovered_sensors[idx]
            
        if sensor not in self.selected_sensors:
            self.selected_sensors.append(sensor)
        else:
            self.selected_sensors.remove(sensor)
            
        # Deselect the Automatic-button
        if self.automatic_button:
            self.automatic_button.selected = False
            self.automatic_button.attr_map.set_attr_map({None: "button"})
            self.automatic_button.attr_map.set_focus_map({None: "button_focused"})