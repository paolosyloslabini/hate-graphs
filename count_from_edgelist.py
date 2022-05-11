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
    
    
        tmp_n2s = []
        tmp_vals = []
        last_n1 = -1
        last_n2 = -1
        
        for line in infile.readlines():
            line = line.split(" ")
            n1 = line[0]
            n2 = line[1]
            val = line[2]
            
            if n1 == last_n1:
                if n2 != last_n2:
                    tmp_n2s.append(n2)
                    tmp_vals.append(val)
                else:
                    tmp_vals[-1] += val    
                    
                    
            if n1 != last_n1:
                outfile.writelines([f"{last_n1} {tmp_n2s[i]} {tmp_vals[i]}" for i in range(len(tmp_vals))])
                tmp_n2s = []
                tmp_vals = []
                last_n1 = -1
        last_n2 = -1