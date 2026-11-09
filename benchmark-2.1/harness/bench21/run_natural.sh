#!/bin/bash
# usage: run_natural.sh SYSTEM RUN   (gateway: OPENAI_BASE_URL, default http://127.0.0.1:18878/v1)
cd "$(dirname "$0")/.."   # run from benchmark-2.1/harness
export PYTHONIOENCODING=utf-8
SYS=$1; RUN=$2
NAT=${NAT:-../natural/dataset}
REL=${REL:-../dataset}
for SPLIT in sealed dev; do
  python -m bench21.natural run --release $REL --natural $NAT --system $SYS --split $SPLIT --run $RUN --workers 6
  python -m bench21.natural judge --release $REL --natural $NAT --system $SYS --split $SPLIT --run $RUN --workers 6
  python -m bench21.natural summarize --release $REL --natural $NAT --system $SYS --split $SPLIT --run $RUN
done
