# Full code: https://github.com/michkoll/py-appcharacteristics

import glob
import argparse

from misc.lib.ConfigReader import *
from misc.lib.VMManager import *

# Konfigurationshilfsklasse für Parameter einlesen
conf = ConfigReader("./misc/config.ini")
# Logginglevel setzen
logging.basicConfig(level=logging.INFO)

snapshots = {"init"}
iterations = 3

# Erstellen der RAW-Dateien
def createRawFromSnapshot():
    winVm = VMManager(conf.WinVMName)

    for snapShot in snapshots:
        for iteration in range (1, iterations + 1):
            winVm.cloneHD(conf.RawDir, snapShot + "." + str(iteration) + ".raw", snapShot + "." + str(iteration))

    if not os.path.exists(os.path.join(conf.RawDir, conf.InitSnapshot + ".raw")):
        logging.info("Cloning init raw")
        winVm.cloneHD(conf.RawDir, conf.InitSnapshot + ".raw", conf.InitSnapshot)


# Übergebene Kommandozeilenargumente parsen
parser = argparse.ArgumentParser(description='Erstellen von RAW-Dateien zu einem bestimmten Snapshot')
parser.add_argument('pathToRaw', help='Absoluter Pfad zu den RAW-Dateien.')
parser.add_argument('snapshot', help='Snapshot für den die RAW-Dateien erstellt werden sollen')
args = parser.parse_args()

# Raw-Verzeichnis prüfen. Falls Verzeichnis nicht vorhanden, Applikation beenden.
rawDir = os.path.normpath(args.pathToRaw)
snapshots = args.snapshot
if not os.path.exists(args.pathToRaw):
    logging.error("Das Verzeichnis mit den Raw-Dateien konnte nicht gefunden werden. Bitte Eingabe überprüfen.")
    exit(1)
else:
    conf.RawDir = rawDir
    logging.info("Raw-Verzeichnis gesetzt: " + conf.RawDir)

# Ablaufsteuerung
try:
    createRawFromSnapshot()
except VirtualBoxError as e:
    logging.error("Fehlermeldung: " + e.message + "\nDetails: " + e.detail + "\nAPPLIKATION MIT FEHLER BEENDET")
except Exception as e:
    print("Unbehandelte Exception: \n" + str(e) + "\n ENDE")