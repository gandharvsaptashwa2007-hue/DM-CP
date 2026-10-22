"""End-to-end Streamlit interactions across CRT, RSA, and public-key recovery."""

from pathlib import Path
from unittest.mock import patch
import unittest

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")


class AppCase(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(APP).run()

    def navigate(self, name):
        self.app.radio(key="module").set_value(name).run()
        self.assertFalse(self.app.exception)

    def click(self, key):
        self.app.button(key=key).click().run()
        self.assertFalse(self.app.exception)

    def text(self):
        return "\n".join(c.value for c in self.app.code)


class CRTUITests(AppCase):
    def test_classroom_playback_and_normalized_verification(self):
        self.navigate("CRT Solver")
        self.click("crt_calculate")
        self.assertFalse(self.app.metric)
        self.assertTrue(self.app.button(key="crt_previous").disabled)
        self.click("crt_next")
        self.assertEqual(self.app.session_state["crt_position"], 1)
        self.click("crt_previous")
        self.assertEqual(self.app.session_state["crt_position"], 0)
        self.click("crt_show_all")
        self.assertEqual([m.value for m in self.app.metric], ["23", "105"])
        self.assertTrue(all(self.app.table[-1].value["Verified"]))
        self.assertTrue(self.app.button(key="crt_next").disabled)
        self.click("crt_restart")
        self.assertFalse(self.app.metric)
        self.click("crt_reset")
        self.assertFalse(self.app.table)
        self.app.selectbox(key="crt_preset").select("Normalize negative residues").run()
        self.click("crt_load")
        self.click("crt_calculate")
        self.click("crt_show_all")
        self.assertEqual([m.value for m in self.app.metric], ["8", "15"])

    def test_dynamic_equations_errors_and_stale_results(self):
        self.navigate("CRT Solver")
        self.app.selectbox(key="crt_preset").select("Six equations").run()
        self.click("crt_load")
        self.assertEqual(self.app.number_input(key="crt_count").value, 6)
        self.click("crt_calculate")
        self.click("crt_show_all")
        self.assertEqual(len(self.app.table[-1].value), 6)
        self.app.number_input(key="crt_count").set_value(2).run()
        self.assertFalse(self.app.metric)
        self.assertIsNone(self.app.session_state["crt_result"])
        self.app.text_input(key="crt_m_0").set_value("1").run()
        self.click("crt_calculate")
        self.assertTrue(self.app.error)
        self.app.selectbox(key="crt_preset").select("Unsupported non-coprime moduli").run()
        self.click("crt_load")
        self.click("crt_calculate")
        self.assertIn("generalized CRT", self.app.error[0].value)
        self.assertFalse(self.app.metric)
        self.app.text_input(key="crt_a_0").set_value("2.5").run()
        self.click("crt_calculate")
        self.assertTrue(self.app.error)


class RSAUITests(AppCase):
    def test_hello_encryption_decryption_traces_and_crt(self):
        self.navigate("RSA Lab")
        self.assertTrue(self.app.button(key="rsa_encrypt").disabled)
        self.click("rsa_build")
        self.assertEqual(self.app.session_state["rsa_keys"].d, 2753)
        self.click("rsa_encrypt")
        self.assertEqual(self.app.text_area(key="rsa_ciphertext").value, "3000, 28, 2726, 2726, 1307")
        self.click("rsa_power_next")
        self.assertEqual(self.app.session_state["rsa_power_position"], 1)
        self.app.selectbox(key="rsa_trace_block").select(1).run()
        self.assertEqual(self.app.session_state["rsa_power_position"], 0)
        self.click("rsa_decrypt")
        self.assertEqual(self.app.session_state["rsa_recovered"]["text"], "HELLO")
        self.assertIn("Round trip verified", " ".join(x.value for x in self.app.success))
        self.app.radio(key="rsa_trace_kind").set_value("Decryption").run()
        self.assertIn("CRT combines these residues into 72 mod 3233", self.text())
        self.click("rsa_power_show_all")
        self.assertTrue(self.app.button(key="rsa_power_next").disabled)

    def test_text_edge_cases_and_ciphertext_validation(self):
        self.navigate("RSA Lab")
        self.click("rsa_build")
        for message in ("hé 🔐 नमस्ते", "", " \n\t", "A" * 256):
            self.app.text_area(key="rsa_message").set_value(message).run()
            self.click("rsa_encrypt")
            self.click("rsa_decrypt")
            self.assertFalse(self.app.error)
            self.assertEqual(self.app.session_state["rsa_recovered"]["text"], message)
        self.app.text_area(key="rsa_message").set_value("🔐" * 65).run()
        self.click("rsa_encrypt")
        self.assertIn("256 UTF-8 bytes", self.app.error[0].value)
        for text in ("3233", "abc", "-1", str(pow(255, 17, 3233)), str(pow(300, 17, 3233))):
            self.app.text_area(key="rsa_ciphertext").set_value(text).run()
            self.click("rsa_decrypt")
            self.assertTrue(self.app.error)
            self.assertIsNone(self.app.session_state["rsa_recovered"])

    def test_integer_mode_key_errors_and_invalidation(self):
        self.navigate("RSA Lab")
        self.click("rsa_build")
        self.click("rsa_encrypt")
        self.click("rsa_decrypt")
        self.app.text_input(key="rsa_e").set_value("6").run()
        self.assertIsNone(self.app.session_state["rsa_keys"])
        self.assertIsNone(self.app.session_state["rsa_recovered"])
        self.assertEqual(self.app.text_area(key="rsa_ciphertext").value, "")
        self.click("rsa_build")
        self.assertIn("coprime", self.app.error[0].value)
        self.click("rsa_demo")
        self.click("rsa_build")
        self.app.radio(key="rsa_mode").set_value("Integer").run()
        for m in ("0", "53", "61", "3232"):
            self.app.text_area(key="rsa_message").set_value(m).run()
            self.click("rsa_encrypt")
            self.click("rsa_decrypt")
            self.assertEqual(self.app.session_state["rsa_recovered"]["text"], m)
        self.app.text_area(key="rsa_message").set_value("3233").run()
        self.click("rsa_encrypt")
        self.assertTrue(self.app.error)
        self.app.text_area(key="rsa_ciphertext").set_value("1, 2").run()
        self.click("rsa_decrypt")
        self.assertIn("exactly one", self.app.error[0].value)

    def test_small_modulus_and_random_keys(self):
        self.navigate("RSA Lab")
        for key, value in (("rsa_p", "3"), ("rsa_q", "5"), ("rsa_e", "3")):
            self.app.text_input(key=key).set_value(value).run()
        self.click("rsa_build")
        self.click("rsa_encrypt")
        self.assertIn("255", self.app.error[0].value)
        with patch("core.rsa.secrets.randbelow", side_effect=(0, 1)):
            self.click("rsa_generate")
        self.assertEqual(self.app.text_input(key="rsa_p").value, "101")
        self.assertEqual(self.app.text_input(key="rsa_q").value, "103")
        self.assertIsNone(self.app.session_state["rsa_packet"])
        self.click("rsa_encrypt")
        self.click("rsa_decrypt")
        self.assertEqual(self.app.session_state["rsa_recovered"]["text"], "HELLO")


class AttackUITests(AppCase):
    def test_public_key_attack_success_and_budget_exhaustion(self):
        self.navigate("Break the Key")
        self.click("attack_run")
        self.assertEqual(self.app.session_state["attack_result"].d, 2753)
        self.assertIn("HELLO", self.text())
        self.app.number_input(key="attack_budget").set_value(1).run()
        self.assertIsNone(self.app.session_state["attack_result"])
        self.click("attack_run")
        self.assertEqual(self.app.session_state["attack_result"].status, "incomplete")
        self.assertIn("no private key", self.app.warning[0].value)
        self.assertNotIn("Recovered d", self.text())

    def test_import_navigation_and_public_data_only(self):
        self.navigate("CRT Solver")
        self.click("crt_calculate")
        self.click("crt_show_all")
        self.navigate("RSA Lab")
        self.click("rsa_build")
        self.app.text_area(key="rsa_message").set_value("HELLO 🌍").run()
        self.click("rsa_encrypt")
        self.click("rsa_decrypt")
        ciphertext = self.app.text_area(key="rsa_ciphertext").value
        self.navigate("Break the Key")
        self.click("attack_import")
        self.assertEqual(self.app.text_area(key="attack_ciphertext").value, ciphertext)
        # Remove every private lab value before the actual attack is run.
        self.app.session_state["rsa_keys"] = None
        self.app.session_state["rsa_packet"] = None
        self.app.session_state["rsa_recovered"] = None
        self.click("attack_run")
        self.assertEqual(self.app.session_state["attack_result"].status, "recovered")
        self.assertIn("HELLO 🌍", self.text())
        self.navigate("CRT Solver")
        self.assertEqual([m.value for m in self.app.metric], ["23", "105"])
        self.navigate("Break the Key")
        self.assertIn("HELLO 🌍", self.text())
        self.assertEqual(self.app.text_area(key="attack_ciphertext").value, ciphertext)

    def test_invalid_inputs_and_recovered_key_with_invalid_utf8(self):
        self.navigate("Break the Key")
        self.click("attack_import")
        self.assertTrue(self.app.error)
        self.app.text_area(key="attack_ciphertext").set_value("3233").run()
        self.click("attack_run")
        self.assertTrue(self.app.error)
        self.app.text_area(key="attack_ciphertext").set_value(str(pow(255, 17, 3233))).run()
        self.click("attack_run")
        self.assertEqual(self.app.session_state["attack_result"].status, "recovered")
        self.assertIn("text decoding failed", self.app.error[0].value)
        self.app.radio(key="attack_mode").set_value("Integer").run()
        self.click("attack_run")
        self.assertFalse(self.app.error)
        self.assertIn("255", self.text())
        self.click("attack_reset")
        self.assertIsNone(self.app.session_state["attack_result"])

    def test_public_key_presets(self):
        self.navigate("Break the Key")
        for preset, status in (("Medium public key · n = 1022117", "recovered"),
                               ("Beyond this trial budget · n = 999962000357", "incomplete")):
            self.app.selectbox(key="attack_preset").select(preset).run()
            self.click("attack_load")
            self.click("attack_run")
            self.assertEqual(self.app.session_state["attack_result"].status, status)
