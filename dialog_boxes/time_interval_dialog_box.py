import urwid
import json

import globals
from constants import *
from buttons.custom_button import CustomButton

#-------------------------------------------------------------------------------------------------#
#                                      TimeIntervalDialogBox                                      #
#-------------------------------------------------------------------------------------------------#
class TimeIntervalDialogBox:
    #---------------------------------------------------------------------------------------------#
    # Constructor                                                                                 #
    #---------------------------------------------------------------------------------------------#
    def __init__(self, owner):
        self.owner = owner
        blank = urwid.Divider()
        self.edit = urwid.Edit(("body", "Enter time interval (minutes): "), str(globals.settings["time_interval"]))

        save_button = CustomButton("Save", self.save_time_interval)
        cancel_button = CustomButton("Cancel", self.back)

        buttons = urwid.GridFlow(
            [urwid.AttrMap(save_button, "button", "button_focused"),
            urwid.AttrMap(cancel_button, "button", "button_focused")],
            10, 3, 1, urwid.RIGHT
        )

        pile = urwid.Pile([blank, self.edit, blank, buttons])
        padded_pile = urwid.Padding(pile, left=1, right=1)
        filler = urwid.Filler(padded_pile, valign="top")

        box = urwid.LineBox(
            filler,
            tlcorner=urwid.LineBox.Symbols.LIGHT.TOP_LEFT_ROUNDED,
            trcorner=urwid.LineBox.Symbols.LIGHT.TOP_RIGHT_ROUNDED,
            blcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_LEFT_ROUNDED,
            brcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_RIGHT_ROUNDED,
            title="Set Time Interval",
            title_align="left"
        )

        if self.owner.top:
            self.owner.top.open_box(box, TIME_INTERVAL_DIALOG_WIDTH, TIME_INTERVAL_DIALOG_HEIGHT)

    #---------------------------------------------------------------------------------------------#
    # back -                                                                                      #
    #---------------------------------------------------------------------------------------------#
    def back(self, *_args) -> None:
        if self.owner.top and self.owner.top.box_level > 1:
            # Go back one level (same as pressing ESC)
            self.owner.top.original_widget = self.owner.top.original_widget[0]
            self.owner.top.box_level -= 1

    #---------------------------------------------------------------------------------------------#
    # show_error_box - Displays an Error Box                                                      #
    #---------------------------------------------------------------------------------------------#
    def show_error_box(self, message: str) -> None:
        original_widget = globals.loop.widget

        #---------------------------------------------------------------------#
        # on_ok_clicked -                                                     #
        #---------------------------------------------------------------------#
        def on_ok_clicked(button):
            globals.loop.widget = original_widget
        #---------------------------------------------------------------------#

        error_text = urwid.Text(('error', message), align='center')
        ok_button = CustomButton("OK", on_ok_clicked)
        ok_button = urwid.Padding(ok_button, align='center', width=10)

        pile = urwid.Pile([error_text, urwid.Divider(), ok_button])
        filler = urwid.Filler(pile, valign='middle')

        box = urwid.LineBox(
            filler,
            title="Error",
            tlcorner=urwid.LineBox.Symbols.LIGHT.TOP_LEFT_ROUNDED,
            trcorner=urwid.LineBox.Symbols.LIGHT.TOP_RIGHT_ROUNDED,
            blcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_LEFT_ROUNDED,
            brcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_RIGHT_ROUNDED,
        )

        overlay = urwid.Overlay(
            box, original_widget,
            align='center', width=('relative', 50),
            valign='middle', height=('relative', 30),
            min_width=20, min_height=5
        )
        globals.loop.widget = overlay

    #---------------------------------------------------------------------------------------------#
    # save_time_interval -                                                                        #
    #---------------------------------------------------------------------------------------------#
    def save_time_interval(self, button: urwid.Button):
        # Get the value from the Edit widget
        try:
            value = int(self.edit.edit_text)
            globals.settings["time_interval"] = value
        except ValueError:
            self.show_error_box("Invalid number type")

        # refresh the UI
        if hasattr(self.owner, "main_screen"):
            self.owner.main_screen.refresh_info()

        # Save settings...
        try:
            with open(SETTINGS_PATH, 'w') as f:
                json.dump(globals.settings, f, indent=4)
        except IOError:
            print(f"{SETTINGS_PATH}: Could not write file. Please check if you have write permissions.")
            exit(1)

        # Go back
        self.back()