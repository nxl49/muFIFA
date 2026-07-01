#!/usr/bin/env bash
# Fetch the international football datasets used by the model.
# A pinned snapshot is committed in this folder; run this only to refresh.
set -euo pipefail
cd "$(dirname "$0")"
BASE="https://raw.githubusercontent.com/martj42/international_results/master"
for f in results goalscorers shootouts; do
  echo "downloading $f.csv ..."
  curl -sSL -o "$f.csv" "$BASE/$f.csv"
done
echo "done: $(wc -l < results.csv) result rows"
