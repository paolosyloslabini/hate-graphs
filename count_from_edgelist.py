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


input_file = "complete_local_bigraph.txt"
output_bigraph = "counted_bigraph.txt"

with open(input_file, "r") as infile:
    with open(output_bigraph, "w") as outfile:
    
    
        tmp_dict = {}
        last_node = -1
        
        for line in infile.readlines():
            line = line.split(" ")
            n1 = line[0]
            n2 = line[1]
            val = line[2]
            
            if n1 == last_node:
                if n2 not in tmp_dict:
                    tmp_dict[n2] = val
                else:
                    tmp_dict[n2] += val
            
            if n1 != last_node:
                outfile.writelines([f"{last_node} {n2} {val}" for n2, val in tmp_dict.items()])
                last_node = n1
                tmp_dict = {}