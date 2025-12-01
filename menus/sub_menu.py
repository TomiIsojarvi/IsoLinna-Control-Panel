from buttons.menu_button import MenuButton
from menus.menu import Menu

#-------------------------------------------------------------------------------------------------#
#                                             SubMenu                                             #
#-------------------------------------------------------------------------------------------------#
class SubMenu(MenuButton):

    #---------------------------------------------------------------------------------------------#
    # Constructor                                                                                 #
    #---------------------------------------------------------------------------------------------# 
    def __init__(self, caption, choices, owner, width, height):
        self._owner = owner
        self._width = width
        self._height = height
        self._contents = Menu(caption, choices)
        super().__init__(caption, self.open_menu)

    #---------------------------------------------------------------------------------------------#
    # open_menu -                                                                                 #
    #---------------------------------------------------------------------------------------------# 
    def open_menu(self, *_args) -> None:
        top = getattr(self._owner, "top", None)
        if top:
            top.open_box(self._contents, self._width, self._height)
