"""
Logging setup and startup utilities for Bot.
═════════════════════════════════════════════════════

Provides three functions used by bot.py:

  - _setup_logging(bot)       Called by Bot._setup_logging() to
                              initialize console + file handlers with
                              ANSI color support on Windows.

  - print_startup_banner()    Called in __main__ to print the bot's
                              startup header to the console.

  - _enable_windows_ansi()    Activates ANSI escape codes in PowerShell
                              via os.system("") — works even when stdout
                              is piped or redirected.

NOTES:
  - File handler writes full DEBUG log to mn_trading_bot_YYYMMDD.log
  - Console handler respects the bot's DEBUG_MODE flag
  - No registry edits or Windows Terminal required for color output
"""

import sys
import os

# ─────────────────────────────────────────────────────────────────────────────
# ENABLE ANSI IN WINDOWS POWERSHELL
#
# os.system("") is the most reliable trick:
#   - Spawns a null cmd process which sets ENABLE_VIRTUAL_TERMINAL_PROCESSING
#     on the *real* console (not just the Python stdout handle).
#   - Works in PowerShell 5.1, PowerShell 7, and classic cmd.exe.
#   - Safe on Linux/macOS (no-op empty shell command).
#   - Must be called before any ANSI bytes hit stdout.
# ─────────────────────────────────────────────────────────────────────────────
def _enable_windows_ansi():
    """Activate VT100/ANSI processing in the Windows console."""
    if sys.platform == "win32":
        os.system("")           # triggers ENABLE_VIRTUAL_TERMINAL_PROCESSING
        # Belt-and-suspenders: also try the ctypes route
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # Try both stdout (-10) and the real console handle
            for handle_id in (-10, -11):
                h = kernel32.GetStdHandle(handle_id)
                if h and h != -1:
                    mode = ctypes.c_ulong()
                    if kernel32.GetConsoleMode(h, ctypes.byref(mode)):
                        kernel32.SetConsoleMode(h, mode.value | 0x0004)
        except Exception:
            pass


# Call on import so it fires before anything else in SPX.py
_enable_windows_ansi()


# ─────────────────────────────────────────────────────────────────────────────
# ANSI PALETTE
# ─────────────────────────────────────────────────────────────────────────────
R        = "\033[0m"
BOLD     = "\033[1m"
G0       = "\033[38;5;240m"    # very dark gray  — dim lines / timestamps
G1       = "\033[38;5;245m"    # medium gray     — labels
G2       = "\033[38;5;252m"    # near-white      — body text
TEAL     = "\033[38;5;43m"     # section banners / profit target
GREEN    = "\033[38;5;83m"     # success / fill confirmed
YELLOW   = "\033[38;5;220m"    # sweep attempts / warnings
BLUE     = "\033[38;5;75m"     # monitoring / info
CYAN     = "\033[38;5;87m"     # price values
RED      = "\033[38;5;203m"    # errors
ORANGE   = "\033[38;5;215m"    # warnings / natural credit
BG_GREEN = "\033[48;5;22m"     # fill banner background
BG_BLUE  = "\033[48;5;17m"     # paper-trading badge background


def _rule(char="-", width=72, color=G0):
    return f"{color}{char * width}{R}"


def _kv(key, value, key_w=28, key_color=G1, val_color=CYAN):
    return f"  {key_color}{key:<{key_w}}{R}{val_color}{value}{R}"


def _bar(attempt, total, price, filled=False):
    """Sweep progress bar  [████░░░░]  N/20 @ $X.XX"""
    filled_n  = round((attempt / total) * 20)
    empty_n   = 20 - filled_n
    bar_color = GREEN if filled else YELLOW
    return (
        f"  {G1}[{bar_color}{'#' * filled_n}{G0}{'.' * empty_n}{G1}] "
        f"{G2}{attempt:>2}/{total} "
        f"{G1}@ {CYAN}${price:.2f}{R}"
    )


def print_startup_banner():
    """
    Replacement for the raw print() block in __main__.
    Prints a slim one-liner — the full bot banner comes from the logger
    once IB connects and logs PAPER/LIVE TRADING MODE.
    """
    _enable_windows_ansi()
    print(
        f"\n  {TEAL}MN TRADING BOT{R}  {G0}v1.0.0{R}  "
        f"{G1}Log: {G2}logs/mn_trading_bot_YYYMMDD.log{R}  "
        f"{G0}Ctrl+C to stop{R}\n"
    )


# ═════════════════════════════════════════════════════════════════════════════     
# _setup_logging  —  paste this entire method into Bot,
#                    replacing the existing _setup_logging()
# ═════════════════════════════════════════════════════════════════════════════
def _setup_logging(self):       
    """
    FILE    -> logs/mn_trading_bot_YYYMMDD.log  (full DEBUG detail)
    CONSOLE -> structured ANSI color output for PowerShell
    """
    import logging
    from datetime import datetime

    _enable_windows_ansi()

    # ── log file ──────────────────────────────────────────────────────────────
    logs_dir = os.environ.get("MN_BOT_LOG_DIR", "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    log_filename = os.path.join(
        logs_dir, f"mn_trading_bot_{datetime.now().strftime('%Y%m%d')}.log"
    )

    # ── UTF-8 stdout ──────────────────────────────────────────────────────────
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    # ══════════════════════════════════════════════════════════════════════════
    # CONSOLE FORMATTER
    # ══════════════════════════════════════════════════════════════════════════
    class RichConsoleFormatter(logging.Formatter):

        def format(self, record):
            msg = record.getMessage()
            lvl = record.levelname

            if not msg.strip():
                return "\x00"   # sentinel — StreamHandler will skip blank emit
            if all(c == "=" for c in msg.strip()):
                return "\x00"   # swallow raw === dividers; we draw our own

            # ── PHASE BANNERS ─────────────────────────────────────────────

            if "PAPER TRADING MODE" in msg:
                return (
                    f"\n{_rule('=', 72, TEAL)}\n"
                    f"{BG_BLUE} PAPER TRADING {R}  {G1}IB connected{R}\n"
                    f"{_rule('=', 72, TEAL)}"
                )

            if "LIVE TRADING MODE" in msg:
                return (
                    f"\n{_rule('=', 72, GREEN)}\n"
                    f"{BG_GREEN} LIVE TRADING {R}  {G1}IB connected{R}\n"
                    f"{_rule('=', 72, GREEN)}"
                )

            if "MARKET IS OPEN" in msg:
                time_part = msg.split("(")[1].split(")")[0] if "(" in msg else ""
                return (
                    f"\n{_rule('-', 72, TEAL)}\n"
                    f"  {GREEN}* MARKET OPEN{R}  {G1}{time_part}{R}\n"
                    f"{_rule('-', 72, TEAL)}"
                )

            if "SCANNING FOR" in msg.upper():
                return (
                    f"\n{_rule('-', 72, BLUE)}\n"
                    f"  {BOLD}{BLUE}SCANNING STRIKES{R}  "
                    f"{G1}Looking for strikes...{R}\n"
                    f"{_rule('-', 72, BLUE)}"
                )

            if "COMBO PRICE" in msg:
                return (
                    f"\n{_rule('-', 72, BLUE)}\n"
                    f"  {BOLD}{BLUE}MARKET QUOTES{R}\n"
                    f"{_rule('-', 72, BLUE)}"
                )

            if "EXECUTING CREDIT SWEEP" in msg:
                return (
                    f"\n{_rule('-', 72, YELLOW)}\n"
                    f"  {BOLD}{YELLOW}CREDIT SWEEP{R}  "
                    f"{G1}Sweeping from mid toward ceiling...{R}\n"
                    f"{_rule('-', 72, YELLOW)}"
                )

            if "✅ ORDER FILLED" in msg or "ORDER FILLED ✅" in msg:
                return (
                    f"\n{_rule('=', 72, GREEN)}\n"
                    f"  {BOLD}{BG_GREEN} ORDER FILLED {R}  "
                    f"{BOLD}{GREEN}Position entered{R}\n"
                    f"{_rule('=', 72, GREEN)}"
                )
            if msg.strip() == "SUMMARY":
                return (
                    f"\n{_rule('=', 72, G0)}\n"
                    f"  {BOLD}{G2}SUMMARY{R}\n"
                    f"{_rule('=', 72, G0)}"
                )

            if "PROFIT TARGET ORDER PLACED" in msg:
                return (
                    f"\n{_rule('-', 72, TEAL)}\n"
                    f"  {BOLD}{TEAL}PROFIT TARGET ORDER{R}  "
                    f"{G1}GTC sell order placed{R}\n"
                    f"{_rule('-', 72, TEAL)}"
                )

            if "PROFIT TARGET MONITOR - STARTING" in msg:
                return (
                    f"\n{_rule('-', 72, BLUE)}\n"
                    f"  {BOLD}{BLUE}PROFIT TARGET MONITOR{R}  "
                    f"{G1}Active{R}\n"
                    f"{_rule('-', 72, BLUE)}"
                )

            if "PROFIT TARGET MONITOR STOPPED" in msg:
                return f"\n  {RED}* Monitor stopped{R}"

            if "REGISTERING PROFIT TARGET ORDER" in msg:
                oid = msg.split("ORDER")[-1].strip()
                return (
                    f"\n{_rule('-', 72, TEAL)}\n"
                    f"  {TEAL}REGISTERED ORDER {oid}{R}  {G1}Now monitoring{R}"
                )

            if "Starting trading cycle" in msg:
                return (
                    f"\n{_rule('-', 72, G1)}\n"
                    f"  {BOLD}{G2}TRADING CYCLE{R}\n"
                    f"{_rule('-', 72, G1)}"
                )


            if msg.startswith("♻️  RESCAN"):
                n = msg.split("#")[-1].strip()
                return (
                    f"\n{_rule('-', 72, G1)}\n"
                    f"  {BOLD}{G2}{n}{R}\n"
                    f"{_rule('-', 72, G1)}"
                )

            
            if msg.startswith("Executing BUY"):
                return (
                    f"\n{_rule('-', 72, YELLOW)}\n"
                    f"  {BOLD}{YELLOW}{msg.strip()}{R}\n"
                    f"{_rule('-', 72, YELLOW)}"
                )


            # ── KEY / VALUE LINES ─────────────────────────────────────────

            if "Current SPX price:" in msg:
                price = msg.split(":")[-1].strip()
                return _kv("SPX", f"${price}", key_color=G2, val_color=BOLD + CYAN)

            if "Target expiration:" in msg:
                raw = msg.split(":")[-1].strip()          # e.g. "20260313 (7 DTE)"
                parts = raw.split()
                date_part = parts[0]                      # "20260313"
                rest = " ".join(parts[1:])                # "(7 DTE)"
                if len(date_part) == 8 and date_part.isdigit():
                    date_part = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:]}"
                formatted = f"{date_part} {rest}".strip()
                return _kv("Expiry", formatted)

            if "Leg1 (SHORT):" in msg:
                return _kv("Upper strike (short 1x)", msg.split(":")[-1].strip())

            if "Leg2 (BUY, lower):" in msg:
                return _kv("Lower strike (long 1x)", msg.split(":")[-1].strip())

            if "Leg3 (BUY, upper):" in msg:
                return _kv("Upper wing (long 1x)", msg.split(":")[-1].strip())

            if "Leg1 bid/ask (SELL 2" in msg:
                return _kv("Upper bid / ask", msg.split(":")[-1].strip())

            if "Leg2 bid/ask (BUY  1" in msg:
                return _kv("Lower bid / ask", msg.split(":")[-1].strip())

            if "Leg3 bid/ask (BUY" in msg:
                return _kv("Upper wing bid / ask", msg.split(":")[-1].strip())

            if "Natural credit (worst):" in msg:
                return _kv("Natural credit", msg.split(":")[-1].strip(), val_color=ORANGE)

            if "Mid credit (fair value):" in msg:
                return _kv("Mid credit", msg.split(":")[-1].strip(), val_color=BOLD + CYAN)

            if "Credit within range:" in msg:
                val = msg.split(":")[-1].strip()
                return f"  {GREEN}>{R} {G1}Credit valid  {CYAN}{val}{R}"

            if "All strikes available" in msg:
                return f"  {GREEN}>{R} {G1}All strikes available in chain{R}"

            if "Position sizing:" in msg:
                return (
                    f"\n{_kv('Position sizing', msg.split(':', 1)[-1].strip(), val_color=G2)}"
                )

            # ── SWEEP BARS ────────────────────────────────────────────────

            if ("Placing order @" in msg or "Modifying to" in msg) and "[" in msg:
                try:
                    bracket = msg.split("[")[1].split("]")[0]
                    attempt, total = (int(x) for x in bracket.split("/"))
                    price = float(msg.split("$")[-1])
                    return _bar(attempt, total, price, filled=False)
                except Exception:
                    return f"  {YELLOW}>{R} {G2}{msg.strip()}{R}"

            if "Fill credit:" in msg:
                try:
                    parts = msg.split(",")
                    price = parts[0].split("$")[-1].strip()
                    qty   = parts[1].strip().split()[-1]
                    return _kv("Fill credit",
                                f"${price}  x  {qty} contracts",
                                val_color=BOLD + GREEN)
                except Exception:
                    return f"  {GREEN}>{R} {G2}{msg.strip()}{R}"

            if "Filled at:" in msg:
                try:
                    price   = msg.split("$")[1].split(" ")[0]
                    attempt = int(msg.split("attempt")[1].split("/")[0].strip())
                    total   = int(msg.split("/")[1].split(")")[0].strip())
                    return _bar(attempt, total, float(price), filled=True)
                except Exception:
                    return f"  {GREEN}>{R} {G2}{msg.strip()}{R}"

            # ── POST-FILL ─────────────────────────────────────────────────

            if "Trade logged:" in msg:
                body = msg.split(":", 1)[-1].strip()
                return f"  {GREEN}>{R} {G2}Trade logged  {CYAN}{body}{R}"

            if "Action: SELL" in msg:
                return _kv("Sell order", msg.split("Action:")[-1].strip(), val_color=TEAL)

            if "Expected profit:" in msg:
                return _kv("Expected profit", msg.split(":")[-1].strip(), val_color=GREEN)

            if "Registered - now monitoring" in msg:
                n = msg.split("monitoring")[-1].strip().split()[0]
                return f"  {TEAL}+{R} {G1}Monitoring  {CYAN}{n} order(s){R}"

            # ── MONITOR PARAMS ────────────────────────────────────────────

            if "Active orders:" in msg:
                return _kv("Active orders", msg.split(":")[-1].strip(), val_color=BLUE)

            if "Already notified:" in msg:
                return _kv("Already notified", msg.split(":")[-1].strip())

            if "Telegram:" in msg and ("ENABLED" in msg or "DISABLED" in msg):
                state = "ENABLED" if "ENABLED" in msg else "DISABLED"
                return _kv("Telegram", state,
                            val_color=GREEN if state == "ENABLED" else RED)

            if "Checking for fills every" in msg:
                return _kv("Check interval", msg.split("every")[-1].strip())

            if "Telegram notification sent" in msg:
                return f"  {TEAL}~{R} {G1}Telegram notification sent{R}"

            if "monitoring thread started" in msg.lower():
                return f"  {BLUE}*{R} {G1}Position monitoring thread started{R}"

            if "Monitoring thread started" in msg:
                # "✅ Monitoring thread started" from ProfitTargetMonitor.start()
                # already caught above; this is the fallback — suppress duplicate
                return ""

            # ── MONITOR STATUS LINE ────────────────────────────────────────────────────────
            # Real format (from ProfitTargetMonitor):
            #   "#18     watching 1 orders  IB OK  11:22:54 ET"
            # Also handles the older  "[Check N] Status: ..."  format.
            # Only print every 360th check (≈ 60 minutes at 10 s interval).

            _is_check = msg.lstrip().startswith("[Check") and "Status: watching" in msg
            if _is_check:
                try:
                    check_n = int(msg.split("[Check")[1].split("]")[0].strip())
                    # Only show every 720th check (each 2 hours)
                    if check_n % 720 != 0:
                        return ""
        
                    watching  = msg.split("watching")[1].split("order")[0].strip()
                    watching_n = int(watching)
                    watch_col = BLUE if watching_n > 0 else G1
                    order_word = "order" if watching_n == 1 else "orders"
                    from datetime import datetime as _dt
                    ts = _dt.fromtimestamp(record.created).strftime("%H:%M ET")
                    orders_part = (
                        f"{watch_col}{watching_n} {order_word}{R}"
                        if watching_n > 0
                        else f"{G0}no open orders{R}"
                    )
                    return (
                        f"{_rule('.', 72, G0)}\n"
                        f"  {G0}{ts}{R}  Watching {orders_part}"
                    )
                except Exception:
                    return ""

            # ── FILL DETECTION BLOCK (from _handle_filled_order) ──────────

            if "ORDER" in msg and "DISAPPEARED FROM openTrades" in msg:
                return "\x00"

            if msg.strip() == "This means: ORDER FILLED":
                return (
                    f"\n{_rule('=', 72, GREEN)}\n"
                    f"  {BOLD}{BG_GREEN} PROFIT TARGET FILLED {R}  "
                    f"{BOLD}{GREEN}Exit confirmed{R}\n"
                    f"{_rule('=', 72, GREEN)}"
                )

            if msg.startswith("EXIT_SUMMARY|"):
                try:
                    parts = dict(p.split("=", 1) for p in msg.split("|")[1:])
                    strikes   = parts["strikes"]
                    expiry    = parts["expiry"]
                    entry     = float(parts["entry"])
                    exit_p    = float(parts["exit"])
                    qty       = int(parts["qty"])
                    profit    = float(parts["profit"])
                    comm      = float(parts["commission"])
                    # Format expiry YYYYMMDD -> YYYY-MM-DD
                    if len(expiry) == 8 and expiry.isdigit():
                        expiry = f"{expiry[:4]}-{expiry[4:6]}-{expiry[6:]}"
                    # Format profit with explicit +/- sign
                    per_contract = exit_p - entry
                    sign         = "+" if profit >= 0 else "-"
                    p_col        = GREEN if profit >= 0 else RED
                    profit_str   = (
                        f"{sign}${abs(per_contract):.2f} x {qty} Qty"
                        f" = {p_col}{sign}${abs(profit):.2f}{R}"
                    )
                    return (
                        f"  {GREEN}>{R} {G1}Trade logged  "
                        f"{CYAN}{strikes} @ ${exit_p:.2f} x {qty}{R}"
                        f"  {G1}| Commission: ${comm:.2f}{R}\n"
                        f"{_kv('Strikes', strikes, val_color=G2)}\n"
                        f"{_kv('Expiry',  expiry,          val_color=G2)}\n"
                        f"{_kv('Entry',   f'${entry:.2f}', val_color=CYAN)}\n"
                        f"{_kv('Exit',    f'${exit_p:.2f}',val_color=CYAN)}\n"
                        f"{_kv('Profit',  profit_str,      val_color=G2)}\n"
                        f"{_rule('=', 72, GREEN)}"
                    )
                except Exception as e:
                    return f"  {G2}{msg.strip()}{R}"

            if "Logging exit trade to CSV" in msg:
                return "\x00"

            if "Exit logged to" in msg:
                return "\x00"

            if "Sending Telegram notification" in msg:
                return "\x00"

            if "Order" in msg and "fully processed" in msg:
                return "\x00"

            if "Now monitoring" in msg and "order(s)" in msg and "+" not in msg:
                try:
                    n = int(msg.split("monitoring")[-1].strip().split()[0])
                    if n == 0:
                        return "\x00"   # nothing to monitor — suppress
                    return f"  {G1}Monitoring  {CYAN}{n} order(s){R}"
                except Exception as e:
                    return f"  {G1}{msg.strip()}{R}"

            # ── STRIKES / ENTRY (from register_order) ─────────────────────

            if "Strikes:" in msg and "/" in msg:
                return _kv("Strikes", msg.split(":", 1)[-1].strip(), val_color=G2)

            if "Entry:" in msg and "Qty:" in msg:
                val = msg.split("Entry:")[-1].strip()     # "$2.05, Qty: 3, Expiry: 20260313"
                if "Expiry:" in val:
                    pre, exp = val.split("Expiry:")
                    exp = exp.strip()
                    if len(exp) == 8 and exp.isdigit():
                        exp = f"{exp[:4]}-{exp[4:6]}-{exp[6:]}"
                    val = f"{pre.strip()} Expiry: {exp}"
                return _kv("Entry", val, val_color=G2)

            # ── MARKET WAIT / SLEEP ───────────────────────────────────────────────────────

            if "Starting trading cycle" in msg:
                # ONLY match the exact banner message, not other logs that mention it
                if msg.strip() == "Starting trading cycle":
                    return (
                        f"\n{_rule('-', 72, G1)}\n"
                        f"  {BOLD}{G2}TRADING CYCLE{G2} \n"
                        f"{_rule('-', 72, G1)}"
                    )

            if "Sleeping for" in msg and "hours" in msg:
                return (
                    f"\n{_rule('-', 72, G0)}\n"
                    f"  {G0}* Sleeping -- next cycle in 24 hours{R}\n"
                    f"{_rule('-', 72, G0)}"
                )

            if "Pre-market:" in msg and "minutes until open" in msg:
                try:
                    mins   = msg.split("Pre-market:")[1].split("minutes")[0].strip()
                    open_t = (msg.split(" at ")[1].strip()
                              if " at " in msg else "09:30 ET")
                    return (
                        f"\n{_rule('-', 72, G0)}\n"
                        f"  {G0}o Pre-market{R}  "
                        f"{G1}Opens {G2}{open_t}{R}  {G0}({mins} min){R}\n"
                        f"{_rule('-', 72, G0)}"
                    )
                except Exception:
                    return f"  {G0}{msg.strip()}{R}"

            if "Disconnecting to save resources" in msg:
                return f"  {G0}v Disconnecting -- will reconnect before open{R}"

            if "Sleeping for" in msg and "minutes (disconnected)" in msg:
                try:
                    mins = msg.split("for")[1].split("minutes")[0].strip()
                except Exception:
                    mins = "?"
                return f"  {G0}| Sleeping {mins} min (disconnected){R}"

            if ("Reconnecting" in msg and
                    ("before market" in msg or "5 minutes" in msg)):
                return f"\n  {TEAL}^ Reconnecting 5 min before market open...{R}"

            # Market status messages — ONLY if the message is EXACT
            if msg.strip().startswith("Market is closed - "):
                # Pre-market
                if "Pre-market" in msg:
                    try:
                        time_part = msg.split("(")[1].split(")")[0] if "(" in msg else ""
                        return f"  {G0}o Market closed (pre) {G1}{time_part}{R}"
                    except Exception:
                        return f"  {G0}o {msg.strip()}{R}"
                # After hours
                elif "After hours" in msg or "after-hours" in msg.lower():
                    return f"  {G0}o Market closed (after-hours){R}"
                # Weekend
                elif "Weekend" in msg:
                    return f"  {G0}o {msg.strip()}{R}"
                # Generic
                else:
                    return f"  {G0}o {msg.strip()}{R}"

            if "Market is open" in msg and ("(" in msg):
                # Match "Market is open (10:33 ET)"
                try:
                    time_part = msg.split("(")[1].split(")")[0] if "(" in msg else ""
                    return (
                        f"\n{_rule('-', 72, TEAL)}\n"
                        f"  {GREEN}* MARKET OPEN{R}  {G1}{time_part}{R}\n"
                        f"{_rule('-', 72, TEAL)}"
                    )
                except Exception:
                    return f"  {GREEN}* {msg.strip()}{R}"

            if "After market close" in msg:
                return f"  {G0}o After-hours -- waiting for next session{R}"

            if "Weekend detected" in msg:
                return f"  {G0}o {msg.strip()}{R}"

            # ── TWS RESTART WINDOW ────────────────────────────────────────────
            if "Entered TWS restart window" in msg:
                try:
                    window = msg.split("(")[1].split(")")[0]   # "23:45 - 00:25"
                    return (
                        f"\n{_rule('-', 72, ORANGE)}\n"
                        f"  {BOLD}{ORANGE}ENTERED TWS RESTART WINDOW ({window}){R}\n"
                        f"{_rule('-', 72, ORANGE)}"
                    )
                except Exception:
                    return f"  {ORANGE}{msg.strip()}{R}"

            if "Reconnected" in msg and "attempt" in msg and "after" in msg:
                return f"  {GREEN}✓  ✓{R} {GREEN}{msg.strip()}{R}"

            # ── READY / DONE ──────────────────────────────────────────────

            if "No trades today" in msg or "Ready to trade" in msg:
                return f"  {GREEN}>{R} {G1}No trades today -- ready{R}"

            if "Already traded today" in msg or "already traded" in msg.lower():
                return f"  {ORANGE}o{R} {G1}Already traded today -- skipping{R}"

            # ── WARNINGS / ERRORS ─────────────────────────────────────────

            if lvl == "WARNING":
                return f"  {ORANGE}!{R}  {ORANGE}{msg.strip()}{R}"

            if lvl == "ERROR":
                return f"  {RED}X{R}  {RED}{msg.strip()}{R}"

            # ── ENTRY TIME WAIT ──────────────────────────────────────────────────────────
            if "Waiting until entry time" in msg:
                try:
                    # Format: "Waiting until entry time 11:23:48 ET (50.8 minutes)"
                    time_part = msg.split("until entry time")[1].split("(")[0].strip()
                    minutes   = msg.split("(")[1].split("minutes")[0].strip() if "(" in msg else "?"
                    return f"  {G0}⏱ Waiting for entry time {CYAN}{time_part}{R}  {G0}({minutes}m){R}"
                except Exception:
                    return f"  {G0}{msg.strip()}{R}"

            # ── GENERIC FALLBACK ──────────────────────────────────────────
            clean = msg.strip()
            return f"  {G1}{clean}{R}" if clean else ""

    # ══════════════════════════════════════════════════════════════════════════
    # CONSOLE FILTER  — suppress verbose internal messages
    # ══════════════════════════════════════════════════════════════════════════
    class ConsoleFilter(logging.Filter):

        SKIP = [
            # IB / chain internals
            "Received ", "Chain: exchange", "chain: exchange",
            "Peer closed connection.",
            "Found SMART", "Selected chain", "Requesting option chains",
            "All contracts qualified", "Ticker data ready", "Market data received",
            "Creating Bull Put Spread combo", "Bull Put Spread combo created",
            # Strike calc debug
            "Leg1 parameters:", "Leg2 parameters:", "Leg3 parameters:",
            # Combo confirmation lines that leak after MARKET QUOTES
            "Leg1: ", "Leg2: ", "Leg3: ",
            # Order IDs / low-level
            "Order ID:", "orderId", "conId=",
            "Fill (BAG", "Fill (leg):", "Actual commission",
            # Persistence
            "Saved ", "Loaded ", "active profit target",
            "Stored metadata", "Removed metadata", "Metadata persisted",
            # Monitor internals
            "Discovering new", "Loaded known profit",
            "Found 0 Bull Put Spread", "Processing filled order",
            "Fetching fill prices", "Could not fetch",
            "Using ESTIMATED", "DISAPPEARED FROM",
            "reqCompletedOrders", "Error processing",
            # Config noise
            "Entry time check disabled", "Entry condition checks",
            "Setting last_trade_date", "grace period",
            # Reconnect noise
            "CREATING COMBO CONTRACT", "Combo created:",
            "Starting credit sweep",
            "No Trade object stored", "RECONNECTING",
            # Sweep internals already shown via bar
            "Wait per attempt", "Max attempts", "Expiration window",
            "Start price", "Max price ceiling", "Step:",
            "vs Mid price",
            # These two appear right before the sweep bar — redundant
            "Quantity:", "Mid price:",
            # Profit target fill detection (not an entry fill)
            "profit target FILLED", "Bull Put Spread profit target FILLED",
            # Monitor logs TWO "started" lines; suppress the second
            "✅ Monitoring thread started",
            # Fill handler internals shown via formatter rules
            "Logging exit trade to CSV", "Sending Telegram notification",
            "✅ Telegram notification sent",   # shown once via "~ Telegram notification sent"
            # Exit fill detail lines — replaced by EXIT_SUMMARY| block in formatter
            "Fill prices:", "Found ", "fill records in Trade object",
            "Processing filled order", "Fetching fill prices",
            "Exit combo:", "Exit logged to",
            "Order ", "fully processed",
            "Error 1100",
            "Error 1102",
        ]

        def filter(self, record):
            msg = record.getMessage()
            if not msg.strip():
                return False
            if all(c == "=" for c in msg.strip()):
                return False
            for kw in self.SKIP:
                if kw in msg:
                    return False
            # Suppress check lines that didn't get throttled in formatter
            # (safety net — formatter returns "" for non-360th checks,
            #  but logging still calls emit; this stops them before that)
            stripped = msg.lstrip()
            if (stripped.startswith("#") and "watching" in msg
                    and ("IB OK" in msg or "IB !!" in msg)):
                try:
                    check_n = int(stripped.lstrip("#").split()[0])
                    if check_n % 360 != 0:
                        return False
                except Exception:
                    pass
            return True

    # ── File handler ──────────────────────────────────────────────────────────
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))

    # ── Console handler ───────────────────────────────────────────────────────
    class _SilentStreamHandler(logging.StreamHandler):
        """Skip records whose formatted output is empty or the sentinel."""
        def emit(self, record):
            try:
                msg = self.format(record)
                if not msg or msg == "\x00":
                    return
                self.stream.write(msg + self.terminator)
                self.flush()
            except Exception:
                self.handleError(record)

    console_handler = _SilentStreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(RichConsoleFormatter())
    console_handler.addFilter(ConsoleFilter())

    # ── Logger ────────────────────────────────────────────────────────────────
    self.logger = logging.getLogger("Bot")
    self.logger.setLevel(logging.DEBUG)
    self.logger.handlers = []
    self.logger.addHandler(file_handler)
    self.logger.addHandler(console_handler)