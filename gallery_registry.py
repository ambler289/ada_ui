# -*- coding: utf-8 -*-
from __future__ import annotations

from .gallery_previews import ( #type: ignore
    preview_info_alert,
    preview_yes_no,
    preview_string_input,
    preview_number_input,
    preview_pick_one,
    preview_pick_many,
    preview_big_buttons,
    preview_big_buttons_multi,
)

DIALOG_REGISTRY = [
    {
        "name": "Info Alert",
        "category": "Alerts",
        "description": "Standard branded message dialog",
        "preview": preview_info_alert,
        "sample": {
            "title": "ADa UI Preview",
            "message": "This is the standard ADa info alert.",
        },
    },
    {
        "name": "Yes / No Confirmation",
        "category": "Alerts",
        "description": "Standard confirmation dialog",
        "preview": preview_yes_no,
        "sample": {
            "title": "ADa UI Preview",
            "message": "Proceed with the preview?",
        },
    },
    {
        "name": "String Input",
        "category": "Inputs",
        "description": "Single-line text input",
        "preview": preview_string_input,
        "sample": {
            "title": "ADa UI Preview",
            "prompt": "Enter some sample text",
            "default": "Example",
        },
    },
    {
        "name": "Number Input",
        "category": "Inputs",
        "description": "Numeric input built on top of text input",
        "preview": preview_number_input,
        "sample": {
            "title": "ADa UI Preview",
            "prompt": "Enter a sample number",
            "default": "25",
        },
    },
    {
        "name": "Searchable List Picker",
        "category": "Pickers",
        "description": "Single-select searchable list",
        "preview": preview_pick_one,
        "sample": {
            "title": "ADa UI Preview",
            "prompt": "Pick one category",
            "items": ["Walls", "Doors", "Windows", "Floors"],
        },
    },
    {
        "name": "Searchable Multi Picker",
        "category": "Pickers",
        "description": "Multi-select searchable list",
        "preview": preview_pick_many,
        "sample": {
            "title": "ADa UI Preview",
            "prompt": "Pick one or more categories",
            "items": ["Walls", "Doors", "Windows", "Floors"],
        },
    },
    {
        "name": "Big Button Chooser",
        "category": "Buttons",
        "description": "Large single-select action buttons",
        "preview": preview_big_buttons,
        "sample": {
            "title": "ADa UI Preview",
            "prompt": "Choose an action",
            "items": ["Pin Elements", "Unpin Elements", "Cancel"],
        },
    },
    {
        "name": "Big Button Multi Chooser",
        "category": "Buttons",
        "description": "Large multi-select action chooser",
        "preview": preview_big_buttons_multi,
        "sample": {
            "title": "ADa UI Preview",
            "prompt": "Choose one or more options",
            "items": ["Walls", "Doors", "Windows", "Floors"],
        },
    },
]