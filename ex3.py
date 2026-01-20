from typing import Any, List
from itertools import product
from collections import Counter

ids = ["111111111, 222222222"]

''''
input layout:
list[
    tuple[int, int]: (width, length) of each rectangle
    tuple[int, int, int]: (x, y, val) of each pre-filled cell
    tuple[int, int, int, int, int]: (x1, y1, x2, y2, sum) of each sum constraint
]
 '''


def to_CNF(input: list[tuple[int, int], tuple[int, int, int], tuple[int, int, int, int, int]]) -> tuple[
    list, list[list[tuple[Any, bool]]]]:
    # print(input)
    L, K = input[0]
    known_locations = input[1]
    sum_constraints = input[2]

    N = L * K

    variables = [f'{i},{j},{v}' for i in range(N) for j in range(N) for v in range(1, N + 1)]

    clauses = []

    # apply known locations:
    for x, y, val in known_locations:
        # add unit clause
        clauses.append([(f'{x},{y},{val}', True)])
        # set all other values for that cell to False
        for other_val in range(1, N + 1):
            if other_val != val:
                #variables.remove(f'{x},{y},{other_val}')
                clauses.append([(f'{x},{y},{other_val}', False)])

    # Every square has exactly one number in it:
    for i, j in product(range(N), range(N)):
        # some value should be in the square - unit clause
        clauses.append([(f'{i},{j},{val}', True) for val in range(1, N + 1)])

        # if some digit d is in the square then d` shouldn't be
        for val1, val2 in product(range(1, N + 1), range(1, N + 1)):
            if val1 < val2:
                clauses.append([(f'{i},{j},{val1}', False), (f'{i},{j},{val2}', False)])

    # A number never appears twice in the same row:
    for digit in range(1, N + 1):
        for row in range(N):
            for col1, col2 in product(range(N), range(N)):
                if col1 < col2:
                    clauses.append([(f'{row},{col1},{digit}', False), (f'{row},{col2},{digit}', False)])

    # A number never appears twice in the same column:
    for digit in range(1, N + 1):
        for col in range(N):
            for row1, row2 in product(range(N), range(N)):
                if row1 < row2:
                    clauses.append([(f'{row1},{col},{digit}', False), (f'{row2},{col},{digit}', False)])

    # A number never appears twice in the same rectangle:
    for i1, j1 in product(range(N), range(N)):
        for i2, j2 in product(range(N), range(N)):
            if (i1 // L == i2 // L) and (j1 // K == j2 // K) and (i1 < i2 or (i1 == i2 and j1 < j2)):
                for digit in range(1, N + 1):
                    clauses.append([(f'{i1},{j1},{digit}', False), (f'{i2},{j2},{digit}', False)])

    # sum constraints:
    for constraint in sum_constraints:
        x1, y1, x2, y2, target_sum = constraint
        for val in range(1, N + 1):
            if target_sum - val >= 1 and target_sum - val <= N:
                clauses.append([(f'{x1},{y1},{val}', False), (f'{x2},{y2},{target_sum - val}', True)])
                clauses.append([(f'{x1},{y1},{val}', True), (f'{x2},{y2},{target_sum - val}', False)])
            else:
                clauses.append([(f'{x1},{y1},{val}', False)])

    # print(f'CNF has {len(clauses)} clauses and {len(variables)} variables')
    return variables, clauses


def unit_propogation(variables, CNF_formula, assignment):
    while True:
        # Check current status
        units = []
        conflict = False

        # We will rebuild the formula to filter out satisfied clauses
        new_formula = []

        for clause in CNF_formula:
            status, value = clause_status(clause, assignment)

            if status == "conflict":
                return False, []  # Backtrack immediately
            elif status == "satisfied":
                continue  # Remove this clause from consideration
            elif status == "unit":
                units.append(value)  # value is (variable, bool_val)
                new_formula.append(clause)
            else:
                new_formula.append(clause)

        # If formula is empty, we solved it!
        if not new_formula:
            return True, assignment

        # Update formula for the next iteration
        CNF_formula = new_formula

        # If no new unit clauses were found, stop propagating
        if not units:
            break

        # Apply all found unit assignments
        # We use a set to avoid processing the same unit assignment twice in one pass
        for var_name, bool_val in set(units):
            # Conflict check: if we try to assign True to something already False
            if var_name in assignment and assignment[var_name] != bool_val:
                return False, []
            assignment[var_name] = bool_val

    return None


def solve_SAT(variables, CNF_formula, assignment) -> tuple[bool, list]:
    # 1. Simplify formula based on current assignment (Unit Propagation Loop)
    # We loop until no more unit clauses are found
    res = unit_propogation(variables, CNF_formula, assignment)

    if res is not None:
        return res

    # 2. Variable Selection Heuristic (DLIS)
    # Count how often each unassigned variable appears in the remaining clauses
    # We want to pick the variable that appears most often (to simplify the most clauses)
    literal_counts = Counter()
    for clause in CNF_formula:
        for (var, is_true) in clause:
            if var not in assignment:
                literal_counts[var] += 1

    # If no variables left to assign but formula not empty (shouldn't happen if logic is correct)
    if not literal_counts:
        return True, assignment

    # Pick variable with highest count
    chosen_var, _ = literal_counts.most_common(1)[0]

    # 3. Recursive Backtracking (Branching)
    # Try setting chosen_var to True
    assignment_true = assignment.copy()
    assignment_true[chosen_var] = True
    is_sat, res_assignment = solve_SAT(variables, CNF_formula, assignment_true)
    if is_sat:
        return True, res_assignment

    # If True failed, try False
    assignment_false = assignment.copy()
    assignment_false[chosen_var] = False
    is_sat, res_assignment = solve_SAT(variables, CNF_formula, assignment_false)
    if is_sat:
        return True, res_assignment

    # If both failed, this path is dead
    return False, []


# assignment structure: dict{ variable_name (str) -> bool_value (bool) }
def clause_status(clause, assignment):
    # "satisfied": at least one literal is True
    # "conflict": all literals are False
    # "unit": all but one are False, one is unassigned
    # "unresolved": otherwise

    unassigned_literals = []

    for var, is_positive in clause:
        # Check if variable is assigned
        if var in assignment:
            val = assignment[var]
            # If the assignment matches the literal polarity, the clause is satisfied
            if val == is_positive:
                return "satisfied", None
        else:
            unassigned_literals.append((var, is_positive))

    # If we are here, no literal satisfied the clause yet.

    if len(unassigned_literals) == 0:
        return "conflict", None

    if len(unassigned_literals) == 1:
        # Unit clause! We must set this literal to match its polarity
        # logic: if literal is (A, False), we must set A=False to satisfy.
        var, is_positive = unassigned_literals[0]
        return "unit", (var, is_positive)

    return "unresolved", None


def numbers_assignment(variables: list, assignment: dict, input: Any) -> List[List[int]]:
    L, K = input[0]
    N = L * K
    board = [[0 for _ in range(N)] for _ in range(N)]

    for var in variables:
        if var in assignment.keys() and assignment[var]:
            i, j, v = map(int, var.split(','))
            board[i][j] = v
    #print(board)
    return board
