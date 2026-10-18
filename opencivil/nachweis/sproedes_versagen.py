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

Der Teiler 3 gilt fuer Platten unter Biegung -- es reisst der Randbereich, nicht
die halbe Hoehe wie beim Zwang (SIA 262:2025, 4.4.1.3).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

from opencivil.core.berechnung import (
    Ausfuehrung, Eingabebezug, Eingaben, Fallbefund, Nachweis, NachweisUrteil, grad_def,
    grad_formel,
)
from opencivil.core.einheiten import EINHEITSLOS, Groesse
from opencivil.core.latex import angabe, bedingung
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.nachweis.rissgroessen import (
    Rissgroessen, protokoll_rissmoment_rechteck, rissmoment_rechteck, rissmoment_wert,
)
from opencivil.querschnitt.platte import Bewehrungslage, Richtung


@dataclass
class Lagenergebnis:
    """Was der Nachweis fuer eine Lage gefunden hat."""

    lage: Bewehrungslage
    M_Rd: float = 0.0
    """Biegewiderstand bei N_Ed = 0 auf der Seite dieser Lage, in Nm (Betrag)."""

    erfuellungsgrad: float = 0.0
    erfuellt: bool = False
    begruendung: str = ""
    hinweis: str = ""

    @property
    def machbar(self) -> bool:
        return self.M_Rd > 0.0


class SproedesVersagen(Nachweis):
    """
    Mindestbewehrung gegen sprödes Versagen.

    Ein Nachweis je Platte, ein Urteil je Lage der Tragrichtung. In der
    Zusammenfassung steht die ungünstigere der beiden -- geht die auf, geht
    auch die andere auf.

    ``M_Rd(N=0)`` kommt als Eingang aus dem M-N-Nachweis. Als Eingang und nicht
    als mitgegebene Zahl, damit die Abhängigkeit im Graphen steht und die
    Rückverfolgung sie zeigt.
    """

    THEMA = "Sprödes Versagen"

    def __init__(
        self,
        querschnitt,
        richtung: Richtung,
        lagen: Sequence[int],
        mn_nachweis,
    ) -> None:
        gewaehlt = sorted(set(lagen))
        self.lagen = [l for l in querschnitt.lagen
                      if l.richtung is richtung and l.nummer in gewaehlt]
        if not self.lagen:
            raise ValueError(
                f"Querschnitt '{querschnitt.name}': in {richtung.beschriftung} "
                f"ist keine der gewählten Lagen vorhanden.")

        self.querschnitt = querschnitt
        self.richtung = richtung
        self.mn = mn_nachweis

        r = richtung.value
        basis = f"{querschnitt.id}.nachweis.sproede.{r}"
        self.d_ausnutzung: Dict[int, WertDef] = {
            l.nummer: grad_def(
                f"{basis}.lage{l.nummer}.erfuellungsgrad",
                rf"\alpha_{{eff,SV,{l.nummer},{r}}}",
                (f"Erfüllungsgrad sprödes Versagen – "
                 f"{l.nummer}. Lage {r}"),
                "SIA 262:2025, 4.4.1.3",
            )
            for l in self.lagen
        }

        bezuege = [
            Eingabebezug("h", querschnitt.id_von("h")),
            Eingabebezug("b", querschnitt.id_breite(richtung)),
            Eingabebezug("f_ctm", querschnitt.beton.id_von("f_ctm")),
        ]
        # Je Seite der passende Eckwert: die untere Lage traegt das positive
        # Moment, die obere das negative.
        for lage in self.lagen:
            bezuege.append(Eingabebezug(
                f"M_Rd_{lage.nummer}",
                mn_nachweis.d_eckwerte[f"M_Rd_N0_{lage.seite.marke}"].id))

        super().__init__(
            basis,
            ausgaben=list(self.d_ausnutzung.values()),
            bezuege=bezuege,
            titel=(f"Sprödes Versagen {richtung.beschriftung} – "
                   f"{querschnitt.name}"),
            referenz="SIA 262:2025, 4.4.1.3",
            abschnitt=querschnitt.abschnitt,
        )

    # -- Rechnen ------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        h = e.g("h").si
        b = e.g("b").si
        f_ctm = e.g("f_ctm").si

        groessen = rissmoment_rechteck(h=h, b=b, f_ctm=f_ctm)
        self._protokoll_ansatz(p, e, groessen)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        befund = Fallbefund()

        for lage in self.lagen:
            erg = Lagenergebnis(lage=lage)
            erg.M_Rd = abs(e.g(f"M_Rd_{lage.nummer}").si)
            M_Riss = groessen.M_Riss

            if erg.M_Rd <= 0.0:
                erg.begruendung = erg.hinweis = (
                    f"{lage.nummer}. Lage ({lage.seite}) ohne Bewehrung → kein "
                    f"Biegewiderstand, kein Nachweis.")
            else:
                erg.erfuellungsgrad = (float("inf") if M_Riss == 0
                                       else erg.M_Rd / M_Riss)
                erg.erfuellt = erg.M_Rd >= M_Riss
                erg.begruendung = (
                    f"M_{self.mn.wahl.index}(N_Ed = 0) = {erg.M_Rd / 1e3:.1f} kNm "
                    f"{'≥' if erg.erfuellt else '<'} M_Riss = {M_Riss / 1e3:.1f} kNm.")

            befund.ergebnisse.append(erg)
            self._protokoll_lage(p, erg, groessen)
            ergebnis[self.d_ausnutzung[lage.nummer].id] = Groesse(
                erg.erfuellungsgrad, EINHEITSLOS)
            urteile.append(self._urteil(erg, groessen))

        self.protokoll_massgebend(p, urteile)
        return Ausfuehrung(ergebnis, self.teilurteile(urteile), befund)

    def _m_rd(self, erg: Lagenergebnis) -> Wert:
        """Der Biegewiderstand der Lage -- der Widerstand in Tabelle und Herleitung."""
        nummer, r = erg.lage.nummer, self.richtung.value
        return Zwischenwerte(f"{self.id}.lage{nummer}").moment(
            "M_Rd", rf"M_{{{self.mn.wahl.index},{r}}}(N_{{Ed}} = 0)_{{{nummer}}}", erg.M_Rd,
            "Widerstand")

    def _urteil(self, erg: Lagenergebnis, groessen: Rissgroessen) -> NachweisUrteil:
        nummer = erg.lage.nummer
        return NachweisUrteil(
            art="SV",
            ziel=self.d_ausnutzung[nummer].id,
            fall=f"{nummer}. Lage",
            erfuellt=erg.erfuellt,
            erfuellungsgrad=Groesse(erg.erfuellungsgrad, EINHEITSLOS),
            begruendung=erg.begruendung,
            hinweis=erg.hinweis,
            einwirkung=rissmoment_wert(self.id, groessen) if erg.machbar else None,
            widerstand=self._m_rd(erg) if erg.machbar else None,
        )

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben, groessen: Rissgroessen) -> None:
        p.titel(f"Sprödes Versagen – {self.richtung.beschriftung}")
        p.erklaerung(
            "Ein zu schwach bewehrter Querschnitt reisst und versagt im selben "
            "Augenblick. Nachgewiesen wird deshalb, dass der bewehrte "
            "Querschnitt mehr trägt als der unbewehrte im Augenblick des "
            f"Risses: M_{self.mn.wahl.index}(N_Ed = 0) ≥ M_Riss."
        )
        protokoll_rissmoment_rechteck(p, e, groessen, basis=self.id,
                                      referenz="SIA 262:2025, 4.4.1.3")

    def _protokoll_lage(self, p: Protokoll, erg: Lagenergebnis,
                        groessen: Rissgroessen) -> None:
        nummer = erg.lage.nummer
        r = self.richtung.value
        p.titel(f"Sprödes Versagen – {nummer}. Lage {r}", ebene=3)

        if not erg.machbar:
            p.text(erg.begruendung)
            return

        m_rd, m_riss = self._m_rd(erg), rissmoment_wert(self.id, groessen)
        p.gleichung(bedingung(angabe(m_rd), r"\ge", angabe(m_riss), erg.erfuellt),
                    titel="Biegewiderstand gegen Rissmoment")
        grad_formel(p, self.d_ausnutzung[nummer], erg.erfuellungsgrad,
                    m_rd, m_riss, erg.erfuellt)
