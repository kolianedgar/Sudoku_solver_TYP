import cv2
import numpy as np

def save_as_image(original_board, current_board, solved_board, system_revealed_positions, user_guess_positions, incorrect_guess_positions):
    # Load the extracted Sudoku image.
    initial_board_image = cv2.imread("extracted_sudoku.jpg")

    # Define text overlay parameters (OpenCV uses BGR format).
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1  # Adjust based on image resolution.
    thickness = 2

    # Colors in BGR:
    color_auto_fill = (0, 255, 0)       # Green for auto-solved (solver-filled) numbers.
    color_system_reveal = (255, 0, 255)   # Magenta for cells revealed by the system (option 1).
    color_user_guess = (255, 255, 0)      # Cyan for user-entered correct guesses (option 4).
    color_incorrect = (0, 0, 255)         # Red for incorrect user guesses.

    # Assuming a square grid, determine the cell size.
    grid_size = initial_board_image.shape[0] // 9

    # Iterate over each cell.
    for row in range(9):
        for col in range(9):
            # Do not augment cells that were pre-filled in the original puzzle.
            if original_board[row, col] != 0:
                continue

            # Calculate the overlay position.
            x = col * grid_size + grid_size // 4
            y = row * grid_size + int(grid_size * 0.8)

            # Determine the color based on the origin of the filled number.
            if (row, col) in incorrect_guess_positions:
                number = current_board[row, col]
                cv2.putText(initial_board_image, str(number), (x, y), font, font_scale, color_incorrect, thickness)
            elif (row, col) in user_guess_positions:
                number = current_board[row, col]
                cv2.putText(initial_board_image, str(number), (x, y), font, font_scale, color_user_guess, thickness)
            elif (row, col) in system_revealed_positions:
                number = current_board[row, col]
                cv2.putText(initial_board_image, str(number), (x, y), font, font_scale, color_system_reveal, thickness)
            else:
                # For cells that are auto-filled by the solver.
                number = solved_board[row, col]
                cv2.putText(initial_board_image, str(number), (x, y), font, font_scale, color_auto_fill, thickness)

    # Save the final augmented Sudoku image.
    cv2.imwrite("solved_sudoku.png", initial_board_image)
    print("Solved Sudoku image saved as solved_sudoku.png")