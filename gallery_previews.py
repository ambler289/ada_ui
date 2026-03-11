# -*- coding: utf-8 -*-
from __future__ import annotations


def preview_info_alert(item):
    from .alerts import show_info
    sample = item.get("sample", {})
    show_info(
        sample.get("message", "This is the standard ADa info alert."),
        title=sample.get("title", "ADa UI Preview")
    )


def preview_yes_no(item):
    from .alerts import ask_yes_no
    sample = item.get("sample", {})
    ask_yes_no(
        sample.get("message", "Proceed with the preview?"),
        title=sample.get("title", "ADa UI Preview")
    )


def preview_string_input(item):
    from .inputs import ask_string
    sample = item.get("sample", {})
    ask_string(
        prompt=sample.get("prompt", "Enter some sample text"),
        title=sample.get("title", "ADa UI Preview"),
        default=sample.get("default", "Example")
    )


def preview_number_input(item):
    from .inputs import ask_number
    sample = item.get("sample", {})
    ask_number(
        prompt=sample.get("prompt", "Enter a sample number"),
        title=sample.get("title", "ADa UI Preview"),
        default=sample.get("default", "25")
    )


def preview_pick_one(item):
    from .pickers import pick_one  # type: ignore
    sample = item.get("sample", {})
    pick_one(
        sample.get("items", ["Walls", "Doors", "Windows", "Floors"]),
        title=sample.get("title", "ADa UI Preview"),
        prompt=sample.get("prompt", "Pick one category")
    )


def preview_pick_many(item):
    from .pickers import pick_many  # type: ignore
    sample = item.get("sample", {})
    pick_many(
        sample.get("items", ["Walls", "Doors", "Windows", "Floors"]),
        title=sample.get("title", "ADa UI Preview"),
        prompt=sample.get("prompt", "Pick one or more categories")
    )


def preview_big_buttons(item):
    from .buttons import choose_action  # type: ignore
    sample = item.get("sample", {})
    choose_action(
        sample.get("items", ["Pin Elements", "Unpin Elements", "Cancel"]),
        title=sample.get("title", "ADa UI Preview"),
        message=sample.get("prompt", "Choose an action")
    )


def preview_big_buttons_multi(item):
    from .buttons import choose_actions  # type: ignore
    sample = item.get("sample", {})
    choose_actions(
        sample.get("items", ["Walls", "Doors", "Windows", "Floors"]),
        title=sample.get("title", "ADa UI Preview"),
        message=sample.get("prompt", "Choose one or more options")
    )


def preview_warning_alert(item):
    from .alerts import show_warning
    sample = item.get("sample", {})
    show_warning(
        sample.get("message", "This action may modify elements in the model."),
        title=sample.get("title", "ADa Warning")
    )


def preview_error_alert(item):
    from .alerts import show_error
    sample = item.get("sample", {})
    show_error(
        sample.get("message", "The operation could not be completed."),
        title=sample.get("title", "ADa Error")
    )


def preview_small_buttons(item):
    from .alerts import show_buttons
    sample = item.get("sample", {})
    show_buttons(
        sample.get("buttons", ["Option A", "Option B", "Cancel"]),
        title=sample.get("title", "ADa UI Preview"),
        message=sample.get("message", "Choose an option")
    )


def preview_next_action(item):
    from .alerts import show_buttons
    sample = item.get("sample", {})

    while True:
        result = show_buttons(
            sample.get("buttons", ["Run Again", "Change Mode", "Finish"]),
            title=sample.get("title", "Next Action"),
            message=sample.get("message", "Select what you would like to do next.")
        )

        if result == "Finish" or not result:
            break


def preview_completion_summary(item):
    from .alerts import show_info
    sample = item.get("sample", {})

    show_info(
        sample.get(
            "message",
            "Operation completed successfully.\n\nItems processed: 12\nWarnings: 0\nErrors: 0"
        ),
        title=sample.get("title", "ADa Tool Summary")
    )


def preview_grid_buttons(item):
    from .gridbuttons import choose_grid_buttons

    sample = item.get("sample", {})

    choose_grid_buttons(
        sample.get("items", ["Walls", "Doors", "Windows", "Floors", "Roofs", "Columns"]),
        title=sample.get("title", "ADa UI Preview"),
        message=sample.get("prompt", "Choose a category"),
        columns=3
    )


def preview_bulk_parameter_setter(item):
    from .editors import bulk_parameter_editor
    from .alerts import show_info

    sample = item.get("sample", {})

    result = bulk_parameter_editor(
        sample.get(
            "parameters",
            [
                "Comments",
                "Mark",
                "Fire Rating",
                "Window Type",
                "Jamb Liner",
                "Glazing",
            ],
        ),
        title=sample.get("title", "Bulk Parameter Setter"),
        message=sample.get("prompt", "Choose parameter and value"),
    )

    if not result:
        return None

    show_info(
        "Preview only.\n\nParameter: {}\nValue: {}".format(
            result["parameter"],
            result["value"]
        ),
        title=sample.get("title", "Bulk Parameter Setter"),
    )

    return None


def preview_bulk_parameter_table_editor(item):
    from .editors import bulk_parameter_table_editor

    sample = item.get("sample", {})

    rows = sample.get(
        "rows",
        [
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
    )

    return bulk_parameter_table_editor(
        rows,
        title=sample.get("title", "Edit Parameters (Bulk)")
    )


# ----------------------------------------------------------------------
# New gallery previews
# ----------------------------------------------------------------------

def preview_big_button_launcher(item):
    from .buttons import choose_action  # type: ignore

    sample = item.get("sample", {})
    return choose_action(
        sample.get("items", ["Renumber Sheets", "Rename Views", "Adjust Crops", "Project Startup"]),
        title=sample.get("title", "ADa Action Launcher"),
        message=sample.get("prompt", "Choose an action")
    )

def preview_big_button_toggle_multi(item):
    from .alerts import show_info

    sample = item.get("sample", {})
    prompt = sample.get("prompt", "Choose one or more categories")
    items = sample.get("items", ["Walls", "Floors", "Roofs", "Windows", "Doors"])
    selected = sample.get("selected", ["Walls", "Roofs"])

    lines = [
        "Pattern preview",
        "",
        prompt,
        "",
        "Quick actions:",
        "[All]   [None]   [Go]",
        "",
    ]

    for item_name in items:
        prefix = "✓ " if item_name in selected else "☐ "
        lines.append(prefix + str(item_name))

    show_info(
        "\n".join(lines),
        title=sample.get("title", "ADa Toggle Multi Pattern")
    )

def preview_searchable_checklist_picker(item):
    from .pickers import pick_checklist

    sample = item.get("sample", {})
    return pick_checklist(
        sample.get("items", []),
        title=sample.get("title", "Searchable Checklist Picker"),
        prompt=sample.get("prompt", "Search and select one or more items"),
        multiselect=True
    )

def preview_start_number_picker(item):
    from .buttons import choose_action  # type: ignore

    sample = item.get("sample", {})
    return choose_action(
        sample.get("items", ["Start at 1", "Start at 10", "Start at 100", "Custom..."]),
        title=sample.get("title", "Start Number"),
        message=sample.get("prompt", "Choose a starting number")
    )


def preview_info_result_alert(item):
    return preview_info_alert(item)


def preview_parameter_form(item):
    from .editors import parameter_form

    sample = item.get("sample", {})
    fields = sample.get("fields", [])

    return parameter_form(
        fields,
        title=sample.get("title", "Parameter Form"),
        message=sample.get("message", "Edit the example fields below.")
    )


def preview_folder_creation_report(item):
    return preview_info_alert(item)


def preview_progress_window(item):
    from .alerts import show_info

    sample = item.get("sample", {})
    title = sample.get("title", "Progress")
    message = sample.get("message", "Processing...")
    current = sample.get("current", 0)
    total = sample.get("total", 0)

    progress_line = "Progress: {} / {}".format(current, total) if total else "Progress: in progress"

    show_info(
        "{}\n\n{}".format(message, progress_line),
        title=title
    )


def preview_confirmation_dialog(item):
    return preview_yes_no(item)