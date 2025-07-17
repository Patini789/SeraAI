"""Model Administrator"""
import importlib.util
import sys


class ModelAdministrator:
    def __init__(self):
        pass
    @staticmethod
    def load_module_from_path(path, module_name="prompter"):
        spec = importlib.util.spec_from_file_location(module_name, str(path))
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
