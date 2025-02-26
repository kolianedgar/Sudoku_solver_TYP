import cv2
import numpy as np

def save_as_image(original_board, current_board, solved_board, revealed_positions, user_guess_positions):
    # Load the extracted Sudoku image.
    initial_board_image = cv2.imread("extracted_sudoku.jpg")

    # Define parameters for text overlay.
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1  # Adjust based on image resolution.
    thickness = 2
    color_auto_fill = (0, 255, 0)       # Green for automatically filled numbers.
    color_system_reveal = (255, 0, 255)   # Magenta for system-revealed cells (option 1).
    color_user_guess = (255, 255, 0)      # Cyan for user-entered correct guesses (option 4).

    # Define cell size (assuming a square Sudoku grid).
    grid_size = initial_board_image.shape[0] // 9

    # Iterate over each cell.
    for row in range(9):
        for col in range(9):
            x = col * grid_size + grid_size // 4   # Adjust x-position as needed.
            y = row * grid_size + int(grid_size * 0.8)  # Adjust y-position as needed.

            # Process only cells that were originally empty.
            if original_board[row, col] == 0:
                if (row, col) in revealed_positions:
                    # Cell was revealed by the system (option 1) → use magenta.
                    number = current_board[row, col]
                    cv2.putText(initial_board_image, str(number), (x, y), font, font_scale, color_system_reveal, thickness)
                elif (row, col) in user_guess_positions:
                    # Cell was filled by the user (option 4) → use cyan.
                    number = current_board[row, col]
                    cv2.putText(initial_board_image, str(number), (x, y), font, font_scale, color_user_guess, thickness)
                elif current_board[row, col] != 0:
                    # Otherwise, if the cell is filled (by auto-fill, for example), use green.
                    number = current_board[row, col]
                    cv2.putText(initial_board_image, str(number), (x, y), font, font_scale, color_auto_fill, thickness)
                else:
                    # If still empty, overlay the solved number (auto-fill in green).
                    number = solved_board[row, col]
                    cv2.putText(initial_board_image, str(number), (x, y), font, font_scale, color_auto_fill, thickness)
    # Save the final augmented Sudoku image.
    cv2.imwrite("solved_sudoku.png", initial_board_image)
    print("Solved Sudoku image saved as solved_sudoku.png")