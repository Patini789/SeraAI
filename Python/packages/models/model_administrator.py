"""Model Administrator"""
import importlib.util
import sys


class ModelAdministrator:
    def __init__(self, constructor_paths=None):
        self.constructor_paths = constructor_paths or {} # Why did i did this? why paths needeed? i must check
        if not self.constructor_paths:
            pass  # Handle empty paths if needed
    @staticmethod
    def load_module_from_path(path, module_name="prompter"):
        spec = importlib.util.spec_from_file_location(module_name, str(path))
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
