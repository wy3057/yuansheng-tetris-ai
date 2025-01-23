import cv2
import pyautogui
import numpy as np
from Pierre_Dellacherie import choose_best_action, apply_action
import pygetwindow as gw

def find_genshin_window():
    """
    定位名为“原神”窗口的位置，返回窗口的 x, y, width, height。

    返回:
    tuple: 包含窗口的 x, y, width, height 的元组。
    """
    try:
        # 获取所有窗口
        windows = gw.getAllTitles()
        # 查找名为“原神”的窗口
        genshin_window = gw.getWindowsWithTitle('原神')[0]
        # 获取窗口的位置和大小
        x, y, width, height = genshin_window.left, genshin_window.top, genshin_window.width, genshin_window.height
        return x, y, width, height
    except IndexError:
        # 如果没有找到名为“原神”的窗口，返回 None
        return None

# 示例调用
window_position = find_genshin_window()
if window_position:
    print(f"原神窗口的位置和大小: x={window_position[0]}, y={window_position[1]}, width={window_position[2]}, height={window_position[3]}")
else:
    print("未找到名为“原神”的窗口")

def capture_game_window(region):
    # 使用 OpenCV 捕获游戏窗口
    screenshot = pyautogui.screenshot(region=region)
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return frame

def preprocess_frame(frame):
    # 预处理图像，提取棋盘状态
    board_height = 12
    board_width = 6
    board_state = [[0] * board_width for _ in range(board_height)]
    
    # 假设每个单元格的大小为 cell_size x cell_size
    cell_size = frame.shape[0] // board_height
    
    for i in range(board_height):
        for j in range(board_width):
            # 提取每个单元格的颜色
            cell = frame[i * cell_size:(i + 1) * cell_size, j * cell_size:(j + 1) * cell_size]
            # 假设空单元格的颜色为黑色 (0, 0, 0)
            if not np.all(cell == [0, 0, 0]):
                board_state[i][j] = 1  # 假设非空单元格的值为1
    
    return board_state

def control_game(action):
    # 根据动作控制游戏
    if action == 'left':
        pyautogui.press('a')
    elif action == 'right':
        pyautogui.press('d')
    elif action == 'down':
        pyautogui.press('s')
    elif action == 'rotate':
        pyautogui.press('w')

def main():
    x, y, width, height = find_genshin_window()
    game_region = (x, y, width, height)  # 游戏窗口的坐标和大小
    while True:
        frame = capture_game_window(game_region)
        board_state = preprocess_frame(frame)
        possible_actions = ['left', 'right', 'down', 'rotate']  # 假设的动作集合
        best_action = choose_best_action(board_state, possible_actions)
        control_game(best_action)

if __name__ == "__main__":
    main()