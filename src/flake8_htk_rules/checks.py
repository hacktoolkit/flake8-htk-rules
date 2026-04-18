"""AST checks for Hacktoolkit Flake8 rules."""

from __future__ import annotations

import ast
from dataclasses import dataclass


HTK100 = "HTK100 do not commit print() calls"
HTK101 = "HTK101 do not commit debugger traps"
HTK102 = "HTK102 do not commit HTK debug helper calls"

DEBUG_MODULES = {"pdb", "ipdb", "pudb", "wdb"}
DEBUG_METHODS = {"set_trace", "post_mortem", "pm", "runcall", "runctx"}
HTK_DEBUG_HELPERS = {
    "fdb",
    "fdb_json",
    "fdebug",
    "fdebug_json",
    "slack_debug",
    "slack_debug_json",
}


@dataclass(frozen=True, order=True)
class Violation:
    line: int
    column: int
    message: str


class HtkVisitor(ast.NodeVisitor):
    """Collect HTK rule violations from a Python AST."""

    def __init__(self) -> None:
        self.violations: list[Violation] = []
        self._debug_aliases: set[str] = set()
        self._helper_aliases: set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            module_name = alias.name.split(".", 1)[0]
            if module_name in DEBUG_MODULES:
                self._debug_aliases.add(alias.asname or module_name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module_name = (node.module or "").split(".", 1)[0]
        if module_name in DEBUG_MODULES:
            for alias in node.names:
                if alias.name in DEBUG_METHODS or alias.name == "*":
                    self._debug_aliases.add(alias.asname or alias.name)
        if module_name == "htk":
            for alias in node.names:
                if alias.name in HTK_DEBUG_HELPERS or alias.name == "*":
                    self._helper_aliases.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        name = _call_name(node.func)
        if name == "print":
            self._add(node, HTK100)
        elif _is_debugger_call(name, self._debug_aliases):
            self._add(node, HTK101)
        elif _is_htk_debug_helper(name, self._helper_aliases):
            self._add(node, HTK102)
        self.generic_visit(node)

    def _add(self, node: ast.AST, message: str) -> None:
        self.violations.append(
            Violation(
                line=getattr(node, "lineno", 1),
                column=getattr(node, "col_offset", 0),
                message=message,
            )
        )


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent_name = _call_name(node.value)
        if parent_name:
            return f"{parent_name}.{node.attr}"
        return node.attr
    return ""


def _is_debugger_call(name: str, aliases: set[str]) -> bool:
    if name == "breakpoint":
        return True
    if name in aliases:
        return True
    if "." not in name:
        return False
    module_name, method_name = name.rsplit(".", 1)
    return module_name in DEBUG_MODULES | aliases and method_name in DEBUG_METHODS


def _is_htk_debug_helper(name: str, aliases: set[str]) -> bool:
    if name in HTK_DEBUG_HELPERS | aliases:
        return True
    if "." not in name:
        return False
    _, method_name = name.rsplit(".", 1)
    return method_name in HTK_DEBUG_HELPERS

