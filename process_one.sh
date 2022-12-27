#!/bin/bash

if [ ! -f $1.emb.npz ]; then
	echo "Starting $1"
	ffmpeg -y -i $1 -acodec pcm_s16le -ar 16000 -f wav $1.wav
    ./process.py $1.wav $1 $THREADS
	rm -f $1.wav
    mv $1.embt.npz $1.emb.npz
else
    echo "Skipping $1 (already done)"
fi
