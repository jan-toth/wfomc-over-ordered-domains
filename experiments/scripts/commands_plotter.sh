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
#           FIGURES
# =============================

uv run auto_plotter.py bar ../results/math_x1.csv -o ../results/figs/math_wfomc.png -a inc2 rec inc --sort-by inc2
uv run auto_plotter.py bar ../results/math_x1.csv -o ../results/figs/math_wmc.png -a inc2 ganak d4 --sort-by inc2 --legend "upper left"
uv run auto_plotter.py bar ../results/math_x1.csv -o ../results/figs/math_x1.png -a inc2 ganak d4 rec inc --sort-by inc2 --legend "upper left"
uv run auto_plotter.py bar ../results/math_x2.csv -o ../results/figs/math_x2.png -a inc2 ganak d4 --sort-by inc2
uv run auto_plotter.py bar ../results/math_x3.csv -o ../results/figs/math_x3.png -a inc2 ganak d4 --sort-by inc2 --legend "upper left"

uv run auto_plotter.py cactus ../results/math_x1.csv -o ../results/figs/math_cactus_x1.png -a inc2 ganak d4 rec inc
uv run auto_plotter.py cactus ../results/math_x2.csv -o ../results/figs/math_cactus_x2.png -a inc2 ganak d4 --legend "upper left"
uv run auto_plotter.py cactus ../results/math_x3.csv -o ../results/figs/math_cactus_x3.png -a inc2 ganak d4 --legend "lower right"


uv run auto_plotter.py scale ../results/ht.csv -o ../results/figs/ht.png -a inc ganak d4 --prefix ht --max 15 --legend "upper left"
uv run auto_plotter.py scale ../results/ht.csv -o ../results/figs/ht_large.png -a inc --prefix ht --min 50 --xticks 100,1001,100 --legend "upper left"

uv run auto_plotter.py scale ../results/books.csv -o ../results/figs/books.png  -a inc2 ganak d4 rec inc --prefix b --legend "upper left"


uv run auto_plotter.py scale ../results/hmm.csv -o ../results/figs/hmm.png -a inc2 ganak d4 rec inc --prefix kl --max 20 --legend "upper left"
uv run auto_plotter.py scale ../results/hmm.csv -o ../results/figs/hmm_large.png -a inc2 --prefix kl --min 20 --legend "upper left" --xticks 20,90,10

uv run auto_plotter.py scale ../results/higher_hmm.csv -o ../results/figs/higher_hmm.png -a inc2 ganak d4 --prefix k --max 15 --legend "upper left"
uv run auto_plotter.py scale ../results/higher_hmm.csv -o ../results/figs/higher_hmm_large.png -a inc2 --prefix k --min 15 --legend "upper left" --xticks 15,55,5


uv run auto_plotter.py scale ../results/ws.csv -o ../results/figs/ws_z1.png -a inc2 ganak d4 rec inc --prefix z --suffix 1 --max 20 --legend "upper left"
uv run auto_plotter.py scale ../results/ws.csv -o ../results/figs/ws_z2.png -a inc2 ganak d4 rec inc --prefix z --suffix 2 --max 20 --legend "upper left"
uv run auto_plotter.py scale ../results/ws.csv -o ../results/figs/ws_z3.png -a inc2 ganak d4 rec inc --prefix z --suffix 3 --max 20 --legend "upper left"
uv run auto_plotter.py scale ../results/ws.csv -o ../results/figs/ws_large_z1.png -a inc2  --prefix z --suffix 1 --min 20 --legend "upper left" --xticks 100,501,100
uv run auto_plotter.py scale ../results/ws.csv -o ../results/figs/ws_large_z2.png -a inc2 --prefix z --suffix 2 --min 20 --legend "upper left" --xticks 100,501,100
uv run auto_plotter.py scale ../results/ws.csv -o ../results/figs/ws_large_z3.png -a inc2 --prefix z --suffix 3 --min 20 --legend "upper left" --xticks 100,501,100
uv run auto_plotter.py scale ../results/ws2.csv -o ../results/figs/ws2.png -a inc2 ganak d4 rec inc --prefix zt --legend "upper right" --max 20
uv run auto_plotter.py scale ../results/ws2.csv -o ../results/figs/ws2_large.png -a inc2 --prefix zt --legend "upper left" --xticks 10,95,10 --min 15

