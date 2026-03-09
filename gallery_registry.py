# -*- coding: utf-8 -*-
from __future__ import annotations


def preview_info_alert():
    from .alerts import show_info
    show_info("This is the standard ADa info alert.", title="ADa UI Preview")


def preview_yes_no():
    from .alerts import ask_yes_no
    ask_yes_no("Proceed with the preview?", title="ADa UI Preview")


def preview_string_input():
    from .inputs import ask_string
    ask_string(
        prompt="Enter some sample text",
        title="ADa UI Preview",
        default="Example"
    )


def preview_number_input():
    from .inputs import ask_number
    ask_number(
        prompt="Enter a sample number",
        title="ADa UI Preview",
        default="25"
    )


def preview_pick_one():
    from .pickers import pick_one # type: ignore
    pick_one(
        ["Walls", "Doors", "Windows", "Floors"],
        title="ADa UI Preview",
        prompt="Pick one category"
    )


def preview_pick_many():
    from .pickers import pick_many # type: ignore
    pick_many(
        ["Walls", "Doors", "Windows", "Floors"],
        title="ADa UI Preview",
        prompt="Pick one or more categories"
    )


def preview_big_buttons():
    from .buttons import choose_action # type: ignore
    choose_action(
        ["Pin Elements", "Unpin Elements", "Cancel"],
        title="ADa UI Preview",
        message="Choose an action"
    )


def preview_big_buttons_multi():
    from .buttons import choose_actions # type: ignore
    choose_actions(
        ["Walls", "Doors", "Windows", "Floors"],
        title="ADa UI Preview",
        message="Choose one or more options"
    )


DIALOG_REGISTRY = [
    {
        "name": "Info Alert",
        "category": "Alerts",
        "description": "Standard branded message dialog",
        "preview": preview_info_alert,
    },
    {
        "name": "Yes / No Confirmation",
        "category": "Alerts",
        "description": "Standard confirmation dialog",
        "preview": preview_yes_no,
    },
    {
        "name": "String Input",
        "category": "Inputs",
        "description": "Single-line text input",
        "preview": preview_string_input,
    },
    {
        "name": "Number Input",
        "category": "Inputs",
        "description": "Numeric input built on top of text input",
        "preview": preview_number_input,
    },
    {
        "name": "Searchable List Picker",
        "category": "Pickers",
        "description": "Single-select searchable list",
        "preview": preview_pick_one,
    },
    {
        "name": "Searchable Multi Picker",
        "category": "Pickers",
        "description": "Multi-select searchable list",
        "preview": preview_pick_many,
    },
    {
        "name": "Big Button Chooser",
        "category": "Buttons",
        "description": "Large single-select action buttons",
        "preview": preview_big_buttons,
    },
    {
        "name": "Big Button Multi Chooser",
        "category": "Buttons",
        "description": "Large multi-select action chooser",
        "preview": preview_big_buttons_multi,
    },
]