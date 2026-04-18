# Initial Rule Set

## Context

The repo is intended to be a standalone Flake8 plugin for Hacktoolkit rules.
Linear task `JON-261` points at the `accounts-django` seed commit
`27b9a788a25117fbdb14158704928564d5370337`, whose custom checker introduced
structured programming rules.

The Linear comments also call out Jonathan's datetime clarity preference from
his blog post on fully qualified datetime usage.

## Options

- Preserve the first placeholder debug-output checks.
- Extract the `accounts-django` structured programming checker and add the
  datetime import rules from the Linear task comments.

## Decision

Ship the task-backed rule set instead of the placeholder debug checks:

- `SP100` flags multiple returns in a configured function.
- `SP101` flags complex return expressions in configured files.
- `DT100` flags `from datetime import datetime`.
- `DT101` flags `from datetime import date`.
- `DT102` flags `from datetime import timedelta`.
- `DB100` flags debugger imports.
- `DB101` flags debugger calls.
- `NM100` flags functions and methods named with the vague `get_` prefix.

Structured programming checks are gated by `--structured-programming-files`,
matching the original accounts-django rollout pattern. Datetime checks are
always available when their `DT`, `DB`, or `NM` rules are selected.

## Action Items

- Add more rule families from Jonathan's writing only after the first extracted
  SP/DT set is stable.
- Consider a future ESLint package separately if real JavaScript rules emerge.
