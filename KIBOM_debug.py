import sys

global DEBUG

DEBUG = True

def Debug(*arg):
    global DEBUG
    if DEBUG:
        print >> sys.stdout, " ".join(map(str,arg))