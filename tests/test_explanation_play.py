from pathlib import Path
import unittest
from streamlit.testing.v1 import AppTest


class ExplanationPlayTests(unittest.TestCase):
    def test_answer_feedback_and_live_remainders(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
        app.button(key="open_gcd").click().run()
        for answer, expected in (("oops", "invalid"), ("9", "retry"), ("6", "correct")):
            app.text_input(key="challenge_answer_gcd").set_value(answer).run()
            app.button(key="challenge_check_gcd").click().run()
            self.assertEqual(app.session_state["challenge_feedback_gcd"], expected)
        app.slider(key="explore_number_gcd").set_value(20).run()
        self.assertTrue(any("20 mod 5 = **0**" in item.value for item in app.markdown))
        self.assertEqual(app.session_state["history_gcd"], [])
        app.selectbox(key="page_picker").select("RSA Lab").run()
        app.button(key="page_previous").click().run()
        self.assertEqual(app.text_input(key="challenge_answer_gcd").value, "6")
        self.assertFalse(app.exception)
