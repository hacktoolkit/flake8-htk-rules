"""Debugger prevention checks."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field


DB100 = "DB100 do not commit debugger imports"
DB101 = "DB101 do not commit debugger calls"

DEBUGGER_MODULES = {"pdb", "ipdb", "pudb", "wdb"}
DEBUGGER_METHODS = {
    "set_trace",
    "post_mortem",
    "pm",
    "runcall",
    "runctx",
}


@dataclass
class DebuggerState:
    module_aliases: set[str] = field(default_factory=set)
    call_aliases: set[str] = field(default_factory=set)


def check_import(
    node: ast.Import,
    state: DebuggerState,
) -> list[tuple[ast.AST, str]]:
    violations = []
    for alias in node.names:
        root_module = alias.name.split(".", 1)[0]
        if root_module in DEBUGGER_MODULES:
            state.module_aliases.add(alias.asname or root_module)
            violations.append((alias, DB100))
    return violations


def check_import_from(
    node: ast.ImportFrom,
    state: DebuggerState,
) -> list[tuple[ast.AST, str]]:
    root_module = (node.module or "").split(".", 1)[0]
    if root_module not in DEBUGGER_MODULES:
        return []

    violations = []
    for alias in node.names:
        violations.append((alias, DB100))
        if alias.name == "*":
            state.call_aliases.update(DEBUGGER_METHODS)
        elif alias.name in DEBUGGER_METHODS:
            state.call_aliases.add(alias.asname or alias.name)
    return violations


def check_call(
    node: ast.Call,
    state: DebuggerState,
) -> list[tuple[ast.AST, str]]:
    name = _call_name(node.func)
    if _is_debugger_call(name, state):
        return [(node, DB101)]
    return []


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent_name = _call_name(node.value)
        if parent_name:
            return f"{parent_name}.{node.attr}"
        return node.attr
    return ""


def _is_debugger_call(name: str, state: DebuggerState) -> bool:
    if name == "breakpoint" or name in state.call_aliases:
        return True
    if "." not in name:
        return False

    module_name, method_name = name.rsplit(".", 1)
    root_module = module_name.split(".", 1)[0]
    return (
        method_name in DEBUGGER_METHODS
        and root_module in DEBUGGER_MODULES | state.module_aliases
    )
