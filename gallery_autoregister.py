# -*- coding: utf-8 -*-
from __future__ import annotations

import inspect


MODULES = {
    "Alerts": "ada_ui.alerts",
    "Inputs": "ada_ui.inputs",
    "Pickers": "ada_ui.pickers",
    "Buttons": "ada_ui.buttons",
}


def discover_dialogs():

    registry = []

    for category, module_name in MODULES.items():

        try:
            module = __import__(module_name, fromlist=["*"])
        except Exception:
            continue

        for name, obj in inspect.getmembers(module):

            if not callable(obj):
                continue

            if name.startswith("_"):
                continue

            registry.append({
                "name": name.replace("_", " ").title(),
                "category": category,
                "function": obj
            })

    return registry