#!/bin/bash

# pwd == {{wfomc-over-ordered-domains}}/experiments/scripts
# cd experiments/scripts
uv sync



## =============================
##        INCREMENTAL
## =============================


# sequences
uv run auto_counter.py -w ../models/seq/head_tail -inc -o seq_ht_results.csv
uv run auto_counter.py -w ../models/seq/head_tail_pysdd -d4 -ganak -o seq_ht_results.csv
uv run auto_counter.py -w ../models/seq/head_middle_tail -inc -o seq_hmt_results.csv


# combinatorics
uv run auto_counter.py -w ../models/comb/new_encode -inc -l inc2 -ee 2 -o comb_results.csv
uv run auto_counter.py -w ../models/comb/pysdd -ganak -d4 -ee 1 -o comb_results.csv

uv run auto_counter.py -w ../models/comb/old_encode -inc -ee 2 -o comb_results.csv
uv run auto_counter.py -w ../models/comb/old_encode -rec -ee 1 -o comb_results.csv


# combinatorics scaling
# TODO


# MLNs
uv run auto_counter.py -w ../models/weather -inc -l inc2 -o mln_results.csv
uv run auto_counter.py -w ../models/weather2/new_encode -inc -l inc2 -o mln_results.csv
uv run auto_counter.py -w ../models/weather2/old_encode -inc -rec -o mln_results.csv


# Watts-Strogatz
uv run auto_counter.py -w ../models/ws/new_encode -inc -l inc2 -o ws_results.csv
uv run auto_counter.py -w ../models/ws/old_encode -inc -rec -o ws_results.csv
# TODO ... all cnf are UNSAT ??
# uv run auto_counter.py -w ../models/ws/old_encode -ganak -d4 -o ws_results.csv
# uv run fo2ex2cnf.py -i ../models/ws/old_encode/z8_1.wfomcs



## =============================
##        LO + Successor
## =============================
# TODO
