#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/optimize/scaffold-context-eval.sh <context-file> [--command "<behavior cmd>"] [--out PATH] [--root PATH] [--force] [--dry-run]

Scaffolds a canon optimize eval for a context file (CLAUDE.md / MEMORY.md / AGENTS.md).
The eval has a deterministic cost-budget task (max_chars set to the file's current
size, so the optimize loop must make it strictly smaller) and, if --command is given,
a behavior task that runs your project's own tests/checks and must not regress.

Options:
  --command CMD  Behavior check, e.g. "npm test". Optional but recommended — without
                 it, optimize runs cost-only and labels the result low-confidence.
  --out PATH     Eval output path. Defaults to evals/<basename>-context.json
  --root PATH    Target project root. Defaults to the current directory.
  --force        Overwrite the eval file if it already exists.
  --dry-run      Print what would be written without writing.
  -h, --help     Show this help.
USAGE
}

ctx_file="${1:-}"
if [[ -z "$ctx_file" || "$ctx_file" == "-h" || "$ctx_file" == "--help" ]]; then
  usage
  [[ "$ctx_file" == "-h" || "$ctx_file" == "--help" ]] && exit 0
  echo "error: <context-file> is required" >&2
  exit 2
fi
shift || true

behavior_cmd=""
out_path=""
target_root="$(pwd)"
force=0
dry_run=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --command) behavior_cmd="${2:-}"; shift 2 ;;
    --out)     out_path="${2:-}"; shift 2 ;;
    --root)    target_root="${2:-}"; shift 2 ;;
    --force)   force=1; shift ;;
    --dry-run) dry_run=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 2 ;;
  esac
done

ctx_path="$target_root/$ctx_file"
if [[ ! -f "$ctx_path" ]]; then
  echo "error: context file not found: $ctx_path" >&2
  exit 2
fi

# Deterministic baseline: current char count. The optimize loop must beat this.
baseline_chars="$(wc -c < "$ctx_path" | tr -d ' ')"

base="$(basename "$ctx_file")"
stem="${base%.*}"
[[ -z "$out_path" ]] && out_path="evals/${stem}-context.json"
abs_out="$target_root/$out_path"

# Build the eval JSON (dependency-free; no PyYAML needed).
tasks="    {
      \"id\": \"cost-budget\",
      \"input\": \"${ctx_file}\",
      \"expected\": { \"max_chars\": ${baseline_chars} }
    }"
if [[ -n "$behavior_cmd" ]]; then
  esc_cmd="${behavior_cmd//\\/\\\\}"; esc_cmd="${esc_cmd//\"/\\\"}"
  tasks="${tasks},
    {
      \"id\": \"behavior-held\",
      \"expected\": { \"command\": \"${esc_cmd}\", \"not_contains\": [\"FAIL\", \"Error\"] }
    }"
fi

eval_json="{
  \"name\": \"${stem}-context-optimize\",
  \"_note\": \"canon optimize context-file eval. cost-budget max_chars is the file's baseline size; the optimize loop must make the file strictly smaller. behavior-held (if present) runs your tests and must not regress. Re-baseline max_chars after each accepted prune.\",
  \"tasks\": [
${tasks}
  ]
}"

if [[ "$dry_run" == "1" ]]; then
  echo "[dry-run] would write $abs_out (baseline ${baseline_chars} chars):"
  echo "$eval_json"
  exit 0
fi

if [[ -f "$abs_out" && "$force" != "1" ]]; then
  echo "error: $abs_out already exists. Pass --force to overwrite." >&2
  exit 2
fi

mkdir -p "$(dirname "$abs_out")"
printf '%s\n' "$eval_json" > "$abs_out"
echo "Wrote $abs_out"
echo "Baseline: ${baseline_chars} chars. Run: hooks/scripts/canon-eval.sh ${out_path}"
echo "After each accepted prune, lower max_chars to the new size to lock the gain."
