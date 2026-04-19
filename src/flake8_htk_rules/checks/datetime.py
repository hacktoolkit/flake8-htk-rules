"""Datetime clarity checks."""

from __future__ import annotations

import ast


DT100 = (
    "DT100 use 'import datetime' instead of "
    "'from datetime import datetime'"
)
DT101 = (
    "DT101 use 'import datetime' instead of "
    "'from datetime import date'"
)
DT102 = (
    "DT102 use 'import datetime' instead of "
    "'from datetime import timedelta'"
)

DATETIME_IMPORT_MESSAGES = {
    "datetime": DT100,
    "date": DT101,
    "timedelta": DT102,
}


def check_import_from(node: ast.ImportFrom) -> list[tuple[ast.AST, str]]:
    if node.module != "datetime" or node.level != 0:
        return []

    violations = []
    for alias in node.names:
        message = DATETIME_IMPORT_MESSAGES.get(alias.name)
        if message is not None:
            violations.append((alias, message))
    return violations
