#!/bin/bash

DIR="$(dirname $0)"

prefix="$DIR/../"
suffix=".wfomcs"

for fn in $(ls -v "$DIR/.."); do
    name=${fn#$prefix}
    name=${name%$suffix}
    echo "Processing $fn"
    time uv run "$DIR/../../../../scripts/generators/fo2ex2cnf.py" -e 3 -i "$DIR/../$fn" -o "$DIR/${name}.cnf"
done
