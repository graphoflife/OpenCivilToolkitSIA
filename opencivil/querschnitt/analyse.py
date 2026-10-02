"""
opencivil/querschnitt/analyse.py -- der gezeichnete Querschnitt als Bauteil im Rechenwerk.

VERANTWORTUNG:
Aus der Beschreibung einer Querschnittsanalyse wird hier ein Bauteil wie die
Platte (:class:`~opencivil.querschnitt.platte.Plattenquerschnitt`): mit
Namensraum, Ueberschrift, Werten und einer Herleitung des Querschnitts --
Polygone, Bruttoquerschnitt, Bewehrung, Schubwaende. Die Nachweise bekommen
das Bauteil und lesen daraus die Geometrie; seine Zahlen beziehen sie ueber
das Rechenwerk, damit jede rueckverfolgbar bleibt.

DIE ZEICHNUNG WIRD HIER GEPRUEFT:
Kreuzt sich ein Polygon, ueberlappen sich zwei, liegt ein Stab nicht ganz im
Beton oder eine Wand ausserhalb -- dann entsteht kein Bauteil, sondern ein
:class:`~opencivil.querschnitt.geometrie.GeometrieFehler` mit dem Element,
das nicht stimmt. Erst hier und nicht beim Oeffnen der Datei: eine Analyse
mit einem verunglueckten Polygon soll sich oeffnen und korrigieren lassen.

KOORDINATEN UND EINHEITEN:
Die Beschreibung zeichnet in Millimetern, y nach rechts, z nach oben. Die
Tabellen der Herleitung bleiben in Millimetern; fuer die Nachweise wird
einmal in Meter umgerechnet (:meth:`Querschnittsanalyse.geometrie`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Berechnung, Eingabebezug, Eingaben, Prozedur, Vorgabe,
)
from opencivil.core.einheiten import EINHEITSLOS, GRAD, MIO_MM4, MM, MM2, Groesse
from opencivil.core.latex import Mathe, als_text
from opencivil.core.protokoll import (
    Abschnitt, GleichungBlock, Protokoll, TabellenBlock, Zwischenwerte,
)
from opencivil.core.wert import WertDef, kennung_aus
from opencivil.material.basis import Baustoff, Baustoffart
from opencivil.material.beton import BETON_VORLAGEN
from opencivil.querschnitt import geometrie as geo
from opencivil.querschnitt.geometrie import GeometrieFehler, Linienart, Punkt
from opencivil.querschnitt.interaktion import (
    Bewehrung, Querschnitt, Teil, Werkstoff, linie_als_bewehrung,
)
from opencivil.querschnitt.schubwaende import Wand
from opencivil.querschnitt.werkstoffgesetz import (
    Betongesetz, Spannungsblock, Stahlgesetz,
)

#: Die Kennwerte, die die Nachweise eines Werkstoffs lesen -- je Art alle, die
#: eine der Wahlen braucht. Das Rechenwerk rechnet sie ohnehin.
KENNWERTE = {
    Baustoffart.BETON: ("f_ck", "f_cd", "eps_c1d", "eps_c2d", "k_sigma", "E_cd", "f_ctm"),
    Baustoffart.BETONSTAHL: ("f_yk", "f_yd", "f_yk_druck", "f_yd_druck", "E_s", "eps_ud"),
}

#: Die Regel fuer k_sigma steht beim Beton. Mit charakteristischen Werten gilt
#: dieselbe, mit f_ck statt f_cd -- also wird sie von dort genommen.
_K_SIGMA = next(v for v in BETON_VORLAGEN if v.kurzname == "k_sigma")


@dataclass(frozen=True)
class Lastfall:
    """
    Ein Lastfall der Analyse, in SI-Basis: N in N, Momente in Nm.

    Vorzeichen wie in der Beschreibung: N > 0 Zug, M_y > 0 zieht unten, M_z > 0
    links, V_y und V_z in Achsrichtung, T im Gegenuhrzeigersinn.
    """

    name: str
    N: float = 0.0
    M_y: float = 0.0
    M_z: float = 0.0
    V_y: float = 0.0
    V_z: float = 0.0
    T: float = 0.0

    @property
    def kennung(self) -> str:
        return kennung_aus(self.name)


@dataclass(frozen=True)
class Flaechenteil:
    """Ein Polygon der Zeichnung -- Ecken in mm, ohne Material eine Aussparung."""

    nummer: int
    punkte: Tuple[Punkt, ...]
    stoff: Optional[Baustoff]

    @property
    def name(self) -> str:
        return f"{'Aussparung' if self.stoff is None else 'Polygon'} {self.nummer}"


@dataclass(frozen=True)
class Stabgruppe:
    """
    Ein Bewehrungselement der Zeichnung: ein Einzelstab oder eine Stablinie.

    ``punkte`` sind die Stabmitten in mm, bei einer verschmierten Flaeche leer.
    ``flaeche`` ist die ganze Stahlflaeche des Elements in mm².
    """

    name: str
    art: str
    """``stab`` oder eine :class:`Linienart`."""

    stahl: Baustoff
    durchmesser: float
    punkte: Tuple[Punkt, ...]
    flaeche: float
    von: Punkt
    bis: Punkt
    linie: Optional[geo.Stablinie] = None
    gewaehlt: Optional[float] = None
    """Bei einer Linie nach Teilung der eingegebene Abstand."""


@dataclass(frozen=True)
class Wandangabe:
    """Eine Schubwand, wie gezeichnet: Achse in mm, Bügel, und der Beton, in dem sie liegt."""

    nummer: int
    von: Punkt
    bis: Punkt
    dicke: float
    durchmesser: float
    teilung: float
    schnitte: int
    stahl: Optional[Baustoff]
    beton: Baustoff

    @property
    def name(self) -> str:
        return f"Wand {self.nummer}"

    @property
    def laenge(self) -> float:
        return math.hypot(self.bis[0] - self.von[0], self.bis[1] - self.von[1])

    @property
    def a_sw_s(self) -> float:
        """Buegelquerschnitt je Laenge, ``n · π⌀²/4 / s``, in mm²/mm."""
        if self.durchmesser <= 0 or self.teilung <= 0:
            return 0.0
        return self.schnitte * math.pi * self.durchmesser ** 2 / 4.0 / self.teilung


class QuerschnittsaufbauProzedur(Prozedur):
    """Polygone, Bruttoquerschnitt, Bewehrung und Schubwaende -- in Tabellen."""

    def __init__(self, analyse: "Querschnittsanalyse", **kwargs) -> None:
        super().__init__(**kwargs)
        self.analyse = analyse

    def rechne(self, e: Eingaben, p: Protokoll) -> Mapping[str, Groesse]:
        return self.analyse.aufbau_protokollieren(p)


class Querschnittsanalyse:
    """Ein gezeichneter Querschnitt, fertig fuer das Rechenwerk und die Nachweise."""

    def __init__(
        self, *, name: str, praefix: str,
        flaechen: Sequence[Flaechenteil],
        staebe: Sequence[Tuple[Punkt, float, Baustoff]],
        linien: Sequence[dict],
        waende: Sequence[dict],
        alpha_min: int, alpha_max: int, k_c: float,
        wahl: Mapping[str, Tuple[str, str]],
    ) -> None:
        self.name = name
        self.id = praefix
        self.wahl = dict(wahl)
        """Je Baustoff-ID die Rechenwerte und beim Beton das Gesetz."""
        self.flaechen = tuple(flaechen)
        self.definitionen: Dict[str, WertDef] = {}
        self.berechnungen: List[Berechnung] = []
        self._interaktionen: Dict[tuple, Tuple[Querschnitt, List[str]]] = {}

        self._zeichnung_pruefen()
        self.gruppen: List[Stabgruppe] = self._bewehrung(staebe, linien)
        self.waende: List[Wandangabe] = self._waende(waende)
        self.brutto = geo.summe([
            (self._gewicht(i), geo.flaechenwerte(f.punkte))
            for i, f in enumerate(self.flaechen) if self._gewicht(i) != 0.0])
        self._aufbauen(alpha_min, alpha_max, k_c)

    # -- Pruefen --------------------------------------------------------------

    def _zeichnung_pruefen(self) -> None:
        if not any(f.stoff is not None for f in self.flaechen):
            raise GeometrieFehler("Es gibt kein Polygon mit Material -- nichts, was trägt.")
        for f in self.flaechen:
            geo.polygon_pruefen(f.punkte, f.name)
        self.eltern = geo.verschachteln([f.punkte for f in self.flaechen],
                                        [f.name for f in self.flaechen])
        for f, eltern in zip(self.flaechen, self.eltern):
            if f.stoff is None and (eltern is None or self.flaechen[eltern].stoff is None):
                raise GeometrieFehler(
                    f"{f.name} liegt in keinem Polygon mit Material. Eine "
                    f"Aussparung nimmt Fläche weg -- sie muss in einer liegen.")
        self._polygone = [f.punkte for f in self.flaechen]
        self._traegt = [f.stoff is not None for f in self.flaechen]

    def _gewicht(self, i: int) -> float:
        """+1 fuer ein Polygon mit Material, -1 fuer eine Aussparung darin, sonst 0."""
        eigen = self.flaechen[i].stoff is not None
        eltern = self.eltern[i]
        fremd = eltern is not None and self.flaechen[eltern].stoff is not None
        return float(eigen) - float(fremd)

    def _im_beton(self, p: Punkt, durchmesser: float) -> bool:
        return geo.stab_liegt_in(p, durchmesser / 2.0, self._polygone, self._traegt)

    def beton_an(self, p: Punkt) -> Optional[Baustoff]:
        """Der Werkstoff des innersten Polygons an dieser Stelle."""
        innen = geo.innerstes(p, self._polygone)
        return None if innen is None else self.flaechen[innen].stoff

    def _bewehrung(self, staebe, linien) -> List[Stabgruppe]:
        gruppen: List[Stabgruppe] = []
        for nummer, (lage, durchmesser, stahl) in enumerate(staebe, start=1):
            name = f"Stab {nummer}"
            if durchmesser <= 0:
                raise GeometrieFehler(f"{name}: der Durchmesser muss grösser als null sein.")
            if not self._im_beton(lage, durchmesser):
                raise GeometrieFehler(
                    f"{name} (y = {lage[0]:g}, z = {lage[1]:g} mm) liegt nicht ganz "
                    f"im Beton. Bewehrung muss im Beton liegen.")
            gruppen.append(Stabgruppe(
                name=name, art="stab", stahl=stahl, durchmesser=durchmesser,
                punkte=(lage,), flaeche=math.pi * durchmesser ** 2 / 4.0,
                von=lage, bis=lage))

        for nummer, l in enumerate(linien, start=1):
            name = f"Linie {nummer}"
            art = Linienart(l["art"])
            wert = {Linienart.FLAECHE: l["flaeche"], Linienart.ANZAHL: l["anzahl"],
                    Linienart.TEILUNG: l["teilung"]}[art]
            try:
                aufgeloest = geo.stablinie(l["von"], l["bis"], art, wert,
                                           starteisen=l["starteisen"], endeisen=l["endeisen"])
            except GeometrieFehler as fehler:
                raise GeometrieFehler(f"{name}: {fehler}") from None
            if art is Linienart.FLAECHE:
                if not geo.strecke_liegt_in(l["von"], l["bis"], self._polygone, self._traegt):
                    raise GeometrieFehler(f"{name} liegt nicht ganz im Beton.")
                flaeche = wert
            else:
                if l["durchmesser"] <= 0:
                    raise GeometrieFehler(f"{name}: der Durchmesser muss grösser als null sein.")
                for k, p in enumerate(aufgeloest.punkte, start=1):
                    if not self._im_beton(p, l["durchmesser"]):
                        raise GeometrieFehler(
                            f"{name}, {k}. Stab (y = {p[0]:.1f}, z = {p[1]:.1f} mm) liegt "
                            f"nicht ganz im Beton.")
                flaeche = len(aufgeloest.punkte) * math.pi * l["durchmesser"] ** 2 / 4.0
            gruppen.append(Stabgruppe(
                name=name, art=art.value, stahl=l["stahl"], durchmesser=l["durchmesser"],
                punkte=aufgeloest.punkte, flaeche=flaeche, von=tuple(l["von"]),
                bis=tuple(l["bis"]), linie=aufgeloest,
                gewaehlt=wert if art is Linienart.TEILUNG else None))
        return gruppen

    def _waende(self, waende) -> List[Wandangabe]:
        ergebnis: List[Wandangabe] = []
        for nummer, w in enumerate(waende, start=1):
            name = f"Wand {nummer}"
            von, bis = tuple(w["von"]), tuple(w["bis"])
            if math.hypot(bis[0] - von[0], bis[1] - von[1]) <= geo.TOLERANZ:
                raise GeometrieFehler(f"{name} hat keine Länge.")
            if w["dicke"] <= 0:
                raise GeometrieFehler(f"{name}: die Dicke muss grösser als null sein.")
            if w["durchmesser"] > 0 and w["teilung"] <= 0:
                raise GeometrieFehler(f"{name}: die Bügelteilung muss grösser als null sein.")
            if not geo.strecke_liegt_in(von, bis, self._polygone, self._traegt):
                raise GeometrieFehler(
                    f"{name} liegt nicht ganz im Beton. Eine Schubwand wird von Gurt zu "
                    f"Gurt im Beton gezeichnet.")
            mitte = ((von[0] + bis[0]) / 2.0, (von[1] + bis[1]) / 2.0)
            ergebnis.append(Wandangabe(
                nummer=nummer, von=von, bis=bis, dicke=w["dicke"],
                durchmesser=w["durchmesser"], teilung=w["teilung"],
                schnitte=w["schnitte"], stahl=w["stahl"], beton=self.beton_an(mitte)))
        return ergebnis

    # -- Rechenwerk -----------------------------------------------------------

    @property
    def abschnitt(self) -> Abschnitt:
        return Abschnitt(f"Querschnittsanalyse: {self.name}", self.id,
                         thema="Querschnittsanalyse")

    def _def(self, kurzname: str, symbol: str, einheit, beschreibung: str,
             stellen: int = 1, referenz: str = "") -> WertDef:
        d = WertDef(id=f"{self.id}.{kurzname}", symbol=symbol, einheit=einheit,
                    beschreibung=beschreibung, referenz=referenz, stellen=stellen)
        self.definitionen[kurzname] = d
        return d

    def id_von(self, kurzname: str) -> str:
        return self.definitionen[kurzname].id

    def _aufbauen(self, alpha_min: int, alpha_max: int, k_c: float) -> None:
        self.d_brutto = {
            "A": self._def("A", "A", MM2, "Fläche des Bruttoquerschnitts", 0),
            "y_S": self._def("y_S", "y_S", MM, "Schwerpunkt, y", 1),
            "z_S": self._def("z_S", "z_S", MM, "Schwerpunkt, z", 1),
            "I_y": self._def("I_y", "I_y", MIO_MM4, "Trägheitsmoment um y", 1),
            "I_z": self._def("I_z", "I_z", MIO_MM4, "Trägheitsmoment um z", 1),
            "I_yz": self._def("I_yz", "I_{yz}", MIO_MM4, "Deviationsmoment", 1),
            "A_s": self._def("A_s", r"A_{s,tot}", MM2, "Stahlfläche der Bewehrung", 0),
        }
        abschnitt = self.abschnitt
        self.berechnungen.append(QuerschnittsaufbauProzedur(
            self, id=f"{self.id}.aufbau", ausgaben=list(self.d_brutto.values()),
            titel="Querschnitt", abschnitt=abschnitt))

        gruppe = "Schubwände"
        for kurzname, symbol, einheit, groesse, beschreibung, stellen in (
                ("alpha_min", r"\alpha_{min}", GRAD, Groesse(alpha_min, GRAD),
                 "Kleinste Neigung der Druckdiagonalen", 0),
                ("alpha_max", r"\alpha_{max}", GRAD, Groesse(alpha_max, GRAD),
                 "Grösste Neigung der Druckdiagonalen", 0),
                ("k_c", "k_c", EINHEITSLOS, Groesse(k_c, EINHEITSLOS),
                 "Abminderung der Betondruckfestigkeit in der Druckdiagonalen", 2)):
            d = self._def(kurzname, symbol, einheit, beschreibung, stellen)
            self.berechnungen.append(Vorgabe(
                id=d.id, ausgabe=d, groesse=groesse, abschnitt=abschnitt,
                gruppe=gruppe, stumm=True))

    def ins_rechenwerk(self, werk) -> "Querschnittsanalyse":
        for stoff in self.baustoffe:
            stoff.ins_rechenwerk(werk)
        werk.definiere(*self.definitionen.values())
        werk.registriere(*self.berechnungen)
        return self

    @property
    def baustoffe(self) -> List[Baustoff]:
        """Jeder Baustoff, den die Analyse benutzt: erst die der Flaechen, dann die Staehle."""
        gesehen: Dict[str, Baustoff] = {}
        for stoff in ([f.stoff for f in self.flaechen]
                      + [g.stahl for g in self.gruppen]
                      + [w.stahl for w in self.waende]):
            if stoff is not None:
                gesehen.setdefault(stoff.id, stoff)
        return list(gesehen.values())

    # -- Herleitung des Querschnitts -------------------------------------------

    def aufbau_protokollieren(self, p: Protokoll) -> Dict[str, Groesse]:
        p.erklaerung(
            "Der Querschnitt ist gezeichnet: Polygone, jedes mit seinem Material. "
            "Liegt ein Polygon ganz in einem anderen, ersetzt es dieses dort -- "
            "eine Aussparung nimmt die Fläche weg. y zeigt nach rechts, z nach "
            "oben; alle Masse in Millimetern.")
        p.ansatz(
            r"A = \frac{1}{2} \sum_i c_i \qquad "
            r"y_S = \frac{1}{6A} \sum_i (y_i + y_{i+1})\, c_i \qquad "
            r"z_S = \frac{1}{6A} \sum_i (z_i + z_{i+1})\, c_i \qquad "
            r"c_i = y_i\, z_{i+1} - y_{i+1}\, z_i",
            titel="Fläche und Schwerpunkt eines Polygons (Satz von Gauss)")
        p.ansatz(
            r"I_y = \frac{1}{12} \sum_i (z_i^2 + z_i z_{i+1} + z_{i+1}^2)\, c_i - A\, z_S^2"
            r"\qquad I_z = \frac{1}{12} \sum_i (y_i^2 + y_i y_{i+1} + y_{i+1}^2)\, c_i"
            r" - A\, y_S^2",
            titel="Trägheitsmomente eines Polygons, bezogen auf den Schwerpunkt")

        zeilen = []
        for i, f in enumerate(self.flaechen):
            w = geo.flaechenwerte(f.punkte)
            zeilen.append([
                f.name,
                f.stoff.name if f.stoff is not None else "–",
                self.flaechen[self.eltern[i]].name if self.eltern[i] is not None else "–",
                Mathe(f"{len(f.punkte)}"),
                Mathe(f"{self._gewicht(i) * w.A:.0f}"),
                Mathe(f"{w.y_S:.1f}"), Mathe(f"{w.z_S:.1f}"),
            ])
        p.tabelle(
            kopf=["Polygon", "Material", "liegt in", "Ecken",
                  Mathe(r"\pm A\ [\mathrm{mm}^2]"), Mathe(r"y_S\ [\mathrm{mm}]"),
                  Mathe(r"z_S\ [\mathrm{mm}]")],
            zeilen=zeilen, titel="Polygone des Querschnitts", ausrichtung="lllrrrr")

        b = self.brutto
        werte = {
            "A": Groesse(b.A, MM2), "y_S": Groesse(b.y_S, MM), "z_S": Groesse(b.z_S, MM),
            "I_y": Groesse.aus_si(b.I_y * 1e-12, MIO_MM4),
            "I_z": Groesse.aus_si(b.I_z * 1e-12, MIO_MM4),
            "I_yz": Groesse.aus_si(b.I_yz * 1e-12, MIO_MM4),
        }
        for kurz, groesse in werte.items():
            p.wert(self.d_brutto[kurz].belegen(groesse), gruppe="Bruttoquerschnitt")

        a_s = self._bewehrung_protokollieren(p)
        werte["A_s"] = Groesse(a_s, MM2)
        p.wert(self.d_brutto["A_s"].belegen(werte["A_s"]))
        if self.waende:
            self._waende_protokollieren(p)
        return {self.d_brutto[k].id: g for k, g in werte.items()}

    def _bewehrung_protokollieren(self, p: Protokoll) -> float:
        if not self.gruppen:
            p.text("Keine Bewehrung gezeichnet.")
            return 0.0
        p.ansatz(r"s = \frac{L}{m} \qquad m = \mathrm{runde}\left(\frac{L}{s_{gewählt}}\right)",
                 titel="Teilung einer Stablinie: gleiche Felder, auf die Länge gerundet")
        zeilen = []
        for g in self.gruppen:
            if g.art == "stab":
                menge = Mathe(rf"\varnothing {g.durchmesser:g}")
                lage = Mathe(f"({g.von[0]:g};\\ {g.von[1]:g})")
            else:
                lage = Mathe(f"({g.von[0]:g};\\ {g.von[1]:g}) \\rightarrow "
                             f"({g.bis[0]:g};\\ {g.bis[1]:g})")
                if g.art == Linienart.FLAECHE.value:
                    menge = "verschmiert"
                else:
                    n = len(g.punkte)
                    teilung = f"{g.linie.teilung:.1f}" if g.linie else ""
                    menge = Mathe(rf"{n} \varnothing {g.durchmesser:g}"
                                  + (rf"\ @\ {teilung}" if n > 1 else "")
                                  + (rf"\ (\text{{gewählt }} {g.gewaehlt:g})"
                                     if g.gewaehlt is not None else ""))
            zeilen.append([g.name, lage, menge, g.stahl.name, Mathe(f"{g.flaeche:.0f}")])
        p.tabelle(kopf=["Element", Mathe(r"\text{Lage}\ [\mathrm{mm}]"), "Bewehrung",
                        "Stahl", Mathe(r"A_s\ [\mathrm{mm}^2]")],
                  zeilen=zeilen, titel="Bewehrung", ausrichtung="lllr" + "r")
        return sum(g.flaeche for g in self.gruppen)

    def _waende_protokollieren(self, p: Protokoll) -> None:
        p.ansatz(r"\frac{A_{sw}}{s} = \frac{n \cdot \pi\, \varnothing^2 / 4}{s}",
                 titel="Bügelquerschnitt je Länge einer Schubwand (n Schnitte)")
        zeilen = []
        for w in self.waende:
            zeilen.append([
                w.name,
                Mathe(f"({w.von[0]:g};\\ {w.von[1]:g}) \\rightarrow ({w.bis[0]:g};\\ {w.bis[1]:g})"),
                Mathe(f"{w.laenge:.0f}"), Mathe(f"{w.dicke:g}"),
                Mathe(rf"{w.schnitte} \times \varnothing {w.durchmesser:g}\ @\ {w.teilung:g}")
                if w.durchmesser > 0 else "keine",
                Mathe(f"{w.a_sw_s * 1000.0:.0f}"),
            ])
        p.tabelle(kopf=["Wand", Mathe(r"\text{Achse}\ [\mathrm{mm}]"),
                        Mathe(r"l\ [\mathrm{mm}]"), Mathe(r"b_w\ [\mathrm{mm}]"), "Bügel",
                        Mathe(r"A_{sw}/s\ [\mathrm{mm}^2/\mathrm{m}]")],
                  zeilen=zeilen, titel="Schubwände", ausrichtung="llrrlr")

    # -- Fuer die Zusammenfassung -------------------------------------------------

    def angaben(self) -> Tuple[GleichungBlock, TabellenBlock]:
        """Was ueber der Nachweistabelle steht: Werkstoffe, Flaeche, Schwerpunkt; die Bewehrung."""
        betone = sorted({f.stoff.name for f in self.flaechen if f.stoff is not None})
        b = self.brutto
        latex = (rf"{als_text(', '.join(betone))} \qquad A = {b.A:.0f}\,\mathrm{{mm}}^2"
                 rf" \qquad y_S = {b.y_S:.1f}\,\mathrm{{mm}} \qquad z_S = {b.z_S:.1f}\,\mathrm{{mm}}")
        kopf = GleichungBlock(latex=latex, titel="Angaben zum Querschnitt")
        zeilen = []
        for g in self.gruppen:
            if g.art == "stab":
                menge = Mathe(rf"\varnothing {g.durchmesser:g}")
            elif g.art == Linienart.FLAECHE.value:
                menge = Mathe(rf"{g.flaeche:.0f}\,\mathrm{{mm}}^2")
            else:
                menge = Mathe(rf"{len(g.punkte)} \varnothing {g.durchmesser:g}")
            zeilen.append([g.name, menge, g.stahl.name])
        for w in self.waende:
            zeilen.append([w.name, Mathe(
                rf"b_w = {w.dicke:g},\ {w.schnitte} \times \varnothing {w.durchmesser:g}"
                rf"\ @\ {w.teilung:g}") if w.durchmesser > 0 else "ohne Bügel",
                w.stahl.name if w.stahl is not None else "–"])
        tabelle = TabellenBlock(kopf=["Element", "Bewehrung", "Stahl"], zeilen=zeilen,
                                titel="Bewehrung und Schubwände", ausrichtung="lll")
        return kopf, tabelle

    # -- Fuer die Nachweise: Werkstoffe ---------------------------------------------

    def satz(self, stoff: Baustoff) -> str:
        return self.wahl.get(stoff.id, ("bemessung", "parabel"))[0]

    def betongesetz(self, stoff: Baustoff) -> str:
        return self.wahl.get(stoff.id, ("bemessung", "parabel"))[1]

    @staticmethod
    def _name(stoff: Baustoff, kennwert: str) -> str:
        return f"{kennwert}__{kennung_aus(stoff.id)}"

    def werkstoffbezuege(self) -> List[Eingabebezug]:
        """Die Kennwerte jedes Baustoffs der Analyse, als Eingaben der Nachweise."""
        return [Eingabebezug(self._name(stoff, k), stoff.id_von(k))
                for stoff in self.baustoffe for k in KENNWERTE[stoff.art]]

    def kennwert(self, e: Eingaben, stoff: Baustoff, kennwert: str) -> float:
        return e.g(self._name(stoff, kennwert)).si

    def werkstoffe(self, e: Eingaben) -> Tuple[List[Werkstoff], Callable[[Baustoff], int]]:
        """
        Die Werkstoffe der Interaktion, mit den gewaehlten Rechenwerten.

        Beton: Parabel-Rechteck oder Spannungsblock, gedrueckt bis ``-eps_c2d``
        samt C-Punkt, verdraengt von den Staeben. Betonstahl: bilinear,
        ``±eps_ud``. Die Rechenwerte bestimmen, wo die Plateaus liegen
        (``f_cd`` oder ``f_ck``, ``f_yd`` oder ``f_yk``); Moduln und
        Dehnungsgrenzen bleiben -- wie beim Loeser der Platte
        (:class:`~opencivil.nachweis.querschnittsloeser.Werkstoffsatz`).
        """
        liste: List[Werkstoff] = []
        index: Dict[str, int] = {}
        for stoff in self.baustoffe:
            w = lambda k: abs(self.kennwert(e, stoff, k))
            bemessung = self.satz(stoff) == "bemessung"
            if stoff.art is Baustoffart.BETON:
                f_c = w("f_cd") if bemessung else w("f_ck")
                eps_c1d, eps_c2d = w("eps_c1d"), w("eps_c2d")
                if self.betongesetz(stoff) == "block":
                    gesetz = Spannungsblock(f_cd=f_c, eps_c2d=eps_c2d).spannung
                else:
                    k = (self.kennwert(e, stoff, "k_sigma") if bemessung
                         else _K_SIGMA.funktion(E_cd=w("E_cd"), f_cd=f_c))
                    gesetz = Betongesetz(f_cd=f_c, eps_c1d=eps_c1d, eps_c2d=eps_c2d,
                                         k_sigma=k).spannung
                liste.append(Werkstoff(stoff.name, gesetz, -eps_c2d, math.inf,
                                       c_punkt=(eps_c1d, eps_c2d), verdraengbar=True))
            else:
                gesetz = Stahlgesetz(
                    E_s=w("E_s"), f_yd=w("f_yd") if bemessung else w("f_yk"),
                    f_yd_druck=w("f_yd_druck") if bemessung else w("f_yk_druck"),
                    eps_ud=w("eps_ud"))
                liste.append(Werkstoff(stoff.name, gesetz.spannung, -gesetz.eps_ud,
                                       gesetz.eps_ud))
            index[stoff.id] = len(liste) - 1
        return liste, (lambda stoff: index[stoff.id])

    def werkstoffe_protokollieren(self, p: Protokoll, e: Eingaben, basis: str) -> None:
        """Die Gesetze, mit denen gerechnet wird, und die Werte darin."""
        werte = Zwischenwerte(basis)
        for stoff in self.baustoffe:
            bemessung = self.satz(stoff) == "bemessung"
            satz = "Bemessungswerte" if bemessung else "charakteristische Werte"
            symbol = lambda k: stoff.definition(k).symbol
            if stoff.art is Baustoffart.BETON:
                f_c = "f_cd" if bemessung else "f_ck"
                if self.betongesetz(stoff) == "block":
                    latex = Spannungsblock(1.0, 1.0).latex()
                    titel = f"{stoff.name}: Spannungsblock 0.85·x, {satz}"
                    referenz = ""
                else:
                    latex = Betongesetz(1.0, 1.0, 1.0, 1.0).latex()
                    titel = f"{stoff.name}: Parabel-Rechteck-Beziehung, {satz}"
                    referenz = "SIA 262:2025, 4.2.1.6"
                if not bemessung:
                    latex = latex.replace("f_{cd}", "f_{ck}")
                p.ansatz(latex, titel=titel, referenz=referenz)
                if not bemessung and self.betongesetz(stoff) != "block":
                    k = _K_SIGMA.funktion(E_cd=abs(self.kennwert(e, stoff, "E_cd")),
                                          f_cd=abs(self.kennwert(e, stoff, "f_ck")))
                    p.formel(werte.zahl(f"k_sigma_{kennung_aus(stoff.id)}",
                                        rf"k_{{\sigma,k}}", k, stellen=3),
                             _K_SIGMA.vorlage_latex,
                             {"E_cd": e[self._name(stoff, "E_cd")],
                              "f_cd": e[self._name(stoff, "f_ck")]},
                             titel="Krümmungsbeiwert mit charakteristischer Festigkeit",
                             referenz=_K_SIGMA.referenz)
                p.tabelle(kopf=["Kennwert", "Wert"], zeilen=[
                    [Mathe(symbol(k)), Mathe(e[self._name(stoff, k)].formatiert(latex=True))]
                    for k in (f_c, "eps_c1d", "eps_c2d")], titel=f"Werte {stoff.name}",
                    ausrichtung="lr")
            else:
                f_s = "f_yd" if bemessung else "f_yk"
                latex = Stahlgesetz(1.0, 1.0, 1.0, 1.0).latex()
                if not bemessung:
                    latex = latex.replace("f_{yd}", "f_{yk}")
                p.ansatz(latex, titel=f"{stoff.name}: bilineare Beziehung, {satz}",
                         referenz="SIA 262:2025, 4.2.2.4")
                p.tabelle(kopf=["Kennwert", "Wert"], zeilen=[
                    [Mathe(symbol(k)), Mathe(e[self._name(stoff, k)].formatiert(latex=True))]
                    for k in (f_s, f"{f_s}_druck", "E_s", "eps_ud")],
                    titel=f"Werte {stoff.name}", ausrichtung="lr")

    def grundbezuege(self) -> List[Eingabebezug]:
        """Was jeder Nachweis der Analyse liest: den Schwerpunkt und die Werkstoffe."""
        return ([Eingabebezug("y_S", self.id_von("y_S")),
                 Eingabebezug("z_S", self.id_von("z_S"))]
                + self.werkstoffbezuege())

    def interaktion(self, e: Eingaben) -> Tuple[Querschnitt, List[str]]:
        """
        Der Querschnitt im Bruchzustand, mit den gewaehlten Werkstoffgesetzen
        und dem Schwerpunkt aus dem Rechenwerk als Bezugspunkt -- dazu je
        Bewehrung der Name ihres Elements.
        """
        # Einmal je Satz von Werten: die Nachweise der Analyse teilen sich den
        # Querschnitt und mit ihm alles, was er schon gesucht hat.
        schluessel = tuple(e.g(b.name).si for b in self.grundbezuege())
        if schluessel not in self._interaktionen:
            werkstoffe, index = self.werkstoffe(e)
            teile, bewehrung, herkunft = self.geometrie(index)
            self._interaktionen[schluessel] = (Querschnitt(
                werkstoffe=werkstoffe, teile=teile, bewehrung=bewehrung,
                bezug=(e.g("y_S").si, e.g("z_S").si)), herkunft)
        return self._interaktionen[schluessel]

    # -- Fuer die Nachweise: Geometrie in Metern ------------------------------------

    def geometrie(self, index_von: Callable[[Baustoff], int],
                  ) -> Tuple[List[Teil], List[Bewehrung], List[str]]:
        """
        Polygone und Bewehrung in Metern, mit den Werkstoffen als Index --
        dazu je Bewehrung der Name ihres Elements, fuer die Kraefte in der Probe.
        """
        mm = 1e-3
        teile = [Teil(punkte=tuple((y * mm, z * mm) for y, z in f.punkte),
                      werkstoff=index_von(f.stoff) if f.stoff is not None else None,
                      eltern=self.eltern[i])
                 for i, f in enumerate(self.flaechen)]
        bewehrung: List[Bewehrung] = []
        herkunft: List[str] = []
        for g in self.gruppen:
            stahl = index_von(g.stahl)
            if g.art == Linienart.FLAECHE.value:
                mitte = ((g.von[0] + g.bis[0]) / 2.0, (g.von[1] + g.bis[1]) / 2.0)
                beton = self.beton_an(mitte)
                stuecke = linie_als_bewehrung(
                    (g.von[0] * mm, g.von[1] * mm), (g.bis[0] * mm, g.bis[1] * mm),
                    g.flaeche * mm * mm, stahl,
                    index_von(beton) if beton is not None else None)
                bewehrung += stuecke
                herkunft += [g.name] * len(stuecke)
                continue
            einzeln = math.pi * g.durchmesser ** 2 / 4.0 * mm * mm
            for p in g.punkte:
                beton = self.beton_an(p)
                bewehrung.append(Bewehrung(
                    lage=(p[0] * mm, p[1] * mm), flaeche=einzeln, werkstoff=stahl,
                    verdraengt=index_von(beton) if beton is not None else None))
                herkunft.append(g.name)
        return teile, bewehrung, herkunft

    def schubwaende(self, f_sd: Callable[[Wandangabe], float],
                    f_cd: Callable[[Wandangabe], float], k_c: float) -> List[Wand]:
        """Die Schubwaende in Metern, mit den Festigkeiten, die der Nachweis waehlt."""
        mm = 1e-3
        return [Wand(name=w.name, von=(w.von[0] * mm, w.von[1] * mm),
                     bis=(w.bis[0] * mm, w.bis[1] * mm), b_w=w.dicke * mm,
                     a_sw_s=w.a_sw_s * mm, f_sd=f_sd(w), f_cd=f_cd(w), k_c=k_c)
                for w in self.waende]

    @property
    def beton_ecken(self) -> List[Tuple[Punkt, Baustoff]]:
        """Jede Ecke eines Polygons mit Material -- fuer das Rissmoment, in mm."""
        return [(p, f.stoff) for f in self.flaechen if f.stoff is not None for p in f.punkte]
