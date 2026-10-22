"""Exercise the inverse screen and navigation through real Streamlit widgets."""

from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")


class InverseUITests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(APP).run()
        self.app.radio(key="module").set_value("Extended Euclid & Inverse").run()
        self.assertFalse(self.app.exception)

    def click(self, key):
        self.app.button(key=key).click().run()
        self.assertFalse(self.app.exception)

    def example(self, label):
        self.app.selectbox(key="inverse_preset").select(label).run()
        self.click("inverse_load")
        self.click("inverse_calculate")
        if self.app.session_state["inverse_result"].steps:
            self.click("inverse_show_all")

    def test_rsa_example_playback_and_back_substitution(self):
        self.click("inverse_calculate")
        self.assertEqual(len(self.app.metric), 0)
        self.assertTrue(self.app.button(key="inverse_previous").disabled)
        self.click("inverse_next")
        self.assertEqual(len(self.app.table[0].value), 4)
        self.click("inverse_previous")
        self.assertEqual(len(self.app.table[0].value), 3)
        self.click("inverse_show_all")
        self.assertEqual([m.value for m in self.app.metric], ["1", "2753"])
        self.assertTrue(self.app.button(key="inverse_next").disabled)
        code = "\n".join(c.value for c in self.app.code)
        self.assertIn("Replace 9 with 3120 − 183 × 17", code)
        self.assertIn("Original signs: 1 = (17) × (-367) + (3120) × (2)", code)
        self.click("inverse_restart")
        self.assertEqual(len(self.app.metric), 0)
        self.click("inverse_reset")
        self.assertEqual(len(self.app.table), 0)

    def test_no_inverse_retains_explanation(self):
        self.example("No inverse · 6 mod 9")
        self.assertEqual([m.value for m in self.app.metric], ["3"])
        self.assertIn("No modular inverse exists", self.app.warning[0].value)
        self.assertTrue(self.app.table)
        self.assertIsNone(self.app.session_state["inverse_value"])

    def test_signed_and_zero_examples(self):
        for label, values in (
            ("Negative number · −3 mod 11", ["1", "7"]),
            ("Signed inputs · −252 and −105", ["21"]),
            ("Zero input · 42 and 0", ["42"]),
            ("Both zero · 0 and 0", ["0"]),
        ):
            with self.subTest(label=label):
                self.example(label)
                self.assertEqual([m.value for m in self.app.metric], values)

    def test_invalid_inputs_and_recovery(self):
        for invalid in ("0", "1", "-11", "2.5", "", str(10**18 + 1)):
            self.app.text_input(key="inverse_b").set_value(invalid).run()
            self.click("inverse_calculate")
            self.assertEqual(len(self.app.error), 1)
            self.assertEqual(len(self.app.metric), 0)
        self.app.text_input(key="inverse_b").set_value("3120").run()
        self.click("inverse_calculate")
        self.assertFalse(self.app.error)
        self.click("inverse_show_all")
        self.app.text_input(key="inverse_a").set_value("6").run()
        self.assertFalse(self.app.metric)
        self.assertIsNone(self.app.session_state["inverse_result"])

    def test_mode_change_clears_results(self):
        self.click("inverse_calculate")
        self.click("inverse_show_all")
        self.app.radio(key="inverse_mode").set_value("Extended Euclid").run()
        self.assertFalse(self.app.metric)
        self.click("inverse_calculate")
        self.click("inverse_show_all")
        self.assertEqual([m.value for m in self.app.metric], ["1"])

    def test_navigation_preserves_inputs_and_results_independently(self):
        self.example("Negative number · −3 mod 11")
        self.app.radio(key="module").set_value("GCD Visualizer").run()
        self.app.text_input(key="gcd_a").set_value("48").run()
        self.app.text_input(key="gcd_b").set_value("18").run()
        self.click("calculate")
        self.click("show_all")
        self.assertEqual(self.app.metric[0].value, "6")
        for _ in range(2):
            self.app.radio(key="module").set_value("Extended Euclid & Inverse").run()
            self.assertEqual(self.app.text_input(key="inverse_a").value, "-3")
            self.assertEqual(self.app.text_input(key="inverse_b").value, "11")
            self.assertEqual([m.value for m in self.app.metric], ["1", "7"])
            self.app.radio(key="module").set_value("GCD Visualizer").run()
            self.assertEqual(self.app.text_input(key="gcd_a").value, "48")
            self.assertEqual(self.app.text_input(key="gcd_b").value, "18")
            self.assertEqual(self.app.metric[0].value, "6")
            self.assertFalse(self.app.exception)
