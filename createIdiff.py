# Full code: https://github.com/michkoll/py-appcharacteristics

import glob
import argparse

from misc.lib.ConfigReader import *
from misc.lib.VMManager import *

# Konfigurationshilfsklasse für Parameter einlesen
conf = ConfigReader("./misc/config.ini")
# Logginglevel setzen
logging.basicConfig(level=logging.INFO)

idifferencePath = "idifference2.py"
initRaw = "init.raw"

initSnapshot = "005-deleteScan"
useInitSnapshots = True
snapshots = {"006-uninstall"}
iterations = 3

def createIdiff():
    for snapShot in snapshots:
        for iteration in range (1, iterations + 1):
            outFile = os.path.join(conf.IdiffDir, snapShot + "." + str(iteration) + ".idiff")
            rawFile = os.path.join(conf.RawDir, snapShot + "." + str(iteration) + ".raw")
            if os.path.exists(outFile):
                logging.warn("Idiff-Datei existiert bereits:" + outFile)
                break
            with open(outFile, "wb", 0) as out:
                if useInitSnapshots:
                    initSnapRaw = os.path.join(conf.RawDir, initSnapshot + "." + str(iteration) + ".raw")
                    proc = subprocess.call(["python3", idifferencePath, initSnapRaw, rawFile],
                                           stdout=out)
                else:
                    proc = subprocess.call(["python3", idifferencePath, os.path.join(conf.RawDir, initRaw), rawFile], stdout=out)


# Übergebene Kommandozeilenargumente parsen
parser = argparse.ArgumentParser(description='Erstellt idiff Dateien zu gegebenen RAW-Files')
parser.add_argument('pathToRaw', help='Absoluter Pfad zu den RAW-Dateien.')
parser.add_argument('pathIdiff', help='Absoluter Pfad zu den idiff-Dateien')
parser.add_argument('snapshotBase', help='Snapshot der als Basis für die Analyse gilt')
parser.add_argument('snapshotDest', help='Snapshot für den die Spuren erzeugt werden sollen')
parser.add_argument('idifference2Path', help='Absoluter Pfad zu idifference2.py')

args = parser.parse_args()

# Raw-Verzeichnis prüfen. Falls Verzeichnis nicht vorhanden, Applikation beenden.
rawDir = os.path.normpath(args.pathToRaw)
idiffDir = os.path.normpath(args.pathIdiff)
initSnapshot = args.snapshotBase
snapshots = args.snapshots
idifferencePath = args.idifference2Path
if not os.path.exists(args.pathToRaw):
    logging.error("Das Verzeichnis mit den Raw-Dateien konnte nicht gefunden werden. Bitte Eingabe überprüfen.")
if not os.path.exists(args.pathIdiff):
    logging.error("Das Verzeichnis mit den idiff-Dateien konnte nicht gefunden werden. Bitte Eingabe überprüfen.")
    exit(1)
if not os.path.exists(args.idifference2Path):
    logging.error("idifference2 konnte nicht gefunden werden")
    exit(1)
else:
    conf.RawDir = rawDir
    logging.info("Raw-Verzeichnis gesetzt: " + conf.RawDir)
    conf.IdiffDir = idiffDir
    logging.info("Idiff-Verzeichnis gesetzt: " + conf.IdiffDir)


# Ablaufsteuerung der Analyse
try:
    createIdiff()
except VirtualBoxError as e:
    logging.error("Fehlermeldung: " + e.message + "\nDetails: " + e.detail + "\nAPPLIKATION MIT FEHLER BEENDET")
except Exception as e:
    print("Unbehandelte Exception: \n" + str(e) + "\n ENDE")