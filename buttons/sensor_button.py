import urwid

#-------------------------------------------------------------------------------------------------#
#                                          SensorButton                                           #
#-------------------------------------------------------------------------------------------------#
class SensorButton(urwid.Button):

    #---------------------------------------------------------------------------------------------#
    # Constructor                                                                                 #
    #---------------------------------------------------------------------------------------------# 
    def __init__(self, caption, callback=None, selected: bool = False):
        # Initialize Button with empty label; we'll use SelectableIcon
        super().__init__("", on_press=self.toggle, user_data=caption)
        self.caption = caption
        self.callback = callback
        self.selected = selected


        # Create the selectable text
        self.icon = urwid.SelectableIcon(caption)

        # Set up the AttrMap for colors
        self.attr_map = urwid.AttrMap(
            self.icon,
            "sensor_selected" if self.selected else "button",
            focus_map={
                "button": "button_focused",
                "sensor_selected": "sensor_selected_focused",
            },
        )

        # Is the sensor selected?
        if self.selected:
            # Yes...
            self.attr_map.set_attr_map({None: "sensor_selected"})
            self.attr_map.set_focus_map({
                None: "sensor_selected_focused"
            })
        else:
            # No...
            self.attr_map.set_attr_map({None: "button"})
            self.attr_map.set_focus_map({
                None: "button_focused"
            })

        # Use the AttrMap as the widget urwid sees
        self._w = self.attr_map

    #---------------------------------------------------------------------------------------------#
    # toggle -                                                                                    #
    #---------------------------------------------------------------------------------------------# 
    def toggle(self, button, caption):
        # Toggle selection state
        self.selected = not self.selected

        if self.selected:
            self.attr_map.set_attr_map({None: "sensor_selected"})
            self.attr_map.set_focus_map({
                None: "sensor_selected_focused"
            })
        else:
            self.attr_map.set_attr_map({None: "button"})
            self.attr_map.set_focus_map({
                None: "button_focused"
            })

        # Call external callback if provided
        if self.callback:
            self.callback(self, caption)