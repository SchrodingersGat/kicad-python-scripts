import sys
import os

sys.path.append(os.getcwd() + os.sep + ".." + os.sep)

from kicad_symbol_gen import cmp

#Packet
P = {
    "BM": ", in SOIC-8 Package",
    "BN": ", in DIP-8 Package"
    }

#output
O = {
    "1": "Active High Output",
    "2": "Active Low Output"
    }

#generic description
desc = "Dual-channel, high side, power distribution switch, 2.7V-5.5V, "
keys = "mosfet distribution"
docs = "http://www.micrel.com/_PDF/mic2026.pdf"

parts = []

aliases = []

basename = "MIC2026-"

for oCode in O.keys():
    for pCode in P.keys():
        name = basename + oCode + pCode
        aliases.append(name)
        description = desc + O[oCode] + P[pCode]
        parts.append(cmp(name,description,keys,docs))

for part in parts:
    print(part,)

alias = "ALIAS " + " ".join(aliases[1:])
