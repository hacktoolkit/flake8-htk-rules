# flake8-htk-rules

Hacktoolkit Flake8 rules for structured Python code and datetime clarity.

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
| `SP100` | Functions in configured files should prefer a single return statement. |
| `SP101` | Return values in configured files should be simple variables, attributes, literals, or bare returns. |
| `DT100` | Use `import datetime` instead of `from datetime import datetime`. |
| `DT101` | Use `import datetime` instead of `from datetime import date`. |
| `DT102` | Use `import datetime` instead of `from datetime import timedelta`. |
| `DB100` | Do not commit debugger imports such as `import pdb`. |
| `DB101` | Do not commit debugger calls such as `breakpoint()` or `pdb.set_trace()`. |

## Flake8 Configuration

Enable the structured-programming and datetime rules:

```ini
[flake8]
select = SP,DT,DB
structured-programming-files =
    accounts/services.py
    accounts/view_helpers.py
    accounts/views.py
```

Or combine with existing checks:

```ini
[flake8]
extend-select = SP,DT,DB,DB
structured-programming-files =
    accounts/services.py
    accounts/view_helpers.py
    accounts/views.py
```

The `SP` rules are gated by `structured-programming-files` so teams can roll them
out on a targeted set of modules. The `DT` and `DB` rules are always active when
selected.

## Development

The plugin is implemented as a single AST checker registered through the
`flake8.extension` entry point. Add new checks in
`src/flake8_htk_rules/checks.py` and cover them in `tests/`.

Run the test suite without installing the package:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```
