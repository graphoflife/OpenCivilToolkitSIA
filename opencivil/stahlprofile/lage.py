"""
opencivil/stahlprofile/lage.py -- ein Stahlprofil im gezeichneten Querschnitt.

VERANTWORTUNG:
Wo ein Profil der Tabelle oder aus Vollstahl in einer Querschnittsanalyse liegt
(:class:`Profillage`): aus seiner Mitte, seiner Drehung und ob es gespiegelt
ist, seine Umrisse in der Zeichnung und wie es in Bericht und Meldungen
heisst; ob Drehen oder Spiegeln es ueberhaupt aendert (:func:`drehbar`,
:func:`spiegelbar`); woran der Zeiger faengt (:func:`fangpunkte`); und seine
Skizze fuer das Fenster der Vorlagen (:func:`skizze`). Wohin seine Bleche
kommen, rechnet dieselbe Lage (:mod:`~opencivil.stahlprofile.bleche`).

DIE MITTE:
Die Mitte des umschreibenden Rechtecks, in mm -- nicht der Schwerpunkt, der
beim U neben ihr liegt. An ihr haengt das Profil in der Zeichnung (ein
Knoten), um sie dreht es sich. Ungedreht steht es wie in der Tabelle
(:mod:`~opencivil.stahlprofile.formen`): der Steg senkrecht, beim U der
Ruecken links.

DREHEN UND SPIEGELN:
Erst gespiegelt, an der senkrechten Achse durch die Mitte -- beim U ist der
Ruecken dann rechts --, danach gedreht um 0, 90, 180 oder 270 Grad gegen den
Uhrzeigersinn, mit y nach rechts und z nach oben. Ein U um 90 Grad ist
nach oben offen, ein I um 90 Grad liegt: der Steg waagrecht.

GERECHNET WIRD MIT DEM UMRISS:
Die Querschnittsanalyse rechnet mit dem Vieleck, nicht mit den Formeln der
Tabelle: Fasern, Schwerpunkt und Traegheitsmomente kommen aus ihm, wie bei
jeder gezeichneten Flaeche. Wie genau es die Tabelle trifft, steht bei
:data:`~opencivil.stahlprofile.formen.BOGENECKEN`.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import List, Sequence, Tuple

from opencivil.querschnitt.vorlagen import Teile, masslinie
from opencivil.stahlprofile import tabelle

Punkt = Tuple[float, float]

#: Was der Bericht zu einem Profil sagt, unter dem Satz zu den Polygonen
#: (:meth:`~opencivil.querschnitt.analyse.Querschnittsanalyse.aufbau_protokollieren`).
#: Ein halbes Prozent gegen die Formeln der Formen: so weit liegt das UNP mit
#: I_z daneben (0.44 %), die anderen Reihen trifft der Umriss auf 0.33 %
#: (:data:`~opencivil.stahlprofile.formen.BOGENECKEN`). Gegen die Werte der
#: Tabelle des Benutzers ist es beim UNP bis 0.9 %: dort sind sie von Hand
#: eingetippt, mit drei Stellen (tests/test_stahlprofile.py).
IM_BERICHT = ("Ein Stahlprofil zählt mit seinem Umriss: die Ausrundungen als Vieleck, "
              "ein Rohr mit seinem Loch als Aussparung. Fläche und Trägheitsmomente "
              "weichen so höchstens ein halbes Prozent von den Kennwerten ab, mit denen "
              "das Balkensystem dasselbe Profil rechnet.")

#: Unter diesem Schluessel steht das Profil bei den Vorlagen des
#: Zeichenfensters: es setzt ein Profil ein, keine Flaeche (Plan vom
#: 2026-11-25, Schritt 11).
VORLAGE = "stahlprofil"

#: Um so viele Grad gegen den Uhrzeigersinn laesst sich ein Profil drehen.
DREHUNGEN: Tuple[int, ...] = (0, 90, 180, 270)

#: cos und sin je Drehung -- genau, ohne Rundungsrest der Winkelfunktionen.
_DREHUNG = {0: (1, 0), 90: (0, 1), 180: (-1, 0), 270: (0, -1)}

#: Die vier Richtungen der Zeichnung, als Einheitsvektor -- so heisst ein
#: Blech nach seiner Lage, auch am gedrehten Profil (:meth:`Profillage.richtung`).
_RICHTUNGEN = {"oben": (0, 1), "unten": (0, -1), "links": (-1, 0), "rechts": (1, 0)}

#: Auf so viele Stellen nach dem Komma in mm liegen die Ecken -- wie beim
#: Einsetzen einer Vorlage, damit die Summe keinen Rundungsrest behaelt.
_STELLEN = 6

#: So viele Profile behaelt jeder Speicher unten -- die der Tabelle alle,
#: dazu die frei eingegebenen aus Vollstahl, deren Zahl offen ist.
_GEMERKT = 4096


def _rahmen(punkte: Sequence[Punkt]) -> Tuple[float, float, float, float]:
    ys = [p[0] for p in punkte]
    zs = [p[1] for p in punkte]
    return min(ys), min(zs), max(ys), max(zs)


@lru_cache(maxsize=_GEMERKT)
def _lokal(name: str) -> Tuple[Tuple[Punkt, ...], ...]:
    """Die Umrisse, wie die Form sie zeichnet -- einmal je Profil: sein Name sagt seine Masse."""
    profil = tabelle.profil(name)
    return tuple(tuple(teil) for teil in profil.form.umriss(profil.masse))


@lru_cache(maxsize=_GEMERKT)
def _mitte_lokal(name: str) -> Punkt:
    """Die Mitte des umschreibenden Rechtecks, wie die Form das Profil zeichnet."""
    y0, z0, y1, z1 = _rahmen(_lokal(name)[0])
    return (y0 + y1) / 2, (z0 + z1) / 2


@dataclass(frozen=True)
class Profillage:
    """
    Ein Profil, wie es im Querschnitt liegt: sein Name, seine Mitte in mm,
    seine Drehung und ob es gespiegelt ist -- siehe Dateikopf. Einen Namen,
    der nicht geht, sagt ein ``KeyError``, sobald etwas gerechnet wird
    (:func:`~opencivil.stahlprofile.tabelle.profil`).
    """

    name: str
    mitte: Punkt = (0.0, 0.0)
    drehung: int = 0
    gespiegelt: bool = False

    def setzen(self, p: Punkt) -> Punkt:
        """Ein Punkt, wie die Form das Profil zeichnet, an seiner Stelle in der Zeichnung."""
        my, mz = _mitte_lokal(self.name)
        c, s = _DREHUNG[self.drehung]
        y, z = (-1 if self.gespiegelt else 1) * (p[0] - my), p[1] - mz
        return (round(self.mitte[0] + c * y - s * z, _STELLEN),
                round(self.mitte[1] + s * y + c * z, _STELLEN))

    def richtung(self, wort: str) -> str:
        """Wohin «oben», «unten», «links» oder «rechts» der Form in der Zeichnung zeigt."""
        y, z = _RICHTUNGEN[wort]
        y = -y if self.gespiegelt else y
        c, s = _DREHUNG[self.drehung]
        gedreht = (c * y - s * z, s * y + c * z)
        return next(k for k, v in _RICHTUNGEN.items() if v == gedreht)

    @property
    def umrisse(self) -> List[List[Punkt]]:
        """Die Umrisse in der Zeichnung, in mm: der erste aussen, die weiteren Loecher -- beim Rohr eines."""
        return [[self.setzen(p) for p in teil] for teil in _lokal(self.name)]

    @property
    def beschreibung(self) -> str:
        """
        Was das Profil ist, fuer Bericht und Liste: «UPE 200, gespiegelt, um
        90° gedreht» -- nur, was etwas aendert: ein gespiegeltes I heisst wie
        jedes.
        """
        teile = [self.name]
        if self.gespiegelt and spiegelbar(self.name):
            teile.append("gespiegelt")
        if self.drehung and drehbar(self.name):
            teile.append(f"um {self.drehung}° gedreht")
        return ", ".join(teile)


def _gleich(a: Sequence[Sequence[Punkt]], b: Sequence[Sequence[Punkt]]) -> bool:
    """Ob zwei Umrisse dieselben Ecken haben, auf einen Hundertstel Millimeter -- gleich in welcher Folge."""
    def ecken(teil: Sequence[Punkt]) -> set:
        # + 0.0: aus -0.0 wird 0.0, sonst unterschiede sich die Mitte.
        return {(round(y, 2) + 0.0, round(z, 2) + 0.0) for y, z in teil}
    return len(a) == len(b) and all(ecken(p) == ecken(q) for p, q in zip(a, b))


@lru_cache(maxsize=_GEMERKT)
def drehbar(name: str) -> bool:
    """Ob eine Drehung um 90 Grad das Profil aendert -- beim Rundrohr nicht, beim quadratischen Rohr auch nicht."""
    return not _gleich(Profillage(name).umrisse, Profillage(name, drehung=90).umrisse)


@lru_cache(maxsize=_GEMERKT)
def spiegelbar(name: str) -> bool:
    """Ob das Spiegeln das Profil aendert -- nur, wenn es zur senkrechten Achse nicht symmetrisch ist, wie das U."""
    return not _gleich(Profillage(name).umrisse, Profillage(name, gespiegelt=True).umrisse)


def fangpunkte(teile: Sequence[Sequence[Punkt]]) -> List[Punkt]:
    """
    Woran der Zeiger am Profil faengt: die Ecken des umschreibenden
    Rechtecks und die Mitten seiner Seiten -- beim I die Spitzen und Mitten
    der Flansche, so legt sich eine Platte auf den Obergurt.
    """
    y0, z0, y1, z1 = _rahmen(teile[0])
    ym, zm = (y0 + y1) / 2, (z0 + z1) / 2
    return [(y0, z0), (ym, z0), (y1, z0), (y1, zm), (y1, z1), (ym, z1), (y0, z1), (y0, zm)]


def _aussen(profil: tabelle.Profil) -> Tuple[str, ...]:
    """
    Welche Masse die Skizze zeigt: bei Vollstahl die frei eingegebenen --
    beim Vierkant nur ``a`` --, beim Rundrohr ``D``, sonst ``b`` und ``h``.
    """
    frei = tabelle.reihe(profil.reihe).frei
    if frei:
        return tuple(m.schluessel for m in frei)
    return ("D",) if "D" in profil.masse else ("b", "h")


def skizze(name: str, drehung: int = 0, gespiegelt: bool = False) -> Teile:
    """
    Das Profil fuer das Fenster der Vorlagen: seine Umrisse um seine Mitte
    -- nicht von unten links wie die Teile der anderen Vorlagen: die Mitte
    kommt an den Einsetzpunkt -- und die Masse, die es von aussen hat
    (:func:`_aussen`), Breite unten, Hoehe links, nach der Drehung; ein
    einziges steht unten.
    """
    teile = Profillage(name, drehung=drehung, gespiegelt=gespiegelt).umrisse
    y0, z0, y1, z1 = _rahmen(teile[0])
    profil = tabelle.profil(name)
    namen = _aussen(profil)
    if len(namen) == 2 and drehung in (90, 270):
        namen = namen[::-1]
    seiten = (((y0, z0), (y1, z0), "unten"), ((y0, z0), (y0, z1), "links"))
    masse = [masslinie(von, bis, n, profil.masse[n], seite)
             for n, (von, bis, seite) in zip(namen, seiten)]
    return Teile(polygone=[{"punkte": teil, "aussparung": i > 0} for i, teil in enumerate(teile)],
                 masslinien=masse)
