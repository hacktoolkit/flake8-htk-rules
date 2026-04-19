"""Naming precision checks."""

from __future__ import annotations

import ast


NM100 = (
    "NM100 avoid get_ function prefix; choose a more precise verb "
    "such as build_, calculate_, extract_, fetch_, look_up_, "
    "retrieve_, format_, or transform_"
)


def check_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[tuple[ast.AST, str]]:
    if node.name.startswith("get_"):
        return [(node, NM100)]
    return []
