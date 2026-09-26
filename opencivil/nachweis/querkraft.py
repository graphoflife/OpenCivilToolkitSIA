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
in Millimeter ein, ``f_ck`` in N/mm^2. ``k_g`` laeuft deshalb ueber
:func:`opencivil.core.einheiten.empirisch`, das diese Voraussetzung erzwingt;
``k_d`` rechnet ``d`` in Millimeter um, und die Herleitung sagt es dazu.
``V_Rd`` ergibt sich in N/mm, also kN/m -- eine Querkraft je Laufmeter.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Eingabebezug, Eingaben, Nachweis, NachweisUrteil, grad_def, grad_formel,
)
from opencivil.core.einheiten import (
    EINHEITSLOS, GRAD, KN, KN_PRO_M, KNM, MM, N_PRO_MM2, EmpirischesErgebnis,
    Groesse, empirisch,
)
from opencivil.core.latex import als_text
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef, kennung_aus
from opencivil.nachweis.biegung_normalkraft import protokoll_interpolation
from opencivil.querschnitt.platte import (
    ALPHA_ZUG, Plattenquerschnitt, Richtung, protokoll_statische_hoehe,
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
            grund=(f"m_Rd(N_Ed) = {m_Rd / 1e3:.1f} kNm ≤ m_Dd = {m_Dd / 1e3:.1f} kNm "
                   f"→ V_Rd nicht bestimmbar."))
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
    i = _zuglage(lagen, moment_positiv)
    if i is None:
        return None
    z = lagen[i][0]
    return z if moment_positiv else h - z


def _zuglage(
    lagen: Sequence[Tuple[float, bool]], moment_positiv: bool
) -> Optional[int]:
    """Die aeusserste Lage der gezogenen Seite, als Index in ``lagen``."""
    gezogen = [i for i, (_, unten) in enumerate(lagen) if unten is moment_positiv]
    if not gezogen:
        return None
    return (max if moment_positiv else min)(gezogen, key=lambda i: lagen[i][0])


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


#: Der Fall eines Querkraftnachweises ohne Querkraft: er rechnet still, nur
#: fuer das Diagramm -- die M-V-Kurve und der Verlauf ueber die Neigung
#: brauchen die Beiwerte, die erst im Lauf entstehen. Ohne Einwirkung kein
#: Urteil und kein Punkt im Bild; M = 0 misst d fuer das positive Moment.
NUR_KURVE = Querkraftfall(name="ohne Einwirkung", V_Ed=Groesse(0.0, KN_PRO_M),
                          M_Ed=Groesse(0.0, KNM), N_Ed=Groesse(0.0, KN))


@dataclass
class Querkraftergebnis:
    """Alle Zwischenwerte eines Falls, damit die Herleitung vollstaendig ist."""

    fall: Querkraftfall
    zuglage: Optional[int] = None
    """Die aeusserste gezogene Lage, als Index in den Posten -- aus ihr kommt ``d``."""

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

    THEMA = "Querkraft"

    def __init__(
        self,
        querschnitt: Plattenquerschnitt,
        faelle: Sequence[Querkraftfall],
        richtung: Richtung,
        mn_nachweis,
    ) -> None:
        self.posten = querschnitt.posten_in_richtung(richtung)
        if not self.posten:
            raise ValueError(
                f"Querschnitt '{querschnitt.name}': in {richtung.beschriftung} liegt "
                f"keine Bewehrung.")
        self.querschnitt = querschnitt
        self.richtung = richtung
        # Ohne Fall still und mit dem Nullfall -- siehe NUR_KURVE.
        self.faelle = list(faelle) or [NUR_KURVE]
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
            f.name: grad_def(
                f"{basis}.{f.kennung}.erfuellungsgrad",
                rf"\alpha_{{eff,V,{r},{als_text(f.name)}}}",
                f"Erfüllungsgrad Querkraft {richtung.beschriftung} – {f.name}",
                "SIA 262:2025, 4.3.3.2",
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
            # Der Nullfall hat keine Kombination; ohne Normalkraft gilt der
            # Eckwert M_Rd(N = 0).
            for f in self.faelle:
                m_rd = (mn_nachweis.d_eckwerte["M_Rd_N0_pos"] if f == NUR_KURVE
                        else mn_nachweis.d_m_rd[f.name])
                bezuege.append(Eingabebezug(f"m_Rd_{f.kennung}", m_rd.id))
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
        self.still = not faelle

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
        lagen = self._lagen(e)

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
        beiwert = self._protokoll_k_g(p, e, k_g_erg)

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
            self._protokoll_fall(p, e, erg, beiwert)
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
            erg.erfuellungsgrad, EINHEITSLOS)
        # Der Nullfall ist nur das Ziel des Laufs. Ein Urteil von ihm meldete
        # die Zusammenfassung als ausgeschalteten Mangel, sobald V_Rd = 0 ist
        # (Zugseite ohne Bewehrung) -- ohne dass es eine Querkraft gibt.
        if fall is NUR_KURVE:
            return

        urteile.append(NachweisUrteil(
            name=f"Querkraft {self.richtung.value} – {fall.name}",
            art="V",
            ziel=self.d_ausnutzung[fall.name].id,
            langname=self.thema,
            fall=fall.name,
            erfuellt=erg.erfuellt,
            erfuellungsgrad=Groesse(erg.erfuellungsgrad, EINHEITSLOS),
            begruendung=erg.begruendung,
            hinweis=erg.hinweis,
            einwirkung=self._einwirkung(fall),
            widerstand=self._widerstand(erg),
        ))

    def _einwirkung(self, fall: Querkraftfall) -> Wert:
        """
        Die Querkraft als Betrag -- fuer Urteil und Erfuellungsgrad dieselbe.

        Das Vorzeichen spielt keine Rolle, verglichen wird der Betrag. Also
        steht auch der Betrag da; sonst teilte der Leser den Widerstand durch
        eine negative Zahl und bekaeme etwas anderes als den danebenstehenden
        Erfuellungsgrad. Die Betragsstriche stehen trotzdem nicht am Symbol:
        sie sagen nichts, was die Zahl daneben nicht schon zeigt.
        """
        return Zwischenwerte(f"{self.id}.{fall.kennung}").wert(
            "V_Ed", rf"V_{{Ed,{self.richtung.value}}}",
            Groesse.aus_si(abs(fall.V_Ed.si), KN_PRO_M), beschreibung="Einwirkung")

    def _widerstand(self, erg: Querkraftergebnis) -> Wert:
        """
        Der Widerstand eines Falls -- fuer Urteil und Herleitung derselbe.

        Er gilt nur unter genau dieser Einwirkung; das gehoert ins Symbol,
        sonst liest sich V_Rd wie ein Kennwert des Querschnitts.
        """
        return Zwischenwerte(f"{self.id}.{erg.fall.kennung}").wert(
            "v_Rd", self._widerstandssymbol(erg.fall),
            Groesse.aus_si(erg.v_Rd, KN_PRO_M), beschreibung="Widerstand")

    def _lagen(self, e: Eingaben) -> List[Tuple[float, bool]]:
        """
        Je Posten die Tiefe und auf welcher Seite er liegt -- ohne das laesst
        sich die gezogene Bewehrung nicht von der gedrueckten trennen.
        """
        return [(e.g(f"z_{l.nummer}{a.kuerzel}").si, l.von_unten)
                for l, a, _, _, _ in self.posten]

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
        lagen = self._lagen(e)

        # Die Menge in y: entweder eine Teilung oder eine Stabzahl über die
        # betrachtete Breite. Aus der Zahl wird hier eine Teilung -- die Formel
        # kennt nur Teilungen, und die Umrechnung steht in der Herleitung.
        menge_y = e.g("menge_y")
        ueber_teilung = self.buegel.ueber_abstand_y
        s_y = menge_y.si if ueber_teilung else (b / menge_y.si if menge_y.si else 0.0)

        self.buegelwerte = Buegelwerte(
            a_s=a_s, s_x=s_x, s_y=s_y, f_yd=f_yd, f_cd=f_cd, k_c=k_c)

        teilung_y = (e["menge_y"] if ueber_teilung else
                     Zwischenwerte(self.id).laenge("s_y", "s_{V,y}", s_y))
        self._protokoll_ansatz_buegel(p, e, teilung_y)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        self.ergebnisse = []

        for fall in self.faelle:
            erg = self._einen_fall_buegel(
                fall, h=h, lagen=lagen, a_s=a_s, s_x=s_x, s_y=s_y,
                f_yd=f_yd, f_cd=f_cd, k_c=k_c, ueber_teilung=ueber_teilung)
            self.ergebnisse.append(erg)
            self._protokoll_fall_buegel(p, e, erg, teilung_y)
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
                "Bügel in y als Stabzahl → kein Widerstand in y. Für y: Teilung "
                "in mm.")
            return erg

        erg.zuglage = _zuglage(lagen, M_Ed >= 0)
        hoehen = _statische_hoehe(lagen, h, M_Ed >= 0)
        if hoehen is None:
            seite = "unten" if M_Ed >= 0 else "oben"
            erg.begruendung = erg.hinweis = (
                f"Zugseite ({seite}) ohne Bewehrung → kein d, V_Rd = 0.")
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
        massgebend = ("Bügel" if erg.massgebend.V_Rd_s <= erg.massgebend.V_Rd_c
                      else "Druckdiagonale")
        erg.begruendung = (
            f"α = {erg.massgebend.alpha}°: "
            f"V_Rd,s = {erg.massgebend.V_Rd_s / 1e3:.1f} kN/m, "
            f"V_Rd,c = {erg.massgebend.V_Rd_c / 1e3:.1f} kN/m → massgebend "
            f"{massgebend}.")
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
        erg.zuglage = _zuglage(lagen, M_Ed >= 0)
        hoehen = _statische_hoehe(lagen, h, M_Ed >= 0)
        if hoehen is None:
            seite = "unten" if M_Ed >= 0 else "oben"
            erg.erfuellungsgrad = 0.0
            erg.erfuellt = False
            erg.begruendung = erg.hinweis = (
                f"Zugseite ({seite}) ohne Bewehrung → kein d, V_Rd = 0.")
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
            f"V_Rd = k_d · τ_cd · d_v = {erg.k_d:.4f} · "
            f"{tau_cd.formatiert(4, N_PRO_MM2)} N/mm² · "
            f"{Groesse.aus_si(erg.d_v, MM).formatiert(1)} mm "
            f"= {erg.v_Rd / 1e3:.1f} kN/m.")
        return erg


    # -- Mitschrift mit Bügeln ----------------------------------------------

    def _protokoll_ansatz_buegel(
        self, p: Protokoll, e: Eingaben, s_y: Wert
    ) -> None:
        p.titel(f"Querkraft – {self.richtung.beschriftung}")
        p.erklaerung(
            "Querkraftwiderstand mit Querkraftbewehrung, Fachwerkmodell mit "
            "veränderlicher Neigung der Druckdiagonalen. Massgebend ist das "
            "Kleinere aus dem Widerstand der Bügel und dem der Druckdiagonalen; "
            "der Betonanteil ohne Bügel geht nicht zusätzlich ein."
        )
        s = {name: e[name].symbol for name in ("a_s_V", "s_x", "f_yd_V", "k_c", "f_cd")}
        p.ansatz(
            rf"V_{{Rd,s}} = \frac{{{s['a_s_V']}}}{{{s['s_x']} \cdot {s_y.symbol}}} "
            rf"\cdot 0.9 \cdot d \cdot {s['f_yd_V']} \cdot \cot\alpha \qquad "
            rf"V_{{Rd,c}} = 0.9 \cdot d \cdot {s['k_c']} \cdot {s['f_cd']} "
            r"\cdot \sin\alpha \cdot \cos\alpha",
            titel="Ansatz", referenz="SIA 262:2025, 4.3.3.4")
        p.erklaerung(
            "Beide Anteile gelten je Laufmeter, wie die Querkraft selbst. "
            "Gesucht wird ganzgradig zwischen α_min und α_max die Neigung mit "
            f"dem grössten Widerstand V_Rd = min(V_Rd,s; V_Rd,c). Bei einer "
            f"Normalzugkraft steilt sich die Druckdiagonale auf: α_min wird "
            f"dann auf {ALPHA_ZUG}° gesetzt und α_max notfalls mitgehoben."
        )
        if not self.buegel.ueber_abstand_y:
            p.formel(s_y, r"\frac{@b}{@n}", {"b": e["b"], "n": e["menge_y"]},
                     titel="Teilung in y aus der Stabzahl")

    def _protokoll_fall_buegel(
        self, p: Protokoll, e: Eingaben, erg: Querkraftergebnis, s_y: Wert,
    ) -> None:
        fall = erg.fall
        p.titel(f"Nachweis – {fall.name}", ebene=3)
        self._protokoll_einwirkung(p, fall)

        if erg.massgebend is None:
            p.text(erg.begruendung)
            return

        werte = Zwischenwerte(f"{self.id}.{fall.kennung}")
        d = self._protokoll_hoehe(p, e, erg, werte)

        if erg.zug_hebt_alpha:
            p.text(f"N_Ed = {fall.N_Ed.formatiert(1, KN)} kN (Zug) → "
                   f"α_min = {erg.alpha_min}°, α_max = {erg.alpha_max}°.")

        q = erg.massgebend
        p.text(f"α = {erg.alpha_min}° … {erg.alpha_max}° ganzgradig → grösster "
               f"Widerstand bei α = {q.alpha}°.")

        alpha = werte.wert("alpha", r"\alpha", Groesse(q.alpha, GRAD), 0)
        buegel = werte.wert("V_Rd_s", "V_{Rd,s}", Groesse.aus_si(q.V_Rd_s, KN_PRO_M))
        diagonale = werte.wert("V_Rd_c", "V_{Rd,c}", Groesse.aus_si(q.V_Rd_c, KN_PRO_M))
        p.formel(
            buegel,
            r"\frac{@A}{@s_x \cdot @s_y} \cdot 0.9 \cdot @d \cdot @f_yd \cdot \cot @alpha",
            {"A": e["a_s_V"], "s_x": e["s_x"], "s_y": s_y, "d": d,
             "f_yd": e["f_yd_V"], "alpha": alpha},
            titel="Widerstand der Bügel")
        p.formel(
            diagonale,
            r"0.9 \cdot @d \cdot @k_c \cdot @f_cd \cdot \sin @alpha \cdot \cos @alpha",
            {"d": d, "k_c": e["k_c"], "f_cd": e["f_cd"], "alpha": alpha},
            titel="Widerstand der Druckdiagonalen")
        p.formel(self._widerstand(erg), r"\min\left[@s;\ @c\right]",
                 {"s": buegel, "c": diagonale}, titel="Querkraftwiderstand")

        self._protokoll_grad(p, erg)

    # -- Mitschrift, für beide Ansätze ----------------------------------------

    def _protokoll_einwirkung(self, p: Protokoll, fall: Querkraftfall) -> None:
        p.gleichung(
            rf"V_{{Ed}} = {fall.V_Ed.als_latex(1, KN_PRO_M)} \qquad "
            rf"M_{{Ed}} = {fall.M_Ed.als_latex(1, KNM)} \qquad "
            rf"N_{{Ed}} = {fall.N_Ed.als_latex(1, KN)}",
            titel="Einwirkung")

    def _protokoll_hoehe(self, p: Protokoll, e: Eingaben, erg: Querkraftergebnis,
                         werte: Zwischenwerte) -> Wert:
        """Die statische Höhe der gezogenen Bewehrung -- geschrieben, und für die Formeln danach."""
        positiv = erg.fall.M_Ed.si >= 0
        lage, art = self.posten[erg.zuglage][:2]
        d = werte.laenge("d", "d", erg.d)
        protokoll_statische_hoehe(p, d, h=e["h"], z=e[f"z_{lage.nummer}{art.kuerzel}"],
                                  von_unten=positiv)
        return d

    def _protokoll_grad(self, p: Protokoll, erg: Querkraftergebnis) -> None:
        """Die letzte Zeile jedes Falls -- für beide Ansätze dieselbe."""
        name = erg.fall.name
        widerstand = self.d_v_rd[name].belegen(Groesse.aus_si(erg.v_Rd, KN_PRO_M))
        grad_formel(p, self.d_ausnutzung[name], erg.erfuellungsgrad, widerstand,
                    self._einwirkung(erg.fall), erg.erfuellt, mit_urteil=True)

    # -- Mitschrift ohne Bügel -------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben) -> None:
        p.titel(f"Querkraft – {self.richtung.beschriftung}")
        p.erklaerung(
            "Querkraftwiderstand ohne Querkraftbewehrung. Massgebend sind die "
            "statische Höhe der gezogenen Bewehrung, die Grösstkorngrösse und "
            "die Dehnung auf halber Höhe."
        )
        s = {name: e[name].symbol for name in ("tau_cd", "f_yd", "E_s")}
        p.ansatz(
            rf"V_{{Rd}} = k_d \cdot {s['tau_cd']} \cdot d_v \qquad "
            r"k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g}",
            titel="Ansatz", referenz="SIA 262:2025, 4.3.3.2.1")
        p.ansatz(
            r"m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} \qquad "
            rf"\varepsilon_v = \frac{{{s['f_yd']} \cdot \left(\left|m_{{Ed}}\right| "
            r"- m_{Dd}\right)}"
            rf"{{{s['E_s']} \cdot \left(\left|m_{{Rd}}(N_{{Ed}})\right| - m_{{Dd}}\right)}}",
            titel="Dekompressionsmoment und Dehnung")
        p.erklaerung(
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

    def _protokoll_k_g(self, p: Protokoll, e: Eingaben,
                       k_g: EmpirischesErgebnis) -> Wert:
        beiwert = Zwischenwerte(self.id).zahl("k_g", "k_g", k_g.wert.si)
        p.formel(
            beiwert,
            rf"\max\left[{K_G_MINDEST:.2f};\ \frac{{48}}{{16 + @D_max \cdot "
            r"\min\left[1.0;\ \left(\frac{60}{@f_ck}\right)^{2}\right]}\right]",
            {"D_max": e["D_max"], "f_ck": e["f_ck"]}, empirisch=k_g.einheiten,
            titel="Beiwert der Gesteinskörnung", referenz="SIA 262:2025, 4.3.3.2.1")
        return beiwert

    def _protokoll_fall(
        self, p: Protokoll, e: Eingaben, erg: Querkraftergebnis, k_g: Wert,
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
        self._protokoll_einwirkung(p, fall)

        # Ohne Bewehrung auf der gezogenen Seite gibt es kein d -- und nichts
        # weiter herzuleiten.
        if erg.zuglage is None:
            p.text(erg.begruendung)
            return

        werte = Zwischenwerte(f"{self.id}.{fall.kennung}")
        d = self._protokoll_hoehe(p, e, erg, werte)
        d_v = werte.laenge("d_v", "d_v", erg.d_v)
        if erg.d_v < erg.d:
            p.formel(d_v, "@d - @e", {"d": d, "e": e["einlagenhoehe"]},
                     titel="Wirksame Höhe, um die Einlage vermindert")
        else:
            p.formel(d_v, "@d", {"d": d},
                     titel="Wirksame Höhe (Einlage nicht massgebend)")

        m_Dd = werte.moment("m_Dd", "m_{Dd}", erg.m_Dd)
        p.formel(m_Dd, r"\frac{\left|\min(@N_Ed;\ 0)\right| \cdot @h}{6}",
                 {"N_Ed": werte.kraft("N_Ed", "N_{Ed}", N_Ed), "h": e["h"]},
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
                p, bei_n, basis=werte.basis,
                titel=f"Momentenwiderstand bei N_Ed = {N_Ed / 1e3:.1f} kN")

        m_Ed = werte.moment("m_Ed", "m_{Ed}", M_Ed)
        m_Rd = werte.moment("m_Rd", "m_{Rd}(N_{Ed})", erg.m_Rd)
        eps_v = werte.dehnung("eps_v", r"\varepsilon_v", erg.eps_v, stellen=3)
        stahl = {"f_yd": e["f_yd"], "E_s": e["E_s"]}
        if erg.eps_v == 0.0:
            p.text(f"|m_Ed| = {Groesse.aus_si(abs(M_Ed), KNM).formatiert(1)} kNm "
                   f"≤ m_Dd = {m_Dd.formatiert()} kNm → ungerissen, ε_v = 0.")
        elif erg.plastisch:
            # Die Dehnung folgt hier nicht der Formel darüber -- sie ist fest.
            # Stünde die Formel mit den Zahlen da, ergäbe sie etwas anderes
            # als das Resultat daneben.
            p.text(f"|m_Ed| = {Groesse.aus_si(abs(M_Ed), KNM).formatiert(1)} kNm "
                   f"> m_Rd(N_Ed) = {m_Rd.formatiert()} kNm → Bewehrung fliesst, "
                   f"ε_v fest.")
            p.formel(eps_v, rf"{PLASTISCH} \cdot \frac{{@f_yd}}{{@E_s}}", stahl,
                     titel="Dehnung auf halber Höhe")
        else:
            p.formel(
                eps_v,
                r"\frac{@f_yd \cdot \left(\left|@m_Ed\right| - @m_Dd\right)}"
                r"{@E_s \cdot \left(\left|@m_Rd\right| - @m_Dd\right)}",
                {**stahl, "m_Ed": m_Ed, "m_Dd": m_Dd, "m_Rd": m_Rd},
                titel="Dehnung auf halber Höhe")

        k_d = werte.zahl("k_d", "k_d", erg.k_d, stellen=4)
        p.formel(k_d, r"\frac{1}{1 + @eps_v \cdot @d \cdot @k_g}",
                 {"eps_v": eps_v, "d": d, "k_g": k_g}, empirisch={"d": MM},
                 titel="Beiwert für die statische Höhe")

        # tau_cd steht in der Baustofftabelle auf zwei Stellen (1.1); mit so
        # wenigen ginge die Nachrechnung hier um ein halbes Prozent daneben.
        tau = e["tau_cd"]
        p.formel(self._widerstand(erg), r"@k_d \cdot @tau_cd \cdot @d_v",
                 {"k_d": k_d, "tau_cd": werte.wert("tau_cd", tau.symbol, tau.groesse, 4),
                  "d_v": d_v},
                 titel="Querkraftwiderstand", referenz="SIA 262:2025, 4.3.3.2.1")

        self._protokoll_grad(p, erg)
