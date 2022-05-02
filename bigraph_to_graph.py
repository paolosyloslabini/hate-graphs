# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 17:53:33 2022

@author: Paolo


bipartite to normal
"""
import timeit
import re


input_bigraph = "bipartite_edgelist_en.csv"
output_bigraph = "bigraph_converted.csv"
mapping_file = "bigraph_map.csv"

graph = {}

bigraph = {}

with open(input_bigraph) as infile:
    i = 0    
    firstline = infile.readline()
    for line in infile.readlines():
        i += 1;
        linesplit = line.split(",")
        source = re.escape(linesplit[0])
        target = re.escape(linesplit[1])
        if source not in graph:
            graph[source] = []
        graph[source].append(target)
        
 
print("graph read, with ", len(graph), " sources")

mapping = {}   
inverse_mapping = {}
node_count = 0
time = timeit.timeit()


for i, source in enumerate(graph):
    neighbours = graph[source]
    
    for i,n1 in enumerate(neighbours):
        #add node to mapping
        if n1 not in mapping:
            mapping[n1] = node_count
            inverse_mapping[node_count] = n1
            source_n = node_count
            node_count += 1
            bigraph[source_n] = {}
        else:
            source_n = mapping[n1]
            
        source_neigh = bigraph[source_n]
        
        #add edges
        for n2 in neighbours[i+1:]:
                
                #add node to mapping
                if n2 not in mapping:
                    mapping[n2] = node_count
                    inverse_mapping[node_count] = n2
                    target = node_count
                    node_count += 1
                    bigraph[target] = {}
                else:
                    target = mapping[n2]
                    
                target_neigh = bigraph[target]
                #add n2 to n1 nieghbourood
                if target not in source_neigh:
                    source_neigh[target] = 1
                else:
                    source_neigh[target] += 1
                
                if source_n not in target_neigh:
                    target_neigh[source_n] = 1
                else:
                    target_neigh[source_n] += 1
                    

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
    