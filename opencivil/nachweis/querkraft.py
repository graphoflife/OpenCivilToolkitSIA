"""
opencivil/nachweis/querkraft.py -- Querkraftnachweis ohne Querkraftbewehrung.

VERANTWORTUNG:
Bestimmt den Querkraftwiderstand einer Platte je Tragrichtung und prueft ihn
gegen die angegebenen Querkraefte.

ANSATZ::

    v_Rd = k_d * tau_cd * d_v

    k_d   = 1 / (1 + eps_v * d * k_g)
    k_g   = 48 / (16 + D_max * min[1.0; (60/f_ck)^2])
    m_Dd  = |N_Ed| * h / 6                      Dekompressionsmoment
    eps_v = f_yd * (m_Ed - m_Dd) / (E_s * (m_Rd(N_Ed) - m_Dd))

    d_v = d - Einlagenhoehe,  falls  h/6 < Einlagenhoehe < d
    d_v = d                   sonst

``d`` ist die statische Hoehe der *gezogenen* Bewehrung und haengt damit vom
Vorzeichen des Moments ab: bei positivem Moment liegt der Zug unten, bei
negativem oben.

ZUG BRAUCHT KEINEN SONDERFALL:
Das Dekompressionsmoment ist ueber ``min(N_Ed; 0)`` definiert und wird bei
einer Normalzugkraft von selbst null -- entlastend wirkt nur Druck. Der
Nachweis laeuft damit unveraendert weiter; frueher stand hier ein Sonderfall,
der ``v_Rd = 0`` setzte.

EINHEITEN:
Die Formeln der Norm sind dimensionell inhomogen -- ``d`` und ``D_max`` gehen
in Millimeter ein, ``f_ck`` in N/mm^2. Sie laufen deshalb ueber
:func:`opencivil.core.einheiten.empirisch`, das diese Voraussetzung erzwingt.
``v_Rd`` ergibt sich in N/mm, also kN/m -- eine Querkraft je Laufmeter.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Eingabebezug, Eingaben, Nachweis, NachweisUrteil,
)
from opencivil.core.einheiten import (
    EINHEITSLOS, KN, KN_PRO_M, KNM, MM, N_PRO_MM2, Groesse, empirisch,
)
from opencivil.core.latex import als_text
from opencivil.core.protokoll import Protokoll
from opencivil.core.wert import WertDef
from opencivil.nachweis.biegung_normalkraft import protokoll_interpolation
from opencivil.querschnitt.platte import Plattenquerschnitt, Richtung

#: Unterer Riegel fuer den Beiwert der Gesteinskoernung.
K_G_MINDEST = 1.20

#: Aufschlag auf die Fliessdehnung, sobald ``m_Ed`` den Widerstand ueberschreitet.
PLASTISCH = 1.5

#: Stuetzstellen der M_Ed-v_Rd-Kurve.
KURVENPUNKTE = 50

#: Wie weit die Kurve ueber ``m_Rd`` hinaus gezeichnet wird, in Nm.
KURVENZUGABE = 20e3


@dataclass(frozen=True)
class Kurvenbeiwerte:
    """
    Was ausser Moment und Normalkraft in den Widerstand eingeht.

    Alles in SI-Basis. Steht nach dem Lauf am Nachweis bereit, damit sich die
    Kurve zu jeder eingestellten Normalkraft neu rechnen laesst -- ohne dass
    die Oberflaeche die Formel ein zweites Mal enthaelt.
    """

    h: float
    tiefen: Tuple[float, ...]
    einlage: float
    tau_cd: float
    f_yd: float
    E_s: float
    k_g: float

    def hoehen(self, moment_positiv: bool) -> Tuple[float, float]:
        """``(d, d_v)`` fuer diese Momentenrichtung."""
        d = _statische_hoehe(self.tiefen, self.h, moment_positiv)
        d_v = d - self.einlage if (self.h / 6.0 < self.einlage < d) else d
        return d, d_v


@dataclass(frozen=True)
class Widerstandspunkt:
    """
    Was bei einem bestimmten Moment noch an Querkraft aufnehmbar ist.

    Ein einzelner Punkt der Rechnung -- der Nachweis braucht ihn fuer seine
    Faelle, die Kurve fuer ihre fuenfzig Stuetzstellen. Beide ueber dieselbe
    Funktion, sonst zeigte das Diagramm etwas anderes als der Nachweis.
    """

    m_Dd: float
    eps_v: float
    k_d: float
    v_Rd: float
    """in N/m."""

    plastisch: bool = False
    """``m_Ed`` liegt ueber dem Momentenwiderstand; die Bewehrung fliesst."""

    grund: str = ""
    """Gesetzt, wenn sich kein Widerstand bestimmen liess."""


def widerstand(
    *, M_Ed: float, N_Ed: float, h: float, d: float, d_v: float,
    tau_cd: float, f_yd: float, E_s: float, k_g: float, m_Rd: float,
) -> Widerstandspunkt:
    """
    Der Querkraftwiderstand bei diesem Moment und dieser Normalkraft.

    Alles in SI-Basis; ``tau_cd`` in Pa, ``m_Rd`` in Nm, Rueckgabe in N/m.

    DREI AESTE:

    * ``|m_Ed| <= m_Dd`` -- der Querschnitt bleibt ungerissen, ``eps_v = 0``
      und ``k_d`` damit am groessten.
    * ``|m_Ed| <= m_Rd`` -- der Regelfall der Norm.
    * ``|m_Ed| >  m_Rd`` -- die Bewehrung fliesst. Die Dehnung waechst dann
      nicht mehr nach der elastischen Beziehung; angesetzt wird
      ``eps_v = 1.5 * f_yd/E_s * |m_Ed|/m_Rd``. Der Widerstand faellt damit
      sprunghaft, und genau das soll die Kurve zeigen.
    """
    m_Dd = abs(min(N_Ed, 0.0)) * h / 6.0
    zaehler = abs(M_Ed) - m_Dd
    nenner = m_Rd - m_Dd
    plastisch = False

    if zaehler <= 0.0:
        eps_v = 0.0
    elif nenner <= 0.0:
        return Widerstandspunkt(
            m_Dd=m_Dd, eps_v=0.0, k_d=0.0, v_Rd=0.0,
            grund=(f"m_Rd(N_Ed) = {m_Rd / 1e3:.1f} kNm liegt nicht über dem "
                   f"Dekompressionsmoment m_Dd = {m_Dd / 1e3:.1f} kNm. "
                   f"Der Querkraftwiderstand ist so nicht bestimmbar."))
    elif abs(M_Ed) > m_Rd:
        eps_v = PLASTISCH * (f_yd / E_s) * abs(M_Ed) / m_Rd
        plastisch = True
    else:
        eps_v = f_yd * zaehler / (E_s * nenner)

    # k_d ist empirisch: d geht in Millimeter ein.
    k_d = 1.0 / (1.0 + eps_v * (d * 1e3) * k_g)
    return Widerstandspunkt(
        m_Dd=m_Dd, eps_v=eps_v, k_d=k_d,
        v_Rd=k_d * (tau_cd / 1e6) * (d_v * 1e3) * 1e3,   # N/m
        plastisch=plastisch)


def _statische_hoehe(tiefen: Sequence[float], h: float, moment_positiv: bool) -> float:
    """
    Statische Hoehe der gezogenen Bewehrung, in m ab der gedrueckten Kante.

    Bei positivem Moment liegt der Zug unten: gemessen wird von der Oberkante
    zur untersten Lage. Bei negativem Moment umgekehrt.
    """
    return max(tiefen) if moment_positiv else h - min(tiefen)


@dataclass(frozen=True)
class Querkraftfall:
    """Eine zu pruefende Kombination fuer den Querkraftnachweis."""

    name: str
    V_Ed: Groesse
    M_Ed: Groesse
    N_Ed: Groesse

    @property
    def kennung(self) -> str:
        return "".join(z if z.isalnum() else "_" for z in self.name)


@dataclass
class Querkraftergebnis:
    """Alle Zwischenwerte eines Falls, damit die Herleitung vollstaendig ist."""

    fall: Querkraftfall
    d: float = 0.0
    d_v: float = 0.0
    k_g: float = 0.0
    k_d: float = 0.0
    eps_v: float = 0.0
    m_Dd: float = 0.0
    m_Rd: float = 0.0
    """Momentenwiderstand bei der wirkenden Normalkraft, in Nm."""

    v_Rd: float = 0.0
    """in N/m."""

    plastisch: bool = False
    """``m_Ed`` liegt ueber dem Momentenwiderstand -- siehe :func:`widerstand`."""

    erfuellungsgrad: float = 0.0
    erfuellt: bool = False
    begruendung: str = ""


class Querkraft(Nachweis):
    """Querkraftwiderstand ohne Querkraftbewehrung, je Tragrichtung."""

    def __init__(
        self,
        querschnitt: Plattenquerschnitt,
        faelle: Sequence[Querkraftfall],
        richtung: Richtung,
        mn_nachweis,
    ) -> None:
        if not faelle:
            raise ValueError("Der Querkraftnachweis braucht mindestens einen Fall.")
        self.posten = querschnitt.posten_in_richtung(richtung)
        if not self.posten:
            raise ValueError(
                f"Querschnitt '{querschnitt.name}': in {richtung.beschriftung} liegt "
                f"keine Bewehrung.")
        self.querschnitt = querschnitt
        self.richtung = richtung
        self.faelle = list(faelle)
        self.ergebnisse: List[Querkraftergebnis] = []

        self.beiwerte: Optional[Kurvenbeiwerte] = None
        """
        Die geloesten Eingaenge, nach dem Lauf. Fuer :meth:`kurve`.

        Ein Ergebnis des Laufs, das ein anderer braucht -- wie
        :attr:`BiegungNormalkraft.bei_normalkraft`. Nicht zu verwechseln mit
        Zwischenwerten, die zwischen eigenen Methoden gereicht werden; die
        gehen durch die Argumentliste.
        """

        self.mn = mn_nachweis
        """
        Der M-N-Nachweis derselben Richtung.

        Gebraucht fuer die Herleitung von ``m_Rd(N_Ed)``: die Zahl kommt als
        Eingang aus dem Graphen, die Interpolation dahinter aber liegt beim
        Nachweis, der das Polygon gerechnet hat. Sie hier nachzubauen hiesse,
        dieselbe Rechnung ein zweites Mal zu schreiben.
        """

        r = richtung.value
        basis = f"{querschnitt.id}.nachweis.querkraft.{r}"
        self.d_grad: Dict[str, WertDef] = {
            f.name: WertDef(
                id=f"{basis}.{f.kennung}.erfuellungsgrad",
                symbol=rf"\alpha_{{eff,V,{r},{f.kennung}}}",
                einheit=EINHEITSLOS,
                beschreibung=f"Erfüllungsgrad Querkraft {richtung.beschriftung} – {f.name}",
                referenz="SIA 262:2025, 4.3.3.2",
                stellen=2,
            )
            for f in self.faelle
        }
        self.d_v_rd: Dict[str, WertDef] = {
            f.name: WertDef(
                id=f"{basis}.{f.kennung}.v_Rd",
                symbol=f"v_{{Rd,{r}}}",
                einheit=KN_PRO_M,
                beschreibung=f"Querkraftwiderstand {richtung.beschriftung} – {f.name}",
                referenz="SIA 262:2025, 4.3.3.2.1",
                stellen=1,
            )
            for f in self.faelle
        }

        bezuege = [
            Eingabebezug("h", querschnitt.id_von("h")),
            Eingabebezug("D_max", querschnitt.id_von("D_max")),
            Eingabebezug("einlagenhoehe", querschnitt.id_von("einlagenhoehe")),
            Eingabebezug("f_ck", querschnitt.beton.id_von("f_ck")),
            Eingabebezug("tau_cd", querschnitt.beton.id_von("tau_cd")),
        ]
        for lage, art, _, as_id, z_id in self.posten:
            bezuege.append(Eingabebezug(f"z_{lage.nummer}{art.kuerzel}", z_id))
        stahl = self.posten[0][0].stahl
        bezuege += [
            Eingabebezug("f_yd", stahl.id_von("f_yd")),
            Eingabebezug("E_s", stahl.id_von("E_s")),
        ]
        # Der Momentenwiderstand bei der wirkenden Normalkraft kommt aus dem
        # M-N-Nachweis -- je Fall einer. Als Eingang statt als mitgegebene Zahl,
        # damit die Abhaengigkeit im Graphen steht und die Rueckverfolgung sie
        # zeigt.
        for f in self.faelle:
            bezuege.append(Eingabebezug(
                f"m_Rd_{f.kennung}", mn_nachweis.d_m_rd[f.name].id))

        super().__init__(
            basis,
            ausgaben=list(self.d_grad.values()) + list(self.d_v_rd.values()),
            bezuege=bezuege,
            titel=f"Querkraftnachweis {richtung.beschriftung} – {querschnitt.name}",
            referenz="SIA 262:2025, 4.3.3.2",
            # Der Nachweis gehoert zu seiner Platte. Ohne diese Angabe stuende
            # er unter der Ueberschrift, die zufaellig zuletzt offen war -- und
            # welche das ist, entscheidet die Abhaengigkeitsfolge.
            abschnitt=querschnitt.abschnitt,
        )

    # -- Rechnen ------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        h = e.g("h").si
        tau_cd = e.g("tau_cd")
        f_yd = e.g("f_yd").si
        E_s = e.g("E_s").si
        einlage = e.g("einlagenhoehe").si
        m_rd = {f.name: abs(e.g(f"m_Rd_{f.kennung}").si) for f in self.faelle}
        tiefen = [e.g(f"z_{l.nummer}{a.kuerzel}").si for l, a, _, _, _ in self.posten]

        self._protokoll_ansatz(p, e)

        D_max = e.g("D_max")
        f_ck = e.g("f_ck")
        k_g_erg = empirisch(
            lambda D_max, f_ck: max(
                K_G_MINDEST, 48.0 / (16.0 + D_max * min(1.0, (60.0 / f_ck) ** 2))),
            ergebnis=EINHEITSLOS,
            D_max=(D_max, MM),
            f_ck=(f_ck, N_PRO_MM2),
        )
        k_g = k_g_erg.wert.si
        roh = 48.0 / (16.0 + D_max.in_einheit(MM)
                      * min(1.0, (60.0 / f_ck.in_einheit(N_PRO_MM2)) ** 2))
        p.gleichung(
            rf"k_g = \max\left[{K_G_MINDEST:.2f};\ \frac{{48}}"
            rf"{{16 + D_{{max}} \cdot \min\left[1.0;\ "
            rf"\left(\frac{{60}}{{f_{{ck}}}}\right)^{{2}}\right]}}\right]"
            "\n= "
            rf"\max\left[{K_G_MINDEST:.2f};\ \frac{{48}}"
            rf"{{16 + {D_max.formatiert(0, MM)} \cdot \min\left[1.0;\ "
            rf"\left(\frac{{60}}{{{f_ck.formatiert(0, N_PRO_MM2)}}}\right)^{{2}}\right]}}\right]"
            rf" = \max\left[{K_G_MINDEST:.2f};\ {roh:.3f}\right] = {k_g:.3f}",
            titel="Beiwert der Gesteinskörnung", referenz="SIA 262:2025, 4.3.3.2.1")

        self.beiwerte = Kurvenbeiwerte(
            h=h, tiefen=tuple(tiefen), einlage=einlage, tau_cd=tau_cd.si,
            f_yd=f_yd, E_s=E_s, k_g=k_g)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        self.ergebnisse = []

        for fall in self.faelle:
            erg = self._einen_fall(fall, h, tau_cd, f_yd, E_s, einlage, k_g,
                                   m_rd[fall.name], tiefen)
            self.ergebnisse.append(erg)
            self._protokoll_fall(p, erg, h, tau_cd, f_yd, E_s, einlage, k_g)

            ergebnis[self.d_v_rd[fall.name].id] = Groesse.aus_si(erg.v_Rd, KN_PRO_M)
            ergebnis[self.d_grad[fall.name].id] = Groesse(
                min(erg.erfuellungsgrad, 1e9), EINHEITSLOS)

            urteile.append(NachweisUrteil(
                name=f"Querkraft {self.richtung.value} – {fall.name}",
                erfuellt=erg.erfuellt,
                erfuellungsgrad=Groesse(erg.erfuellungsgrad, EINHEITSLOS),
                begruendung=erg.begruendung,
                einwirkung=WertDef(
                    id=f"{self.id}.{fall.kennung}.V_Ed", symbol=f"V_{{Ed,{self.richtung.value}}}",
                    einheit=KN_PRO_M, beschreibung="Einwirkung", stellen=1,
                ).belegen(fall.V_Ed.als(KN_PRO_M) if fall.V_Ed.dimension == KN_PRO_M.dimension
                          else Groesse.aus_si(fall.V_Ed.si, KN_PRO_M)),
                # Der Widerstand gilt nur unter genau dieser Einwirkung -- das
                # gehoert ins Symbol, sonst liest sich v_Rd wie ein Kennwert des
                # Querschnitts.
                widerstand=WertDef(
                    id=self.d_v_rd[fall.name].id,
                    symbol=self._widerstandssymbol(fall),
                    einheit=KN_PRO_M, beschreibung="Widerstand", stellen=1,
                ).belegen(Groesse.aus_si(erg.v_Rd, KN_PRO_M)),
            ))

        return ergebnis, urteile

    # -- Kurve --------------------------------------------------------------

    @property
    def momentenrichtungen(self) -> List[bool]:
        """
        Welche Momentenvorzeichen ueberhaupt vorkommen -- hoechstens zwei.

        Danach richtet sich, wie viele Kurven es fuer diese Tragrichtung gibt.
        Ohne einen Fall mit negativem Moment waere eine Kurve fuer «Zug oben»
        eine Aussage ueber etwas, das niemand nachgewiesen haben wollte.
        """
        vorhanden = {f.M_Ed.si >= 0 for f in self.faelle}
        return [p for p in (True, False) if p in vorhanden]

    def kurve(self, N_Ed: float, moment_positiv: bool) -> Optional[dict]:
        """
        Der Querkraftwiderstand ueber dem Moment, bei festgehaltener Normalkraft.

        Fuenfzig Stuetzstellen von null bis ``m_Rd + 20 kNm``. Der Bereich
        jenseits von ``m_Rd`` ist der eigentliche Zweck: dort faellt der
        Widerstand, weil die Bewehrung fliesst (siehe :func:`widerstand`).

        Gerechnet wird mit derselben Funktion wie im Nachweis. Die Kurve kann
        also nicht etwas anderes zeigen als die Punkte, die darauf liegen.

        :param N_Ed: eingestellte Normalkraft in N, Zug positiv.
        :return: ``None``, wenn bei dieser Normalkraft kein Widerstand besteht.
        """
        if self.beiwerte is None:
            return None
        m_Rd = self.mn.moment_bei(N_Ed, positiv=moment_positiv)
        if not m_Rd or m_Rd <= 0.0:
            return None

        d, d_v = self.beiwerte.hoehen(moment_positiv)
        bis = m_Rd + KURVENZUGABE
        punkte = []
        for i in range(KURVENPUNKTE):
            M_Ed = bis * i / (KURVENPUNKTE - 1)
            p = widerstand(
                M_Ed=M_Ed, N_Ed=N_Ed, h=self.beiwerte.h, d=d, d_v=d_v,
                tau_cd=self.beiwerte.tau_cd, f_yd=self.beiwerte.f_yd,
                E_s=self.beiwerte.E_s, k_g=self.beiwerte.k_g, m_Rd=m_Rd)
            punkte.append((M_Ed, p.v_Rd, p.plastisch))

        return {"punkte": punkte, "m_Rd": m_Rd, "d": d, "d_v": d_v, "N_Ed": N_Ed}

    def _widerstandssymbol(self, fall: Querkraftfall) -> str:
        """``v_Rd(M_Ed = 100 kNm, N_Ed = -300 kN)`` -- der Widerstand ist bedingt."""
        r = self.richtung.value
        return (rf"v_{{Rd,{r}}}(M_{{Ed}} = {fall.M_Ed.als_latex(1, KNM)},\ "
                rf"N_{{Ed}} = {fall.N_Ed.als_latex(1, KN)})")

    def _einen_fall(
        self, fall: Querkraftfall, h: float, tau_cd: Groesse,
        f_yd: float, E_s: float, einlage: float, k_g: float,
        m_Rd: float, tiefen: Sequence[float],
    ) -> Querkraftergebnis:
        erg = Querkraftergebnis(fall=fall)
        M_Ed, N_Ed, V_Ed = fall.M_Ed.si, fall.N_Ed.si, fall.V_Ed.si

        erg.d = _statische_hoehe(tiefen, h, M_Ed >= 0)
        erg.d_v = erg.d - einlage if (h / 6.0 < einlage < erg.d) else erg.d
        erg.m_Rd = m_Rd

        # Nur Druck entlastet: bei Zug liefert min(N_Ed; 0) null, das
        # Dekompressionsmoment entfaellt und der Nachweis laeuft unveraendert
        # weiter. Eine Sonderbehandlung braucht es dafuer nicht -- sie stand
        # frueher hier und setzte v_Rd kurzerhand auf null.
        punkt = widerstand(
            M_Ed=M_Ed, N_Ed=N_Ed, h=h, d=erg.d, d_v=erg.d_v,
            tau_cd=tau_cd.si, f_yd=f_yd, E_s=E_s, k_g=k_g, m_Rd=m_Rd)
        erg.m_Dd = punkt.m_Dd
        erg.eps_v = punkt.eps_v
        erg.k_d = punkt.k_d
        erg.v_Rd = punkt.v_Rd
        erg.plastisch = punkt.plastisch

        if punkt.grund:
            erg.erfuellungsgrad = 0.0
            erg.erfuellt = False
            erg.begruendung = punkt.grund
            return erg

        erg.erfuellungsgrad = float("inf") if V_Ed == 0 else abs(erg.v_Rd) / abs(V_Ed)
        erg.erfuellt = erg.erfuellungsgrad >= 1.0
        erg.begruendung = (
            f"v_Rd = k_d · τ_cd · d_v = {erg.k_d:.3f} · "
            f"{tau_cd.formatiert(2, N_PRO_MM2)} N/mm² · {erg.d_v * 1e3:.0f} mm "
            f"= {erg.v_Rd / 1e3:.1f} kN/m.")
        return erg


    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben) -> None:
        p.titel(f"Querkraft – {self.richtung.beschriftung}")
        p.text(
            "Querkraftwiderstand ohne Querkraftbewehrung. Massgebend sind die "
            "statische Höhe der gezogenen Bewehrung, die Grösstkorngrösse und "
            "die Dehnung auf halber Höhe."
        )
        p.gleichung(
            r"v_{Rd} = k_d \cdot \tau_{cd} \cdot d_v \qquad "
            r"k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g}",
            titel="Ansatz", referenz="SIA 262:2025, 4.3.3.2.1")
        p.gleichung(
            r"m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} \qquad "
            r"\varepsilon_v = \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| "
            r"- m_{Dd}\right)}"
            r"{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)}",
            titel="Dekompressionsmoment und Dehnung")
        p.text(
            "Nur eine Normaldruckkraft entlastet; eine Zugkraft bleibt beim "
            "Dekompressionsmoment unberücksichtigt. Da der Widerstand über "
            "m_Ed und N_Ed von der Einwirkung abhängt, wird er für jede "
            "Kombination einzeln bestimmt."
        )
        # Grösstkorn und Einlagenhöhe gehen nur hier ein. Sie stehen darum
        # hier und nicht am Anfang der Plattenanalyse, wo sie zwischen
        # Abmessungen und Bewehrung niemandem etwas sagen.
        for name in ("D_max", "einlagenhoehe"):
            p.wert(e[name])

    def _protokoll_fall(
        self, p: Protokoll, erg: Querkraftergebnis, h: float, tau_cd: Groesse,
        f_yd: float, E_s: float, einlage: float, k_g: float,
    ) -> None:
        """
        Die vollstaendige Rechnung eines Falls, mit Zahlen in jeder Zeile.

        Frueher stand hier nur der Ansatz und eine Ergebnistabelle -- damit war
        der Querkraftwiderstand die einzige Zahl im ganzen Werkzeug, die man
        nicht nachrechnen konnte.
        """
        fall = erg.fall
        r = self.richtung.value
        M_Ed, N_Ed = fall.M_Ed.si, fall.N_Ed.si

        p.titel(f"Querkraftnachweis – {fall.name}", ebene=3)
        p.gleichung(
            rf"V_{{Ed}} = {fall.V_Ed.als_latex(1, KN_PRO_M)} \qquad "
            rf"M_{{Ed}} = {fall.M_Ed.als_latex(1, KNM)} \qquad "
            rf"N_{{Ed}} = {fall.N_Ed.als_latex(1, KN)}",
            titel="Einwirkung")

        seite = "unten" if M_Ed >= 0 else "oben"
        p.gleichung(
            rf"d = {erg.d * 1e3:.1f}\,\mathrm{{mm}}"
            rf"\qquad \text{{(Zug {seite})}}",
            titel="Statische Höhe der gezogenen Bewehrung")

        if erg.d_v < erg.d:
            p.gleichung(
                rf"d_v = d - e_{{Einlage}} = {erg.d * 1e3:.1f}\,\mathrm{{mm}} - "
                rf"{einlage * 1e3:.1f}\,\mathrm{{mm}} = {erg.d_v * 1e3:.1f}\,\mathrm{{mm}}",
                titel="Wirksame Höhe, um die Einlage vermindert")
        else:
            p.gleichung(
                rf"d_v = d = {erg.d_v * 1e3:.1f}\,\mathrm{{mm}}",
                titel="Wirksame Höhe (Einlage nicht massgebend)")

        p.gleichung(
            r"m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6}"
            rf" = \frac{{\left|{min(N_Ed, 0.0) / 1e3:.1f}\right| \cdot "
            rf"{h * 1e3:.0f}\,\mathrm{{mm}}}}{{6}}"
            rf" = {erg.m_Dd / 1e3:.1f}\,\mathrm{{kNm/m}}",
            titel="Dekompressionsmoment")

        if erg.v_Rd == 0.0 and erg.begruendung:
            p.text(erg.begruendung)
            return

        # Der Momentenwiderstand, mit dem gleich gerechnet wird, hängt von der
        # wirkenden Normalkraft ab. Wo er auf dem Polygon herkommt, steht hier
        # -- geschrieben vom M-N-Nachweis, der es gerechnet hat.
        bei_n = self.mn.widerstand_bei_n(fall.name)
        if bei_n is not None:
            protokoll_interpolation(
                p, bei_n,
                titel=f"Momentenwiderstand bei N_Ed = {N_Ed / 1e3:.1f} kN")

        if erg.eps_v == 0.0:
            p.text(
                f"m_Ed = {abs(M_Ed) / 1e3:.1f} kNm/m liegt nicht über "
                f"m_Dd = {erg.m_Dd / 1e3:.1f} kNm/m – der Querschnitt bleibt "
                f"ungerissen, ε_v = 0.")
        else:
            p.gleichung(
                r"\varepsilon_v = \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| "
                r"- m_{Dd}\right)}"
                r"{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)}"
                "\n= "
                rf"\frac{{{f_yd / 1e6:.0f} \cdot \left({abs(M_Ed) / 1e3:.1f} - "
                rf"{erg.m_Dd / 1e3:.1f}\right)}}"
                rf"{{{E_s / 1e6:.0f} \cdot \left({erg.m_Rd / 1e3:.1f} - "
                rf"{erg.m_Dd / 1e3:.1f}\right)}}"
                rf" = {erg.eps_v * 1e3:.3f}\,\text{{‰}}",
                titel="Dehnung auf halber Höhe")

        p.gleichung(
            r"k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g}"
            rf" = \frac{{1}}{{1 + {erg.eps_v * 1e3:.4f} \cdot 10^{{-3}} \cdot "
            rf"{erg.d * 1e3:.1f} \cdot {k_g:.3f}}} = {erg.k_d:.4f}",
            titel="Beiwert für die statische Höhe")

        p.gleichung(
            rf"{self._widerstandssymbol(fall)} = k_d \cdot \tau_{{cd}} \cdot d_v"
            "\n= "
            rf"{erg.k_d:.4f} \cdot {tau_cd.in_einheit(N_PRO_MM2):.4f}\,"
            rf"\mathrm{{N}}/\mathrm{{mm}}^{{2}} \cdot {erg.d_v * 1e3:.1f}\,\mathrm{{mm}}"
            rf" = {erg.v_Rd / 1e3:.1f}\,\mathrm{{kN}}/\mathrm{{m}}",
            titel="Querkraftwiderstand", referenz="SIA 262:2025, 4.3.3.2.1")

        zustand = r"\text{erfüllt}" if erg.erfuellt else r"\text{NICHT erfüllt}"
        grad = (r"\infty" if math.isinf(erg.erfuellungsgrad)
                else f"{erg.erfuellungsgrad:.2f}")
        p.gleichung(
            rf"\alpha_{{eff,V,{r}}} = \frac{{v_{{Rd}}}}{{V_{{Ed}}}} = "
            rf"\frac{{{erg.v_Rd / 1e3:.1f}}}{{{abs(fall.V_Ed.si) / 1e3:.1f}}} = {grad}"
            rf" \quad \Rightarrow \quad {zustand}"
            if fall.V_Ed.si else
            rf"\alpha_{{eff,V,{r}}} = \frac{{v_{{Rd}}}}{{V_{{Ed}}}} = {grad}"
            rf" \quad \Rightarrow \quad {zustand}",
            titel="Erfüllungsgrad")
