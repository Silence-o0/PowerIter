from Pyro4 import expose


class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers

    def solve(self):
        matrix, n = self.read_input()
        epsilon = 0.0001
        eigenvalue_vector = ['1'] * n
        div_sum = 1

        while div_sum >= epsilon:
            multiply_result = Solver.multiply_matrix_by_vector_and_max(matrix, eigenvalue_vector)
            max_elem = max(multiply_result)

            iter_result, div_sum = Solver.normalize_and_compare(multiply_result, eigenvalue_vector, max_elem)
            eigenvalue_vector = iter_result

        self.write_output(eigenvalue_vector)

    @staticmethod
    @expose
    def multiply_matrix_by_vector_and_max(matrix_part, vector):
        result = []
        for row in matrix_part:
            result.append(sum(float(value) * float(v) for value, v in zip(row, vector)))
        return result

    @staticmethod
    @expose
    def normalize_and_compare(new_vector_part, old_vector_part, max_elem):
        normalize_vector_part = []
        div_sum = 0
        for new_val, old_val in zip(new_vector_part, old_vector_part):
            div_val = float(new_val) / max_elem
            normalize_vector_part.append(div_val)
            div_sum += (div_val - float(old_val)) ** 2
        return normalize_vector_part, div_sum

    def read_input(self):
        with open(self.input_file_name, 'r') as f:
            lines = [list(map(float, line.split())) for line in f]
        n = len(lines)
        if not all(len(row) == n for row in lines):
            raise ValueError("Non-square matrix.")
        return lines, n

    def write_output(self, output):
        with open(self.output_file_name, 'w') as f:
            f.write(' '.join(map(str, output)))