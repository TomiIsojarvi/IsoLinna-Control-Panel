import urwid
import uuid
import json

import globals
from constants import *
from buttons.custom_button import CustomButton

#-------------------------------------------------------------------------------------------------#
#                                      GenerateUuidDialogBox                                      #
#-------------------------------------------------------------------------------------------------#
class GenerateUuidDialogBox:
    #---------------------------------------------------------------------------------------------#
    # Constructor                                                                                 #
    #---------------------------------------------------------------------------------------------#
    def __init__(self, owner):
        self.owner = owner
        blank = urwid.Divider()
        self.new_uuid = str(uuid.uuid1()) # Generate UUID and convert it to string
        text = urwid.Text([
            ("info", "New Device UUID: "), 
            ("body", f"{self.new_uuid}")
        ])

        save_button = CustomButton("Save", self.save_uuid)
        cancel_button = CustomButton("Cancel", self.back)

        buttons = urwid.GridFlow(
            [urwid.AttrMap(save_button, "button", "button_focused"),
            urwid.AttrMap(cancel_button, "button", "button_focused")],
            10, 3, 1, urwid.RIGHT
        )

        pile = urwid.Pile([blank, text, blank, buttons])
        padded_pile = urwid.Padding(pile, left=1, right=1)
        filler = urwid.Filler(padded_pile, valign="top")

        box = urwid.LineBox(
            filler,
            tlcorner=urwid.LineBox.Symbols.LIGHT.TOP_LEFT_ROUNDED,
            trcorner=urwid.LineBox.Symbols.LIGHT.TOP_RIGHT_ROUNDED,
            blcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_LEFT_ROUNDED,
            brcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_RIGHT_ROUNDED,
            title="Generate new Device UUID",
            title_align="left"
        )

        if self.owner.top:
            self.owner.top.open_box(box, UUID_DIALOG_WIDTH, UUID_DIALOG_HEIGHT)

    #---------------------------------------------------------------------------------------------#
    # back - Goes back to the previous view                                                       #
    #---------------------------------------------------------------------------------------------#
    def back(self, *_args) -> None:
        if self.owner.top and self.owner.top.box_level > 1:
            # Go back one level (same as pressing ESC)
            self.owner.top.original_widget = self.owner.top.original_widget[0]
            self.owner.top.box_level -= 1

    #---------------------------------------------------------------------------------------------#
    # save_uuid - Save the UUID and goes back to the previous view                                #
    #---------------------------------------------------------------------------------------------#
    def save_uuid(self, button: urwid.Button):
        globals.settings['device_uuid'] = self.new_uuid

        #  refresh the UI
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

