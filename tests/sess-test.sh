#!/bin/bash
# Stop-hook once-per-session tests (PR #8). Usage: sess-test.sh WORKDIR
# Set CANON_CLONE to the canon checkout under test (default: this repo).
set -u
CLONE=${CANON_CLONE:-$(cd "$(dirname "$0")/.." && pwd)}
SP=$1
CMD=$(python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));print(*[h["command"] for g in d["hooks"]["Stop"] for h in g["hooks"] if "protected-sections-stop-hook.py" in h.get("command","")])' $CLONE/hooks/hooks.json)
export CLAUDE_PLUGIN_ROOT=$CLONE
rm -rf $SP/sess && mkdir -p $SP/sess && cd $SP/sess && git -c init.defaultBranch=main init -q repo && cd repo
git config user.email t@e.x; git config user.name t
printf '<!-- canon:protected:start name="routing-invariant" -->\nRequests are always routed through the blue gateway.\n<!-- canon:protected:end -->\n' > NOTES.md
git add . && git commit -qm base
n=0; fails=0
run() { # $1 expected exit, $2 label, $3 stdin
  n=$((n+1)); printf '%s' "$3" | bash -c "$CMD" >/dev/null 2>err.txt; rc=$?
  if [ "$rc" = "$1" ]; then echo "PASS  $n. $2 -> exit $rc"; else fails=$((fails+1)); echo "FAIL  $n. $2 -> exit $rc (want $1)"; tail -3 err.txt | sed 's/^/      /'; fi
  rm -f err.txt
}
check() { if eval "$1"; then echo "PASS  $2"; else fails=$((fails+1)); echo "FAIL  $2"; fi; }
S1='{"session_id":"sess-1","stop_hook_active":false}'
S2='{"session_id":"sess-2","stop_hook_active":false}'
STATE=.git/canon-protected-sections
perl -pi -e 's/blue/green/' NOTES.md
run 2 "S1 touched block, first stop" "$S1"
run 0 "S1 same violation, next turn" "$S1"
run 0 "S1 stop_hook_active=true" '{"session_id":"sess-1","stop_hook_active":true}'
printf '# Title\n\n' | cat - NOTES.md > t && mv t NOTES.md
run 0 "S1 lines shifted by an edit above the block" "$S1"
run 2 "S2 (another session) same violation" "$S2"
perl -pi -e 's/green/red/' NOTES.md
run 2 "S1 block edited again (green->red)" "$S1"
run 0 "S1 next turn" "$S1"
git add NOTES.md
run 0 "S1 same change now staged (index)" "$S1"
git reset -q; git checkout -q NOTES.md
run 0 "S1 reverted, check passes" "$S1"
check "[ ! -e $STATE/sess-1.json ]" "state for sess-1 cleared once the violation went away"
perl -pi -e 's/blue/green/' NOTES.md
run 2 "S1 same violation comes back -> reported again" "$S1"
run 2 "no session_id -> no memory, blocks" '{"stop_hook_active":false}'
run 2 "no session_id again -> blocks again" '{"stop_hook_active":false}'
run 2 "path-traversal session_id rejected, blocks" '{"session_id":"../../escape","stop_hook_active":false}'
check "! ls -R $SP/sess | grep -q escape" "nothing written for the rejected session_id"
echo 'not json{' > $STATE/sess-3.json
run 2 "corrupt state file -> treated as empty, blocks" '{"session_id":"sess-3","stop_hook_active":false}'
run 0 "corrupt file was rewritten, next turn" '{"session_id":"sess-3","stop_hook_active":false}'
touch -t 202001010000 $STATE/sess-2.json
run 2 "new session saves and prunes week-old state" '{"session_id":"sess-4","stop_hook_active":false}'
check "[ ! -e $STATE/sess-2.json ]" "stale sess-2.json pruned"
git checkout -q NOTES.md && grep -v 'canon:protected' NOTES.md > t && mv t NOTES.md
run 2 "S5 block removed" '{"session_id":"sess-5","stop_hook_active":false}'
run 0 "S5 removed block, next turn" '{"session_id":"sess-5","stop_hook_active":false}'
git checkout -q NOTES.md && perl -pi -e 's/blue/green/' NOTES.md
chmod 000 $STATE
run 2 "unreadable state dir -> still blocks" '{"session_id":"sess-6","stop_hook_active":false}'
run 2 "unreadable state dir -> blocks again (no memory)" '{"session_id":"sess-6","stop_hook_active":false}'
chmod 755 $STATE
check "[ -z \"\$(git status --short | grep -v NOTES.md)\" ]" "state files never show in git status"
echo "--- $n hook runs, $fails failures"
[ $fails = 0 ]
