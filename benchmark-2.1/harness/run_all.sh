#!/bin/bash
# Sequential driver for the Bench 2.1 reruns (unified environment). Usage: bash bench21/run_all.sh RUN_NAME
cd "$(dirname "$0")/.."
export PYTHONUTF8=1
REL=F:/Olivia/ClaudeWork/memory-bench-private/bench2/release-2.1
RUN=${1:-R21}
for sys in qwen-base; do
  python -m bench21.runner --release $REL --system $sys --split sealed --run $RUN
done
python -m bench21.runner --release $REL --system qwen-base --split sealed --run $RUN --sentinel
python -m bench21.runner --release $REL --system qwen-base --split sealed --run $RUN --sentinel --leaky
for sys in none recent6; do
  python -m bench21.runner --release $REL --system $sys --split sealed --run $RUN
done
for sys in qwen-base; do
  python -m bench21.runner --release $REL --system $sys --split dev --run $RUN
done
echo ALL-DONE
