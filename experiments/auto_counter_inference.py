from subprocess import run, TimeoutExpired, CalledProcessError
from contexttimer import Timer
import argparse
import os
import shutil

timeout = 3600
domain_size = 3

def parse_args():
    parser = argparse.ArgumentParser(
        description='Count with WFOMC, d4, or ganak',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--walk", "-w", type=str, required=False, help="folder to walk for .wfomcs files", default=None)
    parser.add_argument('--input', '-i', type=str, required=False, help='single .wfomcs file, NOT IMPLEMENTED YET!', default=None)
    parser.add_argument("--generator", "-g", type=str, required=False, help="path to .py generator file that creates .wfomcs file and takes a single argument - the size of the domain, NOT IMPLEMENTED YET!")

    parser.add_argument("-d4", "--d4", action='store_true', help="problems will be copmuted with d4")
    parser.add_argument("--ganak", "-ganak", action="store_true", help="problems will be computed with ganak")
    parser.add_argument("--incremental", "-inc", action="store_true", help="problems will be copmuted with incremental wfomc")
    #parser.add_argument("-wfomcs_solver", type=str, required=False)
    #parser.add_argument("-cnf_solver", type=str, required=False)
    
    #parser.add_argument('--input', '-i', type=str, required=True, help='sentence file')
    #parser.add_argument('--linearencode', '-e', type=int, required=False, help='linear order and predcessor encode method 0-disable 1-hard encode 2-TODO first order encode',default=0 )
    args = parser.parse_args()
    return args

D4_PATH = "./d4-main/d4"
D4_ARGS = ["-mc"]

GANAK_PATH = "./ganak/ganak"
GANAK_ARGS = []

INCREMENTAL_PATH = "inc2_code/WFOMC/wfomc/solver.py"
INCREMENTAL_ARGS = ["-a", "incremental"]

FO2CNF_PATH = "inc2_code/PYSDD/fo2ex2cnf/fo2ex2cnf.py"

TIMEOUT = 3600
#MAX_DOMAIN_SIZE = 500

"""
while True:
    run(["python3.10", "more_efficient_stable_roommates.py", \
        f"{domain_size}", "3"])
    with Timer() as t:
        try:
            run(["uv", "run", "wfomc", \
                "-i", "stable_roommates_eff.wfomcs"], timeout=timeout, check=True)
        except TimeoutExpired:
            break
        with open(f"stable_roommates_wfomc_3.txt", "a") as f:
            f.write(f"{t.elapsed} \n")
        
        print(f"Problem 1 for domain size {domain_size} solved in {t.elapsed} s")
        domain_size += 3
        if domain_size >= 500:
            break
"""
if __name__ == "__main__":
    args = parse_args()
    print(args)
    if args.d4 is False and args.ganak is False and args.incremental is False:
        print("Please select at least one solver from [-d4, -ganak, -inc]")
        exit(1)

    if args.walk is None and args.input is None and args.generator is None:
        print("Please select at least one method of input from [-i, -w, -g]")
        exit(1)

    if args.d4 or args.ganak:
        if os.path.isdir("tmp"):
                print("Temporary directory tmp in use, cannot proceed")
                exit(1)
        os.mkdir("tmp")

    if os.path.isdir("results"):
        print("Using results folder, check contents")
    else:
        os.mkdir("results")

    if args.walk is not None:

        wfomcs = [os.path.join(args.walk, f) for f in os.listdir(args.walk) if (os.path.isfile(os.path.join(args.walk, f)) and f[-7:] == ".wfomcs")]
        filenames = [f for f in os.listdir(args.walk) if (os.path.isfile(os.path.join(args.walk, f)) and f[-7:] == ".wfomcs")]
        print(wfomcs)

        for file, fn in zip(wfomcs, filenames):
            if args.incremental:
                #run incremental
                with Timer() as t:
                    out = run(["python3", INCREMENTAL_PATH, "-i", file] + INCREMENTAL_ARGS,
                            capture_output=True)
                    with open("results/" + fn[:-7] + "_time_wfomc.txt", "a") as f:
                        f.write(f"{t.elapsed} \n")
                    with open("results/" + fn[:-7] + "_val_wfomc.txt", "a") as f:
                        to_print = out.stderr.decode().split("\n")[-4].rstrip().split()[-1]
                        f.write(f"{to_print} \n")
            if args.d4 or args.ganak:
                run(["python3", FO2CNF_PATH,
                    "-i", file, "-e", "3"])
        
            if args.d4:
                #run d4
                with Timer() as t:
                    out = run([D4_PATH, "tmp/" + fn[:-7] + ".cnf"] + D4_ARGS, capture_output=True)
                    with open("results/" + fn[:-7] + "_time_d4.txt", "a") as f:
                        f.write(f"{t.elapsed} \n")
                    with open("results/" + fn[:-7] + "_val_d4.txt", "a") as f:
                        to_print = out.stdout.decode().split("\n")[-2].rstrip().split()[-1]
                        f.write(f"{to_print} \n")
            if args.ganak:
                with Timer() as t:
                    out = run([GANAK_PATH, f"tmp/{fn[:-7]}.cnf"] + GANAK_ARGS, capture_output=True)
                    with open("results/" + fn[:-7] + "_time_ganak.txt", "a") as f:
                        f.write(f"{t.elapsed} \n")
                    with open("results/" + fn[:-7] + "_val_ganak.txt", "a") as f:
                        print(out.stdout.decode())
                        to_print = out.stdout.decode().split("\n")[-3].rstrip().split()[-1]
                        f.write(f"{to_print} \n")
    if args.input is not None:
        if args.incremental:
            #run incremental
            pass
        if args.d4 or args.ganak:
            run(["python3", FO2CNF_PATH,
                "-i", args.input, "-e", "3"])
        if args.d4:
            #run d4
            pass
        if args.ganak:
            #run ganak
            pass

    if args.generator is not None:
        pass
    if args.d4 or args.ganak:
        if os.path.isdir("tmp"):
            shutil.rmtree("tmp")