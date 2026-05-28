#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/install-codex.sh init --runtime codex [--root PATH] [options]
  scripts/install-codex.sh install --runtime codex [--root PATH] [options]
  scripts/install-codex.sh doctor --runtime codex [--root PATH]

Options:
  --root PATH       Target workspace root. Defaults to the current directory.
  --name NAME       Project name. Defaults to the target directory name.
  --user NAME       Primary collaborator name. Defaults to "Unknown".
  --role ROLE       Primary collaborator role. Defaults to "maintainer".
  --stack TEXT      Stack summary. Defaults to "Unspecified".
  --voice TEXT      Working style. Defaults to "Direct, concise, implementation-first".
  --force           Replace AGENTS.md, MEMORY.md, and ERRORS.md if they exist.
  --dry-run         Print what would change without writing files.
  -h, --help        Show this help.
USAGE
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source_root="$(cd "$script_dir/.." && pwd)"

command="${1:-}"
if [[ -z "$command" || "$command" == "-h" || "$command" == "--help" ]]; then
  usage
  exit 0
fi
shift || true

target_root="$(pwd)"
project_name=""
user_name="Unknown"
user_role="maintainer"
stack="Unspecified"
voice="Direct, concise, implementation-first"
force=0
dry_run=0
runtime=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --runtime)
      runtime="${2:-}"
      shift 2
      ;;
    --root)
      target_root="${2:-}"
      shift 2
      ;;
    --name)
      project_name="${2:-}"
      shift 2
      ;;
    --user)
      user_name="${2:-}"
      shift 2
      ;;
    --role)
      user_role="${2:-}"
      shift 2
      ;;
    --stack)
      stack="${2:-}"
      shift 2
      ;;
    --voice)
      voice="${2:-}"
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

if [[ -n "$runtime" && "$runtime" != "codex" ]]; then
  echo "Unsupported runtime: $runtime" >&2
  exit 2
fi

if [[ ! -d "$target_root" ]]; then
  if [[ "$command" == "init" || "$command" == "install" ]]; then
    if [[ "$dry_run" -eq 1 ]]; then
      case "$target_root" in
        /*) ;;
        *) target_root="$(pwd)/$target_root" ;;
      esac
    else
      mkdir -p "$target_root"
      target_root="$(cd "$target_root" && pwd)"
    fi
  else
    echo "Target root does not exist: $target_root" >&2
    exit 1
  fi
else
  target_root="$(cd "$target_root" && pwd)"
fi
if [[ -z "$project_name" ]]; then
  project_name="$(basename "$target_root")"
fi

render_template() {
  local src="$1"
  local dst="$2"
  local content
  content="$(<"$src")"
  content="${content//\{\{PROJECT_NAME\}\}/$project_name}"
  content="${content//\{\{USER_NAME\}\}/$user_name}"
  content="${content//\{\{USER_ROLE\}\}/$user_role}"
  content="${content//\{\{STACK\}\}/$stack}"
  content="${content//\{\{VOICE\}\}/$voice}"
  content="${content//\{\{DATE\}\}/$(date +%F)}"
  printf '%s\n' "$content" > "$dst"
  perl -0pi -e 's/\{\{TODO:[^}]+\}\}/_No project-specific entry recorded yet._/g; s/\{\{[^}]+\}\}/Unspecified/g' "$dst"
}

write_main_file() {
  local src="$1"
  local dst="$2"
  local label
  label="$(basename "$dst")"
  if [[ -e "$dst" && "$force" -ne 1 ]]; then
    echo "skip: $label already exists"
    echo "      append guidance: copy relevant canon sections from $src into $dst"
    echo "      replace guidance: rerun with --force after reviewing the existing file"
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
  render_template "$src" "$dst"
  echo "write: $label"
}

install_skills() {
  local skills_root="$target_root/.canon/codex/skills"
  if [[ "$dry_run" -eq 1 ]]; then
    echo "dry-run: would write .canon/codex/skills"
    return
  fi
  mkdir -p "$skills_root/look-back" "$skills_root/protected-sections" "$skills_root/optimize"
  cp "$source_root/ports/codex/SKILL-look-back.md" "$skills_root/look-back/SKILL.md"
  cp "$source_root/ports/codex/SKILL-protected-sections.md" "$skills_root/protected-sections/SKILL.md"
  cp "$source_root/ports/codex/SKILL-optimize.md" "$skills_root/optimize/SKILL.md"
  echo "write: .canon/codex/skills"
}

install_bin() {
  local bin_root="$target_root/.canon/codex/bin"
  if [[ "$dry_run" -eq 1 ]]; then
    echo "dry-run: would write .canon/codex/bin/check-protected-sections.py"
    return
  fi
  mkdir -p "$bin_root"
  cp "$source_root/hooks/scripts/check-protected-sections.py" "$bin_root/check-protected-sections.py"
  chmod +x "$bin_root/check-protected-sections.py"
  echo "write: .canon/codex/bin/check-protected-sections.py"
}

init_codex() {
  if [[ "$dry_run" -eq 1 ]]; then
    echo "[canon codex dry-run]"
    echo "target: $target_root"
  else
    mkdir -p "$target_root"
  fi
  write_main_file "$source_root/templates/AGENTS-codex.md" "$target_root/AGENTS.md"
  write_main_file "$source_root/templates/MEMORY.md" "$target_root/MEMORY.md"
  write_main_file "$source_root/templates/ERRORS.md" "$target_root/ERRORS.md"
  install_skills
  install_bin
  echo
  echo "Next:"
  echo "  Ask Codex: read AGENTS.md, then run scripts/install-codex.sh doctor --runtime codex"
  echo "  Ask Codex: look back over recent work and suggest reusable skills"
}

check_file() {
  local path="$1"
  local label="$2"
  if [[ -f "$path" ]]; then
    echo "ok: $label"
    return 0
  fi
  echo "fail: missing $label"
  return 1
}

check_no_placeholders() {
  local failed=0
  local file
  for file in "$target_root/AGENTS.md" "$target_root/MEMORY.md" "$target_root/ERRORS.md"; do
    if [[ -f "$file" ]] && grep -q '{{' "$file"; then
      echo "fail: unresolved template placeholder in $(basename "$file")"
      failed=1
    fi
  done
  return "$failed"
}

doctor_codex() {
  local failed=0
  echo "[canon doctor: codex]"
  check_file "$target_root/AGENTS.md" "AGENTS.md" || failed=1
  check_file "$target_root/MEMORY.md" "MEMORY.md" || failed=1
  check_file "$target_root/ERRORS.md" "ERRORS.md" || failed=1
  check_file "$target_root/.canon/codex/bin/check-protected-sections.py" "protected-section checker" || failed=1
  check_file "$target_root/.canon/codex/skills/look-back/SKILL.md" "look-back skill" || failed=1
  check_file "$target_root/.canon/codex/skills/protected-sections/SKILL.md" "protected-sections skill" || failed=1
  check_file "$target_root/.canon/codex/skills/optimize/SKILL.md" "optimize skill" || failed=1
  check_no_placeholders || failed=1
  if [[ "$failed" -eq 0 ]]; then
    echo "ok: no unresolved template placeholders"
    echo "pass: Codex workspace is canon-ready"
    return 0
  fi
  echo "fail: Codex workspace needs attention"
  return 1
}

case "$command" in
  init|install)
    init_codex
    ;;
  doctor)
    doctor_codex
    ;;
  *)
    echo "Unknown command: $command" >&2
    usage
    exit 2
    ;;
esac
