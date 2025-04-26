import tkinter as tk
import random

ROWS = 5
COLS = 5
SELECTED_BG = "#f57c00"
OPTIMAL_BG = "#388e3c"
TEXT_FG = "white"
INSTR_TEXT = (
    "🏆 Gold Mine Game Instructions & Overview 🏆\n\n"
    "1. You are a miner in a 5x5 grid; each cell has 1-9 tons of gold.\n"
    "2. Start by clicking any cell in the first (leftmost) column.\n"
    "3. From (row,col), you may move →, ↗, or ↘ only.\n"
    "4. Your collected total appears at the top as you click.\n"
    "5. Clicking the last column ends the game:\n"
    "   • Optimal path is computed and highlighted in green.\n"
    "   • If your path exactly matches optimal: 🎉 You Win!\n"
    "   • Otherwise: 😞 Better luck next time!\n\n"
    "Controls: 🔁 Reset  |  🎲 New Game  |  ❌ Exit\n"
)

class GoldMineGame:
    def __init__(self, master):
        self.master = master
        self.master.title("🏆 Gold Mine Game")
        self._user_path = []
        self.make_ui()
        self.new_game()
        self.apply_theme()

    def make_ui(self):
        # Top controls
        top = tk.Frame(self.master, bg="#1e1e1e")
        top.pack(pady=6)
        self.gold_label = tk.Label(top, text="Gold: 0",
                                   font=("Arial", 14, "bold"),
                                   fg=TEXT_FG, bg="#1e1e1e")
        self.gold_label.grid(row=0, column=0, padx=6)
        tk.Button(top, text="🔁 Reset", command=self.reset_game,
                  font=("Arial", 12)).grid(row=0, column=1, padx=6)
        tk.Button(top, text="🎲 New Game", command=self.new_game,
                  font=("Arial", 12)).grid(row=0, column=2, padx=6)
        tk.Button(top, text="❌ Exit", command=self.master.quit,
                  font=("Arial", 12)).grid(row=0, column=3, padx=6)

        # Grid canvas
        self.canvas = tk.Frame(self.master, bg="#1e1e1e")
        self.canvas.pack(pady=6)

        # Result label
        self.opt_label = tk.Label(self.master, text="",
                                  font=("Arial", 13),
                                  fg=TEXT_FG, bg="#1e1e1e")
        self.opt_label.pack(pady=4)

        # Instructions text below
        self.instr_text = tk.Text(self.master, height=12, wrap="word",
                                  font=("Arial", 10),
                                  fg="white", bg="#222",
                                  padx=8, pady=6)
        self.instr_text.insert("1.0", INSTR_TEXT)
        self.instr_text.configure(state="disabled")
        self.instr_text.pack(fill="x", padx=10, pady=6)

    def apply_theme(self):
        bg = "#1e1e1e"
        for widget in (self.master, self.canvas):
            widget.configure(bg=bg)
        self.gold_label.configure(bg=bg)
        self.opt_label.configure(bg=bg)
        for row in getattr(self, "buttons", []):
            for btn in row:
                btn.configure(bg="#333", fg=TEXT_FG, relief="raised", state="normal")

    def new_game(self):
        self.grid = [[random.randint(1, 9) for _ in range(COLS)]
                     for _ in range(ROWS)]
        self.total_gold = 0
        self.current_pos = None
        self._user_path.clear()
        self.opt_label.config(text="")
        self.build_grid()

    def reset_game(self):
        self.total_gold = 0
        self.current_pos = None
        self._user_path.clear()
        self.gold_label.config(text="Gold: 0")
        self.opt_label.config(text="")
        for i, row in enumerate(self.buttons):
            for j, btn in enumerate(row):
                btn.configure(text=str(self.grid[i][j]),
                              bg="#333", fg=TEXT_FG,
                              state="normal", relief="raised")

    def build_grid(self):
        for w in self.canvas.winfo_children():
            w.destroy()
        self.buttons = []
        for i in range(ROWS):
            row = []
            for j in range(COLS):
                btn = tk.Button(self.canvas,
                                text=str(self.grid[i][j]),
                                width=4, height=2,
                                font=("Arial", 12, "bold"),
                                fg=TEXT_FG, bg="#333",
                                command=lambda i=i, j=j: self.click_cell(i, j))
                btn.grid(row=i, column=j, padx=3, pady=3)
                row.append(btn)
            self.buttons.append(row)
        self.gold_label.config(text="Gold: 0")

    def click_cell(self, i, j):
        if self.current_pos is None:
            if j != 0:
                return
        else:
            ci, cj = self.current_pos
            if (i, j) not in [(ci, cj+1), (ci-1, cj+1), (ci+1, cj+1)]:
                return

        self.total_gold += self.grid[i][j]
        self._user_path.append((i, j))
        self.gold_label.config(text=f"Gold: {self.total_gold}")
        self.buttons[i][j].configure(bg=SELECTED_BG,
                                     fg=TEXT_FG,
                                     relief="sunken",
                                     state="disabled")
        self.current_pos = (i, j)

        if j == COLS - 1:
            opt_gold, opt_path = self.get_optimal_path()
            # Win/Lose check
            if self._user_path == opt_path:
                res = "🎉 You Win!"
            else:
                res = "😞 Better luck next time!"
            self.opt_label.config(text=f"{res} Optimal Gold: {opt_gold}")
            for r in self.buttons:
                for b in r:
                    b.configure(state="disabled")
            for (x, y) in opt_path:
                btn = self.buttons[x][y]
                if btn["bg"] != SELECTED_BG:
                    btn.configure(bg=OPTIMAL_BG,
                                  fg=TEXT_FG,
                                  relief="sunken")

    def get_optimal_path(self):
        dp = [[0]*COLS for _ in range(ROWS)]
        nxt = [[None]*COLS for _ in range(ROWS)]
        for i in range(ROWS):
            dp[i][COLS-1] = self.grid[i][COLS-1]
        for j in range(COLS-2, -1, -1):
            for i in range(ROWS):
                best, mv = dp[i][j+1], (i, j+1)
                if i > 0 and dp[i-1][j+1] > best:
                    best, mv = dp[i-1][j+1], (i-1, j+1)
                if i < ROWS-1 and dp[i+1][j+1] > best:
                    best, mv = dp[i+1][j+1], (i+1, j+1)
                dp[i][j] = self.grid[i][j] + best
                nxt[i][j] = mv

        start = max(range(ROWS), key=lambda r: dp[r][0])
        path, i, j = [], start, 0
        while j < COLS:
            path.append((i, j))
            i, j = nxt[i][j] or (i, j+1)
        return dp[start][0], path

def main():
    root = tk.Tk()
    GoldMineGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
