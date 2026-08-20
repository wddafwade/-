import tkinter as tk
from tkinter import messagebox
import random

class Minesweeper:
    def __init__(self, root, rows=10, cols=10, mines=10):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.flags = set()
        self.revealed = set()
        self.mine_positions = set()
        self.game_over = False
        
        # 设置窗口
        self.root.title("扫雷游戏")
        self.root.resizable(False, False)
        
        # 创建界面组件
        self.create_widgets()
        self.init_game()
        
    def create_widgets(self):
        # 顶部信息栏
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(pady=10)
        
        self.mine_label = tk.Label(self.info_frame, text=f"💣 剩余地雷: {self.mines}", 
                                   font=("Arial", 12))
        self.mine_label.pack(side=tk.LEFT, padx=20)
        
        self.timer_label = tk.Label(self.info_frame, text="⏱ 时间: 0", 
                                    font=("Arial", 12))
        self.timer_label.pack(side=tk.LEFT, padx=20)
        
        self.new_game_btn = tk.Button(self.info_frame, text="🔄 新游戏", 
                                      command=self.restart_game, font=("Arial", 10))
        self.new_game_btn.pack(side=tk.LEFT, padx=20)
        
        # 游戏区域
        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack(pady=10)
        
        # 创建按钮网格
        self.buttons = {}
        for r in range(self.rows):
            for c in range(self.cols):
                button = tk.Button(self.game_frame, width=2, height=1, 
                                  font=("Arial", 10, "bold"),
                                  command=lambda row=r, col=c: self.reveal_cell(row, col))
                button.bind("<Button-3>", lambda event, row=r, col=c: self.toggle_flag(row, col))
                button.grid(row=r, column=c, padx=1, pady=1)
                self.buttons[(r, c)] = button
        
        # 难度选择
        self.difficulty_frame = tk.Frame(self.root)
        self.difficulty_frame.pack(pady=10)
        
        tk.Label(self.difficulty_frame, text="难度:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        difficulties = [
            ("初级", 9, 9, 10),
            ("中级", 16, 16, 40),
            ("高级", 16, 30, 99)
        ]
        
        for text, r, c, m in difficulties:
            btn = tk.Button(self.difficulty_frame, text=text, font=("Arial", 10),
                          command=lambda rows=r, cols=c, mines=m: self.change_difficulty(rows, cols, mines))
            btn.pack(side=tk.LEFT, padx=5)
    
    def init_game(self):
        """初始化游戏"""
        self.game_over = False
        self.flags = set()
        self.revealed = set()
        self.mine_positions = set()
        self.time = 0
        self.timer_running = False
        
        # 随机放置地雷
        positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        self.mine_positions = set(random.sample(positions, self.mines))
        
        # 更新显示
        self.update_mine_label()
        self.update_timer_label()
        
        # 重置所有按钮
        for r in range(self.rows):
            for c in range(self.cols):
                button = self.buttons[(r, c)]
                button.config(text="", state=tk.NORMAL, bg="SystemButtonFace")
    
    def change_difficulty(self, rows, cols, mines):
        """更改难度"""
        # 清除现有按钮
        for button in self.buttons.values():
            button.destroy()
        
        self.rows = rows
        self.cols = cols
        self.mines = mines
        
        # 重新创建按钮
        self.buttons = {}
        for r in range(self.rows):
            for c in range(self.cols):
                button = tk.Button(self.game_frame, width=2, height=1, 
                                  font=("Arial", 8, "bold"),
                                  command=lambda row=r, col=c: self.reveal_cell(row, col))
                button.bind("<Button-3>", lambda event, row=r, col=c: self.toggle_flag(row, col))
                button.grid(row=r, column=c, padx=1, pady=1)
                self.buttons[(r, c)] = button
        
        self.init_game()
    
    def restart_game(self):
        """重新开始游戏"""
        self.init_game()
    
    def get_neighbors(self, row, col):
        """获取相邻格子"""
        neighbors = []
        for r in range(max(0, row-1), min(self.rows, row+2)):
            for c in range(max(0, col-1), min(self.cols, col+2)):
                if (r, c) != (row, col):
                    neighbors.append((r, c))
        return neighbors
    
    def count_adjacent_mines(self, row, col):
        """计算相邻地雷数量"""
        count = 0
        for r, c in self.get_neighbors(row, col):
            if (r, c) in self.mine_positions:
                count += 1
        return count
    
    def reveal_cell(self, row, col):
        """翻开格子"""
        if self.game_over or (row, col) in self.flags or (row, col) in self.revealed:
            return
        
        # 启动计时器
        if not self.timer_running:
            self.start_timer()
        
        if (row, col) in self.mine_positions:
            # 踩到地雷
            self.game_over = True
            self.reveal_all_mines()
            self.buttons[(row, col)].config(bg="red", text="💣")
            messagebox.showinfo("游戏结束", "很遗憾，你踩到地雷了！")
            return
        
        # 翻开格子
        self.revealed.add((row, col))
        adjacent_mines = self.count_adjacent_mines(row, col)
        
        if adjacent_mines == 0:
            self.buttons[(row, col)].config(text="", relief=tk.SUNKEN, bg="lightgray")
            # 自动展开空白区域
            for r, c in self.get_neighbors(row, col):
                if (r, c) not in self.revealed and (r, c) not in self.flags:
                    self.reveal_cell(r, c)
        else:
            colors = {1: "blue", 2: "green", 3: "red", 4: "darkblue", 
                     5: "darkred", 6: "cyan", 7: "black", 8: "gray"}
            self.buttons[(row, col)].config(text=str(adjacent_mines), 
                                           fg=colors.get(adjacent_mines, "black"),
                                           relief=tk.SUNKEN, bg="lightgray")
        
        # 检查是否获胜
        if len(self.revealed) == self.rows * self.cols - self.mines:
            self.game_over = True
            self.stop_timer()
            messagebox.showinfo("恭喜", "你赢了！🎉")
    
    def toggle_flag(self, row, col):
        """标记/取消标记旗帜"""
        if self.game_over or (row, col) in self.revealed:
            return
        
        button = self.buttons[(row, col)]
        
        if (row, col) in self.flags:
            self.flags.remove((row, col))
            button.config(text="", bg="SystemButtonFace")
        else:
            self.flags.add((row, col))
            button.config(text="🚩", bg="yellow")
        
        self.update_mine_label()
    
    def reveal_all_mines(self):
        """显示所有地雷"""
        for r, c in self.mine_positions:
            if (r, c) not in self.flags:
                self.buttons[(r, c)].config(text="💣", bg="red")
    
    def update_mine_label(self):
        """更新地雷计数"""
        remaining = self.mines - len(self.flags)
        self.mine_label.config(text=f"💣 剩余地雷: {remaining}")
    
    def start_timer(self):
        """启动计时器"""
        self.timer_running = True
        self.update_timer()
    
    def stop_timer(self):
        """停止计时器"""
        self.timer_running = False
    
    def update_timer(self):
        """更新计时器"""
        if self.timer_running and not self.game_over:
            self.time += 1
            self.update_timer_label()
            self.root.after(1000, self.update_timer)
    
    def update_timer_label(self):
        """更新计时器显示"""
        self.timer_label.config(text=f"⏱ 时间: {self.time}")

def main():
    root = tk.Tk()
    game = Minesweeper(root, rows=9, cols=9, mines=10)
    root.mainloop()

if __name__ == "__main__":
    main()