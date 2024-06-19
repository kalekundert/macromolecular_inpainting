#!/usr/bin/env sh

for replicate in {1..3}; do
    for img_size in 24A 16A; do
        for max_threads in {1..16}; do
            for profiler in simple advanced; do
                out_path="${profiler}.max_threads=${max_threads}.img_size=${img_size}.rep=${replicate}.prof"
                [ -e $out_path ] && continue
                date
                echo $out_path
                POLARS_MAX_THREADS=$max_threads \
                    ./profile_mmg.py \
                    $profiler \
                    $img_size \
                    2> $out_path
            done
        done
    done
done

