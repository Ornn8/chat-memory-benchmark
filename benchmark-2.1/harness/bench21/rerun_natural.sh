#!/bin/bash
cd "$(dirname "$0")/.."   # run from benchmark-2.1/harness
export PYTHONIOENCODING=utf-8
SYS=$1; RUN=$2; shift 2
NAT=${NAT:-../natural/dataset}
REL=${REL:-../dataset}
for SPLIT in "$@"; do
  python -m bench21.natural run --release $REL --natural $NAT --system $SYS --split $SPLIT --run $RUN --workers 6
  python -m bench21.natural judge --release $REL --natural $NAT --system $SYS --split $SPLIT --run $RUN --workers 8
  python -m bench21.natural summarize --release $REL --natural $NAT --system $SYS --split $SPLIT --run $RUN
done
