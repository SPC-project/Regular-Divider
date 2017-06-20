#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Author: Mykolaj Konovalow
   for CMPS department of NTU "KhPI"
   http://web.kpi.kharkov.ua/cmps/ru/kafedra-cmps/

Unite results of dividing (.tmp files) into singular .pmd file
   Remove duplicate nodes and fix created gaps in indexing
   Remove overlaying elements (material ones have priority)

Input:
    argv[1] - destination for combined mesh file
    argv[2] - how many elements are in mesh
"""

import os
import sys
import logging
from traceback import format_exception
from src.output import Output
from collections import OrderedDict

DIR = ".temp/"
EXTENSION = ".tmp"
SECTIONS_NAMES = ["[settings]\n", "[inds]\n", "[coor]\n", "[contact]\n", "[force]\n", "[elements' material]\n"]


def init():
    if not os.path.exists(DIR):
        print("No temporary dir found: " + DIR)
        exit(1)
    files = list()
    if len(sys.argv) > 3:
        files = sys.argv[3:]
    else:
        files = Output.FILENAMES

    for i, item in enumerate(files):
        files[i] = DIR + item + EXTENSION
        if not os.path.isfile(files[i]):
            print("No such file: " + item)
            exit(i + 1)

    return files


def find_excessive_indexes(node_file):
    data = list()
    for line in node_file.readlines():
        node = line.split(' ')
        data.append([float(node[0]), float(node[1]), int(node[2])])
    data.sort(key=lambda x: (x[0], x[1]))

    offset = 1
    excessive_indexes = list()
    for curr_index, node in enumerate(data):
        curr_x = node[0]
        curr_y = node[1]

        offset = 1
        while curr_index + offset < len(data):
            next_node = data[curr_index + offset]
            if next_node[0] != curr_x:
                break

            if next_node[1] == curr_y:
                already_excessive = False
                for (rem_index, _) in excessive_indexes:
                    if rem_index == next_node[2]:
                        already_excessive = True
                        break

                if not already_excessive:
                    excessive_indexes.append([data[curr_index + offset][2], node[2]])
            offset += 1
    node_file.seek(0)  # move cursor to the start of file
    return excessive_indexes, len(data) - len(excessive_indexes)


def adjust_node_index(min_duplicate, max_duplicate, excessive_indexes, index):
    # Rename duplicate nodes
    if index >= min_duplicate and index <= max_duplicate:
        for node in excessive_indexes:
            if index == node[0]:
                index = node[1]
                break

    # Remove possible gap in indexing
    if index > min_duplicate:
        offset = 0
        for ind, _ in excessive_indexes:
            if index >= ind:
                offset += 1
            else:
                break

        index -= offset

    return index


def excessive_elements(excessive_indexes, old_elems, old_elems_material, output):
    min_duplicate, max_duplicate = -1, -1
    if len(excessive_indexes) != 0:
        excessive_indexes.sort(key=lambda coord: coord[0])
        min_duplicate = excessive_indexes[0][0]
        max_duplicate = excessive_indexes[-1][0]

    # Remove excessive nodes and adjust indexing
    pre_output = OrderedDict()  # OrderedDict will keep order of our elements and their material
    for line in elems.readlines():
        element = line.split(' ')
        A, B, C = [int(element[0]), int(element[1]), int(element[2])]
        if min_duplicate != -1:
            A = adjust_node_index(min_duplicate, max_duplicate, excessive_indexes, A)
            B = adjust_node_index(min_duplicate, max_duplicate, excessive_indexes, B)
            C = adjust_node_index(min_duplicate, max_duplicate, excessive_indexes, C)

        material = int(old_elems_material.readline())
        key = "{} {} {}\n".format(A, B, C)
        if key not in pre_output:  # Remove duplicate elements
            pre_output[key] = material
        else:
            pre_output[key] += material

    for elem in pre_output.keys():
        output.write(elem)

    return pre_output.values()


def write_nodes(output, nodes, excessive_indexes):
    index = 0
    for line in nodes.readlines():
        skip = False
        for ind, _ in excessive_indexes:
            if int(ind) == index:
                skip = True
                break
        if not skip:
            x, y, _ = line.split(' ')
            output.write("{} {}\n".format(x, y))
        index += 1


def combine_output(elems, nodes, elems_material, output):
    excessive_indexes, nodes_amount = find_excessive_indexes(nodes)
    output.write(SECTIONS_NAMES[0])  # settings
    output.write("n_nodes={}\n".format(nodes_amount))
    output.write("n_elements={}\n".format(ELEMENTS_AMOUNT))
    output.write("n_forces=0\n")
    output.write("n_contacts=0\n")

    output.write(SECTIONS_NAMES[1])  # elements
    materials = excessive_elements(excessive_indexes, elems, elems_material, output)

    output.write(SECTIONS_NAMES[2])  # nodes
    write_nodes(output, nodes, excessive_indexes)

    output.write(SECTIONS_NAMES[3])  # contacts
    output.write(SECTIONS_NAMES[4])  # force
    output.write(SECTIONS_NAMES[5])  # elements' material
    for mat in materials:
        if mat > 0:
            output.write("1\n")
        else:
            output.write("0\n")


def my_excepthook(type_, value, tback):
    """
    Перехватывает исключения, логгирует их и позволяет уронить програму
    """
    logging.error(''.join(format_exception(type_, value, tback)))
    sys.__excepthook__(type_, value, tback)


if __name__ == '__main__':
    global OUTPUT_FILENAME
    global ELEMENTS_AMOUNT
    OUTPUT_FILENAME = sys.argv[1]
    ELEMENTS_AMOUNT = int(sys.argv[2])

    log_format = 'Combiner.py — [%(asctime)s]  %(message)s'
    logging.basicConfig(format=log_format, level=logging.ERROR,
                        filename='errors.log')
    sys.excepthook = my_excepthook

    ELEMENTS, NODES, ELEMENTS_MATERIAL = init()
    elems = open(ELEMENTS, 'r')
    nodes = open(NODES, 'r')
    elems_material = open(ELEMENTS_MATERIAL, 'r')
    output = open(OUTPUT_FILENAME, 'w')

    combine_output(elems, nodes, elems_material, output)

    nodes.close()
    elems.close()
    output.close()
    exit(0)
