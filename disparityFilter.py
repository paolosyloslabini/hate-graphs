# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 15:14:55 2022

@author: Paolo
"""


import argparse
import os
import numpy as np

class CSR: 
    def __init__(self):
        self.clean()
        
    def clean(self):
        self.N = 0
        self.nzcount = []
        self.pos = []
        self.vals = []
        
    def __str__(self):
        print("N:", self.N)
        print("nzcount: ", self.nzcount)
        #print("pos: ", self.pos)
        #print("vals: ", self.vals)
        return " "
        
    def fill_from_edgelist(self,edgelist_file, delimiter = " "):
        #must be a sorted edgelist (gaps allowed)
        self.clean()
        warning = False
        with open(edgelist_file) as f:
            for line in f:
                linesplit = line.split(delimiter)
                inc = int(linesplit[0]);
                out = int(linesplit[1]);
                try:
                    weight = float(linesplit[2])
                except: 
                    warning = True
                    weight = np.random.random();
                
                while inc > self.N - 1:
                    #create new node;
                    self.add_node()
                    
                self.add_edge(row = -1, col = out, weight = weight)
                
        if warning:
            print("WARNING! used random weights!")
        return self.N;
    
    def add_node(self):
        self.N += 1
        self.nzcount.append(0)
        self.pos.append([])
        self.vals.append([])
    
    def add_edge(self, row, col, weight):
        self.nzcount[row] += 1;
        self.pos[row].append(col);
        self.vals[row].append(weight)
    
    def symmetrize_add(self):
        #BUG
        for i in range(self.N):
            for j in range(self.nzcount[i]):
                col = self.pos[i][j];
                if col not in self.pos[j]:
                    self.add_edge(j,col,self.vals[i][j]);
        for i in range(self.N):
            #reorder each node list
            self.pos[i], self.vals[i] = zip(*sorted(zip(self.pos[i],self.vals[i]), key = lambda x : x[0]))
            
    def symmetrize_del(self):
        #BUG
        for i in range(self.N):
            for j in range(self.nzcount[i]):
                col = self.pos[i][j];
                if col not in self.pos[j]:
                    self.pos[i].pop(j);
                    self.vals[i].pop(j);
        
def disparity_filter(csr, alpha = 0.8):
    if csr.N == 0:
        return -1;
    
    total_weights = np.zeros(csr.N);
    for i in range(csr.N):
        for weight in csr.vals[i]:
            total_weights[i] += weight
            
    filtered_csr = CSR();
    for i in range(csr.N):
        degree = csr.nzcount[i]
        
        filtered_csr.add_node()
        
        for j in range(degree):
            weight = csr.vals[i][j];
            col = csr.pos[i][j];
            keep_edge = filter_eval(weight = weight, degree = degree, total_weight = total_weights[i], alpha = alpha)
            if keep_edge:
                filtered_csr.add_edge(-1, col, weight);
                
    return filtered_csr;
            
def filter_eval(weight, degree, total_weight, alpha):
    p = (1. - 1.*weight/total_weight)**(degree - 1);
    return p < alpha;


graph = CSR();
graph.fill_from_edgelist("test_converted.txt", delimiter = " ")
print(graph)

filtered_graph = disparity_filter(graph)
print(filtered_graph)