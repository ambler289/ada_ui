# ada_brand_bulk_editor_shim.py
# ADa-styled bulk editor for parameter lists.
# Usage in your main script:
#   try:
#       from ada_core.ui.bulk_editor import bulk_edit as ada_bulk_edit
#       _HAVE_ADA_BULK = True
#   except Exception:
#       try:
#           from ada_brand_bulk_editor_shim import bulk_edit as ada_bulk_edit
#           _HAVE_ADA_BULK = True
#       except Exception:
#           _HAVE_ADA_BULK = False
#           ada_bulk_edit = None
#
# Expects `editable_params` as a list of dicts with keys:
#   'name', 'display_name', 'type' in {'bool','float','string'}, 'value', 'config' (optional: {'unit','notes'})
# Returns dict {param_name: new_value} or None if cancelled.

def _load_forms():
    try:
        from ada_brandforms_v6 import forms as _forms  # type: ignore
        forms = _forms
    except Exception:
        try:
            from ada_bootstrap import forms as _forms  # type: ignore
            forms = _forms
        except Exception:
            try:
                from pyrevit import forms as _forms  # type: ignore
                forms = _forms
            except Exception:
                class _Fallback(object):
                    def alert(self, msg, title="Message"):
                        print("[ALERT]", title, msg)
                    def SelectFromList(self, items=None, **kwargs):
                        return None
                    def ask_for_string(self, *args, **kwargs):
                        return None
                forms = _Fallback()
    try:
        # If gp_ui_shims is available, install it so yes/no etc. work
        from gp_ui_shims import install_ui_shims
        install_ui_shims(forms)
    except Exception:
        pass
    return forms

FORMS = _load_forms()

def _sfl(items, **kwargs):
    sfl = getattr(FORMS, "SelectFromList", None) or getattr(FORMS, "select_from_list", None)
    if sfl is not None and hasattr(sfl, "show"):
        try:
            return sfl.show(items, **kwargs)
        except TypeError:
            pass
    try:
        return sfl(items, **kwargs)
    except Exception:
        return None

def _ask(prompt, title="Input", default=""):
    for name in ("ask_for_string", "ask_string", "AskForString"):
        f = getattr(FORMS, name, None)
        if callable(f):
            try:
                return f(prompt=prompt, title=title, default=default)
            except TypeError:
                try:
                    return f(prompt, default, title)
                except TypeError:
                    try:
                        return f(prompt)
                    except TypeError:
                        pass
    try:
        print("[INPUT]", title, prompt)
    except Exception:
        pass
    return default

def _fmt_current(v, ptype, unit):
    if v is None: return ""
    if ptype == "bool":
        return "Yes" if bool(v) else "No"
    if ptype == "float":
        try:
            vv = float(v)
            s = ("{:.0f}".format(vv) if vv.is_integer() else "{:g}".format(vv))
        except Exception:
            s = str(v)
        return s + ((" " + unit) if unit else "")
    return str(v)

def _parse_value(ptype, unit, raw, keep_token=""):
    if raw is None:
        return keep_token
    txt = str(raw).strip()
    if txt == "":
        return keep_token
    if ptype == "bool":
        if txt.lower() in ("yes","true","1","y","t","✓","check","tick"):
            return True
        if txt.lower() in ("no","false","0","n","f","✗","cross","x"):
            return False
        return keep_token
    if ptype == "float":
        try:
            val_txt = txt.replace(",", ".").split()[0]
            return float(val_txt)
        except Exception:
            return keep_token
    return txt

def bulk_edit(editable_params, title="Edit Parameters (ADa)"):
    """
    ADa-themed iterative editor using SelectFromList + ask_for_string.
    Shows a live list with "new value" markers; user edits rows until Apply/Cancel.
    """
    if not editable_params:
        return None

    # Working copy and change set
    rows = []
    for p in editable_params:
        rows.append({
            "name": p["name"],
            "display": p.get("display_name", p["name"]),
            "ptype": p.get("type","string"),
            "cur": p.get("value"),
            "unit": (p.get("config") or {}).get("unit",""),
            "notes": (p.get("config") or {}).get("notes",""),
            "new": None  # sentinel for "no change"
        })

    def make_menu():
        menu = []
        menu.append("Apply / Done")
        menu.append("Cancel")
        menu.append("—")  # separator
        for r in rows:
            cur = _fmt_current(r["cur"], r["ptype"], r["unit"])
            if r["new"] is None:
                ndisp = "(keep)"
            else:
                ndisp = _fmt_current(r["new"], r["ptype"], r["unit"])
            menu.append("• {disp:<30}  current: {cur:<10}  new: {new}".format(
                disp=r["display"], cur=cur, new=ndisp
            ))
        return menu

    while True:
        items = make_menu()
        sel = _sfl(items, title=title, multiselect=False, width=780, height=560, button_name="Select")
        if not sel:
            return None
        if sel.startswith("Apply"):
            out = {}
            for r in rows:
                if r["new"] is not None:
                    out[r["name"]] = r["new"]
            return out
        if sel.startswith("Cancel"):
            return None
        if sel == "—":
            continue

        # Which row?
        try:
            idx = items.index(sel) - 3  # subtract header + 2 actions + separator
            if idx < 0 or idx >= len(rows):
                continue
        except Exception:
            continue

        r = rows[idx]
        ptype = r["ptype"]
        unit = r["unit"]
        if ptype == "bool":
            choice = _sfl(["Keep (no change)", "Yes", "No"],
                          title="{} — {}".format(title, r["display"]),
                          multiselect=False, width=520, height=260, button_name="Set")
            if not choice or choice.startswith("Keep"):
                r["new"] = None
            elif choice == "Yes":
                r["new"] = True
            elif choice == "No":
                r["new"] = False
        else:
            prompt = "{}\n\nCurrent: {}\nUnit: {}\n(Leave blank to keep)".format(
                r["display"], _fmt_current(r["cur"], ptype, unit), unit or "—"
            )
            default = "" if r["new"] is None else str(r["new"])
            raw = _ask(prompt=prompt, title=title, default=default)
            value = _parse_value(ptype, unit, raw, keep_token=None)
            r["new"] = value

    # unreachable
    return None
