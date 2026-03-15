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


def ask_start_number(title="Start Number"):
    from .buttons import choose_action

    choice = choose_action(
        ["Start at 1", "Start at 10", "Start at 100", "Custom..."],
        title=title,
        message="Choose a starting number"
    )

    if choice == "Start at 1":
        return "1"
    if choice == "Start at 10":
        return "10"
    if choice == "Start at 100":
        return "100"
    if choice == "Custom...":
        return ask_string("Enter starting number", title=title, default="1")
    return None


def ask_include_subfolders(title="PNG Creator", default=False):
    """
    ADa-themed wrapper for a single optional batch setting.

    Returns:
        {"checked": bool} on confirm
        None on cancel
    """
    from .buttons import choose_actions

    selected = choose_actions(
        ["Include subfolders"],
        title=title,
        message="Choose one or more options",
        include_all=False
    )

    if selected is None:
        return None

    # Some chooser implementations may return a single string, some a list/tuple/set
    if isinstance(selected, str):
        checked = (selected == "Include subfolders")
    else:
        try:
            checked = "Include subfolders" in selected
        except Exception:
            checked = bool(default)

    return {"checked": bool(checked)}
