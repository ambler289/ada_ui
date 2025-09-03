# ada_ui/forms.py — legacy shim so "from ada_ui import forms" works
from importlib import import_module

_candidates = ("ada_brandforms_v6", "ada_brandforms_v5", "ada_brandforms_v4_2",
               "ada_brandforms_v4", "ada_brandforms_v3")

for name in _candidates:
    try:
        _m = import_module("." + name, __package__)
        # re-export everything public from the chosen brandforms module
        globals().update({k: v for k, v in vars(_m).items() if not k.startswith("_")})
        break
    except Exception:
        continue
else:
    raise ImportError("No ADa brandforms module found under ada_ui.")