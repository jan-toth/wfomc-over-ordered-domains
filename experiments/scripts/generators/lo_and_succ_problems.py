import numpy as np
import math
from sys import argv
from pathlib import Path


PHI_1 = lambda n: fr"""\forall X: (\forall Y: (~B(X, Y) | SUC(X, Y))) &
\forall X: (\forall Y: (~SUC(X, Y) | ~LEQ(X, Y) | B(X, Y)))

domain = {n}
"""

PHI_2 = lambda n: fr"""\forall X: (\forall Y: ((SUC(X, Y) & LEQ(X, Y)) -> (U(X) <-> ~U(Y))))

domain = {n}
"""

PHI_4 = lambda n: fr"""\forall X: (\forall Y: ((U1(X) & LEQ(X, Y)) -> U1(Y))) &
\forall X: (\forall Y: ((U1(X) & SUC(X, Y)) -> U2(Y)))

domain = {n}
"""

PHI_5 = lambda n: fr"""\forall X: (\forall Y: ((U1(X) & LEQ(X, Y)) -> U1(Y))) &
\forall X: (\forall Y: ((U1(X) & SUC(X, Y)) -> U2(Y))) &
\forall X: (\forall Y: (B(X, Y) -> (U1(X) & U2(Y))))

domain = {n}
"""

PHI_CARDS = lambda n: fr"""\forall X: (\forall Y:(SUC(X, Y) -> ~PRED(Y, X))) &
\forall X: (\forall Y: (SUC(X, Y) -> ~PRED(X, Y)))

domain = {n}
"""

class LOwithAnotherSuccProblems:

    def __init__(self):
        self.script_path = Path(__file__).absolute()
        self.output_dir = self.script_path.parent.parent.parent.joinpath("models").joinpath("lops")  # experiments/models/lops

        self.p1_dir = self.output_dir.joinpath("p1")
        self.p2_dir = self.output_dir.joinpath("p2")
        self.p4_dir = self.output_dir.joinpath("p4")
        self.p5_dir = self.output_dir.joinpath("p5")
        self.cards_dir = self.output_dir.joinpath("cards")



    def phi_p1(self, domain_size):
        output_name = self.p1_dir.joinpath("wfomcs").joinpath(f"a{domain_size}.wfomcs")
        with open(output_name, "w") as fw:
            fw.write(PHI_1(domain_size))

    def phi_p2(self, domain_size):
        output_name = self.p2_dir.joinpath("wfomcs").joinpath(f"b{domain_size}.wfomcs")
        with open(output_name, "w") as fw:
            fw.write(PHI_2(domain_size))

    def phi_p4(self, domain_size):
        output_name = self.p4_dir.joinpath("wfomcs").joinpath(f"c{domain_size}.wfomcs")
        with open(output_name, "w") as fw:
            fw.write(PHI_4(domain_size))

    def phi_p5(self, domain_size):
        output_name = self.p5_dir.joinpath("wfomcs").joinpath(f"d{domain_size}.wfomcs")
        with open(output_name, "w") as fw:
            fw.write(PHI_5(domain_size))

    def phi_cards(self, domain_size):
        output_name = self.cards_dir.joinpath("wfomcs").joinpath(f"cards{domain_size}.wfomcs")
        with open(output_name, "w") as fw:
            fw.write(PHI_CARDS(domain_size))

if __name__ == "__main__":
    gen = LOwithAnotherSuccProblems()

    small = False
    if small:
        for n in range(1, 16):
            # gen.phi_cards(n)
            # gen.phi_p1(n)
            # gen.phi_p2(n)
            gen.phi_p4(n)
            gen.phi_p5(n)
    else:
        for n in range(20,101,5):
            # gen.phi_cards(n)
            # gen.phi_p1(n)
            # gen.phi_p2(n)
            gen.phi_p4(n)
            gen.phi_p5(n)







# class cnf_problem:
#     def __init__(self, domain_size):
#         self.domain_size = domain_size
#         self.next_var = 1
#         self.vars = dict()
#         self.body = []
        
#     def get_leq(self, var_name="leq"):
#         self.vars[var_name] = np.arange(self.domain_size ** 2).reshape((self.domain_size, self.domain_size)) + self.next_var
#         self.next_var += self.domain_size ** 2
#         for i in range(self.domain_size):
#             self.body.append([self.vars[var_name][i, i]])
#         for i in range(self.domain_size):
#             for j in range(self.domain_size):
#                 if i < j:
#                     self.body.append([-self.vars[var_name][i, j], -self.vars[var_name][j, i]])
#                     self.body.append([self.vars[var_name][i, j], self.vars[var_name][j, i]])
#                 for k in range(self.domain_size):
#                     if j!= k and j != i and k!= i:
#                         self.body.append([-self.vars[var_name][i, j], -self.vars[var_name][j, k], self.vars[var_name][i, k]])
    
#     def fixed_leq(self, var_name="leq"):
#         self.vars[var_name] = np.arange(self.domain_size ** 2).reshape((self.domain_size, self.domain_size)) + self.next_var
#         self.next_var += self.domain_size ** 2
#         for i in range(self.domain_size):
#             for j in range(self.domain_size):
#                 if i <= j:
#                     self.body.append([self.vars[var_name][i, j]])
#                 else:
#                     self.body.append([-self.vars[var_name][i, j]])

#     def get_succ(self, leq="leq", var_name="suc"):
#         self.vars[var_name] = np.arange(self.domain_size ** 2).reshape((self.domain_size, self.domain_size)) + self.next_var
#         self.next_var += self.domain_size ** 2
#         for i in range(self.domain_size):
#             self.body.append([-self.vars[var_name][i, i]])
#             for j in range(self.domain_size):
#                 if j == i:
#                     continue
#                 self.body.append([self.vars[leq][i, j], -self.vars[var_name][i, j]])
#                 for k in range(self.domain_size):
#                     if k == i or k == j:
#                         continue
#                     self.body.append([-self.vars[leq][i, k], -self.vars[leq][k, j], -self.vars[var_name][i, j]])
#                     self.body.append([-self.vars[leq][k, i], -self.vars[leq][j, k], -self.vars[var_name][i, j]])
#         for i in range(self.domain_size):
#             for j in range(self.domain_size):
#                 if i != j:
#                     clause = [-self.vars[leq][i, j]]
#                     clause.extend(self.vars[var_name][i, :i])
#                     if i < self.domain_size - 1:
#                         clause.extend(self.vars[var_name][i, i + 1:])
#                     self.body.append(clause)

#     def to_file(self, fname):
#         with open(fname, "w") as f:
#             f.write(f"c domain size = {self.domain_size}\n")
#             f.write(f"p cnf {self.next_var - 1} {len(self.body)}\n")
#             for clause in self.body:
#                 out = " ".join(str(x) for x in clause)
#                 f.write(f"{out} 0\n")

#     def mark_lower_successors(self, leq="leq", suc="suc", var_name="p"):
#         #marks all successor relations, where x <= y and potentionally some more

#         # V x V y: (LEQ(x, y) & SUC(x, y)) -> P(x, y) &
#         # V x V y: P(x, y) -> SUC(x, y)
#         self.vars[var_name] = np.arange(self.domain_size ** 2).reshape((self.domain_size, self.domain_size)) + self.next_var
#         self.next_var += self.domain_size ** 2
#         for i in range(self.domain_size):
#             for j in range(self.domain_size):
#                 self.body.append([-self.vars[leq][i, j], self.vars[var_name][i, j], -self.vars[suc][i, j]])
#                 self.body.append([-self.vars[var_name][i, j], self.vars[suc][i, j]])

#     def mark_continuous(self, leq="leq", suc="suc", var_name="p"):
#         self.vars[var_name] = np.arange(self.domain_size) + self.next_var
#         self.next_var += self.domain_size
#         for i in range(self.domain_size):
#             for j in range(self.domain_size):
#                 self.body.append([-self.vars[var_name][i], -self.vars[suc][i, j], -self.vars[leq][i, j], self.vars[var_name][j]])
#                 self.body.append([self.vars[var_name][i], -self.vars[suc][i, j], -self.vars[leq][i, j], -self.vars[var_name][j]])
#                 self.body.append([-self.vars[var_name][i], -self.vars[suc][j, i], -self.vars[leq][j, i], self.vars[var_name][j]])
#                 self.body.append([self.vars[var_name][i], -self.vars[suc][j, i], -self.vars[leq][j, i], -self.vars[var_name][j]])

#     def a_b_problem(self, leq="leq", suc="suc", var_names=("p", "q")):
#         p = var_names[0]
#         q = var_names[1]
#         self.vars[p] = np.arange(self.domain_size) + self.next_var
#         print(self.vars[p])
#         self.next_var += self.domain_size
#         self.vars[q] = np.arange(self.domain_size) + self.next_var
#         self.next_var += self.domain_size
#         for i in range(self.domain_size):
#             for j in range(self.domain_size):
#                 if i!= j:
#                     self.body.append([-self.vars[p][i], -self.vars[leq][i, j], self.vars[p][j]])
#                     self.body.append([-self.vars[p][i], -self.vars[suc][i, j], self.vars[q][j]])

#     def a_b_r_problem(self, leq="leq", suc="suc", var_names=("p", "q", "r")):
#         p = var_names[0]
#         q = var_names[1]
#         r = var_names[2]
#         self.vars[p] = np.arange(self.domain_size) + self.next_var
#         self.next_var += self.domain_size
#         self.vars[q] = np.arange(self.domain_size) + self.next_var
#         self.next_var += self.domain_size
#         self.vars[r] = np.arange(self.domain_size**2).reshape((self.domain_size, self.domain_size)) + self.next_var
#         self.next_var += self.domain_size**2
#         for i in range(self.domain_size):
#             for j in range(self.domain_size):
#                 if i!= j:
#                     self.body.append([-self.vars[p][i], -self.vars[leq][i, j], self.vars[p][j]])
#                     self.body.append([-self.vars[p][i], -self.vars[suc][i, j], self.vars[q][j]])
#                 self.body.append([-self.vars[r][i, j], self.vars[p][i]])
#                 self.body.append([-self.vars[r][i, j], self.vars[q][j]])
    
#     def train(self, leq="leq", succ="suc", var_names=("V", "VR", "R")):
#         v = var_names[0]
#         vr = var_names[1]
#         r = var_names[2]
#         self.vars[v] = np.arange(self.domain_size) + self.next_var
#         self.next_var += self.domain_size
#         self.vars[vr] = np.arange(self.domain_size) + self.next_var
#         self.next_var += self.domain_size
#         self.vars[r] = np.arange(self.domain_size) + self.next_var
#         self.next_var += self.domain_size
#         for i in range(self.domain_size):
#             self.body.append([self.vars[v][i], self.vars[vr][i]])
#             self.body.append([-self.vars[v][i], -self.vars[vr][i]])
        
#         for i in range(self.domain_size):
#             for j in range(self.domain_size):
#                 if i == j:
#                     continue
#                 self.body.append(
#                     [-self.vars[succ][i, j], -self.vars[leq][i, j],
#                     -self.vars[v][i], -self.vars[r][i]])
#                 self.body.append(
#                     [-self.vars[succ][i, j], -self.vars[leq][i, j],
#                     -self.vars[vr][i], self.vars[r][i]])
#                 self.body.append(
#                     [-self.vars[succ][i, j], -self.vars[leq][j, i],
#                     -self.vars[v][i], self.vars[r][i]])
#                 self.body.append(
#                     [-self.vars[succ][i, j], -self.vars[leq][j, i],
#                     -self.vars[vr][i], -self.vars[r][i]])

#                 self.body.append(
#                     [-self.vars[r][i], -self.vars[v][i], 
#                         -self.vars[succ][i, j], self.vars[vr][j]])
#                 self.body.append(
#                     [self.vars[r][i], -self.vars[v][i], 
#                         -self.vars[succ][i, j], self.vars[v][j]])
#                 self.body.append(
#                     [-self.vars[r][i], -self.vars[vr][i], 
#                         -self.vars[succ][i, j], self.vars[v][j]])
#                 self.body.append(
#                     [self.vars[r][i], -self.vars[vr][i], 
#                         -self.vars[succ][i, j], self.vars[vr][j]])
        
#         self.body.append([self.vars[v][0]])
#         self.body.append([-self.vars[r][0]])
#         self.body.append([self.vars[v][-1]])
#         self.body.append([-self.vars[r][-1]])
#         for i in range(self.domain_size):
#             self.body.append([-self.vars[succ][i, 0]])
#             self.body.append([-self.vars[succ][-1, i]])

#         for i in range(self.domain_size):
#             for j in range(i + 1, self.domain_size):
#                 for k in range(j + 1, self.domain_size):
#                     if i == j or i == k or j == k:
#                         continue
#                     self.body.append([-self.vars[r][i],
#                         -self.vars[r][j], -self.vars[r][k]])
                    
#     def friends(self, leq="leq", suc="suc", var_names=("s")):
#         s = var_names[0]
#         self.vars[s] = np.arange(self.domain_size) + self.next_var
#         self.next_var += self.domain_size
#         fr = "fr"
#         self.vars[fr] = np.arange(self.domain_size**2).reshape((self.domain_size, self.domain_size)) + self.next_var
#         self.next_var += self.domain_size**2
#         for i in range(self.domain_size):
#             self.body.append([-self.vars[fr][i, i]])
#         for i in range(self.domain_size):
#             for j in range(self.domain_size):
#                 if i == j:
#                     continue
#                 self.body.append([-self.vars[fr][i, j], -self.vars[fr][j, i]])
#                 self.body.append([-self.vars[fr][i, j], -self.vars[s][i], -self.vars[leq][j, i], self.vars[s][j]])
#                 self.body.append([-self.vars[s][i], -self.vars[suc][i, j], self.vars[s][j]])
#                 self.body.append([
#                     -self.vars[suc][i, j], self.vars[leq][i, j], self.vars[s][j]
#                 ])
#                 self.body.append([
#                     -self.vars[suc][i, j], self.vars[leq][i, j], -self.vars[s][i]
#                 ])


# def example1(domain_size, fname="example1.cnf"):
#     problem = cnf_problem(domain_size=domain_size)
#     problem.fixed_leq("leq1")
#     problem.get_leq("leq2")
#     problem.get_succ(leq="leq2", var_name="suc")
#     problem.to_file(fname)

# def example2(domain_size, fname="example2.cnf"):
#     problem = cnf_problem(domain_size=domain_size)
#     problem.fixed_leq("leq1")
#     problem.get_leq("leq2")
#     problem.get_succ(leq="leq2", var_name="suc")
#     problem.mark_lower_successors(leq="leq1")
#     problem.to_file(fname)

# def example3(domain_size, fname="example3.cnf"):
#     problem = cnf_problem(domain_size=domain_size)
#     problem.fixed_leq("leq1")
#     problem.get_leq("leq2")
#     problem.get_succ(leq="leq2", var_name="suc")
#     problem.mark_continuous(leq="leq1")
#     problem.to_file(fname)

# def example4(domain_size, fname="example4.cnf"):
#     problem = cnf_problem(domain_size=domain_size)
#     problem.fixed_leq("leq1")
#     problem.get_leq("leq2")
#     problem.get_succ(leq="leq2", var_name="suc")
#     problem.a_b_problem(leq="leq1")
#     problem.to_file(fname)

# def example5(domain_size, fname="example5.cnf"):
#     problem = cnf_problem(domain_size=domain_size)
#     problem.fixed_leq("leq1")
#     problem.get_leq("leq2")
#     problem.get_succ(leq="leq2", var_name="suc")
#     problem.a_b_r_problem(leq="leq1")
#     problem.to_file(fname)

# def example_train(domain_size, fname="train.cnf"):
#     problem = cnf_problem(domain_size=domain_size)
#     problem.fixed_leq("leq1")
#     problem.get_leq("leq2")
#     problem.get_succ(leq="leq2", var_name="suc")
#     problem.train(leq="leq1", succ="suc")
#     problem.to_file(fname)

# def example_friends(domain_size, fname="friends.cnf"):
#     problem = cnf_problem(domain_size=domain_size)
#     problem.fixed_leq("leq1")
#     problem.get_leq("leq2")
#     problem.get_succ(leq="leq2", var_name="suc")
#     problem.friends(leq="leq1", succ="suc")
#     problem.to_file(fname)

# if __name__ == "__main__":
#     if len(argv) == 1 or "-h" in argv:
#         print("usage: examples.py [-h] -ds DOMAIN_SIZE -p {1, 2, 3, 4, 5} [-o OUT_FILE]")
#         print("")
#         print("Produces .cnf file for some problems")
#         print("")
#         print("\t-h show this message and exit")
#         print("\t-ds required, specify the domain size")
#         print("\t-p required, which problem to produce .cnf of")
#         print("\t-o optional, specify the name of the output file")
#         exit(0)
#     if "-ds" in argv:
#         domain_size = int(argv[argv.index("-ds") + 1])
#     else:
#         print("Missing domain size!")
#         exit(1)
#     if "-o" in argv:
#         fname = argv[argv.index("-o") + 1]
#     else:
#         fname = None
#     if "-p" in argv:
#         switch = int(argv[argv.index("-p") + 1])
#         if switch == 1:
#             produce = example1
#         if switch == 2:
#             produce = example2
#         if switch == 3:
#             produce = example3
#         if switch == 4:
#             produce = example4
#         if switch == 5:
#             produce = example5
#         if switch == 6:
#             produce = example_train
#         if switch == 7:
#             produce = example_friends
#     else:
#         print("Missing problem specification!")
#         exit(2)

#     if fname is None:
#         produce(domain_size)
#     else:
#         produce(domain_size, fname)
