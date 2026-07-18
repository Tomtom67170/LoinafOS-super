import toga, json, os

from toga.style.pack import CENTER, COLUMN, ROW
from toga.style import Pack

from pathlib import Path

class Keymaps:
    def __init__(self, main_window:toga.MainWindow):
        self.main_box = toga.Box(style=Pack(direction=COLUMN, margin=20))
        self.main_window = main_window

        try:
            with open(Path("~/.config/hypr/keys.json").expanduser(), "r") as fichier:
                keys = json.load(fichier)
        except FileNotFoundError:
            print("Erreur critique: keys.json est introuvable! Il est recommandé de réinstaller LoinafOS!")
            self.main_box.add(toga.Label(text="Erreur critique: keys.json est introuvable! Il est recommandé de réinstaller LoinafOS!"))
            return

        table_data = []

        for row in keys:
            #print(row)
            table_data.append((row["Touches"], row["Commande"], row["Description"]))

        data = toga.Table(
            columns=["Touches", "Commande", "Description"],
            data = table_data,
            style=Pack(flex=1)
        )

        titre = toga.Label(text="Combinaisons", style=Pack(font_size=28, text_align=CENTER))

        edit = toga.Button(text="Modifier", style=Pack(font_size=16, text_align=CENTER), on_press=self.edit)

        self.main_box.add(titre, data, edit)

    def draw(self, widget):
        self.main_window.content = self.main_box

        self.main_window.content.refresh()

        new_size = self.main_window.content.layout

        self.main_window.size = (new_size.width + 40, new_size.height + 40)

        self.main_window.show()

    async def edit(self, widget):
        await self.main_window.dialog(toga.InfoDialog("Modifier les combinaisons de touches", "Pour modifier les combinaisons de touches, vous êtes invités à modifier manuellement le fichier de configuration des combinaisons de touches dans ~/.config/hypr/keymaps.lua. Vous pourrez ensuite les réferencer dans ~/.config/hypr/keys.json afin qu'ils apparaissent dans cette fenêtre!\nPour la syntaxe Lua Hyprland pour créer vos propres combinsaisons, consultez la documentation officielle: https://wiki.hypr.land/Configuring/Basics/Binds/"))

        os.system("kitty nvim ~/.config/hypr/keymaps.lua")

        os.system("kitty nvim ~/.config/hypr/keys.json")

if __name__ == "__main__":
    main_window = toga.MainWindow(title="LoinafOS Panel")

    keys = Keymaps(main_window)

    keys.draw()
