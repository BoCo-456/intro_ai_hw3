generated_problems = [
    # Problem 1: 6x6 Board (Rectangles 2x3).
    # Difficulty: Sparse givens with "Killer Sudoku" style sum chains.
    [
        (2, 3), # K=2, L=3. Board is 6x6. [cite: 7, 8]
        # Minimal Givens
        [
            (0, 0, 1), (1, 5, 4), (2, 2, 1), (3, 3, 2), (4, 0, 3), (5, 5, 2)
        ],
        # Complex Sum Constraints
        [
            (0, 1, 0, 2, 5),   # Neighbors in Row 0
            (1, 0, 2, 0, 6),   # Neighbors in Col 0
            (0, 5, 1, 5, 7),   # Vertical pair
            (2, 3, 2, 4, 9),   # Horizontal pair
            (3, 0, 3, 1, 7),   # Horizontal pair
            (3, 4, 3, 5, 5),   # Horizontal pair
            (4, 4, 5, 4, 5),   # Vertical pair crossing blocks
            (4, 1, 5, 1, 9),   # Vertical pair
            (1, 2, 2, 2, 8)    # Vertical pair
        ],
    ],

    # Problem 2: 9x9 Board (Rectangles 3x3).
    # Difficulty: Standard size but with extremely low givens and high sum constraints.
    [
        (3, 3), # K=3, L=3. Board is 9x9. [cite: 7, 8]
        # Very Sparse Givens
        [
            (0, 0, 1), (4, 4, 9), (8, 8, 5), (1, 8, 3), (7, 0, 6)
        ],
        # Sum Constraints forcing logic chains
        [
            (0, 1, 0, 2, 5),   # 2+3? 1+4?
            (1, 0, 2, 0, 11),
            (0, 8, 1, 8, 12),
            (2, 3, 2, 4, 6),
            (3, 5, 3, 6, 13),
            (5, 2, 6, 2, 10),
            (6, 6, 6, 7, 14),
            (7, 1, 8, 1, 7),
            (8, 3, 8, 4, 8),
            (4, 0, 5, 0, 13),
            (4, 8, 5, 8, 5)
        ],
    ],

    # Problem 3: 8x8 Board (Rectangles 4x2).
    # Difficulty: Unusual geometry (tall/narrow rectangles) which changes valid placements.
    [
        (4, 2), # K=4, L=2. Board is 8x8. [cite: 10]
        # Givens placed to disrupt easy row/col elimination
        [
            (0, 0, 1), (0, 7, 8),
            (3, 3, 4), (4, 4, 4),
            (7, 0, 8), (7, 7, 5)
        ],
        # Sum Constraints
        [
            (0, 1, 1, 1, 6),
            (2, 2, 2, 3, 15), # High sum forces high numbers (7+8)
            (3, 0, 4, 0, 9),  # Crosses the horizontal middle line of board
            (1, 5, 2, 5, 11),
            (5, 6, 5, 7, 3),  # Low sum forces low numbers (1+2)
            (6, 2, 6, 3, 13),
            (7, 4, 7, 5, 7)
        ],
    ]
]