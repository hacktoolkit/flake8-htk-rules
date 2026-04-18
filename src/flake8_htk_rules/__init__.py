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
    structured_programming_files: tuple[str, ...] = ()

    def __init__(self, tree: ast.AST, filename: str = "<unknown>") -> None:
        self.tree = tree
        self.filename = filename

    @classmethod
    def add_options(cls, parser) -> None:
        parser.add_option(
            "--structured-programming-files",
            parse_from_config=True,
            comma_separated_list=True,
            default=[],
            help=(
                "Comma-separated file globs for structured programming "
                "checks."
            ),
        )

    @classmethod
    def parse_options(cls, options) -> None:
        cls.structured_programming_files = tuple(
            pattern.strip()
            for pattern in getattr(options, "structured_programming_files", [])
            if pattern.strip()
        )

    def run(self) -> Iterator[tuple[int, int, str, type["Plugin"]]]:
        visitor = HtkVisitor(
            filename=self.filename,
            structured_programming_files=self.structured_programming_files,
        )
        visitor.visit(self.tree)
        for violation in visitor.violations:
            yield (
                violation.line,
                violation.column,
                violation.message,
                type(self),
            )


__all__ = ["Plugin", "__version__"]
