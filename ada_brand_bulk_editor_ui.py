# ada_brand_bulk_editor_ui.py
# ADa-themed bulk editor (dark + gradient header, BORDERLESS + ROUNDED CORNERS).
# Returns {param_name: new_value} on OK, or None on Cancel.

def bulk_edit(editable_params, title="Edit Parameters (Bulk)"):
    if not editable_params:
        return None

    import clr
    clr.AddReference("System")
    clr.AddReference("System.Windows.Forms")
    clr.AddReference("System.Drawing")

    # WinForms
    from System.Windows.Forms import (  # type: ignore
        Form, TableLayoutPanel, Label, TextBox, CheckBox, Button,
        FormBorderStyle, FormBorderStyle as _FBS, AnchorStyles, DockStyle, Padding,
        DialogResult, CheckState, FormStartPosition, FlatStyle, BorderStyle,
        MouseButtons, Control
    )
    # Drawing
    from System.Drawing import (  # type: ignore
        Size, Font, FontStyle, ContentAlignment, Color,
        Point, PointF, Rectangle, Brushes, Pen, Region
    )
    from System.Drawing.Drawing2D import (  # type: ignore
        LinearGradientBrush, LinearGradientMode, GraphicsPath
    )

    # ----------------------- THEME / FLAGS --------------------------------
    BORDERLESS     = True                     # remove OS/Revit title bar
    CORNER_RADIUS  = 14                       # rounded corners radius (px)
    DARK_BG        = Color.FromArgb(20, 22, 25)
    DARK_PANEL     = Color.FromArgb(30, 33, 37)
    DARK_TEXT      = Color.FromArgb(240, 240, 240)
    MUTED_TEXT     = Color.FromArgb(200, 200, 200)
    BTN_BG         = Color.FromArgb(52, 55, 60)
    BTN_HOVER      = Color.FromArgb(62, 66, 72)
    BORDER_CLR     = Color.FromArgb(90, 95, 102)

    # Gradient header colors (ADa brand)
    GRAD_LEFT      = Color.FromArgb(108, 99, 255)   # blue/violet
    GRAD_RIGHT     = Color.FromArgb(255, 99, 164)   # pink
    HEADER_H       = 72
    # ---------------------------------------------------------------------

    # -------------------- helpers ----------------------------------------
    def _safe_text(val):
        if val is None:
            return ""
        try:
            if isinstance(val, float):
                return ("{:.0f}".format(val) if float(val).is_integer() else "{:g}".format(val))
            return str(val)
        except Exception:
            return ""

    def _fmt_current(v, ptype, unit):
        if v is None:
            return ""
        if ptype == "bool":
            return "Yes" if bool(v) else "No"
        if ptype == "float":
            try:
                vv = float(v)
                s = "{:.0f}".format(vv) if vv.is_integer() else "{:g}".format(vv)
            except Exception:
                s = str(v)
            return s + ((" " + unit) if unit else "")
        return str(v)

    def _parse_value(ptype, unit, raw):
        if raw is None:
            return None
        txt = str(raw).strip()
        if txt == "":
            return None
        if ptype == "bool":
            tl = txt.lower()
            if tl in ("yes", "true", "1", "y", "t", "✓", "tick", "check"):  return True
            if tl in ("no", "false", "0", "n", "f", "✗", "x", "cross"):    return False
            return None
        if ptype == "float":
            try:
                return float(txt.replace(",", ".").split()[0])
            except Exception:
                return None
        return txt
    # ---------------------------------------------------------------------

    # -------------------- window -----------------------------------------
    form = Form()
    form.Text = title

    # Robust handling for FormBorderStyle.None (avoid name collision with Python None)
    FBS = _FBS
    form.FormBorderStyle = (getattr(FBS, "None", FBS(0))) if BORDERLESS else FBS.FixedDialog

    form.StartPosition = FormStartPosition.CenterScreen
    form.MinimizeBox = False
    form.MaximizeBox = False
    form.Size = Size(860, 600)
    form.BackColor = DARK_BG
    form.ForeColor = DARK_TEXT
    form.ShowIcon = False
    form.ShowInTaskbar = False  # modal tool window feel

    # Gradient header (painted on the form background)
    form.Padding = Padding(16, HEADER_H + 12, 16, 16)

    # --- rounded window corners ------------------------------------------
    def _apply_rounded_region():
        r = int(CORNER_RADIUS)
        if r <= 0:
            form.Region = None
            return
        w, h = form.Width, form.Height
        d = 2 * r
        path = GraphicsPath()
        # top-left, top-right, bottom-right, bottom-left arcs
        path.AddArc(0,            0,            d, d, 180, 90)
        path.AddArc(w - d - 1,    0,            d, d, 270, 90)
        path.AddArc(w - d - 1,    h - d - 1,    d, d,   0, 90)
        path.AddArc(0,            h - d - 1,    d, d,  90, 90)
        path.CloseAllFigures()
        form.Region = Region(path)
        path.Dispose()

    # --- window dragging via header --------------------------------------
    _drag = {"on": False, "sx": 0, "sy": 0, "ox": 0, "oy": 0}
    def _md(sender, e):
        if e.Button == MouseButtons.Left and e.Y <= HEADER_H:
            p = Control.MousePosition
            _drag.update(on=True, sx=p.X, sy=p.Y, ox=form.Location.X, oy=form.Location.Y)
    def _mm(sender, e):
        if _drag["on"]:
            p = Control.MousePosition
            form.Location = Point(_drag["ox"] + (p.X - _drag["sx"]), _drag["oy"] + (p.Y - _drag["sy"]))
    def _mu(sender, e):
        _drag["on"] = False
    form.MouseDown += _md
    form.MouseMove += _mm
    form.MouseUp   += _mu

    # --- paint header + title --------------------------------------------
    def _paint_header(sender, e):
        rect = Rectangle(0, 0, form.ClientSize.Width, HEADER_H)
        grad = LinearGradientBrush(rect, GRAD_LEFT, GRAD_RIGHT, LinearGradientMode.Horizontal)
        e.Graphics.FillRectangle(grad, rect); grad.Dispose()
        e.Graphics.DrawString(title, Font("Segoe UI", 13.0, FontStyle.Bold), Brushes.White, PointF(16.0, 18.0))
        pen = Pen(Color.FromArgb(60, 60, 60))
        e.Graphics.DrawLine(pen, 0, HEADER_H - 1, form.ClientSize.Width, HEADER_H - 1); pen.Dispose()

    form.Paint  += _paint_header
    form.Resize += (lambda s, ev: (_apply_rounded_region(),
                                   form.Invalidate(Rectangle(0, 0, form.ClientSize.Width, HEADER_H))))
    form.Shown  += (lambda s, ev: _apply_rounded_region())

    # --- close “✕” (transparent label so gradient shows through) ----------
    lbl_close = Label()
    lbl_close.Text = u"✕"
    lbl_close.AutoSize = False
    lbl_close.TextAlign = ContentAlignment.MiddleCenter
    lbl_close.Font = Font("Segoe UI", 11.0, FontStyle.Bold)
    lbl_close.ForeColor = Color.White
    lbl_close.BackColor = Color.Transparent
    lbl_close.Size = Size(36, 28)

    def _locate_close():
        lbl_close.Location = Point(form.ClientSize.Width - lbl_close.Width - 12, 10)

    _locate_close()
    def _enter(s, e): lbl_close.ForeColor = Color.FromArgb(255, 235, 235)
    def _leave(s, e): lbl_close.ForeColor = Color.White
    def _click(s, e):
        form.DialogResult = DialogResult.Cancel
        form.Close()
    lbl_close.MouseEnter += _enter
    lbl_close.MouseLeave += _leave
    lbl_close.Click      += _click
    # allow drag from the close label area too
    lbl_close.MouseDown += _md
    lbl_close.MouseMove += _mm
    lbl_close.MouseUp   += _mu
    form.Controls.Add(lbl_close)
    form.Resize += (lambda s, e: _locate_close())
    # ---------------------------------------------------------------------

    # -------------------- table ------------------------------------------
    table = TableLayoutPanel()
    table.Dock = DockStyle.Fill
    table.Padding = Padding(16, 12, 16, 16)
    table.AutoScroll = True
    table.ColumnCount = 4
    table.RowCount = 1
    table.BackColor = DARK_BG

    def _hdr(text):
        lbl = Label()
        lbl.Text = text
        lbl.Font = Font("Segoe UI", 9.5, FontStyle.Bold)
        lbl.AutoSize = True
        lbl.TextAlign = ContentAlignment.MiddleLeft
        lbl.ForeColor = DARK_TEXT
        lbl.BackColor = DARK_BG
        return lbl

    table.Controls.Add(_hdr("Parameter"), 0, 0)
    table.Controls.Add(_hdr("Current"),   1, 0)
    table.Controls.Add(_hdr("New Value"), 2, 0)
    table.Controls.Add(_hdr("Unit"),      3, 0)

    editors = []  # (kind, name, control, ptype)
    row = 1
    for p in editable_params:
        name    = p["name"]
        display = p.get("display_name", name)
        ptype   = p.get("type", "string")
        current = p.get("value")
        cfg     = p.get("config", {}) or {}
        unit    = cfg.get("unit", "") or ""

        name_lbl = Label()
        name_lbl.Text = _safe_text(display)
        name_lbl.AutoSize = True
        name_lbl.TextAlign = ContentAlignment.MiddleLeft
        name_lbl.ForeColor = DARK_TEXT
        name_lbl.BackColor = DARK_BG
        table.Controls.Add(name_lbl, 0, row)

        current_lbl = Label()
        current_lbl.Text = _fmt_current(current, ptype, unit)
        current_lbl.AutoSize = True
        current_lbl.TextAlign = ContentAlignment.MiddleLeft
        current_lbl.ForeColor = MUTED_TEXT
        current_lbl.BackColor = DARK_BG
        table.Controls.Add(current_lbl, 1, row)

        if ptype == "bool":
            cb = CheckBox()
            cb.ThreeState = True
            cb.CheckState = CheckState.Indeterminate
            cb.Text = "(tick = Yes, untick = No; dash = keep)"
            cb.AutoSize = True
            cb.ForeColor = DARK_TEXT
            cb.BackColor = DARK_BG
            table.Controls.Add(cb, 2, row)

            unit_lbl = Label()
            unit_lbl.Text = ""
            unit_lbl.AutoSize = True
            unit_lbl.ForeColor = MUTED_TEXT
            unit_lbl.BackColor = DARK_BG
            table.Controls.Add(unit_lbl, 3, row)

            editors.append(("bool", name, cb, ptype))
        else:
            tb = TextBox()
            tb.Width = 310
            tb.Text = ""
            tb.BackColor = DARK_PANEL
            tb.ForeColor = DARK_TEXT
            tb.BorderStyle = BorderStyle.FixedSingle
            table.Controls.Add(tb, 2, row)

            unit_lbl = Label()
            unit_lbl.Text = unit
            unit_lbl.AutoSize = True
            unit_lbl.ForeColor = MUTED_TEXT
            unit_lbl.BackColor = DARK_BG
            table.Controls.Add(unit_lbl, 3, row)

            editors.append(("text", name, tb, ptype))

        row += 1
    # ---------------------------------------------------------------------

    # -------------------- buttons ----------------------------------------
    btn_ok = Button()
    btn_ok.Text = "OK"
    btn_ok.Anchor = AnchorStyles.Right
    btn_ok.DialogResult = DialogResult.OK

    btn_cancel = Button()
    btn_cancel.Text = "Cancel"
    btn_cancel.Anchor = AnchorStyles.Right
    btn_cancel.DialogResult = DialogResult.Cancel

    for b in (btn_ok, btn_cancel):
        b.FlatStyle = FlatStyle.Flat
        b.UseVisualStyleBackColor = False
        b.BackColor = BTN_BG
        b.ForeColor = DARK_TEXT
        fa = getattr(b, "FlatAppearance", None)
        if fa is not None:
            fa.BorderColor = BORDER_CLR
            fa.MouseOverBackColor = BTN_HOVER

    table.RowCount = row + 1
    table.Controls.Add(btn_ok,     2, row)
    table.Controls.Add(btn_cancel, 3, row)

    form.AcceptButton = btn_ok
    form.CancelButton = btn_cancel
    form.Controls.Add(table)
    # ---------------------------------------------------------------------

    # Show and collect
    result = form.ShowDialog()
    if result != DialogResult.OK:
        return None

    changes = {}
    for kind, name, ctrl, ptype in editors:
        if kind == "bool":
            st = ctrl.CheckState
            if st == CheckState.Indeterminate:
                continue
            changes[name] = (st == CheckState.Checked)
        else:
            raw = _safe_text(ctrl.Text).strip()
            if raw == "":
                continue
            parsed = _parse_value(ptype, "", raw)
            if parsed is None:
                continue
            changes[name] = parsed

    return changes
