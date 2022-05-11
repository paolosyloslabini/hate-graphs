# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 17:53:33 2022

@author: Paolo


bipartite to normal
"""
from timeit import default_timer as timer
import re
import pickle
import os
from collections import Counter, defaultdict
import numpy as np


input_file = "tmp/complete_local_bigraph.txt"
output_bigraph = "counted_bigraph.txt"

with open(input_file, "r") as infile:
    with open(output_bigraph, "w") as outfile:
    
    
        tmp_val = 0
        last_n1 = -1
        last_n2 = -1
        
        for line in infile.readlines():
            line = line.split(" ")
            n1 = line[0]
            n2 = line[1]
            val = line[2]


            if n2 != last_n2 or n1 != last_n1:
                outfile.write(f"{last_n1} {last_n2} {tmp_val}")
                print(last_n1, last_n2, tmp_val)
                last_n2 = n2
                tmp_val = 0
            if n1 != last_n1:
                last_n1 = n1
            
            tmp_val += val