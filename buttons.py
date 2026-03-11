# -*- coding: utf-8 -*-
from __future__ import annotations

from .ada_core_bigbuttons import choose, choose_multi, alert as _bb_alert


def choose_action(options, title="Choose Action", message=""):
    return choose(options, title=title, message=message)


def choose_actions(options, title="Choose Actions", message="", include_all=True):
    return choose_multi(
        options,
        title=title,
        message=message,
        include_all=include_all
    )


def choose_actions_toggle(options, title="Choose Actions", message=""):
    """
    Toggle-style multi-select wrapper.

    Intended for staged multi-selection workflows such as:
    - All / Clear / Done
    - category toggles
    - CPython-safe button-driven multi-pickers

    Currently falls back to the standard multi chooser.
    """
    return choose_multi(
        options,
        title=title,
        message=message,
        include_all=True
    )


def show_button_alert(message, title="Message"):
    return _bb_alert(message, title=title)