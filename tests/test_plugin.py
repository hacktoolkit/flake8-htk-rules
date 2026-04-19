from __future__ import annotations

import ast
import unittest
from types import SimpleNamespace

from flake8_htk_rules import Plugin

SP100_SAMPLE = (
    "SP100 function 'sample' has 2 return statements; "
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


def run_plugin(
    source: str,
    *,
    filename: str = "accounts/services.py",
    structured_programming_files: list[str] | None = None,
) -> list[str]:
    Plugin.parse_options(
        SimpleNamespace(
            structured_programming_files=structured_programming_files or [],
        )
    )
    tree = ast.parse(source)
    return [message for _, _, message, _ in Plugin(tree, filename).run()]


class PluginTest(unittest.TestCase):
    def test_flags_multiple_returns_for_configured_file(self) -> None:
        messages = run_plugin(
            """
def sample(value):
    if value:
        return value
    return None
""",
            structured_programming_files=["accounts/services.py"],
        )

        self.assertEqual(messages, [SP100_SAMPLE])

    def test_flags_complex_return_expression_for_configured_file(self) -> None:
        messages = run_plugin(
            """
def sample(value):
    return value + 1
""",
            structured_programming_files=["accounts/services.py"],
        )

        self.assertEqual(messages, [SP101])

    def test_allows_single_simple_return_for_configured_file(self) -> None:
        messages = run_plugin(
            """
def sample(value):
    result = value + 1
    return result
""",
            structured_programming_files=["accounts/services.py"],
        )

        self.assertEqual(messages, [])

    def test_allows_literal_return_values_for_configured_file(self) -> None:
        messages = run_plugin(
            """
def sample():
    return {"ok": [1, 2, (3, -4)]}
""",
            structured_programming_files=["accounts/services.py"],
        )

        self.assertEqual(messages, [])

    def test_flags_container_return_with_nonliteral_values(self) -> None:
        messages = run_plugin(
            """
def sample(value):
    return [value]
""",
            structured_programming_files=["accounts/services.py"],
        )

        self.assertEqual(messages, [SP101])

    def test_skips_structured_programming_for_unconfigured_file(self) -> None:
        messages = run_plugin(
            """
def sample(value):
    if value:
        return value
    return value + 1
""",
            filename="accounts/forms.py",
            structured_programming_files=["accounts/services.py"],
        )

        self.assertEqual(messages, [])

    def test_ignores_returns_inside_nested_functions(self) -> None:
        messages = run_plugin(
            """
def outer(value):
    def inner():
        return value
    return value
""",
            structured_programming_files=["accounts/services.py"],
        )

        self.assertEqual(messages, [])

    def test_flags_datetime_datetime_import(self) -> None:
        messages = run_plugin("from datetime import datetime\n")

        self.assertEqual(messages, [DT100])

    def test_flags_datetime_date_import(self) -> None:
        messages = run_plugin("from datetime import date\n")

        self.assertEqual(messages, [DT101])

    def test_flags_datetime_timedelta_import(self) -> None:
        messages = run_plugin("from datetime import timedelta\n")

        self.assertEqual(messages, [DT102])

    def test_allows_fully_qualified_datetime_import(self) -> None:
        messages = run_plugin("import datetime\n")

        self.assertEqual(messages, [])

    def test_flags_multiple_datetime_imports(self) -> None:
        messages = run_plugin(
            "from datetime import date, datetime, timedelta\n"
        )

        self.assertEqual(messages, [DT101, DT100, DT102])

    def test_flags_builtin_breakpoint(self) -> None:
        messages = run_plugin(
            """
def handler():
    breakpoint()
"""
        )

        self.assertEqual(messages, [DB101])

    def test_flags_debugger_module_import_and_call(self) -> None:
        messages = run_plugin(
            """
import pdb
import ipdb as debugger

def handler():
    pdb.set_trace()
    debugger.set_trace()
"""
        )

        self.assertEqual(messages, [DB100, DB100, DB101, DB101])

    def test_flags_imported_debugger_call_alias(self) -> None:
        messages = run_plugin(
            """
from pdb import set_trace
from ipdb import set_trace as trace

def handler():
    set_trace()
    trace()
"""
        )

        self.assertEqual(messages, [DB100, DB100, DB101, DB101])

    def test_flags_debugger_wildcard_imported_call(self) -> None:
        messages = run_plugin(
            """
from pdb import *

def handler():
    set_trace()
"""
        )

        self.assertEqual(messages, [DB100, DB101])

    def test_flags_get_prefixed_function_name(self) -> None:
        messages = run_plugin(
            """
def get_total(items):
    return sum(items)
"""
        )

        self.assertEqual(messages, [NM100])

    def test_flags_get_prefixed_async_function_name(self) -> None:
        messages = run_plugin(
            """
async def get_story_details(story_id):
    return story_id
"""
        )

        self.assertEqual(messages, [NM100])

    def test_allows_non_get_prefixed_function_name(self) -> None:
        messages = run_plugin(
            """
def fetch_story_details(story_id):
    return story_id
"""
        )

        self.assertEqual(messages, [])


if __name__ == "__main__":
    unittest.main()
