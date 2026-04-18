# flake8-htk-rules

Hacktoolkit Flake8 rules for catching code that should not ship.

## Installation

```bash
pip install flake8-htk-rules
```

For local development:

```bash
python -m pip install -e ".[dev]"
python -m unittest discover -s tests -v
```

## Rules

| Code | Description |
| --- | --- |
| `HTK100` | Do not commit `print(...)` calls. |
| `HTK101` | Do not commit debugger traps such as `breakpoint()` or `pdb.set_trace()`. |
| `HTK102` | Do not commit HTK debug helper calls such as `fdb(...)` or `slack_debug(...)`. |

## Flake8 Configuration

```ini
[flake8]
select = HTK
```

Or combine with existing checks:

```ini
[flake8]
extend-select = HTK
```

## Development

The plugin is implemented as a single AST checker registered through the
`flake8.extension` entry point. Add new checks in
`src/flake8_htk_rules/checks.py` and cover them in `tests/`.

Run the test suite without installing the package:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```
