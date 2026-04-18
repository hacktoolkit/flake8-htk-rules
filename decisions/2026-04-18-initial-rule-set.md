# Initial Rule Set

## Context

The repo is intended to be a standalone Flake8 plugin for Hacktoolkit rules.
Linear task `JON-261` points at the `accounts-django` seed commit
`27b9a788a25117fbdb14158704928564d5370337`, whose custom checker introduced
structured programming rules.

The Linear comments also call out Jonathan's datetime clarity preference from
his blog post on fully qualified datetime usage. Follow-up Slack feedback added
explicit debugger prevention and the `get_` naming rule from Jonathan's writing
on vague function prefixes.

## Options

- Keep the first placeholder debug-output-only rule set.
- Extract the `accounts-django` structured programming checker, then add the
  task/comment-backed datetime, debugger, and naming rules.

## Decision

Ship the task-backed rule set and keep debugger prevention as a first-class rule
family:

- `SP100` flags multiple returns in a configured function.
- `SP101` flags complex return expressions in configured files.
- `DT100` flags `from datetime import datetime`.
- `DT101` flags `from datetime import date`.
- `DT102` flags `from datetime import timedelta`.
- `DB100` flags debugger imports.
- `DB101` flags debugger calls.
- `NM100` flags functions and methods named with the vague `get_` prefix.

Structured programming checks are gated by `--structured-programming-files`,
matching the original accounts-django rollout pattern. Datetime, debugger, and
naming checks are always available when their `DT`, `DB`, or `NM` rules are
selected.

## Action Items

- Add more rule families from Jonathan's writing only after the current SP, DT,
  DB, and NM rules are stable.
- Consider a future ESLint package separately if real JavaScript rules emerge.
