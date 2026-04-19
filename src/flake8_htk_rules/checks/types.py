"""Shared types for Hacktoolkit checks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Violation:
    line: int
    column: int
    message: str
