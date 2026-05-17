# Chess AI Engine
### Minimax, Alpha-Beta Pruning & Random Search

![Python](https://img.shields.io/badge/Language-Python-blue?style=flat-square)
![AI](https://img.shields.io/badge/AI-Minimax%20%7C%20Alpha--Beta-green?style=flat-square)
![UI](https://img.shields.io/badge/UI-HTML-orange?style=flat-square)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=flat-square)
![Course](https://img.shields.io/badge/Course-Artificial%20Intelligence-red?style=flat-square)

---

## Overview

This repository implements a fully functional **Chess AI Engine** supporting three distinct difficulty levels, each powered by a different algorithmic strategy:

| Difficulty | Algorithm | Search Depth | Avg. Move Time |
|------------|-----------|-------------|----------------|
| Easy | Random Search | 0 | < 1 ms |
| Medium | Minimax | 3 | ~ 500 ms |
| Hard | Alpha-Beta Pruning | 4 | ~ 1–2 s |

The project demonstrates a clear progression from uninformed to informed adversarial search, implementing the core algorithms that underpin virtually every classical chess engine in existence. A playable **HTML-based UI** allows users to select difficulty and play against the AI directly in the browser.

---

## The Problem

Chess contains approximately **10¹²⁰ possible games** — the Shannon Number — larger than the number of atoms in the observable universe. Brute-force enumeration is computationally impossible. With an average branching factor of ~30 legal moves per position, node count explodes rapidly:

| Depth | Nodes Explored |
|-------|---------------|
| 1 | 30 |
| 3 | 27,000 |
| 4 | 810,000 |
| 5 | 24,300,000 |

The challenge is identifying the best move within a practical time budget, without exhaustively evaluating all future game states — requiring smart, selective search strategies.

---

## Architecture

The project follows a clean **separation of concerns** across two core Python files:

```
chess-ai-engine/
│
├── chess_rules.py       # Layer 1 — Game engine: board, move generation, rules
├── chess_game.py        # Layer 2 — AI layer: search algorithms, state management
├── chess_ui.html        # Playable UI — browser-based interface
└── README.md
```

This means the AI can be upgraded or replaced without touching any game logic, and the rules engine can be tested in isolation.

---

## Module Descriptions

### `chess_rules.py` — Chess Rules Engine

**Board Representation**
The board is an 8×8 Python list. Each cell is `None` (empty) or a two-character string encoding the piece — first character is colour (`w`/`b`), second is piece type (`p`/`n`/`b`/`r`/`q`/`k`).

**Move Generation**
Candidate moves are generated per piece type and filtered: each candidate is played on a temporary board and discarded if it leaves the moving side's king in check. Special moves fully supported: en passant, castling (with empty-square and check-path validation), and automatic queen promotion.

**Game Termination**
Handles checkmate, stalemate, insufficient material (K vs K, K+B vs K, K+N vs K), and the 50-move rule.

---

### `chess_game.py` — AI Algorithms

#### Easy Mode — Random Search
No lookahead, no evaluation. Selects a random legal move in O(1) time. Serves purely as a baseline.

#### Medium Mode — Minimax (Depth 3)
Models the game as a two-player zero-sum tree. The AI (maximiser) picks the move with the highest board score; the opponent (minimiser) picks the move with the lowest. At depth 3 the AI sees: AI move → opponent reply → AI follow-up. Explores approximately 27,000 nodes per move.

#### Hard Mode — Alpha-Beta Pruning (Depth 4)
Augments Minimax with two pruning parameters:
- **α** — the best score the maximiser is guaranteed so far (floor value)
- **β** — the best score the minimiser is guaranteed so far (ceiling value)

When β ≤ α, the current branch cannot affect the final decision and is pruned entirely. Move ordering (captures evaluated first) ensures tight α/β bounds are established early, maximising pruning efficiency. Reduces the effective node count from ~810,000 (plain Minimax depth 4) down to ~50,000 — bringing response time from ~15 seconds to 1–2 seconds.

---

## Board Evaluation Function

Both search algorithms use a static evaluation function:

```
score = Σ(white: material + positional bonus) − Σ(black: material + positional bonus)
```

**Piece Material Values:**

| Piece | Value |
|-------|-------|
| Pawn | 100 |
| Knight | 320 |
| Bishop | 330 |
| Rook | 500 |
| Queen | 900 |
| King | 20,000 |

Positional bonuses are applied via **piece-square tables** — lookup grids that reward pieces for occupying strategically valuable squares. The king's value of 20,000 exceeds all material combined, ensuring the AI always prioritises checkmate.

---

## Results

| Metric | Easy | Medium | Hard |
|--------|------|--------|------|
| Algorithm | Random | Minimax | Alpha-Beta |
| Search Depth | 0 | 3 | 4 |
| Avg. Move Time | < 1 ms | ~ 500 ms | ~ 1.5 s |
| Nodes per Move | 1 | ~ 27,000 | ~ 50,000 |
| Win Rate vs Easy | — | ≈ 95% | ≈ 99% |
| Win Rate vs Medium | — | — | ≈ 80% |

---

## How to Run

### Run the Engine
```bash
python chess_game.py
```

### Play via UI
Open `chess_ui.html` in your browser and select a difficulty level to play against the AI.

---

## Known Limitations

- Fixed search depth — no iterative deepening
- No transposition table — identical positions re-evaluated from scratch
- Simplified evaluation function — no king safety, pawn structure, or mobility terms
- No quiescence search — may miss tactics at search horizon
- Auto-queen promotion only — no underpromotion support
- No opening book or endgame tablebase
- No draw-by-repetition detection
- Pure Python — lower depth ceiling than C/C++ implementations

---

## Author

**Jon Abbas Kazmi**
BS Electronics and Computing
Artificial Intelligence — Course Project, May 2026

---

*Implements classical adversarial search — the same algorithmic foundation used by Stockfish and Deep Blue.*
