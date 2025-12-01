from __future__ import annotations
import urwid
import sys
import globals
from menus.main_menu import MainMenu

#-------------------------------------------------------------------------------------------------#
#                                           MainScreen                                            #
#-------------------------------------------------------------------------------------------------#
class MainScreen:
    palette = [
        ("body", "white", "black", "standout"),
        ("error", "light red", "black", "bold"),
        ("edit_caption", "dark gray", "black"),
        ("focus_edit_caption", "white", "black", "standout"),
        ("button", "dark gray", "black"),
        ("button_focused", "white,bold", "black"),
        ("sensor_selected", "black", "dark gray"),
        ("sensor_selected_focused", "white,bold", "dark gray"),
        ("info", "light green,bold", "black"),

    ]

    #---------------------------------------------------------------------------------------------#
    # Constructor                                                                                 #
    #---------------------------------------------------------------------------------------------#
    def __init__(self, width: int, height: int) -> None:
        self.login = True

        self.width = width
        if self.width <= 0:
            self.width = (urwid.RELATIVE, 80)
        self.height = height
        if self.height <= 0:
            self.height = (urwid.RELATIVE, 80)

        # Title box -----------------------------
        title_text = urwid.Text("IsoLinna Control Panel", align="center")
        title_box = urwid.LineBox(
            urwid.Filler(title_text),
            tlcorner=urwid.LineBox.Symbols.LIGHT.TOP_LEFT_ROUNDED,
            trcorner=urwid.LineBox.Symbols.LIGHT.TOP_RIGHT_ROUNDED,
            blcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_LEFT_ROUNDED,
            brcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_RIGHT_ROUNDED,
            title_align="center"
        )
        #----------------------------------------

        # Device Info Box -----------------------
        self.user_uid_text = urwid.Text([
            ("info", " User UID: "), 
            ("body", f"{globals.settings['user_uid']}")
        ])
        self.device_uuid_text = urwid.Text([
            ("info", " Device UUID: "), 
            ("body", f"{globals.settings['device_uuid']}")
        ])

        interval = globals.settings["time_interval"]
        unit = "minute" if interval == 1 else "minutes"

        self.time_interval_text = urwid.Text([
            ("info", " Time Interval: "), 
            ("body", f"{interval} {unit}")
        ])

        # Stack User UID, Device UUID, and Time Interval Info
        info = urwid.Pile([
            self.user_uid_text,
            self.device_uuid_text,
            self.time_interval_text,
        ])

        # Make a LineBox
        info_box = urwid.LineBox(
            urwid.Filler(info, valign="top"),
            tlcorner=urwid.LineBox.Symbols.LIGHT.TOP_LEFT_ROUNDED,
            trcorner=urwid.LineBox.Symbols.LIGHT.TOP_RIGHT_ROUNDED,
            blcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_LEFT_ROUNDED,
            brcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_RIGHT_ROUNDED,
            title="Device Information",
            title_align="center"
        )

        info_box = urwid.AttrMap(info_box, "body")
        #----------------------------------------

        # --------- MAIN MENU AT BOTTOM ---------
        self.main_menu = MainMenu(main_screen=self)

        # Stack title, info, and menu
        layout = urwid.Pile([
            ("pack", title_box),
            ("pack", info_box),
            self.main_menu.top,
        ])
        #----------------------------------------

        # Final layout with padding
        w = urwid.Padding(layout, align=urwid.CENTER, width=self.width)

        self.view = w
        

    #---------------------------------------------------------------------------------------------#
    # unhandled_key - Handles the keys that aren't normally supported                             #
    #---------------------------------------------------------------------------------------------#
    def unhandled_key(self, k: str) -> None:
        if k in ("q", "Q"):
            if globals.runFlag != None and globals.runFlag == True:
                globals.runFlag.running = False
            sys.exit(0)
            
    #---------------------------------------------------------------------------------------------#
    # refresh_info - Updates the Device Information                                               #
    #---------------------------------------------------------------------------------------------#
    def refresh_info(self):
        self.device_uuid_text.set_text([
            ("info", " Device UUID: "), 
            ("body", f"{globals.settings['device_uuid']}")
        ])

        interval = globals.settings["time_interval"]
        unit = "minute" if interval == 1 else "minutes"

        self.time_interval_text.set_text([
            ("info", " Time Interval: "), 
            ("body", f"{interval} {unit}")
        ])

    #---------------------------------------------------------------------------------------------#
    # main - Opens the screen and starts the rendering loop                                       #
    #---------------------------------------------------------------------------------------------#
    def main(self) -> None:
        globals.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.unhandled_key)

        # If broadcasting...
        if globals.settings.get('broadcasting'):
            self.main_menu.start_broadcasting()
            
        globals.loop.run()
