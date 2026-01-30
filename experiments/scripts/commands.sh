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
loop_with_timeout_without_break "uv run auto_counter.py -inc -l inc2 -o math.csv" $(ls -v ../models/comb/original/new_encode/*.wfomcs)
loop_with_timeout_without_break "uv run auto_counter.py -inc -o math.csv" $(ls -v ../models/comb/original/old_encode/*.wfomcs)
loop_with_timeout_without_break "uv run auto_counter.py -rec -o math.csv" $(ls -v ../models/comb/original/old_encode/*.wfomcs)
loop_with_timeout_without_break "uv run auto_counter.py -ganak -o math.csv" $(ls -v ../models/comb/original/cnf/*.cnf)
loop_with_timeout_without_break "uv run auto_counter.py -d4 -o math.csv" $(ls -v ../models/comb/original/cnf/*.cnf)

# Twice the domain
loop_with_timeout_without_break "uv run auto_counter.py -inc -l inc2 -o math_x2.csv" $(ls -v ../models/comb/times_2/new_encode/*.wfomcs)
loop_with_timeout_without_break "uv run auto_counter.py -ganak -o math_x2.csv" $(ls -v ../models/comb/times_2/cnf/*.cnf)
loop_with_timeout_without_break "uv run auto_counter.py -d4 -o math_x2.csv" $(ls -v ../models/comb/times_2/cnf/*.cnf)




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

# =============================
#        INCREMENTAL (LO) + SUCCESSOR
# =============================


# TODO


# =============================
#           FIGURES
# =============================

# mkdir ../results/figs

uv run auto_plotter.py bar ../results/math.csv -o ../results/figs/math_wfomc.png -a inc2 rec inc --sort-by inc2
uv run auto_plotter.py bar ../results/math.csv -o ../results/figs/math_wmc.png -a inc2 ganak d4 --sort-by inc2 --legend "upper left"
uv run auto_plotter.py bar ../results/math_x2.csv -o ../results/figs/math_wmc_x2.png -a inc2 ganak d4 --sort-by inc2
uv run auto_plotter.py bar ../results/math.csv -o ../results/figs/math.png -a inc2 ganak d4 rec inc --sort-by inc2 --legend "upper left"


uv run auto_plotter.py cactus ../results/math.csv -o ../results/figs/math_cactus.png -a inc2 ganak d4 rec inc
uv run auto_plotter.py cactus ../results/math_x2.csv -o ../results/figs/math_cactus_x2.png -a inc2 ganak d4 --legend "upper left"


uv run auto_plotter.py scale ../results/ht.csv -o ../results/figs/ht.png -a inc ganak d4 --prefix ht --max 15 --legend "upper left"
uv run auto_plotter.py scale ../results/ht.csv -o ../results/figs/ht_large.png -a inc --prefix ht --min 50 --xticks 100,1001,100 --legend "upper left"

uv run auto_plotter.py scale ../results/books.csv -o ../results/figs/books.png  -a inc2 ganak d4 rec inc --prefix b --legend "upper left"


uv run auto_plotter.py scale ../results/hmm.csv -o ../results/figs/hmm.png -a inc2 ganak d4 rec inc --prefix kl --max 20 --legend "upper left"
uv run auto_plotter.py scale ../results/hmm.csv -o ../results/figs/hmm_large.png -a inc2 --prefix kl --min 20 --legend "upper left" --xticks 20,90,10

uv run auto_plotter.py scale ../results/higher_hmm.csv -o ../results/figs/higher_hmm.png -a inc2 ganak d4 --prefix k --max 15 --legend "upper left"
uv run auto_plotter.py scale ../results/higher_hmm.csv -o ../results/figs/higher_hmm_large.png -a inc2 --prefix k --min 15 --legend "upper left" --xticks 15,55,5


uv run auto_plotter.py scale ../results/ws.csv -o ../results/figs/ws_z1.png -a inc2 ganak d4 rec inc --prefix z --suffix 1 --max 20
uv run auto_plotter.py scale ../results/ws.csv -o ../results/figs/ws_z2.png -a inc2 ganak d4 rec inc --prefix z --suffix 2 --max 20
uv run auto_plotter.py scale ../results/ws.csv -o ../results/figs/ws_z3.png -a inc2 ganak d4 rec inc --prefix z --suffix 3 --max 20
uv run auto_plotter.py scale ../results/ws.csv -o ../results/figs/ws_large_z1.png -a inc2  --prefix z --suffix 1 --min 20 --legend "upper left" --xticks 100,501,100
uv run auto_plotter.py scale ../results/ws.csv -o ../results/figs/ws_large_z2.png -a inc2 --prefix z --suffix 2 --min 20 --legend "upper left" --xticks 100,501,100
uv run auto_plotter.py scale ../results/ws.csv -o ../results/figs/ws_large_z3.png -a inc2 --prefix z --suffix 3 --min 20 --legend "upper left" --xticks 100,501,100
