#!/bin/bash

## =============================
##            SETUP
## =============================
# pwd == {{wfomc-over-ordered-domains}}
uv sync

# cd experiments/scripts
# mkdir ../results


loop_with_timeout() {
    cmd="$1"
    shift

    for fn in "$@"; do
        timeout 3h $cmd -i $fn

        if [ $? -eq 124 ]; then
            echo "Timeout!"
            break
        fi

    done
}


## =============================
##        INCREMENTAL (LO)
## =============================



# sequences
# HEAD & TAIL
loop_with_timeout "uv run auto_counter.py -inc -o seq_ht_results_new.csv" $(ls -v ../models/seq/head_tail/wfomcs/*)
loop_with_timeout "uv run auto_counter.py -ganak -o seq_ht_results_new.csv" $(ls -v ../models/seq/head_tail/cnf/*_e1.cnf)
loop_with_timeout "uv run auto_counter.py -d4 -o seq_ht_results_new.csv" $(ls -v ../models/seq/head_tail/cnf/*_e1.cnf)
loop_with_timeout "uv run auto_counter.py -ganak -o seq_ht_results_new.csv" $(ls -v ../models/seq/head_tail/cnf/*_e3.cnf)
loop_with_timeout "uv run auto_counter.py -d4 -o seq_ht_results_new.csv" $(ls -v ../models/seq/head_tail/cnf/*_e3.cnf)






## =============================
##        INCREMENTAL (LO)
## =============================



# sequences
# for fn in ../models/seq/head_tail/wfomcs/*
# do
#     timeout 3h uv run auto_counter.py -i $fn -inc -o seq_ht_results_new.csv
# done


# for fn in ../models/seq/head_tail/cnf/*_e1.cnf
# do
#     timeout 3h uv run auto_counter.py -i $fn -ganak -o seq_ht_results_new.csv
#     timeout 3h uv run auto_counter.py -i $fn -d4 -o seq_ht_results_new.csv
# done

# for fn in ../models/seq/head_tail/cnf/*_e3.cnf
# do
#     timeout 3h uv run auto_counter.py -i $fn -ganak -o seq_ht_results_new.csv
#     timeout 3h uv run auto_counter.py -i $fn -d4 -o seq_ht_results_new.csv
# done


# problems=(  "../models/seq/head_tail/cnf/1_e3.cnf"
#             "../models/seq/head_tail/cnf/5_e3.cnf"
#             "../models/seq/head_tail/cnf/10_e3.cnf"
#             "../models/seq/head_tail/cnf/15_e3.cnf"
#             "../models/seq/head_tail/cnf/20_e3.cnf"
#             "../models/seq/head_tail/cnf/25_e3.cnf"
#             "../models/seq/head_tail/cnf/30_e3.cnf"
#             # "../models/seq/head_tail/cnf/35_e3.cnf"
#             # "../models/seq/head_tail/cnf/40_e3.cnf"
#             # "../models/seq/head_tail/cnf/45_e3.cnf"
#             # "../models/seq/head_tail/cnf/50_e3.cnf"
# )
# for fn in "${problems[@]}"
# do
#     timeout 3h uv run auto_counter.py -i $fn -ganak -o seq_ht_results_new.csv
# done


# problems=(  "../models/seq/head_tail/cnf/1_e3.cnf"
#             "../models/seq/head_tail/cnf/5_e3.cnf"
#             "../models/seq/head_tail/cnf/10_e3.cnf"
#             "../models/seq/head_tail/cnf/15_e3.cnf"
#             "../models/seq/head_tail/cnf/20_e3.cnf"
#             "../models/seq/head_tail/cnf/25_e3.cnf"
# )
# for fn in "${problems[@]}"
# do
#     timeout 3h uv run auto_counter.py -i $fn -d4 -o seq_ht_results_new.csv
# done

# uv run auto_counter.py -w ../models/seq/head_tail -inc -o seq_ht_results.csv
# uv run auto_counter.py -w ../models/seq/head_tail/ -d4 -ganak -o seq_ht_results.csv

# uv run auto_counter.py -w ../models/seq/topological_orders -inc -o seq_to_results.csv
# uv run auto_counter.py -w ../models/seq/topological_orders/ -d4 -ganak -o seq_to_results.csv


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
# uv run auto_counter.py -w ../models/weather -inc -l inc2 -o mln_results.csv

# uv run auto_counter.py -w ../models/weather2/new_encode -inc -l inc2 -o mln_results.csv
# uv run auto_counter.py -w ../models/weather2/old_encode -rec -o mln_results.csv
# uv run auto_counter.py -i ../models/weather2/old_encode/kl4.mln -inc -o mln_results.csv
# uv run auto_counter.py -i ../models/weather2/old_encode/kl5.mln -inc -o mln_results.csv
# uv run auto_counter.py -i ../models/weather2/old_encode/kl6.mln -inc -o mln_results.csv
# uv run auto_counter.py -i ../models/weather2/old_encode/kl7.mln -inc -o mln_results.csv
# uv run auto_counter.py -i ../models/weather2/old_encode/kl8.mln -inc -o mln_results.csv
# uv run auto_counter.py -i ../models/weather2/old_encode/kl9.mln -inc -o mln_results.csv


# # Watts-Strogatz
# uv run auto_counter.py -w ../models/ws/new_encode -inc -l inc2 -o ws_results.csv
# uv run auto_counter.py -w ../models/ws/old_encode -rec -inc -o ws_results.csv
# uv run auto_counter.py -w ../models/ws/new_encode -ganak -d4 -o ws_results.csv




## =============================
##        LO + Successor
## =============================
# TODO
