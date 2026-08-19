# runtime/validation.py

def validate_startup(
    *,
    ib_host,
    ib_port,
    allocation,
    execution_time,
    market_open_time,
    market_close_time,
    logger
):
    errors = []
    warnings = []

    if not ib_host:
        errors.append("IB_HOST missing")

    if ib_port not in (7496, 7497):
        errors.append(f"Invalid IB_PORT: {ib_port}")

    if allocation <= 0:
        errors.append("ALLOCATION must be > 0")

    if execution_time < market_open_time or execution_time > market_close_time:
        warnings.append("Execution time outside market hours")

    if errors:
        for e in errors:
            logger.error(f"❌ {e}")
        return False

    for w in warnings:
        logger.warning(f"⚠️ {w}")

    logger.debug("✅ Startup validation passed")
    return True