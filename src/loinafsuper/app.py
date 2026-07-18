"""
My first application
"""

import toga
from toga.style.pack import COLUMN, ROW, CENTER
from toga.style import Pack
from loinafsuper.keymaps import Keymaps
from loinafsuper.wallpaper import Wallpaper


class LoinafOSPanel(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        main_box = toga.Box(style=Pack(direction=COLUMN, text_align=CENTER, align_items=CENTER, margin=20))

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box

        keys_inst = Keymaps(self.main_window)
        wall_inst = Wallpaper(self.main_window)

        title = toga.Label(text="LoinafOS\nConfiguration", style=Pack(font_size=36, text_align=CENTER))

        keymap = toga.Button(text="Raccourcis clavier", style=Pack(text_align=CENTER, font_size=16, margin=10), on_press=keys_inst.draw)
        wallpaper = toga.Button(text="Fond d'écran", style=Pack(text_align=CENTER, font_size=16, margin=10), on_press=wall_inst.draw)
        keyboard = toga.Button(text="Langue et saisie", style=Pack(text_align=CENTER, font_size=16, margin=10))
        screens = toga.Button(text="Écrans", style=Pack(text_align=CENTER, font_size=16, margin=10))
        startup = toga.Button(text="Applications au démarrage", style=Pack(text_align=CENTER, font_size=16, margin=10))

        separator = toga.Divider(style=Pack(margin=20))

        update = toga.Button(text="LoinafOS Update", style=Pack(text_align=CENTER, font_size=16, background_color="#d380ff", margin=10))
        remove = toga.Button(text="Désinstaller LoinafOS", style=Pack(text_align=CENTER, font_size=16, background_color="#c90000", margin=10))

        main_box.add(title, keymap, wallpaper, keyboard, screens, startup, separator, update, remove)

        self.main_window.show()


def main():
    return LoinafOSPanel()
