#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/graduation/scaffold.sh <task-name> [--root PATH] [--force] [--dry-run]

Scaffolds a canon skill-graduation workspace at:
  <root>/.canon/graduation/tasks/<task-name>/

Options:
  --root PATH   Target project root. Defaults to the current directory.
  --force       Replace task.md / strategy.md if they already exist.
  --dry-run     Print what would change without writing files.
  -h, --help    Show this help.
USAGE
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source_root="$(cd "$script_dir/../.." && pwd)"

task_name="${1:-}"
if [[ -z "$task_name" || "$task_name" == "-h" || "$task_name" == "--help" ]]; then
  usage
  [[ "$task_name" == "-h" || "$task_name" == "--help" ]] && exit 0
  echo "error: <task-name> is required" >&2
  exit 2
fi
shift || true

target_root="$(pwd)"
force=0
dry_run=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      target_root="${2:-}"
      shift 2
      ;;
    --force)
      force=1
      shift
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ "$dry_run" -ne 1 ]]; then
  mkdir -p "$target_root"
  target_root="$(cd "$target_root" && pwd)"
fi

task_dir="$target_root/.canon/graduation/tasks/$task_name"
reports_dir="$task_dir/reports"
graduated_dir="$task_dir/graduated"
workspace_readme="$target_root/.canon/graduation/README.md"
task_template="$source_root/templates/graduation-task.md"

write_file() {
  local label="$1"
  local dst="$2"
  local content="$3"
  if [[ -e "$dst" && "$force" -ne 1 ]]; then
    echo "skip: $label already exists (use --force to replace)"
    return
  fi
  if [[ "$dry_run" -eq 1 ]]; then
    if [[ -e "$dst" && "$force" -eq 1 ]]; then
      echo "dry-run: would replace $label"
    else
      echo "dry-run: would write $label"
    fi
    return
  fi
  mkdir -p "$(dirname "$dst")"
  printf '%s' "$content" > "$dst"
  echo "write: $label"
}

# task.md — rendered from the canon template with the task name substituted.
task_content=""
if [[ -f "$task_template" ]]; then
  task_content="$(<"$task_template")"
  task_content="${task_content//\{\{TASK_NAME\}\}/$task_name}"
else
  task_content="# Task: $task_name"$'\n'
fi

strategy_content="# Strategy: $task_name

> The only fast-changing state during iteration. One bounded change per run.
> Keep the fast path at the top. No transcripts, no secrets.

## Fast path

- (none yet — fill in after the first successful run)

## Failure recovery

- (none yet)

## What not to do again

- (none yet)
"

workspace_readme_content="# canon skill-graduation workspace

Each task lives under \`tasks/<task-name>/\`:

- \`task.md\` — fixed definition (objective, inputs, success criteria).
- \`strategy.md\` — the only fast-changing state during iteration.
- \`reports/\` — one report per run.
- \`graduated/SKILL.md\` — the final, self-contained skill.

See \`docs/graduation.md\` in the canon repo for the loop and convergence rule.
"

if [[ "$dry_run" -eq 1 ]]; then
  echo "[canon graduation dry-run]"
  echo "target: $task_dir"
fi

write_file ".canon/graduation/README.md" "$workspace_readme" "$workspace_readme_content"
write_file "tasks/$task_name/task.md" "$task_dir/task.md" "$task_content"
write_file "tasks/$task_name/strategy.md" "$task_dir/strategy.md" "$strategy_content"

if [[ "$dry_run" -eq 1 ]]; then
  echo "dry-run: would create tasks/$task_name/reports/ and tasks/$task_name/graduated/"
else
  mkdir -p "$reports_dir" "$graduated_dir"
  echo "write: tasks/$task_name/reports/"
  echo "write: tasks/$task_name/graduated/"
fi

echo
echo "Next:"
echo "  1. Fill in task.md (objective, inputs, success criteria)."
echo "  2. Run the task, save reports/iter-001.md, then iterate strategy.md one change at a time."
echo "  3. Graduate to graduated/SKILL.md when it passes 2 of the last 3 runs."
