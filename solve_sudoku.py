import numpy as np
import time
import random
import cv2
from Save_Solution_as_Image import save_as_image

# Global lists to record positions
system_revealed_positions = []   # For cells revealed randomly by option 1 (magenta)
user_guess_positions = []        # For cells filled correctly by the user (cyan)
incorrect_guess_positions = []   # For cells where the user entered an incorrect guess (red)

# ANSI color codes (you can adjust if needed)
WHITE   = "\033[97m"   # For originally loaded board numbers.
CYAN    = "\033[96m"   # For correct user guesses.
MAGENTA = "\033[95m"   # For system-revealed numbers (option 1).
RED     = "\033[91m"   # For incorrect user guesses.
GREEN   = "\033[92m"   # For auto-filled (solver-filled) numbers in fully solved mode.
RESET   = "\033[0m"    # Reset color.

def print_board_colored(board, original_board, fully_solved=False):
    """
    Prints the Sudoku board with colors as follows:
      - Cells originally loaded from the puzzle (nonzero in original_board) are white.
      - Cells where the user entered a correct guess are cyan.
      - Cells where the user entered an incorrect guess are red.
      - Cells revealed by the system (option 1) are magenta.
      - In fully solved mode (fully_solved=True), any remaining cells (auto-filled) are printed in green.
    """
    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("-" * 25)
        for j in range(9):
            cell = board[i][j]
            # Decide which color to use based on the cell's origin:
            if original_board[i][j] != 0:
                # Pre-filled cell from the file → white.
                color = WHITE
            elif (i, j) in user_guess_positions:
                color = CYAN
            elif (i, j) in incorrect_guess_positions:
                color = RED
            elif (i, j) in system_revealed_positions:
                color = MAGENTA
            else:
                # For cells that are auto-filled by the solver:
                if fully_solved:
                    color = GREEN
                else:
                    color = RESET  # No special color in interactive mode.
            cell_str = str(cell) if cell != 0 else "-"
            if j % 3 == 0 and j != 0:
                print("|", end=" ")
            print(f"{color}{cell_str}{RESET}", end=" ")
        print()
    print()

def print_board(board):
    """Prints the Sudoku board in a readable format."""
    for i in range(len(board)):
        if i % 3 == 0 and i != 0:
            print("-" * 25)
        
        for j in range(len(board[0])):
            if j % 3 == 0 and j != 0:
                print("|", end=" ")

            print(board[i][j] if board[i][j] != 0 else "-", end=" ")
        
        print()
    print("\n")

def find_empty_position(board):
    """Finds an empty position (0) in the Sudoku board."""
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0:
                return (i, j)
    return None

def is_Valid(board, position, number):
    """Checks if a number can be placed at a given position."""
    row, col = position

    # Check row
    if number in board[row]:
        return False

    # Check column
    if number in board[:, col]:
        return False

    # Check 3x3 subgrid
    cube_x, cube_y = (col // 3) * 3, (row // 3) * 3
    if number in board[cube_y:cube_y+3, cube_x:cube_x+3]:
        return False

    return True

recursion_calls = 0
backtracks = 0
max_depth = 0

def solve_board(board, depth=0):
    """Solves the Sudoku board using backtracking."""
    global recursion_calls, backtracks, max_depth
    recursion_calls += 1
    max_depth = max(max_depth, depth)

    empty_position = find_empty_position(board)
    if not empty_position:
        return True  # Solved!

    row, col = empty_position

    for i in range(1, 10):
        if is_Valid(board, (row, col), i):
            board[row][col] = i  # Place number

            if solve_board(board, depth + 1):  # Recur
                return True

            board[row][col] = 0  # Undo (backtrack)
            backtracks += 1

    return False  # No valid number found

def classify_sudoku_difficulty(recursive_calls, backtracks):
    """Classifies Sudoku difficulty based on recursion and backtrack calls."""
    avg_calls = (recursive_calls + backtracks) // 2
    if avg_calls <= 150000:
        return "Easy"
    elif 150000 < avg_calls <= 275000:
        return "Moderate"
    else:
        return "Hard"

def load_sudoku_from_file(filename):
    """Loads a Sudoku grid from a text file without commas."""
    try:
        with open(filename, "r") as file:
            lines = file.readlines()[1:-1]  # Skip first and last bracket
            sudoku_grid = np.array([list(map(int, line.strip()[1:-1].split())) for line in lines])
        return sudoku_grid
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        exit()
    except ValueError:
        print(f"Error: {filename} has an invalid format.")
        exit()

def reveal_numbers(current_board, solution_board, num_reveals):
    """Reveals a given number of solved cells on top of the existing board.
       Returns the updated board and records the positions revealed by the system."""
    global system_revealed_positions
    available_positions = [(r, c) for r in range(9) for c in range(9) if current_board[r, c] == 0]
    
    num_reveals = min(num_reveals, len(available_positions))  # Avoid errors
    
    revealed_positions = random.sample(available_positions, num_reveals)
    system_revealed_positions.extend(revealed_positions)  # Record these positions

    for (r, c) in revealed_positions:
        current_board[r, c] = solution_board[r, c]  # Reveal correct solution

    return current_board  # Return updated board

def is_valid_placement(initial_board, solution_board, row, col, num):
    """
    Checks if a user-entered number is valid for the given cell.
    - Prevents checking pre-filled cells from the original puzzle.
    - Returns detailed feedback on why a number is incorrect.
    """
    if initial_board[row][col] != 0:
        return False, "This cell was pre-filled in the original puzzle. Choose an empty cell."

    correct_num = solution_board[row][col]
    
    if num == correct_num:
        # If the number is correct, print the updated board
        print("Correct! The number is part of the solution.\n")
        initial_board[row][col] = correct_num
        print_board(initial_board)
        return True, f"Correct! The number is part of the solution."
    # Check row conflict
    if num in solution_board[row]:
        return False, f"Incorrect! The number {num} is not a part of the solution."

    # Check column conflict
    if num in solution_board[:, col]:
        return False, f"Incorrect! The number {num} is not a part of the solution."

    # Check 3x3 subgrid conflict
    start_row, start_col = (row // 3) * 3, (col // 3) * 3
    subgrid = solution_board[start_row:start_row+3, start_col:start_col+3]
    if num in subgrid:
        return False, f"Incorrect! The number {num} already exists in this 3x3 box."

    # Default case: The number is incorrect but does not violate row, column, or grid rules.
    return False, f"Incorrect! The correct number for this cell is {correct_num}."

def interactive_sudoku(initial_board, solution_board):
    """Interactive session with visual feedback."""
    original_board = initial_board.copy()  # Keep original for reference (pre-filled cells).
    difficulty_revealed = False  # Flag for option 2.

    while True:
        print("\nOptions:")
        print("1: Reveal a number of solved cells")
        print("2: Reveal the difficulty of the puzzle")
        print("3: Reveal the fully solved puzzle")
        print("4: Check a number option for a cell")
        print("5: Save final solution as an image")
        print("6: Exit")
        choice = input("Please make your choice: ")

        if choice == "1":
            num_reveals = int(input("Please enter the number of cells you want to be revealed: "))
            initial_board = reveal_numbers(initial_board, solution_board, num_reveals)
            print("Puzzle with randomly revealed cells (magenta):")
            print_board_colored(initial_board, original_board, fully_solved=False)

        elif choice == "2":
            if not difficulty_revealed:
                difficulty = classify_sudoku_difficulty(recursion_calls, backtracks)
                print(f"\nThe difficulty of the puzzle is: {difficulty}")
                difficulty_revealed = True
            else:
                print("The difficulty has already been revealed.\n")

        elif choice == "3":
            print("\nHere is the fully solved puzzle:")
            # In fully solved mode, auto-filled cells appear in green,
            # while user guesses (cyan/red), system reveals (magenta), and pre-filled (white) remain unchanged.
            print_board_colored(solution_board, original_board, fully_solved=True)
            break

        elif choice == "4":
            row = int(input("Please enter the row index (0-8): "))
            col = int(input("Please enter the column index (0-8): "))

            # Check against the original board (which remains unchanged) to ensure the cell was originally empty.
            if original_board[row][col] != 0:
                print("This cell was pre-filled in the original puzzle. Choose an empty cell.\n")
                continue

            # Allow the user multiple attempts for the same cell.
            while True:
                test_num = int(input("Enter your guess for the cell (1-9), or 0 to clear the cell: "))
                if test_num == 0:
                    # Clear the cell and remove any recorded incorrect guess.
                    initial_board[row][col] = 0
                    if (row, col) in incorrect_guess_positions:
                        incorrect_guess_positions.remove((row, col))
                    print("Cell cleared.")
                    break

                # Compare the guess directly against the solution.
                correct_num = solution_board[row][col]
                if test_num == correct_num:
                    # Correct guess: update the board and record as a correct user guess.
                    initial_board[row][col] = test_num
                    if (row, col) not in user_guess_positions:
                        user_guess_positions.append((row, col))
                    # If the cell was previously marked as incorrect, remove it.
                    if (row, col) in incorrect_guess_positions:
                        incorrect_guess_positions.remove((row, col))
                    print("\033[96mCorrect! The number is part of the solution.\033[0m\n")
                    break  # Exit loop since the guess is correct.
                else:
                    # Incorrect guess: update board temporarily and record the cell as incorrect.
                    initial_board[row][col] = test_num
                    if (row, col) not in incorrect_guess_positions:
                        incorrect_guess_positions.append((row, col))
                    print("\033[91mIncorrect! The number is not correct.\033[0m")
                    print_board_colored(initial_board, original_board, fully_solved=False)
                    retry = input("Would you like to try again for the same cell? (Y/N): ")
                    if retry.lower() != 'y':
                        clear_choice = input("Would you like to clear the cell? (Y/N): ")
                        if clear_choice.lower() == 'y':
                            initial_board[row][col] = 0
                            if (row, col) in incorrect_guess_positions:
                                incorrect_guess_positions.remove((row, col))
                        break  # Exit the loop if the user chooses not to retry.
            print_board_colored(initial_board, original_board, fully_solved=False)



        elif choice == "5":
            from Save_Solution_as_Image import save_as_image
            save_as_image(original_board, initial_board, solution_board, system_revealed_positions, user_guess_positions, incorrect_guess_positions)

        elif choice == "6":
            print("Exiting interactive mode...")
            break

        else:
            print("Invalid input. Try again")

# # Load Sudoku grid from file
# initial_board = load_sudoku_from_file("test.txt")

# # Start timer
# start_time = time.time()

# print("\nLoaded Sudoku Grid:\n")
# print_board(initial_board)
# print("___________________________")

# # Solve Sudoku
# solved_board = initial_board.copy()  # Copy the board before solving
# if solve_board(solved_board):
#     end_time = time.time()

#     # Print execution time
#     print(f"Execution Time: {end_time - start_time:.6f} seconds")

#     # Start interactive mode with both initial and solved boards
#     interactive_sudoku(initial_board, solved_board)
# else:
#     print("There is no solution")
