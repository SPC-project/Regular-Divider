#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""
Author: Mykolaj Konovalow
    for CMPS department of NTU "KhPI"
    http://web.kpi.kharkov.ua/cmps/ru/kafedra-cmps/

Sort nodes in .pmd file by their coordinates,
    rewrite then elements section properly

argv[1] — input file path ("temp.pmd" as defalut)
argv[2] — if specified, copy output in separated files
"""

import sys
from Combiner import SECTIONS_NAMES

FILENAME = sys.argv[1] if len(sys.argv) > 1 else "temp.pmd"
RESULT = FILENAME + "_sorted"
WANT_SPLIT = len(sys.argv) > 2

In = open(FILENAME, 'r')
Out = open(RESULT, 'w')
Out_nodes = open(RESULT + "_nodes", 'w')
Out_elements = open(RESULT + "_elements", 'w')
Out_nodes_material = open(RESULT + "_nodes-material", 'w')
Out_elements_material = open(RESULT + "_elements-material", 'w')

# Read .pmd
is_header = True
is_elements = False
is_nodes = False
is_stuff = False
is_material = False

elements = list()
nodes = list()
elements_material = list()
nodes_material = list()
index = 0

for line in In.readlines():
    if is_header:
        Out.write(line)
        if line == SECTIONS_NAMES[1]:
            is_header = False
            is_elements = True
    elif is_elements:
        if line != SECTIONS_NAMES[2]:
            elements.append([int(i) for i in line.split(' ')])
        else:
            is_elements = False
            is_nodes = True
    elif is_nodes:
        if line != SECTIONS_NAMES[3]:
            x, y = [float(coor) for coor in line.split(' ')]
            nodes.append([x, y, index])
            index += 1
        else:
            is_nodes = False
            is_stuff = True
    elif is_stuff:
        if line == SECTIONS_NAMES[5]:  # skip force and contacts
            is_stuff = False
            is_material = True
    elif is_material:
        if line != SECTIONS_NAMES[6]:
            nodes_material.append(int(line.strip()))
        else:
            is_material = False
    else:
        elements_material.append(int(line.strip()))

# Sort
nodes_renames = [-1] * len(nodes)
nodes.sort(key=lambda line: (line[1], line[0]))  # sort by y-coordinate first
counter = 0
for x, y, index in nodes:
    nodes_renames[index] = counter
    counter += 1

# Write
for A, B, C in elements:
    line = "{} {} {}\n".format(nodes_renames[A], nodes_renames[B], nodes_renames[C])
    Out.write(line)
    if WANT_SPLIT:
        Out_elements.write(line)
Out.write(SECTIONS_NAMES[2])
for x, y, _ in nodes:
    line = "{} {}\n".format(x, y)
    Out.write(line)
    if WANT_SPLIT:
        Out_nodes.write(line)
Out.write(SECTIONS_NAMES[3])
Out.write(SECTIONS_NAMES[4])
Out.write(SECTIONS_NAMES[5])
for i in range(len(nodes_material)):
    line = "{}\n".format(nodes_material[nodes_renames.index(i)])
    Out.write(line)
    if WANT_SPLIT:
        Out_nodes_material.write(line)
Out.write(SECTIONS_NAMES[6])
for index in elements_material:
    line = "{}\n".format(index)
    Out.write(line)  # cause we do not change order in elements
    if WANT_SPLIT:
        Out_elements_material.write(line)

# Done
In.close()
Out.close()
Out_nodes.close()
Out_elements.close()
Out_nodes_material.close()
Out_elements_material.close()
