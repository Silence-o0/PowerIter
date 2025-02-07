from Pyro4 import expose
import time


class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers

    def solve(self):
        matrix, n = self.read_input()
        epsilon = 0.001
        eigenvalue_vector = [1] * n
        div_sum = 1

        start_time = time.time()
        while div_sum >= epsilon:
            multiply_result, max_val = self.workers[0].multiply_matrix_by_vector_and_max(matrix,
                                                                                         eigenvalue_vector).value

            norm_vector, div_sum = self.workers[0].normalize_and_compare(multiply_result, eigenvalue_vector,
                                                                              max_val).value

            eigenvalue_vector = norm_vector

        total_time = time.time() - start_time
        self.write_output(eigenvalue_vector, total_time)

    @staticmethod
    @expose
    def multiply_matrix_by_vector_and_max(matrix_part, vector):
        result = []
        for row in matrix_part:
            result.append(sum(value * v for value, v in zip(row, vector)))
        max_elem = max(result)
        return result, max_elem

    @staticmethod
    @expose
    def normalize_and_compare(new_vector_part, old_vector_part, max_elem):
        normalize_vector_part = []
        div_sum = 0
        max_elem = max_elem
        for new_val, old_val in zip(new_vector_part, old_vector_part):
            div_val = new_val / max_elem
            normalize_vector_part.append(div_val)
            div_sum += (div_val - old_val) ** 2
        return normalize_vector_part, div_sum

    def read_input(self):
        with open(self.input_file_name, 'r') as f:
            lines = [map(float, line.split()) for line in f]
        n = len(lines)
        if not all(len(row) == n for row in lines):
            raise ValueError("Non-square matrix.")
        return lines, n

    def write_output(self, output, total_time):
        with open(self.output_file_name, 'w') as f:
            f.write("Time: " + str(total_time) + "\n")
            f.write("Eigenvalue vector: "+' '.join(map(str, output)))
