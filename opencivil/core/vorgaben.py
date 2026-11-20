"""
opencivil/core/vorgaben.py -- die Zahlen, die ein Nachweis aus seiner Beschreibung liest.

VERANTWORTUNG:
Je Nachweis eine Tafel seiner Vorgaben, in Gruppen (:class:`Gruppe`): was die
Herleitung in ihren Kästen zeigt und die Maske in ihren Karten -- dieselben
Felder in derselben Folge, mit demselben Zeichen (:class:`Feld`). Eine Gruppe
kann sich nach Wahlen der Beschreibung richten (``nach``): drainiert liest
der Grundbruch anderes als undrainiert. Die Rechnung fragt sie mit ihren
eigenen Wahlen (:meth:`Gruppe.fuer`), der Katalog schreibt sie für jede
Stellung aus (:meth:`Gruppe.als_dict`), und die Maske nimmt die zu ihrem
Eintrag (``eingabekarten`` in ``web/js/bausteine.js``).

Bis 2026-11-20 schrieben die Masken von Durchstanzen, Grundbruch, Setzung und
Pfahl die Tafeln von Hand ab: ein neues Feld des Kerns erschien dort nie, und
die Zeichen liefen auseinander (k_δ im Kern, δ_k/φ_k in der Maske).

ZWEI TEXTE:
Die Herleitung beschreibt eine Zahl ausführlich, die Maske hat für ihre
Beschriftung eine Zeile, die abschneidet, was übersteht -- und mit ihm das
Zeichen. Ein Feld trägt darum beide: die ``beschreibung`` und, wo sie zu lang
ist, eine kurze ``beschriftung``; die Maske zeigt die Beschreibung im Titel
über dem Feld, mit dem ``hinweis`` und der Normstelle. Die Schrittweite der
Pfeile (``schritt``) braucht nur die Maske. Die Einheit und die Grenzen nimmt
sie vom Feld der Beschreibung (``katalog.felder``) -- dort steht, in welcher
Einheit der Kern eine Zahl liest.

WIEDERHOLTE GRUPPEN:
Die Schichten unter einem Fundament oder an einem Pfahl haben je dieselben
Felder: eine Gruppe als Vorlage, je Schicht mit ihrer Nummer
(:meth:`Feld.nummeriert`). «#» in einer Beschreibung steht für die Schicht --
in der Herleitung «Schicht 2», in der Maske, deren Karte schon so heisst,
«Schicht». Hat eine Schicht mehrere Gruppen, wie am Pfahl, teilen sie sich
ihren Kasten und ihre Karte: ihre Titel sagen der Maske nur, wo sie einen
Schalter zwischen die Felder setzt (``eingabezeilen``).
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass, replace
from typing import Any, Callable, Dict, Mapping, Sequence, Tuple

from opencivil.core.berechnung import Vorgabe
from opencivil.core.einheiten import Einheit, Groesse
from opencivil.core.protokoll import Abschnitt
from opencivil.core.wert import WertDef

#: Wofür «#» in der Beschreibung eines wiederholten Feldes steht.
SCHICHT = "Schicht"


def mit_index(zeichen: str, i: int) -> str:
    """
    Ein Zeichen mit der Nummer ``i`` im Index: ``d`` wird ``d_{1}``, ``M_E``
    ``M_{E,1}``, ``s_{u,k}`` ``s_{u,k,1}``.
    """
    m = re.fullmatch(r"(.*?)_(?:\{(.*)\}|(.))", zeichen)
    if m is None:
        return f"{zeichen}_{{{i}}}"
    index = m.group(2) if m.group(2) is not None else m.group(3)
    return f"{m.group(1)}_{{{index},{i}}}"


@dataclass(frozen=True)
class Feld:
    """Eine Zahl, die ein Nachweis liest -- in der Herleitung und in der Maske."""

    kurz: str
    """Der Kurzname: so heisst das Feld der Beschreibung, aus dem die Zahl kommt."""

    zeichen: str
    """LaTeX, ohne Mathematikumgebung."""

    einheit: Einheit
    """Die Einheit in der Herleitung."""

    beschreibung: str
    stellen: int = 2
    """Nachkommastellen in der Herleitung."""

    referenz: str = ""
    beschriftung: str = ""
    """Die Beschriftung in der Maske, wo die Beschreibung zu lang ist -- leer: die Beschreibung."""

    schritt: float = 1.0
    """Wie weit ein Pfeil in der Maske die Zahl verschiebt."""

    hinweis: str = ""
    """Was die Maske über dem Feld dazu sagt -- etwa, wie ein Winkel zählt."""

    def vorgabe(self, praefix: str, abschnitt: Abschnitt, gruppe: str,
                groesse: Groesse) -> Tuple[WertDef, Vorgabe]:
        """Die Definition der Zahl und ihre Vorgabe in der Herleitung, im Kasten ``gruppe``."""
        d = WertDef(id=f"{praefix}.{self.kurz}", symbol=self.zeichen, einheit=self.einheit,
                    beschreibung=self.beschreibung, referenz=self.referenz, stellen=self.stellen)
        return d, Vorgabe(id=d.id, ausgabe=d, groesse=groesse, abschnitt=abschnitt, gruppe=gruppe)

    def nummeriert(self, i: int) -> "Feld":
        """Das Feld der Schicht ``i``: ``d`` wird ``d_1``, sein Zeichen ``d_{1}``, «#» «Schicht 1»."""
        return replace(self, kurz=f"{self.kurz}_{i}", zeichen=mit_index(self.zeichen, i),
                       beschreibung=self.beschreibung.replace("#", f"{SCHICHT} {i}"))

    def als_dict(self) -> Dict[str, Any]:
        """Was die Maske von ihm braucht -- «#» steht dort für die Schicht ihrer Karte."""
        beschreibung = self.beschreibung.replace("#", SCHICHT)
        return {"feld": self.kurz, "zeichen": self.zeichen,
                "beschriftung": self.beschriftung or beschreibung, "beschreibung": beschreibung,
                "referenz": self.referenz, "schritt": self.schritt, "hinweis": self.hinweis}


@dataclass(frozen=True)
class Gruppe:
    """Ein Kasten der Herleitung, eine Karte der Maske."""

    titel: str
    felder: Callable[..., Sequence[Feld]]
    """Die Felder, die gelten, in ihrer Folge -- aus den Stellungen der Wahlen in :attr:`nach`."""

    nach: Tuple[str, ...] = ()
    """Nach welchen Wahlen sie sich richtet: die Namen ihrer Felder in der Beschreibung."""

    def fuer(self, objekt: Any) -> Tuple[Feld, ...]:
        """
        Die Felder, die für ``objekt`` gelten -- eine Beschreibung oder ihre
        Rechnung: beide tragen die Wahlen unter denselben Namen.
        """
        return tuple(self.felder(*(getattr(objekt, n) for n in self.nach)))

    def als_dict(self, stellungen: Mapping[str, Sequence[Any]]) -> Dict[str, Any]:
        """
        Für die Maske: je Stellung der Wahlen die Felder, unter den Werten der
        Wahlen mit «|» dazwischen -- ohne Wahl unter «». ``stellungen`` sagt
        je Wahl, welche Werte sie annehmen kann.
        """
        return {"titel": self.titel, "nach": list(self.nach), "felder": {
            "|".join(str(w) for w in werte): [f.als_dict() for f in self.felder(*werte)]
            for werte in itertools.product(*(stellungen[n] for n in self.nach))}}
