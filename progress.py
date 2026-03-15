# -*- coding: utf-8 -*-
from __future__ import annotations

import clr  # type: ignore
clr.AddReference("System")
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")

from System.Drawing import Point, Size  # type: ignore
from System.Windows.Forms import (  # type: ignore
    Application,
    Button,
    Form,
    FormBorderStyle,
    FormStartPosition,
    Label,
    ProgressBar,
)


class ADaProgressDialog(Form):
    def __init__(self, title="ADa Progress", subtitle="Working...", allow_cancel=True):
        Form.__init__(self)

        self.cancel_requested = False
        self._total = 1

        self.Text = title
        self.Width = 520
        self.Height = 190
        self.FormBorderStyle = FormBorderStyle.FixedDialog
        self.StartPosition = FormStartPosition.CenterScreen
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.TopMost = True

        self.lbl_subtitle = Label()
        self.lbl_subtitle.Text = subtitle
        self.lbl_subtitle.Location = Point(20, 20)
        self.lbl_subtitle.Size = Size(460, 24)

        self.lbl_status = Label()
        self.lbl_status.Text = "Starting..."
        self.lbl_status.Location = Point(20, 55)
        self.lbl_status.Size = Size(460, 26)

        self.progress = ProgressBar()
        self.progress.Location = Point(20, 95)
        self.progress.Size = Size(460, 22)
        self.progress.Minimum = 0
        self.progress.Maximum = 1
        self.progress.Value = 0

        self.btn_cancel = Button()
        self.btn_cancel.Text = "Cancel"
        self.btn_cancel.Width = 100
        self.btn_cancel.Location = Point(380, 125)
        self.btn_cancel.Enabled = bool(allow_cancel)
        self.btn_cancel.Click += self._on_cancel

        self.Controls.Add(self.lbl_subtitle)
        self.Controls.Add(self.lbl_status)
        self.Controls.Add(self.progress)
        self.Controls.Add(self.btn_cancel)

    def _on_cancel(self, sender, args):
        self.cancel_requested = True
        self.lbl_status.Text = "Cancelling after current item..."
        self.btn_cancel.Enabled = False
        self._refresh_ui()

    def _refresh_ui(self):
        self.Refresh()
        Application.DoEvents()

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
        self.progress.Minimum = 0
        self.progress.Maximum = total
        self.progress.Value = 0
        self._refresh_ui()

    def update_progress(self, current, total=None, message=""):
        if total is not None:
            total = max(1, int(total))
            self._total = total
            self.progress.Maximum = total

        current = max(0, min(int(current), self._total))
        self.progress.Value = current
        self.lbl_status.Text = message or ""
        self._refresh_ui()

    def mark_done(self, message="Completed."):
        try:
            self.progress.Value = self.progress.Maximum
        except Exception:
            pass
        self.lbl_status.Text = message
        self.btn_cancel.Enabled = False
        self._refresh_ui()
