"""Check orchestration for Hacktoolkit Flake8 rules."""

from __future__ import annotations

import ast

from . import datetime as datetime_checks
from . import debugger, naming, structured
from .types import Violation


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
        self._debugger_state = debugger.DebuggerState()

    def visit_Import(self, node: ast.Import) -> None:
        for violation_node, message in debugger.check_import(
            node,
            self._debugger_state,
        ):
            self._add(violation_node, node, message)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for violation_node, message in datetime_checks.check_import_from(node):
            self._add(violation_node, node, message)
        for violation_node, message in debugger.check_import_from(
            node,
            self._debugger_state,
        ):
            self._add(violation_node, node, message)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        for violation_node, message in debugger.check_call(
            node,
            self._debugger_state,
        ):
            self._add(violation_node, node, message)
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
        for violation_node, message in naming.check_function(node):
            self._add(violation_node, node, message)

        if not structured.should_check_file(
            self.filename,
            self.structured_programming_files,
        ):
            return

        for violation_node, message in structured.check_function(node):
            self._add(violation_node, node, message)

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


__all__ = ["HtkVisitor", "Violation"]
