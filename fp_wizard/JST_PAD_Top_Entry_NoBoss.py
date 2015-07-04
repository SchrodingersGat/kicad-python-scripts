from fp_generators import *

LIB = "Connectors_JST_PAD.pretty"

PITCH = 2.0

DESCRIPTION = "JST PAD Series Connector, Top Entry Type, 2.0mm pitch dual row"

def JST_PAD_TopEntry(n):
    
    #dual row, so split in two
    if not (n%2 == 0): #whoops!
        return
        
    n_col = int(n / 2)
    
    title = "Connector_JST_PAD_B" + str(n).zfill(2) + "B-PADSS-F"
    fp = Footprint(title, DESCRIPTION, lib=LIB, ref_pos = (0,6), value_pos = (0,-6))
    
    HOLE_DIA = 0.7
    PAD_DIA = 1.3
    
    BOSS_DIA = 1.0
    
    #make the pads
    #top row (starts at pin 2)
    fp.pad_linear_pattern_from_center(
                                    PAD_TYPE_THRU,
                                    PAD_SHAPE_CIRCLE,
                                    PAD_DIA,
                                    n_col,
                                    (0,-PITCH),
                                    (-PITCH, 0),
                                    starting_pad=2,
                                    pad_increment=2,
                                    drill_size = HOLE_DIA,
                                    layers = LAYERS_THRU_PAD
                                    )
    
    #bottom row (starts at pin 1)
    fp.pad_linear_pattern_from_center(
                                    PAD_TYPE_THRU,
                                    PAD_SHAPE_CIRCLE,
                                    PAD_DIA,
                                    n_col,
                                    (0,0),
                                    (-PITCH, 0),
                                    starting_pad=1,
                                    pad_increment=2,
                                    drill_size = HOLE_DIA,
                                    layers = LAYERS_THRU_PAD
                                    )
                            
    #outline
    #outine width = B
    W = n + 2
    H = 8
    
    x1 = -W / 2
    x2 =  W / 2
    y1 = -H / 2 - 1
    y2 =  H / 2 - 1
    
    fp.draw_line(x1, y2, x2, y2)
    fp.draw_line(x1, y1, x2, y1)
    fp.draw_line(x1, y1, x1, y2)
    fp.draw_line(x2, y1, x2, y2)
    
    #draw the tab also
    #6 wide, 2 high
    fp.draw_line(-2.5, y2, -2.5, y2 + 1)
    fp.draw_line(-5, y2,  -5, y2 + 1)
    fp.draw_line(-5, y2+1, -2.5, y2 + 1)

    fp.draw_line(2.5, y2, 2.5, y2 + 1)
    fp.draw_line(5, y2,  5, y2 + 1)
    fp.draw_line(5, y2+1, 2.5, y2 + 1)
                            
    fp.finish()

conns = [10, 12, 14, 16, 20, 22, 24]

for c in conns:
    JST_PAD_TopEntry(c)
    
print("Done")
input()
