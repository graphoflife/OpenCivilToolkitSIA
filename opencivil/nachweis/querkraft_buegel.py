"""
opencivil/nachweis/querkraft_buegel.py -- Querkraft mit Querkraftbewehrung.

VERANTWORTUNG:
Der Querkraftnachweis einer Platte mit Buegeln (:class:`QuerkraftMitBuegeln`),
samt dem Verlauf seines Widerstands ueber der Neigung. Was er mit dem Ansatz
ohne Buegel teilt, steht in :mod:`opencivil.nachweis.querkraft`.

MIT BUEGELN -- Fachwerkmodell, siehe :func:`buegelwiderstand`::

    V_Rd,s = A_(⌀,V)/(s_V,x * s_V,y) * 0.9 * d * f_yd * cot(alpha)
    V_Rd,c = 0.9 * d * k_c * f_cd * sin(alpha) * cos(alpha)
    V_Rd   = max ueber alpha von min(V_Rd,s; V_Rd,c)

Gesucht wird ganzgradig zwischen ``alpha_min`` und ``alpha_max``. Bei
Normalzug steilt sich die Druckdiagonale auf -- beide Grenzen werden dann auf
mindestens ``ALPHA_ZUG`` gehoben. Der Betonanteil des Ansatzes ohne Buegel
geht nicht zusaetzlich ein.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben, NachweisUrteil, Vergleich
from opencivil.core.einheiten import GRAD, KN, KN_PRO_M, KNM, Groesse
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.nachweis.querkraft import (
    Querkraft, Querkraftergebnis, Querkraftfall, _hoch, _ohne_zugbewehrung, _statische_hoehe,
    lagen_von, protokoll_hoehen, zuglage,
)
from opencivil.querschnitt.fachwerk import Buegelpunkt, beste_neigung, fachwerk
from opencivil.querschnitt.platte import ALPHA_ZUG, Richtung
from opencivil.querschnitt.zugseite import Zugseite

MIT_BUEGELN = "Querkraftwiderstand mit Querkraftbewehrung"


def buegelwiderstand(
    *, alpha: int, a_s: float, s_x: float, s_y: float, d: float,
    f_yd: float, f_cd: float, k_c: float,
) -> Buegelpunkt:
    """
    Das Fachwerk der Platte, je Laufmeter (Rueckgabe in N/m)::

        V_Rd,s = A_(⌀,V)/(s_x · s_y) · 0.9 · d · f_yd · cot(alpha)
        V_Rd,c = 0.9 · d · k_c · f_cd · sin(alpha) · cos(alpha)

    ``A_(⌀,V)/(s_x · s_y)`` ist der Bewehrungsgehalt: ein Buegelschenkel je
    Rasterfeld. Beide Groessen gelten **je Laufmeter** -- so wie ``V_Ed`` und
    wie der Widerstand ohne Buegel. Darum ist die Stegbreite ein Meter, und der
    Hebelarm ``0.9 · d``.
    """
    return fachwerk(alpha=alpha, a_sw_s=a_s / (s_x * s_y), z=0.9 * d, b_w=1.0,
                    f_yd=f_yd, f_cd=f_cd, k_c=k_c)


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


def buegelteilung_y(buegel, b: float, menge_y: float) -> float:
    """
    Die Buegelteilung in y, in m: angegeben -- oder aus der Stabzahl ueber die
    betrachtete Breite ``b``. Die Formel kennt nur Teilungen.
    """
    if buegel.ueber_abstand_y:
        return menge_y
    return b / menge_y if menge_y else 0.0


# ===========================================================================
# Herleitung -- fuer den Nachweis und die Kennzahlen der Platte dieselbe
# ===========================================================================


def protokoll_mit_buegeln(p: Protokoll, werte: Zwischenwerte, widerstand: Wert,
                          q: Buegelpunkt, *, e: Eingaben, s_y: Wert, d: Wert,
                          alpha_min: int, alpha_max: int, seite: str = "",
                          zeichen: str = "") -> None:
    """
    Der Widerstand mit Buegeln bei der guenstigsten Neigung ``q``: welche es
    ist, die Buegel, die Druckdiagonale und das Kleinere beider.
    ``widerstand`` ist der Wert, der dabei herauskommt; ``seite`` steht in
    den Titeln, wo zwei Seiten nebeneinander stehen.
    """
    zug = f", Zug {seite}" if seite else ""
    p.text(f"{f'Zug {seite}: ' if seite else ''}α = {alpha_min}° … {alpha_max}° ganzgradig "
           f"→ grösster Widerstand bei α = {q.alpha}°.")
    alpha = werte.wert(*_hoch("alpha", r"\alpha", zeichen), Groesse(q.alpha, GRAD), 0)
    buegel = werte.wert(*_hoch("V_Rd_s", "V_{Rd,s}", zeichen),
                        Groesse.aus_si(q.V_Rd_s, KN_PRO_M))
    diagonale = werte.wert(*_hoch("V_Rd_c", "V_{Rd,c}", zeichen),
                           Groesse.aus_si(q.V_Rd_c, KN_PRO_M))
    p.formel(buegel,
             r"\frac{@A}{@s_x \cdot @s_y} \cdot 0.9 \cdot @d \cdot @f_yd \cdot \cot @alpha",
             {"A": e["a_s_V"], "s_x": e["s_x"], "s_y": s_y, "d": d,
              "f_yd": e["f_yd_V"], "alpha": alpha},
             titel=f"Widerstand der Bügel{zug}", name="Widerstand der Bügel")
    p.formel(diagonale,
             r"0.9 \cdot @d \cdot @k_c \cdot @f_cd \cdot \sin @alpha \cdot \cos @alpha",
             {"d": d, "k_c": e["k_c"], "f_cd": e["f_cd"], "alpha": alpha},
             titel=f"Widerstand der Druckdiagonalen{zug}",
             name="Widerstand der Druckdiagonalen")
    p.formel(widerstand, r"\min\left[@s;\ @c\right]", {"s": buegel, "c": diagonale},
             titel=f"Querkraftwiderstand{zug}", name=MIT_BUEGELN)


@dataclass
class BefundMitBuegeln:
    """
    Was der Nachweis mit Buegeln festhaelt: je Fall die Zwischenwerte, dazu
    die geloesten Eingaenge des Ansatzes. Daraus zeichnet sich der Verlauf
    ueber der Neigung, ohne dass die Oberflaeche die Formel ein zweites Mal
    enthaelt. Steht nach dem Lauf in der Loesung, nicht am Nachweis.
    """

    buegelwerte: Buegelwerte
    """Die geloesten Eingaenge -- fuer :meth:`neigungsverlauf`."""

    ergebnisse: List["ErgebnisMitBuegeln"] = field(default_factory=list)

    ohne_einwirkung: Optional["ErgebnisMitBuegeln"] = None
    """
    Ohne Lastfall: der Ast ueber der Neigung bei M = 0 und N = 0, damit das
    Bild auch ohne Fall dasteht. Kein Fall des Nachweises -- ohne Ausgabe,
    Urteil und Herleitung.
    """

    def neigungsverlauf(self, d: float, von: int, bis: int) -> List[Buegelpunkt]:
        """
        Der Widerstand ueber der Neigung -- fuer das Diagramm.

        Ueber dieselbe Funktion wie der Nachweis selbst, nur ueber einen
        weiteren Bereich: gezeichnet wird auch ausserhalb der beiden Grenzen,
        dort blass. Zwei Rechenwege fuer dieselbe Kurve liefen auseinander.
        """
        w = self.buegelwerte
        return neigungen(
            alpha_min=von, alpha_max=bis, d=d,
            a_s=w.a_s, s_x=w.s_x, s_y=w.s_y,
            f_yd=w.f_yd, f_cd=w.f_cd, k_c=w.k_c)


@dataclass
class ErgebnisMitBuegeln(Querkraftergebnis):
    """Alle Zwischenwerte eines Falls mit Buegeln, damit die Herleitung vollstaendig ist."""

    punkte: Tuple[Buegelpunkt, ...] = ()
    """Der Widerstand je ganzem Grad zwischen den beiden Grenzwinkeln."""

    massgebend: Optional[Buegelpunkt] = None
    """Der Punkt mit dem groessten Widerstand -- daraus stammt ``v_Rd``."""

    alpha_min: int = 0
    alpha_max: int = 0
    """Die tatsaechlich verwendeten Grenzen; bei Normalzug angehoben."""

    zug_hebt_alpha: bool = False
    """Ob die Grenzen wegen einer Normalzugkraft angehoben wurden."""


#: Was der Nachweis mit Buegeln ohne Lastfall rechnet, nur fuer sein Bild
#: (siehe :attr:`BefundMitBuegeln.ohne_einwirkung`).
OHNE_EINWIRKUNG = Querkraftfall(name="ohne Einwirkung", V_Ed=Groesse(0.0, KN_PRO_M),
                                M_Ed=Groesse(0.0, KNM), N_Ed=Groesse(0.0, KN))


class QuerkraftMitBuegeln(Querkraft):
    """Der Querkraftnachweis einer Platte mit Buegeln -- siehe Dateikopf."""

    def __init__(self, querschnitt, faelle: Sequence[Querkraftfall], richtung: Richtung,
                 mn_nachweis) -> None:
        self.buegel = querschnitt.querkraftbewehrung
        """Die Bügel dieser Platte."""
        super().__init__(querschnitt, faelle, richtung, mn_nachweis)

    def _ansatzbezuege(self) -> List[Eingabebezug]:
        # Die Reihenfolge der Eingaenge ist die Reihenfolge, in der der
        # Loeser sie beschafft -- und damit die Reihenfolge der Bloecke in
        # der Mitschrift. Die fuenf Angaben zur Buegelbewehrung stehen
        # deshalb zusammen und der Buegelquerschnitt dahinter: stuende er
        # dazwischen, zerrisse er den Kasten, in dem sie gemeinsam stehen
        # sollen.
        return [
            Eingabebezug("b", self.querschnitt.id_breite(self.richtung)),
            Eingabebezug("k_c", self.querschnitt.id_von("k_c")),
            Eingabebezug("f_cd", self.querschnitt.beton.id_von("f_cd")),
            Eingabebezug("f_yd_V", self.buegel.stahl.id_von("f_yd")),
            Eingabebezug("phi_V", self.querschnitt.id_von("querkraft.phi")),
            Eingabebezug("s_x", self.querschnitt.id_von("querkraft.s_x")),
            Eingabebezug(
                "menge_y",
                self.querschnitt.id_von("querkraft.s_y" if self.buegel.ueber_abstand_y
                                   else "querkraft.n_y")),
            Eingabebezug("alpha_min", self.querschnitt.id_von("querkraft.alpha_min")),
            Eingabebezug("alpha_max", self.querschnitt.id_von("querkraft.alpha_max")),
            Eingabebezug("a_s_V", self.querschnitt.id_von("querkraft.a_s")),
        ]


    # -- Rechnen ------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
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
        lagen = lagen_von(e, self.posten)

        # Die Menge in y: entweder eine Teilung oder eine Stabzahl über die
        # betrachtete Breite. Aus der Zahl wird hier eine Teilung -- die Formel
        # kennt nur Teilungen, und die Umrechnung steht in der Herleitung.
        ueber_teilung = self.buegel.ueber_abstand_y
        s_y = buegelteilung_y(self.buegel, b, e.g("menge_y").si)

        befund = BefundMitBuegeln(buegelwerte=Buegelwerte(
            a_s=a_s, s_x=s_x, s_y=s_y, f_yd=f_yd, f_cd=f_cd, k_c=k_c))

        teilung_y = (e["menge_y"] if ueber_teilung else
                     Zwischenwerte(self.id).laenge("s_y", "s_{V,y}", s_y))
        self._protokoll_ansatz_buegel(p, e, teilung_y)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []

        for fall in self.faelle:
            erg = self._einen_fall_buegel(
                fall, h=h, lagen=lagen, a_s=a_s, s_x=s_x, s_y=s_y,
                f_yd=f_yd, f_cd=f_cd, k_c=k_c, ueber_teilung=ueber_teilung)
            befund.ergebnisse.append(erg)
            self._protokoll_fall_buegel(p, e, erg, teilung_y)
            self._eintragen(erg, ergebnis, urteile)
        if not self.faelle:
            befund.ohne_einwirkung = self._einen_fall_buegel(
                OHNE_EINWIRKUNG, h=h, lagen=lagen, a_s=a_s, s_x=s_x, s_y=s_y,
                f_yd=f_yd, f_cd=f_cd, k_c=k_c, ueber_teilung=ueber_teilung)

        return Ausfuehrung(ergebnis, urteile, befund)

    def _einen_fall_buegel(
        self, fall: Querkraftfall, *, h: float,
        lagen: Sequence[Tuple[float, bool]], a_s: float, s_x: float,
        s_y: float, f_yd: float, f_cd: float, k_c: float, ueber_teilung: bool,
    ) -> ErgebnisMitBuegeln:
        erg = ErgebnisMitBuegeln(fall=fall)
        M_Ed, N_Ed = fall.M_Ed.si, fall.N_Ed.si

        # Eine Stabzahl in y bezieht sich auf die betrachtete Breite. In
        # x-Richtung ergibt das eine Teilung; in y-Richtung liefe die Breite
        # laengs der Traglinie mit und die Formel haette keinen Bezug mehr.
        if not ueber_teilung and self.richtung is Richtung.Y:
            erg.begruendung = (
                "Bügel in y als Stabzahl → kein Widerstand in y. Für y: Teilung "
                "in mm.")
            return erg

        erg.zuglage = zuglage(lagen, M_Ed >= 0)
        hoehen = _statische_hoehe(lagen, h, M_Ed >= 0)
        if hoehen is None:
            erg.begruendung = _ohne_zugbewehrung(M_Ed)
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

        erg.ausgang = Vergleich(self._einwirkung(fall), self._widerstand(erg))
        massgebend = ("Bügel" if erg.massgebend.V_Rd_s <= erg.massgebend.V_Rd_c
                      else "Druckdiagonale")
        erg.begruendung = (
            f"α = {erg.massgebend.alpha}°: "
            f"V_Rd,s = {erg.massgebend.V_Rd_s / 1e3:.1f} kN/m, "
            f"V_Rd,c = {erg.massgebend.V_Rd_c / 1e3:.1f} kN/m → massgebend "
            f"{massgebend}.")
        return erg

    # -- Mitschrift -----------------------------------------------------------

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
            titel="Ansatz", referenz="SIA 262:2025, 4.3.3.4",
            name=MIT_BUEGELN)
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
        self, p: Protokoll, e: Eingaben, erg: ErgebnisMitBuegeln, s_y: Wert,
    ) -> None:
        fall = erg.fall
        p.titel(f"Nachweis – {fall.name}", ebene=3)
        self._protokoll_einwirkung(p, fall)

        if erg.massgebend is None:
            p.text(erg.begruendung)
            return

        werte = Zwischenwerte(f"{self.id}.{fall.kennung}")
        d, _ = protokoll_hoehen(p, werte, e, self.posten, erg.zuglage, erg.d,
                                seite=Zugseite.aus_moment(fall.M_Ed.si))

        if erg.zug_hebt_alpha:
            p.text(f"N_Ed = {fall.N_Ed.formatiert(1, KN)} kN (Zug) → "
                   f"α_min = {erg.alpha_min}°, α_max = {erg.alpha_max}°.")
        protokoll_mit_buegeln(p, werte, self._widerstand(erg), erg.massgebend, e=e, s_y=s_y,
                              d=d, alpha_min=erg.alpha_min, alpha_max=erg.alpha_max)

        self._protokoll_grad(p, erg)
