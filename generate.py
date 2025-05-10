import random

def generate_large_cnf(filename="example4.cnf.txt", num_vars=500000, num_clauses=2500000, clause_len_range=(3, 5)):
    with open(filename, 'w') as f:
        f.write(f"c Generated CNF with {num_vars} vars, {num_clauses} clauses\n")
        f.write(f"p cnf {num_vars} {num_clauses}\n")
        for _ in range(num_clauses):
            clause_len = random.randint(*clause_len_range)
            clause = set()
            while len(clause) < clause_len:
                var = random.randint(1, num_vars)
                sign = random.choice([-1, 1])
                clause.add(sign * var)
            f.write(" ".join(map(str, clause)) + " 0\n")

generate_large_cnf()
print("example1.txt generated.")
