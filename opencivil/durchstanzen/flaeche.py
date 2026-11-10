"""
opencivil/durchstanzen/flaeche.py -- die gestützte Fläche: was Lage und Form für den Nachweis heissen.

VERANTWORTUNG:
Die Wahlen der Lage und der Form (:class:`Lage`, :class:`Stuetzenform`) und
je Lage eine Art gestützter Fläche: :class:`Innenstuetze`,
:class:`Randstuetze` und :class:`Eckstuetze` mit ihrer Form,
:class:`Wandende` und :class:`Wandecke`. Jede Art weiss, was der Nachweis
von ihr braucht -- ihre Masse, den Umriss, die Achse, die Plattenränder, die
Kandidaten des Nachweisschnitts, u_0 als Formel, wo es eine gibt, die
Näherung für k_e, die Gleichungen der Momente im Stützstreifen und ob das
Werkzeug Durchstanzbewehrung und Stahlpilze vorschlägt. Welche Art es ist,
entscheidet :meth:`Lage.flaeche` einmal. Bis 2026-11-10 fragten Stelle,
Nachweis, Bewehrung und Maske an 28 Stellen nach Lage und Form.

KOORDINATEN:
In der Ebene der Platte, in m. Eine Stütze steht mit ihrer Achse im
Ursprung; der Plattenrand einer Randstütze liegt unten (y negativ), bei der
Eckstütze liegt ein zweiter links (x negativ). Ein Wandende liegt im
Ursprung, die Wand läuft nach +x; eine Wandecke liegt mit ihrer äusseren
Ecke im Ursprung, die Wände laufen nach +x und +y, die Platte liegt aussen.

EINHEITEN:
SI-Basis.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Dict, List, Optional, Tuple

from opencivil.core.berechnung import Eingaben
from opencivil.core.wahl import Wahl
from opencivil.core.wert import Wert
from opencivil.durchstanzen.schnitt import (
    ECKENBEREICH, Auswertung, Halbebene, Kandidat, Punkt, Stuetzenflaeche, kandidat_wandecke,
    kandidat_wandende, kandidaten_stuetze,
)
from opencivil.querschnitt.platte import Richtung

#: Die Masse einer Stelle in m, nach ihrem Kurznamen.
Masse = Dict[str, float]


@dataclass(frozen=True)
class Mass:
    """Ein Mass in einer Formel: sein Kurzname, sein Zeichen und sein Wert in m."""

    name: str
    zeichen: str
    wert: float


@dataclass(frozen=True)
class Umfangsformel:
    """u_0 in geschlossener Form: der Wert und wie die Herleitung ihn schreibt."""

    wert: float
    vorlage: str
    eingaben: Dict[str, Wert]
    titel: str
    referenz: str
    name: Optional[str] = None


@dataclass(frozen=True)
class Randbreite:
    """
    Was die Breite b_sr eines Stützstreifens am Plattenrand bestimmt
    (Figur 25): b_sr = quer + 2 · (längs + a), mit den Abmessungen der Stütze
    quer und längs zum Streifen und ihrem Abstand zum Rand.
    """

    quer: Mass
    laengs: Mass
    abstand: Mass


@dataclass(frozen=True)
class Momentengleichung:
    """
    Wie 4.3.6.4.7 das mittlere Moment im Stützstreifen einer Richtung rechnet:
    m_sd = max[V_d · (1/8 + e_u / (teiler · b)); mindest · V_d]. Die Breite b
    ist b_s, am Plattenrand b_sr nach ``rand``.
    """

    nummer: str
    teiler: float
    mindest: float = 0.0
    rand: Optional[Randbreite] = None


class Stuetzenform(Wahl):
    """
    Die Form einer Stütze im Grundriss. Die Ovalstütze ist ein Rechteck mit
    halbrunden Enden, b_x × b_y über alles -- so heisst sie in der Software von
    Leviat (DURA); der Name ist nicht aus der Norm.
    """

    RECHTECK = "rechteck"
    RUND = "rund"
    OVAL = "oval"

    @property
    def beschriftung(self) -> str:
        return {Stuetzenform.RECHTECK: "Rechteckstütze", Stuetzenform.RUND: "Rundstütze",
                Stuetzenform.OVAL: "Ovalstütze"}[self]

    @property
    def masse(self) -> Tuple[str, ...]:
        return ("D",) if self is Stuetzenform.RUND else ("b_x", "b_y")

    @property
    def kurz(self) -> str:
        """Wie die Liste die Stütze nennt -- mit den Kurznamen ihrer Masse, in mm."""
        return "⌀{D} mm" if self is Stuetzenform.RUND else "{b_x}×{b_y} mm"

    def flaeche(self, masse: Masse) -> Stuetzenflaeche:
        """Die Stütze aus ihren Massen, mit der Achse im Ursprung."""
        if self is Stuetzenform.RUND:
            return Stuetzenflaeche(((0.0, 0.0),), masse["D"] / 2.0)
        bx, by = masse["b_x"] / 2.0, masse["b_y"] / 2.0
        if self is Stuetzenform.OVAL:
            # Die Strecke zwischen den Mitten der Halbkreise, mit dem halben
            # kürzeren Mass darum -- bei b_x = b_y ein Kreis.
            r = min(bx, by)
            kern = ((-(bx - r), -(by - r)), (bx - r, by - r))
            return Stuetzenflaeche(kern if kern[0] != kern[1] else ((0.0, 0.0),), r)
        return Stuetzenflaeche(((-bx, -by), (bx, -by), (bx, by), (-bx, by)))

    def breite(self, masse: Masse, achse: str) -> Mass:
        """Die Abmessung in ``achse`` («x» oder «y») -- an der Rundstütze der Durchmesser."""
        name = f"b_{achse}"
        if self is Stuetzenform.RUND:
            return Mass(name, "D", masse["D"])
        return Mass(name, name, masse[name])

    def umfang(self, e: Eingaben, d_v: Wert, wert: float) -> Umfangsformel:
        """u_0 rundum, ohne Rand, Ecken und Aussparungen (Figur 22) -- ``wert`` aus dem Schnitt."""
        if self is Stuetzenform.RECHTECK:
            return Umfangsformel(wert, r"2 \cdot \left(@b_x + @b_y\right) + \pi \cdot @d_v",
                                 {"b_x": e["b_x"], "b_y": e["b_y"], "d_v": d_v},
                                 "Nachweisschnitt im Abstand d_v/2",
                                 "SIA 262:2025, 4.3.6.2.2, Figur 22b")
        if self is Stuetzenform.RUND:
            return Umfangsformel(wert, r"\pi \cdot \left(@D + @d_v\right)",
                                 {"D": e["D"], "d_v": d_v}, "Nachweisschnitt im Abstand d_v/2",
                                 "SIA 262:2025, 4.3.6.2.2, Figur 22a")
        return Umfangsformel(wert, r"2 \cdot \left|@b_x - @b_y\right| + \pi \cdot "
                                   r"\left(\min\left[@b_x;\ @b_y\right] + @d_v\right)",
                             {"b_x": e["b_x"], "b_y": e["b_y"], "d_v": d_v},
                             "Nachweisschnitt im Abstand d_v/2: zwei Geraden und zwei Halbkreise",
                             "SIA 262:2025, 4.3.6.2.2, Figur 22",
                             name="Nachweisschnitt im Abstand d_v/2")


class Lage(Wahl):
    """Wo die gestützte Fläche in der Platte liegt -- :meth:`flaeche` macht daraus ihre Art."""

    INNEN = "innen"
    RAND = "rand"
    ECKE = "ecke"
    WANDENDE = "wandende"
    WANDECKE = "wandecke"

    @property
    def beschriftung(self) -> str:
        return {Lage.INNEN: "Innenstütze", Lage.RAND: "Randstütze", Lage.ECKE: "Eckstütze",
                Lage.WANDENDE: "Wandende", Lage.WANDECKE: "Wandecke"}[self]

    @property
    def mehrzahl(self) -> str:
        """«Innenstützen», «Wandenden» -- wie die Näherung von 4.3.6.2.5 sie nennt."""
        return {Lage.INNEN: "Innenstützen", Lage.RAND: "Randstützen", Lage.ECKE: "Eckstützen",
                Lage.WANDENDE: "Wandenden", Lage.WANDECKE: "Wandecken"}[self]

    def flaeche(self, form: Stuetzenform) -> "GestuetzteFlaeche":
        """Die Art der gestützten Fläche; ``form`` gilt nur für Stützen."""
        if self is Lage.WANDENDE:
            return Wandende()
        if self is Lage.WANDECKE:
            return Wandecke()
        return {Lage.INNEN: Innenstuetze, Lage.RAND: Randstuetze, Lage.ECKE: Eckstuetze}[self](form)


class GestuetzteFlaeche(ABC):
    """Eine Art gestützter Fläche -- siehe Dateikopf."""

    lage: ClassVar[Lage]

    titel: ClassVar[str]
    """Wie die Maske ihre Masse überschreibt: «Stütze» oder «Wand»."""

    k_e: ClassVar[float]
    """Die Näherung nach SIA 262:2025, 4.3.6.2.5."""

    hat_form: ClassVar[bool] = False

    momente: ClassVar[bool] = True
    """Ob 4.3.6.4.7 Momente im Stützstreifen nennt -- für Wände nicht."""

    ecken_abziehen: ClassVar[bool] = True
    """Ob neben Ecken etwas vom Schnitt abgeht -- an Wänden zählt u_0 nur 1.5·d_v entlang der Wand."""

    vorschlag: ClassVar[bool] = True
    """Ob das Werkzeug Durchstanzbewehrung vorschlägt -- an Wänden noch nicht."""

    stahlpilz: ClassVar[bool] = False
    """Ob ein ZEUS-Stahlpilz in Frage kommt: der Katalog hat sie nur für Innenstützen."""

    k_sys_erhoeht: ClassVar[bool] = False
    """Ob das Gutachten von ancoPLUS 3·k_r zulässt: an Innenstützen und Wandenden."""

    @property
    @abstractmethod
    def masse(self) -> Tuple[str, ...]:
        """Die Kurznamen der Masse, die für sie gelten."""

    @property
    @abstractmethod
    def kurz(self) -> str:
        """Wie die Liste sie nennt -- mit den Kurznamen ihrer Masse, in mm."""

    @abstractmethod
    def kandidaten(self, masse: Masse, abstand: float, d_v: float) -> List[Kandidat]:
        """Die möglichen Nachweisschnitte im Abstand ``abstand`` -- siehe :mod:`.schnitt`."""

    @abstractmethod
    def umriss(self, masse: Masse, d_v: float) -> List[Punkt]:
        """Der Umriss fürs Bild."""

    def achse(self, masse: Masse) -> Punkt:
        """Die Achse -- von ihr gehen die Strahlen an Aussparungen vorbei."""
        return (0.0, 0.0)

    def raender(self, masse: Masse) -> Tuple[Halbebene, ...]:
        """Die Plattenränder."""
        return ()

    def umfang(self, e: Eingaben, d_v: Wert, a: Auswertung) -> Optional[Umfangsformel]:
        """u_0 als Formel -- oder nichts, dann steht der Schnitt als Länge in der Platte."""
        return None

    def k_e_naeherung(self, a: Auswertung) -> Tuple[float, str]:
        """Die Näherung für k_e und wie die Herleitung sie nennt."""
        return self.k_e, f"Näherung für {self.lage.mehrzahl}"

    def momentengleichung(self, r: Richtung, masse: Masse) -> Momentengleichung:
        """Die Gleichung der Momente im Stützstreifen in ``r`` -- nur, wo :attr:`momente` gilt."""
        raise TypeError(f"Für {self.lage.mehrzahl} nennt 4.3.6.4.7 keine Momente im Stützstreifen.")


@dataclass(frozen=True)
class Stuetze(GestuetzteFlaeche):
    """Eine Stütze mit ihrer Form; am Rand und an der Ecke mit dem Abstand zum Rand."""

    form: Stuetzenform

    titel: ClassVar[str] = "Stütze"
    hat_form: ClassVar[bool] = True
    randmasse: ClassVar[Tuple[str, ...]] = ()

    @property
    def masse(self) -> Tuple[str, ...]:
        return (*self.form.masse, *self.randmasse)

    @property
    def kurz(self) -> str:
        return self.form.kurz

    def kandidaten(self, masse: Masse, abstand: float, d_v: float) -> List[Kandidat]:
        return kandidaten_stuetze(self.form.flaeche(masse), abstand, ECKENBEREICH * d_v,
                                  self.raender(masse))

    def umriss(self, masse: Masse, d_v: float) -> List[Punkt]:
        return self.form.flaeche(masse).umriss()

    def _randbreite(self, r: Richtung, masse: Masse) -> Randbreite:
        """Der Streifen in ``r`` am Plattenrand: quer zu ihm die Stütze, längs ihr Abstand zum Rand."""
        quer, laengs = ("x", "y") if r is Richtung.Y else ("y", "x")
        abstand = f"a_{laengs}"
        return Randbreite(self.form.breite(masse, quer), self.form.breite(masse, laengs),
                          Mass(abstand, abstand, masse[abstand]))


@dataclass(frozen=True)
class Innenstuetze(Stuetze):
    lage: ClassVar[Lage] = Lage.INNEN
    k_e: ClassVar[float] = 0.9
    stahlpilz: ClassVar[bool] = True
    k_sys_erhoeht: ClassVar[bool] = True

    def umfang(self, e: Eingaben, d_v: Wert, a: Auswertung) -> Optional[Umfangsformel]:
        """Rundum, wo nichts neben Ecken oder hinter Aussparungen abgeht, die Formel der Form."""
        if a.an_ecken < 1e-6 and a.hinter_aussparungen < 1e-6:
            return self.form.umfang(e, d_v, a.in_der_platte)
        return None

    def k_e_naeherung(self, a: Auswertung) -> Tuple[float, str]:
        """Mit grossen Aussparungen in Stützennähe gilt 0.7 wie am Rand (4.3.6.2.5)."""
        if a.hinter_aussparungen > 1e-6:
            return 0.7, "Näherung für Innenstützen mit grossen Aussparungen in Stützennähe"
        return super().k_e_naeherung(a)

    def momentengleichung(self, r: Richtung, masse: Masse) -> Momentengleichung:
        return Momentengleichung("(62)", 2.0)


@dataclass(frozen=True)
class Randstuetze(Stuetze):
    lage: ClassVar[Lage] = Lage.RAND
    k_e: ClassVar[float] = 0.7
    randmasse: ClassVar[Tuple[str, ...]] = ("a_y",)

    def raender(self, masse: Masse) -> Tuple[Halbebene, ...]:
        """Der Rand unten."""
        _, y0, _, _ = self.form.flaeche(masse).grenzen()
        return (Halbebene((0.0, -1.0), -(y0 - masse["a_y"])),)

    def momentengleichung(self, r: Richtung, masse: Masse) -> Momentengleichung:
        """Parallel zum Rand (63), senkrecht zu ihm (64) mit b_sr."""
        if r is Richtung.X:
            return Momentengleichung("(63)", 2.0, 0.25)
        return Momentengleichung("(64)", 1.0, rand=self._randbreite(r, masse))


@dataclass(frozen=True)
class Eckstuetze(Stuetze):
    lage: ClassVar[Lage] = Lage.ECKE
    k_e: ClassVar[float] = 0.65
    randmasse: ClassVar[Tuple[str, ...]] = ("a_x", "a_y")

    def raender(self, masse: Masse) -> Tuple[Halbebene, ...]:
        """Der Rand unten und der links."""
        x0, y0, _, _ = self.form.flaeche(masse).grenzen()
        return (Halbebene((0.0, -1.0), -(y0 - masse["a_y"])),
                Halbebene((-1.0, 0.0), -(x0 - masse["a_x"])))

    def momentengleichung(self, r: Richtung, masse: Masse) -> Momentengleichung:
        return Momentengleichung("(65)", 1.0, 0.5, self._randbreite(r, masse))


class Wand(GestuetzteFlaeche):
    """
    Das Ende oder die Ecke einer Wand mit der Dicke t. Entlang der Wand zählt
    der Schnitt 1.5·d_v; was dahinter läuft, gehört nicht dazu (Figur 23b
    und c).
    """

    titel: ClassVar[str] = "Wand"
    k_e: ClassVar[float] = 0.75
    momente: ClassVar[bool] = False
    ecken_abziehen: ClassVar[bool] = False
    vorschlag: ClassVar[bool] = False

    @property
    def masse(self) -> Tuple[str, ...]:
        return ("t",)

    @property
    def kurz(self) -> str:
        return "Wand {t} mm"


class Wandende(Wand):
    lage: ClassVar[Lage] = Lage.WANDENDE
    k_sys_erhoeht: ClassVar[bool] = True

    def kandidaten(self, masse: Masse, abstand: float, d_v: float) -> List[Kandidat]:
        return [kandidat_wandende(masse["t"], abstand, d_v)]

    def umriss(self, masse: Masse, d_v: float) -> List[Punkt]:
        """Die Wand 4·d_v weit -- etwas über den Schnitt hinaus, der 3.5·d_v weit reicht."""
        t, L = masse["t"], 4.0 * d_v
        return [(0.0, -t / 2), (L, -t / 2), (L, t / 2), (0.0, t / 2)]

    def achse(self, masse: Masse) -> Punkt:
        return (masse["t"] / 2.0, 0.0)

    def umfang(self, e: Eingaben, d_v: Wert, a: Auswertung) -> Optional[Umfangsformel]:
        dv = d_v.groesse.si
        return Umfangsformel(e.g("t").si + 3.0 * dv + math.pi * dv / 2.0,
                             r"@t + 3 \cdot @d_v + \frac{\pi \cdot @d_v}{2}",
                             {"t": e["t"], "d_v": d_v},
                             "Nachweisschnitt um das Wandende: 1.5·d_v entlang der Wand",
                             "SIA 262:2025, 4.3.6.2.3, Figur 23b und c")


class Wandecke(Wand):
    lage: ClassVar[Lage] = Lage.WANDECKE

    def kandidaten(self, masse: Masse, abstand: float, d_v: float) -> List[Kandidat]:
        return [kandidat_wandecke(masse["t"], abstand, d_v)]

    def umriss(self, masse: Masse, d_v: float) -> List[Punkt]:
        """Die beiden Wände je 4·d_v weit."""
        t, L = masse["t"], 4.0 * d_v
        return [(0.0, 0.0), (L, 0.0), (L, t), (t, t), (t, L), (0.0, L)]

    def achse(self, masse: Masse) -> Punkt:
        return (masse["t"] / 2.0, masse["t"] / 2.0)

    def umfang(self, e: Eingaben, d_v: Wert, a: Auswertung) -> Optional[Umfangsformel]:
        dv = d_v.groesse.si
        return Umfangsformel(3.0 * dv + math.pi * dv / 4.0,
                             r"3 \cdot @d_v + \frac{\pi \cdot @d_v}{4}", {"d_v": d_v},
                             "Nachweisschnitt um die Wandecke: je 1.5·d_v entlang der Wände",
                             "SIA 262:2025, 4.3.6.2.3, Figur 23b und c")
