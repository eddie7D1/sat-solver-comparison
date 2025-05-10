import os
import time
import math

# Category constants for SAT solving results
class Cat:
    SATISFIED = 0      # Formula is satisfied
    UNSATISFIED = 1    # Formula is unsatisfied
    NORMAL = 2         # Normal status, no decision yet
    COMPLETED = 3      # Solving process completed

# Class to represent the formula in CNF
class Formula:
    def __init__(self):
        self.literals = []             # List of assigned literal values (-1 means unassigned)
        self.literal_frequency = []    # Frequency of each literal in clauses
        self.literal_polarity = []     # Sum of polarities (positive/negative) for each literal
        self.clauses = []              # List of clauses (each clause is a list of literals)

    def copy(self):
        # Deep copy of the formula for recursive DPLL steps
        new_formula = Formula()
        new_formula.literals = self.literals[:]
        new_formula.literal_frequency = self.literal_frequency[:]
        new_formula.literal_polarity = self.literal_polarity[:]
        new_formula.clauses = [clause[:] for clause in self.clauses]
        return new_formula

# Class implementing DPLL-based SAT solver
class SATSolverDPLL:
    def __init__(self):
        self.formula = Formula()
        self.literal_count = 0         # Total number of literals (variables)
        self.clause_count = 0          # Total number of clauses

    def initialize(self, lines):
        # Initialize formula from the lines of the input CNF file
        header_read = False
        clause = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('c'):
                continue  # Skip empty/comment lines
            if line.startswith('p'):
                # Read problem line (e.g., p cnf 3 2)
                parts = line.split()
                self.literal_count = int(parts[2])
                self.clause_count = int(parts[3])
                self.formula = Formula()
                self.formula.literals = [-1] * self.literal_count
                self.formula.literal_frequency = [0] * self.literal_count
                self.formula.literal_polarity = [0] * self.literal_count
                header_read = True
                continue

            if not header_read:
                raise ValueError("CNF header line (starting with 'p') missing.")

            # Parse clause literals
            for lit_str in line.split():
                literal = int(lit_str)
                if literal == 0:
                    # End of a clause
                    self.formula.clauses.append(clause)
                    clause = []
                else:
                    index = abs(literal) - 1
                    if index >= self.literal_count:
                        raise IndexError(f"Literal {literal} exceeds declared variable count {self.literal_count}.")
                    encoded = 2 * index + (1 if literal < 0 else 0)  # Encode literal
                    clause.append(encoded)
                    self.formula.literal_frequency[index] += 1
                    self.formula.literal_polarity[index] += (1 if literal > 0 else -1)

        if clause:  # Append any unfinished clause
            self.formula.clauses.append(clause)

    def unit_propagate(self, f):
        # Perform unit propagation
        if not f.clauses:
            return Cat.SATISFIED
        while True:
            unit_clause_found = False
            for clause in f.clauses:
                if len(clause) == 0:
                    return Cat.UNSATISFIED  # Empty clause means conflict
                if len(clause) == 1:
                    unit_clause_found = True
                    lit = clause[0]
                    var = lit // 2
                    val = lit % 2
                    f.literals[var] = val
                    f.literal_frequency[var] = -1
                    result = self.apply_transform(f, var)
                    if result in [Cat.SATISFIED, Cat.UNSATISFIED]:
                        return result
                    break
            if not unit_clause_found:
                break
        return Cat.NORMAL

    def apply_transform(self, f, var):
        # Simplify the formula after assigning a variable
        val = f.literals[var]
        i = 0
        while i < len(f.clauses):
            clause = f.clauses[i]
            j = 0
            while j < len(clause):
                lit = clause[j]
                if lit == 2 * var + val:
                    # Clause is satisfied; remove it
                    f.clauses.pop(i)
                    if not f.clauses:
                        return Cat.SATISFIED
                    i -= 1
                    break
                elif lit // 2 == var:
                    # Remove opposing literal from clause
                    clause.pop(j)
                    if not clause:
                        return Cat.UNSATISFIED
                    j -= 1
                    break
                j += 1
            i += 1
        return Cat.NORMAL

    def DPLL(self, f):
        # Main DPLL recursive algorithm
        result = self.unit_propagate(f)
        if result == Cat.SATISFIED:
            self.show_result(f, result)
            return Cat.COMPLETED
        elif result == Cat.UNSATISFIED:
            return Cat.NORMAL

        # Choose the most frequent unassigned variable
        i = max(range(len(f.literal_frequency)), key=lambda x: f.literal_frequency[x])
        for j in range(2):
            new_f = f.copy()
            if new_f.literal_polarity[i] > 0:
                new_f.literals[i] = j
            else:
                new_f.literals[i] = (j + 1) % 2
            new_f.literal_frequency[i] = -1
            result = self.apply_transform(new_f, i)
            if result == Cat.SATISFIED:
                self.show_result(new_f, result)
                return Cat.COMPLETED
            elif result == Cat.UNSATISFIED:
                continue
            dpll_result = self.DPLL(new_f)
            if dpll_result == Cat.COMPLETED:
                return dpll_result
        return Cat.NORMAL

    def show_result(self, f, result):
        # Output the SAT or UNSAT result
        if result == Cat.SATISFIED:
            print("SAT")
            output = []
            for i, val in enumerate(f.literals):
                if val == -1:
                    output.append(str(i + 1))
                else:
                    output.append(str((-1) ** val * (i + 1)))
            print(" ".join(output) + " 0")
        else:
            print("UNSAT")

    def solve(self):
        # Start solving process using DPLL
        result = self.DPLL(self.formula)
        if result == Cat.NORMAL:
            self.show_result(self.formula, Cat.UNSATISFIED)

def main():
    # Process all .txt or .cnf.txt files in the current folder
    folder = os.path.dirname(os.path.abspath(__file__))
    txt_files = [f for f in os.listdir(folder) if f.endswith('.txt') or f.endswith('.cnf.txt')]

    if not txt_files:
        print("No .txt or .cnf.txt files found in the folder.")
        return

    for filename in txt_files:
        print(f"\nProcessing {filename}...")
        start_time = time.time()

        try:
            with open(os.path.join(folder, filename), 'r') as file:
                lines = file.readlines()

            solver = SATSolverDPLL()
            solver.initialize(lines)
            solver.solve()
        except Exception as e:
            print(f"Error processing {filename}: {e}")

        end_time = time.time()
        print(f"Time taken: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    main()
