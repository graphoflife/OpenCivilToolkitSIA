"""
opencivil/core/formelbaum.py -- die Vorlage einer Formel als Rechenbaum.

VERANTWORTUNG:
Liest die Vorlage einer Formelzeile -- LaTeX mit ``@name``-Platzhaltern --
als Baum, setzt darin fuer einen Platzhalter eine andere Formel ein, kuerzt,
setzt den Baum wieder als LaTeX, mit Symbolen und mit Zahlen, und rechnet
ihn nach. Daraus baut die Kurzform eines Nachweises aus mehreren Zeilen eine
(:mod:`opencivil.core.kurzform`)::

    x    = \\frac{A_s \\cdot f_yd}{0.85 \\cdot b \\cdot f_cd}
    M_Rd = A_s \\cdot f_yd \\cdot (d - \\frac{0.85 \\cdot x}{2})
    ->     A_s \\cdot f_yd \\cdot (d - \\frac{A_s \\cdot f_yd}{2 \\cdot b \\cdot f_cd})

Gelesen wird die Teilmenge von LaTeX, in der die Formeln dieses Werkzeugs
stehen: ``+ - \\cdot \\times /``, Nebeneinander als Produkt, ``\\frac``,
``\\sqrt``, Klammern, Hochzahlen mit fester Zahl, ``\\pi``, ``\\min``,
``\\max``, Betraege und die Winkelfunktionen. Was darueber hinausgeht -- eine
Zahl mit Einheit, ``\\text``, ``\\sum``, ein Winkel in Grad -- wirft
:class:`Unlesbar`, und die Formel bleibt, wie sie geschrieben ist. Die
Kurzform rechnet jede Umformung nach; ein falsch gelesener Baum gibt darum
nie eine falsche Formel, nur keine kuerzere.

Gekuerzt wird wenig, und nur, was dasteht: gleiche Faktoren in Zaehler und
Nenner, Faktoren eins, Summanden null. Zahlen werden nicht verrechnet -- die
0.85 des Spannungsblocks soll man wiedererkennen, solange sie dasteht.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field, replace
from fractions import Fraction
from typing import Callable, Dict, List, Mapping, Optional, Tuple, Union

from opencivil.core.einheiten import Einheit
from opencivil.core.latex import (
    PLATZHALTER, Formelzeile, platzhalter_symbol, platzhalter_zahl,
)
from opencivil.core.wert import Wert


class Unlesbar(Exception):
    """Die Vorlage geht ueber das hinaus, was der Baum lesen kann."""


# ===========================================================================
# Knoten
# ===========================================================================


@dataclass(frozen=True)
class Zahl:
    """Eine Zahl, die in der Vorlage steht -- so geschrieben, wie sie dasteht."""

    wert: float
    text: str = field(default="", compare=False)


@dataclass(frozen=True)
class Blatt:
    """
    Ein Platzhalter mit seinem Wert. ``empirisch``: die Einheit, in der er
    in eine empirische Formel als blanke Zahl eingeht -- in ein solches Blatt
    wird nie eingesetzt, die Formel dahinter rechnet in SI.
    """

    kennung: str
    wert: Wert = field(compare=False)
    empirisch: Optional[Einheit] = None


@dataclass(frozen=True)
class Produkt:
    """Faktoren mit ihrer Hochzahl -- ein Nenner hat eine negative."""

    faktoren: Tuple[Tuple["Ausdruck", Fraction], ...]
    vorzeichen: int = 1


@dataclass(frozen=True)
class Summe:
    terme: Tuple["Ausdruck", ...]


@dataclass(frozen=True)
class Funktion:
    """``min``, ``max``, ``abs`` oder eine Winkelfunktion (:data:`WINKEL`)."""

    name: str
    argumente: Tuple["Ausdruck", ...]


Ausdruck = Union[Zahl, Blatt, Produkt, Summe, Funktion]

#: Die Winkelfunktionen, wie LaTeX sie schreibt -- mit ihrer Rechnung.
WINKEL: Dict[str, Callable[[float], float]] = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "cot": lambda x: 1.0 / math.tan(x), "arctan": math.atan,
}
_FUNKTIONEN: Dict[str, Callable[..., float]] = {
    "min": min, "max": max, "abs": abs, **WINKEL}

EINS = Zahl(1.0, "1")


def negiert(a: Ausdruck) -> Ausdruck:
    if isinstance(a, Produkt):
        return replace(a, vorzeichen=-a.vorzeichen)
    return Produkt(((a, Fraction(1)),), -1)


# ===========================================================================
# Lesen
# ===========================================================================

#: Zwischenraeume -- sie tragen nichts zur Rechnung bei.
_ABSTAENDE = {",", ";", ":", "!", " ", "quad", "qquad"}
_BEFEHL = re.compile(r"\\([A-Za-z]+|.)")
_ZAHL = re.compile(r"\d+(?:\.\d+)?")
_ZEICHEN = set("{}()[]|+-^;,/")
#: Was ein Faktor sein kann, der ohne Rechenzeichen folgt: ``2 \\cos x``.
_FAKTORBEFEHLE = {"frac", "tfrac", "dfrac", "sqrt", "left", "pi", "min", "max",
                  *WINKEL}

Teil = Tuple[str, str]


def _zerlegen(vorlage: str) -> List[Teil]:
    """Die Vorlage in ``(art, text)``: platz, zahl, befehl oder zeichen."""
    teile: List[Teil] = []
    i = 0
    while i < len(vorlage):
        zeichen = vorlage[i]
        if zeichen.isspace():
            i += 1
        elif zeichen == "@":
            treffer = PLATZHALTER.match(vorlage, i)
            if treffer is None:
                raise Unlesbar(f"Ein @ ohne Namen an Stelle {i}.")
            teile.append(("platz", treffer.group(1) or treffer.group(2)))
            i = treffer.end()
        elif zeichen.isdigit():
            treffer = _ZAHL.match(vorlage, i)
            teile.append(("zahl", treffer.group(0)))
            i = treffer.end()
        elif zeichen == "\\":
            treffer = _BEFEHL.match(vorlage, i)
            if treffer is None:
                raise Unlesbar("Ein Backslash am Ende.")
            i = treffer.end()
            if treffer.group(1) not in _ABSTAENDE:
                teile.append(("befehl", treffer.group(1)))
        elif zeichen in _ZEICHEN:
            teile.append(("zeichen", zeichen))
            i += 1
        else:
            raise Unlesbar(f"Das Zeichen {zeichen!r} liest der Formelbaum nicht.")
    return teile


_ZU = {"(": ")", "[": "]", "|": "|"}


class _Leser:
    """Rekursiver Abstieg: Summe, Produkt, Potenz, Einheit."""

    def __init__(self, teile: List[Teil], eingaben: Mapping[str, Wert],
                 empirisch: Mapping[str, Einheit]) -> None:
        self.teile = teile
        self.i = 0
        self.eingaben = eingaben
        self.empirisch = empirisch

    def schau(self) -> Teil:
        return self.teile[self.i] if self.i < len(self.teile) else ("ende", "")

    def nimm(self) -> Teil:
        teil = self.schau()
        self.i += 1
        return teil

    def erwarte(self, art: str, text: str) -> None:
        teil = self.nimm()
        if teil != (art, text):
            raise Unlesbar(f"Erwartet {text!r}, steht {teil[1]!r}.")

    def summe(self) -> Ausdruck:
        terme = [self.produkt()]
        while self.schau() in (("zeichen", "+"), ("zeichen", "-")):
            plus = self.nimm()[1] == "+"
            term = self.produkt()
            terme.append(term if plus else negiert(term))
        return terme[0] if len(terme) == 1 else Summe(tuple(terme))

    def produkt(self) -> Ausdruck:
        faktoren = [(self.potenz(), Fraction(1))]
        while True:
            art, text = self.schau()
            if (art, text) in (("befehl", "cdot"), ("befehl", "times")):
                self.nimm()
                faktoren.append((self.potenz(), Fraction(1)))
            elif (art, text) == ("zeichen", "/"):
                self.nimm()
                faktoren.append((self.potenz(), Fraction(-1)))
            elif (art in ("platz", "zahl") or (art, text) == ("zeichen", "(")
                  or (art == "befehl" and text in _FAKTORBEFEHLE)):
                faktoren.append((self.potenz(), Fraction(1)))
            else:
                break
        return faktoren[0][0] if len(faktoren) == 1 else Produkt(tuple(faktoren))

    def potenz(self) -> Ausdruck:
        basis = self.einheit()
        if self.schau() != ("zeichen", "^"):
            return basis
        self.nimm()
        if self.schau() == ("zeichen", "{"):
            self.nimm()
            hoch = self.summe()
            self.erwarte("zeichen", "}")
        else:
            art, text = self.nimm()
            if art != "zahl" or len(text) != 1:
                raise Unlesbar(f"Hochzahl {text!r} ohne Klammer.")
            hoch = Zahl(float(text), text)
        return Produkt(((basis, _bruch(hoch)),))

    def einheit(self) -> Ausdruck:
        art, text = self.nimm()
        if art == "platz":
            if text not in self.eingaben:
                raise Unlesbar(f"Zum Platzhalter {text} fehlt die Eingabe.")
            wert = self.eingaben[text]
            return Blatt(wert.id, wert, self.empirisch.get(text))
        if art == "zahl":
            return Zahl(float(text), text)
        if art == "zeichen":
            if text == "-":
                return negiert(self.potenz())
            if text == "+":
                return self.potenz()
            if text in ("{", "(", "["):
                inhalt = self.summe()
                self.erwarte("zeichen", "}" if text == "{" else _ZU[text])
                return inhalt
            if text == "|":
                inhalt = self.summe()
                self.erwarte("zeichen", "|")
                return Funktion("abs", (inhalt,))
        if art == "befehl":
            if text in ("frac", "tfrac", "dfrac"):
                oben = self.gruppe()
                unten = self.gruppe()
                return Produkt(((oben, Fraction(1)), (unten, Fraction(-1))))
            if text == "sqrt":
                grad = Fraction(2)
                if self.schau() == ("zeichen", "["):
                    self.nimm()
                    grad = _bruch(self.summe())
                    self.erwarte("zeichen", "]")
                return Produkt(((self.gruppe(), 1 / grad),))
            if text == "left":
                return self.links()
            if text == "pi":
                return Zahl(math.pi, r"\pi")
            if text in ("min", "max"):
                return Funktion(text, self.argumente())
            if text in WINKEL:
                return Funktion(text, (self.potenz(),))
        raise Unlesbar(f"{text!r} liest der Formelbaum nicht.")

    def gruppe(self) -> Ausdruck:
        """Das Argument von ``\\frac`` oder ``\\sqrt``: eine ``{...}``-Gruppe."""
        if self.schau() != ("zeichen", "{"):
            return self.einheit()
        self.nimm()
        inhalt = self.summe()
        self.erwarte("zeichen", "}")
        return inhalt

    def links(self) -> Ausdruck:
        """``\\left( ... \\right)``, mit ``[`` ebenso; ``|`` ist ein Betrag."""
        art, auf = self.nimm()
        if art != "zeichen" or auf not in _ZU:
            raise Unlesbar(f"\\left{auf} liest der Formelbaum nicht.")
        inhalt = self.summe()
        self.erwarte("befehl", "right")
        self.erwarte("zeichen", _ZU[auf])
        return Funktion("abs", (inhalt,)) if auf == "|" else inhalt

    def argumente(self) -> Tuple[Ausdruck, ...]:
        """Die Argumente von ``\\min`` und ``\\max``, durch ``;`` oder ``,`` getrennt."""
        links = self.schau() == ("befehl", "left")
        if links:
            self.nimm()
        art, auf = self.nimm()
        if art != "zeichen" or auf not in ("(", "["):
            raise Unlesbar("\\min und \\max brauchen eine Klammer.")
        argumente = [self.summe()]
        while self.schau() in (("zeichen", ";"), ("zeichen", ",")):
            self.nimm()
            argumente.append(self.summe())
        if links:
            self.erwarte("befehl", "right")
        self.erwarte("zeichen", _ZU[auf])
        return tuple(argumente)


def _bruch(hoch: Ausdruck) -> Fraction:
    """Eine Hochzahl als Bruch -- sie muss eine feste Zahl sein."""
    if blaetter(hoch):
        raise Unlesbar("Eine Hochzahl mit Platzhalter liest der Formelbaum nicht.")
    zahl = rechnen(hoch)
    bruch = Fraction(zahl).limit_denominator(1000)
    if not math.isclose(float(bruch), zahl, rel_tol=1e-12, abs_tol=1e-12):
        raise Unlesbar(f"Die Hochzahl {zahl} ist kein einfacher Bruch.")
    return bruch


def lesen(zeile: Formelzeile) -> Ausdruck:
    """Die Vorlage einer Formelzeile als gekuerzter Baum (:func:`normal`)."""
    if zeile.vorlage is None:
        raise Unlesbar("Die Zeile hat keine Vorlage.")
    leser = _Leser(_zerlegen(zeile.vorlage), dict(zeile.eingaben), dict(zeile.empirisch))
    baum = leser.summe()
    if leser.schau()[0] != "ende":
        raise Unlesbar(f"Nach der Formel steht noch {leser.schau()[1]!r}.")
    return normal(baum)


# ===========================================================================
# Umformen
# ===========================================================================


def normal(a: Ausdruck) -> Ausdruck:
    """
    Flach und gekuerzt: ein Produkt im Produkt geht in diesem auf, eine
    Summe in der Summe ebenso; gleiche Faktoren zaehlen ihre Hochzahlen
    zusammen, und was danach eins ist (oder null in einer Summe), entfaellt.
    """
    if isinstance(a, Produkt):
        return _produkt(a)
    if isinstance(a, Summe):
        terme: List[Ausdruck] = []
        for term in map(normal, a.terme):
            terme.extend(term.terme if isinstance(term, Summe) else [term])
        terme = [t for t in terme if t != Zahl(0.0)]
        if not terme:
            return Zahl(0.0, "0")
        return terme[0] if len(terme) == 1 else Summe(tuple(terme))
    if isinstance(a, Funktion):
        return Funktion(a.name, tuple(map(normal, a.argumente)))
    return a


def _produkt(a: Produkt) -> Ausdruck:
    vorzeichen = a.vorzeichen
    flach: List[Tuple[Ausdruck, Fraction]] = []
    for faktor, hoch in a.faktoren:
        faktor = normal(faktor)
        # Nur mit Hochzahl eins aufloesen: aus (x/y)^2 soll nicht x^2/y^2 werden.
        if isinstance(faktor, Produkt) and abs(hoch) == 1:
            vorzeichen *= faktor.vorzeichen
            flach.extend((f, h * hoch) for f, h in faktor.faktoren)
        else:
            flach.append((faktor, hoch))

    gesammelt: List[List] = []
    for faktor, hoch in flach:
        if faktor == EINS:
            continue
        gleich = next((g for g in gesammelt if g[0] == faktor), None)
        if gleich is None:
            gesammelt.append([faktor, hoch])
        else:
            gleich[1] += hoch
    faktoren = tuple((f, h) for f, h in gesammelt if h != 0)

    if not faktoren:
        return EINS if vorzeichen > 0 else Produkt(((EINS, Fraction(1)),), -1)
    if vorzeichen > 0 and len(faktoren) == 1 and faktoren[0][1] == 1:
        return faktoren[0][0]
    return Produkt(faktoren, vorzeichen)


def einsetzen(a: Ausdruck, kennung: str, teil: Ausdruck) -> Ausdruck:
    """``a`` mit ``teil`` an jedem nicht empirischen Blatt ``kennung``, gekuerzt."""

    def ersetzt(x: Ausdruck) -> Ausdruck:
        if isinstance(x, Blatt):
            return teil if x.kennung == kennung and x.empirisch is None else x
        if isinstance(x, Produkt):
            return Produkt(tuple((ersetzt(f), h) for f, h in x.faktoren), x.vorzeichen)
        if isinstance(x, Summe):
            return Summe(tuple(map(ersetzt, x.terme)))
        if isinstance(x, Funktion):
            return Funktion(x.name, tuple(map(ersetzt, x.argumente)))
        return x

    return normal(ersetzt(a))


def _kinder(a: Ausdruck) -> Tuple[Ausdruck, ...]:
    if isinstance(a, Produkt):
        return tuple(f for f, _ in a.faktoren)
    if isinstance(a, Summe):
        return a.terme
    if isinstance(a, Funktion):
        return a.argumente
    return ()


def blaetter(a: Ausdruck) -> List[Blatt]:
    """Die Blaetter in der Reihenfolge, in der sie dastehen -- jedes einmal."""
    if isinstance(a, Blatt):
        return [a]
    heraus: List[Blatt] = []
    for kind in _kinder(a):
        heraus.extend(b for b in blaetter(kind) if b not in heraus)
    return heraus


def empirische(a: Ausdruck) -> List[Tuple[str, Einheit]]:
    """``(Symbol, Einheit)`` je empirischem Blatt -- fuer den Einheitenhinweis."""
    return [(b.wert.symbol, b.empirisch) for b in blaetter(a) if b.empirisch is not None]


def rechnen(a: Ausdruck) -> float:
    """
    Der Wert des Baums in SI; ein empirisches Blatt in seiner Einheit. Eine
    negative Zahl unter einer Wurzel gibt ``nan`` -- dann stimmt nichts mehr.
    """
    if isinstance(a, Zahl):
        return a.wert
    if isinstance(a, Blatt):
        si = a.wert.groesse.si
        return si if a.empirisch is None else si / a.empirisch.faktor
    if isinstance(a, Summe):
        return math.fsum(map(rechnen, a.terme))
    if isinstance(a, Funktion):
        try:
            return float(_FUNKTIONEN[a.name](*map(rechnen, a.argumente)))
        except (ValueError, ZeroDivisionError):
            return math.nan
    ergebnis = float(a.vorzeichen)
    for faktor, hoch in a.faktoren:
        basis = rechnen(faktor)
        if (basis < 0 and hoch.denominator != 1) or (basis == 0 and hoch < 0):
            return math.nan
        ergebnis *= basis ** float(hoch)
    return ergebnis


# ===========================================================================
# Setzen
# ===========================================================================

#: Wie ein Blatt dasteht: ``(blatt, vorn, hoch) -> LaTeX`` -- ``vorn``, wenn
#: kein Rechenzeichen davorsteht, ``hoch``, wenn ein Exponent folgt.
Blattsatz = Callable[[Blatt, bool, bool], str]


def symbolisch(a: Ausdruck) -> str:
    return _setzen(a, lambda b, vorn, hoch: platzhalter_symbol(b.wert, hoch))


def numerisch(a: Ausdruck) -> str:
    return _setzen(a, lambda b, vorn, hoch: platzhalter_zahl(
        b.wert, b.empirisch, hoch, not vorn))


def _klammer(text: str) -> str:
    return rf"\left({text}\right)"


def _setzen(a: Ausdruck, blatt: Blattsatz, vorn: bool = True, hoch: bool = False) -> str:
    if isinstance(a, Zahl):
        return a.text or f"{a.wert:g}"
    if isinstance(a, Blatt):
        return blatt(a, vorn, hoch)
    if isinstance(a, Summe):
        teile = [_setzen(a.terme[0], blatt, vorn)]
        for term in a.terme[1:]:
            minus = isinstance(term, Produkt) and term.vorzeichen < 0
            rest = negiert(term) if minus else term
            teile.append(("- " if minus else "+ ") + _setzen(rest, blatt, vorn=False))
        return " ".join(teile)
    if isinstance(a, Funktion):
        return _funktion(a, blatt)
    return _produkt_setzen(a, blatt, vorn)


def _funktion(a: Funktion, blatt: Blattsatz) -> str:
    if a.name == "abs":
        return rf"\left|{_setzen(a.argumente[0], blatt)}\right|"
    if a.name in ("min", "max"):
        inhalt = r";\ ".join(_setzen(x, blatt) for x in a.argumente)
        return rf"\{a.name}\left[{inhalt}\right]"
    x = a.argumente[0]
    if isinstance(x, (Blatt, Zahl)):
        return rf"\{a.name} {_setzen(x, blatt)}"
    return rf"\{a.name}{_klammer(_setzen(x, blatt))}"


def _produkt_setzen(a: Produkt, blatt: Blattsatz, vorn: bool) -> str:
    """Zahlen zuerst, ein Nenner als Bruch, ein Minus vorne."""

    def zahlen_zuerst(faktoren):
        return sorted(faktoren, key=lambda fh: not isinstance(fh[0], Zahl))

    oben = zahlen_zuerst((f, h) for f, h in a.faktoren if h > 0)
    unten = zahlen_zuerst((f, -h) for f, h in a.faktoren if h < 0)
    minus = "-" if a.vorzeichen < 0 else ""

    def reihe(faktoren, vorn: bool, allein: bool) -> str:
        if not faktoren:
            return "1"
        return r" \cdot ".join(
            _faktor(f, h, blatt, vorn=vorn and i == 0, allein=allein and len(faktoren) == 1)
            for i, (f, h) in enumerate(faktoren))

    if unten:
        return minus + rf"\frac{{{reihe(oben, True, True)}}}{{{reihe(unten, True, True)}}}"
    return minus + reihe(oben, vorn and not minus, False)


def _faktor(f: Ausdruck, hoch: Fraction, blatt: Blattsatz, *, vorn: bool, allein: bool) -> str:
    """Ein Faktor mit seiner (positiven) Hochzahl; ``allein`` im Zaehler oder Nenner."""
    if hoch == 1:
        text = _setzen(f, blatt, vorn)
        return _klammer(text) if isinstance(f, Summe) and not allein else text
    if hoch.numerator == 1:
        inhalt = _setzen(f, blatt)
        return (rf"\sqrt{{{inhalt}}}" if hoch.denominator == 2
                else rf"\sqrt[{hoch.denominator}]{{{inhalt}}}")
    basis = _setzen(f, blatt, hoch=True)
    if isinstance(f, (Summe, Produkt)) or (isinstance(f, Funktion) and f.name in WINKEL):
        basis = _klammer(basis)
    zahl = str(hoch.numerator) if hoch.denominator == 1 else f"{hoch.numerator}/{hoch.denominator}"
    return f"{basis}^{{{zahl}}}"
