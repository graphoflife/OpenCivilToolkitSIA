"""
opencivil/stahlprofile/lage.py -- ein Stahlprofil im gezeichneten Querschnitt.

VERANTWORTUNG:
Wo ein Profil der Tabelle in einer Querschnittsanalyse liegt: seine Umrisse
in der Zeichnung, aus seiner Mitte, seiner Drehung und ob es gespiegelt ist
(:func:`umrisse`); ob Drehen oder Spiegeln es ueberhaupt aendert
(:func:`drehbar`, :func:`spiegelbar`); wie es in Bericht und Meldungen heisst
(:func:`beschreibung`); woran der Zeiger faengt (:func:`fangpunkte`); und
seine Skizze fuer das Fenster der Vorlagen (:func:`skizze`).

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

#: Auf so viele Stellen nach dem Komma in mm liegen die Ecken -- wie beim
#: Einsetzen einer Vorlage, damit die Summe keinen Rundungsrest behaelt.
_STELLEN = 6


def _rahmen(punkte: Sequence[Punkt]) -> Tuple[float, float, float, float]:
    ys = [p[0] for p in punkte]
    zs = [p[1] for p in punkte]
    return min(ys), min(zs), max(ys), max(zs)


@lru_cache(maxsize=None)
def _lokal(name: str) -> Tuple[Tuple[Punkt, ...], ...]:
    """Die Umrisse, wie die Form sie zeichnet -- einmal je Profil: die Tabelle aendert sich nicht."""
    profil = tabelle.profil(name)
    return tuple(tuple(teil) for teil in profil.form.umriss(profil.masse))


def umrisse(name: str, mitte: Punkt = (0.0, 0.0), drehung: int = 0,
            gespiegelt: bool = False) -> List[List[Punkt]]:
    """
    Die Umrisse des Profils ``name`` in der Zeichnung, in mm: der erste
    aussen, die weiteren Loecher -- beim Rohr eines. Siehe Dateikopf. Einen
    Namen, den die Tabelle nicht kennt, sagt ein ``KeyError``
    (:func:`~opencivil.stahlprofile.tabelle.profil`).
    """
    lokal = _lokal(name)
    y0, z0, y1, z1 = _rahmen(lokal[0])
    my, mz = (y0 + y1) / 2, (z0 + z1) / 2
    c, s = _DREHUNG[drehung]
    spiegel = -1 if gespiegelt else 1

    def setzen(p: Punkt) -> Punkt:
        y, z = spiegel * (p[0] - my), p[1] - mz
        return (round(mitte[0] + c * y - s * z, _STELLEN), round(mitte[1] + s * y + c * z, _STELLEN))

    return [[setzen(p) for p in teil] for teil in lokal]


def _gleich(a: Sequence[Sequence[Punkt]], b: Sequence[Sequence[Punkt]]) -> bool:
    """Ob zwei Umrisse dieselben Ecken haben, auf einen Hundertstel Millimeter -- gleich in welcher Folge."""
    def ecken(teil: Sequence[Punkt]) -> set:
        # + 0.0: aus -0.0 wird 0.0, sonst unterschiede sich die Mitte.
        return {(round(y, 2) + 0.0, round(z, 2) + 0.0) for y, z in teil}
    return len(a) == len(b) and all(ecken(p) == ecken(q) for p, q in zip(a, b))


@lru_cache(maxsize=None)
def drehbar(name: str) -> bool:
    """Ob eine Drehung um 90 Grad das Profil aendert -- beim Rundrohr nicht, beim quadratischen Rohr auch nicht."""
    return not _gleich(umrisse(name), umrisse(name, drehung=90))


@lru_cache(maxsize=None)
def spiegelbar(name: str) -> bool:
    """Ob das Spiegeln das Profil aendert -- nur, wenn es zur senkrechten Achse nicht symmetrisch ist, wie das U."""
    return not _gleich(umrisse(name), umrisse(name, gespiegelt=True))


def beschreibung(name: str, drehung: int, gespiegelt: bool) -> str:
    """
    Was das Profil ist, fuer Bericht und Liste: «UPE 200, gespiegelt, um 90°
    gedreht» -- nur, was etwas aendert: ein gespiegeltes I heisst wie jedes.
    """
    teile = [name]
    if gespiegelt and spiegelbar(name):
        teile.append("gespiegelt")
    if drehung and drehbar(name):
        teile.append(f"um {drehung}° gedreht")
    return ", ".join(teile)


def fangpunkte(teile: Sequence[Sequence[Punkt]]) -> List[Punkt]:
    """
    Woran der Zeiger am Profil faengt: die Ecken des umschreibenden
    Rechtecks und die Mitten seiner Seiten -- beim I die Spitzen und Mitten
    der Flansche, so legt sich eine Platte auf den Obergurt.
    """
    y0, z0, y1, z1 = _rahmen(teile[0])
    ym, zm = (y0 + y1) / 2, (z0 + z1) / 2
    return [(y0, z0), (ym, z0), (y1, z0), (y1, zm), (y1, z1), (ym, z1), (y0, z1), (y0, zm)]


def skizze(name: str, drehung: int = 0, gespiegelt: bool = False) -> Teile:
    """
    Das Profil fuer das Fenster der Vorlagen: seine Umrisse um seine Mitte
    -- nicht von unten links wie die Teile der anderen Vorlagen: die Mitte
    kommt an den Einsetzpunkt -- und die zwei Masse, die es von aussen hat,
    Breite unten, Hoehe links, nach der Drehung. Beim Rundrohr nur ``D``.
    """
    teile = umrisse(name, drehung=drehung, gespiegelt=gespiegelt)
    y0, z0, y1, z1 = _rahmen(teile[0])
    m = tabelle.profil(name).masse
    if "D" in m:
        masse = [masslinie((y0, z0), (y1, z0), "D", m["D"], "unten")]
    else:
        quer, hoch = ("h", "b") if drehung in (90, 270) else ("b", "h")
        masse = [masslinie((y0, z0), (y1, z0), quer, m[quer], "unten"),
                 masslinie((y0, z0), (y0, z1), hoch, m[hoch], "links")]
    return Teile(polygone=[{"punkte": teil, "aussparung": i > 0} for i, teil in enumerate(teile)],
                 masslinien=masse)
