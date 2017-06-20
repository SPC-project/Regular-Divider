import os


class Output:
    """
    Вспомогательный класс для записи данных разбиения в промежуточные файлы
    """
    TEMP_DIR = ".temp/"
    FILENAMES = ["elements", "nodes", "elements_material"]

    def __init__(self):
        self.f = {}
        self.last_index = 0
        self.elements_amount = 0

    def __enter__(self):
        if not os.path.isdir(self.TEMP_DIR):
            os.mkdir(self.TEMP_DIR)

        for tmp_name in self.FILENAMES:
            self.f[tmp_name] = open(self.TEMP_DIR + tmp_name + ".tmp", "w")  # TODO: should be "x"
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for tmp_name in self.FILENAMES:
            self.f[tmp_name].close()

    def save_element(self, index_A, index_B, index_C, material):
        self.f[self.FILENAMES[0]].write("{} {} {}\n".format(index_A, index_B, index_C))
        self.f[self.FILENAMES[2]].write("{}\n".format(material))
        self.elements_amount += 1

    def save_node(self, x, y):
        node_text = "{:.4f} {:.4f} {}\n"
        self.f[self.FILENAMES[1]].write(node_text.format(x, y, self.last_index))
        self.last_index += 1
