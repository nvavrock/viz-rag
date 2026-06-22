#!/usr/bin/env bash
# Clone upstream sources for the viz RAG corpus (shallow clones).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/sources"
mkdir -p "$SRC"

clone_if_missing() {
  local name="$1"
  local url="$2"
  if [[ -d "$SRC/$name/.git" ]]; then
    echo "Already cloned: $name"
    git -C "$SRC/$name" fetch --depth 1 origin
    git -C "$SRC/$name" checkout -q master 2>/dev/null || git -C "$SRC/$name" checkout -q main
    git -C "$SRC/$name" pull --depth 1 -q
  else
    echo "Cloning $name..."
    git clone --depth 1 "$url" "$SRC/$name"
  fi
}

clone_if_missing "data_to_viz" "https://github.com/holtzy/data_to_viz.git"
clone_if_missing "ggplot2" "https://github.com/tidyverse/ggplot2.git"

echo "Done. Sources in $SRC"
