import argparse
import glob
import logging
import os
from collections import Counter

# Argumente einlesen und parsen
parser = argparse.ArgumentParser(description='Merge Evidence')
parser.add_argument('pathPe', help='Absoluter Pfad zu den PE-Dateien')
parser.add_argument('pathMe', help='Absoluter Pfad zu den ME-Dateien')
args = parser.parse_args()

# Pfade zu gemeinsanem Ordnern lesen
pathPe = os.path.normpath(args.pathPe)
pathMe = os.path.normpath(args.pathMe)

# alle PE-Files suchen
peFilesAll = glob.glob(pathPe + "/*.pe")

# Leeres Set initialisieren
peFilesApps = set()
# Anhand der PE-Files die zu analysierenden Applikationen ermitteln
for peFile in sorted(peFilesAll):
    peFileBasename = os.path.basename(peFile)
    peFilesApps.add(peFileBasename[0:peFileBasename.find(".")])

# PE-Files zusammenführen. Pro Applikation wird ein ME-File erstellt
# Applikation iterieren
for peFileApp in peFilesApps:
    print("Bearbeite Files " + peFileApp)
    mergedEntries = []

    # Iterationen pro Applikation durchlaufen
    for peFileAppIter in glob.glob(pathPe + "/" + peFileApp + ".[0-9].pe"):
        mergedEntries.extend(open(peFileAppIter, "r").read().splitlines(False))

    # Set mit der Anzahl der Vorkommnisse erweitern
    uniqueEntries = Counter(mergedEntries)

    # ME-File schreiben
    with open(pathMe + "/" + peFileApp + ".me", "w") as peFd:
        for k,v in sorted(uniqueEntries.items()):
            peFd.write(k + "\t" + str(v) + "\n")









