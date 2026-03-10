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
    from .alerts import show_buttons  # small button chooser
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