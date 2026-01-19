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
            echo "Timeout on $fn"
            break
        fi

    done
}


## =============================
##        INCREMENTAL (LO)
## =============================



# sequences
# HEAD & TAIL
loop_with_timeout "uv run auto_counter.py -inc -o seq_ht_results_new.csv" $(ls -v ../models/seq/head_tail/wfomcs/*.wfomcs)



# combinatorics
loop_with_timeout "uv run auto_counter.py -inc -l inc2 -ee 2 -o comb_new_results.csv" $(ls -v ../models/comb/new_encode/*.wfomcs)
loop_with_timeout "uv run auto_counter.py -inc -ee 2 -o comb_new_results.csv" $(ls -v ../models/comb/old_encode/*.wfomcs)
loop_with_timeout "uv run auto_counter.py -rec -o comb_new_results.csv" $(ls -v ../models/comb/old_encode/*.wfomcs)



# MLNs
loop_with_timeout "uv run auto_counter.py -inc -l inc2 -o mln_new_results.csv" $(ls -v ../models/weather/*.mln)
loop_with_timeout "uv run auto_counter.py -inc -l -inc2 -o mln_new_results.csv" $(ls -v ../models/weather2/new_encode/*.mln)
loop_with_timeout "uv run auto_counter.py -inc -o mln_new_results.csv" $(ls -v ../models/weather2/old_encode/*.mln)
loop_with_timeout "uv run auto_counter.py -rec -o mln_new_results.csv" $(ls -v ../models/weather2/old_encode/*.mln)



# # Watts-Strogatz
loop_with_timeout "uv run auto_counter.py -inc -l inc2 -o ws_new_results.csv" $(ls -v ../models/ws/new_encode/*.wfomcs)
loop_with_timeout "uv run auto_counter.py -rec -o ws_new_results.csv" $(ls -v ../models/ws/old_encode/*.wfomcs)
loop_with_timeout "uv run auto_counter.py -inc -o ws_new_results.csv" $(ls -v ../models/ws/old_encode/*.wfomcs)
