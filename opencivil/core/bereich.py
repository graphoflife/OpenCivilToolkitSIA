"""
opencivil/core/bereich.py -- wo eine Zahl liegen muss.

VERANTWORTUNG:
Ein :class:`Bereich` sagt von einer Zahl, die jemand eingibt, wie sie heisst,
in welcher Einheit sie gemeint ist und wo sie liegen muss -- und mit welchem
Satz er sie abweist (:meth:`Bereich.grund`). Derselbe Bereich beschreibt das
Feld eines Eintrags (:func:`opencivil.projekt.lesen.bereich`), den Kennwert
eines Baustoffs, das Mass einer Vorlage
(:class:`opencivil.querschnitt.vorlagen.Mass`) und den Kennwert eines
Stabquerschnitts von Hand (:class:`opencivil.stabwerk.stabquerschnitt.Kennwert`).
Die Oberflaeche bekommt von jedem dieselbe Angabe (:meth:`Bereich.angabe`)
und weist eine Zahl schon am Feld mit dem Satz ab, der sonst beim Rechnen
kaeme.

Bis 2026-11-20 stand er bei den Feldern des Projekts, und die Vorlagen
prueften ihre Masse selbst: mit eigenen Saetzen, und die Oberflaeche mit
eigenen Mindestwerten -- 1 in der Querschnittsanalyse, 0 im Balkensystem.
"""

from __future__ import annotations

import dataclasses
import math
from typing import Any, Dict, Optional, Tuple

from opencivil.core.einheiten import Einheit


@dataclasses.dataclass(frozen=True)
class Bereich:
    """
    Wo eine Zahl liegen muss -- jede Grenze darf fehlen, ``ueber`` und
    ``unter`` schliessen die Grenze aus, ``ab`` und ``bis`` ein.
    """

    heisst: str
    """Wie die Zahl in der Meldung heisst -- wie an der Maske: «Dicke h»."""

    einheit: Optional[Einheit] = None
    ueber: Optional[float] = None
    ab: Optional[float] = None
    bis: Optional[float] = None
    unter: Optional[float] = None

    bis_feld: Optional[str] = None
    """
    Ein Feld desselben Eintrags, dessen Zahl diese nicht uebersteigen darf:
    α_min nicht ueber α_max. Die Regel steht so einmal, beim kleineren Feld.
    Die Maske weist sie an beiden Feldern ab
    (:func:`~opencivil.projekt.lesen.feldangaben`), die Pruefung vor dem
    Rechnen haelt eine Datei damit auf -- mit denselben Worten (:meth:`gegen`).
    """

    quer_zu: Optional[Tuple[str, float]] = None
    """
    Ein Feld desselben Eintrags mit einem Winkel in Grad, und um wie viel
    Grad dieser hier mindestens von ihm abweicht -- als Linie: 180° weiter
    ist dieselbe. Die zwei Richtungen einer Deckenplatte etwa liegen
    mindestens 5° auseinander, sonst trügen sie kaum anders als eine. Wie
    bei :attr:`bis_feld` steht die Regel einmal, an einem der beiden
    Felder, und die Maske weist sie an beiden ab (:meth:`quer`).
    """

    def grund(self, wert: float) -> str:
        """Was an ``wert`` nicht geht, als Satz mit Punkt -- leer, wenn er im Bereich liegt."""
        if ((self.ueber is None or wert > self.ueber) and (self.ab is None or wert >= self.ab)
                and (self.bis is None or wert <= self.bis)
                and (self.unter is None or wert < self.unter)):
            return ""
        return f"{self.heisst} {self.verlangt}, angegeben ist {self.zahl(wert)}."

    @property
    def verlangt(self) -> str:
        """Was die Grenzen verlangen: «muss grösser als null sein»."""
        grenzen = [(wort, g) for wort, g in (("grösser als", self.ueber), ("mindestens", self.ab),
                                             ("kleiner als", self.unter), ("höchstens", self.bis))
                   if g is not None]
        if grenzen == [("mindestens", 0.0)]:
            return "kann nicht negativ sein"
        return "muss " + " und ".join(
            f"{wort} {'null' if g == 0.0 else self.zahl(g)}" for wort, g in grenzen) + " sein"

    def gegen(self, anderer: Bereich) -> Tuple[str, str]:
        """
        Was :attr:`bis_feld` verlangt, an diesem Feld und am anderen
        (``anderer``): «α_min darf nicht grösser sein als α_max», «α_max darf
        nicht kleiner sein als α_min».
        """
        return (f"{self.heisst} darf nicht grösser sein als {anderer.heisst}",
                f"{anderer.heisst} darf nicht kleiner sein als {self.heisst}")

    def grund_gegen(self, wert: Optional[float], anderer: Bereich,
                    grenze: Optional[float]) -> str:
        """
        Was :attr:`bis_feld` verletzt -- die Zahl ueber der des anderen
        Feldes --, als Satz mit Punkt; leer, wenn nichts.
        """
        if wert is not None and grenze is not None and wert > grenze:
            return (f"{self.gegen(anderer)[0]}, angegeben sind "
                    f"{self.zahl(wert)} und {anderer.zahl(grenze)}.")
        return ""

    def quer(self, anderer: Bereich) -> Tuple[str, str]:
        """
        Was :attr:`quer_zu` verlangt, an diesem Feld und am anderen
        (``anderer``): «Richtung 2 muss um mindestens 5° von Richtung 1
        abweichen – 0° und 180° sind dieselbe Linie», und umgekehrt.
        """
        mindestens = self.zahl(self.quer_zu[1])
        return tuple(f"{a.heisst} muss um mindestens {mindestens} von {b.heisst} abweichen "
                     "– 0° und 180° sind dieselbe Linie" for a, b in ((self, anderer), (anderer, self)))

    def grund_quer(self, wert: Optional[float], anderer: Bereich, winkel: Optional[float]) -> str:
        """
        Was :attr:`quer_zu` verletzt -- ``wert`` als Linie zu nahe an
        ``winkel``, dem Winkel des anderen Feldes --, als Satz mit Punkt;
        leer, wenn nichts.
        """
        if wert is None or winkel is None:
            return ""
        abstand = math.fmod(abs(wert - winkel), 180.0)
        if min(abstand, 180.0 - abstand) >= self.quer_zu[1]:
            return ""
        return f"{self.quer(anderer)[0]}; angegeben sind {self.zahl(wert)} und {anderer.zahl(winkel)}."

    def zahl(self, wert: float) -> str:
        """Eine Zahl mit der Einheit: «300 mm», «30°», «0.9»."""
        if self.einheit is None or self.einheit.name in ("", "-"):
            return f"{wert:g}"
        return f"{wert:g}{'' if self.einheit.klebt else ' '}{self.einheit.beschriftung}"

    def angabe(self) -> Dict[str, Any]:
        """
        Was die Oberflaeche von ihm wissen muss -- die Einheit, ob sie an der
        Zahl klebt («30°»), und, hat er Grenzen, die Grenzen mit dem Satz, den
        eine verletzte sagt.
        """
        angabe: Dict[str, Any] = {}
        if self.einheit is not None and self.einheit.name not in ("", "-"):
            angabe["einheit"] = self.einheit.beschriftung
            if self.einheit.klebt:
                angabe["klebt"] = True
        grenzen = {grenze: getattr(self, grenze) for grenze in ("ueber", "ab", "bis", "unter")
                   if getattr(self, grenze) is not None}
        if grenzen:
            angabe.update(grenzen, heisst=self.heisst, verlangt=self.verlangt)
        return angabe
