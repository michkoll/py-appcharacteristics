import argparse
from time import sleep

from lib.ConfigReader import *
from lib.VMManager import *

conf = ConfigReader("misc/config.ini")
winVm = VMManager(conf.WinVMName)


def makeInit(imageName):
    """
    Erstellt einen initialen Zustand zur Vorbereitung der Analyse. Hierbei wird folgender Ablauf angenommen:
    - Starten der frisch importierten VM
    - 30 Sekunden warten
    - Reboot der VM
    - 30 Sekunden warten
    - Snapshot erstellen
    - RAW-Datei für init-Zustand kopieren

    :param imageName: Name des initialien Zustands
    :return: True, falls erfolgreich. Ansonsten False.
    """
    logging.info("Erstelle Initialzustand. Bitte warten ...")
    winVm.removeSnapshot(imageName)
    winVm.startVM()
    # Warten wegen Prefetchdienst
    logging.info("... 30 Sekunden warten ...")
    time.sleep(30)
    winVm.powerOffVM()
    winVm.startVM()
    logging.info("... 30 Sekunden warten ...")
    time.sleep(30)
    winVm.cloneAndResetVM(imageName, conf.RawDir, imageName + ".raw", imageName)
    logging.info("... Initialzustand erstellt: " + imageName)
    return True

def makeNoiseImages(imageName):
    """
    Erstellt Images für Hintegrundrauschen. Wartzeit beträgt 10 Minuten.

    :param imageName: Name der noise-Images
    :return: True, falls erfolgreich
    """
    winVm.resetVM(conf.InitSnapshot)
    winVm.startVM()
    logging.info("... 10 Minuten warten ...")
    sleep(600)
    winVm.cloneAndResetVM(imageName, conf.RawDir, imageName + ".raw", conf.InitSnapshot)
    return True

# Übergebene Kommandozeilenargumente parsen
parser = argparse.ArgumentParser(description='Prepare VMs.')
parser.add_argument('pathToRaw', help='Absoluter Pfad zu den RAW-Dateien.')
args = parser.parse_args()

# Rawverzeichnis prüfen
rawDir = os.path.normpath(args.pathToRaw)
if not os.path.exists(args.pathToRaw):
    logging.error("Das Verzeichnis mit den Raw-Dateien konnte nicht gefunden werden. Bitte Eingabe überprüfen.")
    exit(1)
else:
    conf.RawDir = rawDir
    logging.info("Raw-Verzeichnis gesetzt: " + conf.RawDir)

# Init-Zustand herstellen
#makeInit(conf.InitSnapshot)

# Noise aufnehmen
numNoises = 3
for i in range(0, numNoises):
    logging.info("Erstelle Hintergrundrauschen. Iteration " + str(i+1) + " von " + str(numNoises))
    makeNoiseImages("noise." + str(i+1))
    logging.info("Hintergrundrauschen " + str(i+1) + " von " + str(numNoises) + " erstellt.")
