from fp_generators import *

LIB = "Connectors_JST_PAD.pretty"

PITCH = 2.0

DESCRIPTION = "JST PAD Series Connector, Side Entry Type, 2.0mm pitch dual row (with boss)"

def JST_PAD_TopEntry(n):
    
    #dual row, so split in two
    if not (n%2 == 0): #whoops!
        return
        
    n_col = n / 2
    
    title = "Connector_JST_PAD_S" + str(n).zfill(2) + "B-PADSS-1"
    fp = Footprint(title, DESCRIPTION, lib=LIB, ref_pos = (0,3), value_pos = (0,-6))
    
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
                                    (0,0),
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
                                    (0,PITCH),
                                    (-PITCH, 0),
                                    starting_pad=1,
                                    pad_increment=2,
                                    drill_size = HOLE_DIA,
                                    layers = LAYERS_THRU_PAD
                                    )
                                    
    #calculate coordinates of pin1
    if (n_col % 2) == 0:
        x = n_col/2 * PITCH - PITCH/2
    else:
        x = n_col/2 * PITCH
        
    y = 0 
    
    #boss
    bx = x + 1.6
    by = y - 1.4
    
    fp.write(fp.pad_string('""',
                            PAD_TYPE_NPTH,
                            PAD_SHAPE_CIRCLE,
                            (bx, by),
                            BOSS_DIA,
                            drill_size = BOSS_DIA,
                            layers = LAYERS_THRU_PAD))
                            
    fp.write(fp.pad_string('""',
                            PAD_TYPE_NPTH,
                            PAD_SHAPE_CIRCLE,
                            (-bx, by),
                            BOSS_DIA,
                            drill_size = BOSS_DIA,
                            layers = LAYERS_THRU_PAD))
                            
    #outline
    #outine width = B
    W = n + 2
    H = 8
    
    x1 = -W / 2
    x2 =  W / 2
    y1 = -10.7
    y2 = PITCH + 0.5
    
    fp.draw_line(x1, y2, x2, y2)
    fp.draw_line(x1, y1, x2, y1)
    fp.draw_line(x1, y1, x1, y2)
    fp.draw_line(x2, y1, x2, y2)
    
    #draw the tab also
    #6 wide, 2 high
    fp.draw_line(-3, y2, -3, y2 + 2)
    fp.draw_line( 3, y2,  3, y2 + 2)
    fp.draw_line(-3, y2 + 2, 3, y2 + 2)
                            
    fp.finish()

conns = [10, 12, 14, 16, 20, 24]

for c in conns:
    JST_PAD_TopEntry(c)
    
print("Done")
input()
