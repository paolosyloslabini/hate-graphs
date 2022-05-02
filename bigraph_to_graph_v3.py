# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 17:53:33 2022

@author: Paolo


bipartite to normal
"""
import timeit
import re
import pickle
import os


input_bigraph = "bipartite_edgelist_en.csv"
output_bigraph = "bigraph_converted.csv"
mapping_file = "bigraph_map.csv"

graph = {}

bigraph = {}

mapping = {}   
inverse_mapping = {}



with open(input_bigraph) as infile:
    i = 0 
    j = 0
    firstline = infile.readline()
    for line in infile.readlines():
        i += 1;
        linesplit = line.split(",")
        source = re.escape(linesplit[0])
        target = re.escape(linesplit[1])
        if target not in mapping:
            mapping[target] = j
            inverse_mapping[j] = target
            j += 1
        
        if source not in graph:
            graph[source] = []
        graph[source].append(mapping[target])
        

sources = len(graph)
print("graph read, with ",sources, " sources")

node_count = 0
time = timeit.timeit()


for i, source in enumerate(graph):
    filename = "tmp/container_" + str(i) + ".p"

    with open(filename, "wb+") as pickfile:
        pickle.dump(graph[source], pickfile )

for i in range(sources):
    if i%100 == 0:
        print("processing batch", i)
    filename = "tmp/container_" + str(i) + ".p"
    with open(filename,"rb+") as infile:
        neigh = pickle.load(infile)
    keep = []
    
    for j in range(sources):
        if i != j:
            filename2 = "tmp/container_" + str(j) + ".p"
            with open(filename2,"rb+") as file2:
                other_neigh = pickle.load(file2)
            for n1 in neigh:
                if n1 not in keep:
                    if n1 in other_neigh:
                        keep.append(n1)
    keep.sort()    
    with open(filename,"wb+") as outfile:
        pickle.dump(keep, outfile)                   


for i in range(sources):
    filename = "tmp/container_" + str(i) + ".p"
    with open(filename, "rb+") as infile:
        neighbours = pickle.load(infile)
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

print("graph trasnformed")
graph = {}

for s, neigh in list(bigraph.items()):
    for t, val in list(neigh.items()):
        if val == 1:
            bigraph[s].pop(t)
    if len(neigh) == 0:
        bigraph.pop(s)

print("graph cleaned")

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