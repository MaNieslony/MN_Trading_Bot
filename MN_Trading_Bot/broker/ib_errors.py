# broker/ib_errors.py

def build_error_callback(logger):
    error_1100_logged = False
    error_1102_logged = False

    # IB-Informationsmeldungen ohne Handlungsbedarf - werden komplett
    # ignoriert (weder Datei- noch Konsolen-Log). 10349 ist die seit der
    # neuen TWS-Version zusätzlich gesendete Hinweismeldung, dass die
    # TIF gemäß Order-Voreinstellungen auf GTC gesetzt wurde.
    IGNORED_CODES = (104, 201, 202, 10349)

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

        if errorCode in IGNORED_CODES:
            return

        logger.warning(f"IB Error {errorCode}: {errorString}")

    return error_callback