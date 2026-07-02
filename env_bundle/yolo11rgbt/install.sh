#!/usr/bin/env bash
set -e

# Recommended: portable solve/create
conda env create -n yolo11rgbt -f environment.yml

# Optional exact restore on same OS/arch/channel mirror:
# conda create -n yolo11rgbt --file explicit.txt

# Activate and verify
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate yolo11rgbt
python -V
python -m pip -V
