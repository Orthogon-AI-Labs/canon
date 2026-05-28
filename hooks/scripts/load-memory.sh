#!/bin/bash
# SessionStart hook: read MEMORY.md and ERRORS.md from the project root
# into the agent's context. Search outward from CWD up to git root or 5 levels.

find_project_root() {
  local dir="$PWD"
  local levels=0
  while [ "$dir" != "/" ] && [ $levels -lt 5 ]; do
    if [ -d "$dir/.git" ] || [ -f "$dir/package.json" ] || [ -f "$dir/pyproject.toml" ] || [ -f "$dir/CLAUDE.md" ]; then
      echo "$dir"
      return 0
    fi
    dir="$(dirname "$dir")"
    levels=$((levels + 1))
  done
  echo "$PWD"
}

ROOT="$(find_project_root)"
OUTPUT=""

if [ -f "$ROOT/MEMORY.md" ]; then
  OUTPUT+="## Project memory (from $ROOT/MEMORY.md)"$'\n\n'
  # Cap at first 200 lines to avoid blowing the context window on a huge log
  OUTPUT+="$(head -200 "$ROOT/MEMORY.md")"$'\n\n'
fi

if [ -f "$ROOT/ERRORS.md" ]; then
  OUTPUT+="## Project failure log (from $ROOT/ERRORS.md)"$'\n\n'
  OUTPUT+="$(head -200 "$ROOT/ERRORS.md")"$'\n\n'
fi

if [ -n "$OUTPUT" ]; then
  echo "$OUTPUT"
fi
