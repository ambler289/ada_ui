#! python3
# ada_bootstrap.py — CPython-safe ADa UI shim (no pyrevit.forms dependency)
import os, site, sys
from pathlib import Path

IS_CPYTHON = (sys.implementation.name == "cpython")

# --- ada_bootstrap: replace _add + ensure_paths + call ---

from pathlib import Path
import os, sys

def _add_first(p):
    """Insert path at the FRONT of sys.path (ahead of user site-packages)."""
    if not p:
        return
    p = Path(p)
    if p.is_dir():
        s = str(p)
        if s not in sys.path:
            sys.path.insert(0, s)

def ensure_paths():
    """
    Make third-party libs discoverable, preferring:
      1) ADA_THIRDPARTY share (if set) -> common + win-amd64-cpXY
      2) This extension's lib/thirdparty -> common + win-amd64-cpXY
      3) Sibling ADa extensions under %APPDATA% / %LOCALAPPDATA%
    """
    # cp tag: cp312, cp311, etc.
    tag  = "cp{}{}".format(sys.version_info.major, sys.version_info.minor)
    plat = "win-amd64-" + tag

    # 1) Central override
    root = os.getenv("ADA_THIRDPARTY")
    if root:
        _add_first(Path(root) / "common")
        _add_first(Path(root) / plat)

    # 2) This extension root (walk up to *.extension)
    ext = Path(__file__).resolve()
    while ext and not ext.name.endswith(".extension"):
        ext = ext.parent
    if ext:
        _add_first(ext / "lib")
        tp = ext / "lib" / "thirdparty"
        _add_first(tp / "common")
        _add_first(tp / plat)

    # 3) Sibling extensions under roaming/local
    appdata      = Path(os.environ.get("APPDATA",      Path.home() / "AppData/Roaming"))
    localappdata = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    for base in (appdata, localappdata):
        exts_root = base / "pyRevit" / "Extensions"
        for extname in ("ADa-Manage.extension", "ADa-Tools.extension"):
            er = exts_root / extname
            _add_first(er / "lib")
            tp = er / "lib" / "thirdparty"
            _add_first(tp / "common")
            _add_first(tp / plat)

# call once on import
ensure_paths()

# ---- WinForms base (works on CPython via pythonnet) ----
try:
    import clr
    clr.AddReference("System")
    clr.AddReference("System.Windows.Forms")
    clr.AddReference("System.Drawing")
    from System.Windows.Forms import ( #type:ignore
        Form, ListBox, Button, DialogResult, DockStyle, FormBorderStyle,
        SelectionMode, Label, TextBox, AnchorStyles, FormStartPosition,
        MessageBox, MessageBoxButtons, OpenFileDialog, SaveFileDialog,
        FolderBrowserDialog
    )
    from System.Drawing import Size, Point #type:ignore
    _WINFORMS_OK = True
except Exception:
    _WINFORMS_OK = False

# ---- Revit selection helpers (best-effort; safe fallbacks) ----
def _try_uidoc():
    """Return Revit UIDocument if available under current host; else None."""
    try:
        # pyRevit's revit wrapper is usually present in both IPy and CPython
        from pyrevit import revit  # type: ignore
        return revit.uidoc
    except Exception:
        pass
    try:
        # Direct RevitServices path (Dynamo/other hosts)
        import clr
        clr.AddReference("RevitServices")
        from RevitServices.Persistence import DocumentManager  # type: ignore
        return DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
    except Exception:
        return None

# -----------------------------
# UI building blocks
# -----------------------------
def _wf_select_from_list():
    class _WFSelect(object):
        @staticmethod
        def show(options, title="Select", button_name="OK",
                 multiselect=False, width=520, height=420):
            if not _WINFORMS_OK:
                return [] if multiselect else None
            form = Form()
            form.Text = str(title or "Select")
            form.FormBorderStyle = FormBorderStyle.FixedDialog
            form.MinimizeBox = False; form.MaximizeBox = False
            form.StartPosition = FormStartPosition.CenterScreen
            form.Size = Size(int(width), int(height))

            lb = ListBox()
            lb.Dock = DockStyle.Top
            lb.Height = int(height) - 80
            lb.SelectionMode = SelectionMode.MultiExtended if multiselect else SelectionMode.One
            for opt in (options or []):
                lb.Items.Add(str(opt))
            form.Controls.Add(lb)

            ok = Button(); ok.Text = str(button_name or "OK"); ok.Width = 100
            ok.Location = Point(form.ClientSize.Width - 220, form.ClientSize.Height - 60)
            ok.Anchor = AnchorStyles.Bottom | AnchorStyles.Right
            ok.DialogResult = DialogResult.OK; form.AcceptButton = ok
            form.Controls.Add(ok)

            cancel = Button(); cancel.Text = "Cancel"; cancel.Width = 100
            cancel.Location = Point(form.ClientSize.Width - 110, form.ClientSize.Height - 60)
            cancel.Anchor = AnchorStyles.Bottom | AnchorStyles.Right
            cancel.DialogResult = DialogResult.Cancel; form.CancelButton = cancel
            form.Controls.Add(cancel)

            if form.ShowDialog() != DialogResult.OK:
                return [] if multiselect else None
            return [lb.Items[i] for i in lb.SelectedIndices] if multiselect else lb.SelectedItem
    return _WFSelect

def _wf_ask_for_string():
    # Prefer branded v6 input_box if present
    try:
        m = __import__("ada_brandforms_v6", fromlist=["input_box"])
        def ask_for_string(prompt="", title="Input", default=""):
            ok, text = m.input_box(title=title, label=prompt, default_text=str(default or ""))
            return text if ok else None
        return ask_for_string
    except Exception:
        pass

    class _WF(object):
        @staticmethod
        def ask_for_string(prompt="", title="Input", default=""):
            if not _WINFORMS_OK:
                return None
            form = Form()
            form.Text = str(title or "Input")
            form.FormBorderStyle = FormBorderStyle.FixedDialog
            form.MinimizeBox = False; form.MaximizeBox = False
            form.StartPosition = FormStartPosition.CenterScreen
            form.Size = Size(460, 160)

            lbl = Label(); lbl.Text = str(prompt or "Enter value:"); lbl.AutoSize = True
            lbl.Location = Point(12, 12); form.Controls.Add(lbl)

            tb = TextBox(); tb.Text = str(default or ""); tb.Width = form.ClientSize.Width - 24
            tb.Location = Point(12, 36)
            tb.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right
            form.Controls.Add(tb)

            ok = Button(); ok.Text = "OK"; ok.Width = 100
            ok.Location = Point(form.ClientSize.Width - 220, form.ClientSize.Height - 50)
            ok.Anchor = AnchorStyles.Bottom | AnchorStyles.Right
            ok.DialogResult = DialogResult.OK; form.AcceptButton = ok
            form.Controls.Add(ok)

            cancel = Button(); cancel.Text = "Cancel"; cancel.Width = 100
            cancel.Location = Point(form.ClientSize.Width - 110, form.ClientSize.Height - 50)
            cancel.Anchor = AnchorStyles.Bottom | AnchorStyles.Right
            cancel.DialogResult = DialogResult.Cancel; form.CancelButton = cancel
            form.Controls.Add(cancel)

            return tb.Text if form.ShowDialog() == DialogResult.OK else None
    return _WF.ask_for_string

def _wrap_v6_alert():
    try:
        m = __import__("ada_brandforms_v6", fromlist=["alert","ask_yes_no","input_box"])
        def _alert(msg, title="Message", **kwargs):
            btns = None
            if any(k in kwargs for k in ("yes","no")):       btns = ["Yes","No"]
            elif any(k in kwargs for k in ("ok","cancel")):  btns = ["OK","Cancel"]
            res = m.alert(str(msg), title=str(title), buttons=btns or ("OK",))
            if btns == ["Yes","No"]:   return True if res == "Yes" else False
            if btns == ["OK","Cancel"]: return True if res == "OK" else False
            return res
        def _ask_yes_no(msg, title="Confirm"):
            return True if _alert(msg, title=title, yes=True, no=True) else False
        def _input_box(title, label, default_text=""):
            ok, text = m.input_box(title=title, label=label, default_text=str(default_text or ""))
            return (ok, text)
        return _alert, _ask_yes_no, _input_box
    except Exception:
        def _alert(msg, title="Message", **kwargs):
            if not _WINFORMS_OK: return True
            buttons = MessageBoxButtons.OK
            if any(k in kwargs for k in ("yes","no")):       buttons = MessageBoxButtons.YesNo
            elif any(k in kwargs for k in ("ok","cancel")):  buttons = MessageBoxButtons.OKCancel
            res = MessageBox.Show(str(msg), str(title), buttons)
            # Normalize to bool for Yes/No and OK/Cancel
            return True if ('yes' in kwargs or 'no' in kwargs or 'ok' in kwargs or 'cancel' in kwargs) and res.ToString() in ("Yes","OK") else res
        def _ask_yes_no(msg, title="Confirm"):
            return True if _alert(msg, title=title, yes=True, no=True) else False
        def _input_box(title, label, default_text=""):
            txt = _wf_ask_for_string()(label, title, default_text)
            return (txt is not None, txt)
        return _alert, _ask_yes_no, _input_box

# ---- File/folder pickers (CPython-safe) ----
def _pick_file(filters=None, multi=False):
    if not _WINFORMS_OK:
        return [] if multi else None
    dlg = OpenFileDialog()
    dlg.Multiselect = bool(multi)
    if filters:
        # filters: list of ("Display", "*.ext;*.ext2")
        dlg.Filter = "|".join(["{}|{}".format(n, p) for (n,p) in filters])
    result = dlg.ShowDialog()
    if result != DialogResult.OK:
        return [] if multi else None
    return list(dlg.FileNames) if multi else dlg.FileName

def _save_file(default_name="", filter_str="All files (*.*)|*.*"):
    if not _WINFORMS_OK:
        return None
    dlg = SaveFileDialog()
    if default_name: dlg.FileName = str(default_name)
    if filter_str:   dlg.Filter = str(filter_str)
    return dlg.FileName if dlg.ShowDialog() == DialogResult.OK else None

def _pick_folder():
    if not _WINFORMS_OK:
        return None
    dlg = FolderBrowserDialog()
    return dlg.SelectedPath if dlg.ShowDialog() == DialogResult.OK else None

# ---- Element pickers (best-effort via UIDocument) ----
def _pick_element(prompt="Pick element"):
    uidoc = _try_uidoc()
    if not uidoc:
        return None
    try:
        from Autodesk.Revit.UI.Selection import ObjectType  # type: ignore
        ref = uidoc.Selection.PickObject(ObjectType.Element, prompt)
        return uidoc.Document.GetElement(ref.ElementId) if ref else None
    except Exception:
        return None

def _pick_elements(prompt="Pick elements"):
    uidoc = _try_uidoc()
    if not uidoc:
        return []
    try:
        from Autodesk.Revit.UI.Selection import ObjectType  # type: ignore
        refs = uidoc.Selection.PickObjects(ObjectType.Element, prompt)
        doc = uidoc.Document
        return [doc.GetElement(r.ElementId) for r in (refs or [])]
    except Exception:
        return []

# ---- Public forms object ----
# ---- ADa big button box (non-breaking wrapper) ----
def _big_button_box(title="Choose", buttons=None, cancel=True):
    """ADa-themed vertical big buttons (uses ada_brandforms_v6 if present);
    returns the clicked label or None."""
    buttons = list(buttons or [])
    if not buttons:
        return None

    # --- Preferred: build a v6-themed dialog with big buttons ---
    try:
        v6 = __import__(
            "ada_brandforms_v6",
            fromlist=["_AdaDialog", "StackPanel", "Button",
                      "Thickness", "Colors", "SolidColorBrush"]
        )
        # Base ADa dialog (gradient header, dark body)
        dlg = v6._AdaDialog(str(title or "Choose"), "", ["Cancel"] if cancel else [])

        # Replace the dialog body with a vertical stack of large buttons
        outer_border = dlg.Content            # Border
        root_grid    = outer_border.Child     # Grid (Header / Body / Footer)
        body_border  = root_grid.Children[1]  # Body border (row 1)

        StackPanel        = getattr(v6, "StackPanel")
        Button            = getattr(v6, "Button")
        Thickness         = getattr(v6, "Thickness")
        Colors            = getattr(v6, "Colors")
        SolidColorBrush   = getattr(v6, "SolidColorBrush")

        panel = StackPanel()
        panel.Orientation = 1  # Vertical
        panel.Margin = Thickness(24, 12, 24, 12)
        body_border.Child = panel

        selected = {"v": None}

        def add_big(label, primary=False):
            b = Button()
            b.Content = str(label)
            b.Height = 52
            b.Margin = Thickness(0, 0, 0, 10)
            b.BorderThickness = Thickness(0)
            # Stretch full width
            try:
                # 1 = HorizontalAlignment.Stretch in WPF
                b.HorizontalAlignment = 1
            except Exception:
                pass
            # Theme colors (blue primary, pink secondary)
            try:
                ADA_BLUE = getattr(v6, "ADA_BLUE")
                ADA_PINK = getattr(v6, "ADA_PINK")
                b.Background = SolidColorBrush(ADA_BLUE if primary else ADA_PINK)
                b.Foreground = SolidColorBrush(Colors.White)
            except Exception:
                pass

            def _click(sender, e, _val=str(label)):
                selected["v"] = _val
                try:
                    dlg.DialogResult = True
                except Exception:
                    pass
                dlg.Close()

            b.Click += _click
            panel.Children.Add(b)

        # First button “primary”, rest “secondary”
        for i, lab in enumerate(buttons):
            add_big(lab, primary=(i == 0))

        dlg.ShowDialog()
        return selected["v"]

    except Exception:
        # --- Fallback: plain WinForms big buttons (still one-click) ---
        if not _WINFORMS_OK:
            return None
        try:
            from System.Windows.Forms import (  # type: ignore
                Form, Button as WFButton, DialogResult, FormBorderStyle, FormStartPosition
            )
            from System.Drawing import Size, Point, Font, FontStyle  # type: ignore

            form = Form()
            form.Text = str(title or "Choose")
            form.FormBorderStyle = FormBorderStyle.FixedDialog
            form.StartPosition = FormStartPosition.CenterScreen
            h = 40 + (len(buttons) * 64)
            form.Size = Size(460, max(180, h))

            selected = {"v": None}
            top = 20
            for lab in buttons:
                btn = WFButton()
                btn.Text = str(lab)
                btn.Size = Size(400, 52)
                btn.Location = Point(20, top)
                top += 60
                try:
                    btn.Font = Font("Segoe UI", 12, FontStyle.Bold)
                except Exception:
                    pass

                def _h(sender, e, _val=str(lab)):
                    selected["v"] = _val
                    form.DialogResult = DialogResult.OK
                    form.Close()

                btn.Click += _h
                form.Controls.Add(btn)

            if not cancel:
                form.ControlBox = False

            return selected["v"] if form.ShowDialog() == DialogResult.OK else None
        except Exception:
            return None

class _Forms(object):
    pass

def get_forms():
    f = _Forms()

    # v6-styled alert/input wrappers
    alert, ask_yes_no, input_box = _wrap_v6_alert()
    f.alert       = staticmethod(alert)
    f.ask_yes_no  = staticmethod(ask_yes_no)
    f.input_box   = staticmethod(input_box)

    # Text input (WinForms fallback wrapper you already have)
    f.ask_for_string = staticmethod(_wf_ask_for_string())

    # List selection:
    # 1) try v6's select_from_list if present, else 2) WinForms fallback object
    try:
        import ada_brandforms_v6 as v6  # type: ignore
        if hasattr(v6, "select_from_list"):
            # expose v6 directly to keep behavior identical across tools
            f.SelectFromList = v6.select_from_list
        else:
            f.SelectFromList = _wf_select_from_list()
    except Exception:
        f.SelectFromList = _wf_select_from_list()

    # optional: lowercase alias some scripts use
    f.select_from_list = f.SelectFromList

    # Big button chooser (the new ADa-themed one; WinForms fallback inside)
    f.big_button_box = staticmethod(_big_button_box)

    # Convenience pickers (your existing helpers)
    f.pick_file     = staticmethod(_pick_file)
    f.save_file     = staticmethod(_save_file)
    f.pick_folder   = staticmethod(_pick_folder)
    f.pick_element  = staticmethod(_pick_element)
    f.pick_elements = staticmethod(_pick_elements)

    f.__version__ = "ada_shim_cpython_v2"
    return f

forms = get_forms()