#!/bin/bash

# Activate Conda environment
exec conda activate /workspace/ENVS/Conda_P3.10

# Change directory and launch
cd /workspace/stable-diffusion-webui
exec python launch.py --listen --port 8288 --xformers --theme dark
