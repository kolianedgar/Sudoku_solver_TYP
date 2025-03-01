import os
from pathlib import Path
import sys

current_dir = os.getcwd()
text_file_path = Path(os.path.join(current_dir, "test.txt"))

def check_or_create_text_file():
    """Ensures the test.txt file exists."""
    if not text_file_path.is_file():
        with open(text_file_path, "w") as file:
            file.write("")  # Creates an empty file

def get_user_choice():
    """Prompts user to confirm whether to proceed with solving."""
    while True:
        print("\nWould you like to proceed with solving the Sudoku puzzle in test.txt file?")
        print("\nIf yes, then before making your choice, please make sure that the Sudoku puzzle is loaded correctly.")
        print("If no, then the system will exit.")
        print("\n1: Yes")
        print("2: No")
        choice = input("\nPlease make your choice: ")
        if choice in ('1', '2'):
            return choice
        print("Invalid input. Please try again.")

if len(sys.argv) > 1:
    from tensorflow.keras.models import load_model
    import cv2
    import numpy as np
    import Preprocessing_full
    from utils_MNIST_Classify import predict_user_image_with_empty_check

    image_path = sys.argv[1]
    extracted = Preprocessing_full.extract_sudoku(image_path)
    cv2.imwrite('extracted_sudoku.jpg', extracted)

    model_mnist = load_model('trained_model_classification_MNIST.keras')
    sudoku_grid = np.zeros((9, 9), dtype=int)
    folder_path = "sudoku_digits"
    
    for i in range(1, 82):
        image_file = f"digit_{i}.png"
        image_path = os.path.join(folder_path, image_file)
        if os.path.exists(image_path):
            result = predict_user_image_with_empty_check(image_path, model_mnist)
            row, col = (i - 1) // 9, (i - 1) % 9
            sudoku_grid[row, col] = result
    
    check_or_create_text_file()
    with open("test.txt", "w") as file:
        file.write("[\n")
        for row in sudoku_grid:
            file.write(" [" + " ".join(map(str, row)) + "]\n")
        file.write("]")
    
    
    from solve_sudoku import load_sudoku_from_file, print_board, solve_board, interactive_sudoku
    initial_board = load_sudoku_from_file("test.txt")
    print("\nLoaded Sudoku Grid:\n")
    print_board(initial_board)

    choice = get_user_choice()
    if choice == '2':
        sys.exit("Exiting without solving the puzzle.")

    from solve_sudoku import load_sudoku_from_file, print_board, solve_board, interactive_sudoku
    import time

    initial_board = load_sudoku_from_file("test.txt")
    print("\nLoaded Sudoku Grid:\n")
    print_board(initial_board)
    start_time = time.time()

    solved_board = initial_board.copy()
    
    if solve_board(solved_board):
        end_time = time.time()
        print(f"Execution Time: {end_time - start_time:.6f} seconds")
        interactive_sudoku(initial_board, solved_board)
    else:
        print("There is no solution.")

else:
    if not text_file_path.is_file():
        sys.exit("File not found. Please make sure that test.txt exists.")
    
    from solve_sudoku import load_sudoku_from_file, print_board, solve_board, interactive_sudoku
    
    initial_board = load_sudoku_from_file("test.txt")
    print("\nLoaded Sudoku Grid:\n")
    print_board(initial_board)

    choice = get_user_choice()
    if choice == '2':
        sys.exit("Exiting without solving the puzzle.")
    
    
    import time
    
    initial_board = load_sudoku_from_file("test.txt")
    start_time = time.time()
    print("\nLoaded Sudoku Grid:\n")
    print_board(initial_board)
    solved_board = initial_board.copy()
    
    if solve_board(solved_board):
        end_time = time.time()
        print(f"Execution Time: {end_time - start_time:.6f} seconds")
        interactive_sudoku(initial_board, solved_board)
    else:
        print("There is no solution.")