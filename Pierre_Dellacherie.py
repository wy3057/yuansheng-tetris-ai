def evaluate_board(board):
    """
    评估当前棋盘状态的函数。

    使用 Pierre Dellacherie 的评估算法，考虑因素包括堆叠高度、空洞数量、凸起高度等。
    目的是计算一个分数，分数越高表示当前棋盘状态越好。

    参数:
    board (list): 二维列表，表示当前的棋盘状态。

    返回:
    int: 当前棋盘状态的评估分数。
    """
    # 初始化评估指标
    height = 0
    holes = 0
    bumpiness = 0
    lines_cleared = 0

    # 计算堆叠高度
    for col in range(len(board[0])):
        for row in range(len(board)):
            if board[row][col] != 0:
                height += len(board) - row
                break

    # 计算空洞数量
    for col in range(len(board[0])):
        empty = False
        for row in range(len(board)):
            if board[row][col] == 0:
                empty = True
            elif empty:
                holes += 1

    # 计算凸起高度
    for col in range(len(board[0]) - 1):
        for row in range(len(board)):
            if board[row][col] != 0:
                current_height = len(board) - row
                break
        for row in range(len(board)):
            if board[row][col + 1] != 0:
                next_height = len(board) - row
                break
        bumpiness += abs(current_height - next_height)

    # 计算消除的行数
    for row in range(len(board)):
        if all(cell != 0 for cell in board[row]):
            lines_cleared += 1

    # 计算总分数
    score = -height - 3 * holes - bumpiness + 10 * lines_cleared
    return score

def apply_action(board, action):
    """
    根据指定的动作更新棋盘状态。

    参数:
    board (list): 二维列表，表示当前的棋盘状态。
    action (str): 动作字符串，可以是'left'、'right'、'down'、'rotate'之一。

    返回:
    list: 更新后的棋盘状态。
    """
    # 复制棋盘以避免修改原始棋盘
    new_board = [row[:] for row in board]
    if action == 'left':
        # 向左移动
        for row in new_board:
            while row[0] == 0 and row.count(0) > 0:
                row.pop(0)
                row.append(0)
    elif action == 'right':
        # 向右移动
        for row in new_board:
            while row[-1] == 0 and row.count(0) > 0:
                row.pop()
                row.insert(0, 0)
    elif action == 'down':
        # 向下移动
        pass  # 下降动作通常由游戏引擎自动处理
    elif action == 'rotate':
        # 旋转
        pass  # 旋转动作通常由游戏引擎自动处理
    return new_board

def choose_best_action(board, possible_actions):
    """
    选择最佳动作的函数。

    根据评估函数，从可能的动作中选择一个可以使棋盘状态得分最高的动作。

    参数:
    board (list): 二维列表，表示当前的棋盘状态。
    possible_actions (list): 可能的动作列表，每个动作是一个字符串。

    返回:
    str: 最佳动作。
    """
    # 初始化最佳动作和最佳分数
    best_action = None
    best_score = float('-inf')
    for action in possible_actions:
        # 应用动作并评估新棋盘状态
        new_board = apply_action(board, action)
        score = evaluate_board(new_board)
        # 更新最佳动作和最佳分数
        if score > best_score:
            best_score = score
            best_action = action
    return best_action
