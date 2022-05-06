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
import bisect
from collections import Counter, defaultdict
import numpy as np


input_bigraph = "bipartite_edgelist_en.csv"
output_bigraph = "bigraph_converted.csv"
mapping_file = "bigraph_map.csv"

graph = {}

mapping = {}   
inverse_mapping = {}
counter = {}

start = timer()





chunck_size = 10000
load = True

if load == True:
    
    with open(input_bigraph) as infile:
        i = 0 
        j = 0
        last_source = None
        firstline = infile.readline()
        for line in infile.readlines():
            i += 1; 
            
            if i > 1000000:
                break
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
    
    exit()
    input()
        
    file_id = 0
    while os.path.exists(f"tmp/bigraph_{file_id}.p"):
        os.remove(f"tmp/bigraph_{file_id}.p")
        file_id += 1
    
    max_len = chunck_size
    current_len = 0
    file_id = 0
    tmp_data = []
    for source,neigh in graph.items():
        current_len += len(neigh)
        tmp_data.append(neigh)
        with open(f"tmp/bigraph_{file_id}.p", "wb") as outfile:
            pickle.dump(tmp_data, outfile)    
        if current_len > max_len:
            current_len = 0
            tmp_data = []
            file_id += 1
            
del graph            

#LOAD AND ANALIZE

file_id = 0
start_0 = timer()


count_chunks = 0
while os.path.exists(f"tmp/bigraph_{count_chunks}.p"):
    count_chunks += 1

print(f"Graph divided in {count_chunks} chunks \n")


file_id = 0
while os.path.exists(f"tmp/local_bigraph_{file_id}.txt"):
    os.remove(f"tmp/local_bigraph_{file_id}.txt")
    file_id += 1

for c in range(count_chunks):
    
    local_bigraph = {}
    start = timer()
    with open(f"tmp/bigraph_{file_id}.p", "rb") as infile:
        chunk = pickle.load(infile)
        file_id += 1
    
    print(f"analyzing chunk {file_id -1} out of {count_chunks}, {len(chunk)} neighbouroods")
    for count, neighbours in enumerate(chunk):
        
        for i,n1 in enumerate(neighbours):
            
            if n1 not in local_bigraph:
                local_bigraph[n1] = {}

            for n2 in neighbours[i+1:]:
                
                if n2 not in local_bigraph:
                    local_bigraph[n2] = {}
                
                if n2 not in local_bigraph[n1]:
                    local_bigraph[n1][n2] = 1
                else:
                    local_bigraph[n1][n2] += 1
                
                if n1 not in local_bigraph[n2]:
                    local_bigraph[n2][n1] = 1
                else:
                    local_bigraph[n2][n1] += 1

    with open(f"tmp/local_bigraph_{file_id}.txt", "w") as outfile:
        for source,neigh in local_bigraph.items():
            for target,val in neigh.items():
                print(f"{source} {target} {val}", file = outfile)
    end = timer()
    print(f"****spent {end - start} seconds")
    
end_0  = timer()