import argparse
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
HEAD_MIDDLE_TAIL = r"""
\forall X: (\forall Y: (T(X) & LEQ(X, Y) -> T(Y))) &
\forall X: (\forall Y: (H(Y) & LEQ(X, Y) -> H(X))) &
\forall X: (~T(X) | ~T(Y))
""".strip()


EXPERIMENTS_DIR = Path(__file__).absolute().parent.parent.parent  # experiments
RESULTS_DIR = EXPERIMENTS_DIR.joinpath("results") # experiments/results
SEQ_MODELS_DIR = EXPERIMENTS_DIR.joinpath("models").joinpath("seq") # experiments/models/seq


def parse_args():
    parser = argparse.ArgumentParser(
        description='Generate input files for "seqeunce" experiments.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--dom_size', "-n", required=True, type=int)
    parser.add_argument("--cnf", "-cnf", action="store_true", help="Generate .CNF files")
    parser.add_argument("--wfomcs", "-wfomcs", action="store_true", help="Generate .WFOMCS files")
    parser.add_argument("--count", "-count", action="store_true", help="Compute WFOMC for 1,2,3,...,n")


    parser.add_argument("--head_tail", "-ht", action="store_true", help="Generate files for HEAD-TAIL sentence")
    parser.add_argument("--head_middle_tail", "-hmt", action="store_true", help="Generate files for HEAD-MIDDLE-TAIL sentence")
    parser.add_argument("--combinatorics", "-books", action="store_true", help="Generate files for ENG-MATH-BOOKS (combinatorics id=7) sentence")
    
    args = parser.parse_args()
    return args


def write_wfomcs(path, sentence, n):
    with open(path.joinpath(f"{n}.wfomcs"), "w") as fw:
        fw.write(sentence)
        fw.write("\n\n")
        fw.write(f"domain = {n}\n")


def generate_head_tail(n):
    nvars = n * (n + 1)
    clauses = []

    leq_id = lambda i, j: n*i + j

    for i in range(1, n + 1):
        for j in range(1, i):
            clauses.append([-leq_id(i, j)])
        for j in range(i, n + 1):
            leq_i_j = n*i + j
            clauses.append([leq_id(i, j)])

    for i in range(1, n + 1):
        for j in range(1, n + 1):
            clauses.append([-i, j, -leq_id(i, j)])

    with open(SEQ_MODELS_DIR.joinpath("head_tail").joinpath("cnf").joinpath(f'{n}_e1.cnf'), 'w') as fw:
        fw.write(f"p cnf {nvars} {len(clauses)}\n")
        for cl in clauses:
            for x in cl:
                fw.write(f"{x} ")
            fw.write("0\n")


def generate_head_middle_tail(n):
    def next_id():
        for i in range(1, n**2 + 2*n + 100):
            yield i

    ids = next_id()

    heads = [next(ids) for i in range(n)]
    tails = [next(ids) for i in range(n)]
    leq = [[next(ids) for j in range(n)] for i in range(n)]

    clauses = []
    for i in range(n):
        for j in range(i):
            clauses.append([-leq[i][j]])
        for j in range(i, n):
            clauses.append([leq[i][j]])

    for i in range(n):
        clauses.append([-heads[i], -tails[i]])

        for j in range(n):
            clauses.append([-heads[i], heads[j], -leq[j][i]])
            clauses.append([-tails[i], tails[j], -leq[i][j]])

    nvars = n * (n + 2)

    with open(SEQ_MODELS_DIR.joinpath("head_middle_tail").joinpath("cnf").joinpath(f'{n}_e1.cnf'), 'w') as fw:
        fw.write(f"p cnf {nvars} {len(clauses)}\n")
        for cl in clauses:
            for x in cl:
                fw.write(f"{x} ")
            fw.write("0\n")


def generate_combinatorics_books(n):
    raise Exception("Use Cofola to generate these files")


def run(input, domain_sizes, out_file="seq.csv"):
    OUTPUT_PATH = os.path.join(RESULTS_DIR, out_file)
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
    args = parse_args()

    if args.count:
        if args.head_tail:
            run(HEAD_TAIL, 100, "seq_head_tail.csv")
        
        if args.head_middle_tail:
            run(HEAD_MIDDLE_TAIL, 100, "seq_hmt_orders.csv")

        if args.combinatorics:
            raise Exception("Use Cofola to generate these files")

    if args.cnf:
        if args.head_tail:
            generate_head_tail(args.dom_size)

        if args.head_middle_tail:
            generate_head_middle_tail(args.dom_size)
        
        if args.combinatorics:
            generate_combinatorics_books(args.dom_size)

    if args.wfomcs:
        if args.head_tail:
            write_wfomcs(SEQ_MODELS_DIR.joinpath("head_tail").joinpath("wfomcs"), HEAD_TAIL, args.dom_size)

        if args.head_middle_tail:
            write_wfomcs(SEQ_MODELS_DIR.joinpath("head_middle_tail").joinpath("wfomcs"), HEAD_MIDDLE_TAIL, args.dom_size)

        if args.combinatorics:
            raise Exception("Use Cofola to generate these files")
