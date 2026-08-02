import toga, json

from toga import Window, style
from toga.style import Pack
from toga.style.pack import CENTER, COLUMN

from pathlib import Path

class Startup:
    def __init__(self, main_window:toga.MainWindow):
        self.main_window = main_window

        self.error = [False, None]

        self.main_box = toga.Box(style=Pack(margin=5, direction=COLUMN, align_items=CENTER))

        try:
            with open(Path("~/.config/hypr/settings/start.json").expanduser(), "r") as fichier:
                self.settings = json.load(fichier)
        except FileNotFoundError:
            self.settings = []
            try:
                with open(Path("~/.config/hypr/settings/start.json").expanduser(), "w") as fichier:
                    fichier.write(json.dumps(self.settings, indent=4))
            except PermissionError:
                print("Erreur critique: Le fichier de configuration des applications de démarrage n'a pu être ouvert et n'a u être crée. Vérifiez vos permissions puis réessayé")
                self.error = [True, "Le fichier de configuration des applications de démarrage n'a pu être ouvert et n'a u être crée. Vérifiez vos permissions puis réessayé"]
                return
            except Exception as E:
                print(f"Erreur critique: Une erreur non gérée est survenue lors de l'ouverture du fichier de configuration des applications au démarrage\nErreur: {E}")
                self.error = [True, f"Une erreur non gérée est survenue lors de l'ouverture du fichier de configuration des applications au démarrage\nErreur: {E}"]
                return
        except Exception as E:
            print(f"Erreur critique: Une erreur non gérée est survenue lors de l'ouverture du fichier de configuration des applications au démarrage\nErreur: {E}")
            self.error = [True, f"Une erreur non gérée est survenue lors de l'ouverture du fichier de configuration des applications au démarrage\nErreur: {E}"]
            return

        title = toga.Label("Applications au démarrage", style=Pack(font_size=28, text_align=CENTER, margin=10))

        self.ecran = toga.Table(
            columns=["Commande"],
            data = self.settings,
            style = Pack(font_size=12, flex=1),
            multiple_select=False,
            show_headings=True,
            on_select=self.change_focus
        )

        table_box = toga.Row(style=Pack(flex=1, align_items=CENTER))
        left_box = toga.Column(style=Pack(flex=1))
        right_box = toga.Column(style=Pack(justify_content=CENTER, align_items=CENTER))

        table_box.add(left_box, right_box)

        button_style = Pack(font_size=16, margin=10, text_align=CENTER)

        add_button = toga.Button("Ajouter", style=button_style, on_press=self.add_window)
        self.edit_button = toga.Button("Modifier", style=button_style, enabled=False, on_press=self.edit_window)
        self.del_button = toga.Button("Retirer", style=button_style, enabled=False, on_press=self.rem_command)

        right_box.add(add_button, self.edit_button, self.del_button)
        left_box.add(self.ecran)

        save_box = toga.Column(style=Pack(margin=10))
        save_button = toga.Button("Enregistrer", style=Pack(font_size=16, flex=1), on_press=self.apply_settings)

        save_box.add(save_button)

        self.main_box.add(title, table_box, save_box)

    def add_window(self, widget):
        self.window_add = toga.Window(title="Ajouter une commande")

        add_box = toga.Column(style=Pack(margin=10))

        title = toga.Label("Ajouter une commande", style=Pack(font_size=16, margin=10))

        entry_box = toga.Row(style=Pack(align_items=CENTER, margin=10))

        self.cmd_input = toga.TextInput(style=Pack(font_size=16, flex=1), placeholder="Commande", on_confirm=self.add_command)
        valid_button = toga.Button("Ajouter la commande", style=Pack(font_size=16, margin=10), on_press=self.add_command)

        entry_box.add(self.cmd_input, valid_button)

        add_box.add(title, entry_box)
        self.window_add.content = add_box
        self.window_add.show()

    def edit_window(self, widget):
        self.window_add = toga.Window(title="Editer une commande")

        add_box = toga.Column(style=Pack(margin=10))

        title = toga.Label("Editer une commande", style=Pack(font_size=16, margin=10))

        entry_box = toga.Row(style=Pack(align_items=CENTER, margin=10))

        self.cmd_input = toga.TextInput(style=Pack(font_size=16, flex=1), placeholder="Commande", on_confirm=self.edit_command, value=self.ecran.selection.commande)
        valid_button = toga.Button("Editer la commande", style=Pack(font_size=16, margin=10), on_press=self.edit_command)

        entry_box.add(self.cmd_input, valid_button)

        add_box.add(title, entry_box)
        self.window_add.content = add_box
        self.window_add.show()


    def add_command(self, widget):
        self.settings.append(self.cmd_input.value)
        self.ecran.data = self.settings
        self.main_box.refresh()
        self.window_add.close()
        self.edit_button.enabled = self.del_button.enabled = False

    def edit_command(self, widget):
        old_value = self.ecran.selection.commande

        for i in range(len(self.settings)):
            if self.settings[i] == old_value:
                self.settings[i] = self.cmd_input.value
                break

        self.ecran.data = self.settings
        self.main_box.refresh()
        self.window_add.close()

        self.edit_button.enabled = self.del_button.enabled = False

    def rem_command(self, widget):
        self.settings.remove(self.ecran.selection.commande)

        self.ecran.data = self.settings
        self.main_box.refresh()

        self.edit_button.enabled = self.del_button.enabled = False

    def change_focus(self, widget:toga.Table):
        self.edit_button.enabled = self.del_button.enabled = widget.selection != None
        self.main_box.refresh()

    async def apply_settings(self, widget):
        try:
            with open(Path("~/.config/hypr/settings/start.json").expanduser(), "w") as fichier:
                fichier.write(json.dumps(self.settings, indent=4))
        except Exception as E:
            error = toga.ErrorDialog("Erreur d'enregistrement", f"Une erreur est survenue lors de la tentative d'enregistrement de vos paramètres, aucune modification n'a été appliquée sur Hyprland!\nErreur:{E}")
            await self.main_window.dialog(error)
            return

        try:
            with open(Path("~/.config/hypr/start.lua").expanduser(), "w") as fichier:
                fichier.write("--Fichier de configuration généré automatiquement par le panneau de configuration LoinafOS\n\n\n")
                fichier.write("hl.on(\"hyprland.start\", function ()\n")
                for cmd in self.settings:
                    fichier.write(f"\thl.exec_cmd(\"{cmd}\")\n")
                fichier.write("end)")
        except Exception as E:
            error = toga.ErrorDialog("Erreur d'enregistrement",  f"Une erreur est survenue lors de la tentative d'enregistrement de vos paramètres, des modifications ont pu avoir été appliquées sur Hyprland!\nErreur:{E}")
            await self.main_window.dialog(error)
            return

        info = toga.InfoDialog("Configuration sauvegardé", "Vos paramètres ont été sauvegardés et s'appliqueront au prochain démarrage de LoinafOS")
        await self.main_window.dialog(info)


    async def draw(self, widget):
        if self.error[0]:
            error = toga.QuestionDialog("Erreur critique", self.error[1]+"\nVoulez-vous tentez de réinitialiser votre fichier de configuration?")
            response = await self.main_window.dialog(error)

            if response:
                try:
                    with open(Path("~/.config/hypr/settings/start.json").expanduser(), "w") as fichier:
                        fichier.write("[]")
                    info = toga.InfoDialog("Opération réussi", "Votre configuration a été réinitialisé, veuillez redémarrer ce panneau de configuration")
                    await self.main_window.dialog(info)
                except Exception as E:
                    print(f"Erreur critique de récupération: La récupération a échouée pour la raison suivante: {E}")
                    error = toga.ErrorDialog("Erreur critique lors de la tentative de réparation", f"Votre configuration n'a pu être réinitialisé pour la raison suivante: {E}")
                    await self.main_window.dialog(error)

            #self.main_window.close()
            return
        container = toga.ScrollContainer()

        container.content = self.main_box

        self.main_window.content = container
