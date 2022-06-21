# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 15:14:55 2022

@author: Paolo
"""


import argparse
import os
import numpy as np
import argparse



def symmetrize_graph(edgelist_file, simmetrized_file, delimiter = " "):
    
    
    #save the offset position of each node in the edgelist
    with open(edgelist_file, "r") as infile:
        line_offset = {}
        last_seen = None
        offset = 0;
        for line in infile:
            linesplit = line.split(delimiter)
            inc = int(linesplit[0]);
            out = int(linesplit[1]);
            try:
                weight = float(linesplit[2])
            except: 
                print("ERROR: MISSING EDGE WEIGHT")
                return 0
            
            if inc != last_seen:
                line_offset[inc] = offset
                last_seen = inc
                
            offset += len(line) + 1
        
        
    current_position = 0
    with open(edgelist_file, "r") as infile:
        with open(simmetrized_file, "w") as outfile:
            while True:
                infile.seek(current_position)  
                linesplit = infile.readline()
                if linesplit == '':
                    break
                
                linesplit = linesplit.split(delimiter)
                
                inc = int(linesplit[0]);
                out = int(linesplit[1]);
                try:
                    weight = float(linesplit[2])
                except: 
                    print("ERROR: MISSING EDGE WEIGHT")
                    return 0
                
                print(f"checking edge {inc}-{out}")
                current_position = infile.tell()
                
                if out not in line_offset:
                    print(f"--{out} not found in dict")
                    continue
                infile.seek(line_offset[out])
                new_inc = out
                edge_found = False;
                while True:
                    linesplit = infile.readline().split(delimiter)
                    new_inc = int(linesplit[0]);
                    new_out = int(linesplit[1]);
                    if new_inc != out:
                        print(f"--{inc} not found in {out} edges")
                        break;
                    if new_out == inc:
                        edge_found = True
                        break
                    if new_out > inc:
                        print(f"--{inc} not found in {out} edges")
                        break
                
                if edge_found:
                    outline = str(inc) + delimiter + str(out) + delimiter + str(weight) + "\n"
                    outfile.writelines(outline)
                
                
                

parser = argparse.ArgumentParser(description='Save disparity filtered input to output')
parser.add_argument('--infile', default = "test_converted.txt",
                    help='the file with the original (weighted) edgelist')
parser.add_argument('--outfile', default = "test_symmetrized.txt",
                    help='the file to store the filtered edgelist')
parser.add_argument('--delimiter', default=" ", help='the edegelist delimiter')

args = parser.parse_args()

symmetrize_graph(args.infile, args.outfile)
