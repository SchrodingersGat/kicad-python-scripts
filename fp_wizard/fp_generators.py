import sys,os

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
PAD_TYPE_NPTH = "np_thru_hole"

DRILL_TYPE_CIRCLE = "circle"
DRILL_TYPE_OVAL = "oval"

DEFAULT_LINE_WIDTH = 0.2


class Footprint:
    def __init__(self, title, description, ref_pos=(0,5), value_pos=(0,-5), lib=None):
        self.title = title

        filename = title + ".kicad_mod"
        
        if not lib is None:
            #check if the dir actually exists!!
            if not os.path.exists(lib):
                os.mkdir(lib)
                
            filename = lib + "\\" + filename
            
        print("creating footprint -",filename)
            
        self.fpFile = open(filename + ".kicad_mod", "w")

        self.start(title)
        self.write(self.description_string(description))
        self.write(self.ref_string(ref_pos))
        self.write(self.value_string(title,value_pos))

    def __del__(self):
        if not self.fpFile.closed:
            self.finish()

    def write(self, data):
        self.fpFile.write(data)

    def description_string(self, desc):
        out = "(descr \"" + desc + "\")\n"
        return out
        
    def finish(self):
        self.write(")")
        self.fpFile.close()
        
    def start(self,title):
        self.write("(module " + title + " (layer " + LAYER_F_CU + ")\n")


    #generate a ref string
    def ref_string(self,pos):
        x,y = pos

        out = "(fp_text reference REF** "
        out += self.at_string(x,y) + " "
        out += "(layer " + LAYER_F_SILK + ")"
        out += "\n\t"
        out += "(effects (font (size 1 1) (thickness " + str(DEFAULT_LINE_WIDTH) + ")))"
        out += "\n)\n"

        return out

    def value_string(self,title, pos):
        x,y = pos

        out = "(fp_text value " + title + " "
        out += self.at_string(x,y) + " "
        out += "(layer " + LAYER_F_FAB + ")"
        out += "\n\t"
        out += "(effects (font (size 1 1) (thickness " + str(DEFAULT_LINE_WIDTH) + ")))"
        out += "\n)\n"

        return out
        

    def pair_string(self,desig, *args):

        out = "(" + str(desig) + " "

        for i,arg in enumerate(args):
            out += str(arg)
            if i < (len(args)-1): out += " "

        out += ")"
        return out

    def start_string(self,x, y):
        return self.pair_string("start",x,y)

    def end_string(self,x,y):
        return self.pair_string("end", x, y)

    def width_string(self,w):
        return self.pair_string("width", w)

    def at_string(self,x, y, rot=None):
        if rot is None: #no rotation
            return self.pair_string("at", x, y)
        else:
            return self.pair_string("at", x, y, rot)

    def size_string(self,x, y=None):
        if y is None:
            return self.pair_string("size", x, x)
        else:
            return self.pair_string("size", x, y)

    #pass a list of layers, return a layers string
    def layers_string(self,layers):
        out = "(layers "

        for i,layer in enumerate(layers):
            out += layer
            if i < (len(layers)-1): out += " "

        out += ")"

        return out

    #draw a line from (x1,y1) to (x2,y1) on layer(s) l, thickness = t
    def draw_line(self,x1, y1, x2, y2, layer=LAYER_F_SILK, width=DEFAULT_LINE_WIDTH):
        out = ""
        out += "(fp_line "
        out += self.start_string(x1, y1) + " "
        out += self.end_string(x2, y2) + " "
        out += "(layer " + layer + ") "
        out += self.width_string(width)
        out += ")\n"
        
        self.write(out)

    def drill_string(self,dia,offset=None):
        out = "(drill "

        if isinstance(dia, int) or isinstance(dia, float):
            out += str(dia) 
        elif isinstance(dia, tuple):
            out += DRILL_TYPE_OVAL + " "
            dia_x, dia_y = dia
            out += str(dia_x) + " "
            out += str(dia_y)
        else:
            raise TypeError("Drill diameter should be int, float or (x,y) tuple")
        if not offset is None:
            x,y = offset
            out += " (offset " + str(x) + " " + str(y) + ")"
        
        out += ")"

        return out

    def pad_string(self,pad_num, pad_type, pad_shape, pad_loc, pad_size, rotation=None, drill_size=None, drill_offset=None, layers=[]):

        out = "(pad "
        out += str(pad_num)
        out += " "
        out += pad_type + " " + pad_shape + " "

        #pad location (tuple)
        if not isinstance(pad_loc, tuple):
            raise TypeError("pad_loc must be supplied as a tuple")
        x,y = pad_loc
        out += self.at_string(x,y,rot=rotation) + " "

        #pad size (can be same in x/y or 
        if isinstance(pad_size, int) or isinstance(pad_size, float):
            out += self.size_string(pad_size) + " "
        elif isinstance(pad_size, tuple):
            w,h = pad_size
            out += self.size_string(w,h) + " "
        else:
            raise TypeError("pad_size must be either int, float or tuple")

        
        #drill size (either circular or oval)
        if not drill_size is None:
            out += self.drill_string(drill_size, offset = drill_offset)

        #layers
        out += self.layers_string(layers)

        out += ")\n"

        return out

    def pad_smd_rect(self,pad_num, pad_loc, pad_size, rot=None, layers=LAYERS_SMT_PAD):

        self.write(self.pad_string(pad_num, "smd", "rect", pad_loc, pad_size, rotation=rot, layers=layers))

    def pad_smd_circle(self,pad_num, pad_loc, pad_size, rot=None, layers=LAYERS_SMT_PAD):

        out = self.pad_string(pad_num, "smd", "circle", pad_loc, pad_size, rotation=rot, layers=layers)
        self.write(out)
        
    def pad_smd_oval(self,pad_num, pad_loc, pad_size, rot=None, layers=LAYERS_SMT_PAD):

        out = self.pad_string(pad_num, "smd", "oval", pad_loc, pad_size, rotation=rot, layers=layers)
        self.write(out)
        
    def pad_thru_rect(self,pad_num, pad_loc, pad_size, drill_size, drill_offset=None, rot=None, layers=LAYERS_THRU_PAD):

        out = self.pad_string(pad_num, "thru", "rect", pad_loc, pad_size, drill_size = drill_size, drill_offset=drill_offset, rotation=rot, layers = layers)
        self.write(out)
        
    def pad_thru_circle(self,pad_num, pad_loc, pad_size, drill_size, drill_offset=None, rotation=None, layers=LAYERS_THRU_PAD):

        out = self.pad_string(pad_num, "thru", "circle", pad_loc, pad_size, drill_size = drill_size, drill_offset=drill_offset, rot=rot, layers = layers)
        self.write(out)
        
    def pad_thru_oval(self,pad_num, pad_loc, pad_size, drill_size, drill_offset=None, rotation=None, layers=LAYERS_THRU_PAD):

        out = self.pad_string(pad_num, "thru", "oval", pad_loc, pad_size, drill_size=drill_size, drill_offset=drill_offset, rot=rot, layers=layers)
        self.write(out)
        
    #make a linear pattern of pads
    #pad_type either 'thru' or 'smd'
    #pad_shape either 'rect' 'oval' 'circle'
    #pad_size (x,y) tuple
    #num_pads number of pads in pattern
    #start_pos (x,y) tuple of position of first pad
    #delta_pos (x,y) tuple of position increment to next pad
    #starting_pad ID number of the first pad (default = 1)
    #pad_increment Increment of ID numbers between pads (e.g. starting_pad=1, pad_increment=2 gives pads 1,3,5,7
    def pad_linear_pattern(self,pad_type, pad_shape, pad_size, num_pads, start_pos, delta_pos, starting_pad=1, pad_increment = 1, drill_size = None, drill_offset=None, rot=None, layers = []): 

        out = ""

        x, y = start_pos
        dx, dy = delta_pos

        pad_num = starting_pad

        for i in range(num_pads):
            out += "\t"

            out += self.pad_string(pad_num, pad_type, pad_shape, (x,y), pad_size, drill_size=drill_size, drill_offset=drill_offset, rotation=rot, layers=layers)
            
            x += dx
            y += dy
            
            pad_num += pad_increment
        
        self.write(out)

    #make a linear pattern of pads, but provide the position at the CENTRE of the pattern
    #pad_type either 'thru' or 'smd'
    #pad_shape either 'rect' 'oval' 'circle'
    #pad_size (x,y) tuple
    #num_pads number of pads in pattern
    #start_pos (x,y) tuple of position of first pad
    #delta_pos (x,y) tuple of position increment to next pad
    #starting_pad ID number of the first pad (default = 1)
    #pad_increment Increment of ID numbers between pads (e.g. starting_pad=1, pad_increment=2 gives pads 1,3,5,7
    def pad_linear_pattern_from_center(self,pad_type, pad_shape, pad_size, num_pads, start_pos, delta_pos, starting_pad=1, pad_increment = 1, drill_size = None, drill_offset=None, rot=None, layers = []):
        #work out where the starting position should be!
        dx, dy = delta_pos

        x,y = start_pos

        if (num_pads % 2) == 0: #even number of pads!
            #for an EVEN number of pads, we need to subtract (n/2 - 0.5) from the offset
            x -= (int(num_pads/2) - 0.5) * dx
            y -= (int(num_pads/2) - 0.5) * dy
        else:
            x -= (int(num_pads/2)) * dx
            y -= (int(num_pads/2)) * dy

        out = ""

        pad_num = starting_pad

        for i in range(num_pads):
            out += "\t"

            out += self.pad_string(pad_num, pad_type, pad_shape, (x,y), pad_size, drill_size=drill_size, drill_offset=drill_offset, rotation=rot, layers=layers)

            pad_num += pad_increment
            
            x += dx
            y += dy
        
        self.write(out)
