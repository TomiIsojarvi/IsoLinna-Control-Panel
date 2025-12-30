from __future__ import annotations

import sys
import urwid

import globals
from buttons.custom_button import CustomButton

#-------------------------------------------------------------------------------------------------#
#                                           LoginScreen                                           #
#-------------------------------------------------------------------------------------------------#
class LoginScreen:
    palette = [
        ("body", "white", "black", "standout"),
        ("error", "light red", "black", "bold"),
        ("edit_caption", "dark gray", "black"),
        ("focus_edit_caption", "white", "black", "standout"),
        ("button", "dark gray", "black"),
        ("button_focused", "white,bold", "black", "bold"),
    ]

    #---------------------------------------------------------------------------------------------#
    # Constructor                                                                                 #
    #---------------------------------------------------------------------------------------------#
    def __init__(self, width: int, height: int) -> None:
        self.user = None

        # Set UI width and height; use relative sizing if invalid dimensions are given
        self.width = width
        if self.width <= 0:
            self.width = (urwid.RELATIVE, 80)
        self.height = height
        if self.height <= 0:
            self.height = (urwid.RELATIVE, 80)

        # Create a blank divider for spacing
        blank = urwid.Divider()

        # Header text prompting for email and password
        header_text = urwid.Pile([
            urwid.Text("Please enter your email address and password."),
            blank
        ])

        # Email input field
        self.email_edit = urwid.Edit("Email: ", "", wrap=urwid.CLIP)
        # Apply styles for normal and focus states
        email_edit_attr = urwid.AttrMap(self.email_edit, "edit_caption", "focus_edit_caption")

        # Password input field with masked input
        self.password_edit = urwid.Edit("Password: ", "", wrap=urwid.CLIP, mask="*")
        password_edit_attr = urwid.AttrMap(self.password_edit, "edit_caption", "focus_edit_caption")

        # Stack email and password fields vertically
        edits = urwid.Pile([email_edit_attr, password_edit_attr])

        # Create buttons for login and exit actions
        login_button = CustomButton("Log in", self.login_button_press)
        exit_button = CustomButton("Exit", self.exit_button_press)

        # Place buttons side by side with padding and alignment
        buttons = urwid.GridFlow([
            urwid.AttrMap(login_button, "button", "button_focused"), 
            urwid.AttrMap(exit_button, "button", "button_focused")
        ], 10, 3, 1, urwid.RIGHT)

        # Combine header, input fields, and buttons into a list-based layout
        body = urwid.ListBox(urwid.SimpleListWalker([header_text, edits, blank, buttons]))

        # Create a frame to hold the body (main content area)
        self.frame = urwid.Frame(body, focus_part="body")
        w = self.frame

        # Add padding around the frame
        w = urwid.Padding(w, urwid.LEFT, left=2, right=2)
        # Add top/bottom padding and vertical fill behavior
        w = urwid.Filler(w, urwid.TOP, urwid.RELATIVE_100, top=1, bottom=1)

        # Add a rounded border box with a title
        w = urwid.LineBox(
            w,
            title="IsoLinna Login",
            tlcorner=urwid.LineBox.Symbols.LIGHT.TOP_LEFT_ROUNDED,
            trcorner=urwid.LineBox.Symbols.LIGHT.TOP_RIGHT_ROUNDED,
            blcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_LEFT_ROUNDED,
            brcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_RIGHT_ROUNDED,
        )
        # Apply style to the entire box
        w = urwid.AttrMap(w, "body")

        # Center the whole layout horizontally and vertically
        w = urwid.Padding(w, urwid.CENTER, self.width)
        w = urwid.Filler(w, urwid.MIDDLE, self.height)

        # Save the final view for display
        self.view = w

        # Ensure focus starts in the body (input fields)
        self.frame.focus_position = "body"

    #---------------------------------------------------------------------------------------------#
    # show_error_box - Displays an Error Box                                                      #
    #---------------------------------------------------------------------------------------------#
    def show_error_box(self, message) -> None:
        # Save the current widget so we can restore it
        original_widget = self.loop.widget

        #---------------------------------------------------------------------#
        # on_ok_clicked -                                                     #
        #---------------------------------------------------------------------#
        def on_ok_clicked(button):
            self.loop.widget = original_widget  # Restore the original view
        #---------------------------------------------------------------------#

        # Create error message and OK button
        error_text = urwid.Text(('error', message), align='center')
        ok_button = CustomButton("OK", on_ok_clicked)
        ok_button = urwid.Padding(ok_button, align='center', width=10)

        # Stack message and button
        pile = urwid.Pile([error_text, urwid.Divider(), ok_button])
        filler = urwid.Filler(pile, valign='middle')

        # Create bordered box
        box = urwid.LineBox(
                filler,
                title="Login Error",
                tlcorner=urwid.LineBox.Symbols.LIGHT.TOP_LEFT_ROUNDED,
                trcorner=urwid.LineBox.Symbols.LIGHT.TOP_RIGHT_ROUNDED,
                blcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_LEFT_ROUNDED,
                brcorner=urwid.LineBox.Symbols.LIGHT.BOTTOM_RIGHT_ROUNDED,
            )

        # Overlay it on top of the original view
        overlay = urwid.Overlay(
            box, original_widget,
            align='center', width=('relative', 50),
            valign='middle', height=('relative', 30),
            min_width=20, min_height=5
        )

        self.loop.widget = overlay

    #---------------------------------------------------------------------------------------------#
    # login_button_press - The Login Button                                                       #
    #---------------------------------------------------------------------------------------------#
    def login_button_press(self, button) -> None:
        email = self.email_edit.edit_text
        password = self.password_edit.edit_text

        if email == "":
            self.show_error_box("Please enter your email address.")
        elif password == "":
            self.show_error_box("Please enter your password.")
        else:
            try:
                self.user = globals.auth.sign_in_with_email_and_password(email, password)
            except:
                self.show_error_box("Invalid email or password!")

            if self.user != None:
                raise urwid.ExitMainLoop()

    #---------------------------------------------------------------------------------------------#
    # exit_button_press - The Exit Button                                                         #
    #---------------------------------------------------------------------------------------------#
    def exit_button_press(self, button) -> None:
        sys.exit(0)
    
    #---------------------------------------------------------------------------------------------#
    # unhandled_key - Handles the keys that aren't normally supported                             #
    #---------------------------------------------------------------------------------------------#
    def unhandled_key(self, k: str) -> None:
        if k in ("q", "Q"):
            sys.exit(0)
    
    #---------------------------------------------------------------------------------------------#
    # main - Opens the screen and starts the rendering loop                                       #
    #---------------------------------------------------------------------------------------------#
    def main(self) -> dict:
        self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.unhandled_key)
        self.loop.run()
        return self.user