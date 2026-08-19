# config_trade_ui.py
# Trade Parameter UI for MN Trading Bot (TAT-like)
# Run: python -m streamlit run config_trade_ui.py

import json
from pathlib import Path
import streamlit as st

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
CONFIG_DIR = Path("config")
SCHEDULES_FILE = CONFIG_DIR / "schedules.json"
TEMPLATES_FILE = CONFIG_DIR / "trade_templates.json"

# ------------------------------------------------------------
# Available Entry Conditions (UI definition only)
# ------------------------------------------------------------
AVAILABLE_CONDITIONS = {
    "RSI": {
        "label": "RSI",
        "fields": {
            "PERIOD": ("Periode", 14, "int"),
            "MIN": ("Min", 50, "int"),
            "MAX": ("Max", 75, "int"),
        },
    },
    "INTRADAY_MOVE": {
        "label": "Intraday Move",
        "fields": {
            "MIN_PCT": ("Min %", 0.30, "float"),
        },
    },
    "ABOVE_SMA": {
        "label": "Price above SMA",
        "fields": {
            "PERIOD": ("SMA Periode", 5, "int"),
        },
    },
}

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def load_json(path: Path):
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def cleanup_legacy_keys(template: dict):
    """Remove legacy keys so we don't regress to old schema."""
    legacy = [
        # old execution keys
        "MIN_ENTRY_PRICE",
        "MAX_ENTRY_PRICE",
        "MAX_NUM_ATTEMPTS",
        "WAIT_PER_ATTEMPT",
        "ADJUSTMENT_STEP",
        # old ndx steering keys
        "DELTA_MIN_OFFSET",
        "DELTA_MAX",
        "DELTA_EXPANSION",
        "RESCAN_SHORT_LEG_INCREMENT",
        "MAX_STRIKE_ATTEMPTS",
    ]
    for k in legacy:
        template.pop(k, None)


def tick_step_for_symbol(symbol: str) -> float:
    symbol = (symbol or "").upper()
    if symbol == "SPX":
        return 0.05
    if symbol == "NDX":
        return 0.02
    return 0.05


def is_ndx_like(template: dict) -> bool:
    return (template.get("SYMBOL") == "NDX") or ((template.get("TEMPLATENAME") or "").startswith("NDX"))


def is_pbw_like(template: dict) -> bool:
    tt = (template.get("TRADE_TYPE") or "").upper()
    return tt in ("PBW", "PUT_BROKEN_WING")


def find_template_by_name(templates: list, name: str) -> dict | None:
    for t in templates:
        if t.get("TEMPLATENAME") == name:
            return t
    return None


def find_schedule_by_name(schedules: list, name: str) -> dict | None:
    for s in schedules:
        if s.get("NAME") == name:
            return s
    return None


def normalize_bool(v, default=False) -> bool:
    if v is None:
        return default
    return bool(v)


# ------------------------------------------------------------
# Page setup
# ------------------------------------------------------------
st.set_page_config(
    page_title="MN Trading Bot – Trade UI",
    layout="wide",
)

# ============================================================
# LOAD CONFIGS
# ============================================================
schedules = load_json(SCHEDULES_FILE)
templates = load_json(TEMPLATES_FILE)

st.sidebar.title("📊 MN Trading Bot")

if not isinstance(schedules, list) or not isinstance(templates, list) or not schedules or not templates:
    st.sidebar.error("❌ Config files not found or invalid JSON")
    st.stop()

# ============================================================
# SIDEBAR: NAVIGATION
# ============================================================
page = st.sidebar.radio(
    "Navigation",
    options=["📅 Scheduled Trades", "🧩 Trade Templates"],
    index=0,
)

# ============================================================
# SIDEBAR: IMPORT / EXPORT
# ============================================================
st.sidebar.markdown("---")
st.sidebar.subheader("📦 Import / Export")

# EXPORT
st.sidebar.markdown("**⬇ Export**")
st.sidebar.download_button(
    label="⬇ schedules.json exportieren",
    data=json.dumps(schedules, indent=2, ensure_ascii=False),
    file_name="schedules.json",
    mime="application/json",
)
st.sidebar.download_button(
    label="⬇ trade_templates.json exportieren",
    data=json.dumps(templates, indent=2, ensure_ascii=False),
    file_name="trade_templates.json",
    mime="application/json",
)

# IMPORT
st.sidebar.markdown("---")
st.sidebar.markdown("**⬆ Import**")
uploaded_schedules = st.sidebar.file_uploader(
    "schedules.json importieren",
    type=["json"],
    key="import_schedules",
)
uploaded_templates = st.sidebar.file_uploader(
    "trade_templates.json importieren",
    type=["json"],
    key="import_templates",
)

if uploaded_schedules or uploaded_templates:
    if st.sidebar.button("✅ Import anwenden"):
        try:
            if uploaded_schedules:
                new_schedules = json.loads(uploaded_schedules.read().decode("utf-8"))
                save_json(SCHEDULES_FILE, new_schedules)
                st.sidebar.success("✅ schedules.json importiert")

            if uploaded_templates:
                new_templates = json.loads(uploaded_templates.read().decode("utf-8"))
                save_json(TEMPLATES_FILE, new_templates)
                st.sidebar.success("✅ trade_templates.json importiert")

            st.sidebar.warning("🔄 Seite neu laden, um Änderungen zu sehen")
        except Exception as e:
            st.sidebar.error(f"❌ Import fehlgeschlagen: {e}")

# ============================================================
# MAIN HEADER
# ============================================================
st.title("Trade Automation Toolbox – MN Bot")
st.caption("TAT‑ähnliches Dashboard: Schedules (Wann/Qty/Filter) & Templates (Was/Wie/Execution/Profit Target)")

# ============================================================
# PAGE: SCHEDULED TRADES
# ============================================================
if page == "📅 Scheduled Trades":
    schedule_names = [s.get("NAME", "<no-name>") for s in schedules]
    selected_schedule_name = st.sidebar.selectbox("Schedule auswählen", schedule_names)

    schedule = find_schedule_by_name(schedules, selected_schedule_name)
    if not schedule:
        st.error("❌ Schedule nicht gefunden")
        st.stop()

    # resolve template
    schedule_template_name = schedule.get("TRADETEMPLATE")
    if not schedule_template_name:
        st.sidebar.error("❌ Schedule hat kein Feld 'TRADETEMPLATE'")
        st.stop()

    template = find_template_by_name(templates, schedule_template_name)
    if not template:
        st.sidebar.error(f"❌ Template '{schedule_template_name}' nicht gefunden")
        st.stop()

    # Active config box
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Aktive Konfiguration**")
    st.sidebar.write(f"• Schedule: `{schedule.get('NAME')}`")
    st.sidebar.write(f"• Template: `{template.get('TEMPLATENAME')}`")
    st.sidebar.write(f"• TradeType: `{template.get('TRADE_TYPE')}`")
    st.sidebar.write(f"• Symbol: `{template.get('SYMBOL')}`")

    # Session‑state sync for entry conditions
    if st.session_state.get("_active_schedule") != selected_schedule_name:
        st.session_state._active_schedule = selected_schedule_name
        st.session_state.entry_conditions = dict(schedule.get("ENTRY_CONDITIONS", {}))

    entry_conditions = st.session_state.entry_conditions

    # ----- Tabs like TAT -----
    tab_details, tab_conditions, tab_preview = st.tabs(["🗓 Details", "📊 Entry Conditions", "🧪 Preview"])

    with tab_details:
        st.subheader("Schedule Details")

        c1, c2, c3 = st.columns(3)
        with c1:
            schedule["EXECUTION_TIME"] = st.text_input(
                "Execution Time (HH:MM:SS)",
                schedule.get("EXECUTION_TIME", "09:30:00"),
            )
        with c2:
            schedule["EXPIRATION_MINUTES"] = st.number_input(
                "Expiration Minutes",
                min_value=0,
                max_value=120,
                value=int(schedule.get("EXPIRATION_MINUTES", 5)),
            )
        with c3:
            qty_cfg = schedule.setdefault("QUANTITY", {})
            qty_cfg["MODE"] = "FixedQty"
            qty_cfg["QTY"] = st.number_input(
                "Quantity (FixedQty)",
                min_value=1,
                max_value=200,
                value=int(qty_cfg.get("QTY", 1)),
            )

        st.markdown("#### Linked Template (read-only)")
        st.code(
            f"TEMPLATENAME: {template.get('TEMPLATENAME')}\n"
            f"TRADE_TYPE:   {template.get('TRADE_TYPE')}\n"
            f"SYMBOL:       {template.get('SYMBOL')}\n",
            language="text",
        )

    with tab_conditions:
        st.subheader("Entry Conditions (AND)")

        remove_keys = []
        for cond_key in list(entry_conditions.keys()):
            cond_cfg = entry_conditions.get(cond_key, {})
            cond_def = AVAILABLE_CONDITIONS.get(cond_key)
            if not cond_def:
                continue

            entry_conditions.setdefault(cond_key, {})

            with st.container(border=True):
                cols = st.columns([4, 1])
                cols[0].markdown(f"**{cond_def['label']}**")
                if cols[1].button("🗑 Entfernen", key=f"remove_{selected_schedule_name}_{cond_key}"):
                    remove_keys.append(cond_key)
                    continue

                for field_key, (label, default, kind) in cond_def["fields"].items():
                    widget_key = f"ec_{selected_schedule_name}_{cond_key}_{field_key}"
                    default_value = cond_cfg.get(field_key, default)

                    if kind == "int":
                        entry_conditions[cond_key][field_key] = st.number_input(
                            label,
                            value=int(default_value),
                            step=1,
                            format="%d",
                            key=widget_key,
                        )
                    else:
                        entry_conditions[cond_key][field_key] = st.number_input(
                            label,
                            value=float(default_value),
                            key=widget_key,
                        )

                if "ORDER" not in entry_conditions[cond_key]:
                    entry_conditions[cond_key]["ORDER"] = int(cond_cfg.get("ORDER", 1))

        if remove_keys:
            for k in remove_keys:
                entry_conditions.pop(k, None)
            st.rerun()

        st.markdown("**➕ Condition hinzufügen**")
        available_to_add = [k for k in AVAILABLE_CONDITIONS.keys() if k not in entry_conditions]

        if available_to_add:
            new_cond = st.selectbox(
                "Condition Typ",
                available_to_add,
                format_func=lambda k: AVAILABLE_CONDITIONS[k]["label"],
            )
            if st.button("Hinzufügen"):
                entry_conditions[new_cond] = {
                    field: default
                    for field, (_, default, _) in AVAILABLE_CONDITIONS[new_cond]["fields"].items()
                }
                max_order = 0
                for v in entry_conditions.values():
                    try:
                        max_order = max(max_order, int(v.get("ORDER", 0)))
                    except Exception:
                        pass
                entry_conditions[new_cond]["ORDER"] = max_order + 1
                st.rerun()
        else:
            st.info("Keine Entry Conditions aktiv")

    with tab_preview:
        st.subheader("Dry‑Run (keine Marktdaten, keine Orders)")
        st.caption("Vorschau: Was würde der Bot mit dieser Konfiguration tun?")

        st.markdown("### ⏰ Schedule")
        st.write(f"**Name:** `{schedule['NAME']}`")
        st.write(f"**Execution Time:** `{schedule.get('EXECUTION_TIME')}`")
        st.write(f"**Expiration Window:** `{schedule.get('EXPIRATION_MINUTES', 5)} min`")

        qty = schedule.get("QUANTITY", {})
        st.write(f"**Quantity:** {qty.get('MODE', 'FixedQty')} ({qty.get('QTY', '?')})")

        st.markdown("### 📊 Entry Conditions")
        if entry_conditions:
            for k, v in sorted(entry_conditions.items(), key=lambda x: x[1].get("ORDER", 0)):
                st.write(f"- **{k}** → {v}")
        else:
            st.info("Keine Entry‑Conditions → Bot würde **immer** handeln (wenn Markt/Time es erlauben).")

        st.markdown("### 🧩 Template Summary")
        st.write(f"**Template:** `{template.get('TEMPLATENAME')}`")
        st.write(f"**TradeType:** `{template.get('TRADE_TYPE')}`")
        st.write(f"**Symbol:** `{template.get('SYMBOL')}`")

        st.markdown("### ⚙️ Execution / Sweep")
        min_p = float(template.get("MIN_SWEEP_PRICE", -1.0))
        max_p = float(template.get("MAX_SWEEP_PRICE", -0.3))
        step = float(template.get("SWEEP_STEP", tick_step_for_symbol(template.get('SYMBOL', 'SPX'))))
        st.write(f"**Sweep Range:** {min_p:.2f} → {max_p:.2f} (Step {step})")
        st.write(f"**Attempts:** {template.get('MAX_SWEEP_ATTEMPTS', '?')} @ {template.get('SWEEP_WAIT_SECONDS', '?')}s")

        warnings = []
        if min_p > max_p:
            warnings.append("MIN_SWEEP_PRICE > MAX_SWEEP_PRICE (intern sortiert, aber unleserlich).")
        if step <= 0:
            warnings.append("SWEEP_STEP ≤ 0 → Sweep unmöglich.")
        if abs(max_p - min_p) < step:
            warnings.append("Sweep‑Range < Sweep‑Step → effektiv nur 1 Versuch.")

        if warnings:
            for w in warnings:
                st.warning(w)
        else:
            st.success("Keine offensichtlichen logischen Konflikte erkannt.")

    st.markdown("---")
    if st.button("✅ Schedule speichern", type="primary"):
        schedule["ENTRY_CONDITIONS"] = dict(st.session_state.entry_conditions)
        save_json(SCHEDULES_FILE, schedules)
        st.success("✅ schedules.json gespeichert")

# ============================================================
# PAGE: TRADE TEMPLATES
# ============================================================
else:
    template_names = [t.get("TEMPLATENAME", "<no-name>") for t in templates]
    selected_template_name = st.sidebar.selectbox("Template auswählen", template_names)

    template = find_template_by_name(templates, selected_template_name)
    if not template:
        st.error("❌ Template nicht gefunden")
        st.stop()

    trade_type = (template.get("TRADE_TYPE") or "").upper()
    symbol = (template.get("SYMBOL") or "SPX").upper()
    default_step = tick_step_for_symbol(symbol)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Aktives Template**")
    st.sidebar.write(f"• Template: `{template.get('TEMPLATENAME')}`")
    st.sidebar.write(f"• TradeType: `{template.get('TRADE_TYPE')}`")
    st.sidebar.write(f"• Symbol: `{template.get('SYMBOL')}`")

    tab_struct, tab_exec, tab_profit, tab_ndx = st.tabs([
        "📐 Structure",
        "⚙️ Execution / Sweep",
        "🎯 Profit Target",
        "🧭 NDX Steering",
    ])

    # ----------------------------
    # STRUCTURE
    # ----------------------------
    with tab_struct:
        st.subheader("Trade Structure")

        c1, c2, c3 = st.columns(3)
        with c1:
            template["SYMBOL"] = st.selectbox("Symbol", options=["SPX", "NDX"], index=0 if symbol == "SPX" else 1)
        with c2:
            template["COMMISSION_PER_CONTRACT"] = st.number_input(
                "Commission per Contract",
                min_value=0.0,
                max_value=10.0,
                step=0.01,
                value=float(template.get("COMMISSION_PER_CONTRACT", 1.64)),
            )
        with c3:
            template["TRADE_TYPE"] = st.text_input("Trade Type", value=template.get("TRADE_TYPE", ""))

        is_pbw = is_pbw_like(template)

        st.markdown("### Legs")

        # Common leg fields (keep minimal)
        # Actions & Put/Call are usually fixed per template, but editable if you want.
        colA, colB, colC = st.columns(3)
        with colA:
            template["LEG1_ACTION"] = st.text_input("LEG1_ACTION", value=template.get("LEG1_ACTION", "SELL"))
            template["LEG1_PUT_CALL"] = st.text_input("LEG1_PUT_CALL", value=template.get("LEG1_PUT_CALL", "P"))
        with colB:
            template["LEG1_QTY"] = st.number_input("LEG1_QTY", min_value=1, max_value=10, value=int(template.get("LEG1_QTY", 1)))
            template["LEG1_DTE"] = st.number_input("LEG1_DTE", min_value=0, max_value=365, value=int(template.get("LEG1_DTE", 0)))
        with colC:
            template["LEG1_TARGET_TYPE"] = st.text_input("LEG1_TARGET_TYPE", value=template.get("LEG1_TARGET_TYPE", "Delta"))
            template["LEG1_TARGET"] = st.number_input("LEG1_TARGET", value=float(template.get("LEG1_TARGET", 35)))

        st.markdown("#### Leg 2")
        colA, colB, colC = st.columns(3)
        with colA:
            template["LEG2_ACTION"] = st.text_input("LEG2_ACTION", value=template.get("LEG2_ACTION", "BUY"))
            template["LEG2_PUT_CALL"] = st.text_input("LEG2_PUT_CALL", value=template.get("LEG2_PUT_CALL", "P"))
        with colB:
            template["LEG2_QTY"] = st.number_input("LEG2_QTY", min_value=1, max_value=10, value=int(template.get("LEG2_QTY", 1)))
            template["LEG2_DTE"] = st.number_input("LEG2_DTE", min_value=0, max_value=365, value=int(template.get("LEG2_DTE", 0)))
        with colC:
            template["LEG2_TARGET_TYPE"] = st.text_input("LEG2_TARGET_TYPE", value=template.get("LEG2_TARGET_TYPE", "StrikeOffset_Leg1"))
            template["LEG2_TARGET"] = st.number_input("LEG2_TARGET", value=float(template.get("LEG2_TARGET", -10)))

        if is_pbw:
            st.markdown("#### Leg 3 (PBW)")
            colA, colB, colC = st.columns(3)
            with colA:
                template["LEG3_ACTION"] = st.text_input("LEG3_ACTION", value=template.get("LEG3_ACTION", "BUY"))
                template["LEG3_PUT_CALL"] = st.text_input("LEG3_PUT_CALL", value=template.get("LEG3_PUT_CALL", "P"))
            with colB:
                template["LEG3_QTY"] = st.number_input("LEG3_QTY", min_value=1, max_value=10, value=int(template.get("LEG3_QTY", 1)))
                template["LEG3_DTE"] = st.number_input("LEG3_DTE", min_value=0, max_value=365, value=int(template.get("LEG3_DTE", 0)))
            with colC:
                template["LEG3_TARGET_TYPE"] = st.text_input("LEG3_TARGET_TYPE", value=template.get("LEG3_TARGET_TYPE", "StrikeOffset_Leg1"))
                template["LEG3_TARGET"] = st.number_input("LEG3_TARGET", value=float(template.get("LEG3_TARGET", 40)))

    # ----------------------------
    # EXECUTION / SWEEP
    # ----------------------------
    with tab_exec:
        st.subheader("Execution / Sweep (Fill Progression)")

        c1, c2, c3 = st.columns(3)

        with c1:
            template["MIN_SWEEP_PRICE"] = st.number_input(
                "Min Sweep Price (best credit)",
                value=float(template.get("MIN_SWEEP_PRICE", -1.0)),
                step=default_step,
            )
            template["MAX_SWEEP_PRICE"] = st.number_input(
                "Max Sweep Price (ceiling)",
                value=float(template.get("MAX_SWEEP_PRICE", -0.30)),
                step=default_step,
            )

        with c2:
            template["MAX_SWEEP_ATTEMPTS"] = st.number_input(
                "Max Sweep Attempts",
                min_value=1,
                max_value=200,
                value=int(template.get("MAX_SWEEP_ATTEMPTS", 10)),
            )
            template["SWEEP_WAIT_SECONDS"] = st.number_input(
                "Wait per Sweep (sec)",
                min_value=1,
                max_value=60,
                value=int(template.get("SWEEP_WAIT_SECONDS", 5)),
            )

        with c3:
            template["SWEEP_STEP"] = st.number_input(
                "Sweep Step",
                min_value=0.01,
                max_value=1.0,
                step=0.01,
                value=float(template.get("SWEEP_STEP", default_step)),
            )

        # Basic validation hint
        if float(template["MIN_SWEEP_PRICE"]) > float(template["MAX_SWEEP_PRICE"]):
            st.warning("Hinweis: MIN_SWEEP_PRICE ist größer als MAX_SWEEP_PRICE. Der Bot sortiert das intern, aber für Lesbarkeit bitte prüfen.")

    # ----------------------------
    # PROFIT TARGET
    # ----------------------------
    with tab_profit:
        st.subheader("Profit Target")

        enabled = normalize_bool(template.get("PROFIT_TARGET_ENABLED", False), False)
        template["PROFIT_TARGET_ENABLED"] = st.toggle("Enable Profit Target", value=enabled)

        if template["PROFIT_TARGET_ENABLED"]:
            # Support "PROFIT_TARGET_PCT: null" -> logging-only
            current_pct = template.get("PROFIT_TARGET_PCT", 50)
            logging_only = current_pct is None

            place_exit = st.toggle("Place Exit Order (GTC)", value=not logging_only)

            c1, c2 = st.columns(2)
            with c1:
                if place_exit:
                    # ensure pct exists
                    pct_val = 50 if current_pct is None else int(current_pct)
                    template["PROFIT_TARGET_PCT"] = st.number_input(
                        "Profit Target (%)",
                        min_value=1,
                        max_value=100,
                        value=int(pct_val),
                    )
                else:
                    template["PROFIT_TARGET_PCT"] = None
                    st.info("Logging-only: PROFIT_TARGET_PCT wird als null gespeichert (kein Exit-Order).")

            with c2:
                template["PROFIT_TARGET_ETH"] = st.toggle(
                    "Extended Trading Hours (outsideRth)",
                    value=normalize_bool(template.get("PROFIT_TARGET_ETH", False), False),
                )
        else:
            # keep schema clean (optional)
            # template["PROFIT_TARGET_PCT"] = template.get("PROFIT_TARGET_PCT", 50)
            # template["PROFIT_TARGET_ETH"] = template.get("PROFIT_TARGET_ETH", False)
            st.caption("Profit Target ist deaktiviert für dieses Template.")

    # ----------------------------
    # NDX Steering (only if NDX-like)
    # ----------------------------
    with tab_ndx:
        if is_ndx_like(template):
            st.subheader("NDX Delta / Strike Steering")

            c1, c2, c3 = st.columns(3)
            with c1:
                template["DELTA_TARGET_OFFSET"] = st.number_input(
                    "Delta Target Offset (points)",
                    min_value=0.0,
                    max_value=5.0,
                    step=0.1,
                    value=float(template.get("DELTA_TARGET_OFFSET", 0.2)),
                )
            with c2:
                template["DELTA_MAX_ABS"] = st.number_input(
                    "Delta Max Abs (points)",
                    min_value=0.5,
                    max_value=20.0,
                    step=0.5,
                    value=float(template.get("DELTA_MAX_ABS", 5.0)),
                )
            with c3:
                template["DELTA_RESCAN_EXPANSION"] = st.number_input(
                    "Delta Expansion / Rescan (points)",
                    min_value=0.0,
                    max_value=10.0,
                    step=0.1,
                    value=float(template.get("DELTA_RESCAN_EXPANSION", 0.7)),
                )

            st.markdown("### Short-Leg Mid Steering")
            c1, c2, c3 = st.columns(3)
            with c1:
                template["SHORT_LEG_MID_MIN"] = st.number_input(
                    "Short Leg Mid Min ($)",
                    min_value=0.0,
                    max_value=50.0,
                    step=0.05,
                    value=float(template.get("SHORT_LEG_MID_MIN", 1.0)),
                )
            with c2:
                template["SHORT_LEG_MID_MAX"] = st.number_input(
                    "Short Leg Mid Max ($)",
                    min_value=0.0,
                    max_value=50.0,
                    step=0.05,
                    value=float(template.get("SHORT_LEG_MID_MAX", 2.5)),
                )
            with c3:
                template["SHORT_LEG_MID_EXPANSION"] = st.number_input(
                    "Short Leg Mid Expansion / Rescan ($)",
                    min_value=0.0,
                    max_value=10.0,
                    step=0.05,
                    value=float(template.get("SHORT_LEG_MID_EXPANSION", 0.25)),
                )

            st.markdown("### Strike Window")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                template["STRIKE_UPPER_OFFSET"] = st.number_input(
                    "Upper Offset (pts)",
                    min_value=0,
                    max_value=5000,
                    value=int(template.get("STRIKE_UPPER_OFFSET", 300)),
                )
            with c2:
                template["STRIKE_LOWER_OFFSET"] = st.number_input(
                    "Lower Offset (pts)",
                    min_value=0,
                    max_value=10000,
                    value=int(template.get("STRIKE_LOWER_OFFSET", 600)),
                )
            with c3:
                template["STRIKE_STEP"] = st.number_input(
                    "Strike Step",
                    min_value=1,
                    max_value=100,
                    value=int(template.get("STRIKE_STEP", 10)),
                )
            with c4:
                template["MAX_STRIKE_SCAN"] = st.number_input(
                    "Max Strike Scan",
                    min_value=1,
                    max_value=500,
                    value=int(template.get("MAX_STRIKE_SCAN", 40)),
                )

            template["MAX_RESCAN_ATTEMPTS"] = st.number_input(
                "Max Rescan Attempts",
                min_value=1,
                max_value=50,
                value=int(template.get("MAX_RESCAN_ATTEMPTS", 5)),
            )
        else:
            st.info("NDX-Steering ist nur für NDX-Templates relevant.")

    # SAVE TEMPLATE
    st.markdown("---")
    if st.button("✅ Template speichern", type="primary"):
        cleanup_legacy_keys(template)
        save_json(TEMPLATES_FILE, templates)
        st.success("✅ trade_templates.json gespeichert")
