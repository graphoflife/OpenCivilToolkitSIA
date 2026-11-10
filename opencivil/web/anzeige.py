"""
opencivil/web/anzeige.py -- Zahlen und Zeilen, wie die Oberflaeche sie zeigt.

VERANTWORTUNG:
Was der Kern der Oberflaeche gibt, steht in den Einheiten der Anzeige --
kN, kNm, mm, N/mm², Promille. Umgerechnet wird hier, mit den Einheiten des
Kerns (:mod:`opencivil.core.einheiten`): :func:`zahl` von SI in eine
Einheit, :func:`si` zurueck fuer das, was die Oberflaeche schickt. Eine
Groesse einer Linie traegt dazu Zeichen und Stellen
(:class:`Anzeigegroesse`).

Dazu die Zellen einer Zeile -- Text oder Formel, wie in den Tabellen der
Herleitung (:func:`zelle_dict`). Aus ihnen bestehen die Legenden der
Situationsbilder (:func:`zeile`, :func:`zahlformel`): die Zahlen, ihr
Vergleich und das Urteil kommen aus dem Kern, die Oberflaeche setzt sie nur.

BIS 2026-11-10 standen die Einheiten der Anzeige auf drei Wegen da: als
Groesse nur fuer die Linien der Diagramme, sonst als nackte Faktoren -- und
``kN = 1e-3`` in den Bildern hiess das Gegenteil von ``kN = 1e3`` beim
Bauen. Die Legenden baute das JS selbst, samt Urteil und Normstelle.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence

from opencivil.core.einheiten import Einheit, Groesse
from opencivil.core.latex import Mathe, Zelle, vergleichszeichen


def zahl(si_wert: Optional[float], einheit: Einheit) -> Optional[float]:
    """Ein Wert in SI, in der Einheit der Anzeige -- ``None`` bleibt ``None``."""
    return None if si_wert is None else si_wert / einheit.faktor


def si(angezeigt: float, einheit: Einheit) -> float:
    """Was die Oberflaeche in ``einheit`` schickt, in SI."""
    return angezeigt * einheit.faktor


def punkte(liste: Iterable[Sequence[float]], einheit: Einheit) -> List[List[float]]:
    """Punkte in SI als Listen ``[x, y]`` in der Einheit der Anzeige."""
    return [[zahl(p[0], einheit), zahl(p[1], einheit)] for p in liste]


@dataclass(frozen=True)
class Anzeigegroesse:
    """Eine Groesse einer Linie, wie sie in den Zeichendaten steht: Zeichen und Einheit."""

    zeichen: str
    einheit: Einheit
    latex: str = ""
    stellen: int = 1
    am_bezugsort: bool = False
    """Ob sie an einem Ort des Querschnitts gilt -- die Mitteldehnung, nicht die Kruemmung."""

    def zahl(self, si_wert: Optional[float]) -> Optional[float]:
        """Ein Wert in SI, in der Einheit dieser Groesse."""
        return zahl(si_wert, self.einheit)

    def als_dict(self) -> dict:
        return {"zeichen": self.zeichen, "latex": self.latex or self.zeichen,
                "einheit": self.einheit.beschriftung, "stellen": self.stellen,
                "am_bezugsort": self.am_bezugsort}


def zelle_dict(zelle: Zelle) -> dict:
    """
    Eine Zelle fuer die Oberflaeche: ``{"text": ...}`` oder ``{"mathe": ...}``.
    Die Oberflaeche setzt nur Formeln mit KaTeX -- Text aus LaTeX
    zurueckzulesen, wie sie es frueher musste, entfaellt.
    """
    if isinstance(zelle, Mathe):
        return {"mathe": zelle.latex}
    return {"text": zelle}


def zeile(*teile: Zelle) -> List[dict]:
    """Eine Zeile einer Legende aus Text und Formeln, der Reihe nach."""
    return [zelle_dict(t) for t in teile]


def masszahl(si_wert: float, einheit: Einheit, stellen: int) -> str:
    """``Zahl Einheit`` in LaTeX, gerundet wie in der Herleitung."""
    return Groesse.aus_si(si_wert, einheit).als_latex(stellen)


def zahlformel(zeichen: str, si_wert: float, einheit: Einheit, stellen: int) -> Mathe:
    """``Zeichen = Zahl Einheit`` als Formel -- eine Zahl in einer Zeile."""
    return Mathe(f"{zeichen} = {masszahl(si_wert, einheit, stellen)}")


def urteil(links: str, soll: str, rechts: str, erfuellt: bool, grad: str) -> List[Zelle]:
    """
    Ein Vergleich mit seinem Urteil, als Teile einer Zeile:
    ``s = 12 mm ≤ s_zul = 25 mm – erfüllt, α = 2.08``. ``links`` und
    ``rechts`` in LaTeX, ``soll`` das Zeichen, das gelten muss -- geht er
    nicht auf, steht sein Gegenteil da; ``grad`` der Erfuellungsgrad in LaTeX.
    """
    return [Mathe(f"{links} {vergleichszeichen(soll, erfuellt)} {rechts}"),
            f" – {'erfüllt' if erfuellt else 'nicht erfüllt'}, ", Mathe(rf"\alpha = {grad}")]
