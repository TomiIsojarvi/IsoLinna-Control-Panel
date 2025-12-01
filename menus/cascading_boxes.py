import urwid
from constants import *

#-------------------------------------------------------------------------------------------------#
#                                         CascadingBoxes                                          #
#-------------------------------------------------------------------------------------------------#
class CascadingBoxes(urwid.WidgetPlaceholder):

    # Maximum number of stacked boxes allowed
    max_box_levels = 4

    #---------------------------------------------------------------------------------------------#
    # Constructor                                                                                 #
    #---------------------------------------------------------------------------------------------# 
    def __init__(self, box: urwid.Widget) -> None:
        global MAIN_MENU_WIDTH, MAIN_MENU_HEIGHT

        # Initialize the base WidgetPlaceholder with a blank fill
        super().__init__(urwid.SolidFill(" "))

        # Tracks the current number of stacked boxes
        self.box_level = 0

        # Open the initial box (main menu) with specified width and height
        self.open_box(box, MAIN_MENU_WIDTH, MAIN_MENU_HEIGHT)

    #---------------------------------------------------------------------------------------------#
    # open_box - Overlay a new box on top of the current widget stack.                            #
    #---------------------------------------------------------------------------------------------# 
    def open_box(self, box: urwid.Widget, width: int | None = None, height: int | None = None) -> None:

        # Create an Overlay widget: box on top of the existing original_widget
        self.original_widget = urwid.Overlay(
            box,                         # New box to display
            self.original_widget,        # Widget underneath (current stack)
            align=urwid.LEFT,            # Horizontal alignment of overlay
            width=width if width is not None else ('relative', 80),   # Width of new box
            valign=urwid.TOP,            # Vertical alignment of overlay
            height=height if height is not None else ('relative', 80),# Height of new box
            min_width=24,                # Minimum width of box
            min_height=8,                # Minimum height of box
            # Horizontal and vertical offsets for stacked boxes
            left=self.box_level * 3,
            right=(self.max_box_levels - self.box_level - 1) * 3,
            top=self.box_level * 2,
            bottom=(self.max_box_levels - self.box_level - 1) * 2,
        )

        # Increment the box level since a new box is stacked
        self.box_level += 1

    #---------------------------------------------------------------------------------------------#
    # keypress - Handle keypress events.                                                          #
    #---------------------------------------------------------------------------------------------# 
    def keypress(self, size, key: str) -> str | None:
        # If ESC key pressed and more than one box is stacked
        if key == "esc" and self.box_level > 1:
            # Remove the topmost box by reverting to the widget underneath
            self.original_widget = self.original_widget[0]

            # Decrement box level
            self.box_level -= 1

            # Key has been handled
            return None

        # For all other keys, delegate handling to the current widget
        return super().keypress(size, key)