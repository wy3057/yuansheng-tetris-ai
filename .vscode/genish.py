import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import time
from typing import List, Tuple
from PIL import ImageGrab·
import win32gui
import win32con
import win32api
import ctypes

class GenshinPuzzleGame:
    def __init__(self):
        """初始化游戏参数和窗口信息"""
        # 提升进程权限
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("请以管理员权限运行此程序")
            exit(1)
            
        self.board_width = 6
        self.board_height = 12
        self.window_info = self._find_genshin_window()
        self.cell_colors = {}  # 存储方块颜色的字典
        self.genshin_hwnd = win32gui.FindWindow(None, "原神")  # 获取原神窗口句柄
        
        # 创建三个窗口，分别显示原始捕获区域、处理后的棋盘和数字化的棋盘
        cv2.namedWindow("Captured Area", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Captured Area", 400, 800)
        cv2.namedWindow("Processed Board", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Processed Board", 400, 800)
        cv2.namedWindow("Digital Board", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Digital Board", 400, 800)
        
    def _find_genshin_window(self) -> Tuple[int, int, int, int]:
        """定位原神窗口并返回指定区域的坐标和大小"""
        try:
            genshin_window = gw.getWindowsWithTitle('原神')[0]
            # 获取窗口位置和大小
            window_left = genshin_window.left
            window_top = genshin_window.top
            
            # 直接使用指定的固定区域
            game_left = window_left + 310  # 距离左侧300dpi
            game_top = window_top + 270    # 距离上侧200dpi
            game_width = genshin_window.width - 310 - 1260  # 左侧300dpi，右侧1250dpi
            game_height = genshin_window.height - 270 - 145  # 上侧200dpi，下侧130dpi
            
            return (game_left, game_top, game_width, game_height)
        except IndexError:
            raise Exception("未找到原神窗口")

    def get_game_board(self) -> List[List[int]]:
        """获取当前游戏板状态"""
        try:
            x, y, width, height = self.window_info
            # 使用PIL的ImageGrab替代pyautogui的screenshot
            screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # 显示原始捕获的区域
            cv2.imshow("Captured Area", frame)
            cv2.waitKey(1)  # 更新显示，但不阻塞
            
            # 初始化游戏板
            board = [[0] * self.board_width for _ in range(self.board_height)]
            
            # 计算每个格子的大小
            cell_height = height // self.board_height
            cell_width = width // self.board_width
            
            # 创建一个可视化的棋盘图像
            board_image = np.zeros((height, width, 3), dtype=np.uint8)
            # 创建一个数字化的棋盘图像
            digital_board_image = np.zeros((height, width, 3), dtype=np.uint8)
            digital_board_image.fill(255)  # 设置白色背景
            
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
                    
                    # 在可视化棋盘上绘制方块
                    cv2.rectangle(board_image,
                                (col * cell_width, row * cell_height),
                                ((col + 1) * cell_width, (row + 1) * cell_height),
                                color.tolist(),
                                -1)  # -1表示填充矩形
                    cv2.rectangle(board_image,
                                (col * cell_width, row * cell_height),
                                ((col + 1) * cell_width, (row + 1) * cell_height),
                                (255, 255, 255),
                                1)  # 绘制白色边框
                    
                    # 在数字化棋盘上绘制数字
                    cv2.rectangle(digital_board_image,
                                (col * cell_width, row * cell_height),
                                ((col + 1) * cell_width, (row + 1) * cell_height),
                                (0, 0, 0),
                                1)  # 绘制黑色边框
                    # 将数字放在格子中央
                    number = str(board[row][col])
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.5
                    font_thickness = 1
                    text_size = cv2.getTextSize(number, font, font_scale, font_thickness)[0]
                    text_x = col * cell_width + (cell_width - text_size[0]) // 2
                    text_y = row * cell_height + (cell_height + text_size[1]) // 2
                    cv2.putText(digital_board_image, number, (text_x, text_y), font, font_scale, (0, 0, 0), font_thickness)
            
            # 显示处理后的棋盘
            cv2.imshow("Processed Board", board_image)
            cv2.imshow("Digital Board", digital_board_image)
            cv2.waitKey(1)
            
            return board
        except Exception as e:
            print(f"截图失败: {str(e)}")
            return [[0] * self.board_width for _ in range(self.board_height)]

    def make_move(self, action: str):
        """执行移动操作"""
        # 定义按键映射
        key_mapping = {
            'a': win32con.VK_LEFT,
            'd': win32con.VK_RIGHT,
            'w': win32con.VK_UP
        }
        
        try:
            # 向原神窗口发送按键消息
            result = win32api.SendMessage(self.genshin_hwnd, win32con.WM_KEYDOWN, key_mapping[action], 0)
            if result == 0:
                time.sleep(0.05)
                win32api.SendMessage(self.genshin_hwnd, win32con.WM_KEYUP, key_mapping[action], 0)
                time.sleep(0.1)  # 等待动作执行完成
            else:
                print(f"按键发送失败，错误代码: {result}")
        except Exception as e:
            print(f"按键操作失败: {str(e)}")

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
            try:
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
                
                # 检查是否按下ESC键退出
                if cv2.waitKey(1) & 0xFF == 27:  # ESC键的ASCII码为27
                    cv2.destroyAllWindows()
                    break
                    
            except Exception as e:
                print(f"游戏循环出错: {str(e)}")
                time.sleep(1)  # 出错时等待一秒后继续

if __name__ == "__main__":
    game = GenshinPuzzleGame()
    game.play()
