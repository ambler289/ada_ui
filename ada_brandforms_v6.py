
# ada_brandforms_v6.py — ADa-branded dialogs with rounded corners & shadow (CPython3 + pythonnet 3.x)
# Public API: alert(msg, title="..."); ask_yes_no(msg, title="..."); input_box(title, label, default_text="")
__ada_forms_version__ = "v6-rounded-2025-08-18"

import clr
clr.AddReference("PresentationCore")
clr.AddReference("PresentationFramework")
clr.AddReference("WindowsBase")

from System import String  # type: ignore
from System.Windows import (  # type: ignore
    Window, WindowStartupLocation, Thickness, HorizontalAlignment, VerticalAlignment,
    SizeToContent, WindowStyle, ResizeMode, TextWrapping, CornerRadius
)
from System.Windows.Controls import (  # type: ignore
    Grid, RowDefinition, ColumnDefinition, TextBlock, Button, Border, StackPanel, TextBox, Orientation, 
    ListBox, ListBoxItem, ScrollViewer, SelectionMode
)
from System.Windows.Media import (  # type: ignore
    SolidColorBrush, LinearGradientBrush, GradientStop, GradientStopCollection,
    Color, Colors
)
from System.Windows.Input import MouseButtonState, Key  # type: ignore


# ── ADa brand colors ─────────────────────────────────────────────────────
ADA_BLUE = Color.FromRgb(0x5C, 0x7C, 0xFA)   # #5C7CFA
ADA_PINK = Color.FromRgb(0xF7, 0x59, 0xC0)   # #F759C0
BG_DARK  = Color.FromRgb(0x1F, 0x23, 0x2B)
FG_LIGHT = Color.FromRgb(0xE8, 0xEA, 0xED)


def _grad_header():
    gsc = GradientStopCollection()
    gsc.Add(GradientStop(ADA_BLUE, 0.0))
    gsc.Add(GradientStop(ADA_PINK, 1.0))
    brush = LinearGradientBrush()
    brush.GradientStops = gsc
    return brush  # default is relative box; visually left→right with these stops


def _ws_none():
    # Handle environments where enum member is exposed as None vs None_
    try:
        return getattr(WindowStyle, "None")
    except AttributeError:
        try:
            return getattr(WindowStyle, "None_")
        except AttributeError:
            return WindowStyle(0)


class _AdaDialog(Window):
    """Skinnable dialog with rounded corners, gradient header, and soft shadow."""

    def __init__(self, title_text, body_text, buttons):
        Window.__init__(self)

        # ── Remove OS chrome, allow transparency so rounded corners cut through ──
        self.WindowStyle = _ws_none()
        self.ResizeMode = ResizeMode.NoResize
        self.AllowsTransparency = True
        self.ShowInTaskbar = False
        self.Title = ""
        # The *window* background must be transparent; the outer border will paint the card
        from System.Windows.Media import Colors as _Colors #type:ignore
        self.Background = SolidColorBrush(_Colors.Transparent)

        # Window behavior
        self.SizeToContent = SizeToContent.WidthAndHeight
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.Padding = Thickness(0)
        self._result = None

        # ── Outer rounded shell (defines visible shape & background) ────────────
        outer = Border()
        outer.CornerRadius = CornerRadius(12)
        outer.Background = SolidColorBrush(BG_DARK)
        outer.SnapsToDevicePixels = True
        outer.Padding = Thickness(0)

        # Optional soft drop shadow
        try:
            from System.Windows.Media.Effects import DropShadowEffect  # type: ignore
            shadow = DropShadowEffect()
            shadow.BlurRadius = 20
            shadow.Opacity = 0.35
            shadow.Direction = 270
            shadow.ShadowDepth = 0
            outer.Effect = shadow
        except Exception:
            pass  # effect unavailable → continue without shadow

        # ── Root grid inside the rounded shell ──────────────────────────────────
        root = Grid()
        root.RowDefinitions.Add(RowDefinition())  # header
        root.RowDefinitions.Add(RowDefinition())  # body
        root.RowDefinitions.Add(RowDefinition())  # footer
        outer.Child = root
        self.Content = outer

        # ── Header (rounded top only) ───────────────────────────────────────────
        header = Border()
        header.Background = _grad_header()
        header.CornerRadius = CornerRadius(12, 12, 0, 0)
        Grid.SetRow(header, 0)
        headerGrid = Grid()
        headerGrid.ColumnDefinitions.Add(ColumnDefinition())  # title
        headerGrid.ColumnDefinitions.Add(ColumnDefinition())  # close
        header.Child = headerGrid
        root.Children.Add(header)

        title_tb = TextBlock()
        title_tb.Text = str(title_text or "")
        title_tb.Margin = Thickness(20, 14, 20, 14)
        title_tb.Foreground = SolidColorBrush(FG_LIGHT)
        title_tb.FontSize = 22
        title_tb.VerticalAlignment = VerticalAlignment.Center
        headerGrid.Children.Add(title_tb)

        btn_close = Button()
        btn_close.Content = "✕"
        btn_close.Width = 36
        btn_close.Height = 28
        btn_close.Margin = Thickness(0, 10, 10, 10)
        btn_close.HorizontalAlignment = HorizontalAlignment.Right
        btn_close.VerticalAlignment = VerticalAlignment.Center
        btn_close.Background = SolidColorBrush(ADA_PINK)
        btn_close.Foreground = SolidColorBrush(Colors.White)
        btn_close.BorderThickness = Thickness(0)
        btn_close.Click += lambda s, e: self._close(False)
        Grid.SetColumn(btn_close, 1)
        headerGrid.Children.Add(btn_close)

        # Drag window by header
        def _drag(sender, e):
            if e.LeftButton == MouseButtonState.Pressed:
                try:
                    self.DragMove()
                except:
                    pass
        header.MouseLeftButtonDown += _drag

        # ── Body ────────────────────────────────────────────────────────────────
        body_border = Border()
        body_border.Margin = Thickness(24, 20, 24, 0)
        body_border.Background = SolidColorBrush(BG_DARK)
        Grid.SetRow(body_border, 1)
        root.Children.Add(body_border)

        body_tb = TextBlock()
        body_tb.Text = str(body_text or "")
        body_tb.TextWrapping = TextWrapping.Wrap
        body_tb.Foreground = SolidColorBrush(FG_LIGHT)
        body_tb.FontSize = 16
        body_border.Child = body_tb

        # ── Footer (rounded bottom only) ───────────────────────────────────────
        btn_row = Border()
        btn_row.Margin = Thickness(24, 18, 24, 20)
        btn_row.Background = SolidColorBrush(BG_DARK)
        btn_row.CornerRadius = CornerRadius(0, 0, 12, 12)
        Grid.SetRow(btn_row, 2)
        root.Children.Add(btn_row)

        btn_panel = StackPanel()
        btn_panel.Orientation = Orientation.Horizontal
        btn_panel.HorizontalAlignment = HorizontalAlignment.Right
        btn_row.Child = btn_panel

        def make_btn(label, is_primary=False):
            b = Button()
            b.Content = String(label)
            b.Width = 130
            b.Height = 36
            b.Margin = Thickness(8, 0, 0, 0)
            b.BorderThickness = Thickness(0)
            b.Background = SolidColorBrush(ADA_BLUE if is_primary else ADA_PINK)
            b.Foreground = SolidColorBrush(Colors.White)
            return b

        for i, lab in enumerate(buttons or ("OK",)):
            b = make_btn(lab, is_primary=(i == 0))
            b.Click += (lambda s, e, lab=lab: self._close(lab))
            btn_panel.Children.Add(b)

        # Keyboard shortcuts
        def _key(sender, e):
            if e.Key == Key.Escape:
                self._close(False)
            elif e.Key == Key.Enter:
                self._close((buttons or ("OK",))[0])
        self.KeyDown += _key

        try:
            self.Margin = Thickness(8)
        except Exception:
            pass

    def _close(self, value):
        self._result = value
        try:
            self.DialogResult = True
        except:
            pass
        self.Close()


# ── Public helpers ───────────────────────────────────────────────────────

def alert(msg, title="Message", buttons=("OK",)):
    """Show a simple message dialog. Returns the clicked label or False if closed with ESC/✕."""
    dlg = _AdaDialog(title, msg, list(buttons))
    dlg.ShowDialog()
    return dlg._result


def ask_yes_no(msg, title="Confirm"):
    """Return True for 'Yes', False for 'No' or close."""
    res = alert(msg, title, buttons=("Yes", "No"))
    return True if res == "Yes" else False


def input_box(title, label, default_text=""):
    """Headerless single-line input box (returns (True, text) on OK; (False, None) on cancel)."""
    dlg = _AdaDialog(title, "", ["OK", "Cancel"])

    # Replace the body with label + textbox stack
    body_border = dlg.Content.Child.Children[1] if hasattr(dlg.Content, "Child") else dlg.Content.Children[1]
    sp = StackPanel()
    sp.Orientation = Orientation.Vertical
    body_border.Child = sp

    lbl = TextBlock()
    lbl.Text = str(label or "")
    lbl.Foreground = SolidColorBrush(FG_LIGHT)
    lbl.FontSize = 16
    lbl.Margin = Thickness(0, 0, 0, 10)
    sp.Children.Add(lbl)

    tb = TextBox()
    tb.Text = str(default_text or "")
    tb.FontSize = 16
    tb.Height = 34
    sp.Children.Add(tb)

    # Enter = OK when focus in textbox
    def _tb_key(sender, e):
        if e.Key == Key.Enter:
            dlg._close("OK")
    tb.KeyDown += _tb_key

    def _loaded(sender, e):
        try: tb.Focus()
        except: pass
    dlg.Loaded += _loaded

    dlg.ShowDialog()
    return (dlg._result == "OK", tb.Text if dlg._result == "OK" else None)

def select_from_list(
    items,
    title="Select",
    prompt=None,
    multiselect=False,
    ok_label="OK",
    cancel_label="Cancel",
    name_attr=None,          # if provided, use obj.<name_attr> for display
    to_str=None              # optional callable to format display text
):
    """
    ADa-themed list selector.
    - items: list of arbitrary Python/.NET objects; returns originals.
    - multiselect: True for multi; False for single.
    - name_attr / to_str let you control display text.
    Returns:
      - single-select: the selected object or None
      - multi-select:  list of selected objects (possibly empty if cancelled)
    """
    # Build dialog with OK/Cancel footer
    dlg = _AdaDialog(title, "", [ok_label, cancel_label])

    # Replace the body with our prompt + filter + list
    outer_border = dlg.Content                                    # Border
    root_grid = outer_border.Child                                # Grid
    body_border = root_grid.Children[1]                           # Border (body)

    container = StackPanel()
    container.Orientation = Orientation.Vertical
    body_border.Child = container

    if prompt:
        lbl = TextBlock()
        lbl.Text = str(prompt)
        lbl.Foreground = SolidColorBrush(FG_LIGHT)
        lbl.FontSize = 16
        lbl.Margin = Thickness(0, 0, 0, 10)
        container.Children.Add(lbl)

    # Filter box
    filter_tb = TextBox()
    filter_tb.FontSize = 15
    filter_tb.Height = 30
    filter_tb.Margin = Thickness(0, 0, 0, 8)
    container.Children.Add(filter_tb)

    # List box
    lb = ListBox()
    lb.SelectionMode = SelectionMode.Multiple if multiselect else SelectionMode.Single
    # make it comfortably big; dialog itself sizes to content
    lb.MinHeight = 220
    lb.MaxHeight = 500
    container.Children.Add(lb)

    # Helpers to render + map items
    def _display(o):
        if to_str:
            try:
                return str(to_str(o))
            except Exception:
                pass
        if name_attr and hasattr(o, name_attr):
            try:
                return str(getattr(o, name_attr))
            except Exception:
                pass
        return str(o)

    # backing store: (text, obj)
    full = [(_display(o), o) for o in (items or [])]

    def _reload(filter_text=""):
        lb.Items.Clear()
        ft = (filter_text or "").lower()
        for text, obj in full:
            if not ft or ft in text.lower():
                it = ListBoxItem()
                it.Content = text
                # stash the original object on the item
                it.Tag = obj
                lb.Items.Add(it)

    _reload()

    # filter as you type
    def _on_filter(sender, e):
        _reload(filter_tb.Text)
    filter_tb.TextChanged += _on_filter

    # double-click accepts in single-select mode
    def _on_double_click(sender, e):
        if not multiselect and lb.SelectedItem is not None:
            dlg._close(ok_label)
    lb.MouseDoubleClick += _on_double_click

    # Focus filter on load
    def _loaded(sender, e):
        try:
            filter_tb.Focus()
            filter_tb.SelectAll()
        except:
            pass
    dlg.Loaded += _loaded

    dlg.ShowDialog()

    if dlg._result == ok_label:
        if multiselect:
            sel = []
            for it in lb.SelectedItems:
                try:
                    sel.append(it.Tag)
                except Exception:
                    pass
            return sel
        else:
            it = lb.SelectedItem
            return (it.Tag if it is not None else None)
    else:
        # cancelled/closed
        return ([] if multiselect else None)

class _V6Shim(object):
    # Keep lowercase alert() for convenience
    def alert(self, msg, title="Message", buttons=("OK",)):
        return alert(msg, title, buttons)

    # pyRevit style: forms.SelectFromList(...)
    def SelectFromList(self, items, **kwargs):
        return select_from_list(items, **kwargs)

    # snake_case alias as well
    def select_from_list(self, items, **kwargs):
        return select_from_list(items, **kwargs)

    # convenience for yes/no parity
    def ask_yes_no(self, msg, title="Confirm"):
        return ask_yes_no(msg, title)

    # simple input (returns string or None)
    def ask_for_string(self, prompt="Enter value", title="Input", default=""):
        ok, txt = input_box(title, prompt, default)
        return txt if ok else None

# public shim instance
forms = _V6Shim()

__all__ = [
    "alert", "ask_yes_no", "input_box",
    "select_from_list", "forms", "__ada_forms_version__"
]
def big_button_box(title="Choose", buttons=None, cancel=True):
    """
    ADa-themed big button box.
    Returns the clicked button text or None if cancelled.
    """
    buttons = list(buttons or [])
    if not buttons:
        return None

    return button_box( #type:ignore
        title=title,
        buttons=buttons,
        big_buttons=True,
        cancel=cancel
    )
