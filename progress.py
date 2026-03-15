# -*- coding: utf-8 -*-
from __future__ import annotations

import clr  # type: ignore
clr.AddReference("System")
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")

from System import Action  # type: ignore
from System.Drawing import (  # type: ignore
    Color,
    Font,
    FontStyle,
    Point,
    Rectangle,
    Size,
    SolidBrush,
    StringAlignment,
    StringFormat,
    Drawing2D,
    Pen,
)
from System.Windows.Forms import (  # type: ignore
    Application,
    Button,
    Form,
    FormBorderStyle,
    FormStartPosition,
    Label,
    MouseButtons,
    FlatStyle,
    PaintEventHandler,
)

def _enum(enum_type, name):
    """Safe access to .NET enum members that collide with Python keywords."""
    try:
        return getattr(enum_type, name)
    except Exception:
        return None

class _ADaProgressBar(object):
    """Simple custom-painted progress bar panel substitute."""
    def __init__(self, owner, x, y, w, h):
        import clr  # type: ignore
        clr.AddReference("System.Windows.Forms")
        from System.Windows.Forms import Panel  # type: ignore

        self.owner = owner
        self.minimum = 0
        self.maximum = 1
        self.value = 0

        self.panel = Panel()
        self.panel.Location = Point(x, y)
        self.panel.Size = Size(w, h)
        self.panel.BackColor = Color.White
        self.panel.Paint += self._on_paint

    def _safe_ratio(self):
        rng = max(1, int(self.maximum) - int(self.minimum))
        val = max(int(self.minimum), min(int(self.value), int(self.maximum)))
        return float(val - int(self.minimum)) / float(rng)

    def _on_paint(self, sender, e):
        g = e.Graphics
        rect = Rectangle(0, 0, self.panel.Width - 1, self.panel.Height - 1)

        g.SmoothingMode = Drawing2D.SmoothingMode.AntiAlias

        # outer border
        border_pen = Pen(Color.FromArgb(210, 215, 225))
        g.DrawRectangle(border_pen, rect)

        # inner background
        bg_rect = Rectangle(1, 1, self.panel.Width - 2, self.panel.Height - 2)
        bg_brush = SolidBrush(Color.FromArgb(245, 247, 250))
        g.FillRectangle(bg_brush, bg_rect)

        # fill
        ratio = self._safe_ratio()
        fill_w = int((self.panel.Width - 2) * ratio)
        if fill_w > 0:
            fill_rect = Rectangle(1, 1, fill_w, self.panel.Height - 2)
            brush = Drawing2D.LinearGradientBrush(
                fill_rect,
                Color.FromArgb(92, 124, 250),   # ADa blue
                Color.FromArgb(247, 89, 192),   # ADa pink
                Drawing2D.LinearGradientMode.Horizontal
            )
            g.FillRectangle(brush, fill_rect)

        # subtle inner highlight line
        if fill_w > 4:
            hi_pen = Pen(Color.FromArgb(255, 255, 255))
            g.DrawLine(hi_pen, 2, 2, max(2, fill_w - 1), 2)

    def refresh(self):
        try:
            self.panel.Invalidate()
            self.panel.Update()
        except Exception:
            pass


class ADaProgressDialog(Form):
    """
    Themed ADa progress dialog.
    Drop-in replacement for the previous WinForms version:
      - show_modeless()
      - close_safe()
      - set_total(total)
      - update_progress(current, total=None, message="")
      - mark_done(message="Completed.")
      - cancel_requested
    """

    HEADER_H = 54

    def __init__(self, title="ADa Progress", subtitle="Working...", allow_cancel=True):
        Form.__init__(self)

        self.cancel_requested = False
        self._total = 1
        self._current = 0
        self._subtitle = subtitle or ""
        self._status = "Starting..."
        self._allow_drag = False
        self._drag_start = None

        self.Text = title
        self.Width = 560
        self.Height = 220

        self.FormBorderStyle = _enum(FormBorderStyle, "None")
        self.StartPosition = FormStartPosition.CenterScreen
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.TopMost = True
        self.BackColor = Color.White

        # enable double-buffered painting
        try:
            self.SetStyle(0x00000020 | 0x00000002 | 0x00000004 | 0x00002000, True)
        except Exception:
            pass

        # fonts
        self._font_title = Font("Segoe UI", 11, FontStyle.Bold)
        self._font_subtitle = Font("Segoe UI", 10, FontStyle.Regular)
        self._font_status = Font("Segoe UI", 10, FontStyle.Bold)
        self._font_meta = Font("Segoe UI", 8.5, FontStyle.Regular)
        self._font_button = Font("Segoe UI", 9, FontStyle.Bold)

        # subtitle label
        self.lbl_subtitle = Label()
        self.lbl_subtitle.Text = self._subtitle
        self.lbl_subtitle.Location = Point(24, 72)
        self.lbl_subtitle.Size = Size(500, 24)
        self.lbl_subtitle.Font = self._font_subtitle
        self.lbl_subtitle.ForeColor = Color.FromArgb(45, 45, 45)
        self.lbl_subtitle.BackColor = Color.Transparent

        # status label
        self.lbl_status = Label()
        self.lbl_status.Text = self._status
        self.lbl_status.Location = Point(24, 104)
        self.lbl_status.Size = Size(500, 24)
        self.lbl_status.Font = self._font_status
        self.lbl_status.ForeColor = Color.FromArgb(35, 35, 35)
        self.lbl_status.BackColor = Color.Transparent

        # counter label
        self.lbl_count = Label()
        self.lbl_count.Text = ""
        self.lbl_count.Location = Point(24, 128)
        self.lbl_count.Size = Size(500, 18)
        self.lbl_count.Font = self._font_meta
        self.lbl_count.ForeColor = Color.FromArgb(110, 110, 110)
        self.lbl_count.BackColor = Color.Transparent

        # custom progress bar
        self.progress = _ADaProgressBar(self, 24, 154, 420, 20)

        # cancel button
        self.btn_cancel = Button()
        self.btn_cancel.Text = "Cancel"
        self.btn_cancel.Width = 90
        self.btn_cancel.Height = 30
        self.btn_cancel.Location = Point(454, 149)
        self.btn_cancel.Enabled = bool(allow_cancel)
        self.btn_cancel.FlatStyle = _enum(FlatStyle, "Standard")
        self.btn_cancel.Font = self._font_button
        self.btn_cancel.BackColor = Color.FromArgb(92, 124, 250)
        self.btn_cancel.ForeColor = Color.White
        self.btn_cancel.Click += self._on_cancel

        self.Controls.Add(self.lbl_subtitle)
        self.Controls.Add(self.lbl_status)
        self.Controls.Add(self.lbl_count)
        self.Controls.Add(self.progress.panel)
        self.Controls.Add(self.btn_cancel)

        self.Paint += PaintEventHandler(self._on_paint)
        self.MouseDown += self._on_mouse_down
        self.MouseMove += self._on_mouse_move
        self.MouseUp += self._on_mouse_up

        # allow dragging from labels too
        for ctl in [self.lbl_subtitle, self.lbl_status, self.lbl_count]:
            ctl.MouseDown += self._on_mouse_down
            ctl.MouseMove += self._on_mouse_move
            ctl.MouseUp += self._on_mouse_up

        self._update_count_text()

    # ---------- painting ----------

    def _on_paint(self, sender, e):
        g = e.Graphics
        g.SmoothingMode = Drawing2D.SmoothingMode.AntiAlias

        # full background
        g.FillRectangle(SolidBrush(Color.White), self.ClientRectangle)

        # outer border
        border_pen = Pen(Color.FromArgb(205, 210, 220))
        g.DrawRectangle(border_pen, 0, 0, self.Width - 1, self.Height - 1)

        # header gradient
        header_rect = Rectangle(0, 0, self.Width, self.HEADER_H)
        grad = Drawing2D.LinearGradientBrush(
            header_rect,
            Color.FromArgb(92, 124, 250),   # ADa blue
            Color.FromArgb(247, 89, 192),   # ADa pink
            Drawing2D.LinearGradientMode.Horizontal
        )
        g.FillRectangle(grad, header_rect)

        # header bottom line
        sep_pen = Pen(Color.FromArgb(225, 225, 230))
        g.DrawLine(sep_pen, 0, self.HEADER_H, self.Width, self.HEADER_H)

        # title text
        sf = StringFormat()
        sf.LineAlignment = StringAlignment.Center
        sf.Alignment = StringAlignment.Near

        title_rect = Rectangle(18, 0, self.Width - 80, self.HEADER_H)
        g.DrawString(self.Text, self._font_title, SolidBrush(Color.White), title_rect, sf)

        # close X
        close_rect = Rectangle(self.Width - 42, 12, 20, 20)
        x_pen = Pen(Color.FromArgb(255, 255, 255), 2)
        g.DrawLine(x_pen, close_rect.Left, close_rect.Top, close_rect.Right, close_rect.Bottom)
        g.DrawLine(x_pen, close_rect.Right, close_rect.Top, close_rect.Left, close_rect.Bottom)

    # ---------- drag support ----------

    def _on_mouse_down(self, sender, args):
        try:
            if args.Button == MouseButtons.Left:
                self._allow_drag = True
                self._drag_start = args.Location
        except Exception:
            pass

    def _on_mouse_move(self, sender, args):
        try:
            if self._allow_drag and self._drag_start is not None:
                screen = self.PointToScreen(args.Location)
                self.Location = Point(screen.X - self._drag_start.X, screen.Y - self._drag_start.Y)
        except Exception:
            pass

    def _on_mouse_up(self, sender, args):
        self._allow_drag = False
        self._drag_start = None

    # ---------- internal helpers ----------

    def _update_count_text(self):
        if self._total <= 0:
            self.lbl_count.Text = ""
            return

        if self._current <= 0:
            self.lbl_count.Text = "Preparing..."
        else:
            self.lbl_count.Text = "Item {} of {}".format(self._current, self._total)

    def _refresh_ui(self):
        try:
            self.progress.refresh()
            self.Invalidate()
            self.Refresh()
            Application.DoEvents()
        except Exception:
            pass

    def _set_status(self, text):
        self._status = text or ""
        self.lbl_status.Text = self._status

    def _on_cancel(self, sender, args):
        self.cancel_requested = True
        self._set_status("Cancelling after current item...")
        self.btn_cancel.Enabled = False
        self.btn_cancel.BackColor = Color.FromArgb(160, 160, 165)
        self._refresh_ui()

    # ---------- public API ----------

    def show_modeless(self):
        self.Show()
        self._refresh_ui()

    def close_safe(self):
        try:
            self.Close()
        except Exception:
            pass

    def set_total(self, total):
        total = max(1, int(total))
        self._total = total
        self._current = 0
        self.progress.minimum = 0
        self.progress.maximum = total
        self.progress.value = 0
        self._update_count_text()
        self._refresh_ui()

    def update_progress(self, current, total=None, message=""):
        if total is not None:
            total = max(1, int(total))
            self._total = total
            self.progress.maximum = total

        self._current = max(0, min(int(current), self._total))
        self.progress.value = self._current
        self._set_status(message or "")
        self._update_count_text()
        self._refresh_ui()

    def mark_done(self, message="Completed."):
        try:
            self._current = self._total
            self.progress.value = self.progress.maximum
        except Exception:
            pass
        self._set_status(message)
        self._update_count_text()
        self.btn_cancel.Enabled = False
        self.btn_cancel.BackColor = Color.FromArgb(160, 160, 165)
        self._refresh_ui()
