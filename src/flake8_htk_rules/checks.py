"""AST checks for Hacktoolkit Flake8 rules."""

from __future__ import annotations

import ast
import os
from dataclasses import dataclass
from fnmatch import fnmatch


SP100 = (
    "SP100 function '{name}' has {count} return statements; "
    "prefer a single return per function"
)
SP101 = (
    "SP101 return value should be a simple variable, attribute, or literal, "
    "not a complex expression"
)
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
DB100 = "DB100 do not commit debugger imports"
DB101 = "DB101 do not commit debugger calls"
NM100 = (
    "NM100 avoid get_ function prefix; choose a more precise verb "
    "such as build_, calculate_, extract_, fetch_, look_up_, "
    "retrieve_, format_, or transform_"
)

DATETIME_IMPORT_MESSAGES = {
    "datetime": DT100,
    "date": DT101,
    "timedelta": DT102,
}
DEBUGGER_MODULES = {"pdb", "ipdb", "pudb", "wdb"}
DEBUGGER_METHODS = {
    "set_trace",
    "post_mortem",
    "pm",
    "runcall",
    "runctx",
}


@dataclass(frozen=True, order=True)
class Violation:
    line: int
    column: int
    message: str


class HtkVisitor(ast.NodeVisitor):
    """Collect Hacktoolkit rule violations from a Python AST."""

    def __init__(
        self,
        *,
        filename: str,
        structured_programming_files: tuple[str, ...] = (),
    ) -> None:
        self.filename = filename
        self.structured_programming_files = structured_programming_files
        self.violations: list[Violation] = []
        self._debugger_module_aliases: set[str] = set()
        self._debugger_call_aliases: set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root_module = alias.name.split(".", 1)[0]
            if root_module in DEBUGGER_MODULES:
                self._debugger_module_aliases.add(alias.asname or root_module)
                self._add(alias, node, DB100)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module == "datetime" and node.level == 0:
            for alias in node.names:
                message = DATETIME_IMPORT_MESSAGES.get(alias.name)
                if message is not None:
                    self._add(alias, node, message)

        root_module = (node.module or "").split(".", 1)[0]
        if root_module in DEBUGGER_MODULES:
            for alias in node.names:
                self._add(alias, node, DB100)
                if alias.name == "*":
                    self._debugger_call_aliases.update(DEBUGGER_METHODS)
                elif alias.name in DEBUGGER_METHODS:
                    self._debugger_call_aliases.add(alias.asname or alias.name)

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        name = _call_name(node.func)
        if _is_debugger_call(
            name,
            module_aliases=self._debugger_module_aliases,
            call_aliases=self._debugger_call_aliases,
        ):
            self._add(node, node, DB101)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def _check_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> None:
        if node.name.startswith("get_"):
            self._add(node, node, NM100)

        if not self._should_run_structured_programming_checks():
            return

        returns = _collect_returns(node)
        if len(returns) > 1:
            self._add(
                node,
                node,
                SP100.format(name=node.name, count=len(returns)),
            )

        for return_node in returns:
            if not _is_simple_return_value(return_node.value):
                self._add(return_node, return_node, SP101)

    def _should_run_structured_programming_checks(self) -> bool:
        if not self.structured_programming_files:
            return False

        relative_path = os.path.relpath(self.filename, os.getcwd()).replace(
            os.sep,
            "/",
        )
        return any(
            fnmatch(relative_path, pattern)
            for pattern in self.structured_programming_files
        )

    def _add(self, node: ast.AST, fallback: ast.AST, message: str) -> None:
        self.violations.append(
            Violation(
                line=getattr(node, "lineno", getattr(fallback, "lineno", 1)),
                column=getattr(
                    node,
                    "col_offset",
                    getattr(fallback, "col_offset", 0),
                ),
                message=message,
            )
        )


def _collect_returns(
    function_node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[ast.Return]:
    collector = _ReturnCollector(function_node)
    collector.visit(function_node)
    return collector.returns


def _is_simple_return_value(value: ast.expr | None) -> bool:
    return value is None or isinstance(
        value,
        (ast.Name, ast.Attribute, ast.Constant),
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


def _is_debugger_call(
    name: str,
    *,
    module_aliases: set[str],
    call_aliases: set[str],
) -> bool:
    if name == "breakpoint" or name in call_aliases:
        return True
    if "." not in name:
        return False

    module_name, method_name = name.rsplit(".", 1)
    root_module = module_name.split(".", 1)[0]
    return (
        method_name in DEBUGGER_METHODS
        and root_module in DEBUGGER_MODULES | module_aliases
    )


class _ReturnCollector(ast.NodeVisitor):
    def __init__(self, root: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self.root = root
        self.returns: list[ast.Return] = []

    def visit_Return(self, node: ast.Return) -> None:
        self.returns.append(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node is self.root:
            self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if node is self.root:
            self.generic_visit(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        return
