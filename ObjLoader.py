import numpy as np
import copy


class ObjLoader:

    @staticmethod
    def search_data(data_values, coordinates, skip, data_type):
        for d in data_values:
            if d == skip:
                continue
            if data_type == 'float':
                coordinates.append(float(d))

    @staticmethod
    def load_model(file):

        vert_data = []
        text_data = []
        norm_data = []

        vertex = []
        indices = []
        all_indices = []

        with open(file, 'r') as f:
            line = f.readline()
            while line:
                values = line.split()
                if values[0] == 'v':
                    ObjLoader.search_data(values, vert_data, 'v', 'float')
                elif values[0] == 'vt':
                    ObjLoader.search_data(values, text_data, 'vt', 'float')
                elif values[0] == 'vn':
                    ObjLoader.search_data(values, norm_data, 'vn', 'float')
                elif values[0] == 'f':
                    for value in values[1:]:
                        val = value.split('/')
                        indices.append(int(val[0]) - 1)
                        all_indices.append(val)

                line = f.readline()

            for x in range(int(len(vert_data) / 3)):

                inner_index = 0

                while x != int(all_indices[inner_index][0]) - 1:
                    inner_index += 1

                vertex_index = x
                texture_index = int(all_indices[inner_index][1]) - 1
                normal_index = int(all_indices[inner_index][2]) - 1

                vertex.extend(vert_data[3 * vertex_index: 3 * vertex_index + 3])
                vertex.extend(text_data[2 * texture_index: 2 * texture_index + 2])
                vertex.extend(norm_data[3 * normal_index: 3 * normal_index + 3])

            f.close()

        return np.array(copy.copy(vertex), dtype=np.float32), np.array(copy.copy(indices), dtype=np.uint32)
