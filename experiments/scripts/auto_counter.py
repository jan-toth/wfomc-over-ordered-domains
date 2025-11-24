import argparse
import os
from pathlib import Path
import shutil
from subprocess import run

from contexttimer import Timer
import logzero

from wfomc.algo import Algo
from wfomc.parser import parse_input
from wfomc.solver import wfomc as compute_wfomc
from wfomc.network import UnaryEvidenceEncoding


SCRIPT_PATH = Path(__file__).absolute()

OUTPUT_DIR = SCRIPT_PATH.parent.parent.joinpath("results")  # experiments/results

D4_PATH = SCRIPT_PATH.parent.parent.joinpath("d4").joinpath("d4")
D4_ARGS = ["-mc"]

GANAK_PATH = SCRIPT_PATH.parent.parent.joinpath("ganak").joinpath("ganak")
GANAK_ARGS = []

FO2CNF_PATH = SCRIPT_PATH.parent.joinpath("fo2ex2cnf.py")


def parse_args():
    parser = argparse.ArgumentParser(
        description='Count with WFOMC, d4, or ganak',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--walk", "-w", type=str, required=True, help="folder to walk for .wfomcs files", default=None)
    # parser.add_argument('--input', '-i', type=str, required=False, help='single .wfomcs file, NOT IMPLEMENTED YET!', default=None)
    # parser.add_argument("--generator", "-g", type=str, required=False, help="path to .py generator file that creates .wfomcs file and takes a single argument - the size of the domain, NOT IMPLEMENTED YET!")

    parser.add_argument("-d4", "--d4", action='store_true', help="Problems will be computed with d4")
    parser.add_argument("--ganak", "-ganak", action="store_true", help="Problems will be computed with ganak")
    parser.add_argument("--incremental", "-inc", action="store_true", help="Problems will be copmuted with incremental wfomc")
    parser.add_argument("--recursive", "-rec", action="store_true", help="Problems will be copmuted with recursive wfomc")
    #parser.add_argument("-wfomcs_solver", type=str, required=False)
    #parser.add_argument("-cnf_solver", type=str, required=False)
    
    #parser.add_argument('--input', '-i', type=str, required=True, help='sentence file')
    #parser.add_argument('--linearencode', '-e', type=int, required=False, help='linear order and predcessor encode method 0-disable 1-hard encode 2-TODO first order encode',default=0 )
    args = parser.parse_args()
    return args


def run_wfomc(infile, algo=Algo.INCREMENTAL):
    problem = parse_input(infile)
    
    # uee = UnaryEvidenceEncoding.PC if problem.unary_evidence is not None and algo == Algo.INCREMENTAL else UnaryEvidenceEncoding.CCS
    
    with Timer() as t:
        val = compute_wfomc(problem, algo, UnaryEvidenceEncoding.CCS)

    return val, t.elapsed


def process_wfomcs(args, out_path, wfomcs, filenames):
    for file, fn in zip(wfomcs, filenames):
        if args.incremental:
            val, time = run_wfomc(file, Algo.INCREMENTAL)

            with open(out_path, "a") as fw:
                fw.write(f"{fn[:-7]},incremental,{time},{val}\n")

        if args.recursive:
            val, time = run_wfomc(file, Algo.RECURSIVE)

            with open(out_path, "a") as fw:
                fw.write(f"{fn[:-7]},recursive,{time},{val}\n")
        
        if args.d4 or args.ganak:
            run(["uv", "run", str(FO2CNF_PATH.absolute()), "-i", file, "-e", "1"])

        if args.d4:
            with Timer() as t:
                out = run([str(D4_PATH.absolute()), "tmp/" + fn[:-7] + ".cnf"] + D4_ARGS, capture_output=True)

            with open(out_path, "a") as fw:
                val = out.stdout.decode().split('\n')[-2].rstrip().split()[-1]
                fw.write(f"{fn[:-7]},d4,{t.elapsed},{val}")
                fw.write("\n")
            
        if args.ganak:
            with Timer() as t:
                val = out.stdout.decode().split('\n')[-2].rstrip().split()[-1]
                out = run([str(GANAK_PATH.absolute()), f"tmp/{fn[:-7]}.cnf"] + GANAK_ARGS, capture_output=True)

            with open(out_path, "a") as fw:
                fw.write(f"{fn[:-7]},ganak,{t.elapsed},{val}")
                fw.write("\n")


def process_mlns(args, out_path, mlns, filenames):
    for file, fn in zip(mlns, filenames):
        if args.incremental:
            val, time = run_wfomc(file, Algo.INCREMENTAL)

            with open(out_path, "a") as fw:
                fw.write(f"{fn[:-4]},incremental,{time},{val}\n")

        if args.recursive:
            val, time = run_wfomc(file, Algo.RECURSIVE)

            with open(out_path, "a") as fw:
                fw.write(f"{fn[:-4]},recursive,{time},{val}\n")


def process_problems(args, out_file="results.csv"):
    out_path = OUTPUT_DIR.joinpath(out_file)

    if not os.path.exists(out_path):
        with open(out_path, "w") as fw:
            fw.write("problem,algo,time,wfomc\n")

    wfomcs = [os.path.join(args.walk, f) for f in os.listdir(args.walk) if (os.path.isfile(os.path.join(args.walk, f)) and f[-7:] == ".wfomcs")]
    filenames = [f for f in os.listdir(args.walk) if (os.path.isfile(os.path.join(args.walk, f)) and f[-7:] == ".wfomcs")]
    process_wfomcs(args, out_path, wfomcs, filenames)

    mlns = [os.path.join(args.walk, f) for f in os.listdir(args.walk) if (os.path.isfile(os.path.join(args.walk, f)) and f[-4:] == ".mln")]
    filenames = [f for f in os.listdir(args.walk) if (os.path.isfile(os.path.join(args.walk, f)) and f[-4:] == ".mln")]
    process_mlns(args, out_path, mlns, filenames)
    

if __name__ == "__main__":
    logzero.loglevel(logzero.WARN)

    args = parse_args()
    print(args)

    if args.d4 is False and args.ganak is False and args.incremental is False and args.recurive is False:
        print("Please select at least one solver from [-d4, -ganak, -inc, -rec]")
        exit(1)

    if args.d4 or args.ganak:
        if os.path.isdir("tmp"):
            print("Temporary directory tmp in use, cannot proceed")
            exit(1)
        os.mkdir("tmp")

    if os.path.isdir(OUTPUT_DIR):
        print("Using results folder, check contents")
    else:
        os.mkdir(OUTPUT_DIR)

    process_problems(args)

    if args.d4 or args.ganak:
        if os.path.isdir("tmp"):
            shutil.rmtree("tmp")
