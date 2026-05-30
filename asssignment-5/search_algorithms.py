import math
import random
import time
from copy import deepcopy

EMPTY = ' '
X = 'X'
O = 'O'

def create_board():
    return [[EMPTY]*3 for _ in range(3)]

def print_board(board):
    for i, row in enumerate(board):
        print(' | '.join(row))
        if i < 2:
            print('---------')
    print()

def get_available_moves(board):
    return [(r, c) for r in range(3) for c in range(3) if board[r][c] == EMPTY]

def make_move(board, row, col, player):
    board[row][col] = player

def check_winner(board):
    for row in board:
        if row[0] == row[1] == row[2] != EMPTY:
            return row[0]
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != EMPTY:
            return board[0][col]
    if board[0][0] == board[1][1] == board[2][2] != EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != EMPTY:
        return board[0][2]
    return None

def is_full(board):
    return all(board[r][c] != EMPTY for r in range(3) for c in range(3))

def is_terminal(board):
    return check_winner(board) is not None or is_full(board)

def evaluate(board):
    winner = check_winner(board)
    if winner == X:
        return 1
    elif winner == O:
        return -1
    return 0


def minimax(board, depth, is_maximizing):
    if is_terminal(board):
        return evaluate(board)
    
    if is_maximizing:
        best = -math.inf
        for (r, c) in get_available_moves(board):
            board[r][c] = X
            score = minimax(board, depth + 1, False)
            board[r][c] = EMPTY
            best = max(best, score)
        return best
    else:
        best = math.inf
        for (r, c) in get_available_moves(board):
            board[r][c] = O
            score = minimax(board, depth + 1, True)
            board[r][c] = EMPTY
            best = min(best, score)
        return best

def best_move_minimax(board):
    best_score = -math.inf
    move = None
    for (r, c) in get_available_moves(board):
        board[r][c] = X
        score = minimax(board, 0, False)
        board[r][c] = EMPTY
        if score > best_score:
            best_score = score
            move = (r, c)
    return move


def alpha_beta(board, depth, alpha, beta, is_maximizing):
    if is_terminal(board):
        return evaluate(board)
    
    if is_maximizing:
        best = -math.inf
        for (r, c) in get_available_moves(board):
            board[r][c] = X
            score = alpha_beta(board, depth + 1, alpha, beta, False)
            board[r][c] = EMPTY
            best = max(best, score)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = math.inf
        for (r, c) in get_available_moves(board):
            board[r][c] = O
            score = alpha_beta(board, depth + 1, alpha, beta, True)
            board[r][c] = EMPTY
            best = min(best, score)
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best

def best_move_alpha_beta(board):
    best_score = -math.inf
    move = None
    for (r, c) in get_available_moves(board):
        board[r][c] = X
        score = alpha_beta(board, 0, -math.inf, math.inf, False)
        board[r][c] = EMPTY
        if score > best_score:
            best_score = score
            move = (r, c)
    return move


def heuristic_evaluate(board, depth):
    winner = check_winner(board)
    if winner == X:
        return 10 - depth
    elif winner == O:
        return depth - 10
    return 0

def heuristic_alpha_beta(board, depth, alpha, beta, is_maximizing, max_depth=4):
    if is_terminal(board) or depth == max_depth:
        return heuristic_evaluate(board, depth)
    
    if is_maximizing:
        best = -math.inf
        for (r, c) in get_available_moves(board):
            board[r][c] = X
            score = heuristic_alpha_beta(board, depth + 1, alpha, beta, False, max_depth)
            board[r][c] = EMPTY
            best = max(best, score)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = math.inf
        for (r, c) in get_available_moves(board):
            board[r][c] = O
            score = heuristic_alpha_beta(board, depth + 1, alpha, beta, True, max_depth)
            board[r][c] = EMPTY
            best = min(best, score)
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best

def best_move_heuristic(board, max_depth=4):
    best_score = -math.inf
    move = None
    for (r, c) in get_available_moves(board):
        board[r][c] = X
        score = heuristic_alpha_beta(board, 0, -math.inf, math.inf, False, max_depth)
        board[r][c] = EMPTY
        if score > best_score:
            best_score = score
            move = (r, c)
    return move


class MCTSNode:
    def __init__(self, board, player, parent=None, move=None):
        self.board = deepcopy(board)
        self.player = player
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = get_available_moves(board)

    def ucb1(self, c=1.41):
        if self.visits == 0:
            return float('inf')
        return (self.wins / self.visits) + c * math.sqrt(math.log(self.parent.visits) / self.visits)

    def select_child(self):
        return max(self.children, key=lambda n: n.ucb1())

    def expand(self):
        move = self.untried_moves.pop(random.randint(0, len(self.untried_moves) - 1))
        new_board = deepcopy(self.board)
        new_board[move[0]][move[1]] = self.player
        next_player = O if self.player == X else X
        child = MCTSNode(new_board, next_player, parent=self, move=move)
        self.children.append(child)
        return child

    def simulate(self):
        sim_board = deepcopy(self.board)
        current = self.player
        while not is_terminal(sim_board):
            moves = get_available_moves(sim_board)
            r, c = random.choice(moves)
            sim_board[r][c] = current
            current = O if current == X else X
        winner = check_winner(sim_board)
        if winner == X:
            return 1
        elif winner == O:
            return -1
        return 0

    def backpropagate(self, result):
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(result)

def mcts(board, player, iterations=1000):
    root = MCTSNode(board, player)
    for _ in range(iterations):
        node = root
        while node.untried_moves == [] and node.children:
            node = node.select_child()
        if node.untried_moves:
            node = node.expand()
        result = node.simulate()
        node.backpropagate(result)
    best = max(root.children, key=lambda n: n.visits)
    return best.move


def run_test(name, move_fn, board_state):
    board = deepcopy(board_state)
    print(f"Algorithm: {name}")
    print("Board before move:")
    print_board(board)
    start = time.time()
    move = move_fn(board)
    elapsed = time.time() - start
    if move:
        board[move[0]][move[1]] = X
    print(f"Best move: {move}")
    print("Board after move:")
    print_board(board)
    print(f"Time taken: {elapsed:.4f}s")
    print("="*40)

test_board = create_board()
test_board[0][0] = X
test_board[1][1] = O
test_board[0][2] = X

run_test("Minimax", best_move_minimax, test_board)
run_test("Alpha-Beta", best_move_alpha_beta, test_board)
run_test("Heuristic Alpha-Beta", lambda b: best_move_heuristic(b, max_depth=4), test_board)
run_test("MCTS", lambda b: mcts(b, X, iterations=500), test_board)


def play_game(ai_fn, ai_player=X):
    board = create_board()
    current = X
    while not is_terminal(board):
        print_board(board)
        if current == ai_player:
            move = ai_fn(board)
            print(f"AI plays: {move}")
        else:
            moves = get_available_moves(board)
            move = random.choice(moves)
            print(f"Random plays: {move}")
        board[move[0]][move[1]] = current
        current = O if current == X else X
    print_board(board)
    winner = check_winner(board)
    if winner:
        print(f"Winner: {winner}")
    else:
        print("Draw!")
    print("="*40)

print("\nGame simulation - Minimax vs Random:")
play_game(best_move_minimax, X)

print("Game simulation - MCTS vs Random:")
play_game(lambda b: mcts(b, X, 300), X)
