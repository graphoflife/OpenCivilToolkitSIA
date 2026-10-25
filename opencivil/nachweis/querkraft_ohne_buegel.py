"""
opencivil/nachweis/querkraft_ohne_buegel.py -- Querkraft ohne Querkraftbewehrung.

VERANTWORTUNG:
Der Querkraftnachweis einer Platte ohne Buegel (:class:`QuerkraftOhneBuegel`),
samt der Kurve seines Widerstands ueber dem Moment. Was er mit dem Ansatz mit
Buegeln teilt, steht in :mod:`opencivil.nachweis.querkraft`.

OHNE BUEGEL::

    V_Rd = k_d * tau_cd * d_v

    k_d   = 1 / (1 + eps_v * d * k_g)
    k_g   = 48 / (16 + D_max * min[1.0; (60/f_ck)^2])
    m_Dd  = |N_Ed| * h / 6                      Dekompressionsmoment
    eps_v = f_yd * (m_Ed - m_Dd) / (E_s * (m_Rd(N_Ed) - m_Dd))

    d_v = d - Einlagenhoehe,  falls  h/6 < Einlagenhoehe < d
    d_v = d                   sonst

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

from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Tuple

from opencivil.core.berechnung import (
    Ausfuehrung, Befundbezug, Eingabebezug, Eingaben, NachweisUrteil, Vergleich,
)
from opencivil.core.einheiten import EINHEITSLOS, KNM, MM, N_PRO_MM2, Groesse, empirisch
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.nachweis.biegung_normalkraft import MNBefund, protokoll_widerstand
from opencivil.nachweis.querkraft import (
    Querkraft, Querkraftergebnis, Querkraftfall, _ohne_zugbewehrung, _hoch, _statische_hoehe,
    lagen_von, protokoll_hoehen, zuglage,
)
from opencivil.nachweis.rechenwahl import stahlbezuege, stahlname, staehle
from opencivil.querschnitt.zugseite import Zugseite

#: Unterer Riegel fuer den Beiwert der Gesteinskoernung.
K_G_MINDEST = 1.20

#: Vielfaches der Fliessdehnung, sobald ``m_Ed`` den Widerstand ueberschreitet.
#: ``eps_v = PLASTISCH * f_yd / E_s`` -- fest, nicht vom Moment abhaengig.
PLASTISCH = 1.5

#: Die Seite des Widerstands im Notizbuch -- Ansatz und Rechnung stehen darauf.
OHNE_BUEGEL = "Querkraftwiderstand ohne Querkraftbewehrung"

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
    zugstahl: Mapping[bool, Tuple[float, float]]
    """
    Je Momentenrichtung (``True``: Zug unten) ``(f_yd, E_s)`` des Stahls der
    gezogenen Seite -- unten und oben duerfen verschiedene Staehle liegen.
    Fehlt eine Richtung, liegt auf ihrer Zugseite keine Bewehrung.
    """

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
    index: str = "Rd",
) -> Widerstandspunkt:
    """
    Der Querkraftwiderstand bei diesem Moment und dieser Normalkraft.

    Alles in SI-Basis; ``tau_cd`` in Pa, ``m_Rd`` in Nm, Rueckgabe in N/m.
    ``index`` ist der des Momentenwiderstands, ``Rd`` oder ``Rk`` -- je nach
    der Linie, aus der er kommt; er steht nur im Text.

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
            grund=(f"m_{index}(N_Ed) = {m_Rd / 1e3:.1f} kNm ≤ m_Dd = {m_Dd / 1e3:.1f} kNm "
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


def beiwert_k_g(p: Protokoll, basis: str, D_max: Wert, f_ck: Wert) -> Wert:
    """
    Der Beiwert der Gesteinskoernung, samt seiner Zeile in der Herleitung --
    fuer den Querkraftnachweis und die Kennzahlen der Platte, eine Formel.
    Empirisch: ``D_max`` in mm, ``f_ck`` in N/mm^2.
    """
    k_g = empirisch(
        lambda D_max, f_ck: max(
            K_G_MINDEST, 48.0 / (16.0 + D_max * min(1.0, (60.0 / f_ck) ** 2))),
        ergebnis=EINHEITSLOS,
        D_max=(D_max.groesse, MM),
        f_ck=(f_ck.groesse, N_PRO_MM2),
    )
    beiwert = Zwischenwerte(basis).zahl("k_g", "k_g", k_g.wert.si)
    p.formel(
        beiwert,
        rf"\max\left[{K_G_MINDEST:.2f};\ \frac{{48}}{{16 + @D_max \cdot "
        r"\min\left[1.0;\ \left(\frac{60}{@f_ck}\right)^{2}\right]}\right]",
        {"D_max": D_max, "f_ck": f_ck}, empirisch=k_g.einheiten,
        titel="Beiwert der Gesteinskörnung", referenz="SIA 262:2025, 4.3.3.2.1")
    return beiwert


# ===========================================================================
# Herleitung -- fuer den Nachweis und die Kennzahlen der Platte dieselbe
# ===========================================================================


def tau_cd_wert(werte: Zwischenwerte, e: Eingaben) -> Wert:
    """
    tau_cd fuer die Herleitung, mit vier Stellen: in der Baustofftabelle steht
    es auf zwei (1.1), und mit so wenigen ginge die Nachrechnung um ein halbes
    Prozent daneben. Fuer den Nachweis und die Kennzahlen.
    """
    tau = e["tau_cd"]
    return werte.wert("tau_cd", tau.symbol, tau.groesse, 4)


def protokoll_ohne_buegel(p: Protokoll, werte: Zwischenwerte, widerstand: Wert, *,
                          k_d: float, eps_v: Wert, d: Wert, d_v: Wert, k_g: Wert,
                          tau_cd: Wert, titel: str = "Querkraftwiderstand",
                          zeichen: str = "") -> None:
    """
    Der Widerstand ohne Buegel aus der Dehnung ``eps_v``, die schon dasteht:
    ``k_d`` und ``V_Rd = k_d · tau_cd · d_v``. ``widerstand`` ist der Wert,
    der dabei herauskommt, mit seinem Zeichen.
    """
    beiwert = werte.zahl(*_hoch("k_d", "k_d", zeichen), k_d, stellen=4)
    p.formel(beiwert, r"\frac{1}{1 + @eps_v \cdot @d \cdot @k_g}",
             {"eps_v": eps_v, "d": d, "k_g": k_g}, empirisch={"d": MM},
             titel="Beiwert für die statische Höhe")
    p.formel(widerstand, r"@k_d \cdot @tau_cd \cdot @d_v",
             {"k_d": beiwert, "tau_cd": tau_cd, "d_v": d_v},
             titel=titel, referenz="SIA 262:2025, 4.3.3.2.1", name=OHNE_BUEGEL)


@dataclass
class BefundOhneBuegel:
    """
    Was der Nachweis ohne Buegel festhaelt: je Fall die Zwischenwerte, dazu
    die geloesten Eingaenge des Ansatzes. Daraus zeichnet sich die Kurve
    ueber dem Moment, ohne dass die Oberflaeche die Formel ein zweites Mal
    enthaelt. Steht nach dem Lauf in der Loesung, nicht am Nachweis.
    """

    beiwerte: Kurvenbeiwerte
    """Die geloesten Eingaenge -- fuer :meth:`kurve`."""

    mn: MNBefund
    """Der Befund des M-N-Nachweises: aus seiner Linie kommt ``m_Rd(N_Ed)`` der Kurve."""

    index: str = "Rd"
    """Wie der Momentenwiderstand heisst -- ``Rd``, oder ``Rk`` mit charakteristischen Werten."""

    ergebnisse: List["ErgebnisOhneBuegel"] = field(default_factory=list)

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
        hoehen = self.beiwerte.hoehen(moment_positiv)
        if hoehen is None:
            return None
        m_Rd = self.mn.moment_bei(N_Ed, positiv=moment_positiv)
        if not m_Rd or m_Rd <= 0.0:
            return None

        d, d_v = hoehen
        f_yd, E_s = self.beiwerte.zugstahl[moment_positiv]
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
                tau_cd=self.beiwerte.tau_cd, f_yd=f_yd,
                E_s=E_s, k_g=self.beiwerte.k_g, m_Rd=m_Rd,
                index=self.index)
            punkte.append((vz * M_Ed, p.v_Rd, p.plastisch))

        return {"punkte": punkte, "m_Rd": vz * m_Rd, "d": d, "d_v": d_v,
                "moment_positiv": moment_positiv}


@dataclass
class ErgebnisOhneBuegel(Querkraftergebnis):
    """Alle Zwischenwerte eines Falls ohne Buegel, damit die Herleitung vollstaendig ist."""

    d_v: float = 0.0
    k_d: float = 0.0
    eps_v: float = 0.0
    m_Dd: float = 0.0
    m_Rd: float = 0.0
    """Momentenwiderstand bei der wirkenden Normalkraft, in Nm."""

    plastisch: bool = False
    """``m_Ed`` liegt ueber dem Momentenwiderstand -- siehe :func:`widerstand`."""


class QuerkraftOhneBuegel(Querkraft):
    """Der Querkraftnachweis einer Platte ohne Buegel -- siehe Dateikopf."""

    def _ansatzbezuege(self) -> List[Eingabebezug]:
        # Die Dehnung eps_v rechnet mit dem Stahl der gezogenen Seite --
        # unten und oben duerfen verschiedene liegen, also je Stahl.
        bezuege = [
            Eingabebezug("D_max", self.querschnitt.id_von("D_max")),
            Eingabebezug("einlagenhoehe", self.querschnitt.id_von("einlagenhoehe")),
            Eingabebezug("f_ck", self.querschnitt.beton.id_von("f_ck")),
            Eingabebezug("tau_cd", self.querschnitt.beton.id_von("tau_cd")),
        ] + stahlbezuege(self.posten, ("f_yd", "E_s"))
        # Der Momentenwiderstand bei der wirkenden Normalkraft kommt aus dem
        # M-N-Nachweis -- je Fall einer. Als Eingang statt als mitgegebene Zahl,
        # damit die Abhaengigkeit im Graphen steht und die Rueckverfolgung sie
        # zeigt. Mit Buegeln geht er nicht ein; ihn trotzdem anzufordern
        # haenge eine Interpolation in die Herleitung, die dort nichts erklaert.
        for f in self.faelle:
            bezuege.append(Eingabebezug(f"m_Rd_{f.kennung}", self.mn.d_m_rd[f.name].id))
        return bezuege

    def _befunde(self) -> List[Befundbezug]:
        # m_Rd(N_Ed) kommt samt Herleitung aus dem M-N-Nachweis.
        return [Befundbezug("mn", self.mn.id)]

    # -- Rechnen ------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        m_rd = {f.name: abs(e.g(f"m_Rd_{f.kennung}").si) for f in self.faelle}
        lagen = lagen_von(e, self.posten)
        zugstahl = {}
        for positiv in (True, False):
            i = zuglage(lagen, positiv)
            if i is not None:
                stahl = self.posten[i][0].stahl
                zugstahl[positiv] = (e.g(stahlname("f_yd", stahl)).si,
                                     e.g(stahlname("E_s", stahl)).si)

        self._protokoll_ansatz(p, e)

        beiwert = beiwert_k_g(p, self.id, e["D_max"], e["f_ck"])
        # Fuer die Faelle und fuer die Kurve dieselben -- auch d_v entsteht
        # darum an einer Stelle (:meth:`Kurvenbeiwerte.hoehen`).
        beiwerte = Kurvenbeiwerte(h=e.g("h").si, lagen=lagen, einlage=e.g("einlagenhoehe").si,
                                  tau_cd=e.g("tau_cd").si, zugstahl=zugstahl,
                                  k_g=beiwert.groesse.si)
        mn = e.befund("mn")
        befund = BefundOhneBuegel(beiwerte=beiwerte, mn=mn, index=self.mn.wahl.index)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []

        for fall in self.faelle:
            erg = self._einen_fall(fall, beiwerte, m_rd[fall.name])
            befund.ergebnisse.append(erg)
            self._protokoll_fall(p, e, erg, beiwert, mn)
            self._eintragen(erg, ergebnis, urteile)

        return Ausfuehrung(ergebnis, urteile, befund)

    def _einen_fall(self, fall: Querkraftfall, w: Kurvenbeiwerte,
                    m_Rd: float) -> ErgebnisOhneBuegel:
        erg = ErgebnisOhneBuegel(fall=fall)
        M_Ed, N_Ed = fall.M_Ed.si, fall.N_Ed.si
        erg.m_Rd = m_Rd

        # Ohne Bewehrung auf der gezogenen Seite gibt es kein d -- und ohne d
        # keinen Querkraftwiderstand. Frueher wurde hier die gedrueckte Seite
        # herangezogen und lieferte eine Zahl, die keine statische Hoehe ist.
        erg.zuglage = zuglage(w.lagen, M_Ed >= 0)
        hoehen = w.hoehen(M_Ed >= 0)
        if hoehen is None:
            erg.begruendung = _ohne_zugbewehrung(M_Ed)
            return erg
        erg.d, erg.d_v = hoehen
        f_yd, E_s = w.zugstahl[M_Ed >= 0]

        # Nur Druck entlastet: bei Zug liefert min(N_Ed; 0) null, das
        # Dekompressionsmoment entfaellt und der Nachweis laeuft unveraendert
        # weiter. Eine Sonderbehandlung braucht es dafuer nicht -- sie stand
        # frueher hier und setzte v_Rd kurzerhand auf null.
        punkt = widerstand(
            M_Ed=M_Ed, N_Ed=N_Ed, h=w.h, d=erg.d, d_v=erg.d_v,
            tau_cd=w.tau_cd, f_yd=f_yd, E_s=E_s, k_g=w.k_g, m_Rd=m_Rd,
            index=self.mn.wahl.index)
        erg.m_Dd = punkt.m_Dd
        erg.eps_v = punkt.eps_v
        erg.k_d = punkt.k_d
        erg.v_Rd = punkt.v_Rd
        erg.plastisch = punkt.plastisch

        if punkt.grund:
            erg.begruendung = punkt.grund
            return erg

        erg.ausgang = Vergleich(self._einwirkung(fall), self._widerstand(erg))
        erg.begruendung = (
            f"V_Rd = k_d · τ_cd · d_v = {erg.k_d:.4f} · "
            f"{Groesse.aus_si(w.tau_cd, N_PRO_MM2).formatiert(4)} N/mm² · "
            f"{Groesse.aus_si(erg.d_v, MM).formatiert(1)} mm "
            f"= {erg.v_Rd / 1e3:.1f} kN/m.")
        return erg

    # -- Mitschrift -----------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben) -> None:
        p.titel(f"Querkraft – {self.richtung.beschriftung}")
        p.erklaerung(
            "Querkraftwiderstand ohne Querkraftbewehrung. Massgebend sind die "
            "statische Höhe der gezogenen Bewehrung, die Grösstkorngrösse und "
            "die Dehnung auf halber Höhe."
        )
        # Bei einem Stahl mit seinem Zeichen; bei zweien das allgemeine --
        # welcher gilt, steht bei jedem Fall.
        s = {"tau_cd": e["tau_cd"].symbol}
        for kennwert, allgemein in (("f_yd", "f_{yd}"), ("E_s", "E_s")):
            zeichen = {e[stahlname(kennwert, st)].symbol for st in staehle(self.posten)}
            s[kennwert] = zeichen.pop() if len(zeichen) == 1 else allgemein
        p.ansatz(
            rf"V_{{Rd}} = k_d \cdot {s['tau_cd']} \cdot d_v \qquad "
            r"k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g}",
            titel="Ansatz", referenz="SIA 262:2025, 4.3.3.2.1", name=OHNE_BUEGEL)
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

    def _protokoll_fall(
        self, p: Protokoll, e: Eingaben, erg: ErgebnisOhneBuegel, k_g: Wert,
        mn: MNBefund,
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
        d, d_v = protokoll_hoehen(p, werte, e, self.posten, erg.zuglage, erg.d, erg.d_v,
                                  seite=Zugseite.aus_moment(M_Ed))

        m_Dd = werte.moment("m_Dd", "m_{Dd}", erg.m_Dd)
        p.formel(m_Dd, r"\frac{\left|\min(@N_Ed;\ 0)\right| \cdot @h}{6}",
                 {"N_Ed": werte.kraft("N_Ed", "N_{Ed}", N_Ed), "h": e["h"]},
                 titel="Dekompressionsmoment")

        if not erg.machbar:
            p.text(erg.begruendung)
            return

        # Der Momentenwiderstand, mit dem gleich gerechnet wird, hängt von der
        # wirkenden Normalkraft ab. Wo er auf dem Polygon herkommt, steht hier
        # -- geschrieben vom M-N-Nachweis, der es gerechnet hat.
        bei_n = mn.widerstand_bei_n(fall.name)
        if bei_n is not None:
            protokoll_widerstand(
                p, bei_n, basis=werte.basis,
                titel=f"Momentenwiderstand bei N_Ed = {N_Ed / 1e3:.1f} kN")

        m_Ed = werte.moment("m_Ed", "m_{Ed}", M_Ed)
        idx = self.mn.wahl.index
        m_Rd = werte.moment("m_Rd", f"m_{{{idx}}}(N_{{Ed}})", erg.m_Rd)
        eps_v = werte.dehnung("eps_v", r"\varepsilon_v", erg.eps_v, stellen=3)
        zugseite = self.posten[erg.zuglage][0].stahl
        stahl = {"f_yd": e[stahlname("f_yd", zugseite)], "E_s": e[stahlname("E_s", zugseite)]}
        if erg.eps_v == 0.0:
            p.text(f"|m_Ed| = {Groesse.aus_si(abs(M_Ed), KNM).formatiert(1)} kNm "
                   f"≤ m_Dd = {m_Dd.formatiert()} kNm → ungerissen, ε_v = 0.")
        elif erg.plastisch:
            # Die Dehnung folgt hier nicht der Formel darüber -- sie ist fest.
            # Stünde die Formel mit den Zahlen da, ergäbe sie etwas anderes
            # als das Resultat daneben.
            p.text(f"|m_Ed| = {Groesse.aus_si(abs(M_Ed), KNM).formatiert(1)} kNm "
                   f"> m_{idx}(N_Ed) = {m_Rd.formatiert()} kNm → Bewehrung fliesst, "
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

        protokoll_ohne_buegel(p, werte, self._widerstand(erg), k_d=erg.k_d, eps_v=eps_v,
                              d=d, d_v=d_v, k_g=k_g, tau_cd=tau_cd_wert(werte, e))

        self._protokoll_grad(p, erg)
