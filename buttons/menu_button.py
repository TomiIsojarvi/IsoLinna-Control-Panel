import urwid

#-------------------------------------------------------------------------------------------------#
#                                           MenuButton                                            #
#-------------------------------------------------------------------------------------------------#
class MenuButton(urwid.Button):
    def __init__(self, caption, callback):
        super().__init__("", on_press=callback, user_data=caption)
        self._w = urwid.AttrMap(
            urwid.SelectableIcon(caption),
            "button",
            focus_map="button_focused",
        )