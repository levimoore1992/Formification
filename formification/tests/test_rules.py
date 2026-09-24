"""Boundary cases for server-side rule evaluation."""

from django import forms
from django.test import SimpleTestCase

from formification.rules import RuleAssessor


class RuleComparisonTests(SimpleTestCase):
    def test_comparisons(self):
        cases = [
            ("contains", "a cat here", "cat", True),
            ("contains", "a Cat here", "cat", False),
            ("does_not_contain", "dog", "cat", True),
            ("begins_with", "copycat", "cat", False),
            ("ends_with", "copycat", "cat", True),
            ("greater_than", "20", 3, True),
            ("greater_than", "3", 3, False),
            ("less_than", "2", 10, True),
            ("less_than", "", 10, False),
            ("less_than", None, 10, False),
            ("greater_than", "invalid", 10, False),
            ("greater_than", "Infinity", 10, False),
            ("less_than", 10, "NaN", False),
            ("is", ["1", "2"], 1, True),
            ("is_not", ["1", "2"], 1, False),
            ("any_selected", ["1"], [1, 2], True),
            ("all_selected", ["1"], [1, 2], False),
            ("all_selected", ["1", "2"], [1, 2], True),
            ("any_selected", [], [1, 2], False),
            ("all_selected", [], [1, 2], False),
            ("unknown", "other", "value", False),
        ]
        for operator, actual, expected, hidden in cases:
            with self.subTest(operator=operator, actual=actual, expected=expected):
                rule = {
                    "operator": "and",
                    "conditions": [
                        {
                            "field_slug": "watched",
                            "operator": operator,
                            "value": expected,
                        }
                    ],
                    "results": [{"field_slug": "target", "action": "hide"}],
                }
                assessor = RuleAssessor(
                    [rule],
                    {"watched": forms.CharField(), "target": forms.CharField()},
                    {"watched": actual},
                )
                self.assertEqual(not assessor.is_field_visible("target"), hidden)
