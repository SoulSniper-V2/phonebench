#!/bin/zsh
# Usage: scripts/run_batch.sh <log> [runner args...]
cd "$(dirname "$0")/.."
export PHONEBENCH_DEVICE=${PHONEBENCH_DEVICE:-$(phonedriver devices 2>/dev/null | awk '/^ios:/{print $1; exit}')}
log=$1; shift
python3 -u -m phonebench.runner "$@" >> "$log" 2>&1
