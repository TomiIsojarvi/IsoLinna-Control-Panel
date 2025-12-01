import urwid
from collections.abc import Iterable

#-------------------------------------------------------------------------------------------------#
#                                              Menu                                               #
#-------------------------------------------------------------------------------------------------#
class Menu(urwid.LineBox):   
    def __init__(self, title: str, choices: Iterable[urwid.Widget]):
        body = [urwid.Divider(), *choices, urwid.Divider()]
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        padded = urwid.Padding(listbox, left=1, right=1)

        super().__init__( 
            padded,
            tlcorner=urwid.LineBox.Symbols.LIGHT.TOP_LEFT_ROUNDED,
            trcorner=urwid.LineBox.Symbols.LIGHT.TOP_RIGHT_ROUNDED,
            blcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_LEFT_ROUNDED,
            brcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_RIGHT_ROUNDED,
            title=title,
            title_align="left"
        )