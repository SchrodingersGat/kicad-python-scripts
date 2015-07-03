from fp_generators import *

LIB = "Connectors_JST.pretty"

PAD_W = 0.6
PAD_H = 1.55
PITCH = 1.0

DESCRIPTION = "JST SH Series Connector, Top Entry Type"

def JST_SH_BM(n):
    title = "Connector_JST_SH_BM" + str(n).zfill(2) + "B"
    fp = Footprint(title, DESCRIPTION, lib=LIB)

    #position of support pads
    if (n%2 == 0): #even
        SX = (int(n/2) - 0.5) * PITCH
    else:
        SX = (int(n/2)) * PITCH

    SX += 1.3

    #pads
    fp.pad_linear_pattern_from_center("smd",
                                      "rect",
                                      (PAD_W,PAD_H),
                                      n,
                                      (0,0),
                                      (PITCH,0),
                                      layers = LAYERS_SMT_PAD)


    #support pads
    fp.pad_smd_rect(n + 1,
                    (-SX, -2.525),
                    (1.2,1.8))

    fp.pad_smd_rect(n + 1,
                    (SX, -2.525),
                    (1.2, 1.8))

    X1 = -SX - 0.5
    X2 =  SX + 0.5
    Y1 = -3
    Y2 = -0.2

    #lines
    fp.draw_line(X1, Y1, X2, Y1)
    fp.draw_line(X1, Y2, X2, Y2)
    fp.draw_line(X1, Y1, X1, Y2)
    fp.draw_line(X2, Y1, X2, Y2)
    
    fp.finish()


for i in range(2,16):
    JST_SH_BM(i)
