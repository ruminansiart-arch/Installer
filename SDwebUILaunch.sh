#!/bin/bash

# Activate Conda environment
source /workspace/ENVS/Conda_P3.10/bin/activate

# Navigate and launch
cd /workspace/stable-diffusion-webui
python launch.py --listen --port 8288 --theme dark
