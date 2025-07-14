def generate_php(n=4, filename="php_n4.cnf.txt"):
    clauses = []
    for i in range(n + 1):  # n+1 pigeons
        clauses.append([i * n + j + 1 for j in range(n)])  # each pigeon in at least one hole
    for j in range(n):  # no two pigeons share the same hole
        for i in range(n + 1):
            for k in range(i + 1, n + 1):
                clauses.append([-(i * n + j + 1), -(k * n + j + 1)])
    num_vars = n * (n + 1)
    with open(filename, "w") as f:
        f.write(f"p cnf {num_vars} {len(clauses)}\n")
        for clause in clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")
    print(f"Generated {filename}")

def generate_triangle_coloring(filename="triangle_3color.cnf.txt"):
    # 3-coloring on triangle (3 nodes fully connected)
    vars_per_node = 3
    clauses = []
    for v in range(3):  # 3 nodes
        base = v * vars_per_node
        clauses.append([base + 1, base + 2, base + 3])  # at least one color
        clauses.append([-(base + 1), -(base + 2)])
        clauses.append([-(base + 1), -(base + 3)])
        clauses.append([-(base + 2), -(base + 3)])  # at most one color

    edges = [(0, 1), (1, 2), (0, 2)]
    for (u, v) in edges:
        for c in range(3):  # prevent u and v from sharing the same color
            clauses.append([-(u * 3 + c + 1), -(v * 3 + c + 1)])
    
    with open(filename, "w") as f:
        f.write(f"p cnf 9 {len(clauses)}\n")
        for clause in clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")
    print(f"Generated {filename}")

if __name__ == "__main__":
    generate_php()
    generate_triangle_coloring()
