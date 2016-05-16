import sys
import os

sys.path.append(os.getcwd() + os.sep + ".." + os.sep)

from kicad_symbol_gen import cmp

# http://ww1.microchip.com/downloads/en/DeviceDoc/21942e.pdf

#accuracy
A = {
    '9700' : '2C',
    '9700A' : '4C'
    }

T = {
    'E' : '-40C to +125C',
    'H' : '-40C to +150C'
    }    
    
#package
P = {
    #'TT' : 'SOT-23-3',
    'LT' : 'SC-70-5'
    }

#generic description
desc = "Low power, analog thermistor temperature sensor, {accuracy} accuracy, {range}, in {package} package"
keys = "temperature sensor thermistor"
docs = "http://ww1.microchip.com/downloads/en/DeviceDoc/21942e.pdf"

parts = []

aliases = []

basename = "MCP{suff}-{temp}/{pack}"

for a in A.keys():
    for t in T.keys():
        for p in P.keys():
            
            name = basename.format(suff=a,temp=t,pack=p)
            aliases.append(name)
            
            description = desc.format(accuracy=A[a],range=T[t],package=P[p])
            
            parts.append(cmp(name,description,keys,docs))

for part in parts:
    print(part)

alias = "ALIAS " + " ".join(aliases[1:])
