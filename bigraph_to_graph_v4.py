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



def find_in_sorted_list(elem, sorted_list):
    # https://docs.python.org/3/library/bisect.html
    'Locate the leftmost value exactly equal to x'
    i = bisect.bisect_left(sorted_list, elem)
    if i != len(sorted_list) and sorted_list[i] == elem:
        return i
    return -1

def in_sorted_list(elem, sorted_list):
    i = bisect.bisect_left(sorted_list, elem)
    return i != len(sorted_list) and sorted_list[i] == elem



input_bigraph = "bipartite_edgelist_en.csv"
output_bigraph = "bigraph_converted.csv"
mapping_file = "bigraph_map.csv"

graph = {}

bigraph = {}

mapping = {}   
inverse_mapping = {}
counter = {}

start = timer()
load = False

if load == False:
    
    with open(input_bigraph) as infile:
        i = 0 
        j = 0
        firstline = infile.readline()
        for line in infile.readlines():
            i += 1; 
            if i > 10000:
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
                
            if source not in graph:
                graph[source] = []
            graph[source].append(mapping[target])
            
    
    end = timer()
    
    sources = len(graph)
    print("graph read, with ",sources, " sources in ", end - start, " seconds")
    
    start = timer()
    
    for i, source in enumerate(graph):    
        keep = [x for x in graph[source] if counter[x] > 1]
        graph[source] = keep
    
    end = timer()               
        
    print("removed 1-edges in ", end - start, "seconds")
    
    
    max_len = 1000
    current_len = 0
    file_id = 0
    tmp_data = []
    for source,neigh in graph.items():
        
        current_len += len(neigh)
        tmp_data.append(neigh)
        
        if current_len > max_len:
            with open("tmp/bigraph_{file_id}.p", "w") as outfile:
                pickle.dump(tmp_data, outfile)    
            current_len = 0
            tmp_data = []
            file_id += 1
            
            
            
#LOAD AND ANALIZE            
start = timer()

file_id = 0
while os.path.exists("tmp/bigraph_{file_id}.p"):
    
    with open("tmp/bigraph_{file_id}.p") as infile:
        chunk = pickle.load(infile)
        print("analyzed chunk", file_id)
        file_id += 1
    for count, source in enumerate(chunk):
        neighbours = graph[source]
        for i,n1 in enumerate(neighbours):
            if n1 not in bigraph:
                bigraph[n1] = {}
            source_neigh = bigraph[n1]
            
            for n2 in neighbours[i+1:]:
                if n2 not in bigraph:
                    bigraph[n2] = {}
                
                #add n2 to n1 nieghbourood
                target_neigh = bigraph[n2]
                if n2 not in source_neigh:
                    source_neigh[n2] = 1
                else:
                    source_neigh[n2] += 1
                
                if n1 not in target_neigh:
                    target_neigh[n1] = 1
                else:
                    target_neigh[n1] += 1

print("graph trasnformed in", end-start, "seconds")

graph = {}


start = timer()

for s, neigh in list(bigraph.items()):
    tmp_dict = {}
    for t, val in list(neigh.items()):
        if val != 1:
            tmp_dict[t] = val
    if len(tmp_dict) == 0:
        bigraph.pop(s)
    else:
        bigraph[s] = tmp_dict

end = timer()

print("graph cleaned in", end - start, "seconds")

count = 0;
new_mapping = {}
for s in bigraph:
    new_mapping[s] = count
    count += 1
    
with open(output_bigraph, "w") as outfile:
    for source,neigh in bigraph.items():
        s_n = new_mapping[source]
        for target in sorted(list(neigh), key = lambda x: new_mapping[x]):
            val = neigh[target]
            t_n = new_mapping[target]
            line = str(s_n) + "," + str(t_n) + "," + str(val) + "\n"
            outfile.writelines(line)
            

print("bigraph saved")

with open(mapping_file, "w") as mapfile:
    for thing,name in mapping.items():
        if name in new_mapping:
            mapfile.writelines(str(thing) +","+ str(new_mapping[name]) + "\n")

print("bigraph map saved")