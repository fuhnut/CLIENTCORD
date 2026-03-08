import os
import importlib.util
import sys

def load_config(file_name: str = "cc_init.py") -> dict[str, any]:
    path = os.path.join(os.getcwd(), file_name)
    if not os.path.exists(path):
        return {}

    spec = importlib.util.spec_from_file_location("cc_init", path)
    if not spec or not spec.loader:
        return {}

    module = importlib.util.module_from_spec(spec)
    sys.modules["cc_init"] = module
    spec.loader.exec_module(module)

    return {k: getattr(module, k) for k in dir(module) if not k.startswith("_")}
