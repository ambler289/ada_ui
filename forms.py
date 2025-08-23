# -*- coding: utf-8 -*-
"""
ada_ui.forms — ADa XAML wrapper (names aligned to your XAML)
Exposes: alert, confirm, input_text, big_buttons, SelectFromList.show
"""
from __future__ import annotations
from pathlib import Path

import clr  # type: ignore
clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")
clr.AddReference("WindowsBase")

from System import String
from System.IO import StringReader
from System.Windows import Window, ResourceDictionary, MessageBox, MessageBoxButton, MessageBoxResult
from System.Windows.Markup import XamlReader
from System.Windows.Controls import Button, StackPanel, TextBlock, TextBox, ListBox
from System.Windows import Controls

HERE = Path(__file__).resolve().parent

def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def _parse(xaml_text: str):
    return XamlReader.Parse(StringReader(xaml_text).ReadToEnd())

def _merge_theme(win: Window):
    """Load Controls.xaml and Theme.xaml into the Window resources (in this order)."""
    for name in ("Controls.xaml", "Theme.xaml"):
        path = HERE / name
        if path.exists():
            try:
                rd = _parse(_read(path))
                if isinstance(rd, ResourceDictionary):
                    win.Resources.MergedDictionaries.Add(rd)
            except Exception:
                # best-effort; keep going
                pass

def _load_win(xaml_name: str) -> Window:
    xaml_path = HERE / xaml_name
    if not xaml_path.exists():
        raise IOError("Missing XAML: {}".format(xaml_path))
    win = _parse(_read(xaml_path))
    if not isinstance(win, Window):
        w = Window()
        w.Content = win
        win = w
    _merge_theme(win)
    # 1 = WidthAndHeight
    win.SizeToContent = 1
    win.Topmost = True
    return win

def alert(message, title="Message"):
    try:
        win = _load_win("Alert.xaml")
        try: win.Title = title
        except Exception: pass
        tb = getattr(win, "text_message", None)
        if tb is not None:
            tb.Text = String(str(message))
        ok = getattr(win, "button_ok", None)
        cancel = getattr(win, "button_cancel", None)
        if ok is not None:
            def _ok(sender, e):
                try: win.DialogResult = True
                except Exception: pass
                win.Close()
            ok.Click += _ok
        if cancel is not None:
            def _cancel(sender, e):
                try: win.DialogResult = False
                except Exception: pass
                win.Close()
            cancel.Click += _cancel
        win.ShowDialog()
    except Exception:
        MessageBox.Show(str(message), str(title))

def confirm(message, title="Confirm", ok_text="Yes", cancel_text="No"):
    try:
        win = _load_win("Confirm.xaml")
        try: win.Title = title
        except Exception: pass
        tb = getattr(win, "text_message", None)
        if tb is not None:
            tb.Text = String(str(message))
        yes = getattr(win, "button_yes", None)
        no  = getattr(win, "button_no", None)
        if yes is not None:
            try: yes.Content = ok_text
            except Exception: pass
            def _yes(sender, e):
                try: win.DialogResult = True
                except Exception: pass
                win.Close()
            yes.Click += _yes
        if no is not None:
            try: no.Content = cancel_text
            except Exception: pass
            def _no(sender, e):
                try: win.DialogResult = False
                except Exception: pass
                win.Close()
            no.Click += _no
        rv = win.ShowDialog()
        return bool(rv)
    except Exception:
        res = MessageBox.Show(str(message), str(title), MessageBoxButton.OKCancel)
        return res == MessageBoxResult.OK

def input_text(prompt="Enter text", title="Input"):
    try:
        win = _load_win("InputText.xaml")
        try: win.Title = title
        except Exception: pass
        prompt_tb = getattr(win, "text_prompt", None)
        if prompt_tb is not None:
            prompt_tb.Text = String(str(prompt))
        box = getattr(win, "text_input", None)
        result = {"text": None}
        ok = getattr(win, "button_ok", None)
        cancel = getattr(win, "button_cancel", None)
        if ok is not None:
            def _ok(sender, e):
                result["text"] = box.Text if box is not None else ""
                try: win.DialogResult = True
                except Exception: pass
                win.Close()
            ok.Click += _ok
        if cancel is not None:
            def _cancel(sender, e):
                result["text"] = None
                try: win.DialogResult = False
                except Exception: pass
                win.Close()
            cancel.Click += _cancel
        rv = win.ShowDialog()
        return result["text"] if rv else None
    except Exception:
        return None

def big_buttons(title, items, message=None, cancel=True):
    """Use ButtonBox.xaml; add a button per label into panel_buttons."""
    try:
        win = _load_win("ButtonBox.xaml")
        try: win.Title = title
        except Exception: pass
        # optional top text blocks, if present
        title_tb = getattr(win, "TitleText", None)
        desc_tb  = getattr(win, "text_message", None)
        if message and desc_tb is not None:
            desc_tb.Text = String(str(message))
        host = getattr(win, "panel_buttons", None)
        result = {"choice": None}
        def _make(label):
            def _click(sender, e):
                result["choice"] = label
                try: win.DialogResult = True
                except Exception: pass
                win.Close()
            return _click
        for label in items:
            b = Button()
            b.Content = String(str(label))
            b.Margin = Controls.Thickness(4)
            b.MinWidth = 200
            b.Height = 36
            b.Click += _make(label)
            if host is not None:
                host.Children.Add(b)
        if cancel and getattr(win, "button_cancel", None) is not None:
            def _cancel(sender, e):
                result["choice"] = None
                try: win.DialogResult = False
                except Exception: pass
                win.Close()
            win.button_cancel.Click += _cancel
        ok = getattr(win, "button_ok", None)
        if ok is not None:
            # If OK is present, default it to pick first choice (or just close)
            def _ok(sender, e):
                if result["choice"] is None and items:
                    result["choice"] = items[0]
                try: win.DialogResult = True
                except Exception: pass
                win.Close()
            ok.Click += _ok
        win.ShowDialog()
        return result["choice"]
    except Exception:
        return None

class SelectFromList(object):
    @staticmethod
    def show(items, title="Select", name_attr=None, button_name="OK", multiselect=False):
        try:
            win = _load_win("SelectFromList.xaml")
            try: win.Title = title
            except Exception: pass
            lb = getattr(win, "list_items", None)
            if lb is None:
                return None
            from System.Windows.Controls import SelectionMode
            lb.SelectionMode = SelectionMode.Multiple if multiselect else SelectionMode.Single
            def _label(x):
                if name_attr and hasattr(x, name_attr):
                    return str(getattr(x, name_attr))
                return str(x)
            for it in items:
                lb.Items.Add(_label(it))
            result = {"sel": None, "selm": []}
            ok = getattr(win, "button_ok", None)
            cancel = getattr(win, "button_cancel", None)
            if ok is not None:
                try: ok.Content = button_name
                except Exception: pass
                def _ok(sender, e):
                    if multiselect:
                        result["selm"] = [lb.Items[i] for i in range(lb.Items.Count) if lb.SelectedItems.Contains(lb.Items[i])]
                    else:
                        result["sel"] = lb.SelectedItem
                    try: win.DialogResult = True
                    except Exception: pass
                    win.Close()
                ok.Click += _ok
            if cancel is not None:
                def _cancel(sender, e):
                    try: win.DialogResult = False
                    except Exception: pass
                    win.Close()
                cancel.Click += _cancel
            rv = win.ShowDialog()
            if not rv:
                return None
            if multiselect:
                # map back to original objects by string label
                labels = [str(x) for x in items]
                selected = [str(x) for x in result["selm"]]
                out = [items[labels.index(s)] for s in selected if s in labels]
                return out
            else:
                if result["sel"] is None:
                    return None
                lbl = str(result["sel"])
                labels = [str(x) for x in items]
                return items[labels.index(lbl)] if lbl in labels else None
        except Exception:
            return None
