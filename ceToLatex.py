# Kommandozeilenargumente einlesen und parsen
import argparse
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
# ceAttributes = {
#     "accessed" : False,
#     "changed" : False,
#     "created" : False,
#     "modified" : False,
#     "deleted" : False
# }


ceEntries = dict()
with open(pathIn, "r") as inFile:
    for line in inFile.read().splitlines():
        f, t = line.split("\t")

        if f not in ceEntries:
            ceEntries[f] = ceAttributes.copy()

        timestamp = ""
        if t == "a":
            timestamp = "accessed"
        elif t == "c":
            timestamp = "changed"
        elif t == "cr":
            timestamp = "created"
        elif t == "m":
            timestamp = "modified"
        elif t == "d":
            timestamp = "deleted"
        else:
            logging.info("No type for timestamp found")

        if timestamp != "":
            ceEntries[f][timestamp] = True

latexEntries = []
with open(pathOut, "w") as outFile:
    for k in ceEntries:
        entryLine = "\\path{" + k + "}" + latexColumnFeed
        entryLine.replace('_', '\\_')


        if ceEntries[k]["accessed"]:
            entryLine += "a" + latexColumnFeed
        else:
            entryLine += " " + latexColumnFeed

        if ceEntries[k]["changed"]:
            entryLine += "c" + latexColumnFeed
        else:
            entryLine += " " + latexColumnFeed

        if ceEntries[k]["created"]:
            entryLine += "cr" + latexColumnFeed
        else:
            entryLine += " " + latexColumnFeed

        if ceEntries[k]["modified"]:
            entryLine += "m" + latexColumnFeed
        else:
            entryLine += " " + latexColumnFeed

        if ceEntries[k]["deleted"]:
            entryLine += "d"
        else:
            entryLine += " "

        entryLine += latexLineFeed

        latexEntries.append(entryLine)

    outFile.writelines(latexEntries)


