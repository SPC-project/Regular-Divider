#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""
Author: Mykolaj Konovalow
    for CMPS department of NTU "KhPI"
    http://web.kpi.kharkov.ua/cmps/ru/kafedra-cmps/

Sort nodes in .pmd file by their coordinates,
    rewrite then elements section properly

argv[1] — input file path ("temp.pmd" as defalut)
argv[2] — if 'True', copy output in separated files
argv[3] — if 'True', rearrange (sort) elements by coordinates
"""

import sys
import logging
from traceback import format_exception
from Combiner import SECTIONS_NAMES


def read_pmd(In, Out=False):
    is_header = True
    is_elements = False
    is_nodes = False
    is_stuff = False

    elements = list()
    coordinates = list()
    material = list()
    index = 0

    for line in In.readlines():
        if is_header:
            if Out:
                Out.write(line)
            if line == SECTIONS_NAMES[1]:
                is_header = False
                is_elements = True
        elif is_elements:
            if line != SECTIONS_NAMES[2]:
                elem = line.split(' ')
                elements.append((int(elem[0]), int(elem[1]), int(elem[2])))
            else:
                is_elements = False
                is_nodes = True
        elif is_nodes:
            if line != SECTIONS_NAMES[3]:
                x, y = [float(coor) for coor in line.split(' ')]
                coordinates.append((x, y, index))
                index += 1
            else:
                is_nodes = False
                is_stuff = True
        elif is_stuff:
            if line == SECTIONS_NAMES[5]:  # skip force and contacts
                is_stuff = False
        else:
            material.append(int(line.strip()))

    return elements, coordinates, material


def sort_nodes(nodes):
    nodes_renames = [-1] * len(nodes)
    nodes.sort(key=lambda line: (line[1], line[0]))  # sort by y-coordinate first
    counter = 0
    for x, y, index in nodes:
        nodes_renames[index] = counter
        counter += 1

    return nodes_renames


def sort_elements(elements, coordinates, material):
    """
    Sort elements by y-coordinate of first node and element's average x-coordinate
    """
    sorted_ = list()
    for i, elem in enumerate(elements):
        A, B, C = elem
        x = coordinates[A][0] + coordinates[B][0] + coordinates[C][0]
        y = coordinates[A][1]
        meta_element = (A, B, C, material[i], x/3, y/3)
        sorted_.append(meta_element)
    sorted_.sort(key=lambda elem: (elem[5], elem[4]))

    for i, elem in enumerate(sorted_):
        elements[i] = (elem[0], elem[1], elem[2])
        material[i] = elem[3]

    return elements, material


def process(In, Out, want_split, want_sorted_grid):
    if want_split:
        Out_nodes = open(out_fname + "_nodes", 'w')
        Out_elements = open(out_fname + "_elements", 'w')
        Out_elements_material = open(out_fname + "_elements-material", 'w')

    elements, coordinates, material = read_pmd(In, Out)
    if want_sorted_grid:
        elements, material = sort_elements(elements, coordinates, material)
    nodes_renames = sort_nodes(coordinates)

    for A, B, C in elements:
        line = "{} {} {}\n".format(nodes_renames[A], nodes_renames[B], nodes_renames[C])
        Out.write(line)
        if want_split:
            Out_elements.write(line)
    Out.write(SECTIONS_NAMES[2])
    for x, y, _ in coordinates:
        line = "{} {}\n".format(x, y)
        Out.write(line)
        if want_split:
            Out_nodes.write(line)
    Out.write(SECTIONS_NAMES[3])
    Out.write(SECTIONS_NAMES[4])
    Out.write(SECTIONS_NAMES[5])
    for index in material:
        line = "{}\n".format(index)
        Out.write(line)  # cause we do not change order in elements
        if want_split:
            Out_elements_material.write(line)

    if want_split:
        Out_nodes.close()
        Out_elements.close()
        Out_elements_material.close()


def my_excepthook(type_, value, tback):
    """
    Перехватывает исключения, логгирует их и позволяет уронить програму
    """
    logging.error(''.join(format_exception(type_, value, tback)))
    sys.__excepthook__(type_, value, tback)


if __name__ == '__main__':
    log_format = 'Sorter.py — [%(asctime)s]  %(message)s'
    logging.basicConfig(format=log_format, level=logging.ERROR,
                        filename='errors.log')
    sys.excepthook = my_excepthook

    in_fname = sys.argv[1] if len(sys.argv) > 1 else "temp.pmd"
    out_fname = in_fname + "_sorted"
    want_split = len(sys.argv) > 2 and sys.argv[2] == "True"
    want_sorted_grid = len(sys.argv) > 3 and sys.argv[3] == "True"

    In = open(in_fname, 'r')
    Out = open(out_fname, 'w')

    process(In, Out, want_split, want_sorted_grid)

    In.close()
    Out.close()
