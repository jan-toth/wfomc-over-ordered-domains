#!/bin/bash

## =============================
##            SETUP
## =============================
## pwd == {{wfomc-over-ordered-domains}}
## cd experiments/scripts
## mkdir ../results
## bash commands.sh

uv sync


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

# =============================
#        INCREMENTAL (LO)
# =============================


# ================
# SIMPLE EXAMPLES

# Head & Tail
loop_with_timeout "uv run auto_counter.py -inc -o ht.csv" $(ls -v ../models/seq/head_tail/wfomcs/*.wfomcs)
loop_with_timeout "uv run auto_counter.py -ganak -o ht.csv" $(ls -v ../models/seq/head_tail/cnf/*.cnf)
loop_with_timeout "uv run auto_counter.py -d4 -o ht.csv" $(ls -v ../models/seq/head_tail/cnf/*.cnf)

# English & Math Books
# loop_with_timeout "uv run auto_counter.py -inc -l inc2 -o books.csv" $(ls -v ../models/seq/eng_math/new_encode/*.wfomcs)
# loop_with_timeout "uv run auto_counter.py -inc -o books.csv" $(ls -v ../models/seq/eng_math/old_encode/*.wfomcs)
# loop_with_timeout "uv run auto_counter.py -rec  -o books.csv" $(ls -v ../models/seq/eng_math/old_encode/*.wfomcs)
# loop_with_timeout "uv run auto_counter.py -ganak -o books.csv" $(ls -v ../models/seq/eng_math/cnf/*.cnf)
# loop_with_timeout "uv run auto_counter.py -d4 -o books.csv" $(ls -v ../models/seq/eng_math/cnf/*.cnf)




## ================
# COMBINATORICS

# Original MATH problems
loop_with_timeout_without_break "uv run auto_counter.py -inc -l inc2 -o math_x1.csv" $(ls -v ../models/comb/original/new_encode/*.wfomcs)
loop_with_timeout_without_break "uv run auto_counter.py -inc -o math_x1.csv" $(ls -v ../models/comb/original/old_encode/*.wfomcs)
loop_with_timeout_without_break "uv run auto_counter.py -rec -o math_x1.csv" $(ls -v ../models/comb/original/old_encode/*.wfomcs)
loop_with_timeout_without_break "uv run auto_counter.py -ganak -o math_x1.csv" $(ls -v ../models/comb/original/cnf/*.cnf)
loop_with_timeout_without_break "uv run auto_counter.py -d4 -o math_x1.csv" $(ls -v ../models/comb/original/cnf/*.cnf)

# Twice the domain
loop_with_timeout_without_break "uv run auto_counter.py -inc -l inc2 -o math_x2.csv" $(ls -v ../models/comb/times_2/new_encode/*.wfomcs)
loop_with_timeout_without_break "uv run auto_counter.py -ganak -o math_x2.csv" $(ls -v ../models/comb/times_2/cnf/*.cnf)
loop_with_timeout_without_break "uv run auto_counter.py -d4 -o math_x2.csv" $(ls -v ../models/comb/times_2/cnf/*.cnf)

# Thrice the domain
loop_with_timeout_without_break "uv run auto_counter.py -inc -l inc2 -o math_x3.csv" $(ls -v ../models/comb/times_3/new_encode/*.wfomcs)
loop_with_timeout_without_break "uv run auto_counter.py -ganak -o math_x3.csv" $(ls -v ../models/comb/times_3/cnf/*.cnf)
loop_with_timeout_without_break "uv run auto_counter.py -d4 -o math_x3.csv" $(ls -v ../models/comb/times_3/cnf/*.cnf)



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

loop_with_timeout "uv run auto_counter.py -inc -l inc2 -o ws2.csv" $(ls -v ../models/ws2/new_encode/*.mln)
loop_with_timeout "uv run auto_counter.py -inc -o ws2.csv" $(ls -v ../models/ws2/old_encode/*.mln)
loop_with_timeout "uv run auto_counter.py -rec -o ws2.csv" $(ls -v ../models/ws2/old_encode/*.mln)
loop_with_timeout "uv run auto_counter.py -ganak -o ws2.csv" $(ls -v ../models/ws2/cnf/*.cnf)
loop_with_timeout "uv run auto_counter.py -d4 -o ws2.csv" $(ls -v ../models/ws2/cnf/*.cnf)





# =============================
#        INCREMENTAL (LO) + SUCCESSOR
# =============================
loop_with_timeout "uv run auto_counter.py -lops -o lops_cards.csv" $(ls -v ../models/lops/cards/wfomcs/*.wfomcs)
loop_with_timeout "uv run auto_counter.py -ganak -o lops_cards.csv" $(ls -v ../models/lops/cards/cnf/*.cnf)
loop_with_timeout "uv run auto_counter.py -d4 -o lops_cards.csv" $(ls -v ../models/lops/cards/cnf/*.cnf)

loop_with_timeout "uv run auto_counter.py -lops -o lops_1.csv" $(ls -v ../models/lops/p1/wfomcs/*.wfomcs)
loop_with_timeout "uv run auto_counter.py -ganak -o lops_1.csv" $(ls -v ../models/lops/p1/cnf/*.cnf)
loop_with_timeout "uv run auto_counter.py -d4 -o lops_1.csv" $(ls -v ../models/lops/p1/cnf/*.cnf)

loop_with_timeout "uv run auto_counter.py -lops -o lops_2.csv" $(ls -v ../models/lops/p2/wfomcs/*.wfomcs)
loop_with_timeout "uv run auto_counter.py -ganak -o lops_2.csv" $(ls -v ../models/lops/p2/cnf/*.cnf)
loop_with_timeout "uv run auto_counter.py -d4 -o lops_2.csv" $(ls -v ../models/lops/p2/cnf/*.cnf)

loop_with_timeout "uv run auto_counter.py -lops -o lops_4.csv" $(ls -v ../models/lops/p4/wfomcs/*.wfomcs)
loop_with_timeout "uv run auto_counter.py -ganak -o lops_4.csv" $(ls -v ../models/lops/p4/cnf/*.cnf)
loop_with_timeout "uv run auto_counter.py -d4 -o lops_4.csv" $(ls -v ../models/lops/p4/cnf/*.cnf)

loop_with_timeout "uv run auto_counter.py -lops -o lops_5.csv" $(ls -v ../models/lops/p5/wfomcs/*.wfomcs)
loop_with_timeout "uv run auto_counter.py -ganak -o lops_5.csv" $(ls -v ../models/lops/p5/cnf/*.cnf)
loop_with_timeout "uv run auto_counter.py -d4 -o lops_5.csv" $(ls -v ../models/lops/p5/cnf/*.cnf)
