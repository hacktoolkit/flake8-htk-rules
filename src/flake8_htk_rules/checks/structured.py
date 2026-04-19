"""Structured programming checks."""

from __future__ import annotations

import ast
import os
from fnmatch import fnmatch


SP100 = (
    "SP100 function '{name}' has {count} return statements; "
    "prefer a single return per function"
)
SP101 = (
    "SP101 return value should be a simple variable, attribute, or literal, "
    "not a complex expression"
)


def should_check_file(
    filename: str,
    structured_programming_files: tuple[str, ...],
) -> bool:
    if not structured_programming_files:
        return False

    relative_path = os.path.relpath(filename, os.getcwd()).replace(os.sep, "/")
    return any(
        fnmatch(relative_path, pattern)
        for pattern in structured_programming_files
    )


def check_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[tuple[ast.AST, str]]:
    violations: list[tuple[ast.AST, str]] = []
    returns = _collect_returns(node)

    if len(returns) > 1:
        violations.append(
            (node, SP100.format(name=node.name, count=len(returns)))
        )

    for return_node in returns:
        if not _is_simple_return_value(return_node.value):
            violations.append((return_node, SP101))

    return violations


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
