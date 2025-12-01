#!/bin/bash

for fn in $(ls ../models/seq/head_middle_tail_cnf); do
    base="${fn%.*}"
    uv run ./fo2ex2cnf.py -i "../models/seq/head_middle_tail_cnf/$fn" -o "../models/seq/head_middle_tail_cnf/$base.cnf"  
done
