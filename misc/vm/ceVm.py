import argparse
import glob
import logging
import os
from collections import Counter

# Argumente einlesen und parsen
parser = argparse.ArgumentParser(description='Merge Evidence')
parser.add_argument('pathMe', help='Absoluter Pfad zu den ME-Dateien')
parser.add_argument('pathCe', help='Absoluter Pfad zu den PE-Dateien')
args = parser.parse_args()

# Pfade zu gemeinsamen Ordnern lesen
pathCe = os.path.normpath(args.pathCe)
pathMe = os.path.normpath(args.pathMe)

# Alle relevanten ME-Files identifizieren
meFilesApp = glob.glob(pathMe + "/*.me")
meEntries = dict()
meEntriesSub = dict()

# Iteration über jedes ME-File
# Hier werden alle Einträge aus den ME-Files gelesen und in das Dict meEntries auf Filebasis geschrieben
for meFile in meFilesApp:
    meFileEntriesPar = []
    meFileEntriesSub = []
    # ME-File lesen für jeden Eintrag Dateiname und Timestamps lesen
    with open(meFile, "r") as meFd:
        for line in meFd.read().splitlines():
            d, t, c = line.split("\t")
            # Ignoriere ME-Einträge als Minuend, die nicht dreimal (oder mehr wegen noise) aufgetreten sind, da diese nicht für eine charakteristische
            # Spur in Frage kommen
            if int(c) >= 3:
                meFileEntriesPar.append(d + "\t" + t + "\n")
            meFileEntriesSub.append(d + "\t" + t + "\n")
        meFileBase = os.path.basename(meFile)
        # Dictionary, mit key=meFile und value=List<MEEntries>
        meEntries[os.path.basename(meFileBase)[0:meFileBase.find(".")]] = meFileEntriesPar
        meEntriesSub[os.path.basename(meFileBase)[0:meFileBase.find(".")]] = meFileEntriesSub

# Iteriere über jedes ME-File in Dictionary (aktuell zu erstellendens CE-File)
# Hier wird die eigentliche Erstellung der CE-Spuren vollzogen (Subtrahieren der Spuren)
# Als Minuend werden nur Spuren genommen, die exakt drei Mal vorkommen. Wenn eine Spur nicht drei Mal vorkommt, kann
# diese nicht als charakteristische Spur betrachtet werden. Spuren die weniger als dreimal vorkommen werden allerdings
# als Subtrahend betrachtet, da diese eine mögliche charakterisitsche Spur nichtig machen.
for meKey, meValue in meEntries.items():
    # Falls aktuelles ME-File "noise", CE-Erstellung überspringen
    if meKey == "noise":
        continue
    # Einträge aus aktuellem ME-File in Set schreiben
    ceEntries = set(meValue)
    # Iteriere über jedes ME-File in Dictionary (zu subtrahierende ME-Files)
    for meKeySub, meValueSub in meEntriesSub.items():
        # Verhindern, zB a.pe von a.pe subtrahiert wird.
        if meKey == meKeySub:
            continue
        # Sets subtrahieren -> ceEntries enthält verminderte Spurenmenge
        ceEntries = ceEntries - set(meValueSub)
    # CE-File schreiben
    with open(pathCe + "/" + meKey + ".ce", "w") as ceFd:
        ceFd.writelines(sorted(ceEntries))

ceEntriesDir = []
with open(pathCe + "/" + meKey + ".ce", "r") as ceRead:
    for line in ceRead:
        fields = line.split('\t')
        #print(fields[0])
        ceEntriesDir.append(os.path.dirname(fields[0]) + "\n")

setCeEntriesDir = set(ceEntriesDir)
with open(pathCe + "/" + meKey + "Dir.ce", "w") as ceDirWrite:
    ceDirWrite.writelines(sorted(setCeEntriesDir))








