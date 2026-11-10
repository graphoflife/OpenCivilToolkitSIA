"""
opencivil/web/setzungsdaten.py -- was die Oberflaeche von einer Setzung zeichnet.

VERANTWORTUNG:
Je Fundament die Zahlen der Situationszeichnung, in den Einheiten der
Anzeige -- m und mm: wo gerechnet wurde, wie die Zusatzspannung mit der
Tiefe abnimmt und was jede Schicht zur Setzung beitraegt. Dazu die Legende
unter dem Bild (:mod:`opencivil.web.anzeige`): der Punkt, die Setzung gegen
die zulaessige mit dem Urteil, was die Linie zeigt, und die Laenge. Die
Abmessungen selbst liest die Oberflaeche aus dem Eintrag; was der Kern
daraus macht, kommt von hier.

Gerechnet wird hier nichts, was nicht der Kern schon weiss: die Linie des
Einflussfaktors kommt aus :func:`opencivil.geotechnik.setzung.einflusslinie`,
mit denselben L, B und demselben Punkt wie die Tabelle der Teilschichten.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from opencivil.core.einheiten import EINHEITSLOS, MM, M, Groesse
from opencivil.core.latex import Mathe
from opencivil.core.rechenwerk import Loesung
from opencivil.geotechnik import setzung
from opencivil.projekt import Aufbau
from opencivil.web.anzeige import masszahl, urteil, zahl, zahlformel, zeile


def situation(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]:
    """
    Was die Zeichnung eines Fundaments braucht. Ohne Schicht gibt es keinen
    Nachweis und keinen Befund -- dann zeichnet sie nur das Fundament.
    """
    fundament = aufbau.setzungen[kennung]
    nachweis = aufbau.feld("setzung").get(kennung)
    befund: Optional[setzung.Setzungsbefund] = (
        loesung.befunde.get(nachweis.id) if nachweis is not None else None)
    laenge = zeile("Länge des Fundaments ", zahlformel("L", fundament.L.si, M, 2),
                   ", senkrecht zum Schnitt.")
    if befund is None:
        return {"punkt": fundament.steifigkeit.punkt, "lage": None, "linie": [],
                "schichten": [], "legende": [zeile("Ohne Schicht keine Setzung."), laenge]}
    werte = loesung.werte
    L, B = (werte[fundament.id_von(n)].groesse.si for n in ("L", "B"))
    x, y = befund.punkt
    tiefe = befund.schichten[-1].z_u
    gefunden = next(u for u in loesung.urteile if u.raum == nachweis.id)
    return {
        "punkt": fundament.steifigkeit.punkt,
        "lage": [x, y],
        "linie": [list(p) for p in setzung.einflusslinie(L, B, x, y, tiefe)],
        "J_fuss": befund.J_fuss,
        "schichten": [{"name": s.name, "z_o": s.z_o, "z_u": s.z_u, "s_W": zahl(s.s_W, MM),
                       "s_E": zahl(s.s_E, MM), "s": zahl(s.s, MM)} for s in befund.schichten],
        "legende": [*_legende(fundament, befund, werte[fundament.id_von("s_zul")].groesse.si,
                              gefunden), laenge],
    }


def _legende(fundament: setzung.Setzungsfundament, befund: setzung.Setzungsbefund,
             s_zul: float, gefunden) -> List[list]:
    """Wo gerechnet wurde, die Setzung gegen die zulaessige, was die Linie zeigt."""
    if fundament.steifigkeit is setzung.Steifigkeit.SCHLAFF:
        punkt = zeile("Schlaff: gerechnet unter der Mitte – dort ist die Setzung am "
                      "grössten (Kap. 8.10).")
    else:
        x, y = befund.punkt
        punkt = zeile("Starr: gerechnet im Punkt K, ", Mathe(masszahl(x, M, 2)), " längs ",
                      Mathe("L"), " und ", Mathe(masszahl(y, M, 2)), " längs ", Mathe("B"),
                      " von einer Ecke – seine Setzung ist die mittlere des Fundaments "
                      "(Bild 8.15).")
    teile = " + ".join(Groesse.aus_si(t, MM).formatiert(1) for t in (befund.s_W, befund.s_E))
    return [
        punkt,
        zeile(*urteil(rf"s = s_W + s_E = {teile} = {masszahl(befund.s, MM, 1)}", r"\le",
                      f"s_{{zul}} = {masszahl(s_zul, MM, 1)}", gefunden.erfuellt,
                      gefunden.gradtext(latex=True))),
        zeile("Die Linie zeigt ", Mathe("J"), " über die Tiefe: ",
              Mathe(r"\Delta\sigma'_z = J \cdot q"), ". Am Fuss der untersten Schicht noch ",
              zahlformel("J", befund.J_fuss, EINHEITSLOS, 3),
              "; darunter gilt der Baugrund als unzusammendrückbar."),
    ]
