#!/bin/bash

FOLDER="./Data/Audio/"

PARALLEL=$1
if [ "x$PARALLEL" == "x" ]; then
    PARALLEL=1
fi

THREADS=$2
if [ "x$THREADS" == "x" ]; then
    THREADS=1
fi

export THREADS=$THREADS

echo "Processing $FOLDER with $PARALLEL files in parallel, using $THREADS threads per file"


find $FOLDER -name "*.mp4" -print0 | xargs --null -t -n 1 -P $PARALLEL ./process_one.sh
