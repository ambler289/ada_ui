# gp_ui_shims.py
# ADa alert shim
# - SILENT mode: all forms.alert() calls return sensible defaults
#                 (no UI, no console prints, no pyRevit output window)
# - You can flip SILENT_ALERTS to False to bring back the branded dialogs.

SILENT_ALERTS = True   # <- set to False if you ever want the themed popups back


def install_ui_shims(forms):
    _patch_alert_compat(forms)


# ---- (optional) branded confirm dialog used only when SILENT_ALERTS = False ----
def _show_branded_confirm(title, message, buttons="ok", default="ok"):
    import clr
    clr.AddReference("System")
    clr.AddReference("System.Windows.Forms")
    clr.AddReference("System.Drawing")

    from System.Windows.Forms import (  # type: ignore
        Form, Label, Button, Panel, DialogResult, DockStyle, FormStartPosition,
        FlatStyle, MouseButtons, Control, Padding
    )
    from System.Windows.Forms import FormBorderStyle as _FBS # type: ignore
    from System.Drawing import (Size, Point, PointF, Rectangle, Font, FontStyle, # type: ignore
                                Color, Brushes, Pen, Region)
    from System.Drawing.Drawing2D import LinearGradientBrush, LinearGradientMode, GraphicsPath # type: ignore

    # Theme
    DARK_BG   = Color.FromArgb(20, 22, 25)
    DARK_TEXT = Color.FromArgb(240, 240, 240)
    MUTED     = Color.FromArgb(210, 210, 210)
    BTN_BG    = Color.FromArgb(52, 55, 60)
    BTN_HOVER = Color.FromArgb(62, 66, 72)
    BORDER    = Color.FromArgb(90, 95, 102)
    GRAD_L    = Color.FromArgb(108, 99, 255)
    GRAD_R    = Color.FromArgb(255, 99, 164)
    HEADER_H  = 56
    RADIUS    = 14

    form = Form()
    FBS = _FBS
    form.FormBorderStyle = getattr(FBS, "None", FBS(0))
    form.StartPosition   = FormStartPosition.CenterScreen
    form.Size            = Size(560, 300)
    form.BackColor       = DARK_BG
    form.ForeColor       = DARK_TEXT
    form.ShowIcon        = False
    form.ShowInTaskbar   = False
    form.Padding         = Padding(18, HEADER_H + 12, 18, 18)

    # rounded corners
    def _round():
        w,h = form.Width, form.Height
        r   = RADIUS*2
        gp  = GraphicsPath()
        gp.AddArc(0,0, r, r, 180, 90)
        gp.AddArc(w-r-1,0, r, r, 270, 90)
        gp.AddArc(w-r-1,h-r-1, r, r, 0, 90)
        gp.AddArc(0,h-r-1, r, r, 90, 90)
        gp.CloseAllFigures()
        form.Region = Region(gp); gp.Dispose()

    def _paint_header(sender, e):
        rect = Rectangle(0, 0, form.ClientSize.Width, HEADER_H)
        grad = LinearGradientBrush(rect, GRAD_L, GRAD_R, LinearGradientMode.Horizontal)
        e.Graphics.FillRectangle(grad, rect); grad.Dispose()
        e.Graphics.DrawString(title, Font("Segoe UI", 11.5, FontStyle.Bold), Brushes.White, PointF(14.0, 16.0))
        pen = Pen(Color.FromArgb(60,60,60))
        e.Graphics.DrawLine(pen, 0, HEADER_H-1, form.ClientSize.Width, HEADER_H-1); pen.Dispose()

    form.Paint  += _paint_header
    form.Resize += (lambda s,e: (_round(), form.Invalidate(Rectangle(0,0,form.ClientSize.Width, HEADER_H))))
    form.Shown  += (lambda s,e: _round())

    # drag by header
    drag = {"on": False, "sx": 0, "sy": 0, "ox": 0, "oy": 0}
    def _md(s,e):
        if e.Button == MouseButtons.Left and e.Y <= HEADER_H:
            p = Control.MousePosition
            drag.update(on=True, sx=p.X, sy=p.Y, ox=form.Location.X, oy=form.Location.Y)
    def _mm(s,e):
        if drag["on"]:
            p = Control.MousePosition
            form.Location = Point(drag["ox"] + (p.X - drag["sx"]), drag["oy"] + (p.Y - drag["sy"]))
    def _mu(s,e): drag["on"] = False
    form.MouseDown += _md; form.MouseMove += _mm; form.MouseUp += _mu

    # close ✕
    close = Label()
    close.Text = u"✕"; close.AutoSize = False; close.Size = Size(32, 26)
    close.Location = Point(form.ClientSize.Width - close.Width - 10, 8)
    close.ForeColor = Color.White; close.TextAlign = 4; close.Font = Font("Segoe UI", 10.0, FontStyle.Bold)
    close.MouseEnter += (lambda s,e: setattr(close, "ForeColor", Color.FromArgb(255,235,235)))
    close.MouseLeave += (lambda s,e: setattr(close, "ForeColor", Color.White))
    close.Click      += (lambda s,e: (setattr(form, "DialogResult", DialogResult.Cancel), form.Close()))
    close.MouseDown  += _md; close.MouseMove += _mm; close.MouseUp += _mu
    form.Controls.Add(close)
    form.Resize += (lambda s,e: setattr(close, "Location", Point(form.ClientSize.Width - close.Width - 10, 8)))

    panel = Panel(); panel.Dock = DockStyle.Fill; panel.BackColor = DARK_BG
    form.Controls.Add(panel)

    msg = Label()
    msg.Text = str(message); msg.AutoSize = True; msg.ForeColor = MUTED; msg.BackColor = DARK_BG
    msg.Font = Font("Segoe UI", 9.5)
    msg.MaximumSize = Size(form.ClientSize.Width - 48, 0)
    msg.Location = Point(0, 0)
    panel.Controls.Add(msg)

    def _mkbtn(text):
        b = Button()
        b.Text = text
        b.FlatStyle = FlatStyle.Flat
        b.UseVisualStyleBackColor = False
        b.BackColor = BTN_BG
        b.ForeColor = DARK_TEXT
        fa = getattr(b, "FlatAppearance", None)
        if fa is not None:
            fa.BorderColor = BORDER
            fa.MouseOverBackColor = BTN_HOVER
        b.Size = Size(92, 30)
        return b

    b1 = _mkbtn("OK"); b2 = _mkbtn(""); b3 = _mkbtn("")
    val = {"ret": None}

    mode = buttons.lower().strip()
    if mode in ("yesno", "yes/no"):
        b1.Text = "Yes"; b2.Text = "No"
        b1.Click += (lambda s,e: (val.update(ret=True), form.Close()))
        b2.Click += (lambda s,e: (val.update(ret=False), form.Close()))
    elif mode in ("okcancel", "ok/cancel"):
        b1.Text = "OK"; b2.Text = "Cancel"
        b1.Click += (lambda s,e: (val.update(ret=True), form.Close()))
        b2.Click += (lambda s,e: (val.update(ret=None), form.Close()))
    elif mode in ("yesnocancel","yes/no/cancel"):
        b1.Text = "Yes"; b2.Text = "No"; b3.Text = "Cancel"
        b1.Click += (lambda s,e: (val.update(ret=True), form.Close()))
        b2.Click += (lambda s,e: (val.update(ret=False), form.Close()))
        b3.Click += (lambda s,e: (val.update(ret=None), form.Close()))
    else:
        b1.Text = "OK"
        b1.Click += (lambda s,e: (val.update(ret=True), form.Close()))

    # place buttons right
    def _place():
        y = msg.Bottom + 22
        xs = [b for b in (b1,b2,b3) if b.Text]
        x = panel.ClientSize.Width - (len(xs)*xs[0].Width + (len(xs)-1)*10)
        for bt in xs:
            bt.Location = Point(x, y); panel.Controls.Add(bt); x += bt.Width + 10
        panel.Height = y + xs[0].Height
        want = HEADER_H + 12 + panel.Bottom + 18
        if form.Height < want:
            form.Height = want
    _place()

    # default focus
    if "yes" in default.lower() or "ok" in default.lower():
        try: b1.Focus()
        except: pass

    form.ShowDialog()
    return val["ret"]


# ----------------------------- ALERT COMPAT -------------------------------
def _patch_alert_compat(forms):
    """Replace forms.alert with a silent or themed version. Idempotent."""
    if forms is None or getattr(forms, "_ada_patched_alert", False):
        return

    if not hasattr(forms, "_ada_orig_alert"):
        try:
            setattr(forms, "_ada_orig_alert", getattr(forms, "alert", None))
        except Exception:
            pass

    def _alert_compat(msg, title="Message", **kwargs):
        # supported decision flags; ignore the rest
        yes    = bool(kwargs.pop("yes", False))
        no     = bool(kwargs.pop("no", False))
        ok     = bool(kwargs.pop("ok", False))
        cancel = bool(kwargs.pop("cancel", False))
        decision = any((yes, no, ok, cancel))

        if SILENT_ALERTS:
            # Never show UI, never print to console.
            # Default behaviours: proceed (Yes/OK). For *…/Cancel* we still proceed.
            if decision:
                return True
            return True  # info-only
        else:
            # Themed dialogs
            try:
                if decision:
                    if yes and no and cancel:
                        return _show_branded_confirm(title, msg, "yesnocancel", default="yes")
                    if yes and no:
                        return _show_branded_confirm(title, msg, "yesno", default="yes")
                    if ok and cancel:
                        return _show_branded_confirm(title, msg, "okcancel", default="ok")
                    return _show_branded_confirm(title, msg, "ok", default="ok")
                else:
                    _show_branded_confirm(title, msg, "ok", default="ok")
                    return True
            except Exception:
                # absolute fallback: do nothing but keep going
                return True

    try:
        forms.alert = _alert_compat
        setattr(forms, "_ada_patched_alert", True)
    except Exception:
        pass
