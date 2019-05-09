#!/usr/bin/env bash


export PYTHONPATH="${PYTHONPATH}:$HOME/cs267/more-cores"


# Strong scaling
./morph_demo.py 100 6 4
./morph_demo.py 100 5 4
./morph_demo.py 100 4 4
./morph_demo.py 100 3 4
./morph_demo.py 100 2 4
./morph_demo.py 100 1 4

# Weak scaling
./morph_demo.py 240 6 4
./morph_demo.py 200 5 4
./morph_demo.py 160 4 4
./morph_demo.py 120 3 4
./morph_demo.py 80 2 4
./morph_demo.py 40 1 4
