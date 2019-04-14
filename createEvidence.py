# Full code: https://github.com/michkoll/py-appcharacteristics

import glob
import argparse

from misc.lib.ConfigReader import *
from misc.lib.VMManager import *

# Konfigurationshilfsklasse für Parameter einlesen
conf = ConfigReader("./misc/config.ini")
# Logginglevel setzen
logging.basicConfig(level=logging.INFO)

def doPe():
    proc = subprocess.call(["python3", os.getcwd() + "/misc/vm/peVm.py", conf.IdiffDir, conf.PeDir])

def doMe():
    proc = subprocess.call(["python3", os.getcwd() + "/misc/vm/meVm.py", conf.PeDir, conf.MeDir])

def doCe():
    proc = subprocess.call(["python3", os.getcwd() + "/misc/vm/ceVm.py", conf.MeDir, conf.CeDir])

# Übergebene Kommandozeilenargumente parsen
parser = argparse.ArgumentParser(description='Erstellt PE-, ME- und CE-Files für alle gegebenen idiff-Dateien.')
parser.add_argument('pathIdiff', help='Absoluter Pfad zu den idiff-Dateien')
parser.add_argument('pathPe', help='Absoluter Pfad zu den idiff-Dateien')
parser.add_argument('pathMe', help='Absoluter Pfad zu den idiff-Dateien')
parser.add_argument('pathCe', help='Absoluter Pfad zu den idiff-Dateien')
args = parser.parse_args()

# Raw-Verzeichnis prüfen. Falls Verzeichnis nicht vorhanden, Applikation beenden.
idiffDir = os.path.normpath(args.pathIdiff)
peDir = os.path.normpath(args.pathPe)
meDir = os.path.normpath(args.pathMe)
ceDir = os.path.normpath(args.pathCe)
if not os.path.exists(args.pathPe):
    logging.error("Das Verzeichnis mit den Pe-Dateien konnte nicht gefunden werden. Bitte Eingabe überprüfen.")
if not os.path.exists(args.pathIdiff):
    logging.error("Das Verzeichnis mit den idiff-Dateien konnte nicht gefunden werden. Bitte Eingabe überprüfen.")
    exit(1)
if not os.path.exists(args.pathMe):
    logging.error("Das Verzeichnis mit den Me-Dateien konnte nicht gefunden werden. Bitte Eingabe überprüfen.")
    exit(1)
if not os.path.exists(args.pathCe):
    logging.error("Das Verzeichnis mit den Ce-Dateien konnte nicht gefunden werden. Bitte Eingabe überprüfen.")
    exit(1)
else:
    conf.IdiffDir = idiffDir
    conf.PeDir = peDir
    conf.MeDir = meDir
    conf.CeDir = ceDir
    logging.info("Idiff-Verzeichnis gesetzt: " + conf.IdiffDir + "\n" +
                 "Pe-Verzeichnis: " + conf.PeDir + "\n" +
                 "Me-Verzeichnis: " + conf.MeDir + "\n" +
                 "Ce-Verzeichnis: " + conf.CeDir)

# Ablaufsteuerung der Analyse
try:
    doPe()
    doMe()
    doCe()
except VirtualBoxError as e:
    logging.error("Fehlermeldung: " + e.message + "\nDetails: " + e.detail + "\nAPPLIKATION MIT FEHLER BEENDET")
except Exception as e:
    print("Unbehandelte Exception: \n" + str(e) + "\n ENDE")