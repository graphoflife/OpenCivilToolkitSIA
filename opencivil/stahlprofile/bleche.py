"""
opencivil/stahlprofile/bleche.py -- die Bleche eines Stahlprofils, fuer seine Querschnittsklasse.

VERANTWORTUNG:
Je Form die ebenen Teile eines Profils, an denen SIA 263:2013 die
Schlankheit misst (Tabellen 5a und 5b) und die mitwirkende Breite rechnet
(4.5.3): die Flansche und der Steg des I und des U, die vier Waende des
Rechteckrohrs -- und das Rundrohr als Ganzes, dessen Grenze D/t heisst. Jedes
Blech liegt, wo das Profil in der Zeichnung liegt
(:class:`~opencivil.stahlprofile.lage.Profillage`), und heisst nach seiner
Lage dort: «Flansch oben, links», auch am gedrehten Profil.

ZWEI BREITEN AUF EINER GERADEN:
Die theoretische Breite ``b`` laeuft auf der Mittelebene des Blechs zwischen
den Mittellinien der Bleche, an denen es haengt -- beim einseitig gehaltenen
von der Mittellinie des Stegs bis zum freien Rand. Mit ihr rechnet die
mitwirkende Breite: 4.5.3.3 misst von den theoretischen Scheibenschnittlinien
aus. Die Schlankheit misst die Breite ``c``, die die Bilder der Tabellen 5a
und 5b zeigen: beim gewalzten Profil ohne die Ausrundungen, beim
Rechteckrohr ohne 1.5 t je Seite, ob kalt- oder warmgefertigt -- Tabelle 5a
unterscheidet nicht. Sie liegt auf derselben Geraden, ``vor`` nach dem
Anfang der theoretischen.

DAS UNP -- nach Vorgabe, nicht nachgeschlagen:
Seine Flansche sind geneigt. Gerechnet wird mit der Flanschdicke ``t_f`` der
Tabelle, die in der Mitte des Flanschs gilt, und mit ``r_1`` wie beim UPE
mit ``r``: der Steg bis zur Ausrundung misst so ``h - 2 t_f - 2 r_1``, etwas
mehr als zwischen den dickeren Wurzeln der Flansche -- auf der sicheren
Seite.

DER KASTEN:
Die Waende eines Rechteckrohrs mindern nach dem genaueren Faktor fuer
Kastentraeger (:func:`~opencivil.stahlbau.klasse.abminderung_kasten`); das
weiss jedes seiner Bleche (:attr:`Blech.kasten`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Dict, List, Mapping, Tuple

from opencivil.core.wahl import Wahl
from opencivil.stahlprofile import tabelle
from opencivil.stahlprofile.lage import Profillage

Punkt = Tuple[float, float]


class Halterung(Wahl):
    """Wie ein Blech gehalten ist -- danach waehlt die Norm ihre Tabelle."""

    BEIDSEITIG = "beidseitig"
    EINSEITIG = "einseitig"
    ROHR = "Rundrohr"

    @property
    def tabelle(self) -> str:
        """Wo seine Grenzen stehen: Tabelle 5a fuer beidseitig gestuetzte Scheiben und Rohre, sonst 5b."""
        return "Tabelle 5b" if self is Halterung.EINSEITIG else "Tabelle 5a"


@dataclass(frozen=True)
class Blech:
    """
    Ein Blech eines Profils, in mm in der Zeichnung -- siehe Dateikopf.
    ``von`` und ``bis`` sind die Enden der theoretischen Breite, beim
    einseitig gehaltenen ``von`` am gehaltenen Rand und ``bis`` am freien.
    Beim Rundrohr liegen beide in seiner Mitte, und ``c`` ist ``D``.
    """

    name: str
    halterung: Halterung
    von: Punkt
    bis: Punkt
    t: float
    c: float
    vor: float = 0.0
    kasten: bool = False
    """Ob es eine Wand eines Kastens ist -- siehe Dateikopf."""

    @property
    def b(self) -> float:
        """Die theoretische Breite."""
        return math.dist(self.von, self.bis)

    def punkt(self, a: float) -> Punkt:
        """Der Punkt auf der Mittelebene, ``a`` von ``von`` entfernt."""
        b = self.b
        if b == 0.0:
            return self.von
        return (self.von[0] + a / b * (self.bis[0] - self.von[0]),
                self.von[1] + a / b * (self.bis[1] - self.von[1]))

    @property
    def lichte_enden(self) -> Tuple[Punkt, Punkt]:
        """Die Enden der Breite ``c``, an der die Schlankheit gemessen wird."""
        return self.punkt(self.vor), self.punkt(self.vor + self.c)

    def streifen(self, von: float, bis: float) -> Tuple[Punkt, ...]:
        """Das Rechteck des Blechs zwischen ``von`` und ``bis``, ab seinem Anfang gemessen, so dick wie es."""
        a, b = self.punkt(von), self.punkt(bis)
        laenge = self.b
        n = (-(self.bis[1] - self.von[1]) / laenge * self.t / 2.0,
             (self.bis[0] - self.von[0]) / laenge * self.t / 2.0)
        return ((a[0] - n[0], a[1] - n[1]), (b[0] - n[0], b[1] - n[1]),
                (b[0] + n[0], b[1] + n[1]), (a[0] + n[0], a[1] + n[1]))


#: Ein Blech, wie die Form es zeichnet: sein Name aus Woertern -- die
#: Richtungen darin dreht und spiegelt die Lage mit --, die Halterung, die
#: Enden der theoretischen Breite, die Dicke, ``c`` und ``vor``.
_Roh = Tuple[Tuple[str, ...], Halterung, Punkt, Punkt, float, float, float]

_RICHTUNGEN = ("oben", "unten", "links", "rechts")


def _i(m: Mapping[str, float]) -> List[_Roh]:
    h, b, t_w, t_f, r = (m[k] for k in ("h", "b", "t_w", "t_f", "r"))
    mitte = b / 2.0
    flansche = [(("Flansch", ort, seite), Halterung.EINSEITIG, (mitte, z), (spitze, z), t_f,
                 (b - t_w - 2.0 * r) / 2.0, t_w / 2.0 + r)
                for ort, z in (("oben", h - t_f / 2.0), ("unten", t_f / 2.0))
                for seite, spitze in (("links", 0.0), ("rechts", b))]
    return flansche + [_steg(mitte, h, t_f, t_w, r)]


def _u(m: Mapping[str, float], r: float) -> List[_Roh]:
    """Ein U, der Ruecken links: zwei Flansche, je von der Mittellinie des Stegs bis zur Spitze."""
    h, b, t_w, t_f = (m[k] for k in ("h", "b", "t_w", "t_f"))
    flansche = [(("Flansch", ort), Halterung.EINSEITIG, (t_w / 2.0, z), (b, z), t_f,
                 b - t_w - r, t_w / 2.0 + r)
                for ort, z in (("oben", h - t_f / 2.0), ("unten", t_f / 2.0))]
    return flansche + [_steg(t_w / 2.0, h, t_f, t_w, r)]


def _steg(y: float, h: float, t_f: float, t_w: float, r: float) -> _Roh:
    """Der Steg zwischen den Mittellinien der Flansche, ``c`` bis zu den Ausrundungen."""
    return (("Steg",), Halterung.BEIDSEITIG, (y, t_f / 2.0), (y, h - t_f / 2.0), t_w,
            h - 2.0 * t_f - 2.0 * r, t_f / 2.0 + r)


def _rechteckrohr(m: Mapping[str, float]) -> List[_Roh]:
    """Vier Waende zwischen den Mittellinien der anderen; ``c`` ohne 1.5 t je Seite (Tabelle 5a)."""
    h, b, t = m["h"], m["b"], m["t"]
    links, rechts, unten, oben = t / 2.0, b - t / 2.0, t / 2.0, h - t / 2.0
    return [(("Wand", "oben"), Halterung.BEIDSEITIG, (links, oben), (rechts, oben), t, b - 3.0 * t, t),
            (("Wand", "unten"), Halterung.BEIDSEITIG, (links, unten), (rechts, unten), t, b - 3.0 * t, t),
            (("Wand", "links"), Halterung.BEIDSEITIG, (links, unten), (links, oben), t, h - 3.0 * t, t),
            (("Wand", "rechts"), Halterung.BEIDSEITIG, (rechts, unten), (rechts, oben), t,
             h - 3.0 * t, t)]


def _ror(m: Mapping[str, float]) -> List[_Roh]:
    mitte = (m["D"] / 2.0, m["D"] / 2.0)
    return [(("Wand",), Halterung.ROHR, mitte, mitte, m["t"], m["D"], 0.0)]


#: Die Formen, die ein Kasten sind -- siehe Dateikopf.
_KASTEN = {"rechteckrohr_gerundet"}

#: Je Form, welche Bleche sie hat -- nach dem Schluessel ihrer Vorlage.
_BLECHE: Dict[str, Callable[[Mapping[str, float]], List[_Roh]]] = {
    "i_profil": _i,
    "u_parallel": lambda m: _u(m, m["r"]),
    "u_geneigt": lambda m: _u(m, m["r_1"]),
    "rechteckrohr_gerundet": _rechteckrohr,
    "rundrohr": _ror,
}


def bleche(lage: Profillage) -> List[Blech]:
    """Die Bleche des Profils, wo es in der Zeichnung liegt -- siehe Dateikopf."""
    profil = tabelle.profil(lage.name)
    kasten = profil.form.schluessel in _KASTEN

    def name(woerter: Tuple[str, ...]) -> str:
        rolle, *richtungen = (lage.richtung(w) if w in _RICHTUNGEN else w for w in woerter)
        return " ".join([rolle, ", ".join(richtungen)]) if richtungen else rolle

    return [Blech(name=name(woerter), halterung=halterung, von=lage.setzen(von),
                  bis=lage.setzen(bis), t=t, c=c, vor=vor, kasten=kasten)
            for woerter, halterung, von, bis, t, c, vor in _BLECHE[profil.form.schluessel](profil.masse)]
