# FORMAT:
# 1. (K, L) -> Rectangles are KxL. Board size N = K*L.
# 2. Initial assignments [(r, c, val), ...]
# 3. Sum constraints [(r1, c1, r2, c2, target_sum), ...]

hard_problems = [
    # ---------------------------------------------------------
    # PROBLEM 1: "The Arithmetic Grid" (6x6)
    # Dimensions: 2x3 (N=6).
    # Difficulty: Zero initial numbers. Purely driven by sum constraints.
    # Why it's hard: The solver has no "unit clauses" to start. 
    # It must branch immediately and rely on CNF sum logic to prune.
    # ---------------------------------------------------------
    [
        (3, 3), 
        [], # No initial clues!
        [
            # Row 0 pairs
            (0, 0, 0, 1, 3),  # Must be 1+2
            #(0, 2, 0, 3, 11), # Must be 5+6
            #(0, 4, 0, 5, 7),  # 3+4
            # Row 1 pairs
            #(1, 0, 1, 1, 9),  # 3+6 or 4+5 (but restricted by above)
            #(1, 2, 1, 3, 3),  # 1+2
            #(1, 4, 1, 5, 9),  
            # Vertical constraints to lock it in
            #(2, 0, 3, 0, 7),
            #(2, 5, 3, 5, 5),
            #(4, 2, 5, 2, 11),
            #(4, 3, 5, 3, 3)
        ]
    ],

    # ---------------------------------------------------------
    # PROBLEM 2: "The Dozen" (12x12)
    # Dimensions: 3x4 (N=12).
    # Difficulty: Scale. 144 cells, 12 values per cell = 1728 variables.
    # A naive encoding might produce too many clauses here.
    # ---------------------------------------------------------
    [
        (4, 5),
        [
            (0, 0, 1), (0, 11, 12), 
            #(5, 5, 6), (6, 6, 6),
            (11, 0, 12), (11, 11, 1)
        ],
        [
            # A few sums to complicate the center
            (5, 6, 6, 6, 13),
            (5, 5, 6, 5, 13) 
        ]
    ],

    # ---------------------------------------------------------
    # PROBLEM 3: "The Subtle UNSAT" (3x3)
    # Dimensions: 3x3 (N=9).
    # Difficulty: This board is impossible, but the contradiction 
    # isn't obvious until you propagate the sums.
    # ---------------------------------------------------------
    [
        (3, 3),
        [
            (0, 0, 9), (0, 1, 8), # Top left is heavy
            (8, 7, 1), (8, 8, 2)  # Bottom right is light
        ],
        [
            # We force a sum of 17 (8+9) in a column that already has 9.
            # But we place it far away so unit propagation doesn't catch it instantly.
            # (0,0) is 9. Column 0 cannot have another 9.
            # The constraint below asks for sum 17 in Col 0 (rows 7,8).
            # The only way to get 17 is 8+9. 
            # Since Col 0 already has a 9 at (0,0), this is impossible.
            (7, 0, 8, 0, 15) 
        ]
    ],

    # A problem from my sudoku book. Meant to be very hard
    [
        (3, 3),  # Rectangle dimensions (K=3, L=3) for a 9x9 board
        [
            (0, 1, 5), (0, 3, 1), (0, 5, 8),
            (1, 6, 9),
            (2, 3, 5),
            (3, 3, 3), (3, 4, 9), (3, 6, 7),
            (4, 0, 7), (4, 1, 8), (4, 7, 6),
            (5, 4, 4),
            (6, 7, 8), (6, 8, 5),
            (7, 0, 4), (7, 4, 6),
            (8, 0, 9)
        ],
        []  # No extra sum constraints for this standard puzzle
    ],

    # Another problem from my sudoku book. Meant to be very hard
    [
        (3, 3),  # Rectangle dimensions (K=3, L=3) for a 9x9 board
        [
            # Row 0
            (0, 2, 5), (0, 4, 2), (0, 5, 4), (0, 7, 7),
            # Row 1
            (1, 1, 8), (1, 2, 9),
            # Row 2
            (2, 0, 2), (2, 4, 1),
            # Row 3
            (3, 0, 1), (3, 5, 2), (3, 8, 3),
            # Row 4
            (4, 2, 7), (4, 6, 4), (4, 7, 5),
            # Row 5
            (5, 3, 9), (5, 4, 7),
            # Row 6
            (6, 1, 9), (6, 3, 7), (6, 6, 8),
            # Row 7
            (7, 8, 7),
            # Row 8
            (8, 3, 3), (8, 6, 1), (8, 8, 6)
        ],
        []  # No sum constraints visible in this specific input
    ]
]
non_comp_problems = hard_problems