# WrongBook · The Pre-flight Mistake Book for AI Agents

[English](README.en.md) | [中文](README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/rumilhz/wrongbook/actions/workflows/lint.yml/badge.svg)](https://github.com/rumilhz/wrongbook/actions/workflows/lint.yml)

> Turn the waste of "error → diagnose → fix" into a rulebook your agent reads **before it acts**. Think of it as a teacher for your agent — the rules are in front of it before it runs commands, writes code, or installs packages.

## ✨ Core Features

- 🛡️ **Pre-flight prevention** — check the rules before writing; if one matches, write differently and the error loop never happens
- 📋 **Rule format, not post-mortem** — `DON'T X — because Y`: one line, scannable, token-cheap
- 🔔 **Standing trigger** — the meta-rule lives in context every turn; no "remember to check afterwards"
- 🧱 **Two-layer isolation** — the standing file holds only the meta-rule + ≤5 top rules; the full rulebook lives in memory
- 🌱 **Incremental growth** — three recording triggers (errors / user corrections / external cases); repeated errors merge into one entry
- 📊 **Measurable** — HIT / INCIDENT / RULE events are logged; the [first quantitative report](#2026-09-first-validation-report-cycle-2026-08-06--09-02) was backfilled on 2026-09-02

## Core Stack

| Layer | Technology |
|---|---|
| Standing instructions | `AGENTS.md` / `CLAUDE.md` / `REASONIX.md` (auto-loaded every relevant turn) |
| Memory | platform long-term memory / `lessons.md` (retrieved on demand) |
| Lint | `scripts/validate_lessons.py` (rulebook format checker) |
| CI | GitHub Actions (validate on push / PR) |

## Architecture

```
┌───────────────────────────────────────┐
│  Standing instructions (in context    │
│  every turn, cache-stable)            │
│    Meta-rule: check the rulebook      │
│    before you write                   │
└──────────────────┬────────────────────┘
                   │ meta-rule triggers
┌──────────────────▼────────────────────┐
│  Rulebook (memory / lessons.md,       │
│  retrieved on demand)                 │
│    DON'T X — because Y                │
│    (hundreds of rules, categorized)   │
└───────────────────────────────────────┘
```

## Quick start (3 steps, ~3 minutes)

**Step 1 — Create the standing instruction file**

Put an `AGENTS.md` in your workspace (Claude Code: `CLAUDE.md`; Reasonix: `REASONIX.md`). Copy the content from `templates/AGENTS.md` (the `(example)` items under "high-frequency rules" are placeholders — replace them with your own most painful mistakes):

```markdown
## Meta-rule: check the mistake book before you write (prevention first)
- Before every tool/command call, code edit, package install, or API call, check the rulebook
  domains for the action type (commands→[bash]/[shell]; code→[lang]/[encoding]; install→[deps];
  API→[tool]/[quota]…); if a rule matches, use the preventive form — do NOT wait for an error.
- **Visible check**: before each shell tool call, print a line `[rulebook] no hit / hit X→use Y`.
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

## Usage cheat sheet

| Situation | Action |
|---|---|
| About to run a command / write code / install | **Check** the rulebook first; switch to the preventive form if a rule matches |
| Command failed / non-zero exit | **Record** a rule: "DON'T X — because Y" |
| User corrects you directly | **Record** it (don't wait for an error) |
| Same error a second time | **Extend** that entry (add example/variant), don't create a new one |
| Rulebook bloated / stale | **Prune**: merge duplicates, drop obsolete entries |

## Four design decisions (summary)

1. **Rule format, not post-mortem**: `DON'T X — because Y` — one line, scannable, token-cheap; the fix procedure is dropped by default, keeping only the reusable preventive form plus a one-line root cause
2. **Standing instruction > passive retrieval**: memory retrieval has nothing to search on *before* you write — prevention must be triggered by a meta-rule that lives in context every turn. This is the key difference from all lessons/memory approaches
3. **Two-layer isolation**: the standing file holds only the meta-rule + ≤5 high-frequency rules (to avoid bloat and rule-blindness); the full rulebook lives in memory, retrieved on demand
4. **Incremental + pruning**: three recording triggers; merge repeated errors into one entry; prune regularly to keep the list healthy

Full rationale: [docs/principle.md](docs/principle.md).

## Real incidents (from running this method)

| Domain | Rule | Source |
|---|---|---|
| bash | DON'T `ls` a possibly-missing path — exit 2 fails the whole command | probing a missing dir |
| bash/Windows | DON'T pass MSYS paths (`/tmp`) to Windows programs — reports success but writes nothing | batch generation |
| bash/PowerShell | DON'T embed `$_` in a PowerShell command inside bash double quotes — the command breaks | registry query |
| browser automation | DON'T pause >2-3s between operations — the daemon reaps idle sessions | BrowserAct |

## 2026-09 First Validation Report (cycle 2026-08-06 ~ 09-02, backfilled ahead of 09-06)

| Metric | Value | Note |
|---|---|---|
| Rulebook size | 9 → **76** | net +67 (incl. dedup) |
| HIT | **3** | heredoc delimiter / path-exists check / `$_` single-quote |
| Prevented | **3** | est. savings ≈ 3 × 3 = 9× single-fix cost |
| INCIDENT | **6** | 3 on 08-06 + 3 on 08-13 |
| Regressions | **2** (rate 2/(3+2) = **40%**) | "no-exemption for read-only cmds" and "annotation text into command" each recurred once |
| RULE records | +3 new / +3 extend / 1 trim / 1 range-batch | — |

> ⚠️ **Honest notes**:
> - Real data recorded per the protocol in [docs/validation.md](docs/validation.md) since 2026-08-06; log: [data/validation-log.md](data/validation-log.md).
> - **Hit rate (H/T) is not reported**: the retrieval count T was not recorded per turn.
> - 08-14 ~ 09-02 cross-session sediment was not attributed per day (the validation log lagged) and is counted as a range batch; this resulted from low precipitation visibility.
> - **Next step**: the check step runs reliably (`[错题本核对]` appears frequently); the sediment step lacked visibility → fixed on 2026-09-02 with a **precipitation ritual** (mandatory `[沉淀]` line after failures) plus **add-lesson.py** one-command landing (append full text + log + sync copy). The next cycle will verify whether the regression rate drops to zero.

## Comparison with other approaches (full: [docs/comparison.md](docs/comparison.md))

| Approach | Trigger | Pre-flight | Storage | Notes |
|---|---|---|---|---|
| **WrongBook (this)** | standing + retrieval | ✅ | instruction file + memory/lessons.md | zero-dependency, platform-agnostic, pure instructions |
| Claude Code CLAUDE.md rules | standing | ✅ | single instruction file | similar idea; rules share the file with instructions — mind the size |
| Lessons-DB skills (e.g. self-improvement-loop) | passive retrieval | partial | external DB | suits team-level knowledge bases; needs maintenance |
| Post-hoc aggregators (e.g. graphify) | end-of-session | partial | generated LESSONS.md | suits project retrospectives |
| Memory frameworks (mem0 / MemGPT / Letta) | semantic retrieval | partial | vector DB | memory infrastructure, different positioning; suits large-scale memory needs |

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

## License

MIT — see [LICENSE](LICENSE). PRs adding adapters for other platforms are welcome.
