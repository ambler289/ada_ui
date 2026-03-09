# -*- coding: utf-8 -*-
from __future__ import annotations

from . import forms as _forms


def _get_forms_obj():
    return getattr(_forms, "forms", _forms)


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