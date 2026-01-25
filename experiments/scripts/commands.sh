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

loop_with_timeout_without_break() {
    cmd="$1"
    shift

    for fn in "$@"; do
        timeout 3h $cmd -i $fn

        if [ $? -eq 124 ]; then
            echo "Timeout on $fn"
        fi

    done
}


## =============================
##        INCREMENTAL (LO)
## =============================


## ================
# SIMPLE EXAMPLES

# Head & Tail
loop_with_timeout "uv run auto_counter.py -inc -o ht.csv" $(ls -v ../models/seq/head_tail/wfomcs/*.wfomcs)
loop_with_timeout "uv run auto_counter.py -ganak -o ht.csv" $(ls -v ../models/seq/head_tail/cnf/*.cnf)
loop_with_timeout "uv run auto_counter.py -d4 -o ht.csv" $(ls -v ../models/seq/head_tail/cnf/*.cnf)

# English & Math Books
loop_with_timeout "uv run auto_counter.py -inc -l inc2 -o books.csv" $(ls -v ../models/seq/eng_math/new_encode/*.wfomcs)
loop_with_timeout "uv run auto_counter.py -inc -o books.csv" $(ls -v ../models/seq/eng_math/old_encode/*.wfomcs)
loop_with_timeout "uv run auto_counter.py -rec  -o books.csv" $(ls -v ../models/seq/eng_math/old_encode/*.wfomcs)
loop_with_timeout "uv run auto_counter.py -ganak -o books.csv" $(ls -v ../models/seq/eng_math/cnf/*.cnf)
loop_with_timeout "uv run auto_counter.py -d4 -o books.csv" $(ls -v ../models/seq/eng_math/cnf/*.cnf)




## ================
# COMBINATORICS

# Original MATH problems
loop_with_timeout_without_break "uv run auto_counter.py -inc -l inc2 -o combinatorics.csv" $(ls -v ../models/comb/original/new_encode/*.wfomcs)
loop_with_timeout_without_break "uv run auto_counter.py -inc -o combinatorics.csv" $(ls -v ../models/comb/original/old_encode/*.wfomcs)
loop_with_timeout_without_break "uv run auto_counter.py -rec -o combinatorics.csv" $(ls -v ../models/comb/original/old_encode/*.wfomcs)
loop_with_timeout_without_break "uv run auto_counter.py -ganak -o combinatorics.csv" $(ls -v ../models/comb/original/cnf/*.cnf)
loop_with_timeout_without_break "uv run auto_counter.py -d4 -o combinatorics.csv" $(ls -v ../models/comb/original/cnf/*.cnf)

# Twice the domain
loop_with_timeout_without_break "uv run auto_counter.py -inc -l inc2 -o combinatorics.csv" $(ls -v ../models/comb/times_2/new_encode/*.wfomcs)
loop_with_timeout_without_break "uv run auto_counter.py -ganak -o combinatorics.csv" $(ls -v ../models/comb/times_2/cnf/*.cnf)
loop_with_timeout_without_break "uv run auto_counter.py -d4 -o combinatorics.csv" $(ls -v ../models/comb/times_2/cnf/*.cnf)




## ================
# HIDDEN MARKOV MODELS

# Standard HMMs
loop_with_timeout "uv run auto_counter.py -inc -l inc2 -o hmm.csv" $(ls -v ../models/weather2/new_encode/*.mln)
loop_with_timeout "uv run auto_counter.py -inc -o hmm.csv" $(ls -v ../models/weather2/old_encode/*.mln)
loop_with_timeout "uv run auto_counter.py -rec -o hmm.csv" $(ls -v ../models/weather2/old_encode/*.mln)
loop_with_timeout "uv run auto_counter.py -ganak -o hmm.csv" $(ls -v ../models/weather2/cnf/*.cnf)
loop_with_timeout "uv run auto_counter.py -d4 -o hmm.csv" $(ls -v ../models/weather2/cnf/*.cnf)


# Higher Order Dependecies
loop_with_timeout "uv run auto_counter.py -inc -l inc2 -o higher_hmm.csv" $(ls -v ../models/weather/new_encode/*.mln)
loop_with_timeout "uv run auto_counter.py -ganak -o higher_hmm.csv" $(ls -v ../models/weather/cnf/*.cnf)
loop_with_timeout "uv run auto_counter.py -d4 -o higher_hmm.csv" $(ls -v ../models/weather/cnf/*.cnf)




## ================
# WATTS-STROGATZ MODEL
loop_with_timeout "uv run auto_counter.py -inc -l inc2 -o ws.csv" $(ls -v ../models/ws/new_encode/*.wfomcs)
loop_with_timeout "uv run auto_counter.py -inc -o ws.csv" $(ls -v ../models/ws/old_encode/*.wfomcs)
loop_with_timeout "uv run auto_counter.py -rec -o ws.csv" $(ls -v ../models/ws/old_encode/*.wfomcs)
loop_with_timeout "uv run auto_counter.py -ganak -o ws.csv" $(ls -v ../models/ws/cnf/*.cnf)
loop_with_timeout "uv run auto_counter.py -d4 -o ws.csv" $(ls -v ../models/ws/cnf/*.cnf)
