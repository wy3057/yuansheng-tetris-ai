import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import time
from typing import List, Tuple

class GenshinPuzzleGame:
    def __init__(self):
        self.board_width = 6
        self.board_height = 12
        self.window_info = self._find_genshin_window()
        self.cell_colors = {}  # 存储方块颜色的字典
        
    def _find_genshin_window(self) -> Tuple[int, int, int, int]:
        """定位原神窗口"""
        try:
            genshin_window = gw.getWindowsWithTitle('原神')[0]
            return (genshin_window.left, genshin_window.top, 
                   genshin_window.width, genshin_window.height)
        except IndexError:
            raise Exception("未找到原神窗口")

    def get_game_board(self) -> List[List[int]]:
        """获取当前游戏板状态"""
        x, y, width, height = self.window_info
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # 初始化游戏板
        board = [[0] * self.board_width for _ in range(self.board_height)]
        
        # 计算每个格子的大小
        cell_height = height // self.board_height
        cell_width = width // self.board_width
        
        # 分析每个格子的颜色
        for row in range(self.board_height):
            for col in range(self.board_width):
                cell_x = col * cell_width + cell_width // 2
                cell_y = row * cell_height + cell_height // 2
                color = frame[cell_y, cell_x]
                
                # 将BGR颜色转换为唯一的标识符
                color_key = tuple(color)
                if color_key not in self.cell_colors:
                    self.cell_colors[color_key] = len(self.cell_colors) + 1
                
                board[row][col] = self.cell_colors[color_key]
        
        return board

    def make_move(self, action: str):
        """执行移动操作"""
        pyautogui.press(action)
        time.sleep(0.1)  # 等待动作执行完成

    def evaluate_position(self, board: List[List[int]]) -> float:
        """评估当前位置的得分"""
        score = 0
        # 检查相同颜色的连通块
        visited = set()
        
        def dfs(row: int, col: int, color: int) -> List[Tuple[int, int]]:
            if (row, col) in visited or row < 0 or row >= self.board_height or \
               col < 0 or col >= self.board_width or board[row][col] != color:
                return []
            
            visited.add((row, col))
            connected = [(row, col)]
            
            # 检查四个方向
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_row, new_col = row + dr, col + dc
                connected.extend(dfs(new_row, new_col, color))
            
            return connected

        # 寻找可以消除的块
        for row in range(self.board_height):
            for col in range(self.board_width):
                if (row, col) not in visited and board[row][col] != 0:
                    connected = dfs(row, col, board[row][col])
                    if len(connected) >= 4:
                        score += len(connected) * 10

        return score

    def play(self):
        """主游戏循环"""
        while True:
            board = self.get_game_board()
            best_score = float('-inf')
            best_action = None
            
            # 尝试所有可能的动作
            for action in ['a', 'd', 'w']:
                # 模拟动作
                self.make_move(action)
                new_board = self.get_game_board()
                score = self.evaluate_position(new_board)
                
                if score > best_score:
                    best_score = score
                    best_action = action
            
            # 执行最佳动作
            if best_action:
                self.make_move(best_action)
            
            time.sleep(0.5)  # 控制游戏速度

if __name__ == "__main__":
    game = GenshinPuzzleGame()
    game.play()
