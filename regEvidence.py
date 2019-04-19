# ---- regEvidence ----
# Author: michkoll
# URL: https://github.com/michkoll/py-appcharacteristics/blob/master/regEvidence.py
# ----------------------

import argparse
import glob
import json
import os
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)

baseDirectory = "";
peDirectory = "";
ceDirectory = "";
evidenceStats = {}

cmpFileEnding = "hivcmp"
peFileEndingKeys = "regpe-keys"
peFileEndingValues = "regpe-values"
ceFileEndingValues = "regce-values"
ceFileEndingKey = "regce-keys"

allPEEntries = {}

filterPE = True
filterCE = True

# CHANGE THIS
filterExclude =     {
    "HKLM\COMPONENTS\CanonicalData" : 0,
    "HKLM\COMPONENTS\DerivedData" : 0,
    "HKLM\SOFTWARE\Classes" : 0,
    "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion" : 0,
    "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" : 0,
    "HKLM\SOFTWARE\WOW6432Node" : 0,
    "HKLM\SOFTWARE\Microsoft\.NETFramework" : 0,
    "HKLM\SOFTWARE\Microsoft\Windows\EnterpriseResourceManager" : 0,
    "HKLM\SOFTWARE\Microsoft\WindowsRuntime\ActivatableClassId" : 0,
    "HKLM\SOFTWARE\Microsoft\SystemSettings\SettingId\SystemSettings" : 0,
    "HKLM\SOFTWARE\Microsoft" : 0,
    "HKLM\COMPONENTS\Drivers\\amd64" : 0,
    "HK" : 0
    }

# CHANGE THIS
filterInclude = {
    "Nessus" : 0,
    "Tenable" : 0,
    "8D6A097F-3FB4-4543-9015-887DAD0FBAF0" : 0,
    "1516f2d5ff564b34a2496ea81588ab52" : 0,
    "F790A6D84BF33454095188D7DAF0AB0F" : 0,
    "nessus-service" : 0,
    "nessusd" : 0,
    "nessuscli" : 0,
    "6ae7.msi" : 0
}

class Mode(Enum):
    """
    Enum für die Zuordnung der Zeitstempel
    """
    KEYDELETED = 0
    KEYADDED = 1
    VALUEDELETED = 2
    VALUEADDED = 3
    VALUEMODIFIED = 4
    NONE = 99

class EvidenceType(Enum):
    """
    Enum for evidence type (key or value)
    """
    KEY = 0
    VALUE = 1
    NONE = 99

def doFilter(sampleString : str):
    includeFound = False
    for includeString, v in filterInclude.items():
        if includeString in sampleString:
            includeFound = True
            filterInclude[includeString] += 1

    if includeFound:
        return False

    for excludeString, v in filterExclude.items():
        if excludeString in sampleString:
            filterExclude[excludeString] += 1
            return True

    return False

def resetFilter():
    for k, v in filterExclude.items():
        filterExclude[k] = 0
    for k, v in filterInclude.items():
        filterInclude[k] = 0

def dictToStringList(origDict):
    newList = []

    for k_entry, v_entry in origDict.items():
        newEntry = k_entry
        # if no True Timestamp eliminate entry
        hasTimestamp = False

        for k_timestamp, v_timestamp in v_entry.items():
            actTimestamp = " "
            if k_timestamp == "deleted":
                actTimestamp = "d"
            elif k_timestamp == "added":
                actTimestamp = "cr"
            elif k_timestamp == "modified":
                actTimestamp = "c"

            if v_timestamp == True:
                newEntry += "\t" + actTimestamp
                hasTimestamp = True
            else:
                newEntry += "\t"

        if newEntry != "" and hasTimestamp:
            newEntry += "\n"
            newList.append(newEntry)

    return newList

def makePE(filter = False):
    global allPEEntries



    reportFiles = glob.glob(baseDirectory + "/*." + cmpFileEnding)

    global peDirectory
    peDirectory = os.path.join(baseDirectory, "pe")
    if not os.path.exists(peDirectory):
        try:
            os.mkdir(peDirectory)
        except:
            logging.error("pe directory could not be created. Exiting")
            exit(1)

    #reportFiles = ['/datadisk/Studium/M118/Spurend/shots/005-deleteScan.hivcmp','/datadisk/Studium/M118/Spurend/shots/006-uninstall.hivcmp']
    for reportFile in sorted(reportFiles):

        with open(reportFile, "r", encoding='utf-8') as fhReportFile:
            logging.info("Current file: " + reportFile)
            # create file handler for pe File
            fhPeKeyFile = open(os.path.join(peDirectory, os.path.basename(reportFile).replace(cmpFileEnding,peFileEndingKeys)), "w")
            fhPeValuesFile = open(os.path.join(peDirectory, os.path.basename(reportFile).replace(cmpFileEnding, peFileEndingValues)), "w")
            peKeyEntries = {}
            peValueEntries = {}

            peStats = {
                "keysadded": {"Original": 0, "peorig": 0, "pefiltered" : 0, "ceorig" : 0},
                "keysdeleted": {"Original": 0, "peorig": 0, "pefiltered" : 0, "ceorig" : 0},
                "valuesadded": {"Original": 0, "peorig": 0, "pefiltered" : 0, "ceorig" : 0},
                "valuesdeleted": {"Original": 0, "peorig": 0, "pefiltered" : 0, "ceorig" : 0},
                "valuesmodified": {"Original": 0, "peorig": 0, "pefiltered" : 0, "ceorig" : 0},
                "total": {"Original": 0, "peorig": 0, "pefiltered" : 0, "ceorig" : 0},
            }

            # inital action status
            actMode = Mode.NONE

            # for duplicate modified entries
            lastEntryModified = False

            # iterate over lines in cmp report from RegShot
            for cmpLine in fhReportFile.readlines():
                cmpLine = cmpLine.replace("\n", "")

                if "Keys deleted" in cmpLine:
                    actMode = Mode.KEYDELETED
                    k, v = cmpLine.split(":")
                    peStats["keysdeleted"]["Original"] = int(v)
                    continue
                elif "Keys added" in cmpLine:
                    actMode = Mode.KEYADDED
                    k, v = cmpLine.split(":")
                    peStats["keysadded"]["Original"] = int(v)
                    continue
                elif "Values deleted" in cmpLine:
                    actMode = Mode.VALUEDELETED
                    k, v = cmpLine.split(":")
                    peStats["valuesdeleted"]["Original"] = int(v)
                    continue
                elif "Values added" in cmpLine:
                    actMode = Mode.VALUEADDED
                    k, v = cmpLine.split(":")
                    peStats["valuesadded"]["Original"] = int(v)
                    continue
                elif "Values modified" in cmpLine:
                    actMode = Mode.VALUEMODIFIED
                    k, v = cmpLine.split(":")
                    peStats["valuesmodified"]["Original"] = int(v)
                    continue
                elif "Total changes" in cmpLine:
                    actMode = Mode.NONE
                    k, v = cmpLine.split(":")
                    peStats["total"]["Original"] = int(v)
                    continue


                if "----------------------" in cmpLine or cmpLine.strip(" ") == "":
                    logging.debug("Invalid value, continuing ...")
                    continue

                peKeyEntry = {"added" : False, "deleted" : False}
                peValueEntry = {"added" : False, "deleted" : False, "modified" : False}


                if cmpLine.startswith('HK',0,2):
                    # handle key evidence
                    if actMode in (Mode.KEYDELETED, Mode.KEYADDED):
                        # Create new entry
                        if cmpLine not in peKeyEntries:
                            peKeyEntries[cmpLine] = peKeyEntry.copy()

                        if actMode == Mode.KEYDELETED:
                            peKeyEntries[cmpLine]["deleted"] = True
                            peStats["keysdeleted"]["peorig"] += 1
                        elif actMode == Mode.KEYADDED:
                            peKeyEntries[cmpLine]["added"] = True
                            peStats["keysadded"]["peorig"] += 1

                    # handle value evidence
                    elif actMode in (Mode.VALUEMODIFIED, Mode.VALUEADDED, Mode.VALUEDELETED):
                        if actMode == Mode.VALUEMODIFIED:
                            k, v = cmpLine.split(":",1)
                            cmpLine = k
                            if lastEntryModified and cmpLine in peValueEntries:
                                lastEntryModified = False
                                continue

                        if cmpLine not in peValueEntries:
                            peValueEntries[cmpLine] = peValueEntry.copy()

                        if actMode == Mode.VALUEDELETED:
                            peValueEntries[cmpLine]["deleted"] = True
                            peStats["valuesdeleted"]["peorig"] += 1
                        elif actMode == Mode.VALUEADDED:
                            peValueEntries[cmpLine]["added"] = True
                            peStats["valuesadded"]["peorig"] += 1
                        elif actMode == Mode.VALUEMODIFIED:
                            lastEntryModified = True
                            peValueEntries[cmpLine]["modified"] = True
                            peStats["valuesmodified"]["peorig"] += 1
                else:
                    logging.debug("No HK at beginnging. Continue")

            # add dictionaries to global list

            allPEEntries[os.path.basename(fhPeKeyFile.name)] = peKeyEntries
            allPEEntries[os.path.basename(fhPeValuesFile.name)] = peValueEntries

            # PE-File Keys schreiben und FileHandler schließen
            fhPeKeyFile.writelines(dictToStringList(peKeyEntries))
            fhPeKeyFile.flush()
            fhPeKeyFile.close()

            # PE-File Keys schreiben und FileHandler schließen
            fhPeValuesFile.writelines(dictToStringList(peValueEntries))
            fhPeValuesFile.flush()
            fhPeValuesFile.close()

            # update stats
            peStats["total"]["Original"] = peStats["keysdeleted"]["Original"] + peStats["keysadded"]["Original"] + peStats["valuesmodified"]["Original"] + peStats["valuesdeleted"]["Original"] + peStats["valuesadded"]["Original"]
            peStats["total"]["peorig"] = peStats["keysdeleted"]["peorig"] + peStats["keysadded"]["peorig"] + peStats["valuesmodified"]["peorig"] + peStats["valuesdeleted"]["peorig"] + peStats["valuesadded"]["peorig"]

            for k, v in peStats.items():
                v["ceorig"] = v["peorig"]
            evidenceStats[os.path.basename(reportFile)] = peStats

def makeCE(filter = False):
    global allPEEntries
    global ceDirectory
    ceDirectory = os.path.join(baseDirectory, "ce")
    if not os.path.exists(ceDirectory):
        try:
            os.mkdir(ceDirectory)
        except:
            logging.error("ce directory could not be created. Exiting")
            exit(1)

    evidenceType = EvidenceType.NONE

    for k_peDict, v_peDict in allPEEntries.items():
        logging.info("CE Parent file: " + k_peDict)
        countDeletedEvidence = 0
        if peFileEndingKeys in k_peDict:
            evidenceType = EvidenceType.KEY
        elif peFileEndingValues in k_peDict:
            evidenceType = EvidenceType.VALUE

        v_peDictCopy = dict(v_peDict)
        for k_peSubDict, v_peSubDict in allPEEntries.items():
            logging.info("--- CE Sub file: " + k_peSubDict)
            # if same pe evidence file
            if k_peDict == k_peSubDict:
                continue
            # only proces same evidence type
            if (peFileEndingValues in k_peDict and peFileEndingValues in k_peSubDict) or (peFileEndingKeys in k_peDict and peFileEndingKeys in k_peSubDict):
                # iterate each entry in parent dict v_peDict

                for k_entry, v_entry in v_peDict.items():
                    if filter and doFilter(k_entry):
                        if k_entry in v_peDictCopy:
                            del v_peDictCopy[k_entry]
                        continue
                    # if parent entry exists in sub entries
                    if k_entry in v_peSubDict:
                        for k, v in v_peSubDict[k_entry].items():
                            if v == True:
                                if v_peDictCopy[k_entry][k] == True:
                                    v_peDictCopy[k_entry][k] = False
                                    #logging.info(k_entry + "\t Timestamp: " + k)
                                    countDeletedEvidence += 1
                                    # update stat
                                    statString = ""
                                    if evidenceType == EvidenceType.KEY and k == "added":
                                        statString = "keysadded"
                                    elif evidenceType == EvidenceType.KEY and k == "deleted":
                                        statString = "keysdeleted"
                                    elif evidenceType == EvidenceType.VALUE and k == "added":
                                        statString = "valuesadded"
                                    elif evidenceType == EvidenceType.VALUE and k == "deleted":
                                        statString = "valuesdeleted"
                                    elif evidenceType == EvidenceType.VALUE and k == "modified":
                                        statString = "valuesmodified"
                                    if statString != "":
                                        #logging.info(evidenceStats[k_peDict.split(".")[0] + "." + cmpFileEnding][statString])
                                        evidenceStats[k_peDict.split(".")[0] + "." + cmpFileEnding][statString]["ceorig"] -= 1

        evidenceStats[k_peDict.split(".")[0] + "." + cmpFileEnding]["filtered"] = filterExclude.copy()
        evidenceStats[k_peDict.split(".")[0] + "." + cmpFileEnding]["included"] = filterInclude.copy()
        resetFilter()

        logging.info("Eliminated Evidence in " + k_peDict + ": " + str(countDeletedEvidence))
        with open(os.path.join(ceDirectory, k_peDict.replace(peFileEndingKeys, ceFileEndingKey).replace(peFileEndingValues, ceFileEndingValues)), "w") as ceFile:
            ceFile.writelines(dictToStringList(v_peDictCopy))

    return

# Kommandozeilenargumente einlesen und parsen
parser = argparse.ArgumentParser(description='Analyze evidence in RegShot-Reports')
parser.add_argument('pathCompareReports', help='Absoluter Pfad zum Verzeichnis der RegShot-Reports')
args = parser.parse_args()

if not os.path.exists(os.path.normpath(args.pathCompareReports)):
    logging.error("Directory does not exist")
    exit(1)

baseDirectory = os.path.normpath(args.pathCompareReports)
logging.info("Base directory: " + baseDirectory)

makePE(filterPE)
makeCE(filterCE)

with open(os.path.join(baseDirectory, "regEvidence.stats"), "w") as fhPeFileStat:
    fhPeFileStat.write(json.dumps(evidenceStats, indent=2))
