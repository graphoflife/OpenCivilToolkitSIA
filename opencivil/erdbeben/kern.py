"""
opencivil/erdbeben/kern.py -- der Kern eines Geschosses: seine Teile, je um ihren Schwerpunkt.

VERANTWORTUNG:
Was ein Geschoss aus der Querschnittsanalyse seines Kerns nimmt
(:class:`Kerndaten`): die zusammenhaengenden Teile der Zeichnung
(:func:`teile`) und ihre Traegheitsmomente, als Prozedur mit Herleitung
(:class:`Kern`). Gezeichnet ist der ganze Kern, alle Waende in x und in y,
wie er im Grundriss liegt: y der Analyse liegt in x des Gebaeudes, z in y
(Benutzer, 2026-11-27). Bis dahin nahm jede Wand ihre eigene Analyse, mit
Anzahl und Lage 0 oder 90 Grad, ueber die ganze Hoehe.

DIE TEILE:
Zusammen haengen Polygone, die ein Stueck Kante gemeinsam haben
(:func:`~opencivil.querschnitt.geometrie.beruehren`) -- eine Ecke allein
genuegt nicht --; was in einem Polygon liegt, gehoert zu ihm. Die Waende
eines Teils sind fest verbunden und biegen sich gemeinsam: sein I gilt um
seinen Schwerpunkt, mit dem Steiner-Anteil seiner Waende, wie im
Bruttoquerschnitt der Analyse. Getrennte Teile verbinden nur die Decken:
jeder biegt sich um seinen eigenen Schwerpunkt, und ihre I werden addiert,
ohne Steiner-Anteil zwischen ihnen (Benutzer, 2026-11-27; nach Vorgabe,
nicht nachgeschlagen). Eine Aussparung trennt ein Polygon hier nie, auch wo
sie es ganz durchschneidet.

EINHEITEN:
Die Zeichnung in mm, die Werte im Rechenwerk in m^4.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import Eingaben, Prozedur
from opencivil.core.einheiten import M4, Groesse
from opencivil.core.latex import Mathe, fest
from opencivil.core.protokoll import Abschnitt, Protokoll
from opencivil.core.wert import WertDef
from opencivil.querschnitt import geometrie as geo

NACH_VORGABE = "nach Vorgabe, nicht nachgeschlagen"

#: Die Traegheitsmomente des Kerns, je mit ihrem Zeichen und was sie sind.
MOMENTE = (("I_y", "I_y", "Trägheitsmoment um y"), ("I_z", "I_z", "Trägheitsmoment um z"),
           ("I_yz", "I_{yz}", "Deviationsmoment"))

#: Was je Teil ins Rechenwerk geht: das, wonach sich die Kraefte am Fuss verteilen.
JE_TEIL = ("I_y", "I_z")

_WAS = {kurz: was for kurz, _, was in MOMENTE}

#: Von mm⁴ der Zeichnung nach m⁴.
MM4 = 1e-12


@dataclass(frozen=True)
class Kernteil:
    """Ein zusammenhaengender Teil des Kerns: seine Polygone und ihre Werte, in mm."""

    nummer: int
    """Sein Platz, ab 1 -- in der Folge, in der seine Polygone gezeichnet sind."""

    polygone: Tuple[str, ...]
    """Die Namen seiner aeussersten Polygone -- was darin liegt, gehoert dazu."""

    werte: geo.Flaechenwerte


def teile(punkte: Sequence[Sequence[geo.Punkt]], namen: Sequence[str],
          eltern: Sequence[Optional[int]],
          gewicht: Callable[[int], float]) -> Tuple[Kernteil, ...]:
    """
    Die zusammenhaengenden Teile einer gueltigen Zeichnung
    (:class:`~opencivil.querschnitt.analyse.Zeichnung`): ``eltern`` sagt je
    Polygon, in welchem es liegt, ``gewicht`` zaehlt es wie dort -- +1 mit
    Material, -1 fuer eine Aussparung darin, 0 fuer Material in Material.
    """
    def aussen(i: int) -> int:
        while eltern[i] is not None:
            i = eltern[i]
        return i

    wurzeln = [i for i in range(len(punkte)) if eltern[i] is None]
    gruppe = {i: i for i in wurzeln}

    def finde(i: int) -> int:
        while gruppe[i] != i:
            i = gruppe[i]
        return i

    for a, b in itertools.combinations(wurzeln, 2):
        ga, gb = finde(a), finde(b)
        if ga != gb and geo.beruehren(punkte[a], punkte[b]):
            gruppe[max(ga, gb)] = min(ga, gb)
    je_gruppe: Dict[int, List[int]] = {}
    for i in range(len(punkte)):
        je_gruppe.setdefault(finde(aussen(i)), []).append(i)
    return tuple(
        Kernteil(nummer=nummer, polygone=tuple(namen[i] for i in polygone if eltern[i] is None),
                 werte=geo.summe([(gewicht(i), geo.flaechenwerte(punkte[i]))
                                  for i in polygone if gewicht(i) != 0.0]))
        for nummer, (_, polygone) in enumerate(sorted(je_gruppe.items()), start=1))


@dataclass(frozen=True)
class Kerndaten:
    """Was ein Kern aus seiner Querschnittsanalyse nimmt: Namen, E_cm und die Teile."""

    kennung: str
    """Die Kennung der Querschnittsanalyse."""

    analyse: str
    """Ihr Name."""

    beton: str
    """Der Name ihres Betons."""

    E_cm: str
    """Die Wert-ID von dessen E_cm."""

    teile: Tuple[Kernteil, ...]


class Kern(Prozedur):
    """
    Die Traegheitsmomente eines Kerns: je Teil um seinen Schwerpunkt und
    zusammen, ohne Steiner-Anteil zwischen den Teilen -- siehe Dateikopf. Je
    Teil gehen I_y und I_z ins Rechenwerk, wo es mehr als einen gibt: nach
    ihnen verteilen sich die Kraefte am Fuss.
    """

    THEMA = "Erdbeben"

    def __init__(self, basis: str, daten: Kerndaten, abschnitt: Abschnitt) -> None:
        self.daten = daten
        wo = f"des Kerns «{daten.analyse}»"
        self.d: Dict[str, WertDef] = {
            kurz: WertDef(id=f"{basis}.{kurz}", symbol=symbol, einheit=M4, stellen=4,
                          beschreibung=f"{was} {wo}")
            for kurz, symbol, was in MOMENTE}
        self.je_teil: Tuple[Dict[str, WertDef], ...] = () if len(daten.teile) < 2 else tuple(
            {kurz: WertDef(id=f"{basis}.{kurz}_{t.nummer}",
                           symbol=f"I_{{{kurz[2:]},{t.nummer}}}", einheit=M4, stellen=4,
                           beschreibung=f"{_WAS[kurz]} von Teil {t.nummer} {wo}")
             for kurz in JE_TEIL}
            for t in daten.teile)
        """Je Teil seine Definitionen -- leer, wo der Kern ein Teil ist."""
        super().__init__(basis, ausgaben=[*self.d.values(),
                                          *(d for teil in self.je_teil for d in teil.values())],
                         titel=f"Kern «{daten.analyse}»", abschnitt=abschnitt)

    def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]:
        teile_ = self.daten.teile
        p.titel(f"Kern «{self.daten.analyse}»", ebene=3)
        p.erklaerung(
            "Getrennte Teile des Kerns verbinden nur die Decken: jeder biegt sich um seinen "
            "eigenen Schwerpunkt, und ihre Trägheitsmomente werden addiert, ohne "
            "Steiner-Anteil zwischen ihnen. Innerhalb eines Teils bleibt er – seine Wände sind "
            "fest verbunden und biegen sich gemeinsam.")
        if len(teile_) > 1:
            p.text(f"{len(teile_)} getrennte Teile – Polygone, die keine Kante teilen: jeder "
                   f"zählt um seinen eigenen Schwerpunkt.")
        else:
            p.text("Ein zusammenhängender Teil: seine Trägheitsmomente sind die des "
                   "Querschnitts.")
        p.ansatz(r"I_y = \sum_k I_{y,k} \qquad I_z = \sum_k I_{z,k} \qquad "
                 r"I_{yz} = \sum_k I_{yz,k}",
                 titel="Trägheitsmomente des Kerns, je Teil um seinen Schwerpunkt",
                 referenz=NACH_VORGABE, name="Trägheitsmomente des Kerns")
        p.tabelle(
            kopf=["Teil", "Polygone", Mathe(r"A\ [\mathrm{m}^2]"), Mathe(r"y_S\ [\mathrm{m}]"),
                  Mathe(r"z_S\ [\mathrm{m}]"), Mathe(r"I_y\ [\mathrm{m}^4]"),
                  Mathe(r"I_z\ [\mathrm{m}^4]"), Mathe(r"I_{yz}\ [\mathrm{m}^4]")],
            zeilen=[[str(t.nummer), ", ".join(t.polygone), Mathe(fest(t.werte.A * 1e-6, 3)),
                     Mathe(fest(t.werte.y_S * 1e-3, 3)), Mathe(fest(t.werte.z_S * 1e-3, 3)),
                     *(Mathe(fest(getattr(t.werte, kurz) * MM4, 4)) for kurz, _, _ in MOMENTE)]
                    for t in teile_],
            titel="Teile des Kerns – Fläche und Schwerpunkt in der Zeichnung, die "
                  "Trägheitsmomente um den eigenen Schwerpunkt",
            ausrichtung="llrrrrrr")
        ergebnis: Dict[str, Groesse] = {}
        for kurz, _, _ in MOMENTE:
            wert = self.d[kurz].belegen(Groesse.aus_si(
                sum(getattr(t.werte, kurz) for t in teile_) * MM4, M4))
            p.wert(wert, gruppe=f"Kern «{self.daten.analyse}»")
            ergebnis[wert.id] = wert.groesse
        for t, definitionen in zip(teile_, self.je_teil):
            for kurz, d in definitionen.items():
                ergebnis[d.id] = Groesse.aus_si(getattr(t.werte, kurz) * MM4, M4)
        return ergebnis
