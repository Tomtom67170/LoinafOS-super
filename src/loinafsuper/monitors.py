import toga, subprocess, json, os

from toga.style.pack import CENTER
from toga.style import Pack
#from decimal import Decimal

from pathlib import Path

def convert_hypr_label(s:str):
    if s == "preferred": return "Meilleure résolution et taux de rafraichissement"
    if s == "highres": return "Plus haute résolution"
    if s == "highrr": return "Plus haut taux de rafraichissement"
    if s == "maxwidth": return "Plus grande largeur"
    else: return s

def check_scale(s:str):
    try:
        valid = float(s)
        if valid < 0.3:
            return "Valeur inférieur à 0.3"
    except ValueError:
        return "Nombre décimal invalide"

def check_sdr(s:str):
    try:
        valid = float(s)
        if valid < 1.0 or valid > 2.0:
            return "Valeur inférieur à 1.0 ou supérieur à 2.0"
    except ValueError:
        return "Nombre décimal invalide"

def check_sdr_float(s:str):
    try:
        valid = float(s)
        if valid < 0 or valid > 100:
            return "Valeur négative ou supérieure à 100"
    except ValueError:
        return "Nombre décimal invalide"

def check_sdr_int(s:str):
    try:
        valid = int(s)
        if valid < 0 or valid > 100:
            return "Valeur négative ou supérieure à 100"
    except ValueError:
                return "Nombre entier invalide"

def check_hdr_float(s:str):
    try:
        valid = float(s)
        if (valid < 0 and valid != -1) or valid > 100:
            return "Valeur négative ou supérieure à 100"
    except ValueError:
        return "Nombre décimal invalide"

def check_hdr_int(s:str):
    try:
        valid = int(s)
        if (valid < 0 and valid != -1) or valid > 100:
            return "Valeur négative ou supérieure à 100"
    except ValueError:
        return "Nombre entier invalide"

def run_command(cmd:list):
    if os.path.exists("/.flatpak-info"):
        cmd = ["flatpak-spawn", "--host"] + cmd
    else: print("!!! ENVIRONNEMENT FLATPAK NON DÉTÉCTÉ !!!")

    return subprocess.run(cmd, capture_output=True)


class Monitors:
    def __init__(self, main_window):
        self.main_window = main_window

        self.error = [False]

        self.monitors = []

        self.main_box = toga.Column(style=Pack(align_items=CENTER, margin=5))

        out = run_command(["hyprctl", "monitors", "-j"])

        #print(out)#.stdout.decode('utf-8'))
        rst = json.loads(out.stdout.decode('utf-8'))
        for m in rst:
            self.monitors.append([m["description"] + " ("+m["name"]+")", m["description"], m["availableModes"]])

        try:
            with open(Path("~/.config/hypr/settings/mon.json").expanduser(), "r") as fichier:
                self.settings = json.load(fichier)
        except FileNotFoundError:
            try:
                with open(Path("~/.config/hypr/settings/mon.json").expanduser(), "w") as fichier:
                    self.settings = {}
                    fichier.write(json.dumps(self.settings, indent=4))
            except PermissionError:
                error = toga.Label("Erreur critique: Nous n'avons pas pu accéder à vos paramètres en raison d'une erreur de lecture et nous n'avons pas pu les créer. Vérifiez vos permissions")
                print("Erreur critique: Nous n'avons pas pu accéder à vos paramètres en raison d'une erreur de lecture et nous n'avons pas pu les créer. Vérifiez vos permissions")
                self.main_box.add(error)
            except Exception as E:
                error = toga.Label(f"Erreur critique: Une erreur non gérée s'est produite\nErreur: {E}")
                print(f"Erreur critique: Une erreur non gérée s'est produite\nErreur: {E}")
                self.main_box.add(error)
                return
        except Exception as E:
            self.error = [True, E]
            print(f"Une erreur est survenue et une intervention est requise: {E}")

        title = toga.Label("Réglage écran", style=Pack(font_size=26, text_align=CENTER))
        data = []
        for x in self.monitors:
            data.append(x[0])

        for screen in self.settings:
            if screen not in data: data.append(screen+" (Inactif)")
        self.screen_select = toga.Table(style=Pack(font_size=16, text_align=CENTER), data=data, multiple_select=False, show_headings=True, on_select=self.select_spec, columns=["Écran"], headings=None)

        self.spec_box = toga.Column(style=Pack(align_items=CENTER))

        self.main_box.add(title, self.screen_select, self.spec_box)

    def select_spec(self, widget:toga.Table):

        self.main_box.remove(self.spec_box)

        self.spec_box = toga.Column(style=Pack(align_items=CENTER))

        self.monitor = widget.selection.écran.replace(" (Inactif)", "")

        try:
            setting = self.settings[self.monitor]
        except KeyError:
            setting = self.settings[self.monitor] = {
                "desc": mon[1],
                "mode": "preferred",
                "position": [True, 0],
                "scale": 1.0,
                "disabled": False,
                "transform": 0,
                "mirror": None,
                "bitdepht": False,
                "cm": "srgb",
                "sdr_eotf": "default",
                "sdrbrightness": 1.0,
                "sdrsaturation": 1.0,
                "vrr": 0,
                "icc": None,
                "reserved_area": 0,
                "supports_wide_color": 0,
                "supports_hdr": 0,
                "sdr_min_luminance": 0.2,
                "sdr_max_luminance": 80,
                "min_luminance": -1,
                "max_luminance": -1,
                "max_avg_luminance": -1
            }

        apply_button = toga.Button("Valider les changements", style=Pack(font_size=16, margin=5), on_press=self.apply_change)

        res_box = toga.Row(style=Pack(margin=5, justify_content=CENTER, align_items=CENTER))
        res_text = toga.Label("Résolution", style=Pack(font_size=16, text_align=CENTER))
        res_data = []
        for mon in self.monitors:
            if mon[0] == self.monitor:
                res_data = mon[2]
        try:
            res_select = toga.Selection(style=Pack(font_size=16), items=["Meilleure résolution et taux de rafraichissement", "Plus haute résolution", "Plus haut taux de rafraichissement", "Plus grande largeur"] + res_data, value=convert_hypr_label(setting["mode"]), on_change=self.change_res)
        except ValueError:
            setting["mode"] = "preferred"
            res_select = toga.Selection(style=Pack(font_size=16), items=["Meilleure résolution et taux de rafraichissement", "Plus haute résolution", "Plus haut taux de rafraichissement", "Plus grande largeur"] + res_data, value=convert_hypr_label(setting["mode"]), on_change=self.change_res)
        res_box.add(res_text, res_select)

        pos_title = toga.Label("Position de l'écran par rapport au précédent", style=Pack(font_size=16, text_align=CENTER, margin=(5, 5, 0)))

        pos_box = toga.Row(style=Pack(margin=(0,5,5), justify_content=CENTER, align_items=CENTER))
        pos_text = toga.Switch("Position automatique", style=Pack(font_size=16, text_align=CENTER), value=setting["position"], on_change=self.change_auto_pos)
        pos_choice = [
            {"name":"Gauche", "value":"left"},
            {"name":"Droite", "value":"right"},
            {"name":"Bas", "value":"down"},
            {"name":"Haut", "value":"up"}
        ]
        self.pos_select = toga.Selection(style=Pack(font_size=16), items = pos_choice, accessor="name", enabled=not(setting["position"][0]), on_change=self.change_pos)
        self.pos_select.value = self.pos_select.items[setting["position"][1]]
        pos_box.add(pos_text, self.pos_select)

        scale_box = toga.Row(style=Pack(margin=5, justify_content=CENTER, align_items=CENTER))
        scale_text = toga.Label("Mise à l'échelle", style=Pack(font_size=16, text_align=CENTER))
        scale_input = toga.TextInput(style=Pack(font_size=16), placeholder="1.0", validators=[check_scale], value=setting["scale"], on_change=self.change_scale)
        #scale_input.value = setting["scale"]
        #print(scale_input.value)
        #scale_input.on_change=self.change_scale
        scale_box.add(scale_text, scale_input)

        disable_switch = toga.Switch("Désactiver l'écran", style=Pack(font_size=16), value=setting["disabled"], on_change=self.disable_screen)

        transform_box = toga.Row(style=Pack(margin=5, justify_content=CENTER, align_items=CENTER))
        transform_text = toga.Label("Orientation", style=Pack(font_size=16, text_align=CENTER))
        transform_choice = [
            {"name": "Paysage", "value":0},
            {"name": "Portrait", "value":1},
            {"name": "Paysage (inversé)", "value":2},
            {"name": "Portrait (inversé)", "value":3},
            {"name": "Paysage (mirroir)", "value": 4},
            {"name": "Portrait (mirroir)", "value": 5},
            {"name": "Paysage (inversé et mirroir)", "value":6},
            {"name": "Portrait (inversé et mirroir)", "value":7}
        ]
        transform_select = toga.Selection(style=Pack(font_size=16), items=transform_choice, accessor="name", on_change=self.change_transform)
        transform_select.value = transform_select.items[setting["transform"]]
        transform_box.add(transform_text, transform_select)

        mirror_box = toga.Row(style=Pack(margin=5, align_items=CENTER, justify_content=CENTER))
        mirror_switch = toga.Switch("Écran duppliqué", style=Pack(font_size=16), value=setting["mirror"] != None, on_change=self.change_mirror_state)
        mirror_list = []
        for x in self.monitors:
            if x[0] != self.monitor:
                mirror_list.append(x[1])
        self.mirror_select = toga.Selection(style=Pack(font_size=16), items=mirror_list, value=setting["mirror"], enabled=setting["mirror"] != None, on_change=self.change_mirror)
        mirror_box.add(mirror_switch, self.mirror_select)

        more_setting = toga.Button("Options avancées", style=Pack(font_size = 16, text_align=CENTER), on_press=self.show_more)

        #OPTIONS AVANCÉES

        bitdepht_switch = toga.Switch("Profondeur des couleurs améliorés", style=Pack(font_size=16, margin=5), value=setting["bitdepht"], on_change=self.change_bitdepht)

        cm_box = toga.Row(style=Pack(margin=5, align_items=CENTER, justify_content=CENTER))
        cm_text = toga.Label("Color Management", style=Pack(text_align=CENTER, font_size=16))
        cm_select = toga.Selection(style=Pack(font_size=16), items=["srgb", "wide", "dcip3", "adobe", "hdr"], value=setting["cm"], on_change=self.change_cm)
        cm_box.add(cm_text, cm_select)

        eotf_box = toga.Row(style=Pack(margin=5, align_items=CENTER, justify_content=CENTER))
        eotf_text = toga.Label("Fonction de transfert", style=Pack(text_align=CENTER, font_size=16))
        eotf_select = toga.Selection(style=Pack(font_size=16), items=["default", "gamma22", "srgb"], value=setting["sdr_eotf"], on_change=self.change_eotf)
        eotf_box.add(eotf_text, eotf_select)

        sdrbright_box = toga.Row(style=Pack(margin=5, align_items=CENTER, justify_content=CENTER))
        sdrbright_text = toga.Label("Luminosité sur les éléments SDR (écran HDR uniquement)", style=Pack(text_align=CENTER, font_size=16))
        sdrbright_select = toga.TextInput(style=Pack(font_size=16), value=setting["sdrbrightness"], on_change=self.change_sdrbright, validators=[check_sdr])
        #print(sdrbright_select.value)
        sdrbright_box.add(sdrbright_text, sdrbright_select)

        sdrsat_box = toga.Row(style=Pack(margin=5, align_items=CENTER, justify_content=CENTER))
        sdrsat_text = toga.Label("Saturation sur les éléments SDR (écran HDR uniquement)", style=Pack(text_align=CENTER, font_size=16))
        sdrsat_select = toga.TextInput(style=Pack(font_size=16), value=setting["sdrsaturation"], on_change=self.change_sdrsat, validators=[check_sdr])
        sdrsat_box.add(sdrsat_text, sdrsat_select)

        vrr_box = toga.Row(style=Pack(margin=5, align_items=CENTER, justify_content=CENTER))
        vrr_text = toga.Label("Fonction de transfert", style=Pack(text_align=CENTER, font_size=16))
        vrr_options = ["Désactivé", "Activé", "Uniquement si application en plein écran"]
        vrr_select = toga.Selection(style=Pack(font_size=16), items=vrr_options, value=vrr_options[setting["vrr"]], on_change=self.change_vrr)
        vrr_box.add(vrr_text, vrr_select)

        icc_box = toga.Row(style=Pack(margin=5, align_items=CENTER, justify_content=CENTER))
        self.icc_text = toga.Label(""+str(setting["icc"]), style=Pack(text_align=CENTER, font_size=16))
        icc_select = toga.Button("Choisir un fichier", style=Pack(font_size=16), on_press=self.change_icc)
        icc_box.add(self.icc_text, icc_select)

        area_box = toga.Row(style=Pack(margin=5, align_items=CENTER, justify_content=CENTER))
        area_text = toga.Label("reserved_area = ", style=Pack(text_align=CENTER, font_size=16))
        area_select = toga.TextInput(style=Pack(font_size=16), value=str(setting["reserved_area"]), placeholder="Consulter documentation pour en savoir plus!", on_change=self.change_area)
        area_box.add(area_text, area_select)

        wide_box = toga.Row(style=Pack(margin=5, align_items=CENTER, justify_content=CENTER))
        wide_text = toga.Label("Forcer large gamme de couleur", style=Pack(text_align=CENTER, font_size=16))
        wide_options = ["Désactivé", "Automatique", "Activé"]
        wide_select = toga.Selection(style=Pack(font_size=16), items=wide_options, value=wide_options[setting["supports_wide_color"]], on_change=self.change_wide)
        wide_box.add(wide_text, wide_select)

        hdr_box = toga.Row(style=Pack(margin=5, align_items=CENTER, justify_content=CENTER))
        hdr_text = toga.Label("Forcer HDR", style=Pack(text_align=CENTER, font_size=16))
        hdr_options = ["Désactivé", "Automatique", "Activé"]
        hdr_select = toga.Selection(style=Pack(font_size=16), items=hdr_options, value=hdr_options[setting["supports_hdr"]], on_change=self.change_hdr)
        hdr_box.add(hdr_text, hdr_select)

        sdrlum_box = toga.Row(style=Pack(margin=5, align_items=CENTER, justify_content=CENTER))
        sdrlum_text = toga.Label("Luminosité des contenus SDR sur écran HDR comprise entre ", style=Pack(text_align=CENTER, font_size=16))
        sdrlum_select1 = toga.TextInput(style=Pack(font_size=16), value=setting["sdr_min_luminance"], on_change=self.change_sdr_min, validators=[check_sdr_float])
        sdrlum_and = toga.Label(" et ", style=Pack(font_size=16))
        sdrlum_select2 = toga.TextInput(style=Pack(font_size=16), value=setting["sdr_max_luminance"], on_change=self.change_sdr_max, validators=[check_sdr_int])
        sdrlum_box.add(sdrlum_text, sdrlum_select1, sdrlum_and, sdrlum_select2)

        hdrlum_box = toga.Row(style=Pack(margin=(5,5,0), align_items=CENTER, justify_content=CENTER))
        hdrlum_text = toga.Label("Luminosité physique écran HDR comprise entre (-1 pour automatique)", style=Pack(text_align=CENTER, font_size=16))
        hdrlum_select1 = toga.TextInput(style=Pack(font_size=16), value=setting["min_luminance"], on_change=self.change_min_luminance, validators=[check_hdr_float])
        hdrlum_and = toga.Label(" et ", style=Pack(font_size=16))
        hdrlum_select2 = toga.TextInput(style=Pack(font_size=16), value=setting["max_luminance"], on_change=self.change_max_luminance, validators=[check_hdr_int])
        hdrlum_box.add(hdrlum_text, hdrlum_select1, hdrlum_and, hdrlum_select2)

        avglum_box = toga.Row(style=Pack(margin=(0,5,5), align_items=CENTER, justify_content=CENTER))
        avglum_text = toga.Label("Luminosité physique moyenne maximum (-1 pour automatique)", style=Pack(text_align=CENTER, font_size=16))
        avglum_select = toga.TextInput(style=Pack(font_size=16), value=setting["max_avg_luminance"], on_change=self.change_avg_luminance, validators=[check_hdr_int])
        avglum_box.add(avglum_text, avglum_select)

        self.advanced_box = toga.Column(style=Pack(align_items=CENTER))
        self.advanced_box.add(bitdepht_switch, cm_box, eotf_box, sdrbright_box, sdrsat_box, vrr_box, icc_box, area_box, wide_box, hdr_box, sdrlum_box, hdrlum_box, avglum_box)

        self.spec_box.add(apply_button, res_box, pos_title, pos_box, scale_box, disable_switch, transform_box, mirror_box, more_setting)

        self.main_box.add(self.spec_box)
        self.main_box.refresh()

    def change_res(self, widget):
        setting = self.settings[self.monitor]
        if widget.value == "Meilleure résolution et taux de rafraichissement": setting["mode"] = "preferred"
        elif widget.value == "Plus haute résolution": setting["mode"] = "highres"
        elif widget.value == "Plus haut taux de rafraichissement": setting["mode"] = "highrr"
        elif widget.value == "Plus grande largeur": setting["mode"] = "maxwidth"
        else: setting["mode"] = widget.value

    def change_auto_pos(self, widget):
        #print("Salut")
        setting = self.settings[self.monitor]
        setting["position"][0] = widget.value
        self.pos_select.enabled = not(widget.value)
        self.main_box.refresh()

    def change_pos(self, widget):
        #print(widget.value.value)
        self.settings[self.monitor][1] = widget.value.value

    def change_scale(self, widget):
        if widget.value != None: self.settings[self.monitor]["scale"] = widget.value
        else: print("erreur")

    def disable_screen(self, widget):
        self.settings[self.monitor]["disabled"] = widget.value

    def change_transform(self, widget):
        self.settings[self.monitor]["transform"] = widget.value.value

    async def change_mirror_state(self, widget):
        if len(self.mirror_select.items) == 0 and widget.value:
            error = toga.InfoDialog("Écran manquant", "Pour modifier ce paramètre, assurez-vous d'avoir connecté au moins 2 écrans à votre appareil, puis redémarrer le panneau de configuration")
            await self.main_window.dialog(error)
            widget.value = False
            return
        if widget.value: self.settings[self.monitor]["mirror"] = self.mirror_select.value
        else: self.settings[self.monitor]["mirror"] = None
        self.mirror_select.enabled = widget.value

    def change_mirror(self, widget):
        self.settings[self.monitor]["mirror"] = widget.value

    async def show_more(self, widget):
        info = toga.QuestionDialog("Paramètres avancées", "Vous êtes sur le point d'accéder aux paramètres avancées de l'écran. Veuillez noter que ces paramètres sont plus techniques que les précédent et peuvent ne pas fonctionner sur tout les écrans. Nous vous invitons par ailleurs à bien relire la documentation Hyprland relatif aux moniteurs avant de modifier ces paramètres. Voulez-vous continuer ?")
        rst = await self.main_window.dialog(info)

        if rst:
            self.spec_box.remove(widget)
            self.main_box.add(self.advanced_box)
            self.main_box.refresh()

    def change_bitdepht(self, widget):
        self.settings[self.monitor]["bitdepht"] = widget.value

    def change_cm(self, widget):
        self.settings[self.monitor]["cm"] = widget.value

    def change_eotf(self, widget):
        self.settings[self.monitor]["sdr_eotf"]  = widget.value

    def change_sdrbright(self, widget):
        if check_sdr(widget.value) == None: self.settings[self.monitor]["sdrbrightness"] = float(widget.value)

    def change_sdrsat(self, widget):
        if check_sdr(widget.value) == None: self.settings[self.monitor]["sdrsaturation"] = float(widget.value)

    def change_vrr(self, widget):
        setting = self.settings[self.monitor]
        if widget.value == "Désactivé": setting["vrr"] = 0
        elif widget.value == "Activé": setting["vrr"] = 1
        else: setting["vrr"] = 2

    async def change_icc(self, widget):
        file = toga.OpenFileDialog("Sélectionner un profil ICC", file_types=["icc"], multiple_select=False)
        rst = await self.main_window.dialog(file)

        self.settings[self.monitor]["icc"] = rst
        self.icc_text.text = str(rst)

        self.main_box.refresh()

    def change_area(self, widget):
        try:
            self.settings[self.monitor]["reserved_area"] = int(widget.value)
        except ValueError:
            self.settings[self.monitor]["reserved_area"] = widget.value

    def change_wide(self, widget):
        if widget.value == "Désactivé": self.settings[self.monitor]["supports_wide_color"] = 0
        elif widget.value == "Activé": self.settings[self.monitor]["supports_wide_color"] = 2
        else: self.settings[self.monitor]["supports_wide_color"] = 1

    def change_hdr(self, widget):
        if widget.value == "Désactivé": self.settings[self.monitor]["supports_hdr"] = 0
        elif widget.value == "Activé": self.settings[self.monitor]["supports_hdr"] = 2
        else: self.settings[self.monitor]["supports_hdr"] = 1

    def change_sdr_min(self, widget):
        if check_sdr_float(widget.value) == None: self.settings[self.monitor]["sdr_min_luminance"] = float(widget.value)

    def change_sdr_max(self, widget):
        if check_sdr_int(widget.value) == None: self.settings[self.monitor]["sdr_max_luminance"] = int(widget.value)

    def change_min_luminance(self, widget):
        if check_hdr_float(widget.value) == None: self.settings[self.monitor]["min_luminance"] = float(widget.value)

    def change_max_luminance(self, widget):
        if check_hdr_int(widget.value) == None: self.settings[self.monitor]["max_luminance"] = int(widget.value)

    def change_avg_luminance(self, widget):
        if check_hdr_int(widget.value) == None: self.settings[self.monitor]["max_avg_luminance"] = int(widget.value)

    def apply_change(self, widget):
        with open(Path("~/.config/hypr/settings/mon.json").expanduser(), "w") as fichier:
            fichier.write(json.dumps(self.settings, indent=4))

        with open(Path("~/.config/hypr/monitor.lua").expanduser(), "w") as fichier:

            fichier.write("--Fichier généré automatiquement par le panneau de configuration LoinafOS\n\n\n\n")

            def convert_bool(s:bool):
                if s: return "true"
                else: return "false"

            for monitor in self.settings:
                setting = self.settings[monitor]
                fichier.write("hl.monitor({\n")
                fichier.write("\toutput = \"desc:"+str(setting["desc"])+"\",\n")
                fichier.write("\tmode = \""+str(setting["mode"])+"\",\n")
                if setting["position"][0]:
                    fichier.write("\tposition = \"auto\",\n")
                else:
                    pos_dict = ["right", "left", "up", "down"]
                    fichier.write("\tposition = \"auto-"+str(pos_dict[setting["position"][1]])+"\",\n")
                fichier.write("\tscale = "+str(setting["scale"])+",\n")
                fichier.write("\tdisabled = "+convert_bool(setting["disabled"])+",\n")
                fichier.write("\ttransform = "+str(setting["transform"])+",\n")
                if setting["mirror"] == None:
                    fichier.write("\tmirror = nil,\n")
                else:
                    fichier.write("\tmirror = \""+str("desc:"+setting["mirror"])+"\",\n")
                fichier.write("\tbitdepth = "+convert_bool(setting["bitdepht"])+",\n")
                fichier.write("\tcm = \""+str(setting["cm"])+"\",\n")
                fichier.write("\tsdr_eotf = \""+str(setting["sdr_eotf"])+"\",\n")
                fichier.write("\tsdrbrightness = "+str(setting["sdrbrightness"])+",\n")
                fichier.write("\tsdrsaturation = "+str(setting["sdrsaturation"])+",\n")
                fichier.write("\tvrr = "+str(setting["vrr"])+",\n")
                if setting["icc"] == None: fichier.write("\ticc = nil,\n")
                else: fichier.write("\ticc = \""+str(setting["icc"])+"\",\n")
                if type(setting["reserved_area"]) == int: fichier.write("\treserved_area = "+str(setting["reserved_area"])+",\n")
                else: fichier.write("\treserved_area = \""+str(setting["reserved_area"])+"\",\n")
                fichier.write("\tsupports_wide_color = "+str(setting["supports_wide_color"])+",\n")
                fichier.write("\tsupports_hdr = "+str(setting["supports_hdr"])+",\n")
                fichier.write("\tsdr_min_luminance = "+str(setting["sdr_min_luminance"])+",\n")
                fichier.write("\tsdr_max_luminance = "+str(setting["sdr_max_luminance"])+",\n")
                fichier.write("\tmin_luminance = "+str(setting["min_luminance"])+",\n")
                fichier.write("\tmax_luminance = "+str(setting["max_luminance"])+",\n")
                fichier.write("\tmax_avg_luminance = "+str(setting["max_avg_luminance"])+",\n})\n\n")

            fichier.write("hl.monitor({ output = \"\", mode = \"preferred\", position = \"auto\", scale = 1 })\n")

    async def draw(self, widget):
        if self.error[0]:
            error = toga.ErrorDialog("Erreur critique", f"Une erreur est survenue lors de la lecture de vos paramètres\nErreur : {self.error[1]}\nVoulez-vous tenter de réparer cela en réinitialisant vos paramètres sauvegardés?")

            response = await self.main_window.dialog(error)
            if response:
                try:
                    with open(Path("~/.config/hypr/settings/mon.json").expanduser(), "w") as fichier:
                        self.settings = []
                        fichier.write(json.dumps(self.settings, indent=4))
                except PermissionError:
                    error = toga.ErrorDialog("Erreur critique: Nous n'avons pas pu accéder à vos paramètres en raison d'une erreur de lecture et nous n'avons pas pu les créer. Vérifiez vos permissions")
                    print("Erreur critique: Nous n'avons pas pu accéder à vos paramètres en raison d'une erreur de lecture et nous n'avons pas pu les créer. Vérifiez vos permissions")
                    await self.main_window.dialog(error)
                    return
            else: return

        self.container = toga.ScrollContainer()

        self.container.content = self.main_box

        self.main_window.content = self.container
