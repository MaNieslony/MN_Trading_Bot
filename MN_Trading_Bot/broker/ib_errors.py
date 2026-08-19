# broker/ib_errors.py

def build_error_callback(logger):
    error_1100_logged = False
    error_1102_logged = False

    def error_callback(reqId, errorCode, errorString, contract):
        nonlocal error_1100_logged, error_1102_logged

        if errorCode == 1100:
            if not error_1100_logged:
                logger.warning("IB connection lost (1100)")
                error_1100_logged = True
            return

        if errorCode == 1102:
            if not error_1102_logged:
                logger.info("IB connection restored (1102)")
                error_1102_logged = True
                error_1100_logged = False
            return

        if errorCode in (104, 201, 202):
            return

        logger.warning(f"IB Error {errorCode}: {errorString}")

    return error_callback