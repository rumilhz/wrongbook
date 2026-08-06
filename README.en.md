# WrongBook · The Pre-flight Mistake Book for AI Agents

[English](README.en.md) | [中文](README.md)

> Turn the waste of "error → diagnose → fix" into a rulebook your agent reads **before it acts**.

AI agents can self-correct — given an error, they can usually diagnose and fix it themselves. But correcting is not free: it costs time, attention, and tokens. In human learning, a teacher tells you "don't write it that way" *before* you write it, and you skip the detour entirely. **This repo is that teacher for your agent**: it puts the rules in front of the agent before it runs commands, writes code, or installs packages.

---

## Why

Most agent "experience" mechanisms are **post-hoc**:

```
command errors → diagnose → recall/seek fix → repair → (maybe) record
```

Every step costs money, and the same class of errors recurs across sessions — because there is no reliable bridge between "recording" and "avoiding next time".

This project is **pre-flight**:

```
before writing → check the rulebook → rule hit → write it differently → no error
```

The agent already knows how to fix errors; it just spends extra time doing so. **If it knows not to write a certain way before writing, the entire error loop never happens.**

---

## Quick start (3 steps, ~3 minutes)

**Step 1 — Create the standing instruction file**

Put an `AGENTS.md` in your workspace (Claude Code: `CLAUDE.md`; Reasonix: `REASONIX.md`). Copy the content from `templates/AGENTS.md` (the `(example)` items under "high-frequency rules" are placeholders — replace them with your own most painful mistakes):

```markdown
## Meta-rule: check the mistake book before you write (prevention first)
- Before every shell/PowerShell command, code edit, or package install, check the rulebook
  for a matching rule; if one matches, use the preventive form — do NOT wait for an error.
- After a command failure / non-zero exit / tool error: record or extend a rule in the
  "DON'T X — because Y" format. No long post-mortems.
```

**Step 2 — Create your mistake book**

Copy `templates/lessons.seed.md` (a seed library: 9 real rules with applicability notes) to `lessons.md` and drop the domains you don't use. A blank template lives at `templates/lessons.md`.

**Step 3 — On your first error, record your first rule**

Append in this format (and on a repeated error, **extend the existing entry** instead of adding a new one):

```markdown
- [bash/PowerShell] DON'T embed `$_` inside a `powershell -Command "..."` string in bash
  — because bash expands `$_` and corrupts the command (exit 1);
  write a `.ps1` script instead, or wrap the whole string in single quotes
```

---

## Usage cheat sheet

| Situation | Action |
|---|---|
| About to run a command / write code / install | **Check** the rulebook first; switch to the preventive form if a rule matches |
| Command failed / non-zero exit | **Record** a rule: "DON'T X — because Y" |
| User corrects you directly | **Record** it (don't wait for an error) |
| Same error a second time | **Extend** that entry (add example/variant), don't create a new one |
| Rulebook bloated / stale | **Prune**: merge duplicates, drop obsolete entries |

---

## Four design decisions (summary)

1. **Rule format, not post-mortem**: `DON'T X — because Y` — one line, scannable, token-cheap; the fix procedure is dropped by default, keeping only the reusable preventive form plus a one-line root cause
2. **Standing instruction > passive retrieval**: memory retrieval has nothing to search on *before* you write — prevention must be triggered by a meta-rule that lives in context every turn. This is the key difference from all lessons/memory approaches
3. **Two-layer isolation**: the standing file holds only the meta-rule + ≤5 high-frequency rules (to avoid bloat and rule-blindness); the full rulebook lives in memory, retrieved on demand
4. **Incremental + pruning**: three recording triggers; merge repeated errors into one entry; prune regularly to keep the list healthy

Full rationale: [docs/principle.md](docs/principle.md).

---

## Real incidents (from running this method)

| Domain | Rule | Source |
|---|---|---|
| bash | DON'T `ls` a possibly-missing path — exit 2 fails the whole command | probing a missing dir |
| bash/Windows | DON'T pass MSYS paths (`/tmp`) to Windows programs — reports success but writes nothing | batch generation |
| bash/PowerShell | DON'T embed `$_` in a PowerShell command inside bash double quotes — the command breaks | registry query |
| browser automation | DON'T pause >2-3s between operations — the daemon reaps idle sessions | BrowserAct |

> ⚠️ **Honest note on validation**: the table above is anecdotal, not quantitative evidence. Since **2026-08-06** this repo records three event types (HIT / INCIDENT / RULE) per the protocol in [docs/validation.md](docs/validation.md); the first quantitative report (hit rate, prevented count, regression rate, estimated token savings) will be backfilled after 4 weeks. Log: [data/validation-log.md](data/validation-log.md).

---

## Comparison with other approaches (full: [docs/comparison.md](docs/comparison.md))

| Approach | Trigger | Pre-flight | Storage | Notes |
|---|---|---|---|---|
| **WrongBook (this)** | standing + retrieval | ✅ | instruction file + memory/lessons.md | zero-dependency, platform-agnostic, pure instructions |
| Claude Code CLAUDE.md rules | standing | ✅ | single instruction file | similar idea; rules share the file with instructions — mind the size |
| Lessons-DB skills (e.g. self-improvement-loop) | passive retrieval | partial | external DB | suits team-level knowledge bases; needs maintenance |
| Post-hoc aggregators (e.g. graphify) | end-of-session | partial | generated LESSONS.md | suits project retrospectives |
| Memory frameworks (mem0 / MemGPT / Letta) | semantic retrieval | partial | vector DB | memory infrastructure, different positioning; suits large-scale memory needs |

---

## Repository layout

```
wrongbook/
├── README.md                  # This document (Chinese)
├── README.en.md               # English version
├── LICENSE                    # MIT
├── templates/
│   ├── AGENTS.md              # Generic standing-instruction template (any agent)
│   ├── lessons.md             # Blank rulebook template
│   ├── lessons.seed.md        # Seed library: 9 real rules (recommended start)
│   └── REASONIX.md            # Reasonix-specific variant (memory-tool usage)
├── docs/
│   ├── principle.md           # Why pre-flight beats post-hoc
│   ├── implementation.md      # Platform adaptation, maintenance
│   ├── comparison.md          # Deep comparison with other approaches
│   └── validation.md          # Metrics & recording protocol
├── data/
│   └── validation-log.md      # Validation log (since 2026-08-06)
├── scripts/
│   └── validate_lessons.py    # Rulebook format linter (meta-prevention)
└── .github/
    └── workflows/lint.yml     # CI: validate rulebook format on push/PR
```

---

## License

MIT — see [LICENSE](LICENSE). PRs adding adapters for other platforms are welcome.
