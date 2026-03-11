# -*- coding: utf-8 -*-
from __future__ import annotations


def bulk_parameter_editor(parameters, title="Set Parameter", message="Choose parameter and value"):
    """
    ADa Bulk Parameter Editor

    parameters : list[str]
    returns : dict | None

    {
        "parameter": "...",
        "value": "..."
    }
    """

    from .pickers import pick_one
    from .inputs import ask_string

    if not parameters:
        return None

    parameter = pick_one(
        parameters,
        title=title,
        prompt=message
    )

    if not parameter:
        return None

    value = ask_string(
        prompt="Enter value for '{}'".format(parameter),
        title=title,
        default=""
    )

    if value is None:
        return None

    return {
        "parameter": parameter,
        "value": value
    }