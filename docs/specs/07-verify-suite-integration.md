# Spec 07 — agent-verify as a suite member (compose, don't merge)

**Status:** Ready for implementation
**Lands in:** canon 0.6
**Author:** Noah / Orthogon AI Labs

---

## One-line

Make `agent-verify` an opt-in install in `canon-init` (a fourth optional component alongside Compound Engineering and `/last30days`), document the combined `Stop`-hook behavior, and let a verify catch be logged to `ERRORS.md` — without merging the two codebases.

---

## Why

canon + agent-verify + the persistence trio are starting to look like a **lightweight agent OS**: small modules that snap together — context (canon), planning (`/ce`), research (`/last30days`), and now honesty (verify). The right architecture for an OS is composable modules, not one binary. So verify stays its own repo and plugin with its own market position (the verification layer), and canon composes it at install time the same way it already composes Compound Engineering and `/last30days`.

This is the "both" answer: verify is a standalone product *and* a first-class suite member. Today the suite framing exists only in canon's "agent reliability toolkit" README section; this spec adds the install-time and runtime wiring that makes it real.

The composition is already half-built:
- canon and verify **share the protected-sections convention** (canon spec 02 / verify spec 02, same marker syntax). With both installed, a Markdown-touching session is checked at canon's Stop hook *and* at verify's claim boundary.
- A verify catch ("you said tests passed; they didn't") is exactly the kind of failure that belongs in `ERRORS.md`.

---

## Scope

In:
- A new opt-in step in `skills/canon-init/SKILL.md` to install `agent-verify`, mirroring the Compound Engineering / `/last30days` steps (ask → check prior install → install → verify → offline fallback → skip if opted out).
- An update to `canon-init`'s "ask the user" step and final report to include verify.
- A short **combined Stop-hook** note (in the hook explanation `canon-init` already gives the user) so the three Stop behaviors are not surprising together.
- An `ERRORS.md` integration: when verify catches a claim mismatch and the user resolves it, offer to log it to `ERRORS.md` — using the same **propose-and-confirm** discipline as the memory hook (never auto-write).
- README "agent reliability toolkit" / credits: note that `canon-init` can install verify for you.

Not in:
- **Merging the repos or vendoring verify's code into canon.** verify keeps its own repo, README, roadmap, and plugin identity. canon installs it; it does not contain it.
- Making verify a hard dependency. Everything canon does works without verify; verify is recommended, opt-in, and decline-able.
- Changing verify's own behavior. This spec is canon-side wiring only; any verify change is a verify-repo PR.

---

## The install step (mirror the existing pattern)

Add as step 4 in `canon-init` (after `/last30days`), structured exactly like steps 2 and 3:

1. **Ask** (in the step-1 questions): "Also install **agent-verify**? It catches the agent claiming it ran tests / pushed / kept protected sections intact when it didn't. Defaults to **yes** — it's the honesty layer of the same toolkit." Decline-able.
2. **Check prior install.** Look for verify's hook/command in the environment; if present, confirm in one line and skip.
3. **Install.** If not present:
   ```
   /plugin marketplace add Orthogon-AI-Labs/agent-verify
   /plugin install agent-verify
   ```
   (Mirror canon's own install matrix; verify ships the same way canon does.)
4. **Verify the install,** report clearly on failure, and **continue the bootstrap regardless** — canon works without it.
5. **Offline / restricted hosts:** surface the marketplace + install commands as a copy-paste block, same fallback as the other two.
6. **If opted out, skip the whole step.**

---

## Combined Stop-hook behavior (the note)

With both plugins installed, three things run at `Stop`. `canon-init` should explain this in one short block so it isn't surprising:

- **canon — protected sections:** checks that protected Markdown blocks weren't modified after edits.
- **canon — memory (propose):** if substantial work landed, *drafts* a MEMORY.md entry for your confirmation (does not write silently).
- **agent-verify — claims (block once):** if the final answer claimed tests/files/git/protected work that the repo contradicts, blocks once and makes the agent correct the record.

They are independent hooks and coexist cleanly. Order is not guaranteed and does not need to be; each is idempotent and reports separately.

---

## ERRORS.md integration

A verify catch is a failure worth remembering. When verify blocks on a mismatch and the user then fixes it, canon should **offer** (propose-and-confirm, never auto-write) to append an `ERRORS.md` entry:

```
## YYYY-MM-DD: Claimed <X> but verify caught it
- **What didn't work:** agent reported "<claim>"; verify found <reality>.
- **What worked instead:** <the fix>
- **Note for next time:** <e.g. run the test command before claiming a pass>
```

Mechanism: extend `errors-check`'s write-mode triggers to recognize "verify caught …" phrasing, and add a line to the combined-Stop note that canon can offer this. Keep it a proposal — consistent with the propose-and-confirm decision in the context-minimization work, an unconfirmed model-written ERRORS.md entry is the same anti-pattern as an unconfirmed MEMORY.md entry.

---

## Acceptance criteria

1. `canon-init` asks whether to install agent-verify, defaulting to yes, and skips cleanly when declined.
2. When opted in and not already present, `canon-init` runs the marketplace-add + install and verifies the result; on failure it reports and continues the rest of the bootstrap.
3. On a restricted/offline host, `canon-init` surfaces the copy-paste install block instead of failing.
4. The final `canon-init` report lists verify's install status (installed / already present / skipped / failed), alongside CE and `/last30days`.
5. The hook explanation describes the combined three-way Stop behavior.
6. `errors-check` recognizes a "verify caught …" trigger and *proposes* (does not auto-write) an ERRORS.md entry.
7. canon contains no agent-verify code; the integration is install + documentation only.

---

## Open questions

- **Default on or off?** This spec defaults the verify install to **yes** (it's the honesty half of the toolkit). If telemetry or feedback shows people want canon lean, flip it to default-no with a one-line recommendation. *Recommendation: default yes, decline-able — same as CE and `/last30days`.*
- **ERRORS.md auto vs propose.** This spec proposes (never auto-writes), consistent with the memory hook. Hold that line unless a user explicitly opts into silent logging.

---

## Cross-link

Pairs with agent-verify's own positioning (its repo README + ROADMAP) and the shared protected-sections convention (canon spec 02 / verify spec 02). The suite framing it implements is the "agent reliability toolkit" section of canon's README. Compose, don't merge: this spec is the seam, not a fusion.
