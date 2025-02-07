import random


def generate_matrix_and_save_to_file(size, filename, min_val, max_val):
    matrix = [[random.randint(min_val, max_val) for _ in range(size)] for _ in range(size)]

    with open(filename, 'w') as f:
        for row in matrix:
            f.write(' '.join(map(str, row)) + '\n')


if __name__ == '__main__':
    size = 1300
    filename = "input1300.txt"
    min_val = 0
    max_val = 1000

    generate_matrix_and_save_to_file(size, filename, min_val, max_val)
    print(f"Matrix {size}x{size} was generated.")
