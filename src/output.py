import math
from collections import OrderedDict


SECTIONS_NAMES = ["[settings]\n", "[inds]\n", "[coor]\n", "[contact]\n", "[force]\n", "[elements' material]\n"]


class IndexedFile:
    def __init__(self, filename=False):
        self.index = 1
        self.output = False
        if filename:
            self.output = open(filename, 'w')

    def write(self, str):
        if self.output:
            self.output.write("{:4d}:\t {}".format(self.index, str))
            self.index += 1

    def close(self):
        if self.output:
            self.output.close()


class Output:
    """
    Вспомогательный класс для записи данных разбиения в pmd-файл
    """

    def __init__(self, filename, sortElements, splitPMD):
        self.OUT = open(filename, "w")
        self.needSortElements = sortElements
        self.needSplitPMD = splitPMD

        if self.needSplitPMD:
            self.OUT_elems = IndexedFile(filename + ".elements")
            self.OUT_nodes = IndexedFile(filename + ".nodes")
            self.OUT_material = IndexedFile(filename + ".material")
        else:
            self.OUT_elems = IndexedFile()
            self.OUT_nodes = IndexedFile()
            self.OUT_material = IndexedFile()

        # Elements are stored by indexes of it vertices: (index1, index2, index3)
        self.elements = []
        # Nodes are stored by its coordinates: (x, y, the node's index)
        self.nodes = []
        # Material of nodes is: '0' for air, '1' for figure
        self.material = []

        self.last_index = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.write_mesh_down()

        self.OUT.close()
        self.OUT_elems.close()
        self.OUT_nodes.close()
        self.OUT_material.close()

    def save_element(self, index_A, index_B, index_C, material):
        self.elements.append((index_A, index_B, index_C))
        self.material.append(material)

    def save_node(self, x, y):
        self.nodes.append((x, y, self.last_index))
        self.last_index += 1

    def write_mesh_down(self):
        if self.needSortElements:
            self.sort_elements()

        self.sort_nodes()
        excessive_indexes, nodes_amount = self.find_excessive_indexes()
        # 'excessive_indexes' – list of pairs "duplicate index" - "original"
        elements_amount = self.adjust_elements(excessive_indexes)

        output = self.OUT
        output.write(SECTIONS_NAMES[0])  # settings
        output.write("n_nodes={}\n".format(nodes_amount))
        output.write("n_elements={}\n".format(elements_amount))
        output.write("n_forces=0\n")
        output.write("n_contacts=0\n")

        output.write(SECTIONS_NAMES[1])  # elements
        self.write_elements()

        output.write(SECTIONS_NAMES[2])  # coordinate of the nodes
        self.write_nodes(excessive_indexes)

        output.write(SECTIONS_NAMES[3])  # contacts
        output.write(SECTIONS_NAMES[4])  # force

        output.write(SECTIONS_NAMES[5])  # elements' material
        self.write_material()

    def sort_elements(self):
        """
        Sort elements by y-coordinate of first node and element's average x-coordinate
        """
        sorted_ = list()
        for i, (A, B, C) in enumerate(self.elements):
            x1 = self.nodes[A][0]
            x2 = self.nodes[B][0]
            x3 = self.nodes[C][0]
            x = (x1 + x2 + x3) / 3
            y = self.nodes[A][1]
            meta_element = (A, B, C, self.material[i], x, y)
            sorted_.append(meta_element)
        sorted_.sort(key=lambda elem: (elem[5], elem[4]))

        for i, elem in enumerate(sorted_):
            self.elements[i] = (elem[0], elem[1], elem[2])
            self.material[i] = elem[3]

    def sort_nodes(self):
        self.nodes.sort(key=lambda coor: (coor[1], coor[0]))  # sort by y-coordinate
        self.rearanged_nodes = [-1] * len(self.nodes)
        for i, (x, y, index) in enumerate(self.nodes):
            self.rearanged_nodes[index] = i

    def find_excessive_indexes(self):
        """
        Mark indexes of nodes-duplicates
        Return list of pairs of them and their originals
        """
        excessive_indexes = list()
        for i, (curr_x, curr_y, curr_index) in enumerate(self.nodes):
            # Seek duplicates of current nodes (by coordinates),
            #   mark down all pairs of duplicate-original.
            # Because nodes are sorted, possible duplicates are
            #   immediately after this in 'self.nodes' list.
            #   Also, because of sorting we need to adjust indexes
            #   via 'self.rearanged_nodes'
            for j in range(i+1, len(self.nodes)):
                next_x, next_y, next_index = self.nodes[j]
                if not math.isclose(curr_y, next_y):
                    break

                if math.isclose(curr_x, next_x):
                    c_i_sorted = self.rearanged_nodes[curr_index]
                    already_excessive = False
                    for (already_removed_index, _) in excessive_indexes:
                        if c_i_sorted == already_removed_index:
                            already_excessive = True
                            break

                    if not already_excessive:
                        n_i_sorted = self.rearanged_nodes[next_index]
                        excessive_indexes.append((n_i_sorted, c_i_sorted))

        return excessive_indexes, len(self.nodes) - len(excessive_indexes)

    def adjust_elements(self, excessive_indexes):
        excessive_indexes.sort(key=lambda coord: coord[0])
        # 'min_dup' and 'max_dup' will set borders for search for duplicates
        min_dup, max_dup = -1, -1
        if len(excessive_indexes) != 0:
            min_dup = excessive_indexes[0][0]  # lowest index of a duplicate node
            max_dup = excessive_indexes[-1][0]  # highest index of a duplicate node

        # OrderedDict will keep order of our elements and their material
        # If a mesh with overlaying elements would be created, it'll remove them
        #   and figure out the element's material
        pre_output = OrderedDict()

        # Remove excessive nodes and adjust indexing
        for i, (A, B, C) in enumerate(self.elements):
            if len(excessive_indexes) != 0:
                A = self.adjust_node_index(min_dup, max_dup, excessive_indexes, A)
                B = self.adjust_node_index(min_dup, max_dup, excessive_indexes, B)
                C = self.adjust_node_index(min_dup, max_dup, excessive_indexes, C)

            # '-1' because the boss wants indexing from '1', not '0'
            key = "{} {} {}\n".format(A+1, B+1, C+1)
            if key not in pre_output:  # Remove duplicate elements
                pre_output[key] = self.material[i]
            else:
                pre_output[key] += self.material[i]

        self.elements = pre_output.keys()

        for i, value in enumerate(pre_output.values()):
            self.material[i] = 0 if value == 0 else 1

        return len(self.elements)

    def adjust_node_index(self, min_duplicate, max_duplicate, excessive_indexes, index):
        index = self.rearanged_nodes[index]
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

    def write_elements(self):
        for element in self.elements:
            self.OUT.write(element)  # 'element' is already prepared string
            self.OUT_elems.write(element)

    def write_nodes(self, excessive_indexes):
        # 'min_dup' and 'max_dup' set borders in search for duplicates
        min_dup, max_dup = -1, -1
        if len(excessive_indexes) != 0:
            min_dup = excessive_indexes[0][0]  # lowest index of a duplicate node
            max_dup = excessive_indexes[-1][0]  # highest index of a duplicate node

        for x, y, unsorted_curr_index in self.nodes:
            curr_index = self.rearanged_nodes[unsorted_curr_index]

            if curr_index < min_dup or curr_index > max_dup:
                line = "{} {}\n".format(x, y)
                self.OUT.write(line)
                self.OUT_nodes.write(line)
                continue

            isDuplicate = False
            for duplicate, _ in excessive_indexes:
                if curr_index == duplicate:
                    isDuplicate = True
                    break
            if not isDuplicate:
                line = "{} {}\n".format(x, y)
                self.OUT.write(line)
                self.OUT_nodes.write(line)

    def write_material(self):
        for value in self.material:
            line = "{}\n".format(value)
            self.OUT.write(line)
            self.OUT_material.write(line)
