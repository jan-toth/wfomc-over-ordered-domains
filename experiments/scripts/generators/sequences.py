import os
from pathlib import Path

from contexttimer import Timer
import logzero

from wfomc.parser.fol_parser import parse as parse_fol
from wfomc.fol.sc2 import to_sc2
from wfomc.fol.syntax import Const
from wfomc.problems import WFOMCProblem
from wfomc.algo import incremental_wfomc
from wfomc.context import WFOMCContext


HEAD_TAIL = r"\forall X: (\forall Y: (T(X) & LEQ(X, Y) -> T(Y)))"
TOPOLOGICAL_ORDERS = r"""\forall X: (\forall Y: (E(X, Y) -> LEQ(X, Y)))"""


SCRIPT_PATH = Path(__file__).absolute()
OUTPUT_DIR = SCRIPT_PATH.parent.parent.joinpath("results")  # experiments/results


def run(input, domain_sizes, out_file="seq.csv"):
    OUTPUT_PATH = os.path.join(OUTPUT_DIR, out_file)
    if not os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, "w") as fw:
            fw.write("domain,time,wfomc\n")

    phi = to_sc2(parse_fol(input))

    if isinstance(domain_sizes, int):
        domain_sizes = [i for i in range(1, domain_sizes + 1)]

    for n in domain_sizes:
        dom = set(Const(f"{j}") for j in range(n))
        problem = WFOMCProblem(phi, dom, {})

        ctx = WFOMCContext(problem)
        with Timer() as t:
            res = incremental_wfomc(ctx)
            res = ctx.decode_result(res)

        with open(OUTPUT_PATH, "a") as fw:
            fw.write(f"{n},{t.elapsed},{res}\n")


if __name__ == "__main__":
    logzero.loglevel(logzero.WARN)

    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    run(HEAD_TAIL, 100, "seq_head_tail.csv")
    run(TOPOLOGICAL_ORDERS, 100, "seq_top_orders.csv")
