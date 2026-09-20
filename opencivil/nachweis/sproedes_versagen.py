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

``M_Rd(N_Ed = 0)`` kommt aus der Handrechnung und ist dort vollstaendig
hergeleitet; hier wird es nur noch gegenuebergestellt. Das Rissmoment gehoert
dem **ungerissenen** Bruttoquerschnitt::

    k_t      = 1 / (1 + 0.5 * h/3)            h in Metern
    f_ct,eff = k_t * f_ctm
    M_Riss   = f_ct,eff * h^2 * b / 6

Der Teiler 3 gilt fuer Platten unter Biegung -- es reisst der Randbereich, nicht
die halbe Hoehe wie beim Zwang (SIA 262:2025, 4.4.1.3).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Eingabebezug, Eingaben, Nachweis, NachweisUrteil,
)
from opencivil.core.einheiten import EINHEITSLOS, KNM, Groesse
from opencivil.core.protokoll import Protokoll
from opencivil.core.wert import WertDef
from opencivil.material.basis import mit_index
from opencivil.querschnitt.platte import Bewehrungslage, Richtung


@dataclass(frozen=True)
class Rissgroessen:
    """Das Rissmoment und was dazu gehoert -- je Platte, nicht je Lage."""

    k_t: float
    f_ct_eff: float
    M_Riss: float
    """Rissmoment in Nm, bezogen auf die betrachtete Breite."""


#: Teiler der Plattendicke im Beiwert. Unter Biegung reisst der Randbereich,
#: nicht die halbe Hoehe wie beim Zwang. SIA 262:2025, 4.4.1.3.
MOMENTENTEILER = 3.0


def rissmoment(*, h: float, b: float, f_ctm: float) -> Rissgroessen:
    """
    Das Moment, bei dem der ungerissene Querschnitt aufreisst.

    ``h^2*b/6`` ist das elastische Widerstandsmoment des Bruttoquerschnitts.
    Alles in SI-Basis; Rueckgabe in Nm.
    """
    k_t = 1.0 / (1.0 + 0.5 * h / MOMENTENTEILER)
    f_ct_eff = k_t * f_ctm
    return Rissgroessen(k_t=k_t, f_ct_eff=f_ct_eff,
                        M_Riss=f_ct_eff * h * h * b / 6.0)


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
    Mindestbewehrung gegen sprödes Versagen, je gewählter Lage.

    Ein Nachweis je Platte und Tragrichtung, ein Urteil je Lage dieser
    Richtung. Welche Lagen geprüft werden, sagt der Benutzer -- üblich ist die
    Lage, die das grösste Moment trägt.

    ``M_Rd(N=0)`` kommt als Eingang aus dem M-N-Nachweis. Als Eingang und nicht
    als mitgegebene Zahl, damit die Abhängigkeit im Graphen steht und die
    Rückverfolgung sie zeigt.
    """

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
        self.ergebnisse: List[Lagenergebnis] = []
        self.groessen: Optional[Rissgroessen] = None

        r = richtung.value
        basis = f"{querschnitt.id}.nachweis.sproede.{r}"
        self.d_ausnutzung: Dict[int, WertDef] = {
            l.nummer: WertDef(
                id=f"{basis}.lage{l.nummer}.erfuellungsgrad",
                symbol=rf"\alpha_{{eff,SV,{l.nummer},{r}}}",
                einheit=EINHEITSLOS,
                beschreibung=(f"Erfüllungsgrad sprödes Versagen – "
                              f"{l.nummer}. Lage {r}"),
                referenz="SIA 262:2025, 4.4.1.3",
                stellen=2,
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
            schluessel = "M_Rd_N0_pos" if lage.von_unten else "M_Rd_N0_neg"
            bezuege.append(Eingabebezug(
                f"M_Rd_{lage.nummer}", mn_nachweis.d_eckwerte[schluessel].id))

        self.s_f_ctm = mit_index("f_{ctm}", querschnitt.beton.symbol_index)

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

        self.groessen = rissmoment(h=h, b=b, f_ctm=f_ctm)
        self._protokoll_ansatz(p, h, b, f_ctm)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        self.ergebnisse = []

        for lage in self.lagen:
            erg = Lagenergebnis(lage=lage)
            erg.M_Rd = abs(e.g(f"M_Rd_{lage.nummer}").si)
            M_Riss = self.groessen.M_Riss

            if erg.M_Rd <= 0.0:
                seite = "unten" if lage.von_unten else "oben"
                erg.begruendung = erg.hinweis = (
                    f"Nachweis nicht machbar: auf der Seite der "
                    f"{lage.nummer}. Lage ({seite}) hat die Handrechnung keinen "
                    f"Biegewiderstand – dort liegt keine Bewehrung.")
            else:
                erg.erfuellungsgrad = (float("inf") if M_Riss == 0
                                       else erg.M_Rd / M_Riss)
                erg.erfuellt = erg.M_Rd >= M_Riss
                erg.begruendung = (
                    f"M_Rd(N_Ed = 0) = {erg.M_Rd / 1e3:.1f} kNm gegen "
                    f"M_Riss = {M_Riss / 1e3:.1f} kNm.")

            self.ergebnisse.append(erg)
            self._protokoll_lage(p, erg)
            ergebnis[self.d_ausnutzung[lage.nummer].id] = Groesse(
                min(erg.erfuellungsgrad, 1e9), EINHEITSLOS)
            urteile.append(self._urteil(erg))

        return ergebnis, urteile

    def _urteil(self, erg: Lagenergebnis) -> NachweisUrteil:
        nummer = erg.lage.nummer
        r = self.richtung.value
        einwirkung = WertDef(
            id=f"{self.id}.M_Riss",
            symbol=r"M_{Riss}",
            einheit=KNM, beschreibung="Einwirkung", stellen=1,
        ).belegen(Groesse.aus_si(self.groessen.M_Riss, KNM))
        widerstand = WertDef(
            id=f"{self.id}.lage{nummer}.M_Rd",
            symbol=rf"M_{{Rd,{r}}}(N_{{Ed}} = 0)_{{{nummer}}}",
            einheit=KNM, beschreibung="Widerstand", stellen=1,
        ).belegen(Groesse.aus_si(erg.M_Rd, KNM))
        return NachweisUrteil(
            name=f"Sprödes Versagen {r} – {nummer}. Lage",
            art="SV",
            langname=f"Sprödes Versagen ({r})",
            fall=f"{nummer}. Lage",
            erfuellt=erg.erfuellt,
            erfuellungsgrad=Groesse(erg.erfuellungsgrad, EINHEITSLOS),
            begruendung=erg.begruendung,
            hinweis=erg.hinweis,
            einwirkung=einwirkung if erg.machbar else None,
            widerstand=widerstand if erg.machbar else None,
        )

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, h: float, b: float,
                          f_ctm: float) -> None:
        g = self.groessen
        p.titel(f"Sprödes Versagen – {self.richtung.beschriftung}")
        p.text(
            "Ein zu schwach bewehrter Querschnitt reisst und versagt im selben "
            "Augenblick. Nachgewiesen wird deshalb, dass der bewehrte "
            "Querschnitt mehr trägt als der unbewehrte im Augenblick des "
            "Risses: M_Rd(N_Ed = 0) ≥ M_Riss."
        )
        p.gleichung(
            rf"k_t = \frac{{1}}{{1 + 0.5 \cdot h/{MOMENTENTEILER:.0f}}}"
            rf" = \frac{{1}}{{1 + 0.5 \cdot {h:.3f}\,\mathrm{{m}}"
            rf"/{MOMENTENTEILER:.0f}}} = {g.k_t:.3f}",
            titel="Beiwert für die Plattendicke",
            referenz="SIA 262:2025, 4.4.1.3")
        p.gleichung(
            rf"f_{{ct,eff}} = k_t \cdot {self.s_f_ctm} = {g.k_t:.3f} \cdot "
            rf"{f_ctm / 1e6:.2f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}"
            rf" = {g.f_ct_eff / 1e6:.2f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}",
            titel="Wirksame Zugfestigkeit")
        p.gleichung(
            r"M_{Riss} = f_{ct,eff} \cdot \frac{h^{2} \cdot b}{6}"
            rf" = {g.f_ct_eff / 1e6:.2f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}} \cdot "
            rf"\frac{{\left({h * 1e3:.0f}\,\mathrm{{mm}}\right)^{{2}} \cdot "
            rf"{b * 1e3:.0f}\,\mathrm{{mm}}}}{{6}}"
            rf" = {g.M_Riss / 1e3:.1f}\,\mathrm{{kNm}}",
            titel="Rissmoment des ungerissenen Querschnitts")

    def _protokoll_lage(self, p: Protokoll, erg: Lagenergebnis) -> None:
        nummer = erg.lage.nummer
        r = self.richtung.value
        p.titel(f"Sprödes Versagen – {nummer}. Lage {r}", ebene=3)

        if not erg.machbar:
            p.text(erg.begruendung)
            return

        zustand = r"\text{erfüllt}" if erg.erfuellt else r"\text{NICHT erfüllt}"
        vergleich = r"\ge" if erg.erfuellt else "<"
        p.gleichung(
            rf"M_{{Rd,{r}}}(N_{{Ed}} = 0) = {erg.M_Rd / 1e3:.1f}\,\mathrm{{kNm}}"
            rf" \quad {vergleich} \quad M_{{Riss}} = "
            rf"{self.groessen.M_Riss / 1e3:.1f}\,\mathrm{{kNm}}"
            rf" \quad \Rightarrow \quad {zustand}",
            titel="Biegewiderstand gegen Rissmoment")
        grad = ("\\infty" if math.isinf(erg.erfuellungsgrad)
                else f"{erg.erfuellungsgrad:.2f}")
        p.gleichung(
            rf"\alpha_{{eff,SV,{nummer},{r}}} = "
            rf"\frac{{M_{{Rd}}(N_{{Ed}} = 0)}}{{M_{{Riss}}}} = "
            rf"\frac{{{erg.M_Rd / 1e3:.1f}\,\mathrm{{kNm}}}}"
            rf"{{{self.groessen.M_Riss / 1e3:.1f}\,\mathrm{{kNm}}}} = {grad}",
            titel="Erfüllungsgrad")
