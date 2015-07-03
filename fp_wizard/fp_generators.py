#Layer definitions
LAYER_F_SILK = "F.SilkS"
LAYER_B_SILK = "F.SilkS"
LAYER_F_FAB = "F.Fab"
LAYER_B_FAB = "B.Fab"
LAYER_F_CU = "F.Cu"
LAYER_B_CU = "B.Cu"
LAYER_ALL_CU = "*.Cu"
LAYER_ALL_SILK = "*.SilkS"
LAYER_F_MASK = "F.Mask"
LAYER_B_MASK = "B.Mask"
LAYER_ALL_MASK = "*.Mask"
LAYER_F_PASTE = "F.Paste"
LAYER_B_PASTE = "B.Paste"
LAYER_ALL_PASTE = "*.Paste"

LAYERS_SMT_PAD = [LAYER_F_CU, LAYER_F_PASTE, LAYER_F_MASK]
LAYERS_THRU_PAD = [LAYER_ALL_CU, LAYER_ALL_MASK, LAYER_F_SILK]

TEXT_TYPE_VALUE = "value"
TEXT_TYPE_REFERENCE = "reference"

PAD_SHAPE_RECT = "rect"
PAD_SHAPE_CIRCLE = "circle"
PAD_SHAPE_OVAL = "oval" 

PAD_TYPE_SMD = "smd"
PAD_TYPE_THRU = "thru_hole"

DRILL_TYPE_CIRCLE = "circle"
DRILL_TYPE_OVAL = "oval"

DEFAULT_LINE_WIDTH = 0.2


class Footprint:
    def __init__(self, title):
        self.title = title

        self.fpFile = open(title + ".kicad_mod", "w")

        self.write(module_start(title))
        self.write(ref_string((0,5)))
        self.write(value_string(title,(0,-5)))

    def write(self, data):
        self.fpFile.write(data)

    def finish(self):
        self.write(")")
        self.fpFile.close()
        
def module_start(title):
    return "(module " + title + " (layer " + LAYER_F_CU + ")\n"

#generate a ref string
def ref_string(pos):
    x,y = pos

    out = "(fp_text reference REF** "
    out += at_string(x,y) + " "
    out += "(layer " + LAYER_F_SILK + ")"
    out += "\n\t"
    out += "(effects (font (size 1 1) (thickness " + str(DEFAULT_LINE_WIDTH) + ")))"
    out += "\n)\n"

    return out

def value_string(title, pos):
    x,y = pos

    out = "(fp_text value " + title + " "
    out += at_string(x,y) + " "
    out += "(layer " + LAYER_F_FAB + ")"
    out += "\n\t"
    out += "(effects (font (size 1 1) (thickness " + str(DEFAULT_LINE_WIDTH) + ")))"
    out += "\n)\n"

    return out
    

def pair_string(desig, *args):

    out = "(" + str(desig) + " "

    for i,arg in enumerate(args):
        out += str(arg)
        if i < (len(args)-1): out += " "

    out += ")"
    return out

def start_string(x, y):
    return pair_string("start",x,y)

def end_string(x,y):
    return pair_string("end", x, y)

def width_string(w):
    return pair_string("width", w)

def at_string(x, y, rot=None):
    if rot is None: #no rotation
        return pair_string("at", x, y)
    else:
        return pair_string("at", x, y, rot)

def size_string(x, y=None):
    if y is None:
        return pair_string("size", x, x)
    else:
        return pair_string("size", x, y)

#pass a list of layers, return a layers string
def layers_string(layers):
    out = "(layers "

    for i,layer in enumerate(layers):
        out += layer
        if i < (len(layers)-1): out += " "

    out += ")"

    return out

#draw a line from (x1,y1) to (x2,y1) on layer(s) l, thickness = t
def mod_line(x1, y1, x2, y2, layers=[LAYER_F_SILK], t=DEFAULT_LINE_WIDTH):
    out = ""
    out += "(fp_line "
    out += start_string(x1, y1) + " "
    out += end_string(x2, y2) + " "
    out += layers_string(layers) + " "
    out += width_string(t)
    out += ")"
    
    return out

def drill_circle(dia):
    out = "(drill "
    out += str(dia)
    out += ")"

    return out

def drill_oval(dia_x, dia_y):
    out = "(drill " + DRILL_TYPE_OVAL + " "
    out += str(dia_x)
    out += " "
    out += str(dia_y)
    out += ")"

    return out

def pad_string(pad_num, pad_type, pad_shape, pad_loc, pad_size, rotation=None, drill_size=None, layers=[]):

    out = "(pad "
    out += str(pad_num)
    out += " "
    out += pad_type + " " + pad_shape + " "

    #pad location (tuple)
    if not isinstance(pad_loc, tuple):
        raise TypeError("pad_loc must be supplied as a tuple")
    x,y = pad_loc
    out += at_string(x,y,rot=rotation) + " "

    #pad size (can be same in x/y or 
    if isinstance(pad_size, int) or isinstance(pad_size, float):
        out += size_string(pad_size) + " "
    elif isinstance(pad_size, tuple):
        w,h = pad_size
        out += size_string(w,h) + " "
    else:
        raise TypeError("pad_size must be either int, float or tuple")


    #drill size (either circular or oval)
    if not drill_size is None:
        if isinstance(drill_size, int) or isinstance(drill_size, float):
            out += drill_circle(drill_size) + " "
        elif isinstance(drill_size, tuple):
            dx,dy = drill_size
            out += drill_oval(dx, dy) + " "
        else:
            raise TypeError("drill_size must be int, float or tuple")

    #layers
    out += layers_string(layers)

    out += ")\n"

    return out

def pad_smd_rect(pad_num, pad_loc, pad_size, rot=None, layers=LAYERS_SMT_PAD):

    return pad_string(pad_num, "smd", "rect", pad_loc, pad_size, rot=rot, layers=layers)

def pad_smd_circle(pad_num, pad_loc, pad_size, rot=None, layers=LAYERS_SMT_PAD):

    return pad_string(pad_num, "smd", "circle", pad_loc, pad_size, rot=rot, layers=layers)

def pad_smd_oval(pad_num, pad_loc, pad_size, rot=None, layers=LAYERS_SMT_PAD):

    return pad_string(pad_num, "smd", "oval", pad_loc, pad_size, rot=rot, layers=layers)

def pad_thru_rect(pad_num, pad_loc, pad_size, drill_size, rot=None, layers=LAYERS_THRU_PAD):

    return pad_string(pad_num, "thru", "rect", pad_loc, pad_size, drill_size = drill_size, rot=rot, layers = layers)

def pad_thru_circle(pad_num, pad_loc, pad_size, drill_size, rot=None, layers=LAYERS_THRU_PAD):

    return pad_string(pad_num, "thru", "circle", pad_loc, pad_size, drill_size = drill_size, rot=rot, layers = layers)

def pad_thru_oval(pad_num, pad_loc, pad_size, drill_size, rot=None, layers=LAYERS_THRU_PAD):

    return pad_string(pad_num, "thru", "oval", pad_loc, pad_size, drill_size=drill_size, rot=rot, layers=layers)

#make a linear pattern of pads
def pad_linear_pattern(pad_type, pad_shape, pad_size, num_start, num_el, start_pos, delta_pos, drill_size = None, rot=None, layers = []): 

    out = ""

    x0, y0 = start_pos
    dx, dy = delta_pos

    for i in range(num_start, num_start+num_el):
        out += "\t"

        x = x0 + i * dx
        y = y0 + i * dy

        out += pad_string(i, pad_type, pad_shape, (x,y), pad_size, drill_size=drill_size, rotation=rot, layers=layers) 
    
    return out
