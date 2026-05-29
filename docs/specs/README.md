# canon Roadmap Specs

Implementation specs for canon. Each spec is written as a codeplan-style slash-command brief: user surface, scope, file changes, validation, and launch notes. Specs 01–05 are shipped as of v0.5.0.

## Sequence

1. `01-look-back.md` — `/canon:look-back`, mines recent work for reusable skills, subagents, and automations. **(shipped, v0.4.0)**
2. `02-protected-sections.md` — protected Markdown regions plus diff checks for canon and agent-verify. **(shipped, v0.4.0)**
3. `03-canon-optimize-alpha.md` — `/canon:optimize`, measured bounded edits for skill files. **(shipped, v0.4.0)**
4. `04-porting-canon.md` — the model for porting canon to any agent runtime, with the Codex port as reference implementation and Hermes / OpenCode / Cursor / Aider named as wanted next ports. **(shipped, v0.4.0)**
5. `05-autobrowse-skill-graduation.md` — Autobrowse-style strategy iteration and skill graduation. **(shipped, v0.5.0)**
6. `06-optimize-context-files.md` — extend `/canon:optimize` from skills to context files (`CLAUDE.md` / `MEMORY.md`): prune toward minimal, prove the cut against an eval. Implements the context-minimization plan. **(implemented — size grader, scaffold, and optimize context-file mode all shipped — v0.6)**

The repositioning behind spec 06 is in [`../context-minimization-plan-2026-05-29.md`](../context-minimization-plan-2026-05-29.md).
