"""
opencivil/querschnitt/spannglieder.py -- Spannglieder im gezeichneten Querschnitt.

VERANTWORTUNG:
Ein Spannglied der Querschnittsanalyse (:class:`Spannglied`): wo es liegt,
aus welchem Erzeugnis und wie vielen davon oder mit welcher Flaeche, wie es
wirkt -- und was daraus folgt: die Spannung nach dem Spannen und nach allen
Verlusten, die Vordehnung, die Kraft, sein Gesetz im Querschnitt und seine
Grenzdehnung. Jede Regel dazu steht hier, einmal: die Herleitung
(:class:`Spannglieder`), der Aufbau und das Zeichenfenster
(:mod:`opencivil.web.zeichengeometrie`) fragen alle hier (:func:`was_fehlt`,
:func:`aus_glied`, :func:`vorspannung`, :func:`grenzen_verletzt`).

DIE FLAECHE (:class:`Flaechenangabe`):
Aus einem Erzeugnis -- ein Draht, eine Litze oder ein Stab, den Tabelle 7
fuer die Sorte nennt, mit seiner Flaeche aus der Tabelle, und wie viele
davon --, oder eingegeben, etwa fuer ein Glied aus zwoelf Litzen oder ein
Erzeugnis, das die Tabelle nicht fuehrt. Dann zaehlt nur noch die Art: von
ihr haengt E_p ab, 195 000 N/mm² fuer Litzen, 200 000 fuer Draehte und
Staebe (3.3.2.4). Die Art muss es in der Sorte geben, wie das Erzeugnis.

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

DIE SPANNUNGEN:
Eingegeben sind zwei Faktoren, je hoechstens 1: ``sigma_p0 = k_p0 f_pk``
und ``sigma_pinf = k_pinf sigma_p0``. Vorgabe ``k_p0 = 0.70`` und ``k_pinf
= 0.85`` -- nach Vorgabe, nicht nachgeschlagen (Benutzer, 2026-11-25). Die
Verluste haengen am Bauwerk (4.1.5.3); die Vorgabe ersetzt ihre Rechnung
nicht. Bis 2026-11-27 waren die Spannungen selbst die Felder, leer die
Vorgabe: so blieb die Zahl nach einem Wechsel der Sorte stehen, und
``sigma_pinf`` durfte ``sigma_p0`` nicht uebersteigen -- mit einem Faktor
bis 1 kann es das nicht. Die Vordehnung ist ``sigma_pinf/E_p`` mit dem
Modul der Art: die Stauchung des Betons beim Vorspannen faellt weg -- nach
Vorgabe, nicht nachgeschlagen.

DIE NEIGUNG:
Ein Glied mit Vordehnung darf gegen die Stabachse geneigt sein, um
``beta_p`` in der lotrechten Ebene (Figur 18). Seine lotrechte Kraft
``F · sin beta_p`` zaehlt in der Querkraft (:func:`lotrecht`):
``beta_p > 0`` heisst, sie wirkt wie ein positives ``V_z``. Wirkt sie in
einem Lastfall wie dessen ``V_z``, traegt sie es mit, mit ``F = P_inf``
(:func:`guenstig`; 4.3.3.4.8, Gleichung (50)); wirkt sie entgegen, kommt
sie dazu, mit der groessten Kraft im Glied (4.3.3.4.9) -- was der
Nachweis der Schubwaende rechnet
(:mod:`opencivil.nachweis.schubwandnachweis`). Schlaff zaehlt die Neigung
nicht: dort steht die Vorspannung schon samt ihr in den Lastfaellen
(Benutzer, 2026-11-25). Im Biegewiderstand und im Gebrauch zaehlt ein
geneigtes Glied, als laege es laengs: ``cos beta_p`` ist bis
:data:`GRENZE_NEIGUNG` mindestens 0.94 -- nach Vorgabe, nicht
nachgeschlagen.

DIE GRENZEN:
Nach dem Spannen ``sigma_p0 <= min(0.75 f_pk; 0.85 f_p0.1k)`` (4.1.5.2.2,
Gleichung (22)), nach allen Verlusten ``sigma_pinf >= 0.45 f_pk``
(4.1.5.2.3). Wer sie verletzt, bekommt einen roten Hinweis am Glied und
in der Herleitung; gerechnet wird mit seinen Zahlen.

EINHEITEN:
Lage und Durchmesser in mm, Flaechen in mm², die Spannungen in N/mm² --
wie in der Zeichnung. Die Gesetze rechnen in SI.
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
from opencivil.material.basis import Baustoff
from opencivil.material.spannstahl import (
    TABELLE_7, Erzeugnis, Erzeugnisart, erzeugnis, erzeugnisarten,
)
from opencivil.querschnitt.bewehrungselemente import (
    MM, Bewehrungselement, Flaechen, Verdraengt, quadrate,
)
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
REFERENZ_GUENSTIG = "SIA 262:2025, 4.3.3.4.8, (50)"
REFERENZ_UNGUENSTIG = "SIA 262:2025, 4.3.3.4.9"
NACH_VORGABE = "nach Vorgabe, nicht nachgeschlagen"

#: ``k_p0``, womit ein neues Glied beginnt: ``sigma_p0 = 0.70 f_pk`` -- nach
#: Vorgabe, nicht nachgeschlagen (Benutzer, 2026-11-25).
ANTEIL_SPANNEN = 0.70

#: ``k_pinf``, womit ein neues Glied beginnt: ``sigma_pinf = 0.85 sigma_p0``
#: -- nach Vorgabe, nicht nachgeschlagen (Benutzer, 2026-11-25).
ANTEIL_NACH_VERLUSTEN = 0.85

#: Wie die Faktoren im Zeichenfenster stehen -- «σ_p0 = [0.70] · f_pk =
#: 1302 N/mm²»: vor und nach dem Feld, und welche Spannung des Glieds die
#: Zeile dahinter nennt, sobald der Kern sie kennt.
FAKTOREN = (
    {"feld": "anteil_p0", "vor": "σ_p0 =", "nach": "· f_pk", "spannung": "sigma_p0",
     "titel": f"Die Spannung nach dem Spannen als Anteil von f_pk, höchstens 1 – Vorgabe "
              f"{ANTEIL_SPANNEN:.2f}, nach Vorgabe, nicht nachgeschlagen"},
    {"feld": "anteil_pinf", "vor": "σ_p∞ =", "nach": "· σ_p0", "spannung": "sigma_pinf",
     "titel": f"Die Spannung nach allen Verlusten als Anteil von σ_p0, höchstens 1 – Vorgabe "
              f"{ANTEIL_NACH_VERLUSTEN:.2f}, nach Vorgabe, nicht nachgeschlagen; die Verluste "
              f"hängen am Bauwerk (SIA 262:2025, 4.1.5.3)"},
)

#: Gleichung (22): ``sigma_p0 <= min(0.75 f_pk; 0.85 f_p0.1k)``.
GRENZE_F_PK = 0.75
GRENZE_F_P01K = 0.85

#: 4.1.5.2.3: nach allen Verlusten mindestens ``0.45 f_pk``.
MINDESTENS_F_PK = 0.45

#: Wie steil ein Glied hoechstens liegt, in Grad, nach oben wie nach unten:
#: bis dahin zaehlt es im Biegewiderstand laengs, ``cos 20° = 0.94`` -- nach
#: Vorgabe, nicht nachgeschlagen.
GRENZE_NEIGUNG = 20.0

#: Die Kennwerte des Spannstahls, die die Herleitung der Glieder liest.
KENNWERTE = ("f_pk", "f_p01k", "E_p", "E_p_litze")

#: Was das Feld der Neigung im Zeichenfenster sagt: als Titel, in einer
#: Zeile darunter -- und an seiner Stelle, wo sie nicht zaehlt.
NEIGUNG_ERKLAERT = {
    "titel": f"Neigung gegen die Stabachse in Grad, höchstens {GRENZE_NEIGUNG:.0f}° – positiv, "
             "wo die lotrechte Kraft des Glieds wie ein positives V_z wirkt: dann trägt sie "
             f"es mit ({REFERENZ_GUENSTIG}); wirkt sie entgegen, vergrössert sie die Kraft "
             f"der Wände ({REFERENZ_UNGUENSTIG}).",
    "hinweis": "β_p > 0: die lotrechte Kraft des Glieds wirkt wie ein positives V_z.",
    "ohne": "Schlaff zählt die Neigung nicht: sie steht mit der Vorspannung in den Lastfällen.",
}

#: Was eine Tabelle oder ein Bild sagt, das die Dehnung eines Glieds zeigt:
#: es ist die des Betons an seiner Stelle, nicht die des Stahls.
DEHNUNG_AM_GLIED = (
    "Bei einem Spannglied ist ε die Dehnung des Betons an seiner Stelle: mit Verbund ist "
    "der Stahl um seine Vordehnung ε_p mehr gedehnt, ohne Verbund hängt seine Spannung "
    "nicht an ε.")

#: Die Seiten im Notizbuch, je Groesse eine: Querschnitt, Spannungen,
#: Vordehnung und Kraft eines Glieds, die Grenzen seiner Spannung, sein
#: Gesetz im Querschnitt -- dieses eine fuer alle drei Arten.
FLAECHE = "Querschnitt eines Spannglieds"
GESPANNT = "Spannung im Spannglied"
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
    def mit_neigung(self) -> bool:
        """Ob die Neigung zaehlt -- nur mit Vordehnung, siehe Dateikopf."""
        return self is Spannwirkung.VORDEHNUNG

    @property
    def erklaerung(self) -> str:
        return {
            Spannwirkung.VORDEHNUNG:
                "Die Vorspannung zählt zum Widerstand: das Glied trägt schon σ_p∞, bevor "
                "eine Last wirkt – die Lastfälle ohne Vorspannung eingeben "
                f"({REFERENZ_WIDERSTAND}).",
            Spannwirkung.RESTFESTIGKEIT:
                "Die Vorspannung steht schon als Einwirkung in den Lastfällen, samt dem, "
                "was ihre Neigung zur Querkraft beiträgt: das Glied trägt nur noch, was "
                f"über σ_p∞ hinausgeht ({REFERENZ_EINWIRKUNG}).",
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


class Flaechenangabe(Wahl):
    """Woher die Flaeche eines Glieds kommt -- siehe Dateikopf."""

    ERZEUGNIS = "erzeugnis"
    FLAECHE = "flaeche"

    @property
    def beschriftung(self) -> str:
        return {Flaechenangabe.ERZEUGNIS: "Erzeugnis", Flaechenangabe.FLAECHE: "Fläche A_p"}[self]

    @property
    def erklaerung(self) -> str:
        return {
            Flaechenangabe.ERZEUGNIS:
                "Drähte, Litzen oder Stäbe, die Tabelle 7 für die Sorte nennt, je mit ihrer "
                f"Fläche aus der Tabelle, und wie viele davon ({TABELLE_7}).",
            Flaechenangabe.FLAECHE:
                "Die Fläche A_p eingegeben, dazu nur die Art: von ihr hängt E_p ab "
                "(SIA 262:2025, 3.3.2.4).",
        }[self]


# ===========================================================================
# Die Regeln
# ===========================================================================


def vorspannung(f_pk: float, anteil_p0: float, anteil_pinf: float) -> Tuple[float, float]:
    """
    ``sigma_p0 = k_p0 f_pk`` und ``sigma_pinf = k_pinf sigma_p0`` -- in der
    Einheit von ``f_pk``.
    """
    p0 = anteil_p0 * f_pk
    return p0, anteil_pinf * p0


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
    if pinf < MINDESTENS_F_PK * f_pk * (1.0 - 1e-9):
        saetze.append(f"σ_p∞ = {pinf:.0f} N/mm² liegt unter 0.45·f_pk = "
                      f"{MINDESTENS_F_PK * f_pk:.0f} N/mm² (SIA 262:2025, 4.1.5.2.3)")
    return saetze


def was_fehlt(g: Mapping) -> str:
    """
    Warum ein Glied der Beschreibung noch nicht rechnet, als Satzteil -- leer,
    wenn es rechnet. ``g["stahl"]`` ist sein Spannstahl als Baustoff. Es fehlt
    nur eine Wahl: ein Erzeugnis, das Tabelle 7 fuer die Sorte nennt, oder,
    wo die Flaeche eingegeben ist, eine Art, die es in ihr gibt -- etwa nach
    dem Wechsel zu Y1030, das es nur in Staeben gibt.
    """
    stahl: Baustoff = g["stahl"]
    nennt = (f"{stahl.name} (Sorte {stahl.sorte})" if stahl.sorte and stahl.sorte != stahl.name
             else stahl.name)
    if Flaechenangabe(g["flaechenangabe"]) is Flaechenangabe.FLAECHE:
        art = Erzeugnisart(g["art"])
        if art in erzeugnisarten(stahl.sorte):
            return ""
        return f"{nennt} gibt es nicht als {art.beschriftung} (Tabelle 7) – eine Art wählen"
    if erzeugnis(stahl.sorte, g["durchmesser"]) is not None:
        return ""
    return (f"{nennt} gibt es nicht mit ⌀{g['durchmesser']:g} mm (Tabelle 7) – "
            f"einen Durchmesser wählen")


def _stellen(zahl: float) -> int:
    """Mit so vielen Stellen steht ein Faktor in der Herleitung: zwei, mehr nur wo er sie hat."""
    return next((s for s in (2, 3) if abs(round(zahl, s) - zahl) < 1e-12), 4)


def geneigt(g: "Spannglied") -> bool:
    """Ob ein Glied mit seiner Neigung in der Querkraft zaehlt -- siehe Dateikopf."""
    return g.wirkung.mit_neigung and g.neigung != 0.0


def lotrecht(kraft: float, neigung: float) -> float:
    """Die lotrechte Kraft eines Glieds, das ``kraft`` traegt und um ``neigung`` Grad geneigt ist."""
    return kraft * math.sin(math.radians(neigung))


def guenstig(neigung: float, V_z: float) -> bool:
    """
    Ob die lotrechte Kraft eines Glieds die Querkraft ``V_z`` mittraegt:
    beide gleich gerichtet. Ohne ``V_z`` kommt sie dazu -- unguenstig.
    """
    return lotrecht(1.0, neigung) * V_z > 0.0


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
    ``flaeche`` ist ``anzahl`` mal die des Erzeugnisses (Tabelle 7) oder
    eingegeben. Die Spannungen stehen als Faktoren da, siehe Dateikopf.
    """

    art: Erzeugnisart
    """Draht, Litze oder Stab: daran haengt E_p (3.3.2.4)."""

    erzeugnis: Optional[Erzeugnis]
    """Die Zeile von Tabelle 7 -- ``None``, wo die Flaeche eingegeben ist."""

    anzahl: int
    """Wie viele Stuecke des Erzeugnisses; wo die Flaeche eingegeben ist, zaehlt sie nicht."""

    wirkung: Spannwirkung
    verbund: Verbund
    anteil_p0: float
    """``k_p0``: ``sigma_p0 = k_p0 f_pk``."""

    anteil_pinf: float
    """``k_pinf``: ``sigma_pinf = k_pinf sigma_p0``."""

    neigung: float
    """``beta_p`` in Grad, siehe Dateikopf."""

    vorgespannt: ClassVar[bool] = True

    @property
    def punkte(self) -> Tuple[Tuple[float, float], ...]:
        return (self.von,)

    @property
    def lage(self) -> Mathe:
        return Mathe(f"({self.von[0]:g};\\ {self.von[1]:g})")

    @property
    def stuecke(self) -> str:
        """Woraus es besteht: «4 × Litze ⌀15.7» -- mit eingegebener Flaeche die Art, «Litzen»."""
        if self.erzeugnis is None:
            return self.art.mehrzahl
        return f"{self.anzahl} × {self.art.beschriftung} ⌀{self.erzeugnis.durchmesser:g}"

    @property
    def bezeichnung(self) -> str:
        """Wie Tabelle 7 es nennt, «Y1860S7-15.7» -- mit eingegebener Flaeche die Art, «Litzen»."""
        if self.erzeugnis is None:
            return self.art.mehrzahl
        return self.erzeugnis.bezeichnung(self.stahl.sorte)

    @property
    def menge(self) -> Zelle:
        if self.erzeugnis is None:
            return Mathe(rf"\text{{{self.art.mehrzahl}}}")
        return Mathe(rf"{self.anzahl} \times \text{{{self.art.beschriftung}}}"
                     rf"\ \varnothing {self.erzeugnis.durchmesser:g}")

    @property
    def kurzmenge(self) -> Zelle:
        return self.menge

    @property
    def rissdurchmesser(self) -> float:
        """Nur der Form halber: die Rissbreite pruefen die Staebe aus Betonstahl."""
        return self.durchmesser if self.erzeugnis is None else self.erzeugnis.durchmesser

    @property
    def durchmesser(self) -> float:
        """Wie gross es sich zeichnet: ein Kreis mit seiner Flaeche (:func:`flaechendurchmesser`)."""
        return flaechendurchmesser(self.flaeche)

    def als_bewehrung(self, stahl: int, verdraengt: Verdraengt) -> List[Bewehrung]:
        """``stahl`` ist der Index seines eigenen Werkstoffs, nicht der seines Spannstahls."""
        return [Bewehrung(lage=(self.von[0] * MM, self.von[1] * MM),
                          flaeche=self.flaeche * MM * MM, werkstoff=stahl,
                          verdraengt=verdraengt(self.von))]

    def stahlflaechen(self) -> Flaechen:
        """Ein Quadrat seiner Flaeche, wie ein Stab -- im Verbund rechnet das Werkzeug keins."""
        return quadrate(self.punkte, self.durchmesser)


def aus_glied(g: Mapping) -> Spannglied:
    """
    Ein Spannglied der Beschreibung (:meth:`QuerschnittsanalyseEintrag.elemente`),
    mit seinem Spannstahl als Baustoff unter ``stahl`` -- eines, dem nichts
    fehlt (:func:`was_fehlt`): sein Erzeugnis kommt aus Tabelle 7.
    """
    lage = tuple(g["lage"])
    if Flaechenangabe(g["flaechenangabe"]) is Flaechenangabe.FLAECHE:
        gewaehlt, art, flaeche = None, Erzeugnisart(g["art"]), float(g["flaeche"])
    else:
        gewaehlt = erzeugnis(g["stahl"].sorte, g["durchmesser"])
        if gewaehlt is None:
            raise ValueError(f"{g['name']}: {was_fehlt(g)}.")
        art, flaeche = gewaehlt.art, g["anzahl"] * gewaehlt.flaeche
    return Spannglied(
        name=g["name"], kennung=g["kennung"], stahl=g["stahl"], von=lage, bis=lage,
        flaeche=flaeche, art=art, erzeugnis=gewaehlt, anzahl=int(g["anzahl"]),
        wirkung=Spannwirkung(g["wirkung"]), verbund=Verbund(g["verbund"]),
        anteil_p0=g["anteil_p0"], anteil_pinf=g["anteil_pinf"], neigung=g["neigung"])


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
        self.d: Dict[str, Dict[str, WertDef]] = {}
        for g in self.glieder:
            index = self.index(g)

            def d(kurz: str, symbol: str, einheit, beschreibung: str, stellen: int = 0,
                  referenz: str = "", g=g) -> WertDef:
                return WertDef(id=f"{basis}.{g.kennung}.{kurz}", symbol=symbol,
                               einheit=einheit, beschreibung=f"{beschreibung}, {g.name}",
                               referenz=referenz, stellen=stellen)
            self.d[g.kennung] = {
                "A_p": d("A_p", f"A_{{p{index}}}", MM2, "Querschnitt des Spannstahls",
                         referenz=TABELLE_7 if g.erzeugnis is not None else ""),
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

    def index(self, g: Spannglied) -> str:
        """Was an den Symbolen eines Glieds unten steht: «,2» -- bei nur einem nichts."""
        return f",{self.glieder.index(g) + 1}" if len(self.glieder) > 1 else ""

    # -- Fuer die Nachweise -------------------------------------------------------

    def gliedbezuege(self, kurze: Sequence[str] = ("sigma_pinf", "eps_p", "P_inf"),
                     glieder: Optional[Sequence[Spannglied]] = None) -> List[Eingabebezug]:
        """
        Was ein Nachweis von den Gliedern liest, als ``{kurz}__{kennung}`` --
        jeder ``sigma_pinf``, ``eps_p`` und ``P_inf`` von allen; wer mehr
        braucht, nennt die Werte und die Glieder.
        """
        return [Eingabebezug(f"{kurz}__{g.kennung}", self.d[g.kennung][kurz].id)
                for g in (self.glieder if glieder is None else glieder) for kurz in kurze]

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
            stahl = Spannstahlgesetz(E_p=w(g.art.modul),
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
            kurz = {"f_p": wahl.satz(stoff).spannstahl, "E_p": g.art.modul,
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
                 titel="Querschnitt, Vordehnung und Spannkraft eines Glieds – A_p aus n Drähten, "
                       "Litzen oder Stäben oder eingegeben",
                 referenz=f"{TABELLE_7}; {REFERENZ_VORDEHNUNG}", name=SPANNKRAFT)
        p.ansatz(r"\sigma_{p0} = k_{p0} \cdot f_{pk} \qquad "
                 r"\sigma_{p\infty} = k_{p\infty} \cdot \sigma_{p0}",
                 titel="Spannungen nach dem Spannen und nach allen Verlusten, aus den Faktoren "
                       "des Glieds", name=GESPANNT)
        vorgabe = [g.name for g in self.glieder if g.anteil_pinf == ANTEIL_NACH_VERLUSTEN]
        if vorgabe:
            p.annahme(f"{', '.join(vorgabe)}: k_p∞ = {ANTEIL_NACH_VERLUSTEN:.2f} nach Vorgabe, "
                      f"{(1.0 - ANTEIL_NACH_VERLUSTEN) * 100:.0f} % Verlust – die Verluste "
                      f"hängen am Bauwerk ({REFERENZ_VERLUSTE}), die Vorgabe ersetzt ihre "
                      "Rechnung nicht.")
        p.annahme("Die Vordehnung ist σ_p∞/E_p: die Stauchung des Betons beim Vorspannen "
                  f"fällt weg ({NACH_VORGABE}).")
        if any(geneigt(g) for g in self.glieder):
            p.annahme("Geneigt zählt ein Glied im Biegewiderstand und im Gebrauch, als läge "
                      f"es längs: cos β_p ≈ 1, bis {GRENZE_NEIGUNG:.0f}° mindestens "
                      f"{math.cos(math.radians(GRENZE_NEIGUNG)):.2f} ({NACH_VORGABE}). Seine "
                      "lotrechte Kraft nimmt der Nachweis der Querkraft mit "
                      f"({REFERENZ_GUENSTIG}; {REFERENZ_UNGUENSTIG}).")
        p.ansatz(r"\sigma_{p0} \le \min\left(0.75 \cdot f_{pk};\ 0.85 \cdot f_{p0.1k}\right)"
                 r" \qquad \sigma_{p\infty} \ge 0.45 \cdot f_{pk}",
                 titel="Grenzen der Spannung nach dem Spannen und nach allen Verlusten",
                 referenz=f"{REFERENZ_NACH_SPANNEN}; {REFERENZ_NACH_VERLUSTEN}", name=GRENZEN)
        ergebnis: Dict[str, Groesse] = {}
        zeilen = [self._glied(e, p, g, ergebnis) for g in self.glieder]
        kopf = ["Glied", Mathe(r"\text{Lage}\ [\mathrm{mm}]"), "Spannstahl",
                Mathe(r"A_p\ [\mathrm{mm}^2]"), Mathe(r"\sigma_{p\infty}\ [\mathrm{N/mm^2}]"),
                Mathe(r"\varepsilon_p\ [\text{‰}]"), Mathe(r"P_\infty\ [\mathrm{kN}]"),
                "Wirkung", "Verbund"]
        if any(geneigt(g) for g in self.glieder):
            # Die Neigung nur, wo eine zaehlt -- schlaff steht ein Strich.
            kopf.append(Mathe(r"\beta_p\ [{}^{\circ}]"))
            for g, zeile in zip(self.glieder, zeilen):
                zeile.append(Mathe(fest(g.neigung, 1)) if g.wirkung.mit_neigung else "–")
        p.tabelle(kopf=kopf, zeilen=zeilen, titel="Spannglieder",
                  ausrichtung="lllrrrrll" + "r" * (len(kopf) - 9))
        return ergebnis

    def _glied(self, e: Eingaben, p: Protokoll, g: Spannglied,
               ergebnis: Dict[str, Groesse]) -> List[Zelle]:
        """Die Werte eines Glieds, hergeleitet -- und seine Zeile der Tabelle."""
        d, stoff = self.d[g.kennung], g.stahl
        werte = Zwischenwerte(f"{self.id}.{g.kennung}")
        f_pk, f_p01k = e[stoff.eingabename("f_pk")], e[stoff.eingabename("f_p01k")]
        E_p = e[stoff.eingabename(g.art.modul)]

        def belegt(kurz: str, groesse: Groesse) -> Wert:
            ergebnis[d[kurz].id] = groesse
            return d[kurz].belegen(groesse)

        art = g.art
        A_p = belegt("A_p", Groesse(g.flaeche, MM2))
        if g.erzeugnis is None:
            p.wert(A_p, titel=f"{g.name}: {art.mehrzahl} aus {stoff.name}, die Fläche eingegeben")
        else:
            p.formel(A_p, r"@n \cdot @a_p",
                     {"n": werte.zahl("n", "n", g.anzahl, "Anzahl der Drähte, Litzen oder Stäbe",
                                      stellen=0),
                      "a_p": werte.flaeche("a_p", "a_p", g.erzeugnis.flaeche * 1e-6,
                                           "Querschnitt eines Drahts, einer Litze oder eines "
                                           "Stabs", stellen=1)},
                     titel=f"{g.name}: {g.stuecke} aus {stoff.name}", name=FLAECHE)

        p0_si, pinf_si = vorspannung(f_pk.groesse.si, g.anteil_p0, g.anteil_pinf)
        index = self.index(g)

        def faktor(kurz: str, symbol: str, zahl: float, beschreibung: str) -> Wert:
            return werte.zahl(kurz, f"k_{{{symbol}{index}}}", zahl, beschreibung,
                              stellen=_stellen(zahl))

        def woher(zahl: float, vorgabe: float) -> Tuple[str, Optional[str]]:
            """Was der Titel nach dem Faktor sagt, und die Stelle -- bei der Vorgabe diese."""
            return (", nach Vorgabe", NACH_VORGABE) if zahl == vorgabe else ("", None)

        nachsatz, stelle = woher(g.anteil_p0, ANTEIL_SPANNEN)
        p0 = belegt("sigma_p0", Groesse.aus_si(p0_si, N_PRO_MM2))
        p.formel(p0, r"@k \cdot @f_pk",
                 {"k": faktor("k_p0", "p0", g.anteil_p0, "Anteil von f_pk nach dem Spannen"),
                  "f_pk": f_pk},
                 titel=f"{g.name}: nach dem Spannen{nachsatz}", referenz=stelle, name=GESPANNT)
        nachsatz, stelle = woher(g.anteil_pinf, ANTEIL_NACH_VERLUSTEN)
        pinf = belegt("sigma_pinf", Groesse.aus_si(pinf_si, N_PRO_MM2))
        p.formel(pinf, r"@k \cdot @p0",
                 {"k": faktor("k_pinf", r"p\infty", g.anteil_pinf,
                              "Anteil von σ_p0 nach allen Verlusten"), "p0": p0},
                 titel=f"{g.name}: nach allen Verlusten{nachsatz}",
                 referenz=stelle or REFERENZ_VERLUSTE, name=GESPANNT)

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
        return [g.name, g.lage, f"{g.stuecke}, {stoff.name}", Mathe(fest(g.flaeche, 0)),
                Mathe(fest(pinf_si / 1e6, 0)), Mathe(fest(eps_p.groesse.si * 1e3, 2)),
                Mathe(fest(P.groesse.si / 1e3, 1)), g.wirkung.beschriftung,
                g.verbund.beschriftung]
