import re

PREFIX_MICRO = ["μ","u","micro"]
PREFIX_MILLI = ["milli","m"]
PREFIX_NANO = ["nano","n"]
PREFIX_PICO = ["pico","p"]
PREFIX_KILO = ["kilo","k"]
PREFIX_MEGA = ["mega"]
PREFIX_GIGA = ["giga","g"]

PREFIX_ALL = PREFIX_PICO + PREFIX_NANO + PREFIX_MICRO + PREFIX_MILLI + PREFIX_KILO + PREFIX_MEGA + PREFIX_GIGA

UNIT_R = ["r","ohms","ohm","Ω"]
UNIT_C = ["farad","f"]
UNIT_L = ["henry","h"]

UNIT_ALL = UNIT_R + UNIT_C + UNIT_L

def getUnit(unit):

    unit = unit.lower()
    
    if unit in UNIT_R: return "R"
    if unit in UNIT_C: return "F"
    if unit in UNIT_L: return "H"

    return None

def getPrefix(prefix):

    prefix = prefix.lower()
    
    if prefix in PREFIX_PICO: return 1.0e-12
    if prefix in PREFIX_NANO: return 1.0e-9
    if prefix in PREFIX_MICRO: return 1.0e-6
    if prefix in PREFIX_MILLI: return 1.0e-3
    if prefix in PREFIX_KILO: return 1.0e3
    if prefix in PREFIX_MEGA: return 1.0e6
    if prefix in PREFIX_GIGA: return 1.0e9

    return 1

def groupString(group): #return a reg-ex string for a list of values
    return "[" + "|".join(group) + "]"

def matchString():
    return "^([0-9]+)(\.*)(\d*)(" + groupString(PREFIX_ALL) + "?)(" + groupString(UNIT_ALL) + "+)(\d*)$"


def compMatch(component): #return a reg-ex to match any component

    #remove any commas
    component = component.strip().replace(",","")

    match = matchString()

    result = re.search(match, component.lower())

    if not result: return None

    if not len(result.groups()) == 6: return None

    value,decimal,pre,prefix,units,post = result.groups()

    if not getUnit(units): return None

    try:
        val = int(value)
    except:
        return None

    val = val * 1.0 * getPrefix(prefix)

    return (val, getUnit(units))

tests = [
    "15uH",
    "27KOhm",
    "15pF",
    "100F",
    "17,000R",
    "33.333uF",
    "22.1234R",
    "1R05",
    "test",
    "13picofarad",
    "15p"]

for t in tests:
    print(t,compMatch(t))
        
