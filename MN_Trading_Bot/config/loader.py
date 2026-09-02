# config/loader.py

import json
import os

def _config_dir() -> str:
    """
    Basisverzeichnis für Config-Dateien.

    Default: "config" (relativ zum aktuellen Arbeitsverzeichnis – exakt das
    bisherige Verhalten, 100% rückwärtskompatibel).

    Für Multi-User-Setups (z.B. Trading Partner mit eigenem Windows-Account,
    aber gemeinsamem Botcode) kann per Umgebungsvariable MN_BOT_CONFIG_DIR
    ein user-spezifisches Verzeichnis erzwungen werden – unabhängig davon,
    aus welchem cwd der Bot gestartet wird:

        $env:MN_BOT_CONFIG_DIR = "C:\Users\Partner\mn_bot\config"
    """
    return os.environ.get("MN_BOT_CONFIG_DIR", "config")


def load_json_config(path: str, defaults: dict) -> dict:
    """
    Generic JSON config loader with defaults.
    """
    if not os.path.exists(path):
        return defaults.copy()

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            merged = defaults.copy()
            merged.update(data)
            return merged
    except Exception as e:
        print(f"⚠️ Failed to load {path}: {e}")
        return defaults.copy()

def load_bot_mode_settings() -> dict:
    defaults = {
        "DEBUG_MODE": True,
        "CHECK_CONDITIONS": True,
        "CHECK_EXECUTION_TIME": True,
        "CHECK_MARKET_OPEN": True,
    }

    return load_json_config(
        os.path.join(_config_dir(), "bot_mode_settings.json"),
        defaults
    )

def load_broker_settings() -> dict:
    """
    Load broker (IB) connection settings.
    """

    defaults = {
        "IB_HOST": "127.0.0.1",
        "IB_PORT_LIVE": 7496,
        "IB_PORT_PAPER": 7497,
        "USE_PAPER_TRADING": True,
        "CLIENT_ID": 1,
    }

    return load_json_config(
        os.path.join(_config_dir(), "broker_settings.json"),
        defaults
    )

def load_telegram_settings() -> dict:
    defaults = {
        "TELEGRAM_ENABLED": False,
        "TELEGRAM_CHAT_ID": "",
        "TELEGRAM_BOT_TOKEN": "",
    }

    return load_json_config(
        os.path.join(_config_dir(), "telegram_settings.json"),
        defaults
    )

def load_trade_templates() -> dict[str, dict]:
    """
    Load trade templates keyed by TEMPLATENAME.
    """
    path = os.path.join(_config_dir(), "trade_templates.json")

    if not os.path.exists(path):
        print("⚠️ trade_templates.json not found")
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Erwartet: Liste von Templates
        return {
            t["TEMPLATENAME"]: t
            for t in data
            if "TEMPLATENAME" in t
        }

    except Exception as e:
        print(f"⚠️ Failed to load trade_templates.json: {e}")
        return {}

def load_schedules() -> list[dict]:
    """
    Load raw schedules.
    """
    path = os.path.join(_config_dir(), "schedules.json")

    if not os.path.exists(path):
        print("⚠️ schedules.json not found")
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print(f"⚠️ Failed to load schedules.json: {e}")
        return []


def load_merged_schedules() -> list[dict]:
    """
    Merge schedules with trade templates into flat configs.

    Output is 100% compatible with the old
    load_strategy_schedules() return format.
    """

    templates = load_trade_templates()
    schedules = load_schedules()

    merged = []

    for sched in schedules:
        template_name = sched.get("TRADETEMPLATE")

        if not template_name:
            print(f"⚠️ Schedule without TRADETEMPLATE: {sched}")
            continue

        template = templates.get(template_name)

        if not template:
            print(
                f"⚠️ Unknown TRADETEMPLATE '{template_name}' "
                f"in schedule '{sched.get('NAME')}'"
            )
            continue

        # 1️⃣ Template ist Basis
        cfg = template.copy()

        # 2️⃣ Schedule überschreibt Template
        cfg.update(sched)

        # 3️⃣ Kompatibilitäts-Mapping (wichtig!)
        cfg["NAME"] = sched.get("NAME", template_name)

        merged.append(cfg)

    return merged