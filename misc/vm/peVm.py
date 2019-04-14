import argparse
import glob
import os
from enum import Enum


class Mode(Enum):
    """
    Enum für die Zuordnung der Zeitstempel
    """
    NEW = 0
    DELETED = 1
    RENAMED = 2
    MODIFIED = 3
    PROPERTIES = 4
    NONE = 99

# Kommandozeilenargumente einlesen und parsen
parser = argparse.ArgumentParser(description='Prepare Evidence')
parser.add_argument('pathIdiff', help='Absoluter Pfad zu den Idiff-Dateien')
parser.add_argument('pathPe', help='Absoluter Pfad zu den PE-Dateien')
args = parser.parse_args()

# Alle idiff-Dateien einlesen
idiffFiles = glob.glob(os.path.normpath(args.pathIdiff) + "/*.idiff")
# Für alle files in idiffFiles
for idiffFile in sorted(idiffFiles):
    # idiffFile öffnen
    with open(idiffFile) as fhIdiffFile:
        # FileHandler für korrespondierendes PE-File öffnen
        peFile = open(os.path.normpath(args.pathPe) + "/" + os.path.basename(idiffFile).replace("idiff", "pe"), "w")
        peEntries = []
        actMode = Mode.NONE
        # idiffFile zeilenweise einlesen
        for idiffLine in fhIdiffFile.readlines():
            # Modus je nach Sektion einstellen. Falls aktuelle Zeile keine Sektionszeile ist,
            # bleibt der aktuelle Status erhalten
            idiffLine = idiffLine.replace("\n", "")
            if "New files" in idiffLine:
                actMode = Mode.NEW
            elif "Deleted files" in idiffLine:
                actMode = Mode.DELETED
            elif "Renamed files" in idiffLine:
                actMode = Mode.RENAMED
            elif "Files with modified contents" in idiffLine:
                actMode = Mode.MODIFIED
            elif "Files with changed properties" in idiffLine:
                actMode = Mode.PROPERTIES

            # Zeile in Liste aufspalten
            listIdiffLine = idiffLine.split("\t")

            # Falls keine leere Zeile gelesen wurde
            if len(listIdiffLine) > 1:
                newEntry = ""
                # Für neun angelegte Dateien 4 Einträge erzeugen
                if actMode == Mode.NEW:
                    for timestamp in ("a","m","c","cr"):
                        newEntry += "\t".join([listIdiffLine[1], timestamp]) + "\n"
                # Für gelöschte Dateien d-Zeitstempel erzeugen
                elif actMode == Mode.DELETED:
                    newEntry = "\t".join([listIdiffLine[1], "d"]) + "\n"
                # Falls time changed, timestamp übernehmen
                elif actMode == Mode.MODIFIED or Mode.PROPERTIES or Mode.RENAMED:
                    if "time changed" in listIdiffLine[1]:
                        timestamp = listIdiffLine[1][0:listIdiffLine[1].find("time")]
                        newEntry = "\t".join([listIdiffLine[0], timestamp]) + "\n"
                # Falls ein neuer Eintrag erkannt wurde, diesen in die Liste einfügen
                if newEntry != "":
                    peEntries.append(newEntry)

        # PE-File schreiben und FileHandler schließen
        peFile.writelines(peEntries)
        peFile.flush()
        peFile.close()




