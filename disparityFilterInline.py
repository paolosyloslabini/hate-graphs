# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 15:14:55 2022

@author: Paolo
"""


import argparse
import os
import numpy as np
import argparse



def disparity_filter(edgelist_file, filtered_file, alpha = 0.8, delimiter = " "):
    last_visited = -1
    neigh_list = []
    weight_list = []
    
    def print_filtered():
        total_weight = sum(weight_list)
        degree = len(weight_list)
        
        for n, w in zip(neigh_list, weight_list):
            p = (1. - 1.*w/total_weight)**(degree - 1);
            if p < alpha:
                outline = str(last_visited) + delimiter + str(n) + delimiter + str(w) + "\n"
                outfile.writelines(outline)
    
    with open(edgelist_file, "r") as infile:
        with open(filtered_file, "w") as outfile:
            for line in infile:
                
                linesplit = line.split(delimiter)
                inc = int(linesplit[0]);
                out = int(linesplit[1]);
                try:
                    weight = float(linesplit[2])
                except: 
                    print("ERROR: MISSING EDGE WEIGHT")
                    return 0
                
                
                if inc != last_visited:
                    print_filtered()
                    
                    #start new node
                    neigh_list = []
                    weight_list = []
                    last_visited = inc
                    
                #store neighbours and weights
                neigh_list.append(out)
                weight_list.append(weight)
                
            #print last stored node
            print_filtered()
            
            


parser = argparse.ArgumentParser(description='Save disparity filtered input to output')
parser.add_argument('--alpha', type=float, default = 0.8,
                    help='filter threshold')
parser.add_argument('--infile', default = "counted_bigraph.txt",
                    help='the file with the original (weighted) edgelist')
parser.add_argument('--outfile', default = "filtered_bigraph.txt",
                    help='the file to store the filtered edgelist')
parser.add_argument('--delimiter', default=" ", help='the edegelist delimiter')

args = parser.parse_args()

disparity_filter(args.infile, args.outfile, args.alpha, args.delimiter)