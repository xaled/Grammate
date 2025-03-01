import sys
import unittest
import logging
from grammate import (
    flatten_config,
    merge_dicts,
    load_locale_config,
)

TEST_LOCALES_DIR = "locales"


class TestLocalizationConfigs(unittest.TestCase):
    def test_flatten_config(self):
        input_data = {
            "a": {
                "b": {
                    "c": "value"
                },
                "d": "another"
            }
        }
        expected = {
            "a.b.c": "value",
            "a.d": "another"
        }
        self.assertEqual(flatten_config(input_data), expected)

    def test_merge_dicts(self):
        base = {
            "a": {"x": 1},
            "b": 2
        }
        override = {
            "a": {"y": 2},
            "b": 3
        }
        expected = {
            "a": {"x": 1, "y": 2},
            "b": 3
        }
        self.assertEqual(merge_dicts(base, override), expected)

    def test_load_locale_config_inheritance(self):
        config = load_locale_config("fr", locales_dir=TEST_LOCALES_DIR)
        self.assertEqual(config["greeting"], "Bonjour")
        self.assertEqual(config["farewell"], "Goodbye")  # Inherited from "en"

    def test_load_locale_config_nested_inheritance(self):
        config = load_locale_config("ur", locales_dir=TEST_LOCALES_DIR)
        self.assertEqual(config["farewell"], "Goodbye")  # Inherited from "en"
        self.assertEqual(config["nested.key"], "قيمة")  # Inherited from "ar"

    def test_load_locale_config_nested_keys(self):
        config = load_locale_config("ar", locales_dir=TEST_LOCALES_DIR)
        self.assertEqual(config["nested.key"], "قيمة")
        self.assertEqual(config["month"], "شهر")
        self.assertIsInstance(config["month.plural"], list)
        self.assertEqual(config["month.plural.1"], "أشهر")

        # test conflict precedence
        self.assertIsInstance(config["key"], dict)
        self.assertEqual(config["key.subkey1"], "flat_test")

    def test_load_locale_config_with_language_inheritance(self):
        config = load_locale_config("ar_MA", locales_dir=TEST_LOCALES_DIR)
        self.assertEqual(config["greeting"], "مرحبا")  # custom from "ar_MA"
        self.assertEqual(config["farewell"], "الوداع")  # Inherited from "ar"

    def test_load_locale_config_with_fallback(self):
        config = load_locale_config("es", locales_dir=TEST_LOCALES_DIR, fallback_locale="en")
        self.assertEqual(config["greeting"], "Hello")


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
