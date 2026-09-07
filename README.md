# MN Options Trading Bot

Ein konfigurdatei-gestützter **Optionshandel-Bot** für **Interactive Brokers**, der automatisiert mehrere Strategien mit Real-Time-Daten und Technischen-Indikatoren ausführt.

## 🎯 Features

- **Mehrfach-Strategien** via `config/schedules.json` (zeitbasierte Ausführung)
- **Flexible Trade-Typen** via `config/trade_templates.json`:
  - Bull Put Spreads
  - Put Broken Wing (PBW)
  - RUT Iron Condor
  - Butterfly-Spreads
  - Weitere benutzerdefinierte Strukturen
- **Intelligente Entry-Bedingungen** (konfigurierbar):
  - RSI (Relative Strength Index)
  - Intraday-Bewegungen
  - SMA (Simple Moving Average)
  - IV Rank
  - VIX-Level
- **Position Sizing** basierend auf verfügbarer Kaufkraft
- **Paper & Live Trading** Unterstützung
- **Headless CLI** für Server/Automatisierung
- **Telegram-Benachrichtigungen** für Trade-Alerts
- **Detailliertes Logging** und CSV-Trade-Reports
- **Fehlerbehandlung** mit Graceful Shutdown

## 📋 Voraussetzungen

### Systemanforderungen
- **Python 3.13.14**
- **Interactive Brokers Gateway** oder **Trader Workstation (TWS)** läuft lokal
- Windows, macOS oder Linux (macOS/Linux nicht getestet)

### Interactive Brokers Konfiguration
1. IB Gateway/TWS muss laufen (~IP: `127.0.0.1`)
2. Port `7497` (Live) oder `7498` (Paper Trading) - konfigurierbar
3. API-Zugang aktiviert in IB-Einstellungen
4. Paper oder Live Konto verfügbar

## 🚀 Installation

### 1. Repository klonen
git clone https://github.com/MaNieslony/MN_Trading_Bot.git cd MN_Trading_Bot

### 2. Python-Umgebung
Virtual Environment erstellen
python -m venv venv
Aktivieren
Windows:
venv\Scripts\activate
macOS/Linux:
source venv/bin/activate


### 3. Abhängigkeiten installieren
pip install -r requirements.txt


## ⚙️ Konfiguration

Alle Einstellungen befinden sich im `config/` Verzeichnis:

### `%userprofile%/mn_bot/config/broker_settings.json`
{ "IB_HOST": "127.0.0.1", "IB_PORT_PAPER": 7498, "IB_PORT_LIVE": 7497, "CLIENT_ID": 1, "USE_PAPER_TRADING": true }


### `%userprofile%/mn_bot/config/bot_mode_settings.json`
{ "DEBUG_MODE": false, "CHECK_CONDITIONS": true, "CHECK_EXECUTION_TIME": true, "CHECK_MARKET_OPEN": true, "TRADE_REPORT_CSV": "reports/mn_trading_trade_report.csv" }


### `%userprofile%/mn_bot/config/schedules.json`
Definiert **wann** und **unter welchen Bedingungen** gehandelt wird:
{ "schedules": [ { "NAME": "SPX-FFBPS", "ENABLED": true, "TRADE_TYPE": "BULL_PUT", "SYMBOL": "SPX", "EXECUTION_TIME": "09:35", "EXECUTION_DTE": 0, "CHECK_CONDITIONS": true, "ENTRY_CONDITIONS": [ { "type": "RSI", "period": 14, "threshold": 50, "operator": ">" } ] } ] }


### `%userprofile%/mn_bot/config/trade_templates.json`
Definiert **wie** die Trades strukturiert sind:
{ "templates": [ { "TRADE_TYPE": "BULL_PUT", "SYMBOL": "SPX", "LEGS": [...], "TARGET_DELTA": -0.20, "POSITION_SIZE": 5 } ] }

### `%userprofile%/mn_bot/config/telegram_settings.json`
{ "TELEGRAM_ENABLED": true, "TELEGRAM_BOT_TOKEN": "your_bot_token", "TELEGRAM_CHAT_ID": "your_chat_id" }


## 💻 Verwendung

### Grundlegender Start
python bot.py --schedule SPX-FFBPS

### Mit Debug-Modus
python bot.py --schedule SPX-FFBPS --debug

### Verfügbare Optionen
python bot.py --help

**MN Trading Bot Scheduler** 

Der Windows Dienst "MN Trading Bot Scheduler" läuft im Hintergrund und überwacht das jeweilige Schedules File %userprofile%/mn_bot/config/schedules.json
auf "EXECUTION_TIME": "<time>" und lädt die Schedules in seinen RAM.

Bei der Ausführung wird dann ein Windows Task Scheduler Task pro User (MN_Bot_Launcher_%USERNAME%) erstellt,
damit das Konsolenfenster des Bots (python bot.py --schedule <schedule-name>) im User-Kontext während des Durchlaufs sichtbar dargestellt wird.

Der Windows Task ruft wiederum C:/MN_Trading_Bot/run_bot.bat auf
@echo off
set USERNAME_PARAM=%~1
set TASK_NAME=%~2
set BOT_DIR=%~3
set PYTHON_EXE=%~4
set SCRIPT_PATH=%~5

cd /d "%BOT_DIR%"

:: 1. Gezieltes Beenden alter Instanzen genau dieser Schedule für diesen User
taskkill /F /FI "USERNAME eq %USERNAME_PARAM%" /FI "WINDOWTITLE eq MN Trading Bot - %TASK_NAME%*" /IM python.exe >nul 2>&1

:: 2. Warten, damit Ressourcen/Ports sauber freigegeben werden (0.5 Sekunde)
timeout /t 1 /nobreak >nul

:: 3. Starten des Bots in einem frischen Konsolenfenster
start "MN Trading Bot - %TASK_NAME%" "%PYTHON_EXE%" -u "%SCRIPT_PATH%" --schedule "%TASK_NAME%"


## 📁 Projektstruktur
C:\ProgramData\C:\ProgramData\MNTradingBotScheduler

├── service_runner.py


# 1. Dienst mit NSSM erstellen
nssm install "MN Trading Bot Scheduler"  "python.exe" "C:\ProgramData\MNTradingBotScheduler\service_runner.py"

# 2. Arbeitsverzeichnis festlegen
nssm set "MN Trading Bot Scheduler" AppDirectory "C:\ProgramData\MNTradingBotScheduler"

# 3. Log-Dateien für den Dienst festlegen (wichtig für Fehlersuche)
nssm set "MN Trading Bot Scheduler" AppStdout "C:\ProgramData\MNTradingBotScheduler\service_out.log"
nssm set "MN Trading Bot Scheduler  AppStderr "C:\ProgramData\MNTradingBotScheduler\service_err.log"

# 4. Neustart-Verhalten konfigurieren (falls das Skript einmal abstürzt)
nssm set "MN Trading Bot Scheduler" AppExit Default Restart
nssm set "MN Trading Bot Scheduler" AppRestartDelay 5000

# 5. Setzt die UTF-8 Umgebungsvariable für den Windows-Dienst
nssm set "MN Trading Bot Scheduler" AppEnvironmentExtra "PYTHONUTF8=1"

# 6. Description setzen
nssm set "MN Trading Bot Scheduler" Description "Multi-User Trading Scheduler Dienst zur automatischen Steuerung und Ausführung von Python Bot Instanzen."



**Verfügbare Schedules** werden angezeigt, wenn `--schedule` fehlt.

## 📁 Projektstruktur
MN_Trading_Bot/ ├── bot.py                          # Haupteinstiegspunkt ├── requirements.txt                # Python-Abhängigkeiten ├── README.md                       # Diese Datei │ ├── config/                         # Konfigurationsdateien │   ├── schedules.json              # Handels-Zeitpläne & Bedingungen │   ├── trade_templates.json        # Trade-Strukturen (Legs, Deltas) │   ├── broker_settings.json        # IB-Verbindungs-Einstellungen │   ├── bot_mode_settings.json      # DEBUG, Markt-Flags │   └── telegram_settings.json      # Telegram-Benachrichtigungen │ ├── broker/                         # Interactive Brokers Integration │   ├── ib_broker.py                # IBBroker-Klasse │   └── ib_errors.py                # Fehlerbehandlung │ ├── market/                         # Marktdaten & Kontakte │   ├── market_data.py              # Real-Time Daten │   ├── market_flow.py              # Daten-Stream Handling │   ├── contracts.py                # Kontakt-Verwaltung │   └── adapters.py                 # Marktdaten-Adapter │ ├── conditions/                     # Entry-Bedingungen │   └── entry_conditions.py         # RSI, SMA, IV Rank, etc. │ ├── tradetype/                      # Trade-Typ-Implementierungen │   ├── bull_put.py                 # Bull Put Spread │   ├── pbw.py                      # Put Broken Wing │   └── rut_iron_condor.py          # RUT Iron Condor │ ├── trade/                          # Trade Execution & Logging │   ├── trading_cycle.py            # Haupthandels-Zyklus │   ├── execution.py                # Order-Ausführung │   ├── combo_factory.py            # Multi-Leg Kombinationen │   ├── position_sizing.py          # Positionsgröße-Berechnung │   ├── trade_logger.py             # Trade-Protokollierung │   └── telegram.py                 # Benachrichtigungen │ ├── runtime/                        # Runtime-Hilfsfunktionen │   ├── context/                    # Market & Schedule Context │   ├── validation.py               # Startup-Validierung │   ├── shutdown.py                 # Sauberes Herunterfahren │   └── sleep.py                    # Unterbrechbare Schlaf-Funktion │ ├── logs/                           # Log-Dateien │   └── mn_trading_bot_YYYYMMDD.log │ ├── reports/                        # Trade-Reports │   └── mn_trading_trade_report.csv │ └── bot_logging.py                  # Logging-Konfiguration


## 📊 Output & Reports

### Log-Dateien
%userprofile%/mn_bot/logs/mn_trading_bot_YYYYMMDD.log

Detaillierte Logs für Debugging und Audit-Zwecke.

### Trade-Reports (CSV)
%userprofile%/mn_bot/reports/mn_trading_trade_report.csv %userprofile%/mn_bot/reports/mn_trading_trade_report_PAPER.csv  (Paper Trading)

Spalten:
- Trade ID
- Symbol
- Trade-Typ
- Eröffnungs-/Schließungs-Zeit
- Gewinn/Verlust
- Kommissionen
- Status

## 🔌 Verbindung zu Interactive Brokers

1. **IB Gateway oder TWS starten**
2. Sicherstellen, dass API-Verbindungen auf dem konfigurierten Port aktiviert sind
3. Bot startet automatisch Verbindung
4. Bei Verbindungsfehler → Logs prüfen


## Debugging: Logs anschauen
tail -f %userprofile%/mn_bot/logs/mn_trading_bot_YYYYMMDD.log


## 🧪 Testing
Pytest ausführen
pytest
Mit Coverage
pytest --cov=. --cov-report=html


## 🛑 Graceful Shutdown

Bot reagiert auf **Ctrl+C** (SIGINT) und fahrt sauber herunter:
- Offene Positionen werden gemanagt
- Logs werden geflusht
- Verbindung zu IB wird geschlossen

## 📝 Lizenz

Siehe LICENSE-Datei.

## 👤 Autor

**MaNieslony**  
GitHub: [MaNieslony/MN_Trading_Bot](https://github.com/MaNieslony/MN_Trading_Bot)

## 🤝 Contributing

1. Fork das Projekt
2. Erstelle einen Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## ⚠️ Disclaimer

**KEIN FINANZIELLE BERATUNG!** Dieser Bot wird zu Testzwecken bereitgestellt. 

- Nutze **zunächst Paper Trading** zum Testen
- Verstehe deine Strategien vollständig
- Risiko-Management ist deine Verantwortung
- Test gründlich vor Live-Trading

## 📞 Support & Kontakt

Bei Fragen oder Bugs:
1. GitHub Issues erstellen
2. Logs überprüfen: `logs/mn_trading_bot_YYYYMMDD.log`
3. Konfiguration validieren

---

**Status:** 🟢 Aktiv unter Entwicklung




