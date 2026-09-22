# MN Options Trading Bot

Ein UI-gestützter **Optionshandel-Bot** für **Interactive Brokers**, der automatisiert mehrere Strategien mit Real-Time-Daten und Technischen-Indikatoren ausführt.

## 🎯 Features

- **Mehrfach-Strategien**
  - Schedule Editor
- **Flexible Trade-Typen**
  - Bull Put Spreads
  - Put Broken Wing (PBW)
  - RUT Iron Condor
  - Butterfly-Spreads
  - Weitere benutzerdefinierte Strukturen
- **Intelligente Entry-Bedingungen**
  - RSI
  - Intraday-Bewegungen
  - SMA
  - IV Rank
  - VIX-Level
- **Position Sizing**
- **Paper & Live Trading** Unterstützung
- **Telegram-Benachrichtigungen** für Trade-Alerts
- **Detailliertes Logging** und CSV-Trade-Reports

## 📋 Voraussetzungen

### Systemanforderungen
- **Python 3.13.14**
- **Trader Workstation (TWS)** läuft lokal
- Windows

### Interactive Brokers Konfiguration
1. IB TWS muss laufen (~IP: `127.0.0.1`)
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

### 3. Abhängigkeiten installieren
pip install -r requirements.txt


## ⚙️ Konfiguration

Alle Einstellungen werden über den MN Trading Bot Manager gestartet.
Starte start_ui.vbs um den MN Trading Bot Manager zu starten.

## ⚙️ Dienst-Konfiguration
Der Bot benötigt den MN Trading Bot Scheduler (https://github.com/MaNieslony/MNTradingBotScheduler)
um automatisiert die Trades durchführen zu können.

Kurzform:
 0. Voraussetzungen installieren apscheduler, watchdog, nssm(windows)
 1. Dienst mit NSSM erstellen
 2. Arbeitsverzeichnis festlegen
 3. Log-Dateien für den Dienst festlegen (wichtig für Fehlersuche
 4. Neustart-Verhalten konfigurieren (falls das Skript einmal abstürzt)
 5. Setzt die UTF-8 Umgebungsvariable für den Windows-Dienst
 6. Description setzen
 7. Dienst starten

## 💻 Verwendung

### Grundlegender Start
python bot.py --schedule SPX-FFBPS

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
C:\ProgramData\MNTradingBotScheduler

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




