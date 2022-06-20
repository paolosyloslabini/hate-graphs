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
import argparse 

input_bigraph = "bipartite_edgelist_en.csv"
output_bigraph = "bigraph_converted.csv"
mapping_file = "bigraph_map.csv"

graph = {}

mapping = {}   
inverse_mapping = {}
counter = {}

start = timer()

parser = argparse.ArgumentParser(description='Transforms a bipartite graph into a collection of weighted graphs')
parser.add_argument('--load', type=bool, default = True,
                    help='If true, use edgelist (infile). If false, use precomputed chuncks')
parser.add_argument('--analyze', type=bool, default = True,
                    help='False to only produce the chuncks, not the edgelists')
parser.add_argument('--infile', default = "bipartite_edgelist_en.csv",
                    help='the file with the original edgelist')
parser.add_argument('--folder', default = "tmp",
                    help='where to store the results')
parser.add_argument('--mapfile', default="bigraph_map.csv", help='the mapping file')

args = parser.parse_args()



chunck_size = 10000
load = args.load
analyze = args.analyze

input_bigraph = args.infile
folder = args.folder
mapping_file = args.mapfile

if load == False:
    
    with open(input_bigraph) as infile:
        i = 0 
        j = 0
        last_source = None
        firstline = infile.readline()
        for line in infile.readlines():
            i += 1; 
            linesplit = line.split(",")
            source = re.escape(linesplit[0])
            target = re.escape(linesplit[1])
            
            if target not in mapping:
                mapping[target] = j
                inverse_mapping[j] = target
                counter[j] = 1
                j += 1
            else:
                counter[mapping[target]] += 1
            
            if source != last_source:
                graph[source] = []
                last_source = source
            graph[source].append(mapping[target])
            
    
    end = timer()
    
    sources = len(graph)
    print(f"graph read, with {sources} sources and {j} different targets in {end - start} seconds")
    
    start = timer()
    
    
    #remove things that appear only one time
    for i, source in enumerate(graph):    
        keep = [x for x in graph[source] if counter[x] > 1]
        graph[source] = keep
    
    end = timer()  
    
    
    for i in list(inverse_mapping):
        if counter[i] == 1:
            name = inverse_mapping[i]
            inverse_mapping.pop(i)
            mapping.pop(name)
            
    tmp_mapping = {}
    count = 0
    for name,num in mapping.items():
        tmp_mapping[num] = count
        count += 1
    
    for source in list(graph):
        for i, neigh in enumerate(list(graph[source])):
            graph[source][i] = tmp_mapping[graph[source][i]]
        graph[source] = np.array(graph[source])
            
            
    inverse_mapping = {}
    for name in list(mapping):
        mapping[name] = tmp_mapping[mapping[name]]
        inverse_mapping[mapping[name]] = name
    
    del tmp_mapping 
            
    with open(mapping_file, "w") as mapfile:
        for thing,name in mapping.items():
            mapfile.writelines(str(thing) +","+ str(name) + "\n")
    
    del mapping
    del counter
    del inverse_mapping
        
    print("removed 1-edges in ", end - start, "seconds")
    
    
    
    file_id = 0
    while os.path.exists(f"{folder}/bigraph_{file_id}.p"):
        os.remove(f"{folder}/bigraph_{file_id}.p")
        file_id += 1
    
    max_len = chunck_size
    current_len = 0
    file_id = 0
    tmp_data = []
    for source,neigh in graph.items():
        current_len += len(neigh)
        tmp_data.append(neigh)
        with open(f"{folder}/bigraph_{file_id}.p", "wb") as outfile:
            pickle.dump(tmp_data, outfile)    
        if current_len > max_len:
            current_len = 0
            tmp_data = []
            file_id += 1
            
del graph            

#LOAD AND ANALIZE


if analyze:
        
    file_id = 0
    start_0 = timer()
    
    
    count_chunks = 0
    while os.path.exists(f"{folder}/bigraph_{count_chunks}.p"):
        count_chunks += 1
    
    print(f"Graph divided in {count_chunks} chunks \n")
    
    
    file_id = 0
    while os.path.exists(f"{folder}/local_bigraph_{file_id}.txt"):
        os.remove(f"{folder}/local_bigraph_{file_id}.txt")
        file_id += 1
    
    
    local_file_id = 0;
    file_id = 0
    for c in range(count_chunks):
        
        
        #one bigraph for each chunck of neighbouroods
        local_bigraph = {}
        start = timer()
        with open(f"{folder}/bigraph_{file_id}.p", "rb") as infile:
            chunk = pickle.load(infile)
            chunk = [np.array(x) for x in chunk]
       
        for count, neighbours in enumerate(chunk):
                for i, n1 in enumerate(neighbours):
                    local_bigraph[n1] = {}
                    
        print("local bigraph created")
        
        with open(f"{folder}/local_bigraph_{file_id}.txt", "w") as outfile:
    
            print(len(local_bigraph)**2)
            for n1 in local_bigraph:
                tmp_neigh = {}
    
                for count, neighbours in enumerate(chunk):
                    
                    
                    #only process when n1 is in the neighbourood
                    idx = np.searchsorted(neighbours,n1)
                    if idx < len(neighbours) and neighbours[idx] == n1:
                        for n2 in neighbours:
                            if n1 != n2:
                                if n2 not in tmp_neigh:
                                    tmp_neigh[n2] = 1
                                else:
                                    tmp_neigh[n2] += 1
                    
                outfile.writelines(f"{n1} {n2} {val} \n" for n2,val in tmp_neigh.items())
        
        end = timer()
        print(f"****spent {end - start} seconds")
        file_id +=1
