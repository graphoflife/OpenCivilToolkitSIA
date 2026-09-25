"""
opencivil/nachweis/querkraft.py -- Querkraftnachweis.

VERANTWORTUNG:
Bestimmt den Querkraftwiderstand einer Platte je Tragrichtung und prueft ihn
gegen die angegebenen Querkraefte.

ZWEI ANSAETZE, EINER DAVON GILT:
Ob die Platte eine Querkraftbewehrung traegt, entscheidet allein, welcher der
beiden laeuft. Beides zu addieren waere ein drittes Modell -- und dieses
Werkzeug rechnet nur, was es auch herleitet.

MIT BUEGELN -- Fachwerkmodell, siehe :func:`buegelwiderstand`::

    V_Rd,s = A_(⌀,V)/(s_V,x * s_V,y) * 0.9 * d * f_yd * cot(alpha)
    V_Rd,c = 0.9 * d * k_c * f_cd * sin(alpha) * cos(alpha)
    V_Rd   = max ueber alpha von min(V_Rd,s; V_Rd,c)

Gesucht wird ganzgradig zwischen ``alpha_min`` und ``alpha_max``. Bei
Normalzug steilt sich die Druckdiagonale auf -- beide Grenzen werden dann auf
mindestens ``ALPHA_ZUG`` gehoben.

OHNE BUEGEL::

    V_Rd = k_d * tau_cd * d_v

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
der ``V_Rd = 0`` setzte.

EINHEITEN:
Die Formeln der Norm sind dimensionell inhomogen -- ``d`` und ``D_max`` gehen
in Millimeter ein, ``f_ck`` in N/mm^2. Sie laufen deshalb ueber
:func:`opencivil.core.einheiten.empirisch`, das diese Voraussetzung erzwingt.
``V_Rd`` ergibt sich in N/mm, also kN/m -- eine Querkraft je Laufmeter.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Eingabebezug, Eingaben, Nachweis, NachweisUrteil, grad_als_text,
)
from opencivil.core.einheiten import (
    EINHEITSLOS, KN, KN_PRO_M, KNM, MM, N_PRO_MM2, Groesse, empirisch,
)
from opencivil.core.latex import als_text
from opencivil.core.protokoll import Protokoll
from opencivil.core.wert import WertDef
from opencivil.core.wert import kennung_aus
from opencivil.material.basis import mit_index
from opencivil.nachweis.biegung_normalkraft import protokoll_interpolation
from opencivil.querschnitt.platte import (
    ALPHA_ZUG, Plattenquerschnitt, Richtung,
)

#: Unterer Riegel fuer den Beiwert der Gesteinskoernung.
K_G_MINDEST = 1.20

#: Vielfaches der Fliessdehnung, sobald ``m_Ed`` den Widerstand ueberschreitet.
#: ``eps_v = PLASTISCH * f_yd / E_s`` -- fest, nicht vom Moment abhaengig.
PLASTISCH = 1.5

#: Stuetzstellen der M_Ed-v_Rd-Kurve.
KURVENPUNKTE = 50

#: Wie weit die Kurve ueber ``m_Rd`` hinaus gezeichnet wird, in Nm.
KURVENZUGABE = 20e3

#: Abstand der beiden Stellen, zwischen denen der Sprung bei ``m_Rd`` liegt,
#: in Nm. Nur damit der Absatz senkrecht gezeichnet wird -- 1 mNm.
SPRUNGSCHRITT = 1e-3


@dataclass(frozen=True)
class Kurvenbeiwerte:
    """
    Was ausser Moment und Normalkraft in den Widerstand eingeht.

    Alles in SI-Basis. Steht nach dem Lauf am Nachweis bereit, damit sich die
    Kurve zu jeder eingestellten Normalkraft neu rechnen laesst -- ohne dass
    die Oberflaeche die Formel ein zweites Mal enthaelt.
    """

    h: float
    lagen: Tuple[Tuple[float, bool], ...]
    """Je vorhandener Posten: ``(z ab Oberkante, liegt unten)``."""

    einlage: float
    tau_cd: float
    f_yd: float
    E_s: float
    k_g: float

    def hoehen(self, moment_positiv: bool) -> Optional[Tuple[float, float]]:
        """``(d, d_v)`` fuer diese Momentenrichtung -- ``None`` ohne Zugbewehrung."""
        d = _statische_hoehe(self.lagen, self.h, moment_positiv)
        if d is None:
            return None
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
    * ``|m_Ed| >  m_Rd`` -- die Bewehrung fliesst. Die Dehnung folgt dann nicht
      mehr dem Moment, sondern ist **fest**: ``eps_v = 1.5 * f_yd/E_s``. Der
      Widerstand faellt an dieser Stelle sprunghaft und bleibt danach
      unveraendert -- in der Kurve eine Waagrechte.
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
        eps_v = PLASTISCH * f_yd / E_s
        plastisch = True
    else:
        eps_v = f_yd * zaehler / (E_s * nenner)

    # k_d ist empirisch: d geht in Millimeter ein.
    k_d = 1.0 / (1.0 + eps_v * (d * 1e3) * k_g)
    return Widerstandspunkt(
        m_Dd=m_Dd, eps_v=eps_v, k_d=k_d,
        v_Rd=k_d * (tau_cd / 1e6) * (d_v * 1e3) * 1e3,   # N/m
        plastisch=plastisch)


@dataclass(frozen=True)
class Buegelpunkt:
    """
    Was bei einer bestimmten Neigung der Druckdiagonalen aufnehmbar ist.

    Beide Anteile in N/m, also je Laufmeter -- wie ``V_Ed``.
    """

    alpha: int
    """Neigung der Druckdiagonalen in Grad."""

    V_Rd_s: float
    """Bügel: waechst, je flacher die Diagonale liegt."""

    V_Rd_c: float
    """Druckdiagonale: groesst bei 45°, faellt nach beiden Seiten."""

    @property
    def V_Rd(self) -> float:
        """Massgebend ist der kleinere der beiden -- eines von beiden versagt."""
        return min(self.V_Rd_s, self.V_Rd_c)


def buegelwiderstand(
    *, alpha: int, a_s: float, s_x: float, s_y: float, d: float,
    f_yd: float, f_cd: float, k_c: float,
) -> Buegelpunkt:
    """
    Fachwerkmodell mit veraenderlicher Neigung der Druckdiagonalen.

    Alles in SI-Basis: Flaechen in m^2, Laengen in m, Festigkeiten in Pa.
    Rueckgabe in N/m::

        V_Rd,s = A_(⌀,V)/(s_x · s_y) · 0.9 · d · f_yd · cot(alpha)
        V_Rd,c = 0.9 · d · k_c · f_cd · sin(alpha) · cos(alpha)

    ``A_(⌀,V)/(s_x · s_y)`` ist der Bewehrungsgehalt: ein Buegelschenkel je
    Rasterfeld. Beide Groessen gelten **je Laufmeter** -- so wie ``V_Ed`` und
    wie der Widerstand ohne Buegel. Die betrachtete Breite ``b`` steht deshalb
    in keiner der beiden Formeln; sie ist der Bezug, auf den sich alle
    Schnittgroessen ohnehin schon beziehen.
    """
    bogen = math.radians(alpha)
    return Buegelpunkt(
        alpha=alpha,
        V_Rd_s=a_s / (s_x * s_y) * 0.9 * d * f_yd / math.tan(bogen),
        V_Rd_c=0.9 * d * k_c * f_cd * math.sin(bogen) * math.cos(bogen),
    )


@dataclass(frozen=True)
class Buegelwerte:
    """
    Was ausser der Neigung und der statischen Hoehe in den Widerstand eingeht.

    Alles in SI-Basis. Steht nach dem Lauf am Nachweis bereit, damit sich der
    Verlauf ueber der Neigung zeichnen laesst -- ohne dass die Oberflaeche die
    Formel ein zweites Mal enthaelt. Dasselbe Muster wie
    :class:`Kurvenbeiwerte` beim Ansatz ohne Buegel.
    """

    a_s: float
    s_x: float
    s_y: float
    f_yd: float
    f_cd: float
    k_c: float


def neigungen(
    *, alpha_min: int, alpha_max: int, **werte: float
) -> List[Buegelpunkt]:
    """Je ganzes Grad im Bereich ein Punkt, einschliesslich der Grenzen."""
    return [buegelwiderstand(alpha=a, **werte)
            for a in range(alpha_min, alpha_max + 1)]


def beste_neigung(punkte: Sequence[Buegelpunkt]) -> Buegelpunkt:
    """
    Die Neigung mit dem groessten Widerstand.

    ``V_Rd,s`` waechst mit flacherer Diagonale, ``V_Rd,c`` faellt dabei --
    das Kleinere von beiden hat sein Groesstes dort, wo sich die beiden
    Aeste treffen. Gesucht wird ganzgradig; bei Gleichstand gilt die
    steilere Neigung, weil sie die Druckdiagonale weniger beansprucht.
    """
    return max(punkte, key=lambda q: (q.V_Rd, q.alpha))


def _statische_hoehe(
    lagen: Sequence[Tuple[float, bool]], h: float, moment_positiv: bool
) -> Optional[float]:
    """
    Statische Hoehe der gezogenen Bewehrung, in m ab der gedrueckten Kante.

    ``lagen`` ist eine Folge von ``(z ab Oberkante, liegt unten)``.

    Bei positivem Moment liegt der Zug unten: gemessen wird von der Oberkante
    zur aeussersten unteren Lage. Bei negativem Moment umgekehrt. **Nur die
    Lagen der gezogenen Seite zaehlen.** Wer alle nimmt, bekommt bei
    einseitiger Bewehrung eine Zahl, die gar keine statische Hoehe ist: eine
    Platte nur mit unterer Bewehrung lieferte fuers negative Moment
    ``h - 261 = 39 mm`` -- den Abstand der Unterkante zur *unteren* Lage.

    ``None``, wenn auf der gezogenen Seite nichts liegt. Dann gibt es kein
    ``d``, und ohne ``d`` keinen Querkraftwiderstand.
    """
    gezogen = [z for z, unten in lagen if unten is moment_positiv]
    if not gezogen:
        return None
    return max(gezogen) if moment_positiv else h - min(gezogen)


@dataclass(frozen=True)
class Querkraftfall:
    """Eine zu pruefende Kombination fuer den Querkraftnachweis."""

    name: str
    V_Ed: Groesse
    M_Ed: Groesse
    N_Ed: Groesse

    @property
    def kennung(self) -> str:
        return kennung_aus(self.name)


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

    hinweis: str = ""
    """Gesetzt, wenn sich gar kein Widerstand bestimmen liess -- siehe
    :attr:`opencivil.core.berechnung.NachweisUrteil.hinweis`."""

    # -- nur mit Buegeln ----------------------------------------------------

    punkte: Tuple[Buegelpunkt, ...] = ()
    """Der Widerstand je ganzem Grad zwischen den beiden Grenzwinkeln."""

    massgebend: Optional[Buegelpunkt] = None
    """Der Punkt mit dem groessten Widerstand -- daraus stammt ``v_Rd``."""

    alpha_min: int = 0
    alpha_max: int = 0
    """Die tatsaechlich verwendeten Grenzen; bei Normalzug angehoben."""

    zug_hebt_alpha: bool = False
    """Ob die Grenzen wegen einer Normalzugkraft angehoben wurden."""


class Querkraft(Nachweis):
    """
    Querkraftwiderstand je Tragrichtung.

    ZWEI ANSAETZE, EINER DAVON GILT:

    * **Ohne Buegel** -- ``V_Rd = k_d · tau_cd · d_v``, der Widerstand des
      Betons allein. Er haengt ueber ``eps_v`` an ``m_Ed`` und ``m_Rd(N_Ed)``
      und damit an der Einwirkung.
    * **Mit Buegeln** -- das Fachwerkmodell aus :func:`buegelwiderstand`. Der
      Betonanteil des ersten Ansatzes entfaellt dann vollstaendig; massgebend
      ist das Kleinere aus Buegel- und Druckdiagonalenwiderstand, gesucht
      ueber die guenstigste Neigung.

    Welcher gilt, entscheidet allein, ob die Platte eine Querkraftbewehrung
    traegt -- nicht eine Einstellung daneben.
    """

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

        self.buegel = (querschnitt.querkraftbewehrung
                       if querschnitt.hat_buegel else None)
        """Die Bügel dieser Platte -- ``None`` heisst: der Ansatz ohne."""

        self.buegelwerte: Optional[Buegelwerte] = None
        """Die geloesten Eingaenge des Bügelansatzes, nach dem Lauf."""

        self.beiwerte: Optional[Kurvenbeiwerte] = None
        """
        Die geloesten Eingaenge, nach dem Lauf. Fuer :meth:`kurve`.

        Ein Ergebnis des Laufs, das ein anderer braucht -- wie
        :attr:`BiegungNormalkraft.bei_normalkraft`. Nicht zu verwechseln mit
        Zwischenwerten, die zwischen eigenen Methoden gereicht werden; die
        gehen durch die Argumentliste.
        """

        # Symbole der Baustoffkennwerte -- mit Sortenindex, sobald mehrere
        # Betone oder Staehle im Projekt sind. Sonst stuende f_yd zweimal mit
        # verschiedenen Zahlen im selben Bericht.
        self.s_f_yd = mit_index("f_{yd}", self.posten[0][0].stahl.symbol_index)
        self.s_E_s = mit_index("E_s", self.posten[0][0].stahl.symbol_index)
        self.s_tau_cd = mit_index(r"\tau_{cd}", querschnitt.beton.symbol_index)
        self.s_f_ck = mit_index("f_{ck}", querschnitt.beton.symbol_index)
        self.s_f_cd = mit_index("f_{cd}", querschnitt.beton.symbol_index)
        self.s_f_yd_V = mit_index(
            "f_{yd}", self.buegel.stahl.symbol_index if self.buegel else "")

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
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: WertDef(
                id=f"{basis}.{f.kennung}.erfuellungsgrad",
                symbol=rf"\alpha_{{eff,V,{r},{als_text(f.name)}}}",
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
                symbol=f"V_{{Rd,{r}}}",
                einheit=KN_PRO_M,
                beschreibung=f"Querkraftwiderstand {richtung.beschriftung} – {f.name}",
                referenz="SIA 262:2025, 4.3.3.2.1",
                stellen=1,
            )
            for f in self.faelle
        }

        bezuege = [
            Eingabebezug("h", querschnitt.id_von("h")),
        ]
        for lage, art, _, as_id, z_id in self.posten:
            bezuege.append(Eingabebezug(f"z_{lage.nummer}{art.kuerzel}", z_id))

        if self.buegel is None:
            stahl = self.posten[0][0].stahl
            bezuege += [
                Eingabebezug("D_max", querschnitt.id_von("D_max")),
                Eingabebezug("einlagenhoehe", querschnitt.id_von("einlagenhoehe")),
                Eingabebezug("f_ck", querschnitt.beton.id_von("f_ck")),
                Eingabebezug("tau_cd", querschnitt.beton.id_von("tau_cd")),
                Eingabebezug("f_yd", stahl.id_von("f_yd")),
                Eingabebezug("E_s", stahl.id_von("E_s")),
            ]
            # Der Momentenwiderstand bei der wirkenden Normalkraft kommt aus dem
            # M-N-Nachweis -- je Fall einer. Als Eingang statt als mitgegebene Zahl,
            # damit die Abhaengigkeit im Graphen steht und die Rueckverfolgung sie
            # zeigt. Mit Buegeln geht er nicht ein; ihn trotzdem anzufordern
            # haenge eine Interpolation in die Herleitung, die dort nichts erklaert.
            for f in self.faelle:
                bezuege.append(Eingabebezug(
                    f"m_Rd_{f.kennung}", mn_nachweis.d_m_rd[f.name].id))
        else:
            # Die Reihenfolge der Eingaenge ist die Reihenfolge, in der der
            # Loeser sie beschafft -- und damit die Reihenfolge der Bloecke in
            # der Mitschrift. Die fuenf Angaben zur Buegelbewehrung stehen
            # deshalb zusammen und der Buegelquerschnitt dahinter: stuende er
            # dazwischen, zerrisse er den Kasten, in dem sie gemeinsam stehen
            # sollen.
            bezuege += [
                Eingabebezug("b", querschnitt.id_breite(richtung)),
                Eingabebezug("k_c", querschnitt.id_von("k_c")),
                Eingabebezug("f_cd", querschnitt.beton.id_von("f_cd")),
                Eingabebezug("f_yd_V", self.buegel.stahl.id_von("f_yd")),
                Eingabebezug("phi_V", querschnitt.id_von("querkraft.phi")),
                Eingabebezug("s_x", querschnitt.id_von("querkraft.s_x")),
                Eingabebezug(
                    "menge_y",
                    querschnitt.id_von("querkraft.s_y" if self.buegel.ueber_abstand_y
                                       else "querkraft.n_y")),
                Eingabebezug("alpha_min", querschnitt.id_von("querkraft.alpha_min")),
                Eingabebezug("alpha_max", querschnitt.id_von("querkraft.alpha_max")),
                Eingabebezug("a_s_V", querschnitt.id_von("querkraft.a_s")),
            ]

        super().__init__(
            basis,
            ausgaben=list(self.d_ausnutzung.values()) + list(self.d_v_rd.values()),
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
        if self.buegel is not None:
            return self._mit_buegeln(e, p)
        return self._ohne_buegel(e, p)

    def _ohne_buegel(self, e: Eingaben, p: Protokoll):
        h = e.g("h").si
        tau_cd = e.g("tau_cd")
        f_yd = e.g("f_yd").si
        E_s = e.g("E_s").si
        einlage = e.g("einlagenhoehe").si
        m_rd = {f.name: abs(e.g(f"m_Rd_{f.kennung}").si) for f in self.faelle}
        # Je Posten die Tiefe und auf welcher Seite er liegt -- ohne das
        # laesst sich die gezogene Bewehrung nicht von der gedrueckten trennen.
        lagen = [(e.g(f"z_{l.nummer}{a.kuerzel}").si, l.von_unten)
                 for l, a, _, _, _ in self.posten]

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
            rf"\left(\frac{{60}}{{{self.s_f_ck}}}\right)^{{2}}\right]}}\right]"
            "\n= "
            rf"\max\left[{K_G_MINDEST:.2f};\ \frac{{48}}"
            rf"{{16 + {D_max.formatiert(0, MM)} \cdot \min\left[1.0;\ "
            rf"\left(\frac{{60}}{{{f_ck.formatiert(0, N_PRO_MM2)}}}\right)^{{2}}\right]}}\right]"
            rf" = \max\left[{K_G_MINDEST:.2f};\ {roh:.3f}\right] = {k_g:.3f}",
            titel="Beiwert der Gesteinskörnung", referenz="SIA 262:2025, 4.3.3.2.1")

        self.beiwerte = Kurvenbeiwerte(
            h=h, lagen=tuple(lagen), einlage=einlage, tau_cd=tau_cd.si,
            f_yd=f_yd, E_s=E_s, k_g=k_g)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        self.ergebnisse = []

        for fall in self.faelle:
            erg = self._einen_fall(fall, h, tau_cd, f_yd, E_s, einlage, k_g,
                                   m_rd[fall.name], lagen)
            self.ergebnisse.append(erg)
            self._protokoll_fall(p, erg, h, tau_cd, f_yd, E_s, einlage, k_g)
            self._eintragen(erg, ergebnis, urteile)

        return ergebnis, urteile

    def _eintragen(
        self, erg: Querkraftergebnis, ergebnis: Dict[str, Groesse],
        urteile: List[NachweisUrteil],
    ) -> None:
        """
        Ausgaben und Urteil eines Falls -- fuer beide Ansaetze dieselben.

        Was ein Querkraftnachweis herausgibt, haengt nicht davon ab, wie der
        Widerstand zustande kam. Zweimal geschrieben liefen die beiden Faelle
        frueher oder spaeter auseinander.
        """
        fall = erg.fall
        ergebnis[self.d_v_rd[fall.name].id] = Groesse.aus_si(erg.v_Rd, KN_PRO_M)
        ergebnis[self.d_ausnutzung[fall.name].id] = Groesse(
            min(erg.erfuellungsgrad, 1e9), EINHEITSLOS)

        urteile.append(NachweisUrteil(
            name=f"Querkraft {self.richtung.value} – {fall.name}",
            art="V",
            langname="Querkraft",
            fall=fall.name,
            erfuellt=erg.erfuellt,
            erfuellungsgrad=Groesse(erg.erfuellungsgrad, EINHEITSLOS),
            begruendung=erg.begruendung,
            hinweis=erg.hinweis,
            # Das Vorzeichen der Querkraft spielt keine Rolle -- verglichen
            # wird der Betrag. Also steht auch der Betrag da; sonst teilte
            # der Leser den Widerstand durch eine negative Zahl und bekaeme
            # etwas anderes als den danebenstehenden Erfuellungsgrad. Die
            # Betragsstriche stehen trotzdem nicht am Symbol: sie sagen
            # nichts, was die Zahl daneben nicht schon zeigt.
            einwirkung=WertDef(
                id=f"{self.id}.{fall.kennung}.V_Ed",
                symbol=rf"V_{{Ed,{self.richtung.value}}}",
                einheit=KN_PRO_M, beschreibung="Einwirkung", stellen=1,
            ).belegen(Groesse.aus_si(abs(fall.V_Ed.si), KN_PRO_M)),
            # Der Widerstand gilt nur unter genau dieser Einwirkung -- das
            # gehoert ins Symbol, sonst liest sich V_Rd wie ein Kennwert des
            # Querschnitts.
            widerstand=WertDef(
                id=self.d_v_rd[fall.name].id,
                symbol=self._widerstandssymbol(fall),
                einheit=KN_PRO_M, beschreibung="Widerstand", stellen=1,
            ).belegen(Groesse.aus_si(erg.v_Rd, KN_PRO_M)),
        ))

    # -- Mit Querkraftbewehrung ---------------------------------------------

    def _mit_buegeln(self, e: Eingaben, p: Protokoll):
        """
        Fachwerkmodell: Bügel gegen Druckdiagonale, über die Neigung gesucht.

        Der Betonanteil des bügellosen Ansatzes entfällt hier vollständig --
        beides zu addieren wäre ein anderes Modell, und dieses Werkzeug rechnet
        nur, was es auch herleitet.
        """
        h = e.g("h").si
        b = e.g("b").si
        a_s = e.g("a_s_V").si
        s_x = e.g("s_x").si
        f_yd = e.g("f_yd_V").si
        f_cd = e.g("f_cd").si
        k_c = e.g("k_c").si
        lagen = [(e.g(f"z_{l.nummer}{a.kuerzel}").si, l.von_unten)
                 for l, a, _, _, _ in self.posten]

        # Die Menge in y: entweder eine Teilung oder eine Stabzahl über die
        # betrachtete Breite. Aus der Zahl wird hier eine Teilung -- die Formel
        # kennt nur Teilungen, und die Umrechnung steht in der Herleitung.
        menge_y = e.g("menge_y")
        ueber_teilung = self.buegel.ueber_abstand_y
        s_y = menge_y.si if ueber_teilung else (b / menge_y.si if menge_y.si else 0.0)

        self.buegelwerte = Buegelwerte(
            a_s=a_s, s_x=s_x, s_y=s_y, f_yd=f_yd, f_cd=f_cd, k_c=k_c)

        self._protokoll_ansatz_buegel(p, e, s_y)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        self.ergebnisse = []

        for fall in self.faelle:
            erg = self._einen_fall_buegel(
                fall, h=h, lagen=lagen, a_s=a_s, s_x=s_x, s_y=s_y,
                f_yd=f_yd, f_cd=f_cd, k_c=k_c, ueber_teilung=ueber_teilung)
            self.ergebnisse.append(erg)
            self._protokoll_fall_buegel(p, erg, a_s, s_x, s_y, f_yd, f_cd, k_c)
            self._eintragen(erg, ergebnis, urteile)

        return ergebnis, urteile

    def _einen_fall_buegel(
        self, fall: Querkraftfall, *, h: float,
        lagen: Sequence[Tuple[float, bool]], a_s: float, s_x: float,
        s_y: float, f_yd: float, f_cd: float, k_c: float, ueber_teilung: bool,
    ) -> Querkraftergebnis:
        erg = Querkraftergebnis(fall=fall)
        M_Ed, N_Ed, V_Ed = fall.M_Ed.si, fall.N_Ed.si, fall.V_Ed.si

        # Eine Stabzahl in y bezieht sich auf die betrachtete Breite. In
        # x-Richtung ergibt das eine Teilung; in y-Richtung liefe die Breite
        # laengs der Traglinie mit und die Formel haette keinen Bezug mehr.
        if not ueber_teilung and self.richtung is Richtung.Y:
            erg.begruendung = erg.hinweis = (
                "Widerstand in y-Richtung nicht berechenbar, wegen "
                "Bügeldefinition: in y ist eine Stabzahl über die betrachtete "
                "Breite angegeben statt einer Teilung. Für einen Nachweis in "
                "y-Richtung braucht es dort eine Teilung in mm.")
            return erg

        hoehen = _statische_hoehe(lagen, h, M_Ed >= 0)
        if hoehen is None:
            seite = "unten" if M_Ed >= 0 else "oben"
            erg.begruendung = erg.hinweis = (
                f"Auf der gezogenen Seite ({seite}) liegt in dieser Richtung "
                f"keine Bewehrung. Ohne statische Höhe gibt es keinen "
                f"Querkraftwiderstand: V_Rd = 0.")
            return erg
        erg.d = erg.d_v = hoehen

        erg.zug_hebt_alpha = N_Ed > 0.0
        erg.alpha_min, erg.alpha_max = self.buegel.grenzen(erg.zug_hebt_alpha)
        erg.punkte = tuple(neigungen(
            alpha_min=erg.alpha_min, alpha_max=erg.alpha_max,
            a_s=a_s, s_x=s_x, s_y=s_y, d=erg.d,
            f_yd=f_yd, f_cd=f_cd, k_c=k_c))
        erg.massgebend = beste_neigung(erg.punkte)
        erg.v_Rd = erg.massgebend.V_Rd

        erg.erfuellungsgrad = float("inf") if V_Ed == 0 else abs(erg.v_Rd) / abs(V_Ed)
        erg.erfuellt = erg.erfuellungsgrad >= 1.0
        massgebend = ("die Bügel" if erg.massgebend.V_Rd_s <= erg.massgebend.V_Rd_c
                      else "die Druckdiagonale")
        erg.begruendung = (
            f"Günstigste Neigung α = {erg.massgebend.alpha}°: "
            f"V_Rd,s = {erg.massgebend.V_Rd_s / 1e3:.1f} kN/m, "
            f"V_Rd,c = {erg.massgebend.V_Rd_c / 1e3:.1f} kN/m. "
            f"Massgebend {massgebend}.")
        return erg

    # -- Kurve --------------------------------------------------------------

    def kurve(self, N_Ed: float) -> dict:
        """
        Der Querkraftwiderstand ueber dem Moment, bei festgehaltener Normalkraft.

        **Ein** Diagramm je Tragrichtung, mit vorzeichenbehafteter Waagrechten:
        rechts das positive Moment (Zug unten), links das negative (Zug oben).
        Frueher waren das zwei Bilder; nebeneinander liessen sie sich schlecht
        vergleichen, obwohl sie dieselbe Platte beschreiben.

        Die beiden Aeste sind getrennte Linienzuege und treffen sich bei
        ``M_Ed = 0`` nicht unbedingt: sie haben verschiedene statische Hoehen,
        also auch verschiedene Widerstaende bei verschiedwindendem Moment. Das
        ist kein Zeichenfehler, sondern die Platte.

        Je Ast fuenfzig Stuetzstellen von null bis ``m_Rd + 20 kNm``. Der
        Bereich jenseits von ``m_Rd`` ist der eigentliche Zweck: dort faellt der
        Widerstand, weil die Bewehrung fliesst (siehe :func:`widerstand`).

        Gerechnet wird mit derselben Funktion wie im Nachweis. Die Kurve kann
        also nicht etwas anderes zeigen als die Punkte, die darauf liegen.

        :param N_Ed: eingestellte Normalkraft in N, Zug positiv.
        """
        return {"N_Ed": N_Ed,
                "aeste": [ast for ast in (self._ast(N_Ed, True),
                                          self._ast(N_Ed, False)) if ast]}

    def _ast(self, N_Ed: float, moment_positiv: bool) -> Optional[dict]:
        """
        Ein Ast der Kurve. ``None``, wenn es ihn nicht gibt.

        Es gibt ihn nicht, wenn auf der gezogenen Seite keine Bewehrung liegt
        oder die Normalkraft ausserhalb der Resistenzlinie faellt -- in beiden
        Faellen waere jeder gezeichnete Widerstand erfunden.
        """
        if self.beiwerte is None:
            return None
        hoehen = self.beiwerte.hoehen(moment_positiv)
        if hoehen is None:
            return None
        m_Rd = self.mn.moment_bei(N_Ed, positiv=moment_positiv)
        if not m_Rd or m_Rd <= 0.0:
            return None

        d, d_v = hoehen
        bis = m_Rd + KURVENZUGABE

        # Die fuenfzig Stellen liegen gleichmaessig, treffen ``m_Rd`` aber nur
        # zufaellig. Beide Seiten des Sprungs kommen darum eigens dazu: sonst
        # zeigte die Marke «v_Rd bei M_Ed = m_Rd» den Wert des Nachbarpunkts,
        # und der Absatz waere schraeg statt senkrecht.
        stellen = sorted(
            {bis * i / (KURVENPUNKTE - 1) for i in range(KURVENPUNKTE)}
            | {m_Rd, m_Rd + SPRUNGSCHRITT})

        vz = 1.0 if moment_positiv else -1.0
        punkte = []
        for M_Ed in stellen:
            p = widerstand(
                M_Ed=M_Ed, N_Ed=N_Ed, h=self.beiwerte.h, d=d, d_v=d_v,
                tau_cd=self.beiwerte.tau_cd, f_yd=self.beiwerte.f_yd,
                E_s=self.beiwerte.E_s, k_g=self.beiwerte.k_g, m_Rd=m_Rd)
            punkte.append((vz * M_Ed, p.v_Rd, p.plastisch))

        return {"punkte": punkte, "m_Rd": vz * m_Rd, "d": d, "d_v": d_v,
                "moment_positiv": moment_positiv}

    def neigungsverlauf(self, d: float, von: int, bis: int) -> List[Buegelpunkt]:
        """
        Der Widerstand ueber der Neigung -- fuer das Diagramm.

        Ueber dieselbe Funktion wie der Nachweis selbst, nur ueber einen
        weiteren Bereich: gezeichnet wird auch ausserhalb der beiden Grenzen,
        dort blass. Zwei Rechenwege fuer dieselbe Kurve liefen auseinander.
        """
        if self.buegelwerte is None:
            return []
        w = self.buegelwerte
        return neigungen(
            alpha_min=von, alpha_max=bis, d=d,
            a_s=w.a_s, s_x=w.s_x, s_y=w.s_y,
            f_yd=w.f_yd, f_cd=w.f_cd, k_c=w.k_c)

    def _widerstandssymbol(self, fall: Querkraftfall) -> str:
        """``V_Rd(M_Ed = 100 kNm, N_Ed = -300 kN)`` -- der Widerstand ist bedingt."""
        r = self.richtung.value
        return (rf"V_{{Rd,{r}}}(M_{{Ed}} = {fall.M_Ed.als_latex(1, KNM)},\ "
                rf"N_{{Ed}} = {fall.N_Ed.als_latex(1, KN)})")

    def _einen_fall(
        self, fall: Querkraftfall, h: float, tau_cd: Groesse,
        f_yd: float, E_s: float, einlage: float, k_g: float,
        m_Rd: float, lagen: Sequence[Tuple[float, bool]],
    ) -> Querkraftergebnis:
        erg = Querkraftergebnis(fall=fall)
        M_Ed, N_Ed, V_Ed = fall.M_Ed.si, fall.N_Ed.si, fall.V_Ed.si
        erg.m_Rd = m_Rd

        # Ohne Bewehrung auf der gezogenen Seite gibt es kein d -- und ohne d
        # keinen Querkraftwiderstand. Frueher wurde hier die gedrueckte Seite
        # herangezogen und lieferte eine Zahl, die keine statische Hoehe ist.
        hoehen = _statische_hoehe(lagen, h, M_Ed >= 0)
        if hoehen is None:
            seite = "unten" if M_Ed >= 0 else "oben"
            erg.erfuellungsgrad = 0.0
            erg.erfuellt = False
            erg.begruendung = erg.hinweis = (
                f"Auf der gezogenen Seite ({seite}) liegt in dieser Richtung "
                f"keine Bewehrung. Ohne statische Höhe gibt es keinen "
                f"Querkraftwiderstand: V_Rd = 0.")
            return erg
        erg.d = hoehen
        erg.d_v = erg.d - einlage if (h / 6.0 < einlage < erg.d) else erg.d

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
            erg.begruendung = erg.hinweis = punkt.grund
            return erg

        erg.erfuellungsgrad = float("inf") if V_Ed == 0 else abs(erg.v_Rd) / abs(V_Ed)
        erg.erfuellt = erg.erfuellungsgrad >= 1.0
        erg.begruendung = (
            f"V_Rd = k_d · τ_cd · d_v = {erg.k_d:.3f} · "
            f"{tau_cd.formatiert(2, N_PRO_MM2)} N/mm² · {erg.d_v * 1e3:.0f} mm "
            f"= {erg.v_Rd / 1e3:.1f} kN/m.")
        return erg


    # -- Mitschrift mit Bügeln ----------------------------------------------

    def _protokoll_ansatz_buegel(
        self, p: Protokoll, e: Eingaben, s_y: float
    ) -> None:
        p.titel(f"Querkraft – {self.richtung.beschriftung}")
        p.text(
            "Querkraftwiderstand mit Querkraftbewehrung, Fachwerkmodell mit "
            "veränderlicher Neigung der Druckdiagonalen. Massgebend ist das "
            "Kleinere aus dem Widerstand der Bügel und dem der Druckdiagonalen; "
            "der Betonanteil ohne Bügel geht nicht zusätzlich ein."
        )
        p.gleichung(
            rf"V_{{Rd,s}} = \frac{{A_{{\varnothing,V}}}}{{s_{{V,x}} \cdot s_{{V,y}}}} "
            rf"\cdot 0.9 \cdot d \cdot {self.s_f_yd_V} \cdot \cot\alpha \qquad "
            rf"V_{{Rd,c}} = 0.9 \cdot d \cdot k_c \cdot {self.s_f_cd} "
            r"\cdot \sin\alpha \cdot \cos\alpha",
            titel="Ansatz", referenz="SIA 262:2025, 4.3.3.4")
        p.text(
            "Beide Anteile gelten je Laufmeter, wie die Querkraft selbst. "
            "Gesucht wird ganzgradig zwischen α_min und α_max die Neigung mit "
            f"dem grössten Widerstand V_Rd = min(V_Rd,s; V_Rd,c). Bei einer "
            f"Normalzugkraft steilt sich die Druckdiagonale auf: α_min wird "
            f"dann auf {ALPHA_ZUG}° gesetzt und α_max notfalls mitgehoben."
        )
        if not self.buegel.ueber_abstand_y:
            n_y = e.g("menge_y")
            b = e.g("b")
            p.gleichung(
                r"s_{V,y} = \frac{b}{n_{V,y}}"
                rf" = \frac{{{b.formatiert(0, MM)}}}{{{n_y.formatiert(0)}}}"
                rf" = {s_y * 1e3:.1f}\,\mathrm{{mm}}",
                titel="Teilung in y aus der Stabzahl")

    def _protokoll_fall_buegel(
        self, p: Protokoll, erg: Querkraftergebnis, a_s: float, s_x: float,
        s_y: float, f_yd: float, f_cd: float, k_c: float,
    ) -> None:
        fall = erg.fall
        p.titel(f"Nachweis – {fall.name}", ebene=3)
        p.gleichung(
            rf"V_{{Ed}} = {fall.V_Ed.als_latex(1, KN_PRO_M)} \qquad "
            rf"M_{{Ed}} = {fall.M_Ed.als_latex(1, KNM)} \qquad "
            rf"N_{{Ed}} = {fall.N_Ed.als_latex(1, KN)}",
            titel="Einwirkung")

        if erg.massgebend is None:
            p.text(erg.begruendung)
            return

        seite = "unten" if fall.M_Ed.si >= 0 else "oben"
        p.gleichung(
            rf"d = {erg.d * 1e3:.1f}\,\mathrm{{mm}}",
            titel=f"Statische Höhe der gezogenen Bewehrung ({seite})")

        if erg.zug_hebt_alpha:
            p.text(
                f"N_Ed = {fall.N_Ed.formatiert(1, KN)} kN ist eine Zugkraft – "
                f"die Grenzen der Neigung werden auf α_min = {erg.alpha_min}° "
                f"und α_max = {erg.alpha_max}° angehoben.")

        q = erg.massgebend
        p.text(
            f"Zwischen α = {erg.alpha_min}° und α = {erg.alpha_max}° ganzgradig "
            f"durchgerechnet; den grössten Widerstand liefert α = {q.alpha}°.")

        p.gleichung(
            rf"V_{{Rd,s}} = \frac{{A_{{\varnothing,V}}}}"
            rf"{{s_{{V,x}} \cdot s_{{V,y}}}} \cdot 0.9 \cdot d \cdot "
            rf"{self.s_f_yd_V} \cdot \cot\alpha"
            "\n= "
            rf"\frac{{{a_s * 1e6:.1f}\,\mathrm{{mm}}^{{2}}}}"
            rf"{{{s_x * 1e3:.0f}\,\mathrm{{mm}} \cdot {s_y * 1e3:.0f}\,\mathrm{{mm}}}} "
            rf"\cdot 0.9 \cdot {erg.d * 1e3:.1f}\,\mathrm{{mm}} \cdot "
            rf"{f_yd / 1e6:.0f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}} \cdot "
            rf"\cot {q.alpha}^{{\circ}}"
            rf" = {q.V_Rd_s / 1e3:.1f}\,\mathrm{{kN}}/\mathrm{{m}}",
            titel="Widerstand der Bügel")

        p.gleichung(
            rf"V_{{Rd,c}} = 0.9 \cdot d \cdot k_c \cdot {self.s_f_cd} "
            r"\cdot \sin\alpha \cdot \cos\alpha"
            "\n= "
            rf"0.9 \cdot {erg.d * 1e3:.1f}\,\mathrm{{mm}} \cdot {k_c:.2f} \cdot "
            rf"{f_cd / 1e6:.1f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}} \cdot "
            rf"\sin {q.alpha}^{{\circ}} \cdot \cos {q.alpha}^{{\circ}}"
            rf" = {q.V_Rd_c / 1e3:.1f}\,\mathrm{{kN}}/\mathrm{{m}}",
            titel="Widerstand der Druckdiagonalen")

        p.gleichung(
            rf"V_{{Rd}} = \min\left[V_{{Rd,s}};\ V_{{Rd,c}}\right] = "
            rf"\min\left[{q.V_Rd_s / 1e3:.1f}\,\mathrm{{kN}}/\mathrm{{m}};\ "
            rf"{q.V_Rd_c / 1e3:.1f}\,\mathrm{{kN}}/\mathrm{{m}}\right]"
            rf" = {erg.v_Rd / 1e3:.1f}\,\mathrm{{kN}}/\mathrm{{m}}",
            titel="Querkraftwiderstand")

        self._protokoll_grad(p, erg)

    def _protokoll_grad(self, p: Protokoll, erg: Querkraftergebnis) -> None:
        """Die letzte Zeile jedes Falls -- für beide Ansätze dieselbe."""
        r = self.richtung.value
        zustand = r"\text{erfüllt}" if erg.erfuellt else r"\text{NICHT erfüllt}"
        grad = grad_als_text(erg.erfuellungsgrad, erg.erfuellt, latex=True)
        p.gleichung(
            rf"\alpha_{{eff,V,{r}}} = \frac{{V_{{Rd}}}}{{\left|V_{{Ed}}\right|}} = "
            rf"\frac{{{erg.v_Rd / 1e3:.1f}\,\mathrm{{kN}}/\mathrm{{m}}}}"
            rf"{{{abs(erg.fall.V_Ed.si) / 1e3:.1f}\,\mathrm{{kN}}/\mathrm{{m}}}} = {grad}"
            rf" \quad \Rightarrow \quad {zustand}"
            if erg.fall.V_Ed.si else
            rf"\alpha_{{eff,V,{r}}} = \frac{{V_{{Rd}}}}{{\left|V_{{Ed}}\right|}} = {grad}"
            rf" \quad \Rightarrow \quad {zustand}",
            titel="Erfüllungsgrad")

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben) -> None:
        p.titel(f"Querkraft – {self.richtung.beschriftung}")
        p.text(
            "Querkraftwiderstand ohne Querkraftbewehrung. Massgebend sind die "
            "statische Höhe der gezogenen Bewehrung, die Grösstkorngrösse und "
            "die Dehnung auf halber Höhe."
        )
        p.gleichung(
            rf"V_{{Rd}} = k_d \cdot {self.s_tau_cd} \cdot d_v \qquad "
            r"k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g}",
            titel="Ansatz", referenz="SIA 262:2025, 4.3.3.2.1")
        p.gleichung(
            r"m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} \qquad "
            rf"\varepsilon_v = \frac{{{self.s_f_yd} \cdot \left(\left|m_{{Ed}}\right| "
            r"- m_{Dd}\right)}"
            rf"{{{self.s_E_s} \cdot \left(\left|m_{{Rd}}(N_{{Ed}})\right| - m_{{Dd}}\right)}}",
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
                p, bei_n, basis=f"{self.id}.{kennung_aus(fall.name)}",
                titel=f"Momentenwiderstand bei N_Ed = {N_Ed / 1e3:.1f} kN")

        if erg.eps_v == 0.0:
            p.text(
                f"m_Ed = {abs(M_Ed) / 1e3:.1f} kNm/m liegt nicht über "
                f"m_Dd = {erg.m_Dd / 1e3:.1f} kNm/m – der Querschnitt bleibt "
                f"ungerissen, ε_v = 0.")
        else:
            p.gleichung(
                rf"\varepsilon_v = \frac{{{self.s_f_yd} \cdot \left(\left|m_{{Ed}}\right| "
                r"- m_{Dd}\right)}"
                rf"{{{self.s_E_s} \cdot \left(\left|m_{{Rd}}(N_{{Ed}})\right| - m_{{Dd}}\right)}}"
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
            rf"{self._widerstandssymbol(fall)} = k_d \cdot {self.s_tau_cd} \cdot d_v"
            "\n= "
            rf"{erg.k_d:.4f} \cdot {tau_cd.in_einheit(N_PRO_MM2):.4f}\,"
            rf"\mathrm{{N}}/\mathrm{{mm}}^{{2}} \cdot {erg.d_v * 1e3:.1f}\,\mathrm{{mm}}"
            rf" = {erg.v_Rd / 1e3:.1f}\,\mathrm{{kN}}/\mathrm{{m}}",
            titel="Querkraftwiderstand", referenz="SIA 262:2025, 4.3.3.2.1")

        self._protokoll_grad(p, erg)
