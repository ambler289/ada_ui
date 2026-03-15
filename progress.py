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
    DockStyle,
    ProgressBarStyle,
)


def _enum(enum_type, name, fallback=None):
    try:
        return getattr(enum_type, name)
    except Exception:
        return fallback


class _HeaderPanel(Panel):
    """Gradient ADa header."""

    def __init__(self, owner):
        Panel.__init__(self)
        self.owner = owner
        self.Height = 54
        self.Dock = DockStyle.Top
        self.Paint += self._on_paint

    def _on_paint(self, sender, e):
        try:
            g = e.Graphics
            rect = self.ClientRectangle

            brush = Drawing2D.LinearGradientBrush(
                rect,
                Color.FromArgb(92, 124, 250),
                Color.FromArgb(247, 89, 192),
                Drawing2D.LinearGradientMode.Horizontal
            )
            g.FillRectangle(brush, rect)

            title_brush = SolidBrush(Color.White)
            g.DrawString(
                str(self.owner._display_title),
                self.owner._font_title,
                title_brush,
                18.0,
                16.0
            )
        except Exception:
            pass


class _BodyPanel(Panel):
    """Dark ADa body panel."""

    def __init__(self):
        Panel.__init__(self)
        self.Dock = DockStyle.Fill
        self.BackColor = Color.FromArgb(28, 34, 48)


class ADaProgressDialog(Form):
    """
    ADa-styled progress dialog.

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
        self._display_title = title

        self.Text = " "
        self.Width = 560
        self.Height = 240
        self.FormBorderStyle = _enum(FormBorderStyle, "FixedDialog", FormBorderStyle.FixedDialog)
        self.StartPosition = FormStartPosition.CenterScreen
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.ShowInTaskbar = False
        self.TopMost = True
        self.BackColor = Color.FromArgb(28, 34, 48)

        # fonts
        self._font_title = Font("Segoe UI", 11, FontStyle.Bold)
        self._font_subtitle = Font("Segoe UI", 10, FontStyle.Regular)
        self._font_status = Font("Segoe UI", 10.5, FontStyle.Bold)
        self._font_meta = Font("Segoe UI", 8.75, FontStyle.Regular)
        self._font_button = Font("Segoe UI", 9, FontStyle.Bold)

        # header + body
        self.header = _HeaderPanel(self)
        self.body = _BodyPanel()

        self.Controls.Add(self.body)
        self.Controls.Add(self.header)

        # subtitle
        self.lbl_subtitle = Label()
        self.lbl_subtitle.Text = self._subtitle
        self.lbl_subtitle.Location = Point(28, 22)
        self.lbl_subtitle.Size = Size(470, 24)
        self.lbl_subtitle.Font = self._font_subtitle
        self.lbl_subtitle.ForeColor = Color.FromArgb(235, 238, 245)
        self.lbl_subtitle.BackColor = self.body.BackColor

        # status
        self.lbl_status = Label()
        self.lbl_status.Text = self._status
        self.lbl_status.Location = Point(28, 48)
        self.lbl_status.Size = Size(470, 26)
        self.lbl_status.Font = self._font_status
        self.lbl_status.ForeColor = Color.White
        self.lbl_status.BackColor = self.body.BackColor

        # count
        self.lbl_count = Label()
        self.lbl_count.Text = "Preparing..."
        self.lbl_count.Location = Point(28, 72)
        self.lbl_count.Size = Size(470, 20)
        self.lbl_count.Font = self._font_meta
        self.lbl_count.ForeColor = Color.FromArgb(200, 206, 220)
        self.lbl_count.BackColor = self.body.BackColor

        # progress bar
        self.progress = ProgressBar()
        self.progress.Location = Point(28, 96)
        self.progress.Size = Size(330, 18)
        self.progress.Minimum = 0
        self.progress.Maximum = 1
        self.progress.Value = 0
        self.progress.Style = _enum(
            ProgressBarStyle,
            "Continuous",
            self.progress.Style
        )
        self.progress.ForeColor = Color.FromArgb(92, 124, 250)

        # cancel button
        self.btn_cancel = Button()
        self.btn_cancel.Text = "Cancel"
        self.btn_cancel.Width = 110
        self.btn_cancel.Height = 36
        self.btn_cancel.Location = Point(380, 92)
        self.btn_cancel.Enabled = bool(allow_cancel)
        self.btn_cancel.FlatStyle = _enum(FlatStyle, "Flat", FlatStyle.Flat)
        try:
            self.btn_cancel.FlatAppearance.BorderSize = 0
        except Exception:
            pass
        self.btn_cancel.Font = self._font_button
        self.btn_cancel.BackColor = Color.FromArgb(92, 124, 250)
        self.btn_cancel.ForeColor = Color.White
        self.btn_cancel.UseVisualStyleBackColor = False
        self.btn_cancel.Click += self._on_cancel

        # add content to body panel
        self.body.Controls.Add(self.lbl_subtitle)
        self.body.Controls.Add(self.lbl_status)
        self.body.Controls.Add(self.lbl_count)
        self.body.Controls.Add(self.progress)
        self.body.Controls.Add(self.btn_cancel)

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
            self.body.Invalidate()
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
        self.btn_cancel.BackColor = Color.FromArgb(110, 114, 125)
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
        self.btn_cancel.BackColor = Color.FromArgb(110, 114, 125)
        self._refresh_ui()
