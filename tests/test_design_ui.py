"""Dashboard navigation and result journal behavior across Streamlit reruns."""

from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest
from ui.design import MODULES

APP = str(Path(__file__).resolve().parents[1] / "app.py")


class DesignTests(unittest.TestCase):
    def test_page_arrows_and_boundaries(self):
        app = AppTest.from_file(APP).run()
        self.assertTrue(app.button(key="page_previous").disabled)
        app.button(key="page_next").click().run()
        self.assertEqual(app.radio(key="module").value, "GCD Visualizer")
        app.button(key="calculate").click().run()
        app.button(key="page_next").click().run()
        app.button(key="page_previous").click().run()
        self.assertEqual(app.session_state["history_gcd"], ["gcd(252, 105) = 21"])
        app.radio(key="module").set_value("Break the Key").run()
        self.assertTrue(app.button(key="page_next").disabled)
        self.assertFalse(app.exception)

    def setUp(self):
        self.app = AppTest.from_file(APP).run()

    def test_all_dashboard_cards_navigate(self):
        self.assertEqual(self.app.radio(key="module").value, "Home")
        for name, (slug, *_) in MODULES.items():
            self.app.button(key=f"open_{slug}").click().run()
            self.assertEqual(self.app.radio(key="module").value, name)
            self.assertFalse(self.app.exception)
            self.app.radio(key="module").set_value("Home").run()

    def test_history_survives_navigation_and_input_edits(self):
        self.app.button(key="open_gcd").click().run()
        self.app.button(key="calculate").click().run()
        self.app.button(key="next").click().run()
        self.assertEqual(self.app.session_state["history_gcd"], ["gcd(252, 105) = 21"])
        self.app.radio(key="module").set_value("RSA Lab").run()
        self.app.radio(key="module").set_value("GCD Visualizer").run()
        self.app.text_input(key="gcd_a").set_value("17").run()
        self.assertEqual(len(self.app.session_state["history_gcd"]), 1)
        self.app.button(key="calculate").click().run()
        self.assertEqual(self.app.session_state["history_gcd"][0], "gcd(17, 105) = 1")
        self.app.button(key="clear_history_gcd").click().run()
        self.app.run()
        self.assertEqual(self.app.session_state["history_gcd"], [])

    def test_failed_input_does_not_log_and_history_is_bounded(self):
        self.app.button(key="open_gcd").click().run()
        self.app.text_input(key="gcd_a").set_value("invalid").run()
        self.app.button(key="calculate").click().run()
        self.assertEqual(self.app.session_state["history_gcd"], [])
        self.app.text_input(key="gcd_a").set_value("252").run()
        for _ in range(22):
            self.app.button(key="calculate").click().run()
        self.assertEqual(len(self.app.session_state["history_gcd"]), 20)
        self.assertFalse(self.app.exception)

    def test_rsa_journal_tracks_workflow_without_playback_duplicates(self):
        self.app.button(key="open_rsa").click().run()
        for key in ("rsa_build", "rsa_encrypt", "rsa_decrypt"):
            self.app.button(key=key).click().run()
        history = self.app.session_state["history_rsa"]
        self.assertEqual(len(history), 3)
        self.assertIn("Decrypted 5 blocks", history[0])
        self.app.run()
        self.assertEqual(len(self.app.session_state["history_rsa"]), 3)
        self.assertFalse(self.app.exception)
