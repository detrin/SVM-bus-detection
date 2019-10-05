#!/bin/bash

while :; do
    rm buffer/*
    rm test_images/*
    python3 get_stream_address.py
    stream_url=$(cat url_stream.txt)
    time ffmpeg -loglevel panic -y -i $stream_url -q:v 1 -vframes 4 -t 2 buffer/test_image%02d.jpg
    cp buffer/* test_images/
    for i in {0..300}; do
        time python test.py &
        time ffmpeg -loglevel panic -y -i $stream_url -q:v 1 -vframes 4 -t 2 buffer/test_image%02d.jpg &
        wait
        rm test_images/*
        cp buffer/* test_images/
        rm buffer/*
    done
done