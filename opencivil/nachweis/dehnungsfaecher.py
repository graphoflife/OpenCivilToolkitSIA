"""
opencivil/nachweis/dehnungsfaecher.py -- Die zulaessigen Dehnungsebenen einer Platte.

VERANTWORTUNG:
Wo die Dehnungsebene einer Platte im Bruchzustand liegen darf, an einer
Stelle -- auf zwei Arten geschrieben, fuer zwei Nutzer:

* :func:`faecher` faehrt den Rand ab, Ebene fuer Ebene. Daraus baut
  :class:`~opencivil.nachweis.resistenzlinie.Ebenenlinie` die genaue
  M-N-Resistenzlinie.
* :func:`grenzen` schreibt dieselben Grenzen als Bedingungen an einzelne
  Stellen. Damit endet jede Linie der Spannung-Dehnung-Analyse am selben
  Rand, und die Resistenzlinie sagt, welche Grenze ihren Bruchzustand
  bestimmt.

WIE DER FAECHER ENTSTEHT:
Welche Grenze den Faecher begrenzt, wechselt unterwegs dreimal --
entsprechend wird er in drei Abschnitten je Momentenvorzeichen abgefahren:

    1a  Drehung um die unterste Lage bei eps_ud; die Oberkante geht von Zug
        bis auf -eps_c2d. Massgebend ist der Stahl.
    1b  Drehung um die Oberkante bei -eps_c2d; die Unterkante geht bis auf
        null. Massgebend ist die gedrueckte Randfaser.
    1c  Drehung um den Punkt C; die Unterkante geht bis auf -eps_c1d.
        Der Querschnitt ist ganz gedrueckt, massgebend ist eps_c1d.
    2a/2b/2c  dasselbe spiegelbildlich mit Zug oben     (M < 0)

Der Punkt C liegt bei z_C = h * (1 - eps_c1d / eps_c2d) ab dem gedrueckten Rand
und traegt die Dehnung -eps_c1d. Er ist noetig, weil beim vollstaendig
gedrueckten Querschnitt nicht mehr die Randfaser massgebend ist: reiner Druck
endet bei gleichmaessig -eps_c1d, nicht bei -eps_c2d. Ohne diesen Abschnitt
liefe die Linie an beiden Enden ueber die wahre Grenze hinaus und schnitte sich
selbst -- womit Punkt-in-Linie-Test und Schnittsuche unbrauchbar waeren.

Anfang (gleichmaessiger Zug bei eps_ud) und Ende (gleichmaessiger Druck bei
eps_c1d) sind beiden Faechern gemeinsam, sodass sich eine geschlossene Linie
ergibt.

DIE GRENZEN SIND EXPLIZIT:
``eps_c1d`` und ``eps_c2d`` gibt der Aufrufer mit, ``eps_ud`` steht je Lage
dabei. Frueher las der Faecher sie aus dem Betongesetz -- ein Gesetz, das sie
nicht hat, etwa der Spannungsblock, haette keinen Faecher bekommen.

VORZEICHEN:
    N > 0   Zug
    M > 0   Zug an der Unterseite (Feldmoment)
``z`` von der Oberkante nach unten.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from opencivil.core.berechnung import Eingaben
from opencivil.core.wert import kennung_aus
from opencivil.nachweis.querschnittsloeser import Werkstoffsatz
from opencivil.querschnitt.fasern import Dehnungsgrenze
from opencivil.querschnitt.werkstoffgesetz import Dehnungsebene, Stahlgesetz

#: Schritte je Faecherabschnitt. Die Linie nahe dem reinen Druck laeuft
#: schnell und waere mit weniger sichtbar eckig. Die Zahlen im Bericht haengen
#: nicht daran: die Resistenzlinie sucht jeden Widerstand zwischen zwei
#: Schritten genau.
SCHRITTE = 80

#: Fasern ueber die Hoehe fuer die Betonintegration.
FASERN = 200


@dataclass(frozen=True)
class Linienpunkt:
    """Ein Punkt der Resistenzlinie samt der Dehnungsebene, die ihn erzeugt."""

    N: float
    """Normalkraft in N (Zug positiv)."""

    M: float
    """Moment in Nm (Zug unten positiv)."""

    eps_oben: float
    eps_unten: float
    abschnitt: str = ""


def lagen_aus_eingaben(
    posten, e: Eingaben, satz: Werkstoffsatz = Werkstoffsatz.BEMESSUNG,
) -> List[Tuple[float, float, Stahlgesetz, str]]:
    """
    Je Bewehrungsposten dieser Richtung: (Fläche m^2, z m, Gesetz, Text).

    Die Plateaus des Gesetzes liegen, wo der Wertesatz sie hinlegt -- bei
    ``f_yd`` oder ``f_yk``. Die Eingaben heissen je Sorte
    ``{kennwert}__{sorte}``, mit dem Kurznamen des Wertesatzes.
    """
    gesetze: Dict[str, Stahlgesetz] = {}
    for stahl in {l.stahl.id: l.stahl for l, _, _, _, _ in posten}.values():
        kurz = kennung_aus(stahl.id)
        gesetze[stahl.id] = Stahlgesetz.aus_werten({
            "E_s": e[f"E_s__{kurz}"],
            "f_yd": e[f"{satz.stahl}__{kurz}"],
            "f_yd_druck": e[f"{satz.stahl_druck}__{kurz}"],
            "eps_ud": e[f"eps_ud__{kurz}"],
        })

    lagen = []
    for lage, art, _, _, _ in posten:
        marke = f"{lage.nummer}{art.kuerzel}"
        lagen.append((
            e.g(f"a_s_{marke}").si,
            e.g(f"z_{marke}").si,
            gesetze[lage.stahl.id],
            f"{lage.nummer}. Lage {art.beschriftung}",
        ))
    return lagen


def faecher(
    h: float, staebe: Sequence[Tuple[float, float]], schritte: int, *,
    eps_c1d: float, eps_c2d: float,
) -> List[Tuple[str, Dehnungsebene]]:
    """
    Die Folge der Dehnungsebenen auf dem Rand -- die eigentliche Prozedur.

    ``staebe`` sind ``(z, eps_ud)`` je Lage. Beide Faecher laufen von
    gleichmaessigem Zug bis zu gleichmaessigem Druck; zusammengesetzt ergeben
    sie die geschlossene Resistenzlinie.
    """
    beton_grenze = -eps_c2d
    z_unten = max(z for z, _ in staebe)
    z_oben = min(z for z, _ in staebe)
    eps_ud_unten = min(eps_ud for z, eps_ud in staebe if z == z_unten)
    eps_ud_oben = min(eps_ud for z, eps_ud in staebe if z == z_oben)

    ebenen: List[Tuple[str, Dehnungsebene]] = []

    def strecke(
        marke: str,
        eps_fest: float, z_fest: float,
        eps_von: float, eps_bis: float, z_lauf: float,
        ab: int = 0,
    ) -> Dehnungsebene:
        for i in range(ab, schritte + 1):
            anteil = i / schritte
            eps_lauf = eps_von + (eps_bis - eps_von) * anteil
            ebenen.append((
                marke,
                Dehnungsebene.durch_zwei_punkte(eps_fest, z_fest, eps_lauf, z_lauf, h),
            ))
        return ebenen[-1][1]

    # Drehpunkt C: sobald die Nulllinie den Querschnitt verlassen hat, ist
    # nicht mehr die Randfaser massgebend. Fuer den vollstaendig gedrueckten
    # Querschnitt gilt die Stauchung eps_c1d, und alle Ebenen dieses
    # Abschnitts laufen durch den Punkt
    #     z_C = h * (1 - eps_c1d / eps_c2d)   ab dem gedrueckten Rand
    # mit der Dehnung -eps_c1d. Der reine Druck endet folglich bei
    # gleichmaessig -eps_c1d, nicht bei -eps_c2d.
    anteil_c = 1.0 - eps_c1d / eps_c2d
    z_c_oben = h * anteil_c          # von der Oberkante, wenn oben gedrueckt
    z_c_unten = h * (1.0 - anteil_c)  # von der Oberkante, wenn unten gedrueckt

    # Faecher 1 -- Zug unten, positives Moment
    ende_1a = strecke("1a", eps_ud_unten, z_unten, eps_ud_unten, beton_grenze, 0.0)
    strecke("1b", beton_grenze, 0.0, ende_1a.eps_unten, 0.0, h, ab=1)
    strecke("1c", -eps_c1d, z_c_oben, 0.0, -eps_c1d, h, ab=1)

    # Faecher 2 -- Zug oben, negatives Moment; rueckwaerts angehaengt, damit
    # eine geschlossene Linie entsteht.
    merker = len(ebenen)
    ende_2a = strecke("2a", eps_ud_oben, z_oben, eps_ud_oben, beton_grenze, h)
    strecke("2b", beton_grenze, h, ende_2a.eps_oben, 0.0, 0.0, ab=1)
    strecke("2c", -eps_c1d, z_c_unten, 0.0, -eps_c1d, 0.0, ab=1)
    rueck = ebenen[merker:]
    del ebenen[merker:]
    ebenen.extend(reversed(rueck))
    return ebenen


def grenzen(
    h: float, staebe: Sequence[Tuple[float, float, str]], *,
    eps_c1d: float, eps_c2d: float,
) -> Tuple[List[Dehnungsgrenze], Tuple[str, ...]]:
    """
    Dieselben Grenzen als Bedingungen an einzelne Stellen, samt Namen.

    ``staebe`` sind ``(z, eps_ud, Name)`` je Lage. Der Beton an beiden
    Raendern bis ``-eps_c2d``; im Punkt C, im Abstand
    ``h·(1 - eps_c1d/eps_c2d)`` vom gedrueckten Rand, bis ``-eps_c1d`` -- das
    zaehlt erst, wenn der ganze Querschnitt gedrueckt ist, und so ist die
    Bedingung auch gebaut: solange ein Rand nicht gedrueckt ist, haelt sie
    von selbst; jede Stahllage bis ``±eps_ud``. Der Arm gilt ab der halben
    Hoehe, wie in :mod:`opencivil.querschnitt.fasern`.
    """
    halb = h / 2.0
    z_c = h * (1.0 - eps_c1d / eps_c2d)
    paare = [
        (Dehnungsgrenze(arm=-halb, eps_min=-eps_c2d, eps_max=math.inf), "Beton am oberen Rand"),
        (Dehnungsgrenze(arm=halb, eps_min=-eps_c2d, eps_max=math.inf), "Beton am unteren Rand"),
        (Dehnungsgrenze(arm=z_c - halb, eps_min=-eps_c1d, eps_max=math.inf), "Beton im Punkt C"),
        (Dehnungsgrenze(arm=halb - z_c, eps_min=-eps_c1d, eps_max=math.inf), "Beton im Punkt C"),
    ] + [(Dehnungsgrenze(arm=z - halb, eps_min=-eps_ud, eps_max=eps_ud), name)
         for z, eps_ud, name in staebe]
    return [g for g, _ in paare], tuple(n for _, n in paare)
