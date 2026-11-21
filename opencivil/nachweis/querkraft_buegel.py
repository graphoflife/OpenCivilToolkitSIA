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

Die Buegel stehen in SIA 262:2025, 4.3.3.4.3, Gl. (45), die Druckdiagonale
in 4.3.3.4.6, Gl. (47), der Hebelarm ``0.9 * d`` in 4.3.3.4.2.

Gesucht wird ganzgradig zwischen ``alpha_min`` und ``alpha_max`` (4.3.3.3.2,
Gl. (42)). Bei Normalzug steilt sich die Druckdiagonale auf -- beide Grenzen
werden dann auf mindestens ``ALPHA_ZUG`` gehoben (4.3.3.3.3). Der Betonanteil
des Ansatzes ohne Buegel geht nicht zusaetzlich ein.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben
from opencivil.core.nachweis import NachweisUrteil, Vergleich
from opencivil.core.einheiten import GRAD, KN, KN_PRO_M, KNM, Groesse
from opencivil.core.protokoll import Kurz, Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.nachweis.querkraft import (
    Querkraft, Querkraftergebnis, Querkraftfall, _hoch, _ohne_zugbewehrung, protokoll_hoehen,
    statische_hoehen, zugposten,
)
from opencivil.querschnitt.fachwerk import (
    ALPHA_ZUG, Buegelpunkt, Neigungssuche, fachwerk, guenstigste,
)
from opencivil.querschnitt.platte import Richtung
from opencivil.querschnitt.zugseite import Zugseite

MIT_BUEGELN = "Querkraftwiderstand mit Querkraftbewehrung"

#: Wo die Gleichungen stehen, je eine Stelle.
REFERENZ_BUEGEL = "SIA 262:2025, 4.3.3.4.3, (45)"
REFERENZ_DIAGONALE = "SIA 262:2025, 4.3.3.4.6, (47)"
#: Der Ansatz als Ganzes: der Hebelarm 0.9 · d und beide Gleichungen.
REFERENZ = "SIA 262:2025, 4.3.3.4.2; 4.3.3.4.3, (45); 4.3.3.4.6, (47)"


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
    Was ausser der Neigung und der statischen Hoehe in den Widerstand eingeht,
    dazu die Grenzen der Neigung.

    Alles in SI-Basis, die Neigung in Grad. Gebaut von
    :meth:`QuerkraftMitBuegeln.buegelwerte`; damit rechnen die Faelle und die
    Kennzahlen der Platte je Zugseite (:meth:`suche`) und das Bild ueber der
    Neigung (:meth:`neigungen`) -- ohne dass einer, auch nicht die
    Oberflaeche, die Formel ein zweites Mal enthaelt. Dasselbe Muster wie
    :class:`Kurvenbeiwerte` beim Ansatz ohne Buegel.
    """

    a_s: float
    s_x: float
    s_y: float
    f_yd: float
    f_cd: float
    k_c: float
    alpha_min: int
    alpha_max: int
    """Die Grenzen der Neigung, wie eingegeben -- bei Normalzug hebt sie :meth:`suche`."""

    def punkt(self, d: float, alpha: int) -> Buegelpunkt:
        """Der Widerstand bei der Neigung ``alpha`` in Grad und der statischen Hoehe ``d``."""
        return buegelwiderstand(alpha=alpha, a_s=self.a_s, s_x=self.s_x, s_y=self.s_y, d=d,
                                f_yd=self.f_yd, f_cd=self.f_cd, k_c=self.k_c)

    def neigungen(self, d: float, von: int, bis: int) -> List[Buegelpunkt]:
        """
        Der Widerstand je ganzes Grad von ``von`` bis ``bis`` bei der
        statischen Hoehe ``d`` -- fuer das Bild, das auch ausserhalb der
        Grenzen zeichnet, dort blass. Jeder Punkt kommt aus :meth:`punkt`, wie
        bei der Suche: zwei Rechenwege fuer dieselbe Kurve liefen auseinander.
        """
        return [self.punkt(d, alpha) for alpha in range(von, bis + 1)]

    def suche(self, d: float, *, zugkraft: bool) -> Neigungssuche:
        """
        Die guenstigste Neigung bei der statischen Hoehe ``d``
        (:func:`~opencivil.querschnitt.fachwerk.guenstigste`) -- fuer die
        Faelle und die Kennzahlen der Platte dieselbe Suche.
        """
        return guenstigste(lambda alpha: self.punkt(d, alpha), alpha_min=self.alpha_min,
                           alpha_max=self.alpha_max, zugkraft=zugkraft)


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
             titel=f"Widerstand der Bügel{zug}", referenz=REFERENZ_BUEGEL,
             name="Widerstand der Bügel", kurz=Kurz.ZEILE)
    p.formel(diagonale,
             r"0.9 \cdot @d \cdot @k_c \cdot @f_cd \cdot \sin @alpha \cdot \cos @alpha",
             {"d": d, "k_c": e["k_c"], "f_cd": e["f_cd"], "alpha": alpha},
             titel=f"Widerstand der Druckdiagonalen{zug}", referenz=REFERENZ_DIAGONALE,
             name="Widerstand der Druckdiagonalen", kurz=Kurz.ZEILE)
    p.formel(widerstand, r"\min\left[@s;\ @c\right]", {"s": buegel, "c": diagonale},
             titel=f"Querkraftwiderstand{zug}", name=MIT_BUEGELN, kurz=Kurz.EINSETZEN)


@dataclass
class BefundMitBuegeln:
    """
    Was der Nachweis mit Buegeln festhaelt: je Fall die Zwischenwerte, dazu
    die geloesten Eingaenge des Ansatzes. Daraus zeichnet sich der Verlauf
    ueber der Neigung, ohne dass die Oberflaeche die Formel ein zweites Mal
    enthaelt. Steht nach dem Lauf in der Loesung, nicht am Nachweis.
    """

    buegelwerte: Buegelwerte
    """Die geloesten Eingaenge -- fuer das Bild ueber der Neigung (:meth:`Buegelwerte.neigungen`)."""

    ergebnisse: List["ErgebnisMitBuegeln"] = field(default_factory=list)

    ohne_einwirkung: Optional["ErgebnisMitBuegeln"] = None
    """
    Ohne Lastfall: der Ast ueber der Neigung bei M = 0 und N = 0, damit das
    Bild auch ohne Fall dasteht. Kein Fall des Nachweises -- ohne Ausgabe,
    Urteil und Herleitung.
    """


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

    REFERENZ = REFERENZ

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

    # -- Was Fall und Kennzahl teilen ------------------------------------------

    def buegelwerte(self, e: Eingaben) -> Buegelwerte:
        """
        Die geloesten Eingaenge des Ansatzes -- fuer die Faelle, das Bild und
        die Kennzahlen der Platte dieselben. Eine Stabzahl in y wird hier eine
        Teilung (:func:`buegelteilung_y`): die Formel kennt nur Teilungen, und
        die Umrechnung steht in der Herleitung (:meth:`protokoll_teilung_y`).
        """
        return Buegelwerte(
            a_s=e.g("a_s_V").si, s_x=e.g("s_x").si,
            s_y=buegelteilung_y(self.buegel, e.g("b").si, e.g("menge_y").si),
            f_yd=e.g("f_yd_V").si, f_cd=e.g("f_cd").si, k_c=e.g("k_c").si,
            alpha_min=self.buegel.alpha_min, alpha_max=self.buegel.alpha_max)

    def teilung_y(self, werte: Zwischenwerte, e: Eingaben, s_y: float) -> Wert:
        """
        Die Teilung in y als Wert der Herleitung: angegeben, oder aus der
        Stabzahl ueber die Breite (``s_y`` der :meth:`buegelwerte`).
        """
        if self.buegel.ueber_abstand_y:
            return e["menge_y"]
        return werte.laenge("s_y", "s_{V,y}", s_y)

    def protokoll_teilung_y(self, p: Protokoll, e: Eingaben, s_y: Wert) -> None:
        """Die Zeile ``s_y = b/n``, wenn die Teilung aus der Stabzahl kommt."""
        if not self.buegel.ueber_abstand_y:
            p.formel(s_y, r"\frac{@b}{@n}", {"b": e["b"], "n": e["menge_y"]},
                     titel="Teilung in y aus der Stabzahl")

    # -- Rechnen ------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        """
        Fachwerkmodell: Bügel gegen Druckdiagonale, über die Neigung gesucht.

        Der Betonanteil des bügellosen Ansatzes entfällt hier vollständig --
        beides zu addieren wäre ein anderes Modell, und dieses Werkzeug rechnet
        nur, was es auch herleitet.
        """
        w = self.buegelwerte(e)
        hoehen = statische_hoehen(e, self.posten)
        befund = BefundMitBuegeln(buegelwerte=w)

        teilung_y = self.teilung_y(Zwischenwerte(self.id), e, w.s_y)
        self._protokoll_ansatz_buegel(p, e, teilung_y)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []

        for fall in self.faelle:
            erg = self._einen_fall_buegel(fall, w, hoehen)
            befund.ergebnisse.append(erg)
            self._protokoll_fall_buegel(p, e, erg, teilung_y)
            self._eintragen(erg, ergebnis, urteile)
        if not self.faelle:
            befund.ohne_einwirkung = self._einen_fall_buegel(OHNE_EINWIRKUNG, w, hoehen)

        return Ausfuehrung(ergebnis, urteile, befund)

    def _einen_fall_buegel(self, fall: Querkraftfall, w: Buegelwerte,
                           hoehen: Mapping[Zugseite, float]) -> ErgebnisMitBuegeln:
        erg = ErgebnisMitBuegeln(fall=fall)
        M_Ed, N_Ed = fall.M_Ed.si, fall.N_Ed.si

        # Eine Stabzahl in y bezieht sich auf die betrachtete Breite. In
        # x-Richtung ergibt das eine Teilung; in y-Richtung liefe die Breite
        # laengs der Traglinie mit und die Formel haette keinen Bezug mehr.
        if not self.buegel.ueber_abstand_y and self.richtung is Richtung.Y:
            erg.begruendung = (
                "Bügel in y als Stabzahl → kein Widerstand in y. Für y: Teilung "
                "in mm.")
            return erg

        seite = Zugseite.aus_moment(M_Ed)
        erg.zugposten = tuple(zugposten(self.posten, seite))
        d = hoehen.get(seite)
        if d is None:
            erg.begruendung = _ohne_zugbewehrung(M_Ed)
            return erg
        erg.d = d

        erg.zug_hebt_alpha = N_Ed > 0.0
        suche = w.suche(d, zugkraft=erg.zug_hebt_alpha)
        erg.alpha_min, erg.alpha_max = suche.alpha_min, suche.alpha_max
        erg.punkte, erg.massgebend = suche.punkte, suche.massgebend
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
            titel="Ansatz", referenz=REFERENZ, name=MIT_BUEGELN)
        p.erklaerung(
            "Beide Anteile gelten je Laufmeter, wie die Querkraft selbst; der "
            "Hebelarm der inneren Kräfte ist 0.9 · d. Gesucht wird ganzgradig "
            "zwischen α_min und α_max die Neigung mit dem grössten Widerstand "
            f"V_Rd = min(V_Rd,s; V_Rd,c). Bei einer Normalzugkraft steilt sich die "
            f"Druckdiagonale auf: α_min ist dann mindestens {ALPHA_ZUG}°, und α_max "
            f"wird notfalls mitgehoben."
        )
        self.protokoll_teilung_y(p, e, s_y)

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
        d, _ = protokoll_hoehen(p, werte, e, erg.zugposten, erg.d,
                                seite=Zugseite.aus_moment(fall.M_Ed.si))

        if erg.zug_hebt_alpha:
            p.text(f"N_Ed = {fall.N_Ed.formatiert(1, KN)} kN (Zug) → "
                   f"α_min = {erg.alpha_min}°, α_max = {erg.alpha_max}°.")
        protokoll_mit_buegeln(p, werte, self._widerstand(erg), erg.massgebend, e=e, s_y=s_y,
                              d=d, alpha_min=erg.alpha_min, alpha_max=erg.alpha_max)

        self._protokoll_grad(p, erg)
