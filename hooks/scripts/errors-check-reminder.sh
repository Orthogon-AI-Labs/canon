#!/bin/bash
# UserPromptSubmit hook: on exit 0, stdout is added to the agent's context for this prompt.
# A "prompt"-type hook can't do this: its model only returns ok/not-ok, and not-ok blocks the user's prompt.
# Stays silent in projects without an ERRORS.md, so it adds nothing outside canon projects.

ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -f "$ROOT/ERRORS.md" ] || exit 0

echo "canon: If this request involves implementation work that resembles past tasks in this project (bug fix, architecture choice, library selection, performance work, refactor), silently invoke the errors-check skill in read mode before suggesting any approach. Surface a match only if confident it applies. Skip this check for one-line answers, clarifying questions, or non-implementation requests."
