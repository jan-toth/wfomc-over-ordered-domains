import argparse
import datetime
import os
from pathlib import Path
import shutil
from subprocess import run

from contexttimer import Timer
import logzero
from natsort import natsorted

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

    parser.add_argument("-cnf", "--generate_cnf", action='store_true', help="Convert .wfomcs files to .cnf for [-d4, -ganak]")

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


def run_wmc(command, index):
    with Timer() as t:
        out = run(command, capture_output=True)

    val = out.stdout.decode().split('\n')[-index].rstrip().split()[-1]
    return val, t.elapsed


def run_d4(infile_cnf):
    return run_wmc([str(D4_PATH.absolute()), infile_cnf] + D4_ARGS, 2)


def run_ganak(infile_cnf):
    return run_wmc([str(GANAK_PATH.absolute()), infile_cnf] + GANAK_ARGS, 3)


def process_wfomc_problem(args, out_path, file, fn, uee, inc_label):
    print(f"PROCESSING: {file}")
    print(datetime.datetime.now())

    if args.incremental:
        val, time = run_wfomc(file, uee, Algo.INCREMENTAL)
        with open(out_path, "a") as fw:
            fw.write(f'{fn},{inc_label},{time},"{val}"\n')

    if args.recursive:
        val, time = run_wfomc(file, uee, Algo.RECURSIVE)
        with open(out_path, "a") as fw:
            fw.write(f'{fn},rec,{time},"{val}"\n')

    print("========================")


def process_wmc_problem(args, out_path, file, fn):
    print(f"PROCESSING: {file}")
    print(datetime.datetime.now())

    if args.d4:
        val, time = run_d4(file)
        with open(out_path, "a") as fw:
            fw.write(f'{fn},d4,{time},"{val}"')
            fw.write("\n")
        
    if args.ganak:
        val, time = run_ganak(file)
        with open(out_path, "a") as fw:
            fw.write(f'{fn},ganak,{time},"{val}"')
            fw.write("\n")

    print("========================")



if __name__ == "__main__":
    logzero.loglevel(logzero.WARN)

    args = parse_args()
    print(args)

    if args.walk is None:
        if args.input is None:
            print("Please select an input [-w <path>, -i <path>]; if both specified -w takes precedence")
            exit(1)
    elif args.input is not None:
        print("Both --walk and --input specified. Considering ONLY --walk.")

    if args.d4 is False and args.ganak is False and args.incremental is False and args.recursive is False:
        print("Please select at least one solver from [-d4, -ganak, -inc, -rec]")
        exit(1)


    if args.walk is not None:
        input_dir = Path(args.walk)

        files = [str(input_dir.joinpath(f)) for f in natsorted(os.listdir(input_dir)) if (os.path.isfile(input_dir.joinpath(f)))]

        filter_paths = lambda xs, ext: [f for f in xs if os.path.splitext(f)[1] == ext]

        wfomcs_paths = filter_paths(files, ".wfomcs")
        mln_paths = filter_paths(files, ".mln")
        cnf_paths = filter_paths(files, ".cnf")

    else:  # "--walk" switch takes precedence
        p = Path(args.input)

        input_dir = p.parent

        wfomcs_paths = []
        mln_paths = []
        cnf_paths = []

        if os.path.splitext(p)[1] == ".wfomcs":
            wfomcs_paths.append(str(p))
        elif os.path.splitext(p)[1] == ".mln":
            mln_paths.append(str(p))
        elif os.path.splitext(p)[1] == ".cnf":
            cnf_paths.append(str(p))

    filter_names = lambda xs: [os.path.splitext(f)[0] for f in xs]
    wfomcs_names = filter_names(wfomcs_paths)
    mln_names = filter_names(mln_paths)
    cnf_names = filter_names(cnf_paths)


    if (args.d4 is not False or args.ganak is not False) and args.generate_cnf:
        # Convert .wfomcs to .cnf
        for file, fn in zip(wfomcs_paths, wfomcs_names):
            run(["uv", "run", str(FO2CNF_PATH.absolute()), "-i", file, "-e", "3", "-o", f"{fn}.cnf"])


    out_path = OUTPUT_DIR.joinpath(args.output_file)
    uee = UnaryEvidenceEncoding.PC if args.evidenceencode == 2 else UnaryEvidenceEncoding.CCS
    inc_label = args.label if args.label is not None else "inc"

    if not os.path.exists(out_path):
        with open(out_path, "w") as fw:
            fw.write("problem,algo,time,wfomc\n")

    get_problem_name = lambda fn: os.path.split(fn)[1]

    for file, fn in zip(wfomcs_paths, wfomcs_names):
        fn = get_problem_name(fn)
        process_wfomc_problem(args, out_path, file, fn, uee, inc_label)

    for file, fn in zip(mln_paths, mln_names):
        fn = get_problem_name(fn)
        process_wfomc_problem(args, out_path, file, fn, uee, inc_label)

    for file, fn in zip(cnf_paths, cnf_names):
        fn = get_problem_name(fn)
        process_wmc_problem(args, out_path, file, fn)
