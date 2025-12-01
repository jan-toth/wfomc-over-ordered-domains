#!/bin/bash

## =============================
##            SETUP
## =============================
# pwd == {{wfomc-over-ordered-domains}}
uv sync

# cd experiments/scripts
# mkdir ../results



## =============================
##        INCREMENTAL
## =============================


# sequences
uv run auto_counter.py -w ../models/seq/head_tail -inc -o seq_ht_results.csv
uv run auto_counter.py -i ../models/seq/head_tail/1.cnf -d4 -ganak -o seq_ht_results.csv
uv run auto_counter.py -i ../models/seq/head_tail/5.cnf -d4 -ganak -o seq_ht_results.csv
uv run auto_counter.py -i ../models/seq/head_tail/10.cnf -d4 -ganak -o seq_ht_results.csv
uv run auto_counter.py -i ../models/seq/head_tail/15.cnf -d4 -ganak -o seq_ht_results.csv
uv run auto_counter.py -i ../models/seq/head_tail/20.cnf -d4 -ganak -o seq_ht_results.csv

uv run auto_counter.py -w ../models/seq/head_middle_tail -inc -d4 -ganak -o seq_hmt_results.csv
uv run auto_counter.py -i ../models/seq/head_middle_tail/1.cnf -d4 -ganak -o seq_hmt_results.csv
uv run auto_counter.py -i ../models/seq/head_middle_tail/5.cnf -d4 -ganak -o seq_hmt_results.csv
uv run auto_counter.py -i ../models/seq/head_middle_tail/10.cnf -d4 -ganak -o seq_hmt_results.csv
uv run auto_counter.py -i ../models/seq/head_middle_tail/15.cnf -d4 -ganak -o seq_hmt_results.csv
uv run auto_counter.py -i ../models/seq/head_middle_tail/20.cnf -d4 -ganak -o seq_hmt_results.csv

# T OOOOOO D OOOOOOOOO
# # combinatorics
# uv run auto_counter.py -w ../models/comb/new_encode -inc -l inc2 -ee 2 -o comb_results.csv
# uv run auto_counter.py -w ../models/comb/cnf -ganak -d4 -ee 1 -o comb_results.csv

# # uv run auto_counter.py -w ../models/comb/old_encode -inc -ee 2 -o comb_results.csv
# # uv run auto_counter.py -w ../models/comb/old_encode -rec -ee 1 -o comb_results.csv

# # 30 second timeout ??
# uv run ./auto_counter.py -i ../models/comb/old_encode/243.wfomcs -inc -ee 2 -o comb_results.csv
# uv run auto_counter.py -i ../models/comb/old_encode/137.wfomcs -inc -ee 2 -o comb_results.csv


# # combinatorics scaling
# # TODO


# MLNs
uv run auto_counter.py -w ../models/weather -inc -l inc2 -o mln_results.csv
uv run auto_counter.py -w ../models/weather2/new_encode -inc -l inc2 -o mln_results.csv
uv run auto_counter.py -w ../models/weather2/old_encode -rec -o mln_results.csv
uv run auto_counter.py -i ../models/weather2/old_encode/kl4.mln -inc -o mln_results.csv
uv run auto_counter.py -i ../models/weather2/old_encode/kl5.mln -inc -o mln_results.csv
uv run auto_counter.py -i ../models/weather2/old_encode/kl6.mln -inc -o mln_results.csv
uv run auto_counter.py -i ../models/weather2/old_encode/kl7.mln -inc -o mln_results.csv
uv run auto_counter.py -i ../models/weather2/old_encode/kl8.mln -inc -o mln_results.csv
uv run auto_counter.py -i ../models/weather2/old_encode/kl9.mln -inc -o mln_results.csv


# Watts-Strogatz
uv run auto_counter.py -w ../models/ws/new_encode -inc -l inc2 -o ws_results.csv
uv run auto_counter.py -w ../models/ws/old_encode -rec -inc -o ws_results.csv

# TODO ... all cnf are UNSAT ??
# CIRCULAR_PRED ??
# uv run auto_counter.py -w ../models/ws/old_encode -ganak -d4 -o ws_results.csv
# uv run fo2ex2cnf.py -i ../models/ws/old_encode/z8_1.wfomcs



## =============================
##        LO + Successor
## =============================
# TODO
