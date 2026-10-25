"""Run real Streamlit interactions without requiring a browser."""

from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest

from ui.gcd_view import parse_integer

APP = str(Path(__file__).resolve().parents[1] / "app.py")


class GCDUITests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(APP).run()
        self.app.session_state.__setitem__("module", "GCD Visualizer"); self.app.run()
        self.assertFalse(self.app.exception)

    def click(self, key):
        self.app.button(key=key).click().run()
        self.assertFalse(self.app.exception)

    def test_step_navigation_and_reset(self):
        self.assertEqual(len(self.app.metric), 0)
        self.click("calculate")
        self.assertTrue(self.app.button(key="previous").disabled)
        self.assertEqual(len(self.app.table[0].value), 1)
        self.click("next")
        self.assertEqual(len(self.app.table[0].value), 2)
        self.click("previous")
        self.assertEqual(len(self.app.table[0].value), 1)
        self.click("show_all")
        self.assertEqual(self.app.metric[0].value, "21")
        self.assertEqual(len(self.app.table[0].value), 3)
        self.assertTrue(self.app.button(key="next").disabled)
        self.click("restart")
        self.assertEqual(len(self.app.table[0].value), 1)
        self.assertEqual(len(self.app.metric), 0)
        self.click("reset")
        self.assertEqual(len(self.app.table), 0)

    def test_input_change_clears_previous_result(self):
        self.click("calculate")
        self.click("show_all")
        self.app.text_input(key="gcd_a").set_value("17").run()
        self.assertEqual(len(self.app.metric), 0)
        self.assertEqual(len(self.app.table), 0)
        self.click("calculate")
        self.click("show_all")
        self.assertEqual(self.app.metric[0].value, "1")

    def test_presets_negative_and_zero(self):
        examples = [
            ("Negative input · −252 and 105", "21"),
            ("Zero input · 42 and 0", "42"),
            ("Both zero · 0 and 0", "0"),
        ]
        for label, expected in examples:
            self.app.selectbox(key="gcd_preset").select(label).run()
            self.click("load_example")
            self.assertIsNone(self.app.session_state["gcd_result"])
            self.click("calculate")
            if self.app.session_state["gcd_result"].steps:
                self.click("show_all")
            self.assertEqual(self.app.metric[0].value, expected)

    def test_invalid_inputs_and_recovery(self):
        for invalid in ("", "2.5", "hello", "1000000000000000001"):
            self.app.text_input(key="gcd_a").set_value(invalid).run()
            self.click("calculate")
            self.assertEqual(len(self.app.error), 1)
            self.assertEqual(len(self.app.table), 0)
        self.app.text_input(key="gcd_a").set_value("252").run()
        self.click("calculate")
        self.assertEqual(len(self.app.error), 0)
        self.assertEqual(len(self.app.table), 1)

    def test_large_integer_precision(self):
        self.app.text_input(key="gcd_a").set_value("999999999999999999").run()
        self.app.text_input(key="gcd_b").set_value("0").run()
        self.click("calculate")
        self.assertEqual(self.app.metric[0].value, "999999999999999999")


class InputTests(unittest.TestCase):
    def test_exact_decimal_input(self):
        for text, value in ((" -105 ", -105), ("+252", 252), ("0", 0),
                            (str(10**18), 10**18), (str(-10**18), -10**18)):
            self.assertEqual(parse_integer(text, "Input"), value)

    def test_reject_invalid_or_out_of_range(self):
        for text in ("1e3", "1_000", "1.0", "", "--2", str(10**18 + 1), "9" * 100):
            with self.assertRaises(ValueError):
                parse_integer(text, "Input")
