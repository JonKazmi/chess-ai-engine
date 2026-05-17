"""Chess Game Engine + AI - Easy / Medium / Hard"""
import random
import time
from chess_rules import *


class ChessGame:
    def __init__(self):
        self.board = start_board()
        self.current_color = 'white'
        self.move_history = []
        self.ep_square = None  # En passant square
        self.castling_rights = {
            'white': {'k': True, 'q': True},
            'black': {'k': True, 'q': True}
        }
        self.move_count = 0
        self.game_over = False
        self.result = None

    def get_legal_moves(self, color=None):
        if color is None:
            color = self.current_color
        return all_legal_moves(self.board, color, self.ep_square, self.castling_rights)

    def make_move(self, r, c, nr, nc):
        """Make a move, returns True if valid"""
        moves = self.get_legal_moves()
        move = (r, c, nr, nc)

        if move not in moves:
            return False

        piece = self.board[r][c]
        ptype = piece_type(piece)

        # Update en passant
        old_ep = self.ep_square
        if ptype == 'p' and abs(nr - r) == 2:
            self.ep_square = ((r + nr) // 2, c)
        else:
            self.ep_square = None

        # Handle castling rights loss
        if ptype == 'k':
            self.castling_rights[self.current_color]['k'] = False
            self.castling_rights[self.current_color]['q'] = False
        if ptype == 'r':
            if r == 7 and c == 0:
                self.castling_rights['white']['q'] = False
            if r == 7 and c == 7:
                self.castling_rights['white']['k'] = False
            if r == 0 and c == 0:
                self.castling_rights['black']['q'] = False
            if r == 0 and c == 7:
                self.castling_rights['black']['k'] = False

        # Apply move
        self.board = apply_move(self.board, r, c, nr, nc, old_ep, self.castling_rights)

        # Record move
        self.move_history.append({
            'from': (r, c),
            'to': (nr, nc),
            'piece': piece,
            'captured': self.board[nr][nc],
            'ep': old_ep,
            'promotion': ptype == 'p' and (nr == 0 or nr == 7)
        })

        # Switch color
        self.current_color = 'black' if self.current_color == 'white' else 'white'
        self.move_count += 1

        # Check game over
        self.check_game_over()

        return True

    def check_game_over(self):
        color = self.current_color
        if is_checkmate(self.board, color, self.ep_square, self.castling_rights):
            self.game_over = True
            self.result = 'black' if color == 'white' else 'white'
        elif is_stalemate(self.board, color, self.ep_square, self.castling_rights):
            self.game_over = True
            self.result = 'draw'
        elif is_insufficient_material(self.board):
            self.game_over = True
            self.result = 'draw'
        elif self.move_count >= 100:  # 50 move rule
            self.game_over = True
            self.result = 'draw'

    def undo(self):
        """Undo last move"""
        if not self.move_history:
            return False

        # This is a simplified undo - for full undo we'd need more state
        # For the UI we'll rebuild from history
        return True

    def reset(self):
        """Reset game"""
        self.__init__()


# AI Functions
def ai_easy(game):
    """Random move - instant"""
    moves = game.get_legal_moves()
    if not moves:
        return None
    return random.choice(moves)


def ai_medium(game):
    """Minimax depth 3"""
    moves = game.get_legal_moves()
    if not moves:
        return None

    best_move = None
    best_score = float('-inf')

    for r, c, nr, nc in moves:
        # Apply move
        old_board = game.board
        old_ep = game.ep_square
        old_cr = {k: {kk: vv for kk, vv in v.items()} for k, v in game.castling_rights.items()}

        game.board = apply_move(game.board, r, c, nr, nc, game.ep_square, game.castling_rights)
        score = minimax(game, depth=2, maximizing=True)

        # Restore
        game.board = old_board
        game.ep_square = old_ep
        game.castling_rights = old_cr

        if score > best_score:
            best_score = score
            best_move = (r, c, nr, nc)

    return best_move


def ai_hard(game):
    """Minimax + Alpha-Beta pruning depth 4"""
    moves = game.get_legal_moves()
    if not moves:
        return None

    # Order moves - captures first for better pruning
    def move_priority(m):
        r, c, nr, nc = m
        if game.board[nr][nc]:
            return 0
        return 1
    moves = sorted(moves, key=move_priority)

    best_move = None
    best_score = float('-inf')
    alpha = float('-inf')
    beta = float('inf')

    for r, c, nr, nc in moves:
        # Apply move
        old_board = game.board
        old_ep = game.ep_square
        old_cr = {k: {kk: vv for kk, vv in v.items()} for k, v in game.castling_rights.items()}

        game.board = apply_move(game.board, r, c, nr, nc, game.ep_square, game.castling_rights)
        score = alphabeta(game, depth=3, alpha=alpha, beta=beta, maximizing=False)

        # Restore
        game.board = old_board
        game.ep_square = old_ep
        game.castling_rights = old_cr

        if score > best_score:
            best_score = score
            best_move = (r, c, nr, nc)
        alpha = max(alpha, score)

    return best_move


def minimax(game, depth, maximizing):
    """Minimax algorithm"""
    if depth == 0 or game.game_over:
        return evaluate_board(game.board)

    color = game.current_color
    moves = game.get_legal_moves(color)

    if not moves:
        if in_check(game.board, color):
            return -20000 if maximizing else 20000
        return 0

    if maximizing:
        best_score = float('-inf')
        for r, c, nr, nc in moves:
            old_board = game.board
            old_ep = game.ep_square
            old_cr = {k: {kk: vv for kk, vv in v.items()} for k, v in game.castling_rights.items()}

            game.board = apply_move(game.board, r, c, nr, nc, game.ep_square, game.castling_rights)
            score = minimax(game, depth - 1, False)

            game.board = old_board
            game.ep_square = old_ep
            game.castling_rights = old_cr

            best_score = max(best_score, score)
        return best_score
    else:
        best_score = float('inf')
        for r, c, nr, nc in moves:
            old_board = game.board
            old_ep = game.ep_square
            old_cr = {k: {kk: vv for kk, vv in v.items()} for k, v in game.castling_rights.items()}

            game.board = apply_move(game.board, r, c, nr, nc, game.ep_square, game.castling_rights)
            score = minimax(game, depth - 1, True)

            game.board = old_board
            game.ep_square = old_ep
            game.castling_rights = old_cr

            best_score = min(best_score, score)
        return best_score


def alphabeta(game, depth, alpha, beta, maximizing):
    """Alpha-beta pruning"""
    if depth == 0 or game.game_over:
        return evaluate_board(game.board)

    color = game.current_color
    moves = game.get_legal_moves(color)

    if not moves:
        if in_check(game.board, color):
            return -20000 if maximizing else 20000
        return 0

    if maximizing:
        best_score = float('-inf')
        for r, c, nr, nc in moves:
            old_board = game.board
            old_ep = game.ep_square
            old_cr = {k: {kk: vv for kk, vv in v.items()} for k, v in game.castling_rights.items()}

            game.board = apply_move(game.board, r, c, nr, nc, game.ep_square, game.castling_rights)
            score = alphabeta(game, depth - 1, alpha, beta, False)

            game.board = old_board
            game.ep_square = old_ep
            game.castling_rights = old_cr

            best_score = max(best_score, score)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score
    else:
        best_score = float('inf')
        for r, c, nr, nc in moves:
            old_board = game.board
            old_ep = game.ep_square
            old_cr = {k: {kk: vv for kk, vv in v.items()} for k, v in game.castling_rights.items()}

            game.board = apply_move(game.board, r, c, nr, nc, game.ep_square, game.castling_rights)
            score = alphabeta(game, depth - 1, alpha, beta, True)

            game.board = old_board
            game.ep_square = old_ep
            game.castling_rights = old_cr

            best_score = min(best_score, score)
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score


# Run AI
def get_ai_move(game, difficulty):
    """Get AI move based on difficulty"""
    start_time = time.time()

    if difficulty == 'easy':
        move = ai_easy(game)
        algorithm = 'Random'
        depth = '-'
    elif difficulty == 'medium':
        move = ai_medium(game)
        algorithm = 'Minimax'
        depth = '3'
    else:  # hard
        move = ai_hard(game)
        algorithm = 'Alpha-Beta'
        depth = '4'

    elapsed = time.time() - start_time
    return move, algorithm, depth, elapsed


if __name__ == "__main__":
    # Quick test
    game = ChessGame()
    print("Chess AI Engine Ready")
    print(f"Initial position evaluation: {evaluate_board(game.board)}")