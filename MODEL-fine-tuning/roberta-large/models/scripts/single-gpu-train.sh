#!/bin/bash


CUDA_VISIBLE_DEVICES=0 python3 ./training/train_single_large.py \
  --jsonl_path ./data/mdd-gen/llama3_placeholder_10K_v0.jsonl \


# Wait for both processes to finish
wait

echo "Both Python modules have finished execution."
