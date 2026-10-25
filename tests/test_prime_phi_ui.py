"""Interaction tests for both new modules and state isolation."""

from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")


class PrimePhiUITests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(APP).run()

    def navigate(self, module):
        self.app.session_state.__setitem__("module", module); self.app.run()
        self.assertFalse(self.app.exception)

    def click(self, key):
        self.app.button(key=key).click().run()
        self.assertFalse(self.app.exception)

    def test_trial_playback_validation_and_budget(self):
        self.navigate("Primality Tester")
        self.click("prime_calculate")
        self.assertEqual(self.app.metric[0].value, "Prime")
        self.assertTrue(self.app.button(key="prime_previous").disabled)
        self.click("prime_next")
        self.assertEqual(len(self.app.table[0].value), 2)
        self.click("prime_previous")
        self.assertEqual(len(self.app.table[0].value), 1)
        self.click("prime_show_all")
        self.assertEqual(len(self.app.table[0].value), 5)
        self.assertTrue(self.app.button(key="prime_next").disabled)
        self.click("prime_restart")
        self.assertEqual(len(self.app.table[0].value), 1)
        self.app.number_input(key="prime_budget").set_value(1).run()
        self.assertFalse(self.app.metric)
        self.click("prime_calculate")
        self.assertEqual(self.app.metric[0].value, "Unresolved")
        self.assertTrue(self.app.warning)
        for invalid in ("-1", "", "2.5", "abc", "1000000000001"):
            self.app.text_input(key="prime_n").set_value(invalid).run()
            self.click("prime_calculate")
            self.assertTrue(self.app.error)
            self.assertFalse(self.app.metric)

    def test_miller_rabin_presets_rounds_and_exact_large_values(self):
        self.navigate("Primality Tester")
        for example, expected in (
            ("Carmichael number · 561", "Composite"),
            ("Strong pseudoprime to base 2 · 2047", "Composite"),
            ("Large prime · 18446744073709551557", "Prime"),
            ("Smallest prime · 2", "Prime"),
            ("Neither prime nor composite · 1", "Neither"),
        ):
            self.app.selectbox(key="prime_preset").select(example).run()
            self.click("prime_load")
            self.assertFalse(self.app.metric)
            self.click("prime_calculate")
            self.assertEqual(self.app.metric[0].value, expected)
            if example.startswith("Strong"):
                self.click("prime_show_all")
                self.assertIn("witness", self.app.table[-1].value["Outcome"].tolist())
            if example.startswith("Large"):
                self.assertEqual(self.app.session_state["prime_result"].n, 18446744073709551557)
                self.click("prime_show_all")
                self.assertEqual(len(self.app.table[-1].value), 7)
        self.app.radio(key="prime_method").set_value("Miller–Rabin").run()
        self.assertFalse(self.app.metric)
        self.app.text_input(key="prime_n").set_value(str(2**64)).run()
        self.click("prime_calculate")
        self.assertTrue(self.app.error)

    def test_phi_playback_coprime_list_and_reset(self):
        self.navigate("Euler’s Phi")
        self.click("phi_calculate")
        self.assertFalse(self.app.metric)
        self.assertTrue(self.app.button(key="phi_previous").disabled)
        self.click("phi_next")
        self.assertEqual(self.app.metric[0].value, "12")
        self.assertTrue(self.app.button(key="phi_next").disabled)
        self.assertIn("1, 5, 7, 11, 13, 17, 19, 23, 25, 29, 31, 35", "\n".join(c.value for c in self.app.code))
        self.click("phi_previous")
        self.assertFalse(self.app.metric)
        self.click("phi_show_all")
        self.assertEqual(self.app.metric[0].value, "12")
        self.click("phi_restart")
        self.assertFalse(self.app.metric)
        self.click("phi_reset")
        self.assertFalse(self.app.table)

    def test_phi_presets_incomplete_and_invalid(self):
        self.navigate("Euler’s Phi")
        for preset, expected in (("Prime · 13", "12"), ("Prime power · 81", "54"),
                                 ("RSA modulus · 3233", "3120"), ("Special case · 1", "1")):
            self.app.selectbox(key="phi_preset").select(preset).run()
            self.click("phi_load")
            self.click("phi_calculate")
            if self.app.session_state["phi_result"].steps:
                self.click("phi_show_all")
            self.assertEqual(self.app.metric[0].value, expected)
        self.app.text_input(key="phi_n").set_value("36").run()
        self.assertFalse(self.app.metric)
        self.app.number_input(key="phi_budget").set_value(1).run()
        self.click("phi_calculate")
        self.assertTrue(self.app.warning)
        self.assertFalse(self.app.metric)
        self.assertIn("unresolved cofactor", self.app.code[0].value)
        for invalid in ("0", "-1", "", "2.5", "1000000000001"):
            self.app.text_input(key="phi_n").set_value(invalid).run()
            self.click("phi_calculate")
            self.assertTrue(self.app.error)
            self.assertFalse(self.app.metric)

    def test_all_modules_preserve_independent_state(self):
        self.navigate("Primality Tester")
        self.app.text_input(key="prime_n").set_value("91").run()
        self.click("prime_calculate")
        self.click("prime_show_all")
        self.navigate("Euler’s Phi")
        self.app.text_input(key="phi_n").set_value("81").run()
        self.click("phi_calculate")
        self.navigate("GCD Visualizer")
        self.click("calculate")
        self.click("show_all")
        self.navigate("Extended Euclid & Inverse")
        self.click("inverse_calculate")
        self.click("inverse_show_all")
        for _ in range(2):
            self.navigate("Primality Tester")
            self.assertEqual(self.app.text_input(key="prime_n").value, "91")
            self.assertEqual(self.app.metric[0].value, "Composite")
            self.assertTrue(self.app.button(key="prime_next").disabled)
            self.navigate("Euler’s Phi")
            self.assertEqual(self.app.text_input(key="phi_n").value, "81")
            self.assertEqual(self.app.metric[0].value, "54")
            self.navigate("GCD Visualizer")
            self.assertEqual(self.app.metric[0].value, "21")
            self.navigate("Extended Euclid & Inverse")
            self.assertEqual([m.value for m in self.app.metric], ["1", "2753"])
