# tradetype/rut_iron_condor.py
from typing import Optional, Tuple


class RutIronCondorTradeType:
    """
    RUT Iron Condor (nur Einstieg automatisiert, Exit manuell).

    Die eigentliche Strike-Auswahl passiert in market/rut_ic_steering.py
    (delta-symmetrisch, IV-Rank-gesteuertes DTE/Delta, Briefkurs-Regel für
    die Long-Strikes). Diese Klasse liefert nur Metadaten fürs Logging;
    select_strikes() wird bewusst nicht benutzt (siehe cycle_steps.select_legs
    Sonderfall) – analog zu NDX-50BPS, das BullPutTradeType umgeht.
    """
    display_name = "RUT Iron Condor"

    def __init__(self, logger=None):
        self.logger = logger

    def select_strikes(self, **_) -> Optional[Tuple]:
        if self.logger:
            self.logger.error(
                "RutIronCondorTradeType.select_strikes() sollte nie direkt aufgerufen werden – "
                "IRON_CONDOR läuft über market/rut_ic_steering.py in cycle_steps.select_legs()"
            )
        return None