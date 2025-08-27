#!/bin/bash

# Activate Conda environment
exec conda activate /workspace/ENVS/Conda_P3.11

# Change directory and launch
cd /workspace/ComfyUI
exec python main.py --listen --port 8188
