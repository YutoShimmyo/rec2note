#!/bin/bash -l
#SBATCH -p gpu_short
#SBATCH --gres=gpu:1
#SBATCH -c 8
#SBATCH -t 1:00:00
#SBATCH -o logs/minutes_%j.out
#SBATCH -e logs/minutes_%j.err

# Host setup
module load singularity
module load compiler/nvhpc/23.11

echo "Starting recording→artifact pipeline"
echo "Date: $(date)"
echo "Host: $(hostname)"

# Args: <input file (relative to project root)> [extra main.py args...]
INPUT_FILE=$1

if [ -z "$INPUT_FILE" ]; then
  echo "Error: No input file provided."
  echo "Usage: sbatch run_slurm.sh input/file.mp4 [--skill <name>] [--minutes-backend api] ..."
  exit 1
fi
shift
EXTRA_ARGS="$@"   # passed straight through to main.py (e.g. --skill magic-lecture)

# Run inside Singularity container
# Adjust the container path if necessary. Using the one from the user's example.
CONTAINER_PATH="/work/yuto-sh/tensorflow_latest-gpu.sif"
PROJECT_DIR=$(pwd)

echo "Processing $INPUT_FILE in $PROJECT_DIR (args: $EXTRA_ARGS)"

# Cluster-compatible deps only (mlx is Apple-Silicon only; use API or faster-whisper here).
# PDF export needs system libs (pango/cairo) that may be unavailable on the cluster —
# request --output md there, or let PDF degrade gracefully.
singularity exec --nv $CONTAINER_PATH \
  bash -c "cd $PROJECT_DIR && \
           pip install --user faster-whisper huggingface_hub google-genai openai markdown pyyaml python-dotenv && \
           python main.py $INPUT_FILE $EXTRA_ARGS"

echo "Job finished at $(date)"
