# -*- coding: utf-8 -*-
from __future__ import annotations

from . import forms as _forms


def _get_forms_obj():
    # forms.py re-exports public members from the newest available brandforms module
    # In v6, this includes `forms = _V6Shim()`
    return getattr(_forms, "forms", _forms)


def show_info(message, title="ADa Tools"):
    f = _get_forms_obj()
    if hasattr(f, "alert"):
        return f.alert(str(message), title=str(title))
    return None


def show_warning(message, title="Warning"):
    return show_info(message, title=title)


def show_success(message, title="Success"):
    return show_info(message, title=title)


def show_error(message, title="Error"):
    return show_info(message, title=title)


def ask_yes_no(message, title="Confirm"):
    f = _get_forms_obj()

    if hasattr(f, "ask_yes_no"):
        return bool(f.ask_yes_no(str(message), title=str(title)))

    # fallback if only alert exists
    if hasattr(f, "alert"):
        result = f.alert(str(message), title=str(title), buttons=("Yes", "No"))
        return result == "Yes"

    return False


def show_buttons(buttons, title="Choose", message="Select an option"):
    """
    Small button chooser dialog.
    Returns the clicked button label.
    """
    f = _get_forms_obj()

    if hasattr(f, "alert"):
        return f.alert(
            str(message),
            title=str(title),
            buttons=tuple(buttons)
        )

    return None

def show_result(message, title="ADa Tool Summary", warnings=0, errors=0, details=None):
    """
    Branded summary/result dialog for completed operations.

    message: main summary line
    warnings: integer warning count
    errors: integer error count
    details: optional list of extra lines
    """
    lines = [str(message).strip()]

    lines.append("")
    lines.append("Warnings: {}".format(int(warnings)))
    lines.append("Errors: {}".format(int(errors)))

    if details:
        extra = [str(x) for x in details if x is not None and str(x).strip()]
        if extra:
            lines.append("")
            lines.extend(extra)

    body = "\n".join(lines)

    f = _get_forms_obj()
    if hasattr(f, "alert"):
        return f.alert(body, title=str(title))

    return None
