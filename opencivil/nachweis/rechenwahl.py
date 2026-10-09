"""
opencivil/nachweis/rechenwahl.py -- womit ein Kapitel rechnet.

VERANTWORTUNG:
Was ein Nachweis-Kapitel waehlt -- die Kriechzahl, den Wertesatz und die
Rechenart -- und die eine Stelle, die daraus die Werkstoffgesetze und den
Querschnittsloeser baut. Die Kapitel der Platte und die
Spannung-Dehnung-Analyse fragen hier, keines baut seine Gesetze selbst.

DIE RECHENARTEN:
* **Handrechnung Block 0.85·x** -- im Loeser derselbe Querschnitt wie in der
  Resistenzlinie aus Handrechnung: der Spannungsblock, die Bewehrung nur auf
  Zug, je Seite zu einer Lage im Schwerpunkt zusammengefasst, und der Beton
  auch dort gezaehlt, wo der Stahl liegt.
* **Block 0.85·x genau** -- derselbe Spannungsblock, ueber die Hoehe
  integriert, jede Faser mit ihrer mittleren Spannung. Die gedrueckte
  Bewehrung wirkt mit und verdraengt den Beton an ihrer Stelle.
* **Parabel** -- die Parabel-Rechteck-Beziehung, ihr Anstieg mit dem
  wirksamen Modul ``E_cm/(1+phi)``, ``k_sigma`` nie unter 1.
* **elastisch** -- nur fuer die Stahlspannungen: der Beton linear mit
  ``E_cm/(1+phi)``, hoechstens ``f_c``. So rechneten sie bis 2026-10-09 fest.

Die Kriechzahl wirkt nur bei Parabel und elastisch: an den anderen Gesetzen
haengt kein Modul. Der Wertesatz bestimmt, wo die Plateaus liegen
(:class:`Werkstoffsatz`), und wie ein Widerstand heisst -- ``R_d`` oder
``R_k``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Sequence

from opencivil.core.berechnung import Eingabebezug, Eingaben
from opencivil.core.latex import angabe
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.nachweis.querschnittsloeser import (
    Querschnittsloeser, Stahllage, Werkstoffsatz, beton_elastisch,
    beton_nichtlinear, lagen_je_seite, stahl_bilinear, stahl_nur_zug,
    wirksamer_modul,
)
from opencivil.querschnitt.werkstoffgesetz import (
    BLOCKANTEIL, K_SIGMA_LATEX, Betongesetz, Spannungsblock, k_sigma,
)

Gesetz = Callable[[float], float]


class Rechenart(str, Enum):
    """Wie der Querschnitt gerechnet wird -- siehe Dateikopf."""

    HANDRECHNUNG = "handrechnung"
    BLOCK = "block"
    PARABEL = "parabel"
    ELASTISCH = "elastisch"

    @property
    def beschriftung(self) -> str:
        return {
            Rechenart.HANDRECHNUNG: f"Handrechnung Block {BLOCKANTEIL}·x",
            Rechenart.BLOCK: f"Block {BLOCKANTEIL}·x genau",
            Rechenart.PARABEL: "Parabel",
            Rechenart.ELASTISCH: "elastisch",
        }[self]

    @property
    def kurz(self) -> str:
        """Fuer schmale Zeilen."""
        return {
            Rechenart.HANDRECHNUNG: f"Hand {BLOCKANTEIL}·x",
            Rechenart.BLOCK: "Block genau",
            Rechenart.PARABEL: "Parabel",
            Rechenart.ELASTISCH: "elastisch",
        }[self]

    @property
    def latex(self) -> str:
        """Der Name als Formeltext -- fuer die Zeile «Rechenwahl» der Herleitung."""
        return {
            Rechenart.HANDRECHNUNG: rf"\text{{Handrechnung, Block }} {BLOCKANTEIL} \cdot x",
            Rechenart.BLOCK: rf"\text{{Block }} {BLOCKANTEIL} \cdot x \text{{ genau}}",
            Rechenart.PARABEL: r"\text{Parabel}",
            Rechenart.ELASTISCH: r"\text{elastisch}",
        }[self]

    @property
    def mit_kriechzahl(self) -> bool:
        """Ob ``phi`` etwas aendert -- nur, wo ein Gesetz am Modul haengt."""
        return self in (Rechenart.PARABEL, Rechenart.ELASTISCH)

    @property
    def mit_block(self) -> bool:
        """Ob der Beton als Spannungsblock rechnet."""
        return self in (Rechenart.HANDRECHNUNG, Rechenart.BLOCK)


#: Was die Tragsicherheit, das Knicken und die Analysen anbieten.
RECHENARTEN = (Rechenart.HANDRECHNUNG, Rechenart.BLOCK, Rechenart.PARABEL)

#: Die Stahlspannungen zusaetzlich elastisch.
SPANNUNGSARTEN = RECHENARTEN + (Rechenart.ELASTISCH,)


@dataclass(frozen=True)
class Rechenwahl:
    """Was ein Kapitel waehlt: Kriechzahl, Wertesatz, Rechenart."""

    kriechzahl: float = 0.0
    satz: Werkstoffsatz = Werkstoffsatz.BEMESSUNG
    art: Rechenart = Rechenart.HANDRECHNUNG

    @classmethod
    def aus(cls, kriechzahl: float, werkstoffsatz: str, rechenart: str) -> "Rechenwahl":
        """Aus den Feldern einer Beschreibung -- Zahl und zwei Namen."""
        return cls(kriechzahl=float(kriechzahl), satz=Werkstoffsatz(werkstoffsatz),
                   art=Rechenart(rechenart))

    @property
    def index(self) -> str:
        """``Rd`` oder ``Rk`` -- wie ein Widerstand dieser Wahl heisst."""
        return self.satz.widerstandsindex

    @property
    def beschriftung(self) -> str:
        """Fuer Legenden: «Parabel, φ = 2, Bemessung» -- phi nur, wo es wirkt."""
        teile = [self.art.beschriftung]
        if self.art.mit_kriechzahl:
            teile.append(f"φ = {self.kriechzahl:g}")
        return ", ".join(teile + [self.satz.kurz])


# ===========================================================================
# Die Gesetze zu einer Wahl
# ===========================================================================


@dataclass(frozen=True)
class Kennwerte:
    """Die Zahlen, aus denen die Gesetze entstehen -- SI, im Wertesatz der Wahl."""

    f_c: float
    """``f_cd`` oder ``f_ck``."""

    f_s: float
    """``f_yd`` oder ``f_yk`` -- dort beginnt das Plateau im Zug."""

    f_s_druck: float
    """Dasselbe im Druck."""

    E_cm: float
    E_s: float
    eps_c1d: float
    eps_c2d: float

    @classmethod
    def aus_eingaben(cls, e: Eingaben, satz: Werkstoffsatz) -> "Kennwerte":
        """Aus den Eingaben, die :func:`werkstoffbezuege` anmeldet."""
        return cls(f_c=e.g(satz.beton).si, f_s=e.g(satz.stahl).si,
                   f_s_druck=e.g(satz.stahl_druck).si, E_cm=e.g("E_cm").si,
                   E_s=e.g("E_s").si, eps_c1d=e.g("eps_c1d").si, eps_c2d=e.g("eps_c2d").si)


def werkstoffbezuege(satz: Werkstoffsatz, beton, stahl) -> List[Eingabebezug]:
    """
    Was die Gesetze einer Wahl brauchen -- unter den Kurznamen des Wertesatzes,
    ``f_cd`` oder ``f_ck`` usw. So steht in der Herleitung das Zeichen, mit dem
    gerechnet wird.
    """
    return [
        Eingabebezug(satz.beton, beton.id_von(satz.beton)),
        Eingabebezug("E_cm", beton.id_von("E_cm")),
        Eingabebezug("eps_c1d", beton.id_von("eps_c1d")),
        Eingabebezug("eps_c2d", beton.id_von("eps_c2d")),
        Eingabebezug(satz.stahl, stahl.id_von(satz.stahl)),
        Eingabebezug(satz.stahl_druck, stahl.id_von(satz.stahl_druck)),
        Eingabebezug("E_s", stahl.id_von("E_s")),
    ]


def bezuege_vereinen(*listen: Sequence[Eingabebezug]) -> List[Eingabebezug]:
    """
    Mehrere Listen von Eingaben zu einer -- jeder Name einmal.

    Derselbe Name mit derselben Wert-ID ist dieselbe Eingabe und wird einmal
    angemeldet. Derselbe Name mit einer anderen ID waere eine Verwechslung:
    die Rechnung laese dann die eine Zahl unter dem Namen der anderen.
    """
    vorhanden = {}
    heraus: List[Eingabebezug] = []
    for liste in listen:
        for b in liste:
            if b.name not in vorhanden:
                vorhanden[b.name] = b.wert_id
                heraus.append(b)
            elif vorhanden[b.name] != b.wert_id:
                raise ValueError(
                    f"Die Eingabe '{b.name}' steht einmal als {vorhanden[b.name]} "
                    f"und einmal als {b.wert_id} da.")
    return heraus


def betongesetz(wahl: Rechenwahl, *, f_c: float, E_cm: float, eps_c1d: float,
                 eps_c2d: float) -> Gesetz:
    """
    Der Beton im gerissenen Zustand -- je Rechenart. Die eine Stelle fuer
    die Parabel und den Block: der Loeser und die genaue Resistenzlinie
    bekommen ihren Beton beide hier.
    """
    if wahl.art is Rechenart.ELASTISCH:
        return beton_elastisch(E_c=wirksamer_modul(E_cm, wahl.kriechzahl), f_c=f_c)
    if wahl.art is Rechenart.PARABEL:
        return beton_nichtlinear(f_cd=f_c, E_c=wirksamer_modul(E_cm, wahl.kriechzahl),
                                 eps_c1d=eps_c1d, eps_c2d=eps_c2d)
    return Spannungsblock(f_cd=f_c, eps_c2d=eps_c2d)


def stahlgesetz(wahl: Rechenwahl, w: Kennwerte, *, eps_ud: float) -> Gesetz:
    """Der Stahl -- in der Handrechnung nur auf Zug."""
    if wahl.art is Rechenart.HANDRECHNUNG:
        return stahl_nur_zug(E_s=w.E_s, f_sd=w.f_s, eps_ud=eps_ud)
    return stahl_bilinear(E_s=w.E_s, f_sd=w.f_s, eps_ud=eps_ud, f_sd_druck=w.f_s_druck)


@dataclass(frozen=True)
class Gesetze:
    """Was zu einer Wahl gehoert -- Gesetze, Lagen, und wie die Fasern rechnen."""

    wahl: Rechenwahl
    beton: Gesetz
    stahl: Gesetz

    @property
    def gemittelt(self) -> bool:
        """Der Block springt: ueber jede Faser gemittelt, sonst springt N mit."""
        return self.wahl.art.mit_block

    @property
    def verdraengt(self) -> bool:
        """Die Handrechnung zaehlt den Beton auch, wo der Stahl liegt."""
        return self.wahl.art is not Rechenart.HANDRECHNUNG

    def lagen(self, lagen: Sequence[Stahllage], h: float) -> List[Stahllage]:
        """Die Lagen, mit denen gerechnet wird -- in der Handrechnung je Seite eine."""
        if self.wahl.art is Rechenart.HANDRECHNUNG:
            return lagen_je_seite(lagen, h)
        return list(lagen)

    def loeser(self, *, h: float, b: float, lagen: Sequence[Stahllage],
               beton: Gesetz = None, **fenster) -> Querschnittsloeser:
        """
        Der Loeser zu dieser Wahl. ``fenster`` sind die Grenzen der Suche
        (``eps_druck``, ``eps_zug``, ``grenzen``) -- die bringt jeder Nutzer
        selbst mit. ``beton`` ersetzt das Betongesetz, etwa durch den
        ungerissenen Zustand; alles andere bleibt.
        """
        return Querschnittsloeser(
            h=h, b=b, lagen=self.lagen(lagen, h), beton=beton or self.beton,
            stahl=self.stahl, gemittelt=self.gemittelt and beton is None,
            verdraengt=self.verdraengt, **fenster)


def protokoll_rechenwahl(p: Protokoll, wahl: Rechenwahl, basis: str, *,
                         titel: str = "Rechenwahl") -> Wert:
    """
    Womit das Kapitel rechnet, in einer Zeile: phi (nur wo es wirkt), Werte,
    Rechenart. Zurueck kommt phi als Wert -- fuer die Formeln danach.
    """
    phi = Zwischenwerte(basis).zahl("phi", r"\varphi", wahl.kriechzahl, stellen=2)
    satz = wahl.satz
    teile = ([angabe(phi)] if wahl.art.mit_kriechzahl else []) + [
        rf"\text{{{satz.beschriftung}}}\ {satz.beton_zeichen},\ {satz.stahl_zeichen}",
        wahl.art.latex]
    p.gleichung(r" \qquad ".join(teile), titel=titel)
    return phi


def protokoll_gesetze(p: Protokoll, wahl: Rechenwahl, e: Eingaben, basis: str, *,
                      titel: str) -> None:
    """
    Die Werkstoffgesetze der Wahl, mit den Zeichen ihres Wertesatzes.

    Der wirksame Modul steht nicht hier: wo er gebraucht wird, schreibt ihn
    das Kapitel an der Stelle, an der er erklaert wird
    (:func:`~opencivil.nachweis.querschnittsloeser.protokoll_wirksamer_modul`).
    """
    satz = wahl.satz
    f_c, f_s = e[satz.beton], e[satz.stahl]
    if wahl.art is Rechenart.ELASTISCH:
        p.gleichung(
            rf"\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ {f_s.symbol}\right]"
            rf" \quad {angabe(f_s)} \qquad "
            rf"\sigma_c = \max\left[E_{{c,eff}} \cdot \varepsilon_c;\ -{f_c.symbol}\right]"
            rf" \quad {angabe(f_c)}",
            titel=titel)
        return
    if wahl.art is Rechenart.HANDRECHNUNG:
        p.erklaerung(
            "Mit der Handrechnung rechnet der Querschnitt wie die Resistenzlinie "
            "aus Handrechnung: der Beton als Spannungsblock, die gedrückte "
            "Bewehrung weggelassen, die Bewehrung jeder Seite zu einer Lage in "
            "ihrem Schwerpunkt zusammengefasst, und der Beton auch dort gezählt, "
            "wo der Stahl liegt.")
    protokoll_betongesetz(p, wahl, f_c, e["E_cm"], basis, titel=titel)
    if wahl.art is Rechenart.HANDRECHNUNG:
        p.ansatz(
            r"\sigma_s = \begin{cases} \min\left(E_s \cdot \varepsilon_s;\ "
            + f_s.symbol + r"\right) & \varepsilon_s > 0 \\[1ex]"
            r" 0 & \varepsilon_s \le 0 \quad (\text{gedrückt: weggelassen})"
            r" \end{cases}",
            titel=f"{titel}: Stahl, nur auf Zug")
    else:
        p.gleichung(
            rf"\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ {f_s.symbol}\right]"
            rf" \quad {angabe(f_s)}", titel=f"{titel}: Stahl")


def protokoll_betongesetz(p: Protokoll, wahl: Rechenwahl, f_c: Wert, E_cm: Wert, basis: str,
                          *, titel: str) -> None:
    """
    Der Beton einer Wahl mit Block oder Parabel -- bei der Parabel samt ihrem
    Beiwert aus dem wirksamen Modul ``E_cm/(1+phi)``. ``f_c`` ist die
    Festigkeit des Wertesatzes, ``f_cd`` oder ``f_ck``.
    """
    if wahl.art is Rechenart.PARABEL:
        werte = Zwischenwerte(basis)
        E_c_eff = werte.spannung("E_c_eff", "E_{c,eff}",
                                 wirksamer_modul(E_cm.groesse.si, wahl.kriechzahl))
        p.formel(werte.zahl("k_sigma", r"k_{\sigma}", k_sigma(E_c_eff.groesse.si, f_c.groesse.si),
                            stellen=2),
                 K_SIGMA_LATEX, {"E_c": E_c_eff, "f_c": f_c},
                 titel="Beiwert der Parabel, mit dem wirksamen Modul")
        p.ansatz(Betongesetz(0.0, 1.0, 1.0, 0.0).latex(f_c.symbol),
                 titel=f"{titel}: Beton, Parabel-Rechteck", referenz="SIA 262:2025, 4.2.1.6")
    else:
        p.ansatz(Spannungsblock(0.0, 1.0).latex(f_c.symbol),
                 titel=f"{titel}: Beton, Spannungsblock {BLOCKANTEIL}·x")


def gesetze(wahl: Rechenwahl, w: Kennwerte, *, eps_ud: float = 0.045) -> Gesetze:
    """
    Die Gesetze zu einer Wahl. ``eps_ud`` bringt der Nutzer mit: die
    Stahlspannungen rechnen bis heute mit 4.5 %, das Knicken und die Analysen
    mit dem Wert der Stahlsorte.
    """
    return Gesetze(wahl=wahl, beton=betongesetz(wahl, f_c=w.f_c, E_cm=w.E_cm,
                                                eps_c1d=w.eps_c1d, eps_c2d=w.eps_c2d),
                   stahl=stahlgesetz(wahl, w, eps_ud=eps_ud))
