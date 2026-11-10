"""
opencivil/web/grundbruchdaten.py -- was die Oberflaeche von einem Grundbruch zeichnet.

VERANTWORTUNG:
Je Fundament die Zahlen der Situationszeichnung, in den Einheiten der
Anzeige -- m, kN: wie tief und wie weit der Gleitkoerper reicht, sein
Umriss und je Kombination die Kraefte und die beiden Erfuellungsgrade. Dazu
die Legende unter dem Bild (:mod:`opencivil.web.anzeige`): je Kombination
ihre Zeile mit der Neigung der Last, darunter das Grundwasser, wie die
Rechnung es eingeordnet hat, der Gleitkoerper und die Laenge. Die
Abmessungen selbst liest die Oberflaeche aus dem Eintrag; was der Kern
daraus macht, kommt von hier.

Gerechnet wird hier nichts, was nicht der Kern schon weiss: der Umriss kommt
aus :func:`opencivil.geotechnik.grundbruch.gleitkoerper`, mit denselben
Werten b und phi_eff wie die Formeln fuer L_Gl und H_Gl.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from opencivil.core.einheiten import GRAD, KN, M
from opencivil.core.latex import Mathe
from opencivil.core.rechenwerk import Loesung
from opencivil.geotechnik import grundbruch
from opencivil.projekt import Aufbau
from opencivil.web.anzeige import zahl, zahlformel, zeile


def situation(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]:
    """
    Was die Zeichnung eines Fundaments braucht. Ohne eingeschaltete
    Kombination gibt es keinen Nachweis und keinen Befund -- dann zeichnet
    sie nur das Fundament, ohne Gleitkörper und ohne Kräfte.
    """
    fundament = aufbau.grundbrueche[kennung]
    nachweis = aufbau.feld("grundbruch").get(kennung)
    gleiten = aufbau.feld("gleiten").get(kennung)
    befund: Optional[grundbruch.Grundbruchbefund] = (
        loesung.befunde.get(nachweis.id) if nachweis is not None else None)
    drainiert = befund is not None and not befund.undrainiert

    def grad_gleiten(name: str) -> Optional[float]:
        wert = (loesung.werte.get(gleiten.d_ausnutzung[name].id)
                if gleiten is not None and name in gleiten.d_ausnutzung else None)
        return wert.groesse.si if wert is not None else None

    faelle = [{
        "name": r.kombination.name,
        "N_Ed": zahl(r.kombination.N_Ed.si, KN),
        "T_Ed": zahl(r.kombination.T_Ed.si, KN),
        "grad_grundbruch": r.erfuellungsgrad,
        "grad_gleiten": grad_gleiten(r.kombination.name),
        "legende": zeile(
            f"{r.kombination.name}: ", zahlformel("N_{Ed}", r.kombination.N_Ed.si, KN, 1), " · ",
            zahlformel("T_{Ed}", r.kombination.T_Ed.si, KN, 1), " · ",
            zahlformel(r"\delta_R", r.delta_R, GRAD, 1),
            " – die Kräfte im Verhältnis zueinander, nicht im Massstab der Längen"),
    } for r in (befund.ergebnisse if befund is not None else [])]
    # Die Kombination mit dem kleinsten Erfuellungsgrad, Grundbruch oder Gleiten.
    massgebend = min(faelle, default=None, key=lambda f: min(
        f["grad_grundbruch"], math.inf if f["grad_gleiten"] is None else f["grad_gleiten"]))
    # Der Umriss mit denselben b und phi_eff wie L_Gl und H_Gl im Befund.
    umriss = (grundbruch.gleitkoerper(loesung.werte[fundament.id_von("b")].groesse.si,
                                      loesung.werte[fundament.id_von("phi_eff")].groesse.si)
              if drainiert else [])
    return {
        "L_gl": befund.L_gl if befund is not None else None,
        "H_gl": befund.H_gl if befund is not None else None,
        "umriss": [list(punkt) for punkt in umriss],
        "faelle": faelle,
        "massgebend": massgebend["name"] if massgebend is not None else None,
        "legende": _legende(fundament, befund, gezeichnet=bool(umriss)),
    }


def _legende(fundament: grundbruch.Fundament, befund: Optional[grundbruch.Grundbruchbefund],
             *, gezeichnet: bool) -> List[list]:
    """
    Die Zeilen unter dem Bild, die fuer jede Kombination gelten: das
    Grundwasser, der Gleitkoerper -- gezeichnet ist er ohne die Neigungen --
    und die Laenge senkrecht zum Bild. Die Zeile der gezeigten Kombination
    steht bei ihr.
    """
    zeilen = []
    if befund is not None and befund.grundwasser:
        zeilen.append(zeile(befund.grundwasser))
    if gezeichnet:
        geneigt = fundament.alpha.si != 0.0 or fundament.beta.si != 0.0
        zeilen.append(zeile(
            "Gleitkörper nach Prandtl: ", zahlformel("H_{Gl}", befund.H_gl, M, 2),
            " unter der Sohle, ", zahlformel("L_{Gl}", befund.L_gl, M, 2), " neben ihr",
            *((" – gezeichnet für ", Mathe(r"\alpha = \beta = 0")) if geneigt else ())))
    elif befund is not None and befund.undrainiert:
        zeilen.append(zeile("Undrainiert, ", Mathe(r"\varphi = 0"),
                            ": kein Gleitkörper gezeichnet."))
    zeilen.append(zeile("Länge des Fundaments ", zahlformel("L", fundament.L.si, M, 2),
                        ", senkrecht zum Bild."))
    return zeilen
