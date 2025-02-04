from Pyro4 import expose
import array as arr


class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers

    def solve(self):
        matrix, n = self.read_input()
        num_workers = len(self.workers)
        epsilon = 0.001
        eigenvalue_vector = arr.array("d", [1] * n)
        div_sum = 1
        step = (n // num_workers)

        while div_sum >= epsilon:
            multiply_result = []
            for i in range(num_workers):
                if i == num_workers - 1:
                    end_row = n
                else:
                    end_row = i * step + step

                multiply_result.append(self.workers[i].multiply_matrix_by_vector_and_max(matrix[i * step:end_row],
                                                                                         eigenvalue_vector))

            new_vector, max_elements = self.reduce(multiply_result)
            max_val = max(max_elements)

            iter_result = []
            for i in range(num_workers):
                if i == num_workers - 1:
                    end_row = n
                else:
                    end_row = i * step + step

                iter_result.append(self.workers[i].normalize_and_compare(new_vector[i * step:end_row],
                                                                         eigenvalue_vector[i * step:end_row],
                                                                         max_val))

            norm_vector, div_sum_arr = self.reduce(iter_result)
            div_sum = sum(div_sum_arr)
            eigenvalue_vector = norm_vector

        self.write_output(eigenvalue_vector)

    @staticmethod
    @expose
    def multiply_matrix_by_vector_and_max(matrix_part, vector):
        result = arr.array("d", [])
        for row in matrix_part:
            result.append(sum(value * v for value, v in zip(row, vector)))
        max_elem = max(result)
        return result, max_elem

    @staticmethod
    @expose
    def normalize_and_compare(new_vector_part, old_vector_part, max_elem):
        normalize_vector_part = arr.array("d", [])
        div_sum = 0
        max_elem = max_elem
        for new_val, old_val in zip(new_vector_part, old_vector_part):
            div_val = new_val / max_elem
            normalize_vector_part.append(div_val)
            div_sum += (div_val - old_val) ** 2
        return normalize_vector_part, div_sum

    @staticmethod
    @expose
    def reduce(result):
        vector = arr.array("d", [])
        value = arr.array("d", [])
        for x in result:
            for j, i in enumerate(x.value):
                if j % 2 == 0:
                    vector.extend(i)
                else:
                    value.append(i)
        return vector, value

    def read_input(self):
        with open(self.input_file_name, 'r') as f:
            lines = [arr.array("d", map(float, line.split())) for line in f]
        n = len(lines)
        if not all(len(row) == n for row in lines):
            raise ValueError("Non-square matrix.")
        return lines, n

    def write_output(self, output):
        with open(self.output_file_name, 'w') as f:
            f.write(' '.join(map(str, output)))
