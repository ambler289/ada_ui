# -*- coding: utf-8 -*-
from __future__ import annotations

import clr  # type: ignore
clr.AddReference("System")
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")

from System.Drawing import (  # type: ignore
    Color,
    Font,
    FontStyle,
    Point,
    Size,
    SolidBrush,
    Drawing2D,
)
from System.Windows.Forms import (  # type: ignore
    Application,
    Button,
    Form,
    FormBorderStyle,
    FormStartPosition,
    Label,
    Panel,
    ProgressBar,
    FlatStyle,
)


def _enum(enum_type, name):
    try:
        return getattr(enum_type, name)
    except Exception:
        return None


class _HeaderPanel(Panel):
    """Simple gradient header panel with safe custom painting."""

    def __init__(self, owner):
        Panel.__init__(self)
        self.owner = owner
        self.Height = 54
        self.Dock = 1  # Top
        self.Paint += self._on_paint

    def _on_paint(self, sender, e):
        try:
            g = e.Graphics
            rect = self.ClientRectangle

            brush = Drawing2D.LinearGradientBrush(
                rect,
                Color.FromArgb(92, 124, 250),   # ADa blue
                Color.FromArgb(247, 89, 192),   # ADa pink
                Drawing2D.LinearGradientMode.Horizontal
            )
            g.FillRectangle(brush, rect)

            title_brush = SolidBrush(Color.White)
            g.DrawString(
                str(self.owner.Text),
                self.owner._font_title,
                title_brush,
                16.0,
                16.0
            )
        except Exception:
            pass


class ADaProgressDialog(Form):
    """
    Safer ADa-styled progress dialog for pyRevit / Revit 2026.

    Public API:
      - show_modeless()
      - close_safe()
      - set_total(total)
      - update_progress(current, total=None, message="")
      - mark_done(message="Completed.")
      - cancel_requested
    """

    def __init__(self, title="ADa Progress", subtitle="Working...", allow_cancel=True):
        Form.__init__(self)

        self.cancel_requested = False
        self._total = 1
        self._current = 0
        self._subtitle = subtitle or ""
        self._status = "Starting..."

        self.Text = title
        self.Width = 560
        self.Height = 215
        self.FormBorderStyle = FormBorderStyle.FixedDialog
        self.StartPosition = FormStartPosition.CenterScreen
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.ShowInTaskbar = False
        self.TopMost = True
        self.BackColor = Color.White

        # fonts
        self._font_title = Font("Segoe UI", 11, FontStyle.Bold)
        self._font_subtitle = Font("Segoe UI", 10, FontStyle.Regular)
        self._font_status = Font("Segoe UI", 10, FontStyle.Bold)
        self._font_meta = Font("Segoe UI", 8.5, FontStyle.Regular)
        self._font_button = Font("Segoe UI", 9, FontStyle.Bold)

        # header
        self.header = _HeaderPanel(self)
        self.Controls.Add(self.header)

        # subtitle label
        self.lbl_subtitle = Label()
        self.lbl_subtitle.Text = self._subtitle
        self.lbl_subtitle.Location = Point(20, 68)
        self.lbl_subtitle.Size = Size(500, 24)
        self.lbl_subtitle.Font = self._font_subtitle
        self.lbl_subtitle.ForeColor = Color.FromArgb(45, 45, 45)
        self.lbl_subtitle.BackColor = Color.White

        # status label
        self.lbl_status = Label()
        self.lbl_status.Text = self._status
        self.lbl_status.Location = Point(20, 98)
        self.lbl_status.Size = Size(500, 24)
        self.lbl_status.Font = self._font_status
        self.lbl_status.ForeColor = Color.FromArgb(35, 35, 35)
        self.lbl_status.BackColor = Color.White

        # count label
        self.lbl_count = Label()
        self.lbl_count.Text = "Preparing..."
        self.lbl_count.Location = Point(20, 122)
        self.lbl_count.Size = Size(500, 18)
        self.lbl_count.Font = self._font_meta
        self.lbl_count.ForeColor = Color.FromArgb(110, 110, 110)
        self.lbl_count.BackColor = Color.White

        # progress bar
        self.progress = ProgressBar()
        self.progress.Location = Point(20, 148)
        self.progress.Size = Size(420, 20)
        self.progress.Minimum = 0
        self.progress.Maximum = 1
        self.progress.Value = 0
        self.progress.Style = _enum(type(self.progress.Style), "Continuous") or self.progress.Style

        # cancel button
        self.btn_cancel = Button()
        self.btn_cancel.Text = "Cancel"
        self.btn_cancel.Width = 90
        self.btn_cancel.Height = 30
        self.btn_cancel.Location = Point(450, 143)
        self.btn_cancel.Enabled = bool(allow_cancel)
        self.btn_cancel.FlatStyle = FlatStyle.Standard
        self.btn_cancel.Font = self._font_button
        self.btn_cancel.BackColor = Color.FromArgb(92, 124, 250)
        self.btn_cancel.ForeColor = Color.White
        self.btn_cancel.UseVisualStyleBackColor = False
        self.btn_cancel.Click += self._on_cancel

        self.Controls.Add(self.lbl_subtitle)
        self.Controls.Add(self.lbl_status)
        self.Controls.Add(self.lbl_count)
        self.Controls.Add(self.progress)
        self.Controls.Add(self.btn_cancel)

        self._update_count_text()

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
            self.header.Invalidate()
            self.progress.Refresh()
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

    def show_modeless(self):
        try:
            self.Show()
            self.BringToFront()
            self._refresh_ui()
        except Exception:
            pass

    def close_safe(self):
        try:
            if not self.IsDisposed:
                self.Hide()
                self.Close()
                self.Dispose()
        except Exception:
            pass

    def set_total(self, total):
        total = max(1, int(total))
        self._total = total
        self._current = 0
        self.progress.Minimum = 0
        self.progress.Maximum = total
        self.progress.Value = 0
        self._update_count_text()
        self._refresh_ui()

    def update_progress(self, current, total=None, message=""):
        if total is not None:
            total = max(1, int(total))
            self._total = total
            self.progress.Maximum = total

        self._current = max(0, min(int(current), self._total))
        self.progress.Value = self._current
        self._set_status(message or "")
        self._update_count_text()
        self._refresh_ui()

    def mark_done(self, message="Completed."):
        try:
            self._current = self._total
            self.progress.Value = self.progress.Maximum
        except Exception:
            pass

        self._set_status(message)
        self._update_count_text()
        self.btn_cancel.Enabled = False
        self.btn_cancel.BackColor = Color.FromArgb(160, 160, 165)
        self._refresh_ui()
