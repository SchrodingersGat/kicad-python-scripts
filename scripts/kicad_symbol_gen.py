def cmp(name, desc, keys, docs):
    c = "#\n"
    c += "$CMP " + name.upper() + "\n"
    c += "D " + desc + "\n"
    c += "K " + keys.replace(",","").lower() + "\n"
    c += "F " + docs + "\n"
    c += "$ENDCMP\n"

    return c

