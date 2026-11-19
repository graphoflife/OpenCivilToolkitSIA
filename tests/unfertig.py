"""
Was ein Bauteil oder Material aufhält -- für Tests, die einen Wert prüfen,
den der Kern abweist.

Seit 2026-11-19 hält ein solcher Wert nur sein Bauteil oder Material an,
nicht mehr das ganze Projekt (Benutzer: «der Rest rechnet weiter»): es wird
nicht gebaut, und :attr:`Aufbau.unfertige` sagt warum. Vorher hiess der Test
``assertRaisesRegex(ProjektFehler, …)`` um ``aufbauen()``.
"""


def grund(projekt, kennung: str) -> str:
    """
    Warum ``kennung`` nicht rechnet. Rechnet es doch, scheitert der Test:
    dann prüft er nicht mehr, was er sagt.
    """
    aufbau = projekt.aufbauen()
    unfertig = aufbau.unfertige.get(kennung)
    if unfertig is None:
        raise AssertionError(f"'{kennung}' rechnet -- gebaut sind {sorted(aufbau.teile)}, "
                             f"Warnungen: {aufbau.warnungen}")
    return unfertig.grund


def meldung(projekt) -> str:
    """
    Was früher die Meldung des Fehlers war: die des ersten Materials oder
    Bauteils, das nicht rechnet -- «Platte 'Decke': k_c muss grösser als null
    sein, angegeben ist 0.» Geprüft wird in derselben Reihenfolge wie früher,
    Materialien zuerst. Rechnet alles, scheitert der Test.
    """
    aufbau = projekt.aufbauen()
    for unfertig in aufbau.unfertige.values():
        return unfertig.meldung
    raise AssertionError(f"Alles rechnet -- gebaut sind {sorted(aufbau.teile)}")
