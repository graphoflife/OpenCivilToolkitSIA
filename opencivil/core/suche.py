"""
opencivil/core/suche.py -- wo eine steigende Funktion null wird.

VERANTWORTUNG:
Die Verfahren, mit denen das Werkzeug eine Nullstelle sucht, an einer
Stelle: :class:`Halbieren`, :class:`Illinois` mit :func:`illinois` und
:func:`eingrenzen`. Gesucht wird ueberall dasselbe -- eine Stelle zwischen
zwei Grenzen, an der eine Funktion das Vorzeichen wechselt: die Dehnung, bei
der die Normalkraft stimmt, die Kruemmung zum Moment, der Bruchzustand bei
einer Normalkraft, die Neigung der Nulllinie. Bis 2026-10-17 stand Illinois
zweimal da, im Loeser des Querschnitts und in der Interaktion, und das
Eingrenzen mit wachsenden Schritten zweimal im Loeser.

HALBIEREN ODER ILLINOIS:
Halbieren ist sicher: es findet die Stelle auch, wo die Funktion springt,
und braucht bis auf die Schranke rund vierzig Schritte. Illinois -- eine
Sekante, die abwechselnd von beiden Seiten herankommt -- braucht auf glatten
Stuecken ein Viertel davon: zwischen zwei Knicken der Werkstoffgesetze ist
die Kraft eine Gerade, und dort trifft die Sekante. Springt die Funktion,
findet Illinois eine der Stellen um den Sprung, und welche, haengt am Weg
(:mod:`opencivil.nachweis.querschnittsloeser`).

Wer eine Suche braucht, bekommt sie als Gegenstand (:class:`Suche`) und
fragt sie zweierlei: ob sie bei der zuletzt gefundenen Stelle anfaengt
(:attr:`Suche.vom_letzten`) und ob sie auch dort taugt, wo die Funktion
springt (:attr:`Suche.auch_bei_sprung`). Bis 2026-10-17 waren es
Unterklassen des Loesers, die sich mit einem Schalter an vier Stellen
wieder abschalteten.

EINHEITEN:
Keine -- hier gibt es nur Zahlen.
"""

from __future__ import annotations

import math
from typing import Callable, Optional, Protocol, Tuple, TypeVar

#: Hoechstzahl der Schritte einer Suche. Erreicht wird sie nicht: abgebrochen
#: wird an der Schranke. Die Zahl steht nur da, damit keine Schleife ewig
#: laeuft.
SCHRITTE = 80

#: Was eine Funktion an einer Stelle hat -- ``None``, wo sie keinen Wert hat.
Wert = Optional[float]

#: Was :func:`illinois` neben dem Wert mitgibt und an der besten Stelle zurueckgibt.
B = TypeVar("B")


class Suche(Protocol):
    """Was eine Suche kann und von sich sagt -- :class:`Halbieren` oder :class:`Illinois`."""

    vom_letzten: bool
    """
    Ob sie bei der zuletzt gefundenen Stelle anfaengt und von dort eingrenzt
    (:func:`eingrenzen`) -- das lohnt nur, wo sie nahe am Ziel schnell trifft.
    """

    auch_bei_sprung: bool
    """
    Ob sie auch dort taugt, wo die Funktion springt -- wo es also mehrere
    Stellen gibt und welche gefunden wird, am Weg haengt.
    """

    wie: str
    """Wie sie die Stelle findet, in Worten -- fuer die Mitschrift: «durch Halbieren»."""

    def finde(self, f: Callable[[float], Wert], unten: float, oben: float, schranke: float,
              f_unten: Wert = None, f_oben: Wert = None) -> Wert:
        """Wo ``f`` zwischen ``unten`` und ``oben`` null wird."""


class Halbieren:
    """
    Das Fenster halbieren, bis es schmal genug ist. Braucht von ueberall
    gleich viele Schritte und faengt darum von vorn an; sicher, auch wo die
    Funktion springt: die Stelle haengt nur am Fenster.
    """

    vom_letzten = False
    auch_bei_sprung = True
    wie = "durch Halbieren"

    def finde(self, f: Callable[[float], Wert], unten: float, oben: float, schranke: float,
              f_unten: Wert = None, f_oben: Wert = None) -> Wert:
        """
        Wo ``f`` zwischen ``unten`` und ``oben`` null wird -- ``f`` steigt,
        unten ist es negativ, oben nicht. Halbiert, bis das Fenster schmaler
        ist als ``schranke``; ``None``, wenn ``f`` unterwegs keinen Wert hat.
        ``f_unten`` und ``f_oben`` braucht das Halbieren nicht -- sie sind fuer
        eine Suche, die mit ihnen schneller ist (:class:`Illinois`).
        """
        for _ in range(SCHRITTE):
            if oben - unten <= schranke:
                break
            mitte = 0.5 * (unten + oben)
            wert = f(mitte)
            if wert is None:
                return None
            if wert < 0.0:
                unten = mitte
            else:
                oben = mitte
        return 0.5 * (unten + oben)


class Illinois:
    """
    Regula falsi mit der Illinois-Abwandlung: der naechste Punkt liegt, wo die
    Sekante durch die beiden Enden null wird, und bleibt ein Ende zweimal
    hintereinander stehen, wird sein Wert halbiert -- sonst kroeche die
    Sekante an einer gekruemmten Funktion nur von einer Seite heran. Bleibt
    eingegrenzt wie das Halbieren, konvergiert auf glatten Stuecken aber fast
    so schnell wie das Sekantenverfahren -- am schnellsten, wo es nahe der
    Stelle anfaengt: darum bei der zuletzt gefundenen.

    Springt die Funktion, findet es eine der Stellen um den Sprung, und
    welche, haengt am Weg -- von der zuletzt gefundenen Stelle aus also an
    der Reihenfolge der Fragen. Taugen soll es dort nur, wo das nicht zaehlt:
    ``auch_bei_sprung`` fuer eine Suche, die je Frage frisch anfaengt.

    Ohne ``vom_letzten`` sucht es jede Frage im ganzen Fenster: langsamer als
    von der letzten Stelle aus, aber die Antwort haengt allein an der Frage
    (:data:`ILLINOIS_VON_VORN`).
    """

    wie = ("mit dem Illinois-Verfahren, einer Sekante, die abwechselnd von beiden "
           "Seiten herankommt")

    def __init__(self, *, auch_bei_sprung: bool = False, vom_letzten: bool = True) -> None:
        self.auch_bei_sprung = auch_bei_sprung
        self.vom_letzten = vom_letzten

    def finde(self, f: Callable[[float], Wert], unten: float, oben: float, schranke: float,
              f_unten: Wert = None, f_oben: Wert = None) -> Wert:
        """
        Wie :meth:`Halbieren.finde`: wo ``f`` zwischen ``unten`` und ``oben``
        null wird, bis das Fenster schmaler ist als ``schranke`` -- zurueck
        kommt die zuletzt gefundene Stelle. Die Werte an den Enden werden
        gebraucht; wer sie schon kennt, gibt sie mit.
        """
        fa = f(unten) if f_unten is None else f_unten
        fb = f(oben) if f_oben is None else f_oben
        if fa is None or fb is None:
            return None
        a, b = unten, oben
        if fa == 0.0:
            return a
        for _ in range(SCHRITTE):
            if fb == 0.0 or abs(b - a) <= schranke:
                break
            c = _sekante(a, fa, b, fb)
            fc = f(c)
            if fc is None:
                return None
            a, fa, b, fb = _weiter(a, fa, b, fb, c, fc)
        return b


#: Die beiden Suchen, wie sie meist gebraucht werden. Ohne eigenen Zustand --
#: wo eine Suche bei der zuletzt gefundenen Stelle anfaengt, merkt sich die
#: Stelle, wer sucht.
HALBIEREN = Halbieren()
ILLINOIS = Illinois()

#: Illinois ohne Gedaechtnis: jede Suche im ganzen Fenster -- fuer einen
#: Loeser, der viele Fragen beantwortet und dessen Antworten nicht an ihrer
#: Reihenfolge haengen sollen.
ILLINOIS_VON_VORN = Illinois(vom_letzten=False)


def illinois(f: Callable[[float], Tuple[float, Optional[B]]], a: float, fa: float,
             b: float, fb: float, *, schranke_x: float, schranke_f: float) -> Optional[B]:
    """
    Eine Nullstelle von ``f`` zwischen ``a`` und ``b``, die verschiedene
    Vorzeichen haben -- mit :class:`Illinois`, aber fuer eine Frage, die mehr
    als die Stelle braucht: ``f`` gibt ``(Wert, Beigabe)`` zurueck, und
    zurueck kommt die Beigabe der besten Stelle -- ``None``, wenn schon die
    erste keinen Wert hat. Fertig ist die Suche, sobald der Wert unter
    ``schranke_f`` liegt oder das Fenster unter ``schranke_x``.

    Hat ``f`` an einer Stelle keinen Wert (``nan``), endet die Suche dort: ohne
    ihn laesst sich nicht weiter eingrenzen. Bis 2026-10-17 rechnete sie mit
    ``nan`` weiter, bis eine Zerlegung bei ψ = nan abbrach -- an der kippenden
    Nulllinie eines L, wo zwischen zwei Neigungen mit Gleichgewicht eine ohne
    liegen kann.
    """
    beste = None
    for _ in range(SCHRITTE):
        c = _sekante(a, fa, b, fb)
        fc, beigabe = f(c)
        if math.isnan(fc):
            break
        if beste is None or abs(fc) < beste[0]:
            beste = (abs(fc), beigabe)
        if abs(fc) <= schranke_f or abs(b - a) <= schranke_x:
            break
        a, fa, b, fb = _weiter(a, fa, b, fb, c, fc)
    return None if beste is None else beste[1]


def _sekante(a: float, fa: float, b: float, fb: float) -> float:
    """Wo die Gerade durch ``(a, fa)`` und ``(b, fb)`` null wird."""
    return b - fb * (b - a) / (fb - fa)


def _weiter(a: float, fa: float, b: float, fb: float, c: float,
            fc: float) -> Tuple[float, float, float, float]:
    """
    Das Fenster nach dem Schritt nach ``c``: ``c`` wird das neue Ende ``b``.
    Wechselt der Wert dort das Vorzeichen gegen ``b``, wird ``b`` das andere
    Ende; sonst bleibt ``a`` stehen, und sein Wert wird halbiert.
    """
    if (fc > 0.0) != (fb > 0.0):
        a, fa = b, fb
    else:
        fa *= 0.5
    return a, fa, c, fc


def eingrenzen(f: Callable[[float], Wert], a: float, fa: float, schritt: float, *,
               faktor: float, unten: float = -math.inf,
               oben: float = math.inf) -> Optional[Tuple[float, float, float, float]]:
    """
    Von ``a`` aus ein Fenster, in dem ``f`` das Vorzeichen wechselt -- mit
    wachsenden Schritten in die Richtung, in der ``f`` null wird (``f``
    steigt): ``schritt``, dann mal ``faktor``. Zurueck kommt
    ``(unten, oben, f_unten, f_oben)``, unten der kleinere Wert, wie
    :meth:`Illinois.finde` sie nimmt -- ``None``, wo ``f`` unterwegs keinen
    Wert hat oder das Fenster an ``unten`` bzw. ``oben`` stoesst, ohne dass das
    Vorzeichen wechselt.

    Fuer Suchen, die bei einer Stelle anfangen, die nahe liegt -- der zuletzt
    gefundenen Ebene: dort ist das Fenster in wenigen Schritten eng.
    """
    for _ in range(SCHRITTE):
        if fa == 0.0:
            return a, a, fa, fa
        b = min(max(a - schritt if fa > 0.0 else a + schritt, unten), oben)
        fb = f(b)
        if fb is None:
            return None
        if fb == 0.0 or (fb > 0.0) != (fa > 0.0):
            return (a, b, fa, fb) if fa < fb else (b, a, fb, fa)
        if b in (unten, oben):
            return None
        a, fa = b, fb
        schritt *= faktor
    return None
