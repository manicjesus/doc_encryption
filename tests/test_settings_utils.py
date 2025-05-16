import unittest
from unittest.mock import mock_open, patch
import os 
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from settings_utils import loadSettings, saveSettings # type: ignore

class TestSettingsUtils(unittest.TestCase):

    counter = 0
    total_tests = 4

    @classmethod
    def setUpClass(cls):
        cls.total_tests = 4

    def tearDown(self):
        TestSettingsUtils.counter += 1
        print(f"✅ Test {TestSettingsUtils.counter} of {TestSettingsUtils.total_tests} concluded")

# --- TEST LOAD SETTINGS ---

    @patch("builtins.open", new_callable=mock_open, read_data='{}')
    #EMPTY SETTINGS
    def test_empty_settings_load_settings_returns_dict(self, mock_file):
        #Arrange test
        settings_data = loadSettings()

        #Asserts
        self.assertIsInstance(settings_data, dict, "loadSettings() didn't return a dict() as expected")
        self.assertIn("preset", settings_data, f"Preset not in settings_data '{settings_data}")
        self.assertIn("fullscreen", settings_data, f"Fullscreen not in settings_data '{settings_data}")
        self.assertEqual(settings_data["preset"], {}, f"Value of preset isn't dict() type - Preset: {settings_data['preset']}")
        self.assertFalse(settings_data["fullscreen"], f"Fullscreen different then False - Fullscreen: {settings_data['fullscreen']}")
        print("loadSettings() giving the expected responses for empty settings")

    @patch("builtins.open", new_callable=mock_open, read_data='{"preset": [], "fullscreen": "On"}')
    #WRONG TYPE OF VALUES IN SETTINGS
    def test_wrong_type_values_in_settings_load_settings_return_dict(self, mock_file):
        #Arrange test
        settings_data = loadSettings()

        #Asserts
        self.assertEqual(settings_data["preset"], {}, f"Value of preset isn't dict() type - Preset: {settings_data['preset']}")
        self.assertFalse(settings_data["fullscreen"], f"Fullscreen different then False - Fullscreen: {settings_data['fullscreen']}")
        print("loadSettings() correcting invalid values in settings as expected")

    @patch("builtins.open", new_callable=mock_open, read_data='{"preset": {"word":"sub", "anotherWord":"anotherSub"}, "fullscreen": true}')
    def test_load_valid_settings(self, mock_file):
        #Arrange tests
        settings_data = loadSettings()

        #Asserts
        self.assertEqual(settings_data["preset"],{"word":"sub", "anotherWord":"anotherSub"},f"Map loaded is different from the map given - Preset: {settings_data['preset']}")
        self.assertTrue(settings_data["fullscreen"],f"Fullscreen different then the given True - Fullscreen: {settings_data['fullscreen']}")
        print("loadSettings() returned the given values as expected")

    def test_save_settings(self, mock_file):
        #Arrange tests
        text = "June invites even more ways to enjoy the outdoors. At the top of the list? Baby bison-spotting in Yellowstone and 24-hour adventures in Iceland (thanks, midnight sun)."
        #As an example we'll only take the words with pair index from text and add them in the settings
        wordsToEncrypt = [i for i in text.split(" ") if text.index(i) % 2 == 0]
        newPresetMap = {word:f"sub{key}" for key,word in enumerate(wordsToEncrypt)}

        settings_data = {"preset": newPresetMap, "fullscreen": True}

        #Writing Patch
        with patch("builtins.open", mock_open()) as mock_file:
            saveSettings(settings_data)
            mock_file().write.assert_called()

            #Recovers the written content
            written_data = ''.join(call.args[0] for call in mock_file().write.call_args_list)

        #Reloads the settings through a new patch containing new mocked data
        with patch("builtins.open", mock_open(read_data=written_data)):
            reloaded_settings_data = loadSettings()

        #Asserts
        self.assertEqual(reloaded_settings_data["preset"],newPresetMap,f"Reloaded preset map is different then the expected - Reloaded Settings: {reloaded_settings_data['preset']}")
        self.assertTrue(reloaded_settings_data["fullscreen"],f"Fullscreen setting different then True - Fullscreen: {reloaded_settings_data['fullscreen']}")
        print("Loaded settings were updated with the expected values")