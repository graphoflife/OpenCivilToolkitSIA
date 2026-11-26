"""
opencivil/querschnitt/spannglieder.py -- Spannglieder im gezeichneten Querschnitt.

VERANTWORTUNG:
Ein Spannglied der Querschnittsanalyse (:class:`Spannglied`): wo es liegt,
aus welchem Erzeugnis und wie vielen davon, wie es wirkt -- und was daraus
folgt: die Spannung nach dem Spannen und nach allen Verlusten, die
Vordehnung, die Kraft, sein Gesetz im Querschnitt und seine Grenzdehnung.
Jede Regel dazu steht hier, einmal: die Herleitung (:class:`Spannglieder`)
und das Zeichenfenster (:mod:`opencivil.web.zeichengeometrie`) fragen beide
hier (:func:`vorspannung`, :func:`grenzen_verletzt`).

DIE VORSPANNUNG ALS WIDERSTAND:
Die Zugkraft im Spannstahl zaehlt zum Widerstand (SIA 262:2025, 4.1.5.5.1):
die Lastfaelle sind ohne die Vorspannung einzugeben. Mit Verbund traegt ein
Glied mit seiner Vordehnung (4.1.5.1.5), ueber der Dehnung ``eps`` des
Querschnitts an seiner Stelle::

    sigma_p(eps) = sigma_Figur17(eps + eps_p)        eps_p = sigma_pinf / E_p

Ohne Verbund wirkt die Kraft nach allen Verlusten, ohne Zuwachs (4.1.5.1.6):
``sigma_p = sigma_pinf``, gleich welche Dehnung -- und keine Grenzdehnung.

SCHLAFF MIT RESTFESTIGKEIT:
Wer die Vorspannung schon als Einwirkung angesetzt hat (4.1.5.5.2), zaehlt
im Widerstand nur, was das Glied darueber hinaus traegt: das Gesetz mit
Vordehnung, um ``sigma_pinf`` gesenkt. Es beginnt bei null und endet bei
``f_pd - sigma_pinf``; gedrueckt verliert es bis ``sigma_pinf``. Ohne
Verbund bleibt davon nichts.

DIE VORGABEN:
Leer gelassen, gilt ``sigma_p0 = 0.70 f_pk`` und ``sigma_pinf = 0.85
sigma_p0`` -- nach Vorgabe, nicht nachgeschlagen (Benutzer, 2026-11-25).
Die Verluste haengen am Bauwerk (4.1.5.3); die Vorgabe ersetzt ihre
Rechnung nicht. Die Vordehnung ist ``sigma_pinf/E_p`` mit dem Modul des
Erzeugnisses: die Stauchung des Betons beim Vorspannen faellt weg -- nach
Vorgabe, nicht nachgeschlagen.

DIE GRENZEN:
Nach dem Spannen ``sigma_p0 <= min(0.75 f_pk; 0.85 f_p0.1k)`` (4.1.5.2.2,
Gleichung (22)), nach allen Verlusten ``sigma_pinf >= 0.45 f_pk``
(4.1.5.2.3). Wer sie verletzt, bekommt einen roten Hinweis am Glied und
in der Herleitung; gerechnet wird mit seinen Zahlen.

EINHEITEN:
Lage und Durchmesser in mm, Flaechen in mm², die eingegebenen Spannungen in
N/mm² -- wie in der Zeichnung. Die Gesetze rechnen in SI.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, ClassVar, Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.berechnung import Eingabebezug, Eingaben, Prozedur
from opencivil.core.einheiten import KN, MM2, N_PRO_MM2, PROMILLE, Groesse
from opencivil.core.latex import Mathe, Zelle, angabe, fest, vergleich
from opencivil.core.protokoll import Abschnitt, Protokoll, Zwischenwerte
from opencivil.core.wahl import Wahl
from opencivil.core.wert import Wert, WertDef
from opencivil.material.spannstahl import TABELLE_7, Erzeugnis
from opencivil.querschnitt.bewehrungselemente import MM, Bewehrungselement, Verdraengt
from opencivil.querschnitt.interaktion import Bewehrung, Werkstoff
from opencivil.querschnitt.werkstoffgesetz import (
    RUNDUNG, Gesetz, Spannstahlgesetz, Werte, _gebaut,
)

REFERENZ_WIDERSTAND = "SIA 262:2025, 4.1.5.5.1"
REFERENZ_VORDEHNUNG = "SIA 262:2025, 4.1.5.1.5"
REFERENZ_OHNE_VERBUND = "SIA 262:2025, 4.1.5.1.6"
REFERENZ_EINWIRKUNG = "SIA 262:2025, 4.1.5.5.2"
REFERENZ_NACH_SPANNEN = "SIA 262:2025, 4.1.5.2.2, (22)"
REFERENZ_NACH_VERLUSTEN = "SIA 262:2025, 4.1.5.2.3"
REFERENZ_VERLUSTE = "SIA 262:2025, 4.1.5.3"
NACH_VORGABE = "nach Vorgabe, nicht nachgeschlagen"

#: ``sigma_p0 = 0.70 f_pk``, wo nichts eingegeben ist -- nach Vorgabe, nicht
#: nachgeschlagen (Benutzer, 2026-11-25).
ANTEIL_SPANNEN = 0.70

#: ``sigma_pinf = 0.85 sigma_p0``, wo nichts eingegeben ist -- nach Vorgabe,
#: nicht nachgeschlagen (Benutzer, 2026-11-25).
ANTEIL_NACH_VERLUSTEN = 0.85

#: Was ein leeres Feld der Spannung heisst -- fuer den Platzhalter im
#: Zeichenfenster, solange noch kein Glied die Zahl kennt.
VORGABE_SPANNUNG = {
    "sigma_p0": f"{ANTEIL_SPANNEN:.2f}·f_pk",
    "sigma_pinf": f"{ANTEIL_NACH_VERLUSTEN:.2f}·σ_p0",
}

#: Gleichung (22): ``sigma_p0 <= min(0.75 f_pk; 0.85 f_p0.1k)``.
GRENZE_F_PK = 0.75
GRENZE_F_P01K = 0.85

#: 4.1.5.2.3: nach allen Verlusten mindestens ``0.45 f_pk``.
MINDESTENS_F_PK = 0.45

#: Die Kennwerte des Spannstahls, die die Herleitung der Glieder liest.
KENNWERTE = ("f_pk", "f_p01k", "E_p", "E_p_litze")

#: Was eine Tabelle oder ein Bild sagt, das die Dehnung eines Glieds zeigt:
#: es ist die des Betons an seiner Stelle, nicht die des Stahls.
DEHNUNG_AM_GLIED = (
    "Bei einem Spannglied ist ε die Dehnung des Betons an seiner Stelle: mit Verbund ist "
    "der Stahl um seine Vordehnung ε_p mehr gedehnt, ohne Verbund hängt seine Spannung "
    "nicht an ε.")

#: Die Seiten im Notizbuch, je Groesse eine: Querschnitt, Spannungen nach
#: Vorgabe, Vordehnung und Kraft eines Glieds, die Grenzen seiner Spannung,
#: sein Gesetz im Querschnitt -- dieses eine fuer alle drei Arten.
FLAECHE = "Querschnitt eines Spannglieds"
NACH_VORGABE_GESPANNT = "Spannung im Spannglied nach Vorgabe"
VORDEHNUNG = "Vordehnung eines Spannglieds"
SPANNKRAFT = "Spannkraft eines Spannglieds"
GRENZEN = "Grenzen der Spannung im Spannstahl"
IM_QUERSCHNITT = "Spannglied im Querschnitt"


class Spannwirkung(Wahl):
    """Wie ein Spannglied im Widerstand zaehlt -- siehe Dateikopf."""

    VORDEHNUNG = "vordehnung"
    RESTFESTIGKEIT = "restfestigkeit"

    @property
    def beschriftung(self) -> str:
        return {Spannwirkung.VORDEHNUNG: "mit Vordehnung",
                Spannwirkung.RESTFESTIGKEIT: "schlaff mit Restfestigkeit"}[self]

    @property
    def kurz(self) -> str:
        """Im Schalter des Zeichenfensters, wo der Platz knapp ist."""
        return {Spannwirkung.VORDEHNUNG: "Vordehnung", Spannwirkung.RESTFESTIGKEIT: "schlaff"}[self]

    @property
    def erklaerung(self) -> str:
        return {
            Spannwirkung.VORDEHNUNG:
                "Die Vorspannung zählt zum Widerstand: das Glied trägt schon σ_p∞, bevor "
                "eine Last wirkt – die Lastfälle ohne Vorspannung eingeben "
                f"({REFERENZ_WIDERSTAND}).",
            Spannwirkung.RESTFESTIGKEIT:
                "Die Vorspannung steht schon als Einwirkung in den Lastfällen: das Glied "
                f"trägt nur noch, was über σ_p∞ hinausgeht ({REFERENZ_EINWIRKUNG}).",
        }[self]


class Verbund(Wahl):
    """Ob das Glied mit dem Beton verbunden ist -- siehe Dateikopf."""

    MIT = "mit"
    OHNE = "ohne"

    @property
    def beschriftung(self) -> str:
        return {Verbund.MIT: "mit Verbund", Verbund.OHNE: "ohne Verbund"}[self]

    @property
    def kurz(self) -> str:
        """Im Schalter hinter dem Wort «Verbund»."""
        return {Verbund.MIT: "mit", Verbund.OHNE: "ohne"}[self]

    @property
    def erklaerung(self) -> str:
        return {
            Verbund.MIT: "Das Glied dehnt sich mit dem Beton an seiner Stelle "
                         f"({REFERENZ_VORDEHNUNG}).",
            Verbund.OHNE: "Es wirkt die Kraft nach allen Verlusten, ohne Zuwachs "
                          f"({REFERENZ_OHNE_VERBUND}).",
        }[self]


# ===========================================================================
# Die Regeln
# ===========================================================================


def vorspannung(f_pk: float, sigma_p0: Optional[float],
                sigma_pinf: Optional[float]) -> Tuple[float, float]:
    """
    ``sigma_p0`` und ``sigma_pinf``: eingegeben oder nach Vorgabe
    (:data:`ANTEIL_SPANNEN`, :data:`ANTEIL_NACH_VERLUSTEN`) -- in der
    Einheit von ``f_pk``, wie die Eingaben.
    """
    p0 = ANTEIL_SPANNEN * f_pk if sigma_p0 is None else sigma_p0
    return p0, (ANTEIL_NACH_VERLUSTEN * p0 if sigma_pinf is None else sigma_pinf)


def grenze_nach_spannen(f_pk: float, f_p01k: float) -> float:
    """``min(0.75 f_pk; 0.85 f_p0.1k)`` -- Gleichung (22)."""
    return min(GRENZE_F_PK * f_pk, GRENZE_F_P01K * f_p01k)


def grenzen_verletzt(p0: float, pinf: float, f_pk: float, f_p01k: float) -> List[str]:
    """
    Was an den Spannungen eines Glieds nicht stimmt, je ein Satz ohne Punkt
    -- alles in N/mm². Leer, wenn alles stimmt.
    """
    saetze = []
    grenze = grenze_nach_spannen(f_pk, f_p01k)
    if p0 > grenze * (1.0 + 1e-9):
        saetze.append(f"σ_p0 = {p0:.0f} N/mm² liegt über min(0.75·f_pk; 0.85·f_p0.1k) "
                      f"= {grenze:.0f} N/mm² (SIA 262:2025, 4.1.5.2.2, Gl. 22)")
    if pinf > p0 * (1.0 + 1e-9):
        saetze.append(f"σ_p∞ = {pinf:.0f} N/mm² liegt über σ_p0 = {p0:.0f} N/mm² – "
                      f"die Verluste mindern die Spannung")
    if pinf < MINDESTENS_F_PK * f_pk * (1.0 - 1e-9):
        saetze.append(f"σ_p∞ = {pinf:.0f} N/mm² liegt unter 0.45·f_pk = "
                      f"{MINDESTENS_F_PK * f_pk:.0f} N/mm² (SIA 262:2025, 4.1.5.2.3)")
    return saetze


def flaechendurchmesser(flaeche: float) -> float:
    """Der Durchmesser eines Kreises mit dieser Flaeche -- so gross zeichnet sich ein Glied."""
    return math.sqrt(4.0 * flaeche / math.pi)


# ===========================================================================
# Die Gesetze im Querschnitt
# ===========================================================================


@dataclass(frozen=True)
class VorgedehnterSpannstahl(Gesetz):
    """
    Ein Spannglied mit Verbund, ueber der Dehnung des Querschnitts an seiner
    Stelle: das Gesetz des Spannstahls (Figur 17), um die Vordehnung
    verschoben (4.1.5.1.5). Bei ``eps = 0`` traegt es ``sigma_pinf``.
    """

    NAME = IM_QUERSCHNITT
    WORT = "mit Vordehnung"
    REFERENZ = f"{REFERENZ_VORDEHNUNG}; {REFERENZ_WIDERSTAND}; 4.2.3.3, Figur 17"
    ROLLEN = ("f_p", "E_p", "eps_ud", "eps_p")
    WERTTITEL = "Werte des Spannglieds"

    stahl: Spannstahlgesetz
    eps_p: float
    """Die Vordehnung, positiv."""

    def abzug(self) -> float:
        """Was vom Gesetz abgeht -- mit Vordehnung nichts."""
        return 0.0

    def __post_init__(self) -> None:
        E, f, grenze = self.stahl.E_p, self.stahl.f_pd, self.stahl.eps_ud + RUNDUNG
        vor, ab = self.eps_p, self.abzug()
        leer = -ab if ab else 0.0   # ohne Abzug null, nicht «-0»

        def sigma(eps: float) -> float:
            gesamt = eps + vor
            if gesamt <= 0.0 or gesamt > grenze:
                return leer
            return min(gesamt * E, f) - ab
        _gebaut(self, sigma)

    @property
    def eps_yd(self) -> float:
        """Die Dehnung des Querschnitts, bei der das Glied zu fliessen beginnt."""
        return self.stahl.eps_pd - self.eps_p

    @property
    def eps_ud(self) -> float:
        """Die Dehnung des Querschnitts, bei der das Glied reisst."""
        return self.stahl.eps_ud - self.eps_p

    def formel(self, werte: Werte) -> str:
        return self.latex(werte["f_p"].symbol)

    def latex(self, zug: str = "f_{pd}") -> str:
        return (
            r"\sigma_p(\varepsilon) = \begin{cases}"
            rf" \min\left(E_p\,(\varepsilon + \varepsilon_p);\ {zug}\right)"
            r" & -\varepsilon_p < \varepsilon \le \varepsilon_{ud} - \varepsilon_p \\[1ex]"
            r" 0 & \varepsilon \le -\varepsilon_p \quad (\text{entspannt}) \\[1ex]"
            r" 0 & \varepsilon > \varepsilon_{ud} - \varepsilon_p"
            r" \quad (\text{jenseits der Bruchdehnung})"
            r" \end{cases}"
        )


@dataclass(frozen=True)
class Restfestigkeit(VorgedehnterSpannstahl):
    """
    Ein schlaffes Spannglied mit Verbund: was es ueber ``sigma_pinf`` hinaus
    traegt, wenn die Vorspannung schon als Einwirkung zaehlt (4.1.5.5.2) --
    das Gesetz mit Vordehnung, um ``sigma_pinf`` gesenkt.
    """

    WORT = "schlaff mit Restfestigkeit"
    REFERENZ = f"{REFERENZ_EINWIRKUNG}; {REFERENZ_VORDEHNUNG}; 4.2.3.3, Figur 17"
    ROLLEN = ("f_p", "E_p", "eps_ud", "eps_p", "sigma_pinf")

    sigma_pinf: float = 0.0
    """Die Spannung nach allen Verlusten in N/m² -- sie zaehlt schon als Einwirkung."""

    def abzug(self) -> float:
        return self.sigma_pinf

    def latex(self, zug: str = "f_{pd}") -> str:
        return (
            r"\sigma_p(\varepsilon) = \begin{cases}"
            rf" \min\left(E_p\,(\varepsilon + \varepsilon_p);\ {zug}\right) - \sigma_{{p\infty}}"
            r" & -\varepsilon_p < \varepsilon \le \varepsilon_{ud} - \varepsilon_p \\[1ex]"
            r" -\sigma_{p\infty} & \varepsilon \le -\varepsilon_p \quad (\text{entspannt}) \\[1ex]"
            r" -\sigma_{p\infty} & \varepsilon > \varepsilon_{ud} - \varepsilon_p"
            r" \quad (\text{jenseits der Bruchdehnung})"
            r" \end{cases}"
        )


@dataclass(frozen=True)
class FesteSpannung(Gesetz):
    """
    Ein Spannglied ohne Verbund: die Spannung nach allen Verlusten, gleich
    welche Dehnung der Querschnitt an seiner Stelle hat (4.1.5.1.6). Schlaff
    angesetzt ist sie null -- das Glied traegt nichts bei.
    """

    NAME = IM_QUERSCHNITT
    WORT = "ohne Verbund"
    REFERENZ = REFERENZ_OHNE_VERBUND
    ROLLEN = ("sigma_pinf",)
    WERTTITEL = "Werte des Spannglieds"

    sigma: float
    """Die feste Spannung in N/m²."""

    eps_yd: ClassVar[float] = math.inf
    """Es fliesst nie: seine Kraft haengt an keiner Dehnung."""

    def __post_init__(self) -> None:
        bleibt = self.sigma
        _gebaut(self, lambda eps: bleibt)

    def formel(self, werte: Werte) -> str:
        return r"\sigma_p(\varepsilon) = \sigma_{p\infty}"

    def protokoll(self, p: Protokoll, werte: Werte, *, titel: str, basis: str = "") -> None:
        if self.sigma == 0.0:
            p.text(f"{titel}: schlaff und ohne Verbund – das Glied trägt über die "
                   f"angesetzte Vorspannung hinaus nichts ({REFERENZ_OHNE_VERBUND}).")
            return
        super().protokoll(p, werte, titel=titel, basis=basis)


# ===========================================================================
# Das Glied
# ===========================================================================


@dataclass(frozen=True)
class Spannglied(Bewehrungselement):
    """
    Ein Spannglied der Zeichnung -- ``von`` und ``bis`` sind seine Lage,
    ``flaeche`` ist ``anzahl`` mal die des Erzeugnisses (Tabelle 7). Die
    Spannungen stehen, wie eingegeben, in N/mm²; ``None`` heisst Vorgabe.
    """

    erzeugnis: Erzeugnis
    anzahl: int
    wirkung: Spannwirkung
    verbund: Verbund
    sigma_p0: Optional[float]
    sigma_pinf: Optional[float]

    vorgespannt: ClassVar[bool] = True

    @property
    def punkte(self) -> Tuple[Tuple[float, float], ...]:
        return (self.von,)

    @property
    def lage(self) -> Mathe:
        return Mathe(f"({self.von[0]:g};\\ {self.von[1]:g})")

    @property
    def menge(self) -> Zelle:
        return Mathe(rf"{self.anzahl} \times \text{{{self.erzeugnis.art.beschriftung}}}"
                     rf"\ \varnothing {self.erzeugnis.durchmesser:g}")

    @property
    def kurzmenge(self) -> Zelle:
        return self.menge

    @property
    def rissdurchmesser(self) -> float:
        """Nur der Form halber: die Rissbreite pruefen die Staebe aus Betonstahl."""
        return self.erzeugnis.durchmesser

    @property
    def durchmesser(self) -> float:
        """Wie gross es sich zeichnet: ein Kreis mit seiner Flaeche (:func:`flaechendurchmesser`)."""
        return flaechendurchmesser(self.flaeche)

    def als_bewehrung(self, stahl: int, verdraengt: Verdraengt) -> List[Bewehrung]:
        """``stahl`` ist der Index seines eigenen Werkstoffs, nicht der seines Spannstahls."""
        return [Bewehrung(lage=(self.von[0] * MM, self.von[1] * MM),
                          flaeche=self.flaeche * MM * MM, werkstoff=stahl,
                          verdraengt=verdraengt(self.von))]


def aus_glied(g: Mapping, erzeugnis: Erzeugnis) -> Spannglied:
    """
    Ein Spannglied der Beschreibung (:meth:`QuerschnittsanalyseEintrag.elemente`),
    mit seinem Spannstahl als Baustoff unter ``stahl`` und seinem Erzeugnis.
    """
    lage = tuple(g["lage"])
    return Spannglied(
        name=g["name"], kennung=g["kennung"], stahl=g["stahl"], von=lage, bis=lage,
        flaeche=g["anzahl"] * erzeugnis.flaeche, erzeugnis=erzeugnis, anzahl=int(g["anzahl"]),
        wirkung=Spannwirkung(g["wirkung"]), verbund=Verbund(g["verbund"]),
        sigma_p0=g["sigma_p0"], sigma_pinf=g["sigma_pinf"])


# ===========================================================================
# Die Glieder einer Analyse: Herleitung, Werte, Werkstoffe
# ===========================================================================


class Spannglieder(Prozedur):
    """
    Die Spannglieder einer Analyse: je Glied ``A_p``, ``sigma_p0``,
    ``sigma_pinf``, ``eps_p`` und ``P_inf`` als Werte des Rechenwerks, mit
    ihrer Herleitung -- und daraus je Glied sein Werkstoff im Querschnitt
    (:meth:`werkstoffe`). Die Nachweise lesen die Werte ueber
    :meth:`gliedbezuege`, damit jede Spannkraft rueckverfolgbar bleibt.
    """

    def __init__(self, glieder: Sequence[Spannglied], *, basis: str,
                 abschnitt: Abschnitt) -> None:
        self.glieder = tuple(glieder)
        mehrere = len(self.glieder) > 1
        self.d: Dict[str, Dict[str, WertDef]] = {}
        for nummer, g in enumerate(self.glieder, start=1):
            index = f",{nummer}" if mehrere else ""

            def d(kurz: str, symbol: str, einheit, beschreibung: str, stellen: int = 0,
                  referenz: str = "", g=g) -> WertDef:
                return WertDef(id=f"{basis}.{g.kennung}.{kurz}", symbol=symbol,
                               einheit=einheit, beschreibung=f"{beschreibung}, {g.name}",
                               referenz=referenz, stellen=stellen)
            self.d[g.kennung] = {
                "A_p": d("A_p", f"A_{{p{index}}}", MM2, "Querschnitt des Spannstahls",
                         referenz=TABELLE_7),
                "sigma_p0": d("sigma_p0", f"\\sigma_{{p0{index}}}", N_PRO_MM2,
                              "Spannung nach dem Spannen"),
                "sigma_pinf": d("sigma_pinf", f"\\sigma_{{p\\infty{index}}}", N_PRO_MM2,
                                "Spannung nach allen Verlusten"),
                "eps_p": d("eps_p", f"\\varepsilon_{{p{index}}}", PROMILLE, "Vordehnung",
                           stellen=2, referenz=REFERENZ_VORDEHNUNG),
                "P_inf": d("P_inf", f"P_{{\\infty{index}}}", KN,
                           "Spannkraft nach allen Verlusten", stellen=1),
            }
        stoffe = {g.stahl.id: g.stahl for g in self.glieder}.values()
        super().__init__(
            f"{basis}.spannglieder",
            ausgaben=[d for je in self.d.values() for d in je.values()],
            bezuege=[s.bezug(k) for s in stoffe for k in KENNWERTE],
            titel="Spannglieder", abschnitt=abschnitt)

    # -- Fuer die Nachweise -------------------------------------------------------

    def gliedbezuege(self) -> List[Eingabebezug]:
        """Was ein Nachweis von jedem Glied liest: ``sigma_pinf``, ``eps_p`` und ``P_inf``."""
        return [Eingabebezug(f"{kurz}__{g.kennung}", self.d[g.kennung][kurz].id)
                for g in self.glieder for kurz in ("sigma_pinf", "eps_p", "P_inf")]

    def spannkraefte(self) -> List[Tuple[Spannglied, str]]:
        """
        Die Glieder, deren Kraft den Beton schon ohne Last drueckt -- die mit
        Vordehnung, mit oder ohne Verbund --, je mit der ID ihres ``P_inf``.
        Schlaff angesetzt steht die Vorspannung schon in den Lastfaellen.
        """
        return [(g, self.d[g.kennung]["P_inf"].id) for g in self.glieder
                if g.wirkung is Spannwirkung.VORDEHNUNG]

    def werkstoffe(self, wert: Callable[[str], float], wahl) -> List[Werkstoff]:
        """
        Je Glied sein Werkstoff, in der Folge der Glieder: das Gesetz nach
        Wirkung und Verbund, mit der Fliessgrenze des Wertesatzes seines
        Stahls und dem Modul seines Erzeugnisses. ``wert`` liefert zu einer
        Wert-ID die Zahl in SI.
        """
        heraus = []
        for g in self.glieder:
            sigma = wert(self.d[g.kennung]["sigma_pinf"].id)
            vordehnung = g.wirkung is Spannwirkung.VORDEHNUNG
            if g.verbund is Verbund.OHNE:
                heraus.append(Werkstoff(g.name, FesteSpannung(sigma=sigma if vordehnung else 0.0),
                                        -math.inf, math.inf, grenzname=g.name))
                continue
            w = lambda k, s=g.stahl: abs(wert(s.id_von(k)))
            stahl = Spannstahlgesetz(E_p=w(g.erzeugnis.modul),
                                     f_pd=w(wahl.satz(g.stahl).spannstahl), eps_ud=w("eps_ud"))
            eps_p = wert(self.d[g.kennung]["eps_p"].id)
            gesetz = (VorgedehnterSpannstahl(stahl=stahl, eps_p=eps_p) if vordehnung
                      else Restfestigkeit(stahl=stahl, eps_p=eps_p, sigma_pinf=sigma))
            heraus.append(Werkstoff(g.name, gesetz, -math.inf, gesetz.eps_ud,
                                    grenzname=g.name))
        return heraus

    def gesetze_protokollieren(self, p: Protokoll, e: Eingaben, wahl,
                               werkstoffe: Sequence[Werkstoff], *,
                               titel: Callable[[Spannglied], str], basis: str) -> None:
        """
        Je Glied sein Gesetz, mit seinen Werten -- ``werkstoffe`` die von
        :meth:`werkstoffe`, ``titel`` wie die Zeile eines Glieds heisst.
        """
        for g, w in zip(self.glieder, werkstoffe):
            stoff = g.stahl
            kurz = {"f_p": wahl.satz(stoff).spannstahl, "E_p": g.erzeugnis.modul,
                    "eps_ud": "eps_ud"}
            werte = {rolle: e[stoff.eingabename(k)] for rolle, k in kurz.items()}
            werte.update({rolle: e[f"{rolle}__{g.kennung}"] for rolle in ("eps_p", "sigma_pinf")})
            w.gesetz.protokoll(p, {r: werte[r] for r in w.gesetz.ROLLEN}, titel=titel(g),
                               basis=f"{basis}.{g.kennung}")

    # -- Die Herleitung ---------------------------------------------------------

    def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]:
        p.erklaerung(
            "Die Zugkraft im Spannstahl zählt zum Widerstand des Querschnitts; die "
            "Lastfälle stehen darum ohne Vorspannung da. Mit Verbund dehnt sich ein "
            "Glied mit dem Beton an seiner Stelle und trägt dazu seine Vordehnung: "
            "bei der Dehnung null des Querschnitts schon σ_p∞. Ohne Verbund wirkt die "
            "Kraft nach allen Verlusten, ohne Zuwachs. Schlaff angesetzt – wenn die "
            "Vorspannung schon als Einwirkung in den Lastfällen steht – trägt ein Glied "
            "nur, was über σ_p∞ hinausgeht.")
        p.ansatz(r"A_p = n \cdot a_p \qquad \varepsilon_p = \frac{\sigma_{p\infty}}{E_p}"
                 r" \qquad P_\infty = A_p \cdot \sigma_{p\infty}",
                 titel="Querschnitt, Vordehnung und Spannkraft eines Glieds aus n Drähten, "
                       "Litzen oder Stäben",
                 referenz=f"{TABELLE_7}; {REFERENZ_VORDEHNUNG}", name=SPANNKRAFT)
        vorgabe = [g for g in self.glieder if g.sigma_p0 is None or g.sigma_pinf is None]
        if vorgabe:
            p.ansatz(rf"\sigma_{{p0}} = {ANTEIL_SPANNEN:.2f} \cdot f_{{pk}} \qquad "
                     rf"\sigma_{{p\infty}} = {ANTEIL_NACH_VERLUSTEN:.2f} \cdot \sigma_{{p0}}",
                     titel="Spannungen nach Vorgabe, wo keine eingegeben ist",
                     referenz=NACH_VORGABE, name=NACH_VORGABE_GESPANNT)
            p.annahme(f"{', '.join(g.name for g in vorgabe)}: Spannung nach Vorgabe – die "
                      f"Verluste hängen am Bauwerk ({REFERENZ_VERLUSTE}), die Vorgabe "
                      "ersetzt ihre Rechnung nicht.")
        p.annahme("Die Vordehnung ist σ_p∞/E_p: die Stauchung des Betons beim Vorspannen "
                  f"fällt weg ({NACH_VORGABE}).")
        p.ansatz(r"\sigma_{p0} \le \min\left(0.75 \cdot f_{pk};\ 0.85 \cdot f_{p0.1k}\right)"
                 r" \qquad \sigma_{p\infty} \ge 0.45 \cdot f_{pk}",
                 titel="Grenzen der Spannung nach dem Spannen und nach allen Verlusten",
                 referenz=f"{REFERENZ_NACH_SPANNEN}; {REFERENZ_NACH_VERLUSTEN}", name=GRENZEN)
        ergebnis: Dict[str, Groesse] = {}
        zeilen = [self._glied(e, p, g, ergebnis) for g in self.glieder]
        p.tabelle(
            kopf=["Glied", Mathe(r"\text{Lage}\ [\mathrm{mm}]"), "Spannstahl",
                  Mathe(r"A_p\ [\mathrm{mm}^2]"), Mathe(r"\sigma_{p\infty}\ [\mathrm{N/mm^2}]"),
                  Mathe(r"\varepsilon_p\ [\text{‰}]"), Mathe(r"P_\infty\ [\mathrm{kN}]"),
                  "Wirkung", "Verbund"],
            zeilen=zeilen, titel="Spannglieder", ausrichtung="lllrrrrll")
        return ergebnis

    def _glied(self, e: Eingaben, p: Protokoll, g: Spannglied,
               ergebnis: Dict[str, Groesse]) -> List[Zelle]:
        """Die Werte eines Glieds, hergeleitet -- und seine Zeile der Tabelle."""
        d, stoff = self.d[g.kennung], g.stahl
        werte = Zwischenwerte(f"{self.id}.{g.kennung}")
        f_pk, f_p01k = e[stoff.eingabename("f_pk")], e[stoff.eingabename("f_p01k")]
        E_p = e[stoff.eingabename(g.erzeugnis.modul)]

        def belegt(kurz: str, groesse: Groesse) -> Wert:
            ergebnis[d[kurz].id] = groesse
            return d[kurz].belegen(groesse)

        art = g.erzeugnis.art
        erzeugnis = f"{g.anzahl} × {art.beschriftung} ⌀{g.erzeugnis.durchmesser:g}"
        A_p = belegt("A_p", Groesse(g.flaeche, MM2))
        p.formel(A_p, r"@n \cdot @a_p",
                 {"n": werte.zahl("n", "n", g.anzahl, "Anzahl der Drähte, Litzen oder Stäbe",
                                  stellen=0),
                  "a_p": werte.flaeche("a_p", "a_p", g.erzeugnis.flaeche * 1e-6,
                                       "Querschnitt eines Drahts, einer Litze oder eines Stabs",
                                       stellen=1)},
                 titel=f"{g.name}: {erzeugnis} aus {stoff.name}", name=FLAECHE)

        p0_si, pinf_si = vorspannung(
            f_pk.groesse.si,
            None if g.sigma_p0 is None else g.sigma_p0 * 1e6,
            None if g.sigma_pinf is None else g.sigma_pinf * 1e6)
        p0 = belegt("sigma_p0", Groesse.aus_si(p0_si, N_PRO_MM2))
        if g.sigma_p0 is None:
            p.formel(p0, rf"{ANTEIL_SPANNEN:.2f} \cdot @f_pk", {"f_pk": f_pk},
                     titel=f"{g.name}: nach dem Spannen, nach Vorgabe", referenz=NACH_VORGABE,
                     name=NACH_VORGABE_GESPANNT)
        else:
            p.wert(p0, titel=f"{g.name}: nach dem Spannen, eingegeben")
        pinf = belegt("sigma_pinf", Groesse.aus_si(pinf_si, N_PRO_MM2))
        if g.sigma_pinf is None:
            p.formel(pinf, rf"{ANTEIL_NACH_VERLUSTEN:.2f} \cdot @p0", {"p0": p0},
                     titel=f"{g.name}: nach allen Verlusten, nach Vorgabe",
                     referenz=NACH_VORGABE, name=NACH_VORGABE_GESPANNT)
        else:
            p.wert(pinf, titel=f"{g.name}: nach allen Verlusten, eingegeben",
                   referenz=REFERENZ_VERLUSTE)

        grenze = werte.spannung("grenze", r"\sigma_{p,max}", grenze_nach_spannen(
            f_pk.groesse.si, f_p01k.groesse.si))
        p.formel(grenze, r"\min\left(0.75 \cdot @f_pk;\ 0.85 \cdot @f_p01k\right)",
                 {"f_pk": f_pk, "f_p01k": f_p01k}, titel=f"{g.name}: Grenze nach dem Spannen",
                 referenz=REFERENZ_NACH_SPANNEN, name=GRENZEN,
                 nachsatz=vergleich(r"\ge", angabe(p0), p0_si <= grenze.groesse.si * (1 + 1e-9)))
        unten = werte.spannung("mindestens", r"\sigma_{p,min}", MINDESTENS_F_PK * f_pk.groesse.si)
        p.formel(unten, r"0.45 \cdot @f_pk", {"f_pk": f_pk},
                 titel=f"{g.name}: Mindestspannung nach allen Verlusten",
                 referenz=REFERENZ_NACH_VERLUSTEN, name=GRENZEN,
                 nachsatz=vergleich(r"\le", angabe(pinf),
                                    pinf_si >= unten.groesse.si * (1 - 1e-9)))
        for satz in grenzen_verletzt(p0_si / 1e6, pinf_si / 1e6, f_pk.groesse.si / 1e6,
                                     f_p01k.groesse.si / 1e6):
            p.warnung(f"{g.name}: {satz}.")

        eps_p = belegt("eps_p", Groesse.aus_si(pinf_si / E_p.groesse.si, PROMILLE))
        p.formel(eps_p, r"\frac{@pinf}{@E_p}", {"pinf": pinf, "E_p": E_p},
                 titel=f"{g.name}: Vordehnung, mit dem Modul der {art.mehrzahl}",
                 referenz=REFERENZ_VORDEHNUNG, name=VORDEHNUNG)
        P = belegt("P_inf", Groesse.aus_si(g.flaeche * 1e-6 * pinf_si, KN))
        p.formel(P, r"@A_p \cdot @pinf", {"A_p": A_p, "pinf": pinf},
                 titel=f"{g.name}: Spannkraft nach allen Verlusten", name=SPANNKRAFT)
        return [g.name, g.lage, f"{erzeugnis}, {stoff.name}", Mathe(fest(g.flaeche, 0)),
                Mathe(fest(pinf_si / 1e6, 0)), Mathe(fest(eps_p.groesse.si * 1e3, 2)),
                Mathe(fest(P.groesse.si / 1e3, 1)), g.wirkung.beschriftung,
                g.verbund.beschriftung]
