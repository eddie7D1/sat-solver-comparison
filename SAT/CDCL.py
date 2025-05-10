import os
import time
from collections import defaultdict, deque

class Cat:
    SATISFIED = 0
    UNSATISFIED = 1
    NORMAL = 2
    COMPLETED = 3

class Formula:
    def __init__(self):
        self.literals = []
        self.clauses = []
        self.watches = defaultdict(list)
        self.assign_stack = []
        self.reason = {}
        self.level = {}
        self.decision_level = 0

class SATSolverCDCL:
    def __init__(self):
        self.formula = Formula()
        self.literal_count = 0
        self.clause_count = 0

    def initialize(self, lines):
        header_read = False
        clause = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('c'):
                continue
            if line.startswith('p'):
                parts = line.split()
                self.literal_count = int(parts[2])
                self.clause_count = int(parts[3])
                self.formula.literals = [-1] * (self.literal_count + 1)
                header_read = True
                continue
            for lit_str in line.split():
                literal = int(lit_str)
                if literal == 0:
                    self.formula.clauses.append(clause)
                    if len(clause) >= 1:
                        self.formula.watches[clause[0]].append(clause)
                    if len(clause) >= 2:
                        self.formula.watches[clause[1]].append(clause)
                    clause = []
                else:
                    clause.append(literal)
        if clause:
            self.formula.clauses.append(clause)
            if len(clause) >= 1:
                self.formula.watches[clause[0]].append(clause)
            if len(clause) >= 2:
                self.formula.watches[clause[1]].append(clause)

    def pick_branching_variable(self):
        for i in range(1, self.literal_count + 1):
            if self.formula.literals[i] == -1:
                return i
        return None

    def value(self, lit):
        val = self.formula.literals[abs(lit)]
        if val == -1:
            return -1
        return val if lit > 0 else 1 - val

    def assign(self, lit, level, reason):
        var = abs(lit)
        val = 1 if lit > 0 else 0
        self.formula.literals[var] = val
        self.formula.assign_stack.append((lit, level))
        self.formula.level[var] = level
        self.formula.reason[var] = reason

    def propagate(self):
        queue = deque([lit for lit, val in enumerate(self.formula.literals) if val != -1])
        while queue:
            lit = queue.popleft()
            neg_lit = -lit
            watch_list = self.formula.watches[neg_lit][:]
            for clause in watch_list:
                if lit not in clause and neg_lit not in clause:
                    continue
                found_new_watch = False
                for alt in clause:
                    if alt != lit and alt != neg_lit and self.value(alt) != 0:
                        self.formula.watches[alt].append(clause)
                        self.formula.watches[neg_lit].remove(clause)
                        found_new_watch = True
                        break
                if not found_new_watch:
                    unassigned = [x for x in clause if self.value(x) == -1]
                    if not unassigned:
                        if all(self.value(x) == 0 for x in clause):
                            return clause  # conflict
                    elif len(unassigned) == 1:
                        u = unassigned[0]
                        self.assign(u, self.formula.decision_level, clause)
                        queue.append(u)
        return None

    def backtrack(self, level):
        while self.formula.assign_stack:
            lit, lvl = self.formula.assign_stack[-1]
            if lvl <= level:
                break
            self.formula.assign_stack.pop()
            var = abs(lit)
            self.formula.literals[var] = -1
            del self.formula.level[var]
            del self.formula.reason[var]

    def analyze_conflict(self, conflict_clause):
        learned = set()
        seen = set()
        path_count = 0
        current_level = self.formula.decision_level
        queue = list(conflict_clause)
        while queue:
            lit = queue.pop()
            var = abs(lit)
            if var in seen or self.formula.level.get(var, -1) != current_level:
                continue
            seen.add(var)
            reason = self.formula.reason.get(var, [])
            for l in reason:
                if abs(l) not in seen:
                    queue.append(l)
            path_count += 1
            if path_count == 1:
                learned.add(-lit)
        learned_clause = list(learned)
        backtrack_level = 0
        for lit in learned_clause:
            lvl = self.formula.level.get(abs(lit), 0)
            if lvl != current_level:
                backtrack_level = max(backtrack_level, lvl)
        return learned_clause, backtrack_level

    def cdcl(self):
        while True:
            conflict = self.propagate()
            if conflict:
                if self.formula.decision_level == 0:
                    self.show_result(self.formula, Cat.UNSATISFIED)
                    return Cat.COMPLETED
                learned_clause, back_level = self.analyze_conflict(conflict)
                self.formula.clauses.append(learned_clause)
                self.formula.watches[learned_clause[0]].append(learned_clause)
                if len(learned_clause) > 1:
                    self.formula.watches[learned_clause[1]].append(learned_clause)
                self.backtrack(back_level)
                self.formula.decision_level = back_level
                self.assign(learned_clause[0], back_level, learned_clause)
            else:
                var = self.pick_branching_variable()
                if var is None:
                    self.show_result(self.formula, Cat.SATISFIED)
                    return Cat.COMPLETED
                self.formula.decision_level += 1
                self.assign(var, self.formula.decision_level, [])

    def show_result(self, f, result):
        if result == Cat.SATISFIED:
            print("SAT")
            output = []
            for i in range(1, self.literal_count + 1):
                val = f.literals[i]
                if val == -1:
                    output.append(str(i))
                else:
                    output.append(str(i if val == 1 else -i))
            print(" ".join(output) + " 0")
        else:
            print("UNSAT")

    def solve(self):
        result = self.cdcl()
        if result == Cat.NORMAL:
            self.show_result(self.formula, Cat.UNSATISFIED)

def main():
    folder = os.getcwd()
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

            solver = SATSolverCDCL()
            solver.initialize(lines)
            solver.solve()
        except Exception as e:
            print(f"Error processing {filename}: {e}")

        end_time = time.time()
        print(f"Time taken: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    main()
