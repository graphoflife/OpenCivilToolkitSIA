"""
opencivil/web/pfahldaten.py -- was die Oberflaeche von einem Pfahl zeichnet.

VERANTWORTUNG:
Je Pfahl die Zahlen der Situationszeichnung, in den Einheiten der Anzeige:
die Mantelreibung je Stück und der Spitzendruck, wie der äussere Widerstand
sie gerechnet hat. Dazu die Legende unter dem Bild
(:mod:`opencivil.web.anzeige`): Mantel und Fuss, die Bemessungswerte beider
Nachweise auf Druck und auf Zug und der Fall, der entscheidet. Masse,
Schichten und Grundwasser liest die Oberflaeche aus dem Eintrag.

Gerechnet wird hier nichts: alles steht in den Befunden der Nachweise.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from opencivil.core.einheiten import KN, KPA
from opencivil.core.latex import Mathe
from opencivil.core.rechenwerk import Loesung
from opencivil.pfahl.aussen import Aussenbefund
from opencivil.pfahl.innen import Innenbefund
from opencivil.projekt import Aufbau
from opencivil.web.anzeige import zahl, zahlformel, zeile


def situation(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]:
    """
    Was die Zeichnung eines Pfahls braucht. Ohne Kombination gibt es keinen
    Nachweis und keinen Befund -- dann zeichnet sie nur den Pfahl im Boden.
    """
    nachweise = [aufbau.feld(f).get(kennung) for f in ("pfahl_aussen", "pfahl_innen")]
    if any(n is None for n in nachweise):
        return {"stuecke": [], "q_b": None,
                "legende": [zeile("Ohne Kombination kein Nachweis.")]}
    aussen: Optional[Aussenbefund] = loesung.befunde.get(nachweise[0].id)
    innen: Optional[Innenbefund] = loesung.befunde.get(nachweise[1].id)
    if aussen is None or innen is None:
        return {"stuecke": [], "q_b": None, "legende": [zeile("Nicht gerechnet.")]}
    raeume = {n.id for n in nachweise}
    urteile = [u for u in loesung.urteile if u.raum in raeume and not u.still]
    return {
        "stuecke": [{"z_o": s.stueck.z_o, "z_u": s.stueck.z_u, "q_s": zahl(s.q_s, KPA)}
                    for s in aussen.stuecke],
        "q_b": zahl(aussen.q_b, KPA),
        "legende": _legende(aussen, innen, urteile),
    }


def _legende(aussen: Aussenbefund, innen: Innenbefund, urteile: List[Any]) -> List[list]:
    """Mantel und Fuss, die Bemessungswerte, der entscheidende Fall."""
    kn = lambda zeichen, si: zahlformel(zeichen, si, KN, 0)
    if aussen.aus_versuch:
        herkunft = zeile("Aus dem Versuch ", kn("R_{a,k}", aussen.R_ak), " auf Druck und ",
                         kn("R_{a,k,Z}", aussen.R_ak_zug), " auf Zug.")
    else:
        herkunft = zeile("Mantel ", kn("R_{s,k}", aussen.R_s), " und Fuss ",
                         kn("R_{b,k}", aussen.R_b), ": ", kn("R_{a,k}", aussen.R_ak),
                         ". Rechts der Achse die Mantelreibung ", Mathe("q_{s,k}"),
                         " je Stück, unten der Spitzendruck ", Mathe("q_{b,k}"), ".")
    zeilen = [
        herkunft,
        zeile("Auf Druck ", kn("R_{a,d}", aussen.R_ad), " und ", kn("R_{i,d}", innen.R_id),
              ", auf Zug ", kn("R_{a,d,Z}", aussen.R_ad_zug), " und ",
              kn("R_{i,d,Z}", innen.R_id_zug), "."),
    ]
    if urteile:
        u = min(urteile, key=lambda x: x.erfuellungsgrad.si)
        zeilen.append(zeile(f"Massgebend: {u.langname}, {u.fall} – "
                            f"{'erfüllt' if u.erfuellt else 'nicht erfüllt'}, ",
                            Mathe(rf"\alpha = {u.gradtext(latex=True)}"), "."))
    return zeilen
