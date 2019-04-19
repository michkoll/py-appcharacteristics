# Kommandozeilenargumente einlesen und parsen
import argparse
import glob
import os
import logging

parser = argparse.ArgumentParser(description='Convert CE-file to latex table')
parser.add_argument('inFile', help='Absoluter Pfad zum CE-File')
args = parser.parse_args()

pathIn = os.path.normpath(args.inFile)


if not os.path.exists(pathIn):
    logging.error("CE-File nicht gefunden")
    exit(1)

pathOut = pathIn + "-latex"


latexColumnFeed = "\t & \t"
latexLineFeed = "\\\\ \n"

# CHANGE THIS
ceAttributes = {
    "c" : False,
    "cr" : False,
    "d" : False
}

removeList = glob.glob(pathIn + "/*.latex")
for removeFile in removeList:
    os.remove(removeFile)

fileList = glob.glob(pathIn + "/*.regce*")

for file in fileList:
    ceEntries = dict()
    with open(file, "r") as inFile:
        for line in inFile.read().splitlines():
            entry = line.split("\t")
            entryKey = entry[0]

            if entryKey not in ceEntries:
                ceEntries[entryKey] = ceAttributes.copy()

            del entry[0]

            for timestamp in entry:
                if timestamp.strip() != "":
                    ceEntries[entryKey][timestamp] = True

    latexEntries = []

    tableHeader = "\\begin{longtable}{p{12cm}lll}\n\\textbf{Datei} & \\textbf{c} & \\textbf{cr} & \\textbf{d} \\\\\n"
    tableFooter = "\\caption{ " + os.path.basename(file) + "}\n\\label{tab:spurenRegistry" + os.path.basename(file) + "}\n\\end{longtable}"

    with open(file + ".latex", "w") as outFile:
        for k, v in ceEntries.items():
            entryLine = "\\path{" + k + "}"
            entryLine.replace('_', '\\_')

            for k_attribute, v_attribute in sorted(v.items()):
                if v_attribute:
                    entryLine += latexColumnFeed + k_attribute
                else:
                    entryLine += latexColumnFeed + " "

            entryLine += latexLineFeed

            latexEntries.append(entryLine)

        outFile.write(tableHeader)
        outFile.writelines(latexEntries)
        outFile.write(tableFooter)

