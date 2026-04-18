"""Flake8 entry point for Hacktoolkit rules."""

from __future__ import annotations

import ast
from collections.abc import Iterator

from .checks import HtkVisitor

__version__ = "0.1.0"


class Plugin:
    """Flake8 AST plugin entry point."""

    name = "flake8-htk-rules"
    version = __version__

    def __init__(self, tree: ast.AST, filename: str = "<unknown>") -> None:
        self.tree = tree
        self.filename = filename

    def run(self) -> Iterator[tuple[int, int, str, type["Plugin"]]]:
        visitor = HtkVisitor()
        visitor.visit(self.tree)
        for violation in visitor.violations:
            yield (
                violation.line,
                violation.column,
                violation.message,
                type(self),
            )


__all__ = ["Plugin", "__version__"]

