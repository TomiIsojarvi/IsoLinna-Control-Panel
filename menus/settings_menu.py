from constants import *
from menus.sub_menu import SubMenu
from buttons.menu_button import MenuButton
from dialog_boxes.generate_uuid_dialog_box import GenerateUuidDialogBox
from dialog_boxes.time_interval_dialog_box import TimeIntervalDialogBox

#-------------------------------------------------------------------------------------------------#
#                                          SettingsMenu                                           #
#-------------------------------------------------------------------------------------------------#
class SettingsMenu(SubMenu):
    #---------------------------------------------------------------------------------------------#
    # Constructor                                                                                 #
    #---------------------------------------------------------------------------------------------#
    def __init__(self, owner, settings: dict):
        self.settings = settings
        self.owner = owner
        choices = [
            MenuButton("Generate new Device UUID", lambda *_: GenerateUuidDialogBox(self.owner)),
            MenuButton("Time Interval", lambda *_: TimeIntervalDialogBox(self.owner)),
            MenuButton("Back", self.back),
        ]

        super().__init__("Settings", choices, owner, SETTINGS_MENU_WIDTH , SETTINGS_MENU_HEIGHT)

    #---------------------------------------------------------------------------------------------#
    # back -                                                                                      #
    #---------------------------------------------------------------------------------------------#
    def back(self, *_args) -> None:
        if self.owner.top and self.owner.top.box_level > 1:
            # Go back one level (same as pressing ESC)
            self.owner.top.original_widget = self.owner.top.original_widget[0]
            self.owner.top.box_level -= 1