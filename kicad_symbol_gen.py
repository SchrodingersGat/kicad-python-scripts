#create a CMP entry (for KiCAD .dcm file)
def cmp(name, desc, keys, docs):

    #remove any commas from keys
    keys = keys.replace(",","")
    
    out = "#\n"
    out += "$CMP " + name + "\n"
    out += "D " + desc + "\n"
    out += "K " + keys + "\n"
    out += "F " + docs + "\n"
    out += "$ENDCMP\n"

    return out
    
    
