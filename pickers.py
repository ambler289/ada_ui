# -*- coding: utf-8 -*-
from __future__ import annotations

from . import forms as _forms


def _get_forms_obj():
    return getattr(_forms, "forms", _forms)


def _safe_str(value):
    try:
        if value is None:
            return ""
        return str(value)
    except Exception:
        return ""


def _default_group_key(item):
    if isinstance(item, dict):
        return _safe_str(item.get("category", "Other")) or "Other"
    return "Other"


def _default_to_str(item):
    if isinstance(item, dict):
        name = _safe_str(item.get("name", ""))
        desc = _safe_str(item.get("description", ""))

        if name and desc:
            return "{} - {}".format(name, desc)
        if name:
            return name

    return _safe_str(item)


def pick_list(
    items,
    title="Select",
    prompt=None,
    multiselect=False,
    name_attr=None,
    to_str=None
):
    f = _get_forms_obj()

    # v6 shim supports select_from_list / SelectFromList
    if hasattr(f, "select_from_list"):
        return f.select_from_list(
            items,
            title=title,
            prompt=prompt,
            multiselect=multiselect,
            name_attr=name_attr,
            to_str=to_str
        )

    if hasattr(_forms, "select_from_list"):
        return _forms.select_from_list(
            items,
            title=title,
            prompt=prompt,
            multiselect=multiselect,
            name_attr=name_attr,
            to_str=to_str
        )

    return [] if multiselect else None


def pick_one(items, title="Select", prompt=None, name_attr=None, to_str=None):
    return pick_list(
        items,
        title=title,
        prompt=prompt,
        multiselect=False,
        name_attr=name_attr,
        to_str=to_str
    )


def pick_many(items, title="Select", prompt=None, name_attr=None, to_str=None):
    return pick_list(
        items,
        title=title,
        prompt=prompt,
        multiselect=True,
        name_attr=name_attr,
        to_str=to_str
    )


def pick_checklist(
    items,
    title="ADa",
    prompt="Search and select",
    multiselect=True,
    name_attr=None,
    to_str=None
):
    """
    Searchable checklist-style picker.

    Intended for richer multi-select workflows such as:
    - view selection
    - category selection
    - family/type selection
    - checklist-based review dialogs

    For now this falls back to the standard searchable list picker.
    Later it can be upgraded to a custom checkbox/search UI without
    changing calling scripts.
    """
    if multiselect:
        return pick_many(
            items,
            title=title,
            prompt=prompt,
            name_attr=name_attr,
            to_str=to_str
        )

    return pick_one(
        items,
        title=title,
        prompt=prompt,
        name_attr=name_attr,
        to_str=to_str
    )


def pick_one_grouped(
    items,
    group_key=None,
    title="Select",
    prompt=None,
    name_attr=None,
    to_str=None,
    include_empty_groups=False,
    header_format=u"── {} ─────────────────────"
):
    """
    Group a flat item list into a single searchable picker with visual headers.

    This is a compatibility-friendly grouped-picker helper built on top of the
    existing pick_one() API. It injects lightweight non-data header rows into
    the displayed list, then loops until the user picks a real item or cancels.

    Parameters
    ----------
    items : iterable
        Flat sequence of items to display.
    group_key : callable | str | None
        Determines the group label for each item.
        - callable: called as group_key(item)
        - str: if item is a dict, uses item.get(group_key)
        - None: defaults to dict["category"] or "Other"
    title : str
        Picker title.
    prompt : str | None
        Picker prompt.
    name_attr : str | None
        Passed through to pick_one for compatibility.
    to_str : callable | None
        Display formatter for real items.
    include_empty_groups : bool
        Reserved for future expansion. Currently has no effect because the
        helper operates on a flat item list only.
    header_format : str
        Format string used to render group headers.

    Returns
    -------
    object | None
        The selected real item, or None if cancelled.
    """
    del include_empty_groups  # reserved for future grouped-data support

    real_items = list(items or [])
    display_to_str = to_str or _default_to_str

    def resolve_group(item):
        try:
            if callable(group_key):
                value = group_key(item)
                return _safe_str(value) or "Other"

            if isinstance(group_key, str):
                if isinstance(item, dict):
                    return _safe_str(item.get(group_key, "Other")) or "Other"
                return "Other"

            return _default_group_key(item)
        except Exception:
            return "Other"

    sorted_items = sorted(
        real_items,
        key=lambda x: (
            resolve_group(x).lower(),
            _safe_str(display_to_str(x)).lower()
        )
    )

    grouped_rows = []
    current_group = None

    for item in sorted_items:
        group_name = resolve_group(item)

        if group_name != current_group:
            grouped_rows.append({
                "__picker_group_header__": True,
                "label": header_format.format(group_name)
            })
            current_group = group_name

        grouped_rows.append(item)

    def grouped_to_str(item):
        if isinstance(item, dict) and item.get("__picker_group_header__"):
            return _safe_str(item.get("label", ""))
        return display_to_str(item)

    while True:
        picked = pick_one(
            grouped_rows,
            title=title,
            prompt=prompt,
            name_attr=name_attr,
            to_str=grouped_to_str
        )

        if not picked:
            return None

        if isinstance(picked, dict) and picked.get("__picker_group_header__"):
            continue

        return picked
