from __future__ import annotations

import ast
import unittest

from flake8_htk_rules import Plugin


def run_plugin(source: str) -> list[str]:
    tree = ast.parse(source)
    return [message for _, _, message, _ in Plugin(tree).run()]


class PluginTest(unittest.TestCase):
    def test_allows_normal_code(self) -> None:
        messages = run_plugin(
            """
def greet(name):
    return f"hello {name}"
"""
        )

        self.assertEqual(messages, [])

    def test_reports_print_calls(self) -> None:
        messages = run_plugin(
            """
def greet(name):
    print(name)
"""
        )

        self.assertEqual(messages, ["HTK100 do not commit print() calls"])

    def test_reports_builtin_breakpoint(self) -> None:
        messages = run_plugin(
            """
def handler():
    breakpoint()
"""
        )

        self.assertEqual(messages, ["HTK101 do not commit debugger traps"])

    def test_reports_debugger_module_calls(self) -> None:
        messages = run_plugin(
            """
import pdb
import ipdb as debugger

def handler():
    pdb.set_trace()
    debugger.set_trace()
"""
        )

        self.assertEqual(
            messages,
            [
                "HTK101 do not commit debugger traps",
                "HTK101 do not commit debugger traps",
            ],
        )

    def test_reports_imported_debugger_calls(self) -> None:
        messages = run_plugin(
            """
from pdb import set_trace
from ipdb import set_trace as trace

def handler():
    set_trace()
    trace()
"""
        )

        self.assertEqual(
            messages,
            [
                "HTK101 do not commit debugger traps",
                "HTK101 do not commit debugger traps",
            ],
        )

    def test_reports_htk_debug_helpers(self) -> None:
        messages = run_plugin(
            """
import htk
from htk import slack_debug as sd

def handler():
    htk.fdb("state")
    htk.slack_debug_json({"ok": True})
    sd("message")
"""
        )

        self.assertEqual(
            messages,
            [
                "HTK102 do not commit HTK debug helper calls",
                "HTK102 do not commit HTK debug helper calls",
                "HTK102 do not commit HTK debug helper calls",
            ],
        )


if __name__ == "__main__":
    unittest.main()

