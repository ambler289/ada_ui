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

    # new previews
    preview_big_button_launcher,
    preview_searchable_checklist_picker,
    preview_start_number_picker,
    preview_info_result_alert,
    preview_parameter_form,
    preview_folder_creation_report,
    preview_progress_window,
    preview_confirmation_dialog,
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
        "name": "Confirmation Dialog",
        "category": "Alerts",
        "description": "ADa confirm/cancel prompt for destructive or bulk actions.",
        "preview": preview_confirmation_dialog,
        "sample": {
            "title": "Confirm Action",
            "message": "Delete 34 sheets?\n\nThis action cannot be undone.",
        },
    },
    {
        "name": "Info / Result Alert",
        "category": "Alerts",
        "description": "General purpose ADa success/info dialog for finished operations.",
        "preview": preview_info_result_alert,
        "sample": {
            "title": "ADa Tool Summary",
            "message": "Project parameters updated successfully.\n\nWarnings: 0\nErrors: 0",
        },
    },
    {
        "name": "Folder Creation Report",
        "category": "Alerts",
        "description": "Multi-line report dialog showing created folders and skipped items.",
        "preview": preview_folder_creation_report,
        "sample": {
            "title": "Project Folders",
            "message": (
                "Folders created:\n"
                "01_Admin\n"
                "02_Concept\n"
                "03_Design\n\n"
                "Details:\n"
                "04_Consultants already existed\n"
                "05_Renders created"
            ),
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
        "name": "Start Number Picker",
        "category": "Inputs",
        "description": "Preset number chooser with optional custom entry.",
        "preview": preview_start_number_picker,
        "sample": {
            "title": "Start Number",
            "prompt": "Choose a starting number",
            "items": ["Start at 1", "Start at 10", "Start at 100", "Custom..."],
            "default": "1",
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
        "name": "Searchable Checklist Picker",
        "category": "Pickers",
        "description": "Searchable checkbox picker with Select All / None and OK / Cancel.",
        "preview": preview_searchable_checklist_picker,
        "sample": {
            "title": "Select Views",
            "prompt": "Search and select one or more views",
            "items": [
                "SEC-01 Section",
                "SEC-02 Section",
                "NEW-01 Floor Plan",
                "NEW-02 Floor Plan",
                "WORK-01 Roof Plan",
                "WORK-02 Drainage Plan",
            ],
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
        "name": "Big Button Launcher",
        "category": "Buttons",
        "description": "Large branded launcher for choosing one primary action.",
        "preview": preview_big_button_launcher,
        "sample": {
            "title": "ADa Action Launcher",
            "prompt": "Choose an action",
            "items": ["Renumber Sheets", "Rename Views", "Adjust Crops", "Project Startup"],
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
        "name": "Grid Button Chooser",
        "category": "Buttons Layouts",
        "description": "Compact grid of selectable buttons",
        "preview": preview_grid_buttons,
        "sample": {
            "title": "ADa UI Preview",
            "prompt": "Choose a category",
            "items": ["Walls", "Doors", "Windows", "Floors", "Roofs", "Columns"]
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
        "name": "Progress Window",
        "category": "Workflows",
        "description": "Progress/status window pattern for longer-running tools.",
        "preview": preview_progress_window,
        "sample": {
            "title": "Processing Views",
            "message": "Processing 12 of 36 views...",
            "current": 12,
            "total": 36,
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
    {
        "name": "Parameter Form",
        "category": "Editors",
        "description": "Structured multi-field form for project or parameter data entry.",
        "preview": preview_parameter_form,
        "sample": {
            "title": "Project Parameters",
            "fields": [
                {"label": "Project Number", "value": "25-001"},
                {"label": "Client Name", "value": "Sample Client"},
                {"label": "Street", "value": "123 Example Road"},
                {"label": "City", "value": "Wellington"},
            ],
        },
    },
]