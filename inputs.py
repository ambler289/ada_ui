# -*- coding: utf-8 -*-
from __future__ import annotations

from . import forms as _forms


def _get_forms_obj():
    return getattr(_forms, "forms", _forms)


def ask_string(prompt="Enter value", title="Input", default=""):
    f = _get_forms_obj()

    if hasattr(f, "ask_for_string"):
        return f.ask_for_string(
            prompt=str(prompt),
            title=str(title),
            default=str(default or "")
        )

    if hasattr(_forms, "input_box"):
        ok, txt = _forms.input_box(str(title), str(prompt), str(default or ""))
        return txt if ok else None

    return None


def ask_multiline(prompt="Enter value", title="Input", default=""):
    # Placeholder for future custom multiline dialog
    return ask_string(prompt=prompt, title=title, default=default)


def ask_number(prompt="Enter number", title="Input", default=""):
    txt = ask_string(prompt=prompt, title=title, default=str(default or ""))
    if txt is None:
        return None

    txt = str(txt).strip()
    if not txt:
        return None

    try:
        if "." in txt:
            return float(txt)
        return int(txt)
    except Exception:
        return None