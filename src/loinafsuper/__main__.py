import os
import locale

# Définit la locale sur C.UTF-8 si la locale système n'est pas reconnue par la sandbox
os.environ["LC_ALL"] = "C.UTF-8"
try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error:
    locale.setlocale(locale.LC_ALL, "C.UTF-8")

from loinafsuper.app import main

if __name__ == "__main__":
    main().main_loop()
