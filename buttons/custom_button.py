import urwid

class CustomButton(urwid.Button):
    def __init__(self, label, on_press=None, align="center", wrap="any", user_data=None):
        super().__init__("")
        self._label = label  
        self._align = align
        self._wrap = wrap

        # Create a selectable text widget
        self.text = urwid.Text(label, align=self._align, wrap=self._wrap)

        # Add a bordered box
        self.border = urwid.LineBox(
                self.text,
                tlcorner=urwid.LineBox.Symbols.LIGHT.TOP_LEFT_ROUNDED,
                trcorner=urwid.LineBox.Symbols.LIGHT.TOP_RIGHT_ROUNDED,
                blcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_LEFT_ROUNDED,
                brcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_RIGHT_ROUNDED,
            )

        # Set the final widget to display
        self._w = self.border

        # Connect button click
        if on_press:
            urwid.connect_signal(self, "click", on_press, user_data)

    def get_label(self):
        return self._label

    def set_label(self, label):
        self._label = label
        self.text.set_text(label)

    label = property(get_label, set_label)  # Override label property

    def set_alignment(self, align):
        """Dynamically change text alignment"""
        self._align = align
        self.text.set_align_mode(align)

    def set_wrap_mode(self, wrap):
        """Dynamically change text wrapping"""
        self._wrap = wrap
        self.text.set_wrap_mode(wrap)

    def selectable(self):
        return True  # Allow focus

    def keypress(self, size, key):
        if key in ("enter", " "):
            self._emit("click")  # Trigger button click
        return key