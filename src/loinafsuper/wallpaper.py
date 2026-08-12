from json import JSONDecodeError
import toga, subprocess, json, os

from toga.style import Pack
from toga.style.pack import CENTER, COLUMN, ROW, RIGHT

from pathlib import Path

def convert_bool(value) -> str:
    if value == True: return "true"
    else: return "false"

def run_command(cmd:list):
    if os.path.exists("/.flatpak-info"):
        cmd = ["flatpak-spawn", "--host"] + cmd
    else: print("!!! ENVIRONNEMENT FLATPAK NON DÉTÉCTÉ !!!")

    return subprocess.run(cmd, capture_output=True)


class Wallpaper:
    def __init__(self, main_window):

        self.panel_hypr = {
            "Contenir":"contain",
            "Couvrir":"cover",
            "Tuile":"till",
            "Remplir":"fill"
        }

        self.hypr_panel = {
            "contain": "Contenir",
            "cover": "Couvrir",
            "till": "Tuile",
            "fill":"Remplir"
        }

        self.main_window = main_window

        self.main_box = toga.Box(style=Pack(margin = 15, direction=COLUMN, align_items=CENTER))

        self.scroll_box = toga.ScrollContainer(content=self.main_box)
        try:
            with open(Path("~/.config/hypr/settings/wall.json").expanduser(), "r") as fichier:
                self.settings = json.load(fichier)
        except FileNotFoundError:
            try:
                with open(Path("~/.config/hypr/settings/wall.json").expanduser(), "w") as fichier:
                    self.settings = {
                        "general":{
                            "path": "~/.config/hypr/stras.jpg",
                            "is_directory": False,
                            "fit_mode": "cover",
                            "timeout": 30,
                            "recursive": False,
                            "order": False
                        },
                        "specs":{}
                    }
                    fichier.write(json.dumps(self.settings, indent=4))
            except PermissionError:
                print("Erreur critique: wall.json est introuvable et nous n'avons pas pu le créer. Vérifiez vos permissions")
                self.main_box.add(toga.Label("Erreur critique: wall.json est introuvable et nous n'avons pas pu le créer. Vérifiez vos permissions"))
                return
        except JSONDecodeError:
            print("Erreur critique: Impossible de charger vos paramètres d'écran en raison d'une erreur de décodage JSON. Une réinstallation de LoinafOS peut être nécessaire")
            self.main_box.add(toga.Label("Erreur critique: Impossible de charger vos paramètres d'écran en raison d'une erreur de décodage JSON. Une réinstallation de LoinafOS peut être nécessaire"))
            return
        except Exception as e:
            print(f"Une erreur inconnue s'est produite! Erreur : {e}!")
            self.main_box.add(toga.Label(f"Une erreur inconnue s'est produite! Erreur : {e}!"))
            return

        try:
            title = toga.Label("Configuration des fond d'écrans", style=Pack(font_size=26, text_align=CENTER))

            first_section = toga.Divider(style=Pack(margin=10))

            #Première section
            gen_title = toga.Label("Fonds d'écran par défaut", style=Pack(text_align=CENTER, font_size=26, margin=5))
            
            file_select = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin=5, justify_content=CENTER))
            self.file_path = toga.Label(self.settings["general"]["path"], style=Pack(font_size=12))
            image_select = toga.Button("Choisir une image", style=Pack(font_size=12), on_press=self.select_file)
            folder_select = toga.Button("Choisir un dossier d'images", style=Pack(font_size=12), on_press=self.select_folder)
            file_select.add(self.file_path, image_select, folder_select)
            
            self.recursive_switch = toga.Switch("Inclure les sous-dossier", style=Pack(font_size=16, text_align=CENTER, margin=5, justify_content=CENTER), value=self.settings["general"]["recursive"], enabled=self.settings["general"]["is_directory"], on_change=self.switch_recursive)

            #self.random_switch = toga.Switch("Randomiser l'ordre des images", style=Pack(font_size=16, text_align=CENTER, margin=5, justify_content=CENTER), value=self.settings["general"]["order"], enabled=self.settings["general"]["is_directory"], on_change=self.switch_random)

            fit_box = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin=5, justify_content=CENTER))
            fit_label = toga.Label("Méthode d'affichage:", style=Pack(font_size = 16, text_align=CENTER))
            fit_select = toga.Selection(items=[self.hypr_panel["contain"], self.hypr_panel["cover"], self.hypr_panel["till"], self.hypr_panel["fill"]], value=self.hypr_panel[self.settings["general"]["fit_mode"]], style=Pack(font_size=16), on_change=self.select_fit_mode)
            fit_box.add(fit_label, fit_select)

            timeout_box = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin=5, justify_content=CENTER))
            timeout_label = toga.Label("Délai entre chaque images(en secondes)", style=Pack(font_size=16, text_align=CENTER))
            self.timeout_input = toga.NumberInput(style=Pack(font_size = 16, text_align=CENTER), value=self.settings["general"]["timeout"], readonly=not(self.settings["general"]["is_directory"]), on_change=self.edit_timeout)
            timeout_box.add(timeout_label, self.timeout_input)

            last_section = toga.Divider(style=Pack(margin=10))

            #Deuxième section
            #On commence par chercher les différents écrans
            mnames = []

            out = run_command(["hyprctl", "monitors", "-j"])

            #print(out)

            rst = json.loads(out.stdout.decode('utf-8'))

            for m in rst:
                mnames.append(m["name"])

            spec_title = toga.Label("Configuration par écran", style=Pack(text_align=CENTER, font_size=26, margin=5))

            screen_box = toga.Box(style=Pack(direction=ROW, margin=5, text_align=CENTER, align_items=CENTER, justify_content=CENTER))
            screen_select = toga.Selection(items=mnames, style=Pack(font_size=16), on_change=self.select_spec)
            self.spec_activ = toga.Switch("Appliquer pour cet écran", value=False, enabled=True, style=Pack(font_size=16, text_align=RIGHT), on_change=self.switch_screen)
            screen_box.add(screen_select, self.spec_activ)

            self.spec_box = toga.Column()

            self.select_spec(screen_select)

            #Fin

            end = toga.Divider(style=Pack(margin=10))

            apply_button = toga.Button(text="Appliquer", style=Pack(font_size=20, text_align=CENTER, margin=10), on_press=self.apply_settings)

            self.main_box.add(title, first_section, gen_title, file_select, self.recursive_switch, fit_box, timeout_box, last_section, spec_title, screen_box, self.spec_box, end, apply_button)

        except Exception as e:
            print(f"Erreur critique: Vos paramètres sont corrompus! Nous vous invitons à inspecter le fichier ~/.config/hypr/settings/wall.json puis à redémarrer ce panel!\nErreur : {e}")
            self.main_box = toga.Box()
            self.scroll_box.content = self.main_box
            self.main_box.add(toga.Label(f"Erreur critique: Vos paramètres sont corrompus! Nous vous invitons à inspecter le fichier ~/.config/hypr/settings/wall.json puis à redémarrer ce panel!\nErreur : {e}"))
            return

    async def select_file(self, widget):
        file_select = toga.OpenFileDialog("Choisir une image")
        file_path = await self.main_window.dialog(file_select)

        if file_path != None:
            #print(str(file_path))
            self.settings["general"]["is_directory"] = False
            self.settings["general"]["path"] = str(file_path)
            self.file_path.text = str(file_path)
            self.recursive_switch.enabled = False
            self.random_switch.enabled = False
            self.timeout_input.readonly = True

            #self.file_path.refresh()
            self.main_box.refresh()

    async def select_folder(self, widget):
        folder_select = toga.SelectFolderDialog("Choisir un dossier")
        folder_path = await self.main_window.dialog(folder_select)

        if folder_path != None:
            self.settings["general"]["path"] = str(folder_path)
            self.settings["general"]["is_directory"] = True
            self.file_path.text = str(folder_path)
            self.recursive_switch.enabled = True
            self.random_switch.enabled = True
            self.timeout_input.readonly = False

            self.main_box.refresh()

    def switch_recursive(self, widget):
        self.settings["general"]["recursive"] = widget.value
        print(widget.value)

    def switch_random(self, widget):
        self.settings["general"]["order"] = widget.value

    def select_fit_mode (self, widget):
        self.settings["general"]["fit_mode"] = self.panel_hypr[widget.value]

    def edit_timeout(self, widget):
        self.settings["general"]["timeout"] = int(widget.value)

    async def select_file_spec(self, widget):
        file_select = toga.OpenFileDialog("Choisir une image")
        file_path = await self.main_window.dialog(file_select)

        if file_path != None:
            #print(str(file_path))
            spec = self.settings["specs"][self.monitor]
            spec["is_directory"] = False
            spec["path"] = str(file_path)
            self.file_path_spec.text = str(file_path)
            self.recursive_switch_spec.enabled = False
            self.random_switch_spec.enabled = False
            self.timeout_input_spec.readonly = True

            #self.file_path.refresh()
            self.main_box.refresh()

    async def select_folder_spec(self, widget):
        folder_select = toga.SelectFolderDialog("Choisir un dossier")
        folder_path = await self.main_window.dialog(folder_select)

        if folder_path != None:
            spec = self.settings["specs"][self.monitor]
            spec["path"] = str(folder_path)
            spec["is_directory"] = True
            self.file_path_spec.text = str(folder_path)
            self.recursive_switch_spec.enabled = True
            self.random_switch_spec.enabled = True
            self.timeout_input_spec.readonly = False

            self.main_box.refresh()

    def switch_recursive_spec(self, widget):
        self.settings["specs"][self.monitor]["recursive"] = widget.value

    def switch_random_spec(self, widget):
        self.settings["specs"][self.monitor]["order"] = widget.value

    def select_fit_mode_spec (self, widget):
        self.settings["specs"][self.monitor]["fit_mode"] = self.panel_hypr[widget.value]

    def edit_timeout_spec(self, widget):
        self.settings["specs"][self.monitor]["timeout"] = int(widget.value)


    def select_spec(self, widget):
        self.monitor = widget.value

        children = self.spec_box.children

        for child in children:
            self.spec_box.remove(child)

        try:
            spec = self.settings["specs"][self.monitor]
        except KeyError:
            spec = self.settings["specs"][self.monitor] = {
                "path": "~/.config/hypr/stras.jpg",
                "is_directory": False,
                "fit_mode": "cover",
                "timeout": 30,
                "recursive": False,
                "order": False,
                "active": False
            }

        self.spec_activ.value = spec["active"]

        file_select = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin=5, justify_content=CENTER))
        self.file_path_spec = toga.Label(spec["path"], style=Pack(font_size=12))
        image_select = toga.Button("Choisir une image", style=Pack(font_size=12), on_press=self.select_file_spec)
        folder_select = toga.Button("Choisir un dossier d'images", style=Pack(font_size=12), on_press=self.select_folder_spec)
        file_select.add(self.file_path_spec, image_select, folder_select)
        self.recursive_switch_spec = toga.Switch("Inclure les sous-dossier", style=Pack(font_size=16, text_align=CENTER, margin=5, justify_content=CENTER), value=spec["recursive"], enabled=spec["is_directory"], on_change=self.switch_recursive_spec)

        #self.random_switch_spec = toga.Switch("Randomiser l'ordre des images", style=Pack(font_size=16, text_align=CENTER, margin=5, justify_content=CENTER), value=spec["order"], enabled=spec["is_directory"], on_change=self.switch_random_spec)

        fit_box = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin=5, justify_content=CENTER))
        fit_label = toga.Label("Méthode d'affichage:", style=Pack(font_size = 16, text_align=CENTER))
        fit_select = toga.Selection(items=[self.hypr_panel["contain"], self.hypr_panel["cover"], self.hypr_panel["till"], self.hypr_panel["fill"]], value=self.hypr_panel[spec["fit_mode"]], style=Pack(font_size=16), on_change=self.select_fit_mode_spec)
        fit_box.add(fit_label, fit_select)

        timeout_box = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin=5, justify_content=CENTER))
        timeout_label = toga.Label("Délai entre chaque images(en secondes)", style=Pack(font_size=16, text_align=CENTER))
        self.timeout_input_spec = toga.NumberInput(style=Pack(font_size = 16, text_align=CENTER), value=spec["timeout"], readonly=not(spec["is_directory"]), on_change=self.edit_timeout_spec)
        timeout_box.add(timeout_label, self.timeout_input_spec)

        self.spec_box.add(file_select, self.recursive_switch_spec, fit_box, timeout_box)

        self.main_box.refresh()


    async def apply_settings(self, widget):
        with open(Path("~/.config/hypr/settings/wall.json").expanduser(), "w") as fichier:
            fichier.write(json.dumps(self.settings, indent=4))

        with open(Path("~/.config/hypr/hyprpaper.conf").expanduser(), "w") as fichier:
            fichier.write("#FICHIER GÉNÉRÉ AUTOMATIQUEMENT grâce au panneau de configuration LoinafOS\n\n\n")

            for spec_name in self.settings["specs"]:
                spec = self.settings["specs"][spec_name]
                if spec["active"]:
                    fichier.write(
                        "wallpaper {\n"
                        "\tmonitor = " + spec_name +"\n"
                        "\tpath = " + spec["path"]+"\n"
                        "\tfit_mode = " + spec["fit_mode"] + "\n"
                        "\ttimeout = " + str(spec["timeout"]) + "\n"
                        "\trecursive = " + convert_bool(spec["recursive"]) + "\n"
                    )
                    #if spec["order"]: fichier.write("\torder = random\n")
                    fichier.write("}\n\n")

            fichier.write(
                "wallpaper {\n"
                "\tmonitor = \n"
                "\tpath = " + self.settings["general"]["path"]+"\n"
                "\tfit_mode = " + self.settings["general"]["fit_mode"] + "\n"
                "\ttimeout = " + str(self.settings["general"]["timeout"]) + "\n"
                "\trecursive = " + convert_bool(self.settings["general"]["recursive"]) + "\n"
            )
            #if self.settings["general"]["order"]: fichier.write("\torder = random\n")
            fichier.write("}\n\n")
            
            #Désactivé car entraine des problèmes de processus parents/enfants avec le panel
            #os.system("killall hyprpaper && hyprpaper & disown")

            info = toga.InfoDialog("Modification appliquée", "Vos paramètres ont été enregistrés! Redémarrer hyprpaper pour appliquer les modifications!")
            await self.main_window.dialog(info)

    def switch_screen(self, widget):
        self.settings["specs"][self.monitor]["active"] = widget.value

    def draw(self, widget):
        self.main_window.content = self.scroll_box

        self.main_window.show()

if __name__ == "__main__":
    print(convert_bool(True))
    print(convert_bool(False))
