import os
import time

def is_pure_literal(literal, formula):
    opposite = -literal
    for clause in formula:
        if opposite in clause:
            return False
    return True

def find_pure_literals(formula):
    literals = set(l for clause in formula for l in clause)
    return [l for l in literals if is_pure_literal(l, formula)]

def resolve(clause1, clause2, literal):
    if literal not in clause1 or -literal not in clause2:
        return None
    new_clause = (set(clause1) | set(clause2)) - {literal, -literal}
    return list(new_clause)

def apply_resolution(formula, literal):
    pos_clauses = [c for c in formula if literal in c]
    neg_clauses = [c for c in formula if -literal in c]
    new_formula = []

    for clause in formula:
        if literal in clause or -literal in clause:
            continue
        new_formula.append(clause)

    for c1 in pos_clauses:
        for c2 in neg_clauses:
            res = resolve(c1, c2, literal)
            if res is not None:
                if len(res) == 0:
                    return None  # Empty clause → contradiction
                new_formula.append(res)

    return new_formula

def dp_solver(formula):
    while True:
        if not formula:
            return True  # SAT

        pure_literals = find_pure_literals(formula)
        if pure_literals:
            formula = [clause for clause in formula if all(l not in clause for l in pure_literals)]
            continue

        literals = set(l for clause in formula for l in clause)
        if not literals:
            return False  # UNSAT
        chosen_literal = next(iter(literals))

        new_formula = apply_resolution(formula, chosen_literal)
        if new_formula is None:
            return False
        formula = new_formula

def read_formula(filepath):
    formula = []
    with open(filepath, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('c') or line.startswith('p'):
                continue
            clause = list(map(int, line.split()))
            formula.append(clause)
    return formula


def run_all_formulas(folder="."):
    for filename in os.listdir(folder):
        print("Detected file:", filename)

        if not filename.endswith(".cnf") and not filename.endswith(".cnf.txt"):
            continue
        path = os.path.join(folder, filename)
        formula = read_formula(path)

        print(f"Solving {filename}...")
        start_time = time.time()
        result = dp_solver(formula)
        elapsed = time.time() - start_time
        print(f"  Result: {'SAT' if result else 'UNSAT'}")
        print(f"  Time: {elapsed:.6f} seconds\n")

if __name__ == "__main__":
    run_all_formulas()

