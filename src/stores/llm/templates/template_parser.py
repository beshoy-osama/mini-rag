import os
import importlib.util

class TemplateParser:
    def __init__(self, language: str, default_language: str = "en"):

        self.current_path = os.path.dirname(os.path.abspath(__file__))

        self.default_language = default_language
        self.language = None

        self.set_language(language)

    def set_language(self, language: str):
        if not language:
            self.language = self.default_language
            return

        language_path = os.path.join(self.current_path, 'locales', language)

        if os.path.exists(language_path):
            self.language = language
        else:
            self.language = self.default_language

    def get(self, group: str, key: str, vars: dict = None):

        if not group or not key:
            raise ValueError("Both 'group' and 'key' parameters are required.")

        vars = vars or {}

        group_path = os.path.join(self.current_path, 'locales', self.language, f'{group}.py')
        targeted_language = self.language

        if not os.path.exists(group_path):
            group_path = os.path.join(self.current_path, 'locales', self.default_language, f'{group}.py')
            targeted_language = self.default_language

        if not os.path.exists(group_path):
            raise FileNotFoundError(f"Language file '{group}.py' not found for language '{self.language}' or default language '{self.default_language}'.")

        # Import the language module dynamically
        spec = importlib.util.spec_from_file_location(f"{targeted_language}_{group}", group_path)
        lang_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lang_module)

        # Get the template from the module
        template = getattr(lang_module, key, None)
        if template is None:
            raise AttributeError(f"Template '{key}' not found in '{group}.py' for language '{targeted_language}'.")

        # Substitute variables in the template
        return template.substitute(vars)
