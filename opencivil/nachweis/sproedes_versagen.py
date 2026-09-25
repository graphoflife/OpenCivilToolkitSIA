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

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from opencivil.core.berechnung import (
    Eingabebezug, Eingaben, Nachweis, NachweisUrteil, grad_def, grad_formel,
)
from opencivil.core.einheiten import EINHEITSLOS, KNM, M, Groesse
from opencivil.core.latex import angabe, bedingung
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
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


def beiwert_dicke(h_riss: float) -> float:
    """
    ``k_t = 1 / (1 + 0.5 * h)`` -- eine dicke Platte reisst nicht ueber ihre
    ganze Hoehe gleichzeitig.

    Empirisch: ``h_riss`` geht in Metern ein, und Meter ist die SI-Basis.
    Unter Biegung ist es ein Drittel der Dicke, beim Zwang die rissaktive.
    """
    return 1.0 / (1.0 + 0.5 * h_riss)


def rissmoment(*, h: float, b: float, f_ctm: float) -> Rissgroessen:
    """
    Das Moment, bei dem der ungerissene Querschnitt aufreisst.

    ``h^2*b/6`` ist das elastische Widerstandsmoment des Bruttoquerschnitts.
    Alles in SI-Basis; Rueckgabe in Nm.
    """
    k_t = beiwert_dicke(h / MOMENTENTEILER)
    f_ct_eff = k_t * f_ctm
    return Rissgroessen(k_t=k_t, f_ct_eff=f_ct_eff,
                        M_Riss=f_ct_eff * h * h * b / 6.0)


def rissmoment_wert(basis: str, g: Rissgroessen) -> Wert:
    """Das Rissmoment -- die Einwirkung in Tabelle und Herleitung."""
    return WertDef(
        id=f"{basis}.M_Riss", symbol=r"M_{Riss}",
        einheit=KNM, beschreibung="Einwirkung", stellen=1,
    ).belegen(Groesse.aus_si(g.M_Riss, KNM))


def protokoll_zugfestigkeit(
    p: Protokoll, werte: Zwischenwerte, *, k_t: float, f_ct_eff: float,
    h: Wert, f_ctm: Wert, teiler: float, referenz: str,
) -> Wert:
    """
    Beiwert fuer die Plattendicke und wirksame Zugfestigkeit, hergeleitet.

    Drei Nachweise brauchen die beiden Zeilen -- das spröde Versagen und beide
    Zwängungen. ``teiler`` ist der Anteil der Dicke, der reisst: ein Drittel
    unter Biegung, bei der Normalkraft die ganze rissaktive Dicke (``1``).
    Zurueck kommt ``f_ct,eff`` fuer die Zeile danach.
    """
    anteil = "@h" if teiler == 1 else rf"@h/{teiler:.0f}"
    beiwert = werte.zahl("k_t", "k_t", k_t)
    p.formel(beiwert, rf"\frac{{1}}{{1 + 0.5 \cdot {anteil}}}", {"h": h},
             titel="Beiwert für die Plattendicke", referenz=referenz,
             empirisch={"h": M})
    wirksam = werte.spannung("f_ct_eff", "f_{ct,eff}", f_ct_eff, stellen=2)
    p.formel(wirksam, r"@k_t \cdot @f_ctm", {"k_t": beiwert, "f_ctm": f_ctm},
             titel="Wirksame Zugfestigkeit")
    return wirksam


def protokoll_rissmoment(
    p: Protokoll, e: Eingaben, g: Rissgroessen, *, basis: str, referenz: str,
) -> None:
    """
    Das Rissmoment von ``k_t`` an -- fuer das spröde Versagen und die
    Zwängung auf Biegung dieselben drei Zeilen. Gebraucht werden die
    Eingaben ``h``, ``b`` und ``f_ctm``.
    """
    f_ct_eff = protokoll_zugfestigkeit(
        p, Zwischenwerte(basis), k_t=g.k_t, f_ct_eff=g.f_ct_eff, h=e["h"],
        f_ctm=e["f_ctm"], teiler=MOMENTENTEILER, referenz=referenz)
    p.formel(rissmoment_wert(basis, g), r"@f_ct_eff \cdot \frac{@h^{2} \cdot @b}{6}",
             {"f_ct_eff": f_ct_eff, "h": e["h"], "b": e["b"]},
             titel="Rissmoment des ungerissenen Querschnitts")


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
            schluessel = "M_Rd_N0_pos" if lage.von_unten else "M_Rd_N0_neg"
            bezuege.append(Eingabebezug(
                f"M_Rd_{lage.nummer}", mn_nachweis.d_eckwerte[schluessel].id))

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
        self._protokoll_ansatz(p, e)

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
                erg.erfuellungsgrad, EINHEITSLOS)
            urteile.append(self._urteil(erg))

        self._protokoll_massgebend(p, urteile)
        return ergebnis, self.teilurteile(urteile)

    def _m_rd(self, erg: Lagenergebnis) -> Wert:
        """Der Biegewiderstand der Lage -- der Widerstand in Tabelle und Herleitung."""
        nummer, r = erg.lage.nummer, self.richtung.value
        return WertDef(
            id=f"{self.id}.lage{nummer}.M_Rd",
            symbol=rf"M_{{Rd,{r}}}(N_{{Ed}} = 0)_{{{nummer}}}",
            einheit=KNM, beschreibung="Widerstand", stellen=1,
        ).belegen(Groesse.aus_si(erg.M_Rd, KNM))

    def _urteil(self, erg: Lagenergebnis) -> NachweisUrteil:
        nummer = erg.lage.nummer
        r = self.richtung.value
        return NachweisUrteil(
            name=f"Sprödes Versagen {r} – {nummer}. Lage",
            art="SV",
            langname="Sprödes Versagen",
            fall=f"{nummer}. Lage",
            erfuellt=erg.erfuellt,
            erfuellungsgrad=Groesse(erg.erfuellungsgrad, EINHEITSLOS),
            begruendung=erg.begruendung,
            hinweis=erg.hinweis,
            einwirkung=rissmoment_wert(self.id, self.groessen) if erg.machbar else None,
            widerstand=self._m_rd(erg) if erg.machbar else None,
        )


    def _protokoll_massgebend(self, p: Protokoll,
                              urteile: Sequence[NachweisUrteil]) -> None:
        """
        Welche Lage den Nachweis entscheidet.

        In der Zusammenfassung steht nur eine Zeile -- die schlechtere der
        beiden Lagen. Ohne diesen Satz stuende in der Herleitung beides
        nebeneinander und man muesste die Zahlen selbst vergleichen, um zu
        wissen, welche davon in der Tabelle gelandet ist.
        """
        massgebend = self.massgebend(urteile)
        if len(urteile) < 2 or not massgebend:
            return
        p.text(f"Massgebend ist die {massgebend[0].fall} mit dem kleineren "
               f"Erfüllungsgrad; sie steht in der Zusammenfassung.")

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben) -> None:
        p.titel(f"Sprödes Versagen – {self.richtung.beschriftung}")
        p.text(
            "Ein zu schwach bewehrter Querschnitt reisst und versagt im selben "
            "Augenblick. Nachgewiesen wird deshalb, dass der bewehrte "
            "Querschnitt mehr trägt als der unbewehrte im Augenblick des "
            "Risses: M_Rd(N_Ed = 0) ≥ M_Riss."
        )
        protokoll_rissmoment(p, e, self.groessen, basis=self.id,
                             referenz="SIA 262:2025, 4.4.1.3")

    def _protokoll_lage(self, p: Protokoll, erg: Lagenergebnis) -> None:
        nummer = erg.lage.nummer
        r = self.richtung.value
        p.titel(f"Sprödes Versagen – {nummer}. Lage {r}", ebene=3)

        if not erg.machbar:
            p.text(erg.begruendung)
            return

        m_rd, m_riss = self._m_rd(erg), rissmoment_wert(self.id, self.groessen)
        p.gleichung(bedingung(angabe(m_rd), r"\ge" if erg.erfuellt else "<",
                              angabe(m_riss), erg.erfuellt),
                    titel="Biegewiderstand gegen Rissmoment")
        grad_formel(p, self.d_ausnutzung[nummer], erg.erfuellungsgrad,
                    m_rd, m_riss, erg.erfuellt)
