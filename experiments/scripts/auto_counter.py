import argparse
import datetime
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
    parser.add_argument("--walk", "-w", type=str, required=False, help="folder to walk for .wfomcs files", default=None)
    parser.add_argument('--input', '-i', type=str, required=False, help='sentence file', default=None)

    parser.add_argument("-d4", "--d4", action='store_true', help="Problems will be computed with d4")
    parser.add_argument("--ganak", "-ganak", action="store_true", help="Problems will be computed with ganak")
    parser.add_argument("--incremental", "-inc", action="store_true", help="Problems will be copmuted with incremental wfomc")
    parser.add_argument("--recursive", "-rec", action="store_true", help="Problems will be copmuted with recursive wfomc")

    parser.add_argument('--evidenceencode', '-ee', type=int, required=False, help='evidence encode method 1-CCS 2-PC; default=1',default=1)
    parser.add_argument('--label', '-l', type=str, required=False, help='algorithm label to be used in output CSV', default=None)
    parser.add_argument('--output_file', '-o', type=str, required=False, default="results.csv", help='filename of the resulting CSV')

    args = parser.parse_args()
    return args


def run_wfomc(infile, uee, algo=Algo.INCREMENTAL):
    problem = parse_input(infile)
        
    with Timer() as t:
        val = compute_wfomc(problem, algo, uee)

    return val, t.elapsed


def process_single_problem(args, out_path, file, fn, uee, label):
    print(f"PROCESSING: {file}")
    print(datetime.datetime.now())

    if args.incremental:
        val, time = run_wfomc(file, uee, Algo.INCREMENTAL)
        with open(out_path, "a") as fw:
            fw.write(f'{fn},{label},{time},"{val}"\n')

    if args.recursive:
        val, time = run_wfomc(file, uee, Algo.RECURSIVE)

        with open(out_path, "a") as fw:
            fw.write(f'{fn},recursive,{time},"{val}"\n')
    
    if args.d4 or args.ganak:
        run(["uv", "run", str(FO2CNF_PATH.absolute()), "-i", file, "-e", "1"])

    if args.d4:
        with Timer() as t:
            out = run([str(D4_PATH.absolute()), "tmp/" + fn + ".cnf"] + D4_ARGS, capture_output=True)

        with open(out_path, "a") as fw:
            val = out.stdout.decode().split('\n')[-2].rstrip().split()[-1]
            fw.write(f'{fn},d4,{t.elapsed},"{val}"')
            fw.write("\n")
        
    if args.ganak:
        with Timer() as t:
            val = out.stdout.decode().split('\n')[-2].rstrip().split()[-1]
            out = run([str(GANAK_PATH.absolute()), f"tmp/{fn}.cnf"] + GANAK_ARGS, capture_output=True)

        with open(out_path, "a") as fw:
            fw.write(f'{fn},ganak,{t.elapsed},"{val}"')
            fw.write("\n")

    print("========================")



if __name__ == "__main__":
    logzero.loglevel(logzero.WARN)

    args = parse_args()
    print(args)

    if args.walk is None and args.input is None:
        print("Please select an input [-w <path>, -i <path>]; if both specified -w takes precedence")
        exit(1)

    if args.d4 is False and args.ganak is False and args.incremental is False and args.recursive is False:
        print("Please select at least one solver from [-d4, -ganak, -inc, -rec]")
        exit(1)


    out_path = OUTPUT_DIR.joinpath(args.output_file)
    uee = UnaryEvidenceEncoding.PC if args.evidenceencode == 2 else UnaryEvidenceEncoding.CCS
    inc_ver = args.label if args.label is not None else "inc"

    if not os.path.exists(out_path):
        with open(out_path, "w") as fw:
            fw.write("problem,algo,time,wfomc\n")
    else:
        print(f"Using {out_path} folder, check contents")


    if args.d4 or args.ganak:
        if os.path.isdir("tmp"):
            print("Temporary directory tmp in use, cannot proceed")
            exit(1)
        os.mkdir("tmp")

    if args.walk is not None:
        filepaths = [os.path.join(args.walk, f) for f in sorted(os.listdir(args.walk)) if (os.path.isfile(os.path.join(args.walk, f)) and (f[-7:] == ".wfomcs" or f[-4:] == ".mln"))]
        filenames = [os.path.splitext(f)[0] for f in sorted(os.listdir(args.walk)) if (os.path.isfile(os.path.join(args.walk, f)) and (f[-7:] == ".wfomcs" or f[-4:] == '.mln'))]
        for file, fn in zip(filepaths, filenames):
            process_single_problem(args, out_path, file, fn, uee, inc_ver)
    elif args.input is not None:
        fn = os.path.splitext(os.path.basename(args.input))[0]
        process_single_problem(args, out_path, args.input, fn, uee, inc_ver)

    if args.d4 or args.ganak:
        if os.path.isdir("tmp"):
            shutil.rmtree("tmp")
