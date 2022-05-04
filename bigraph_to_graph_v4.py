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

mapping = {}   
inverse_mapping = {}
counter = {}

start = timer()





chunck_size = 10000
load = True

if load == False:
    
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


bigraph = [{} for n in range(1900000)]

for c in range(count_chunks):
    
    chunck_timer = 0
    max_time = 0
    max_elements = 0
    with open(f"tmp/bigraph_{file_id}.p", "rb") as infile:
        chunk = pickle.load(infile)
        file_id += 1
    
    print(f"analyzing chunk {file_id -1} out of {count_chunks}, {len(chunk)} neighbouroods")
    for count, neighbours in enumerate(chunk):

        start = timer() #
        
        for i,n1 in enumerate(neighbours):
            source_neigh = bigraph[n1]
            
            for n2 in neighbours[i+1:]:
                
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
        
        #
        end = timer() #
        
        
        #
        chunck_timer += end - start; #
        max_time = max(max_time, end-start) #
        max_elements = max(max_elements, len(neighbours))
    print(f"************ neighbourood {count},  spent {chunck_timer} seconds, max_neigh_time {max_time}, max_neigh_len {max_elements}")



end_0  = timer()

print("graph trasnformed in", end_0 - start_0, "seconds")
print("graph cleaned in", end - start, "seconds")

with open(output_bigraph, "w") as outfile:
    for s_n,neigh in enumerate(bigraph):
        for t_n in sorted(list(neigh)):
            val = neigh[t_n]
            line = str(s_n) + "," + str(t_n) + "," + str(val) + "\n"
            outfile.writelines(line)
            

print("bigraph saved")