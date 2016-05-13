import sys
import os
import csv

sys.path.append(os.getcwd() + os.sep + ".." + os.sep)

from kicad_symbol_gen import cmp

parts = []
aliases = []

with open("fdm.csv",'r') as file:
    reader= csv.reader(file)

    for row in reader:

        name = row[0]
        desc = row[1].replace("®","").replace("™","")
        datasheet = "https://www.fairchildsemi.com" + row[2]
        temp = row[3]
        vds = row[4]
        rds = row[5].split("@")[0].replace("?","Ω")
        qg = row[6].split("@")[0]
        vgs = row[7]
        i = row[8]

        description = "{desc}, Vds={vds}V, Rds={r}, Id(const)={current}A, Qg(max)={qg}, Temp={temp}, SON8 5x6mm package".format(
            desc = desc,
            vds = vds,
            r = rds,
            current = i,
            qg = qg,
            temp = temp)

        keys = "-".join([l.lower() for  l in desc.split(" ")[1:-1]]) + " mosfet fairchild"
        part = cmp(name, description, keys, datasheet)

        parts.append(part)
        aliases.append(name)

for part in parts:
    print(part,)

aliases = "ALIAS " + " ".join(aliases[1:])
