# -*- coding: utf-8 -*-
import sys

def ad_println(str, blank_line = 0):

    str += "\n"
    for i in range(blank_line):
        str = "\n" + str

    sys.stdout.write(str)
    sys.stdout.flush()
