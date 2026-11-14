"""
opencivil/nachweis/sproedes_versagen.py -- Mindestbewehrung gegen sprödes Versagen.

VERANTWORTUNG:
Prueft je Bewehrungslage, ob der Biegewiderstand das Rissmoment uebertrifft::

    M_Rd(N_Ed = 0)  >=  M_Riss

WARUM DIESE FORM:
Ein zu schwach bewehrter Querschnitt reisst und versagt im selben Augenblick.
Die Frage ist also nicht, welche Spannung im Stahl entsteht, sondern schlicht,
ob der bewehrte Querschnitt mehr traegt als der unbewehrte im Augenblick des
Risses. Genau das ist ``M_Rd >= M_Riss``.

Frueher stand hier ``M_s,adm = sigma_s,adm * A_s * z``. Das war ein anderer
Nachweis -- naemlich der gegen eine **Zwaengung auf Biegung**, und der steht
jetzt in :mod:`opencivil.nachweis.mindestbewehrung`. Bei normaler Anforderung
war er ausserdem *weniger* streng als ``M_Rd``: ``f_yk/f_yd = 1.15`` wiegt den
kleineren Hebelarm des gerissenen Querschnitts mehr als auf.

``M_Rd(N_Ed = 0)`` kommt aus der Resistenzlinie der Tragsicherheit und ist
dort hergeleitet; hier wird es nur noch gegenuebergestellt. Rechnet die
Tragsicherheit mit charakteristischen Werten, heisst es ``M_Rk``. Das Rissmoment gehoert
dem **ungerissenen** Bruttoquerschnitt::

    k_t      = 1 / (1 + 0.5 * h/3)            h in Metern
    f_ct,eff = k_t * f_ctm
    M_Riss   = f_ct,eff * h^2 * b / 6

Der Teiler 3 gilt fuer Platten und Rechtecke unter Biegung; unter Zug zaehlt
die kleinste Abmessung des gezogenen Teils, bei der Platte die ganze Dicke
(SIA 262:2025, 4.4.1.3, (100)). Die Bedingung selbst steht in 4.3.1.2.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple

from opencivil.core.berechnung import Eingabebezug, Eingaben
from opencivil.core.nachweis import NICHT_FUEHRBAR, Ausgang, Fallausgang, Vergleich
from opencivil.core.latex import angabe, bedingung
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.nachweis.lagennachweis import Lagennachweis
from opencivil.nachweis.rissgroessen import (
    Rissgroessen, protokoll_rissmoment_rechteck, rissmoment_rechteck, rissmoment_wert,
)
from opencivil.querschnitt.platte import Bewehrungslage, Richtung


@dataclass
class Lagenergebnis(Fallausgang):
    """Was der Nachweis fuer eine Lage gefunden hat: M_Rd gegen M_Riss."""

    lage: Bewehrungslage
    M_Rd: float = 0.0
    """Biegewiderstand bei N_Ed = 0 auf der Seite dieser Lage, in Nm (Betrag)."""

    ausgang: Ausgang = NICHT_FUEHRBAR
    begruendung: str = ""


class SproedesVersagen(Lagennachweis):
    """
    Mindestbewehrung gegen sprödes Versagen (:class:`~.lagennachweis.Lagennachweis`).

    Ein Nachweis je Platte, ein Urteil je Lage der Tragrichtung. In der
    Zusammenfassung steht die ungünstigere der beiden -- geht die auf, geht
    auch die andere auf.

    ``M_Rd(N=0)`` kommt als Eingang aus dem M-N-Nachweis. Als Eingang und nicht
    als mitgegebene Zahl, damit die Abhängigkeit im Graphen steht und die
    Rückverfolgung sie zeigt.
    """

    THEMA = "Sprödes Versagen"
    ART = "SV"
    KUERZEL = "SV"
    BENENNUNG = "sprödes Versagen"
    REFERENZ = "SIA 262:2025, 4.3.1.2"

    def __init__(
        self,
        querschnitt,
        richtung: Richtung,
        lagen: Sequence[int],
        mn_nachweis,
    ) -> None:
        self.mn = mn_nachweis
        gewaehlt = self.lagen_waehlen(querschnitt, richtung, lagen)
        super().__init__(
            querschnitt, gewaehlt, richtung=richtung,
            basis=f"{querschnitt.id}.nachweis.sproede.{richtung.value}",
            titel=f"Sprödes Versagen {richtung.beschriftung} – {querschnitt.name}",
            bezuege=[
                Eingabebezug("h", querschnitt.id_von("h")),
                Eingabebezug("b", querschnitt.id_breite(richtung)),
                Eingabebezug("f_ctm", querschnitt.beton.id_von("f_ctm")),
                # Je Seite der passende Eckwert: die untere Lage traegt das
                # positive Moment, die obere das negative.
                *[Eingabebezug(f"M_Rd_{lage.nummer}",
                               mn_nachweis.d_eckwerte[f"M_Rd_N0_{lage.seite.marke}"].id)
                  for lage in gewaehlt],
            ])

    # -- Rechnen ------------------------------------------------------------

    def ansatz(self, e: Eingaben, p: Protokoll) -> Tuple[Rissgroessen, Wert]:
        """Das Rissmoment des Rechtecks -- und seine Herleitung."""
        groessen = rissmoment_rechteck(h=e.g("h").si, b=e.g("b").si, f_ctm=e.g("f_ctm").si)
        self._protokoll_ansatz(p, e, groessen)
        return groessen, rissmoment_wert(self.id, groessen)

    def eine_lage(self, e: Eingaben, lage: Bewehrungslage,
                  ansatz: Tuple[Rissgroessen, Wert]) -> Lagenergebnis:
        groessen, M_Riss = ansatz
        erg = Lagenergebnis(lage=lage)
        erg.M_Rd = abs(e.g(f"M_Rd_{lage.nummer}").si)
        erg.ausgang = v = Vergleich(M_Riss, self._m_rd(erg))
        erg.begruendung = (
            f"M_{self.mn.wahl.index}(N_Ed = 0) = {erg.M_Rd / 1e3:.1f} kNm "
            f"{'≥' if v.erfuellt else '<'} M_Riss = {groessen.M_Riss / 1e3:.1f} kNm.")
        return erg

    def _m_rd(self, erg: Lagenergebnis) -> Wert:
        """Der Biegewiderstand der Lage -- der Widerstand in Tabelle und Herleitung."""
        nummer, r = erg.lage.nummer, self.richtung.value
        return Zwischenwerte(f"{self.id}.lage{nummer}").moment(
            "M_Rd", rf"M_{{{self.mn.wahl.index},{r}}}(N_{{Ed}} = 0)_{{{nummer}}}", erg.M_Rd,
            "Widerstand")

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben, groessen: Rissgroessen) -> None:
        p.titel(f"Sprödes Versagen – {self.richtung.beschriftung}")
        p.erklaerung(
            "Ein zu schwach bewehrter Querschnitt reisst und versagt im selben "
            "Augenblick. Nachgewiesen wird deshalb, dass der bewehrte "
            "Querschnitt mehr trägt als der unbewehrte im Augenblick des "
            f"Risses: M_{self.mn.wahl.index}(N_Ed = 0) ≥ M_Riss."
        )
        protokoll_rissmoment_rechteck(p, e, groessen, basis=self.id)

    def protokoll_lage(self, p: Protokoll, e: Eingaben, erg: Lagenergebnis,
                       ansatz: Tuple[Rissgroessen, Wert]) -> None:
        nummer = erg.lage.nummer
        r = self.richtung.value
        p.titel(f"Sprödes Versagen – {nummer}. Lage {r}", ebene=3)

        v = erg.ausgang
        p.gleichung(bedingung(angabe(v.widerstand), r"\ge", angabe(v.einwirkung), v.erfuellt),
                    titel="Biegewiderstand gegen Rissmoment")
        v.zeile(p, self.d_ausnutzung[nummer])
