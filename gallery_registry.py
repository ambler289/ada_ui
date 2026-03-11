# -*- coding: utf-8 -*-
from __future__ import annotations

from .gallery_previews import ( #type: ignore
    preview_info_alert,
    preview_warning_alert,
    preview_error_alert,
    preview_yes_no,
    preview_string_input,
    preview_number_input,
    preview_pick_one,
    preview_pick_many,
    preview_big_buttons,
    preview_big_buttons_multi,
    preview_small_buttons,
    preview_next_action,
    preview_completion_summary,
    preview_grid_buttons,
    preview_bulk_parameter_setter,
    preview_bulk_parameter_table_editor,
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
        "name": "Warning Alert",
        "category": "Alerts",
        "description": "Branded warning message dialog",
        "preview": preview_warning_alert,
        "sample": {
            "title": "ADa Warning",
            "message": "This action may modify elements in the model.\n\nContinue with caution.",
        },
    },
    {
        "name": "Error Alert",
        "category": "Alerts",
        "description": "Branded error message dialog",
        "preview": preview_error_alert,
        "sample": {
            "title": "ADa Error",
            "message": "The operation could not be completed.\n\nNo valid elements were found.",
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
        "name": "Small Button Chooser",
        "category": "Buttons",
        "description": "Compact action selector with custom buttons",
        "preview": preview_small_buttons,
        "sample": {
            "title": "Change Text Case",
            "message": "Choose a text case:",
            "buttons": ["Upper", "Lower", "Title", "Cancel"],
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
        {
        "name": "Next Action Chooser",
        "category": "Workflows",
        "description": "Repeat / change mode / finish workflow pattern",
        "preview": preview_next_action,
        "sample": {
            "title": "Next Action",
            "message": "Select what you would like to do next.",
            "buttons": ["Run Again", "Change Mode", "Finish"],
        },
    },
    {
        "name": "Completion Summary",
        "category": "Workflows",
        "description": "End-of-tool completion report dialog",
        "preview": preview_completion_summary,
        "sample": {
            "title": "ADa Tool Summary",
            "message": "Operation completed successfully.\n\nItems processed: 12\nWarnings: 0\nErrors: 0",
        },
    },
    {
        "name": "Grid Button Chooser",
        "category": "Buttons Layouts",
        "description": "Compact grid of selectable buttons",
        "preview": preview_grid_buttons,
        "sample": {
            "title": "ADa UI Preview",
            "prompt": "Choose a category",
            "items": ["Walls","Doors","Windows","Floors","Roofs","Columns"]
        },
    },   
        {
        "name": "Bulk Parameter Setter",
        "category": "Editors",
        "description": "Large workflow dialog for choosing a parameter and setting a value",
        "preview": preview_bulk_parameter_setter,
        "sample": {
            "title": "Bulk Parameter Setter",
            "prompt": "Choose a parameter to edit",
            "parameters": [
                "Comments",
                "Mark",
                "Fire Rating",
                "Window Type",
                "Jamb Liner",
                "Glazing",
            ],
            "default_value": "Example Value",
            "element_count": 12,
        },
    }, 
        {
        "name": "Bulk Parameter Table Editor",
        "category": "Editors",
        "description": "Large table-based bulk editor for parameter values",
        "preview": preview_bulk_parameter_table_editor,
        "sample": {
            "title": "Edit Parameters (Bulk)",
            "rows": [
                {
                    "parameter": "Exterior_Sill_Show",
                    "current": "Yes",
                    "new_value": True,
                    "unit": "(tick = Yes, untick = No; dash = keep)",
                    "kind": "bool",
                },
                {
                    "parameter": "Exterior_Trim_Show",
                    "current": "No",
                    "new_value": False,
                    "unit": "(tick = Yes, untick = No; dash = keep)",
                    "kind": "bool",
                },
                {
                    "parameter": "Ext_Sill_Angle",
                    "current": "15.00",
                    "new_value": "15.00",
                    "unit": "degrees",
                    "kind": "text",
                },
                {
                    "parameter": "Ext_Sill_Height",
                    "current": "60",
                    "new_value": "60",
                    "unit": "mm",
                    "kind": "text",
                },
                {
                    "parameter": "Ext_Sill_Width",
                    "current": "25",
                    "new_value": "25",
                    "unit": "mm",
                    "kind": "text",
                },
                {
                    "parameter": "Frame_Setback",
                    "current": "120",
                    "new_value": "120",
                    "unit": "mm",
                    "kind": "text",
                },
            ],
        },
    },
]