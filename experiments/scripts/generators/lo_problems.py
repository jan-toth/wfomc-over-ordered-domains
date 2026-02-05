import math
from pathlib import Path


WS2_NEW = lambda n, w: fr"""\forall X: (~Wired(X,X)).
\forall X: (\forall Y: (~Wired(X,Y) | ~Wired(Y,X))).
\forall X: (\exists Y: (Wired(X,Y))).
\forall X: (\forall Y: (Edge(X,Y) <-> (Wired(X,Y) | Wired(Y,X)))).
{w} Wired(X,Y) & ~CIRCULAR_PRED(X,Y)
{-w} Wired(X,Y) & CIRCULAR_PRED(X,Y)

domain = {n}
|Wired| = {n}"""

WS2_OLD = lambda n, w: fr"""\forall X: (~Perm(X,X)).
\forall X: (\exists Y: (Perm(X, Y))).
\forall Y: (\exists X: (Perm(X, Y))).
\forall X: (\forall Y: (Pred(X,Y) -> Perm(X,Y))).
\forall X: (\forall Y: (Pred(X,Y) -> LEQ(X,Y))).
\forall X: (~Wired(X,X)).
\forall X: (\forall Y: (~Wired(X,Y) | ~Wired(Y,X))).
\forall X: (\exists Y: (Wired(X,Y))).
\forall X: (\forall Y: (Edge(X,Y) <-> (Wired(X,Y) | Wired(Y,X)))).
{w} Wired(X,Y) & ~Perm(X,Y)
{-w} Wired(X,Y) & Perm(X,Y)

domain = {n}
|Perm| = {n}
|Pred| = {n-1}
|Wired| = {n}"""


class GeneralizedLinearOrderProblems:

    def __init__(self):
        self.script_path = Path(__file__).absolute()
        self.output_dir = self.script_path.parent.parent.parent.joinpath("models")  # experiments/models

        self.ws2_dir = self.output_dir.joinpath("ws2")



    def watts_strogatz_true(self, domain_size, prob):
        w = round(0.5 * math.log(prob / (1 - prob)), 2)

        output_name = self.ws2_dir.joinpath("new_encode").joinpath(f"zt{domain_size}_p0{str(prob).split('.')[1]}.mln")
        with open(output_name, "w") as fw:
            fw.write(WS2_NEW(domain_size, w))
        
        # output_name = self.ws2_dir.joinpath("old_encode").joinpath(f"zt{domain_size}_p0{str(prob).split('.')[1]}.mln")
        # with open(output_name, "w") as fw:
        #     fw.write(WS2_OLD(domain_size, w))


if __name__ == "__main__":
    gen = GeneralizedLinearOrderProblems()

    prob = 0.3
    # for n in range(4,21,2):
    #     gen.watts_strogatz_true(n, prob)
    # gen.watts_strogatz_true(5, prob)
    for n in range(20, 101, 10):
        gen.watts_strogatz_true(n, prob)
