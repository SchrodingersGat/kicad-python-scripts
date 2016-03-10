import sys
import os

sys.path.append(os.getcwd() + os.sep + ".." + os.sep)

from kicad_symbol_gen import cmp

#temperature rating
T = {"C": "0°C to +40°C",
     "I": "-40°C to +85°C",
     "H": "-40°C to +125°C"}

#package code
P = {
     "DE": "DFN-14",
     "MS": "MSOP-16",
     "S": "SOIC-16"
     }

#generic description
desc = "Surge stopper with ideal diode, UV and OV protection -40V to +80V"
keys = "surge overvoltage undervoltage reverse polarity protection diode ORing MOSFET driver"
docs = "http://cds.linear.com/docs/en/datasheet/436412f.pdf"

parts = []

alias = "ALIAS"

basename = "LTC4364"

for tCode in T.keys():
    for pCode in P.keys():

        name = basename + tCode + pCode
        alias += " " + name
        description = desc + " in " + P[pCode] + " package, " + T[tCode]

        parts.append(cmp(name,description,keys,docs))

for part in parts:
    print(part,)
