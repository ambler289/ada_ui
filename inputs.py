# -*- coding: utf-8 -*-
from __future__ import annotations

from . import forms as _forms


def _get_forms_obj():
    return getattr(_forms, "forms", _forms)


def ask_string(prompt="Enter value", title="Input", default=""):
    f = _get_forms_obj()

    if hasattr(f, "ask_for_string"):
        return f.ask_for_string(
            prompt=str(prompt),
            title=str(title),
            default=str(default or "")
        )

    if hasattr(_forms, "input_box"):
        ok, txt = _forms.input_box(str(title), str(prompt), str(default or ""))
        return txt if ok else None

    return None


def ask_multiline(prompt="Enter value", title="Input", default=""):
    # Placeholder for future custom multiline dialog
    return ask_string(prompt=prompt, title=title, default=default)


def ask_number(prompt="Enter number", title="Input", default=""):
    txt = ask_string(prompt=prompt, title=title, default=str(default or ""))
    if txt is None:
        return None

    txt = str(txt).strip()
    if not txt:
        return None

    try:
        if "." in txt:
            return float(txt)
        return int(txt)
    except Exception:
        return None

def ask_start_number(title="Start Number"):
    from .buttons import choose_action

    choice = choose_action(
        ["Start at 1", "Start at 10", "Start at 100", "Custom..."],
        title=title,
        message="Choose a starting number"
    )

    if choice == "Start at 1":
        return "1"
    if choice == "Start at 10":
        return "10"
    if choice == "Start at 100":
        return "100"
    if choice == "Custom...":
        return ask_string("Enter starting number", title=title, default="1")
    return None

def ask_folder_and_options(title="Select Folder", checkbox_label="Include subfolders", checkbox_default=False):
    """
    Small branded options dialog for simple batch settings.

    Returns:
        {"checked": bool} on OK
        None on cancel
    """
    try:
        from .buttons import choose_action
    except Exception:
        choose_action = None

    # If you already have a branded forms helper that supports yes/no or custom
    # layouts, swap this implementation later. For now keep it simple and ADa-safe.
    if choose_action:
        choice = choose_action(
            ["OK", "Cancel"],
            title=title,
            message=checkbox_label + ("\n\nDefault: On" if checkbox_default else "\n\nDefault: Off")
        )
        if choice != "OK":
            return None

    # Fallback to current simple path until a richer branded checkbox dialog exists.
    try:
        import clr  # type: ignore
        clr.AddReference("System")
        clr.AddReference("System.Drawing")
        clr.AddReference("System.Windows.Forms")

        from System.Drawing import Point, Size  # type: ignore
        from System.Windows.Forms import (  # type: ignore
            Button,
            CheckBox,
            DialogResult,
            Form,
            FormBorderStyle,
            FormStartPosition,
        )

        form = Form()
        form.Text = title
        form.Width = 360
        form.Height = 150
        form.FormBorderStyle = FormBorderStyle.FixedDialog
        form.StartPosition = FormStartPosition.CenterScreen
        form.MinimizeBox = False
        form.MaximizeBox = False
        form.TopMost = True

        chk = CheckBox()
        chk.Text = checkbox_label
        chk.Checked = bool(checkbox_default)
        chk.Location = Point(20, 20)
        chk.Size = Size(250, 24)

        btn_ok = Button()
        btn_ok.Text = "OK"
        btn_ok.Width = 100
        btn_ok.Location = Point(60, 60)
        btn_ok.DialogResult = DialogResult.OK

        btn_cancel = Button()
        btn_cancel.Text = "Cancel"
        btn_cancel.Width = 100
        btn_cancel.Location = Point(170, 60)
        btn_cancel.DialogResult = DialogResult.Cancel

        form.Controls.Add(chk)
        form.Controls.Add(btn_ok)
        form.Controls.Add(btn_cancel)
        form.AcceptButton = btn_ok
        form.CancelButton = btn_cancel

        result = form.ShowDialog()
        if result != DialogResult.OK:
            return None

        return {"checked": bool(chk.Checked)}

    except Exception:
        return None
