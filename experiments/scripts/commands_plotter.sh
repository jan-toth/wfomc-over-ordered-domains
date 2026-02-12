#!/bin/bash

## =============================
##            SETUP
## =============================
## pwd == {{wfomc-over-ordered-domains}}
## cd experiments/scripts
## mkdir ../results/figs
## bash commands.sh

uv sync

# =============================
#           INCREMENTAL (LO)
# =============================

uv run auto_plotter.py bar ../results/math_x1.csv -o ../results/figs/math_bar_x1.pdf -a inc2 ganak d4 rec inc --sort-by inc2 --legend "best"
uv run auto_plotter.py bar ../results/math_x2.csv -o ../results/figs/math_bar_x2.pdf -a inc2 ganak d4 --sort-by inc2 --legend "best"
uv run auto_plotter.py bar ../results/math_x3.csv -o ../results/figs/math_bar_x3.pdf -a inc2 ganak d4 --sort-by inc2 --legend "best"

uv run auto_plotter.py cactus ../results/math_x1.csv -o ../results/figs/math_cactus_x1.pdf -a inc2 ganak d4 rec inc  --legend "best"
uv run auto_plotter.py cactus ../results/math_x2.csv -o ../results/figs/math_cactus_x2.pdf -a inc2 ganak d4 --legend "best"
uv run auto_plotter.py cactus ../results/math_x3.csv -o ../results/figs/math_cactus_x3.pdf -a inc2 ganak d4 --legend "best"


uv run auto_plotter.py scale ../results/ht.csv -o ../results/figs/ht.pdf -a inc ganak d4 --prefix ht --max 15 --legend "upper left"
uv run auto_plotter.py scale ../results/ht.csv -o ../results/figs/ht_large.pdf -a inc --prefix ht --min 50 --xticks 100,1001,100 --legend "upper left"


uv run auto_plotter.py scale ../results/hmm.csv -o ../results/figs/hmm.pdf -a inc2 ganak d4 rec inc --prefix kl --max 20 --legend "best"
uv run auto_plotter.py scale ../results/hmm.csv -o ../results/figs/hmm_large.pdf -a inc2 --prefix kl --min 20 --legend "upper left" --xticks 20,90,10

uv run auto_plotter.py scale ../results/higher_hmm.csv -o ../results/figs/higher_hmm.pdf -a inc2 ganak d4 --prefix k --max 15 --legend "best"
uv run auto_plotter.py scale ../results/higher_hmm.csv -o ../results/figs/higher_hmm_large.pdf -a inc2 --prefix k --min 15 --legend "upper left" --xticks 15,55,5


uv run auto_plotter.py scale ../results/ws.csv -o ../results/figs/ws_z1.pdf -a inc2 ganak d4 rec inc --prefix z --suffix 1 --max 20 --legend "upper left"
uv run auto_plotter.py scale ../results/ws.csv -o ../results/figs/ws_z2.pdf -a inc2 ganak d4 rec inc --prefix z --suffix 2 --max 20 --legend "upper left"
uv run auto_plotter.py scale ../results/ws.csv -o ../results/figs/ws_z3.pdf -a inc2 ganak d4 rec inc --prefix z --suffix 3 --max 20 --legend "upper left"
uv run auto_plotter.py scale ../results/ws.csv -o ../results/figs/ws_large_z1.pdf -a inc2  --prefix z --suffix 1 --min 20 --legend "upper left" --xticks 100,501,100
uv run auto_plotter.py scale ../results/ws.csv -o ../results/figs/ws_large_z2.pdf -a inc2 --prefix z --suffix 2 --min 20 --legend "upper left" --xticks 100,501,100
uv run auto_plotter.py scale ../results/ws.csv -o ../results/figs/ws_large_z3.pdf -a inc2 --prefix z --suffix 3 --min 20 --legend "upper left" --xticks 100,501,100
uv run auto_plotter.py scale ../results/ws2.csv -o ../results/figs/ws2.pdf -a inc2 ganak d4 rec inc --prefix zt --legend "upper right" --max 20
uv run auto_plotter.py scale ../results/ws2.csv -o ../results/figs/ws2_large.pdf -a inc2 --prefix zt --legend "upper left" --xticks 10,95,10 --min 15


# =============================
#           LO + SUCCESSOR
# =============================
uv run auto_plotter.py scale ../results/lops_cards.csv -o ../results/figs/lops_cards.pdf -a inc3 ganak d4 --prefix cards --max 20
uv run auto_plotter.py scale ../results/lops_cards.csv -o ../results/figs/lops_cards_large.pdf -a inc3 --prefix cards --min 20 --legend "lower right"

uv run auto_plotter.py scale ../results/lops_p1.csv -o ../results/figs/lops_p1.pdf -a inc3 ganak d4 --prefix a --max 20
uv run auto_plotter.py scale ../results/lops_p1.csv -o ../results/figs/lops_p1_large.pdf -a inc3 --prefix a --min 20 --legend "lower right"

uv run auto_plotter.py scale ../results/lops_p2.csv -o ../results/figs/lops_p2.pdf -a inc3 ganak d4 --prefix b --max 20
uv run auto_plotter.py scale ../results/lops_p2.csv -o ../results/figs/lops_p2_large.pdf -a inc3 --prefix b --min 20 --legend "lower right"

uv run auto_plotter.py scale ../results/lops_p4.csv -o ../results/figs/lops_p4.pdf -a inc3 ganak d4 --prefix c --legend "lower right"
uv run auto_plotter.py scale ../results/lops_p5.csv -o ../results/figs/lops_p5.pdf -a inc3 ganak d4 --prefix d --legend "lower right"
