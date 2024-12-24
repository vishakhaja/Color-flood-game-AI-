import random
from collections import deque
import tkinter as tk
from tkinter import messagebox

# Constants
GRID_SIZE = 10
COLORS = ['red', 'green', 'blue', 'yellow', 'purple']
CELL_SIZE = 40

class ColorFloodGame:
    def __init__(self):
        self.grid = [[random.choice(COLORS) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.steps = 0
        self.max_steps = 25  # Limit the number of moves

    def flood_fill(self, x, y, target_color, replacement_color):
        """Flood fill algorithm."""
        if target_color == replacement_color:
            return
        queue = deque([(x, y)])
        while queue:
            cx, cy = queue.popleft()
            if 0 <= cx < GRID_SIZE and 0 <= cy < GRID_SIZE and self.grid[cx][cy] == target_color:
                self.grid[cx][cy] = replacement_color
                queue.extend([(cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)])

    def make_move(self, color):
        """Perform a move by flooding the grid."""
        target_color = self.grid[0][0]
        if target_color != color:
            self.flood_fill(0, 0, target_color, color)
            self.steps += 1

    def is_game_won(self):
        """Check if all cells have the same color."""
        first_color = self.grid[0][0]
        return all(cell == first_color for row in self.grid for cell in row)

    def suggest_best_move(self):
        """Suggest the best next move using a refined heuristic."""
        def simulate_move(grid, color):
            """Simulate a flood fill for a specific color."""
            new_grid = [row[:] for row in grid]  # Copy the grid
            self.flood_fill_simulation(0, 0, new_grid[0][0], color, new_grid)
            return new_grid

        def evaluate_grid(grid):
            """Evaluate a grid state based on connectivity."""
            first_color = grid[0][0]
            visited = set()
            queue = deque([(0, 0)])
            connected_count = 0

            while queue:
                x, y = queue.popleft()
                if (x, y) not in visited and 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and grid[x][y] == first_color:
                    visited.add((x, y))
                    connected_count += 1
                    queue.extend([(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)])

            return connected_count

        # Search for the best move
        best_move = None
        best_score = -1

        for color in COLORS:
            if color == self.grid[0][0]:  # Skip if it's the same as the current color
                continue

            simulated_grid = simulate_move(self.grid, color)
            score = evaluate_grid(simulated_grid)

            # Add a penalty for colors that don't expand much
            score -= 0.1 * (GRID_SIZE * GRID_SIZE - score)  # Penalize unconnected cells

            if score > best_score:
                best_score = score
                best_move = color

        return best_move

    def flood_fill_simulation(self, x, y, target_color, replacement_color, grid):
        """Flood fill algorithm for simulation."""
        if target_color == replacement_color:
            return
        queue = deque([(x, y)])
        while queue:
            cx, cy = queue.popleft()
            if 0 <= cx < GRID_SIZE and 0 <= cy < GRID_SIZE and grid[cx][cy] == target_color:
                grid[cx][cy] = replacement_color
                queue.extend([(cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)])


class ColorFloodGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Flood Game")
        self.game = ColorFloodGame()
        self.create_grid()
        self.create_controls()
        self.create_status_bar()
        self.show_instructions()

    def show_instructions(self):
        """Show a popup with game instructions."""
        messagebox.showinfo(
            "Welcome to Color Flood!",
            "Objective: Flood the grid with a single color within 25 moves.\n\n"
            "Instructions:\n"
            "- Select colors using the buttons below the grid.\n"
            "- The top-left corner and all connected cells of the same color will flood with the selected color.\n"
            "- Try to flood the entire grid in as few moves as possible.\n\n"
            "Press 'AI Suggestion' for help.\n"
            "Press 'Reset' to start a new game.\n\nGood luck!"
        )

    def create_grid(self):
        """Create the game grid in the GUI."""
        self.buttons = []
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.grid(row=0, column=0, padx=10, pady=10)

        for r in range(GRID_SIZE):
            row = []
            for c in range(GRID_SIZE):
                btn = tk.Button(
                    self.grid_frame,
                    bg=self.game.grid[r][c],
                    width=3,
                    height=1,
                    command=lambda color=self.game.grid[r][c]: self.make_move(color),
                )
                btn.grid(row=r, column=c, padx=1, pady=1)
                row.append(btn)
            self.buttons.append(row)

    def update_grid(self):
        """Update the grid colors based on the game's state."""
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.buttons[r][c].config(bg=self.game.grid[r][c])

    def create_controls(self):
        """Create control buttons for the game."""
        self.control_frame = tk.Frame(self.root)
        self.control_frame.grid(row=1, column=0, pady=10)

        for color in COLORS:
            btn = tk.Button(
                self.control_frame,
                text=color.capitalize(),
                bg=color,
                width=10,
                command=lambda color=color: self.make_move(color),
            )
            btn.pack(side=tk.LEFT, padx=5)

        ai_button = tk.Button(
            self.control_frame,
            text="AI Suggestion",
            bg="orange",
            width=12,
            command=self.ai_suggest,
        )
        ai_button.pack(side=tk.LEFT, padx=5)

        reset_button = tk.Button(
            self.control_frame,
            text="Reset",
            bg="gray",
            width=10,
            command=self.reset_game,
        )
        reset_button.pack(side=tk.LEFT, padx=5)

    def create_status_bar(self):
        """Create a status bar to show game information."""
        self.status_label = tk.Label(self.root, text="Steps: 0 / 25", font=("Arial", 12), anchor="w")
        self.status_label.grid(row=2, column=0, pady=10, sticky="w")

    def update_status(self):
        """Update the status bar with current game status."""
        if self.game.is_game_won():
            self.status_label.config(text=f"Congratulations! You won in {self.game.steps} steps!")
        elif self.game.steps >= self.game.max_steps:
            self.status_label.config(text="Game Over! You ran out of moves.")
        else:
            self.status_label.config(text=f"Steps: {self.game.steps} / {self.game.max_steps}")

    def make_move(self, color):
        """Handle user moves."""
        if self.game.is_game_won() or self.game.steps >= self.game.max_steps:
            return
        self.game.make_move(color)
        self.update_grid()
        self.update_status()

    def ai_suggest(self):
        """Get AI's suggestion for the best move."""
        suggested_color = self.game.suggest_best_move()
        if suggested_color:
            messagebox.showinfo("AI Suggestion", f"The AI suggests: {suggested_color.capitalize()}")
        else:
            messagebox.showinfo("AI Suggestion", "No valid moves available!")

    def reset_game(self):
        """Reset the game to its initial state."""
        self.game = ColorFloodGame()
        self.update_grid()
        self.update_status()


def main():
    root = tk.Tk()
    app = ColorFloodGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
