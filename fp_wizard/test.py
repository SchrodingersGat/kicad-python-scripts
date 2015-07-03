from fp_generators import *



TITLE = "TestSMT_30Pads"

fp = Footprint(TITLE)

fp.write(pad_linear_pattern("smd",
                            "oval",
                            (1.25,3),
                            1,
                            30,
                            (-29,0),
                            (2,0),
                            layers = LAYERS_SMT_PAD))

fp.finish()

print("Done")
