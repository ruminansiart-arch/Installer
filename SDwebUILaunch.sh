#!/bin/bash

# Source conda initialization
source /opt/conda/etc/profile.d/conda.sh

# Activate Conda environment
conda activate /workspace/ENVS/Conda_P3.10

# Change directory and launch
cd /workspace/stable-diffusion-webui
exec python launch.py --listen --port 8288 --no-download-sd-model --xformers --no-half-vae --theme dark
