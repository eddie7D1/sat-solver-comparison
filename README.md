# SAT Solver Comparison (DP, DPLL, CDCL)

This repo contains three basic SAT solvers written in Python: Davis–Putnam (DP), DPLL, and CDCL. 
They were built for a university project comparing classic algorithms for solving satisfiability problems.


Inside there are:
- `DP.py` – resolution-based solver (educational, not fast).
- `DPLL.py` – backtracking + unit propagation.
- `CDCL.py` – modern SAT solver with clause learning and backjumping.
- `benchmarks/` – sample `.cnf` files (in DIMACS format) used for testing the solvers. Generated for performance testing.



To run, just drop your `.cnf` files (or use ours in `benchmarks/`) and run the solvers from terminal.

```bash
python DPLL.py
python CDCL.py
python DP.py
