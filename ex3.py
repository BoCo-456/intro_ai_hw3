from typing import Any, List, Optional, Tuple
from itertools import product
from collections import Counter, defaultdict
from functools import lru_cache

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
                # variables.remove(f'{x},{y},{other_val}')
                # clauses.append([(f'{x},{y},{other_val}', False)])
                pass

    # Every square has exactly one number in it:
    for i, j in product(range(N), range(N)):
        # some value should be in the square - unit clause
        clauses.append([(f'{i},{j},{val}', True) for val in range(1, N + 1)])

        # if some digit d is in the square then d' shouldn't be
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
            # Check if same box
            same_box = (i1 // L == i2 // L) and (j1 // K == j2 // K)

            # Ensure we only process pairs once (ordering)
            valid_ordering = (i1 < i2 or (i1 == i2 and j1 < j2))

            # REDUNDANCY CHECK: Skip if they share a row (i1==i2) or col (j1==j2)
            # We only want diagonal relationships within the box here.
            not_row_or_col = (i1 != i2) and (j1 != j2)

            if same_box and valid_ordering and not_row_or_col:
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


'''
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
'''


def unit_propogation(variables, CNF_formula, assignment):
    current_formula = CNF_formula

    while True:
        units = []
        new_formula = []

        for clause in current_formula:
            status, value = clause_status(clause, assignment)

            if status == "conflict":
                return False, [], []
            elif status == "satisfied":
                continue
            elif status == "unit":
                units.append(value)
                new_formula.append(clause)
            else:
                new_formula.append(clause)

        # Update formula for next pass
        current_formula = new_formula

        if not units:
            # RETURN THE SIMPLIFIED FORMULA
            return None, assignment, current_formula

        # Determine assignments
        new_assignments = {}
        for var_name, bool_val in units:
            if var_name in assignment and assignment[var_name] != bool_val:
                return False, [], []  # Conflict
            if var_name in new_assignments and new_assignments[var_name] != bool_val:
                return False, [], []  # Conflict within current unit batch

            assignment[var_name] = bool_val
            new_assignments[var_name] = bool_val

        # If the formula is empty, we are done
        if not current_formula:
            return True, assignment, []


def solve_SAT(variables, CNF_formula, assignment) -> tuple[bool, list]:
    # 1. Simplify formula (Unit Propagation)
    # Note: We now capture the simplified 'current_formula'
    res_status, res_assignment, simplified_formula = unit_propogation(variables, CNF_formula, assignment)

    if res_status is False:
        return False, []
    if res_status is True:
        return True, res_assignment

    # 2. Select Variable
    # Note: Pass simplified_formula to MOM (faster)
    # Note: Pass variables list to MRV (required)

    # chosen_var = heuristic_MOM(simplified_formula, assignment)
    chosen_var = heuristic_MRV(variables, assignment)

    if chosen_var is None:
        # Logic safeguard: if no var chosen but formula not empty
        return True, assignment

    # 3. Recursive Backtracking

    # Try True
    assignment_true = assignment.copy()
    assignment_true[chosen_var] = True
    is_sat, final_assign = solve_SAT(variables, simplified_formula, assignment_true)
    if is_sat:
        return True, final_assign

    # Try False
    assignment_false = assignment.copy()
    assignment_false[chosen_var] = False
    is_sat, final_assign = solve_SAT(variables, simplified_formula, assignment_false)
    if is_sat:
        return True, final_assign

    return False, []


def get_unassigned_vars(clause, assignment):
    """Helper: Returns list of variables in a clause that are not yet in assignment."""
    return [lit[0] for lit in clause if lit[0] not in assignment]


# --- Helper with Caching ---
@lru_cache(maxsize=None)
def get_var_coords(var_str: str) -> tuple[str, str]:
    """
    Parses 'row,col,val' and returns ('row', 'col').
    Cached to avoid repeated string splitting.
    """
    parts = var_str.split(',')
    return parts[0], parts[1]


# --- Optimized Heuristics ---

def heuristic_MOM(clauses: list, assignment: dict) -> Optional[str]:
    """
    Maximum Occurrences in Minimum Length Clauses.
    Optimized to avoid list allocations and unnecessary looping.
    """
    min_len = float('inf')
    counts = defaultdict(int)

    for clause in clauses:
        # 1. Check if satisfied & count unassigned in one pass
        # This avoids creating a list of unassigned vars unless needed
        unassigned = []
        is_satisfied = False

        for var, polarity in clause:
            if var in assignment:
                if assignment[var] == polarity:
                    is_satisfied = True
                    break
            else:
                unassigned.append(var)

        if is_satisfied:
            continue

        # 2. Process active clause
        curr_len = len(unassigned)
        if curr_len == 0:
            continue  # Conflict (should be handled by unit_prop, but safety first)

        if curr_len < min_len:
            min_len = curr_len
            counts.clear()  # Reset counts for new minimum length
            for var in unassigned:
                counts[var] += 1
        elif curr_len == min_len:
            for var in unassigned:
                counts[var] += 1

    if not counts:
        return None
    return max(counts, key=counts.get)


def heuristic_MRV(variables: list, assignment: dict) -> Optional[str]:
    """
    Minimum Remaining Values (Sudoku Specific).
    Iterates variables directly (O(N)) instead of clauses (O(M)).
    """
    cell_counts = defaultdict(int)
    cell_vars = defaultdict(list)

    # Iterate ALL variables to find unassigned ones
    for var in variables:
        if var not in assignment:
            r, c = get_var_coords(var)
            cell_key = (r, c)
            cell_counts[cell_key] += 1
            cell_vars[cell_key].append(var)

    if not cell_counts:
        return None

    # Find the cell with the minimum (>0) candidates
    # This implies the most constrained cell
    best_cell = min(cell_counts, key=cell_counts.get)

    # Return the first available variable for that cell
    return cell_vars[best_cell][0]


'''
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
    # chosen_var, _ = literal_counts.most_common(1)[0]

    # Option 2: MOM (Good for general SAT performance)
    chosen_var = heuristic_MOM(CNF_formula, assignment)

    # Option 3: MRV (Best for Sudoku logic)
    # chosen_var = heuristic_MRV(CNF_formula, assignment)

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
'''


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
    # print(board)
    return board
