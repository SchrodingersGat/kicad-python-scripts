import sys
import os

sys.path.append(os.getcwd() + os.sep + ".." + os.sep)

from kicad_symbol_gen import cmp

#voltage rating
V = {
    "-2": "4.20V",
    "-3": "4.35V",
    "-4": "4.40V",
    "-5": "4.50V"
    }

#output
O = {
    "1": "Tri-State Status Output",
    "2": "Open-Drain Status Output"
    }

#generic description
desc = "Single cell, Li-Ion/Li-Po charge management controller, "
keys = "battery charger lithium"
docs = "http://ww1.microchip.com/downloads/en/DeviceDoc/20001984g.pdf"

parts = []

aliases = []

basename = "MCP7383"

for oCode in O.keys():
    for vCode in V.keys():
        name = basename + oCode + vCode + "-OT"
        aliases.append(name)
        description = desc + V[vCode] + ", " + O[oCode] + ", in SOT23-5 package"

        parts.append(cmp(name,description,keys,docs))

for part in parts:
    print(part)

alias = "ALIAS " + " ".join(aliases[1:])
