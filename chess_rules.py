"""Chess Rules Engine - Pure chess logic, no AI"""


def start_board():
    """Returns standard 8x8 starting position"""
    board = [[None] * 8 for _ in range(8)]

    # Black pieces
    board[0] = ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br']
    board[1] = ['bp'] * 8

    # White pieces
    board[6] = ['wp'] * 8
    board[7] = ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']

    return board


def get_piece_color(piece):
    """Returns 'white' or 'black' or None"""
    if piece is None:
        return None
    return 'white' if piece[0] == 'w' else 'black'


def piece_type(piece):
    """Returns 'p', 'n', 'b', 'r', 'q', 'k' or None"""
    if piece is None:
        return None
    return piece[1]


def is_empty(board, r, c):
    return 0 <= r < 8 and 0 <= c < 8 and board[r][c] is None


def is_enemy(board, r, c, color):
    return 0 <= r < 8 and 0 <= c < 8 and get_piece_color(board[r][c]) == color


def slide_moves(board, r, c, directions, color, ep=None, cr=None):
    """Generate sliding piece moves"""
    moves = []
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while 0 <= nr < 8 and 0 <= nc < 8:
            if board[nr][nc] is None:
                moves.append((nr, nc))
            elif get_piece_color(board[nr][nc]) != color:
                moves.append((nr, nc))
                break
            else:
                break
            nr += dr
            nc += dc
    return moves


def legal_moves(board, r, c, ep=None, cr=None):
    """All legal moves for piece at (r,c)"""
    piece = board[r][c]
    if piece is None:
        return []

    color = get_piece_color(piece)
    ptype = piece_type(piece)
    moves = []

    if ptype == 'p':  # Pawn
        direction = -1 if color == 'white' else 1
        start_row = 6 if color == 'white' else 1

        # Forward move
        if is_empty(board, r + direction, c):
            moves.append((r + direction, c))
            # Double move from start
            if r == start_row and is_empty(board, r + 2 * direction, c):
                moves.append((r + 2 * direction, c))

        # Captures
        for dc in [-1, 1]:
            nc = c + dc
            nr = r + direction
            if 0 <= nr < 8 and 0 <= nc < 8:
                # Normal capture
                if board[nr][nc] and get_piece_color(board[nr][nc]) != color:
                    moves.append((nr, nc))
                # En passant
                if ep and nr == ep[0] and nc == ep[1]:
                    moves.append((nr, nc))

    elif ptype == 'n':  # Knight
        offsets = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
        for dr, dc in offsets:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                if board[nr][nc] is None or get_piece_color(board[nr][nc]) != color:
                    moves.append((nr, nc))

    elif ptype == 'b':  # Bishop
        moves = slide_moves(board, r, c, [(-1,-1),(-1,1),(1,-1),(1,1)], color)

    elif ptype == 'r':  # Rook
        moves = slide_moves(board, r, c, [(-1,0),(1,0),(0,-1),(0,1)], color)

    elif ptype == 'q':  # Queen
        moves = slide_moves(board, r, c, [(-1,-1),(-1,1),(1,-1),(1,1),(-1,0),(1,0),(0,-1),(0,1)], color)

    elif ptype == 'k':  # King
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    if board[nr][nc] is None or get_piece_color(board[nr][nc]) != color:
                        moves.append((nr, nc))

        # Castling
        if cr:
            # Kingside
            if cr[color]['k'] and is_empty(board, r, c+1) and is_empty(board, r, c+2):
                if not is_attacked(board, r, c, color) and not is_attacked(board, r, c+1, color) and not is_attacked(board, r, c+2, color):
                    moves.append((r, c+2))
            # Queenside
            if cr[color]['q'] and is_empty(board, r, c-1) and is_empty(board, r, c-2) and is_empty(board, r, c-3):
                if not is_attacked(board, r, c, color) and not is_attacked(board, r, c-1, color) and not is_attacked(board, r, c-2, color):
                    moves.append((r, c-2))

    # Filter out moves that leave king in check
    legal = []
    for nr, nc in moves:
        new_board = apply_move(board, r, c, nr, nc, ep, cr, False)
        if not in_check(new_board, color):
            legal.append((nr, nc))

    return legal


def is_attacked(board, r, c, by_color):
    """Check if square (r,c) is attacked by by_color"""
    # Pawn attacks
    direction = -1 if by_color == 'white' else 1
    for dc in [-1, 1]:
        nr, nc = r + direction, c + dc
        if 0 <= nr < 8 and 0 <= nc < 8:
            if board[nr][nc] == ('wp' if by_color == 'white' else 'bp'):
                return True

    # Knight attacks
    offsets = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
    for dr, dc in offsets:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 8 and 0 <= nc < 8:
            piece = board[nr][nc]
            if piece and piece_type(piece) == 'n' and get_piece_color(piece) == by_color:
                return True

    # King attacks
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                piece = board[nr][nc]
                if piece and piece_type(piece) == 'k' and get_piece_color(piece) == by_color:
                    return True

    # Sliding pieces (bishop, rook, queen)
    directions = [(-1,-1),(-1,1),(1,-1),(1,1),(-1,0),(1,0),(0,-1),(0,1)]
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while 0 <= nr < 8 and 0 <= nc < 8:
            piece = board[nr][nc]
            if piece:
                ptype = piece_type(piece)
                color = get_piece_color(piece)
                if color == by_color:
                    if ptype in ['b', 'q'] and dr in [-1, 1] and dc in [-1, 1]:
                        return True
                    if ptype in ['r', 'q'] and (dr == 0 or dc == 0):
                        return True
                break
            nr += dr
            nc += dc

    return False


def in_check(board, color):
    """Is color's king in check?"""
    # Find king
    king_piece = 'wk' if color == 'white' else 'bk'
    for r in range(8):
        for c in range(8):
            if board[r][c] == king_piece:
                return is_attacked(board, r, c, 'black' if color == 'white' else 'white')
    return False


def all_legal_moves(board, color, ep=None, cr=None):
    """All legal moves for a color"""
    moves = []
    for r in range(8):
        for c in range(8):
            if get_piece_color(board[r][c]) == color:
                for move in legal_moves(board, r, c, ep, cr):
                    moves.append((r, c, move[0], move[1]))
    return moves


def apply_move(board, r, c, nr, nc, ep=None, cr=None, check_legal=True):
    """Apply a move, returns new board"""
    new_board = [row[:] for row in board]
    piece = new_board[r][c]

    # Handle en passant capture
    if piece_type(piece) == 'p' and nc != c and new_board[nr][nc] is None:
        captured_row = r if get_piece_color(piece) == 'white' else r
        new_board[captured_row][nc] = None

    # Move piece
    new_board[nr][nc] = piece
    new_board[r][c] = None

    # Handle castling move
    if piece_type(piece) == 'k' and abs(nc - c) == 2:
        if nc > c:  # Kingside
            new_board[r][5] = new_board[r][7]
            new_board[r][7] = None
        else:  # Queenside
            new_board[r][3] = new_board[r][0]
            new_board[r][0] = None

    # Pawn promotion - promote to queen
    if piece_type(piece) == 'p':
        if (get_piece_color(piece) == 'white' and nr == 0) or (get_piece_color(piece) == 'black' and nr == 7):
            new_board[nr][nc] = 'wq' if get_piece_color(piece) == 'white' else 'bq'

    return new_board


def is_checkmate(board, color, ep=None, cr=None):
    """Is it checkmate?"""
    if not in_check(board, color):
        return False
    return len(all_legal_moves(board, color, ep, cr)) == 0


def is_stalemate(board, color, ep=None, cr=None):
    """Is it stalemate?"""
    if in_check(board, color):
        return False
    return len(all_legal_moves(board, color, ep, cr)) == 0


def is_insufficient_material(board):
    """Insufficient material draw"""
    pieces = {'white': [], 'black': []}
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece:
                color = get_piece_color(piece)
                ptype = piece_type(piece)
                pieces[color].append(ptype)

    white, black = pieces['white'], pieces['black']

    # K vs K
    if len(white) == 1 and len(black) == 1:
        return True

    # K+B vs K or K+N vs K
    if len(white) == 1 and len(black) == 2 and 'k' in black and ('b' in black or 'n' in black):
        return True
    if len(black) == 1 and len(white) == 2 and 'k' in white and ('b' in white or 'n' in white):
        return True

    return False


def evaluate_board(board):
    """Static evaluation score (positive = white better)"""
    piece_values = {'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 20000}

    # Positional bonuses
    pawn_bonus = [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5,  5, 10, 25, 25, 10,  5,  5],
        [0,  0,  0, 20, 20,  0,  0,  0],
        [5, -5, -10,  0,  0, -10, -5,  5],
        [5, 10, 10, -20, -20, 10, 10,  5],
        [0,  0,  0,  0,  0,  0,  0,  0]
    ]

    knight_bonus = [
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20,  0,  0,  0,  0, -20, -40],
        [-30,  0, 10, 15, 15, 10,  0, -30],
        [-30,  5, 15, 20, 20, 15,  5, -30],
        [-30,  0, 15, 20, 20, 15,  0, -30],
        [-30,  5, 10, 15, 15, 10,  5, -30],
        [-40, -20,  0,  5,  5,  0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50]
    ]

    score = 0
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece:
                value = piece_values.get(piece_type(piece), 0)
                color = get_piece_color(piece)

                # Add positional bonus
                bonus = 0
                if piece_type(piece) == 'p':
                    bonus = pawn_bonus[r][c] if color == 'white' else pawn_bonus[7-r][c]
                elif piece_type(piece) == 'n':
                    bonus = knight_bonus[r][c] if color == 'white' else knight_bonus[7-r][c]

                if color == 'white':
                    score += value + bonus
                else:
                    score -= value + bonus

    return score