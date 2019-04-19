# py-appcharacteristics

all scripts in this repository are under development

## regEvidence.py

Tool for getting characteristic evidence from RegShot-Comparison files.

Usage:

~~~~
1. Create all comparison files you need with RegShot
2. Change file ending from txt to hivcmp (don't ask why)
3. Edit exclude and include filter in regEvidence.py (search for CHANGE ME)
4. Run Script with argument pointing to the directory containing the hivcmp-files

$ python regEvidence.py <absolute path>

5. Hope and wait
~~~~

You will get one directory with merged evidence (pe/) and another 
directory with characteristic evidence (ce/).

For statistic freaks you will find some statistics in the base directory at `regEvidence.stats`