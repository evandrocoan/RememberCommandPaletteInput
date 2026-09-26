import importlib.util
import sys
import types
import unittest
from collections import OrderedDict
from pathlib import Path
from unittest.mock import patch


PLUGIN_PATH = Path(__file__).resolve().parents[1] / "input_history.py"


class Settings:
    def __init__(self):
        self.values = {}

    def set(self, key, value):
        self.values[key] = value


class Window:
    def __init__(self):
        self.window_settings = Settings()

    def project_file_name(self):
        return "example.sublime-project"

    def settings(self):
        return self.window_settings


class InputHistoryTests(unittest.TestCase):
    def setUp(self):
        self.saved = []
        self.window = Window()
        sublime = types.ModuleType("sublime")
        sublime.packages_path = lambda: "packages"
        sublime.active_window = lambda: self.window
        sublime_plugin = types.ModuleType("sublime_plugin")
        sublime_plugin.WindowCommand = type("WindowCommand", (), {})
        sublime_plugin.TextCommand = type("TextCommand", (), {})
        sublime_plugin.EventListener = type("EventListener", (), {})
        debug_tools = types.ModuleType("debug_tools")
        debug_tools.__path__ = []
        debug_tools.getLogger = lambda *args: types.SimpleNamespace(exception=lambda *args: None)
        utilities = types.ModuleType("debug_tools.utilities")
        utilities.pop_dict_last_item = lambda value: value.popitem(last=True)
        third_part = types.ModuleType("debug_tools.third_part")
        third_part.load_data_file = lambda *args, **kwargs: self.loaded_settings()
        third_part.write_data_file = lambda path, data, **kwargs: self.saved.append(data.copy())
        modules = {
            "sublime": sublime,
            "sublime_plugin": sublime_plugin,
            "debug_tools": debug_tools,
            "debug_tools.utilities": utilities,
            "debug_tools.third_part": third_part,
        }
        self.module_patch = patch.dict(sys.modules, modules)
        self.module_patch.start()
        self.addCleanup(self.module_patch.stop)
        spec = importlib.util.spec_from_file_location("input_history_under_test", PLUGIN_PATH)
        self.plugin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.plugin)

    def loaded_settings(self):
        raise FileNotFoundError("first session")

    def test_first_session_saves_project_history(self):
        self.plugin.plugin_loaded()
        self.plugin.save_settings("git status")

        self.assertIsInstance(self.plugin.g_settings["workspaces"], OrderedDict)
        self.assertEqual(
            list(self.plugin.g_settings["workspaces"].items()),
            [("example.sublime-project", "git status")],
        )
        self.assertEqual(self.window.window_settings.values["last_command_palette_input"], "git status")
        self.assertEqual(self.saved[-1]["last_input"], "git status")

    def test_loaded_plain_dict_is_normalized(self):
        self.plugin.load_data_file = lambda *args, **kwargs: {
            "last_input": "old",
            "workspaces": {"older.sublime-project": "old"},
        }

        self.plugin.plugin_loaded()
        self.plugin.save_settings("new")

        self.assertEqual(
            list(self.plugin.g_settings["workspaces"].items()),
            [
                ("example.sublime-project", "new"),
                ("older.sublime-project", "old"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
