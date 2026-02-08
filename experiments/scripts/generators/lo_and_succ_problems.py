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
        for n in range(1, 21):
            gen.phi_cards(n)
            gen.phi_p1(n)
            gen.phi_p2(n)
            gen.phi_p4(n)
            gen.phi_p5(n)
    else:
        for n in range(20,101,5):
            gen.phi_cards(n)
            gen.phi_p1(n)
            gen.phi_p2(n)
