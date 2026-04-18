# Initial Rule Set

## Context

The repo is intended to be a standalone Flake8 plugin for Hacktoolkit rules.
The original `accounts-django` extraction source was not available in the
local workspace, and GitHub access from this runtime was blocked by DNS.

## Options

- Wait for the source repo to become available.
- Create a real plugin package with conservative initial checks and tests.

## Decision

Create a standalone package with a modern `pyproject.toml`, `src/` layout,
Flake8 entry point, CI, and an initial HTK rule set focused on code that should
not ship: `print`, debugger traps, and HTK debug helpers.

## Action Items

- Add the exact extracted `accounts-django` rules once that source is reachable.
- Push this package to `hacktoolkit/flake8-htk-rules` when GitHub access is
  available.

