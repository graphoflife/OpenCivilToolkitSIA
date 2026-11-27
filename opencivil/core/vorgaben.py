"""
opencivil/core/vorgaben.py -- die Zahlen, die ein Nachweis aus seiner Beschreibung liest.

VERANTWORTUNG:
Je Nachweis eine Tafel seiner Vorgaben, in Gruppen (:class:`Gruppe`): was die
Herleitung in ihren Kästen zeigt und die Maske in ihren Kacheln -- dieselben
Felder in derselben Folge, mit demselben Zeichen (:class:`Feld`). Eine Gruppe
kann sich nach Wahlen der Beschreibung richten (``nach``): drainiert liest
der Grundbruch anderes als undrainiert. Die Rechnung fragt sie mit ihren
eigenen Wahlen (:meth:`Gruppe.fuer`), der Katalog schreibt sie für jede
Stellung aus (:meth:`Gruppe.als_dict`), und die Maske nimmt die zu ihrem
Eintrag (``eingabegruppen`` in ``web/js/bausteine.js``), je Gruppe eine
Kachel (``gruppenkapitel`` in ``web/js/kapitel.js``).

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

ENGER NACH DEN WAHLEN:
Ein Feld kann nach den Wahlen enger begrenzt sein als sein Feld in der
Beschreibung (:attr:`Feld.bis`): η_a eines Pfahls ist höchstens der
Grenzwert seiner Grundlage. Die Maske weist eine grössere Zahl ab, mit dem
Satz des Feldes. Legen die Wahlen die Zahl fest (:attr:`Feld.fest`), steht
sie grau in der Maske, und die Herleitung rechnet mit ihr statt mit der
Zahl der Beschreibung -- η_a aus der Grundlage (Benutzer, 2026-11-27).

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
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

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

    bis: Optional[float] = None
    """
    Wie gross die Zahl nach den Wahlen höchstens ist, in :attr:`einheit` --
    wo das enger ist als die Grenze ihres Feldes. Die Maske weist eine
    grössere ab und sagt :attr:`bis_satz`; im Kern prüft die Beschreibung
    selbst (``regeln``), denn nur sie weiss, ob die Zahl gilt.
    """

    bis_satz: str = ""
    """Warum die Zahl höchstens :attr:`bis` ist -- der Satz, mit dem die Maske eine grössere abweist."""

    fest: bool = False
    """
    Ob die Wahlen die Zahl auf :attr:`bis` festlegen: die Maske zeigt sie
    grau, und die Herleitung rechnet mit ihr statt mit der Zahl der
    Beschreibung (:meth:`vorgabe`).
    """

    def __post_init__(self) -> None:
        if self.fest and self.bis is None:
            raise ValueError(f"Das Feld {self.kurz} ist fest, aber ohne Zahl (bis).")

    def vorgabe(self, praefix: str, abschnitt: Abschnitt, gruppe: str,
                groesse: Groesse) -> Tuple[WertDef, Vorgabe]:
        """
        Die Definition der Zahl und ihre Vorgabe in der Herleitung, im Kasten
        ``gruppe`` -- ``groesse``, die Zahl der Beschreibung, oder, ist das
        Feld :attr:`fest`, seine Zahl :attr:`bis`.
        """
        d = WertDef(id=f"{praefix}.{self.kurz}", symbol=self.zeichen, einheit=self.einheit,
                    beschreibung=self.beschreibung, referenz=self.referenz, stellen=self.stellen)
        if self.fest:
            groesse = Groesse(self.bis, self.einheit)
        return d, Vorgabe(id=d.id, ausgabe=d, groesse=groesse, abschnitt=abschnitt, gruppe=gruppe)

    def nummeriert(self, i: int) -> "Feld":
        """Das Feld der Schicht ``i``: ``d`` wird ``d_1``, sein Zeichen ``d_{1}``, «#» «Schicht 1»."""
        return replace(self, kurz=f"{self.kurz}_{i}", zeichen=mit_index(self.zeichen, i),
                       beschreibung=self.beschreibung.replace("#", f"{SCHICHT} {i}"))

    def als_dict(self) -> Dict[str, Any]:
        """
        Was die Maske von ihm braucht -- «#» steht dort für die Schicht ihrer
        Karte. ``bis`` mit seinem Satz und ``fest`` nur, wo es sie gibt.
        """
        beschreibung = self.beschreibung.replace("#", SCHICHT)
        angabe = {"feld": self.kurz, "zeichen": self.zeichen,
                  "beschriftung": self.beschriftung or beschreibung, "beschreibung": beschreibung,
                  "referenz": self.referenz, "schritt": self.schritt, "hinweis": self.hinweis}
        if self.bis is not None:
            angabe.update(bis=self.bis, bis_satz=self.bis_satz)
        if self.fest:
            angabe["fest"] = True
        return angabe


@dataclass(frozen=True)
class Gruppe:
    """Ein Kasten der Herleitung, eine Kachel der Maske."""

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
