"""
opencivil/gleichungen/ausdruck.py -- eine Zeile LaTeX: zerlegen, rechnen, setzen.

VERANTWORTUNG:
Liest die LaTeX-Teilmenge, die der Formeleditor (MathLive) schreibt, baut
daraus einen Syntaxbaum, rechnet ihn mit Einheiten aus und setzt ihn wieder als
Vorlage mit ``@name`` -- dieselbe Form, die jede Herleitung benutzt
(:meth:`Protokoll.formel`). Eine selbst geschriebene Gleichung steht so genau
da wie eine des Werkzeugs: Symbol, Formel, Zahlen, Ergebnis.

KEIN EVAL, KEIN ROHES LATEX:
Gerechnet wird ueber den Baum, nie ueber ``eval``. Angezeigt wird nie, was
der Benutzer geschrieben hat, sondern was der Baum daraus macht: KaTeX laeuft
mit ``trust: true``, und ein fremdes ``\\href`` kaeme so nie durch -- der Baum
kennt diesen Befehl nicht und lehnt die Zeile ab.

WAS VERSTANDEN WIRD:
Zahlen (``3.5``, ``3{,}5``), Variablen mit Index (``f_{cd}``, ``\\sigma_s``),
``+ - \\cdot \\times /``, implizites Mal (``2a``), ``\\frac``, ``^``,
``\\sqrt``, ``\\sqrt[n]``, Klammern, Betrag, Winkelfunktionen, ``\\ln \\log
\\exp \\min \\max``, ``\\pi``, Einheiten als ``\\mathrm{kN}``, Grad als
``^{\\circ}``. Nebeneinanderstehende Buchstaben sind ein Produkt (``ab`` ist
``a \\cdot b``) -- ein Name mit mehreren Zeichen braucht einen Index.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Tuple, Union

from opencivil.core.einheiten import (
    DIMENSIONSLOS, EINHEITSLOS, FLAECHE, GRAD, KG_PRO_M3, KN, KN_PRO_M,
    KN_PRO_M2, KNM, KNM_PRO_M, KRAFT, KRAFT_PRO_LAENGE, KRUEMMUNG, LAENGE,
    M, M2, MASSE, MM, MM2, MOMENT, MOMENT_PRO_LAENGE, N_PRO_MM2, PRO_M,
    PROMILLE, PROZENT, SPANNUNG, VOLUMEN, ZEIT, DICHTE, Dimension,
    DimensionsFehler, Einheit, EINHEITEN, Groesse, KG,
)


class AusdruckFehler(Exception):
    """Was an einer Zeile nicht stimmt -- als Satz fuer den Benutzer."""


# ===========================================================================
# Einheiten
# ===========================================================================

S = Einheit("s", ZEIT, 1.0)
MIN = Einheit("min", ZEIT, 60.0)
H = Einheit("h", ZEIT, 3600.0)
M3 = Einheit("m^3", VOLUMEN, 1.0)
KN_PRO_M3 = Einheit("kN/m^3", KRAFT / VOLUMEN, 1e3,
                    latex=r"\mathrm{kN}/\mathrm{m}^{3}")

#: Was in ``\mathrm{...}`` stehen darf. Nur einfache Namen -- zusammengesetzte
#: Einheiten entstehen im Ausdruck selbst: ``\mathrm{kN}/\mathrm{m}^{2}``.
EINHEITENNAMEN: Dict[str, Einheit] = {
    **{name: e for name, e in EINHEITEN.items()
       if name.isalpha() and name not in ("promille", "Grad")},
    "s": S, "min": MIN, "h": H,
}

#: Womit ein Ergebnis angezeigt wird, wenn die Zeile keine Einheit verlangt.
#: Je Dimension eine Einheit oder eine Staffel ``(Grenze in SI, klein, gross)``:
#: 0.265 m liest sich als 265 mm, 5 kN/m² nicht als 0.005 N/mm².
_VORZUG: Dict[Dimension, Union[Einheit, Tuple[float, Einheit, Einheit]]] = {
    DIMENSIONSLOS: EINHEITSLOS,
    LAENGE: (1.0, MM, M),
    FLAECHE: (0.01, MM2, M2),
    VOLUMEN: M3,
    KRAFT: KN,
    SPANNUNG: (1e6, KN_PRO_M2, N_PRO_MM2),
    MOMENT: KNM,
    KRAFT_PRO_LAENGE: KN_PRO_M,
    MOMENT_PRO_LAENGE: KNM_PRO_M,
    KRAFT / VOLUMEN: KN_PRO_M3,
    DICHTE: KG_PRO_M3,
    MASSE: KG,
    ZEIT: S,
    KRUEMMUNG: PRO_M,
}


def _si_einheit(dimension: Dimension) -> Einheit:
    """Eine Einheit aus m, kg, s -- wo es keine gebraeuchliche gibt."""
    teile = [("kg", dimension.masse), ("m", dimension.laenge), ("s", dimension.zeit)]
    oben = [(n, e) for n, e in teile if e > 0]
    unten = [(n, -e) for n, e in teile if e < 0]

    def gesetzt(liste) -> str:
        return r"\,".join(rf"\mathrm{{{n}}}" + ("" if e == 1 else f"^{{{e}}}")
                          for n, e in liste)

    def text(liste) -> str:
        return "·".join(n + ("" if e == 1 else f"^{e}") for n, e in liste)

    latex, beschriftung = gesetzt(oben) or "1", text(oben) or "1"
    if unten:
        latex += "/" + gesetzt(unten)
        beschriftung += "/" + text(unten)
    return Einheit(name=f"si:{dimension}", dimension=dimension, latex=latex,
                   beschriftung=beschriftung)


def anzeigeeinheit(groesse: Groesse, gewuenscht: Optional[Einheit] = None) -> Einheit:
    """Die Einheit, in der ein Ergebnis dasteht."""
    if gewuenscht is not None:
        if gewuenscht.dimension != groesse.dimension:
            raise AusdruckFehler(
                f"Einheit {gewuenscht.beschriftung} passt nicht zum Ergebnis "
                f"({_dimension_text(groesse.dimension)}).")
        return gewuenscht
    if groesse.anzeige.name in EINHEITEN or groesse.anzeige in EINHEITENNAMEN.values():
        return groesse.anzeige
    vorzug = _VORZUG.get(groesse.dimension)
    if isinstance(vorzug, tuple):
        grenze, klein, gross = vorzug
        return klein if 0 < abs(groesse.si) < grenze else gross
    return vorzug or _si_einheit(groesse.dimension)


def _dimension_text(dimension: Dimension) -> str:
    return _si_einheit(dimension).beschriftung or "1"


def einheit_aus_text(text: str) -> Optional[Einheit]:
    """
    Die gewuenschte Ergebniseinheit einer Zeile: ``kN/m^2``, ``N/mm2``, ``mm``.

    Leer heisst: keine Vorgabe. Eine unbekannte Einheit ist ein Fehler der
    Zeile, kein stilles Ignorieren.
    """
    text = text.strip().replace("²", "^2").replace("³", "^3").replace(" ", "")
    if not text:
        return None
    if text in ("°", "Grad"):
        return GRAD
    if text == "%":
        return PROZENT
    if text == "‰":
        return PROMILLE
    ergebnis: Optional[Einheit] = None
    for i, (zeichen, name, hoch) in enumerate(
            re.findall(r"([*/·]?)([A-Za-z]+)(?:\^?(-?\d+))?", text)):
        einheit = EINHEITENNAMEN.get(name)
        if einheit is None:
            raise AusdruckFehler(f"Einheit «{name}» unbekannt.")
        if hoch:
            einheit = einheit ** int(hoch)
        if ergebnis is None:
            ergebnis = einheit
        else:
            ergebnis = ergebnis / einheit if zeichen == "/" else ergebnis * einheit
    if ergebnis is None or not re.fullmatch(r"(?:[*/·]?[A-Za-z]+(?:\^?-?\d+)?)+", text):
        raise AusdruckFehler(f"Einheit «{text}» nicht lesbar.")
    return Einheit(name=text, dimension=ergebnis.dimension, faktor=ergebnis.faktor,
                   latex=ergebnis.latex)


# ===========================================================================
# Zerlegen
# ===========================================================================

@dataclass(frozen=True)
class Token:
    art: str
    """``zahl``, ``buchstabe``, ``befehl``, ``zeichen`` oder ``ende``."""

    text: str
    stelle: int


#: Abstaende -- sie tragen nichts zur Rechnung bei.
_LEER = {r"\,", r"\;", r"\:", r"\!", r"\ ", r"\quad", r"\qquad", r"\enspace",
         r"\thinspace", r"\medspace", r"\thickspace", r"\displaystyle"}

_GRIECHISCH = {
    rf"\{n}" for n in (
        "alpha beta gamma delta epsilon varepsilon zeta eta theta vartheta "
        "iota kappa lambda mu nu xi rho varrho sigma tau upsilon phi varphi "
        "chi psi omega Gamma Delta Theta Lambda Xi Pi Sigma Upsilon Phi Psi "
        "Omega").split()
}

_FUNKTIONEN = {r"\sin", r"\cos", r"\tan", r"\cot", r"\arcsin", r"\arccos",
               r"\arctan", r"\sinh", r"\cosh", r"\tanh", r"\ln", r"\log",
               r"\lg", r"\exp", r"\min", r"\max"}

_MAL = {r"\cdot", r"\times", "*"}
_ZUWEISUNG = {r"\coloneq", r"\coloneqq", r"\colonequals"}

_ZAHL = re.compile(r"\d+(?:(?:\.|\{,\})\d+)?|\.\d+")


def zerlegen(latex: str) -> List[Token]:
    """Die Zeile als Folge von Zeichen, Zahlen und Befehlen."""
    tokens: List[Token] = []
    i = 0
    while i < len(latex):
        zeichen = latex[i]
        if zeichen.isspace():
            i += 1
            continue
        if zeichen == "\\":
            treffer = re.match(r"\\([A-Za-z]+|.)", latex[i:])
            if treffer is None:
                raise AusdruckFehler("Zeile endet mit «\\».")
            befehl = "\\" + treffer.group(1)
            if befehl not in _LEER:
                tokens.append(Token("befehl", befehl, i))
            i += len(treffer.group(0))
            continue
        zahl = _ZAHL.match(latex, i)
        if zahl:
            tokens.append(Token("zahl", zahl.group(0).replace("{,}", "."), i))
            i = zahl.end()
            continue
        if zeichen.isalpha():
            tokens.append(Token("buchstabe", zeichen, i))
        elif zeichen == "°":
            tokens.append(Token("befehl", r"\degree", i))
        else:
            tokens.append(Token("zeichen", zeichen, i))
        i += 1
    tokens.append(Token("ende", "", len(latex)))
    return tokens


# ===========================================================================
# Syntaxbaum
# ===========================================================================

@dataclass(frozen=True)
class Zahl:
    wert: float
    text: str


@dataclass(frozen=True)
class Masseinheit:
    einheit: Einheit


@dataclass(frozen=True)
class Name:
    """Eine Variable. ``latex`` ist ihre gereinigte Schreibweise und ihr Schluessel."""

    latex: str


@dataclass(frozen=True)
class Operation:
    zeichen: str
    """``+``, ``-``, ``*`` oder ``/``."""

    links: "Knoten"
    rechts: "Knoten"


@dataclass(frozen=True)
class Potenz:
    basis: "Knoten"
    exponent: "Knoten"


@dataclass(frozen=True)
class Gegenzahl:
    inhalt: "Knoten"


@dataclass(frozen=True)
class Funktion:
    name: str
    argumente: Tuple["Knoten", ...]


@dataclass(frozen=True)
class Wurzel:
    inhalt: "Knoten"
    grad: Optional["Knoten"] = None


@dataclass(frozen=True)
class Betrag:
    inhalt: "Knoten"


@dataclass(frozen=True)
class Konstante:
    latex: str
    wert: float


Knoten = Union[Zahl, Masseinheit, Name, Operation, Potenz, Gegenzahl, Funktion,
               Wurzel, Betrag, Konstante]


# ===========================================================================
# Lesen
# ===========================================================================

class _Leser:
    """Rekursiver Abstieg ueber die Tokens einer Zeile."""

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.i = 0
        self.betraege = 0
        """Wie viele Betragsstriche offen sind -- dann schliesst ``|``, statt
        einen neuen Faktor zu beginnen."""

    # -- Zugriff ------------------------------------------------------------

    @property
    def jetzt(self) -> Token:
        return self.tokens[self.i]

    def nehmen(self) -> Token:
        token = self.tokens[self.i]
        self.i += 1
        return token

    def ist(self, *texte: str) -> bool:
        return self.jetzt.text in texte and self.jetzt.art in ("zeichen", "befehl")

    def erwarten(self, text: str) -> None:
        if not self.ist(text):
            raise AusdruckFehler(
                f"«{text}» erwartet, gefunden {self._beschreiben(self.jetzt)}.")
        self.nehmen()

    @staticmethod
    def _beschreiben(token: Token) -> str:
        return "Zeilenende" if token.art == "ende" else f"«{token.text}»"

    def _oeffnen(self) -> Optional[str]:
        """Eine oeffnende Klammer, auch ``\\left(`` -- gibt die schliessende zurueck."""
        if self.ist(r"\left"):
            self.nehmen()
        for auf, zu in (("(", ")"), ("[", "]"), (r"\lbrack", r"\rbrack")):
            if self.ist(auf):
                self.nehmen()
                return zu
        return None

    def _schliessen(self, zu: str) -> None:
        if self.ist(r"\right"):
            self.nehmen()
        self.erwarten(zu)

    # -- Grammatik ----------------------------------------------------------

    def ausdruck(self) -> Knoten:
        """Summe: ``summand (± summand)*``."""
        knoten = self.summand()
        while self.ist("+", "-"):
            zeichen = self.nehmen().text
            knoten = Operation(zeichen, knoten, self.summand())
        return knoten

    def summand(self) -> Knoten:
        """Produkt: ``faktor ((· | / | nichts) faktor)*``."""
        knoten = self.faktor()
        while True:
            if self.ist(*_MAL):
                self.nehmen()
                knoten = Operation("*", knoten, self.faktor())
            elif self.ist("/", r"\div"):
                self.nehmen()
                knoten = Operation("/", knoten, self.faktor())
            elif self._beginnt_faktor():
                knoten = Operation("*", knoten, self.faktor())
            else:
                return knoten

    def _beginnt_faktor(self) -> bool:
        token = self.jetzt
        if token.art in ("zahl", "buchstabe"):
            return True
        if token.art == "befehl":
            return (token.text in _GRIECHISCH or token.text in _FUNKTIONEN
                    or token.text in (r"\frac", r"\dfrac", r"\tfrac", r"\sqrt",
                                      r"\pi", r"\mathrm", r"\left", r"\lbrack"))
        return token.text in ("(", "[", "{") or (token.text == "|" and not self.betraege)

    def faktor(self) -> Knoten:
        if self.ist("-"):
            self.nehmen()
            return Gegenzahl(self.faktor())
        if self.ist("+"):
            self.nehmen()
            return self.faktor()
        return self.potenz()

    def potenz(self) -> Knoten:
        basis = self.primaer()
        while True:
            if self.ist("^"):
                self.nehmen()
                if self._grad():
                    basis = Operation("*", basis, Masseinheit(GRAD))
                    continue
                basis = Potenz(basis, self.hochzahl())
            elif self.ist(r"\degree", r"\circ"):
                self.nehmen()
                basis = Operation("*", basis, Masseinheit(GRAD))
            elif self.ist(r"\%"):
                self.nehmen()
                basis = Operation("*", basis, Masseinheit(PROZENT))
            else:
                return basis

    def _grad(self) -> bool:
        """``^{\\circ}`` oder ``^\\circ`` -- das Gradzeichen, kein Exponent."""
        if self.ist(r"\circ"):
            self.nehmen()
            return True
        if self.ist("{") and self.tokens[self.i + 1].text == r"\circ" \
                and self.tokens[self.i + 2].text == "}":
            self.i += 3
            return True
        return False

    def hochzahl(self) -> Knoten:
        """Nach ``^``: eine Gruppe ``{...}`` oder ein einzelnes Zeichen."""
        if self.ist("{"):
            return self.gruppe()
        token = self.nehmen()
        if token.art == "zahl" and len(token.text) > 1 and "." not in token.text:
            # ``x^23`` schreibt LaTeX als x hoch 2, gefolgt von 3.
            self.i -= 1
            self.tokens[self.i] = Token("zahl", token.text[1:], token.stelle + 1)
            return Zahl(float(token.text[0]), token.text[0])
        self.i -= 1
        return self.primaer()

    def gruppe(self) -> Knoten:
        self.erwarten("{")
        knoten = self.ausdruck()
        self.erwarten("}")
        return knoten

    def primaer(self) -> Knoten:
        token = self.jetzt
        if token.art == "zahl":
            self.nehmen()
            return Zahl(float(token.text), token.text)
        if token.art == "buchstabe" or token.text in _GRIECHISCH:
            return self.name()
        if token.art == "ende":
            raise AusdruckFehler("Ausdruck unvollständig.")
        text = token.text
        if text in (r"\frac", r"\dfrac", r"\tfrac"):
            self.nehmen()
            return Operation("/", self.gruppe(), self.gruppe())
        if text == r"\sqrt":
            self.nehmen()
            grad = None
            if self.ist("["):
                self.nehmen()
                grad = self.ausdruck()
                self.erwarten("]")
            return Wurzel(self.gruppe(), grad)
        if text == r"\pi":
            self.nehmen()
            return Konstante(r"\pi", math.pi)
        if text == r"\mathrm":
            return self.masseinheit()
        if text in _FUNKTIONEN:
            return self.funktion()
        if text == "{":
            return self.gruppe()
        if text == "|" or (text == r"\left" and self.tokens[self.i + 1].text == "|"):
            if text == r"\left":
                self.nehmen()
            self.nehmen()
            self.betraege += 1
            inhalt = self.ausdruck()
            self.betraege -= 1
            self._schliessen("|")
            return Betrag(inhalt)
        zu = self._oeffnen()
        if zu is not None:
            inhalt = self.ausdruck()
            self._schliessen(zu)
            return inhalt
        if text == r"\placeholder":
            raise AusdruckFehler("Leerstelle ausfüllen.")
        raise AusdruckFehler(f"{self._beschreiben(token)} hier nicht erlaubt.")

    def name(self) -> Name:
        """Buchstabe oder griechisches Zeichen, dahinter ein Index."""
        basis = self.nehmen().text
        latex = basis
        if self.ist("_"):
            self.nehmen()
            latex = f"{basis}_{{{self.index()}}}"
        return Name(latex)

    def index(self) -> str:
        """Der Index eines Namens -- gereinigt, nur Buchstaben, Ziffern, Komma."""
        if not self.ist("{"):
            token = self.nehmen()
            if token.art not in ("buchstabe", "zahl") and token.text not in _GRIECHISCH:
                raise AusdruckFehler(f"Index {self._beschreiben(token)} nicht erlaubt.")
            return token.text[0] if token.art == "zahl" else token.text
        self.nehmen()
        teile: List[str] = []
        while not self.ist("}"):
            token = self.nehmen()
            if token.art in ("buchstabe", "zahl") or token.text == ",":
                teile.append(token.text)
            elif token.text in _GRIECHISCH:
                teile.append(token.text + " ")
            elif token.art == "befehl" and token.text in (r"\mathrm", r"\text"):
                self.erwarten("{")
                while not self.ist("}"):
                    teil = self.nehmen()
                    if not (teil.text.isalnum() or teil.text == ","):
                        raise AusdruckFehler("Index nur aus Buchstaben und Ziffern.")
                    teile.append(teil.text)
                self.nehmen()
            else:
                raise AusdruckFehler(f"Index {self._beschreiben(token)} nicht erlaubt.")
        self.nehmen()
        if not teile:
            raise AusdruckFehler("Leerer Index.")
        return "".join(teile).strip()

    def masseinheit(self) -> Masseinheit:
        self.erwarten(r"\mathrm")
        self.erwarten("{")
        name = ""
        while not self.ist("}"):
            token = self.nehmen()
            if token.art == "ende":
                raise AusdruckFehler("«}» fehlt.")
            name += token.text
        self.nehmen()
        einheit = EINHEITENNAMEN.get(name)
        if einheit is None:
            raise AusdruckFehler(f"Einheit «{name}» unbekannt.")
        return Masseinheit(einheit)

    def funktion(self) -> Funktion:
        name = self.nehmen().text
        zu = self._oeffnen()
        if zu is None:
            # ``\sin x``: ohne Klammer gilt die Funktion fuer den naechsten
            # Faktor samt Potenz.
            return Funktion(name, (self.potenz(),))
        argumente = [self.ausdruck()]
        while self.ist(",", ";"):
            self.nehmen()
            argumente.append(self.ausdruck())
        self._schliessen(zu)
        return Funktion(name, tuple(argumente))


# ===========================================================================
# Zeile
# ===========================================================================

@dataclass(frozen=True)
class Zeile:
    """Eine gelesene Zeile: was definiert wird (oder nichts) und womit."""

    name: Optional[Name]
    """Links vom Gleichheitszeichen -- ``None`` bei einer blossen Auswertung."""

    ausdruck: Knoten


def lesen(latex: str) -> Zeile:
    """
    ``b = 2a + 1\\,\\mathrm{m}`` definiert ``b``; ``a \\cdot b =`` oder
    ``a \\cdot b`` rechnet nur aus. Eine Neudefinition gilt ab ihrer Zeile.
    """
    tokens = zerlegen(latex)
    teile: List[List[Token]] = [[]]
    tiefe = 0
    for token in tokens[:-1]:
        if token.text in ("{", "(", "[", r"\left"):
            tiefe += token.text != r"\left"
        elif token.text in ("}", ")", "]"):
            tiefe -= 1
        if tiefe == 0 and (token.text == "=" or token.text in _ZUWEISUNG):
            if teile[-1] and teile[-1][-1].text == ":":
                teile[-1].pop()
            teile.append([])
            continue
        teile[-1].append(token)
    ende = tokens[-1]
    if len(teile) > 2 and teile[-1]:
        raise AusdruckFehler("Mehr als ein «=».")
    links, rechts = teile[0], (teile[1] if len(teile) > 1 else [])
    if not links:
        raise AusdruckFehler("Leere Zeile." if len(teile) == 1 else "Links vom «=» fehlt etwas.")
    if not rechts:
        return Zeile(None, _ganz(links, ende))
    name = _ganz(links, ende)
    if not isinstance(name, Name):
        raise AusdruckFehler("Links vom «=» steht kein Name.")
    return Zeile(name, _ganz(rechts, ende))


def _ganz(tokens: List[Token], ende: Token) -> Knoten:
    leser = _Leser(tokens + [ende])
    knoten = leser.ausdruck()
    if leser.jetzt.art != "ende":
        raise AusdruckFehler(f"{leser._beschreiben(leser.jetzt)} hier nicht erwartet.")
    return knoten


# ===========================================================================
# Rechnen
# ===========================================================================

def rechnen(knoten: Knoten, werte: Mapping[str, Groesse]) -> Groesse:
    """Den Baum ausrechnen -- ``werte`` nach Schreibweise der Namen."""
    try:
        return _rechnen(knoten, werte)
    except DimensionsFehler:
        raise AusdruckFehler("Einheiten passen nicht zusammen.") from None
    except ZeroDivisionError:
        raise AusdruckFehler("Division durch null.") from None
    except (ValueError, OverflowError) as fehler:
        raise AusdruckFehler(f"Nicht berechenbar ({fehler}).") from None


def _ohne_einheit(groesse: Groesse, wo: str) -> float:
    if not groesse.dimension.ist_dimensionslos:
        raise AusdruckFehler(f"{wo} braucht eine Zahl ohne Einheit.")
    return groesse.si


def _rechnen(knoten: Knoten, werte: Mapping[str, Groesse]) -> Groesse:
    if isinstance(knoten, Zahl):
        return Groesse(knoten.wert)
    if isinstance(knoten, Konstante):
        return Groesse(knoten.wert)
    if isinstance(knoten, Masseinheit):
        return Groesse(1.0, knoten.einheit)
    if isinstance(knoten, Name):
        if knoten.latex not in werte:
            raise AusdruckFehler(f"{knoten.latex} ist nicht definiert.")
        return werte[knoten.latex]
    if isinstance(knoten, Gegenzahl):
        return -_rechnen(knoten.inhalt, werte)
    if isinstance(knoten, Betrag):
        return abs(_rechnen(knoten.inhalt, werte))
    if isinstance(knoten, Operation):
        links = _rechnen(knoten.links, werte)
        rechts = _rechnen(knoten.rechts, werte)
        if knoten.zeichen == "+":
            return links + rechts
        if knoten.zeichen == "-":
            return links - rechts
        if knoten.zeichen == "*":
            return links * rechts
        if rechts.si == 0.0:
            raise ZeroDivisionError
        return links / rechts
    if isinstance(knoten, Potenz):
        basis = _rechnen(knoten.basis, werte)
        exponent = _ohne_einheit(_rechnen(knoten.exponent, werte), "Die Hochzahl")
        if basis.si < 0 and exponent != int(exponent):
            raise AusdruckFehler("Negative Basis mit gebrochener Hochzahl.")
        return basis ** exponent
    if isinstance(knoten, Wurzel):
        inhalt = _rechnen(knoten.inhalt, werte)
        grad = 2.0 if knoten.grad is None else _ohne_einheit(
            _rechnen(knoten.grad, werte), "Der Wurzelgrad")
        if inhalt.si < 0:
            if grad % 2 != 1:
                raise AusdruckFehler("Wurzel aus einer negativen Zahl.")
            return -((-inhalt) ** (1.0 / grad))
        return inhalt ** (1.0 / grad)
    if isinstance(knoten, Funktion):
        return _funktion(knoten, [_rechnen(a, werte) for a in knoten.argumente])
    raise AusdruckFehler("Unbekannter Ausdruck.")


_WINKEL = {r"\sin": math.sin, r"\cos": math.cos, r"\tan": math.tan,
           r"\cot": lambda x: 1.0 / math.tan(x), r"\sinh": math.sinh,
           r"\cosh": math.cosh, r"\tanh": math.tanh, r"\ln": math.log,
           r"\log": math.log10, r"\lg": math.log10, r"\exp": math.exp}
_ARKUS = {r"\arcsin": math.asin, r"\arccos": math.acos, r"\arctan": math.atan}


def _funktion(knoten: Funktion, argumente: List[Groesse]) -> Groesse:
    name = knoten.name
    if name in (r"\min", r"\max"):
        wahl = min if name == r"\min" else max
        try:
            return wahl(argumente)
        except DimensionsFehler:
            raise AusdruckFehler(f"{name[1:]}: Einheiten der Argumente verschieden.") from None
    if len(argumente) != 1:
        raise AusdruckFehler(f"{name[1:]} nimmt ein Argument.")
    wert = _ohne_einheit(argumente[0], name[1:])
    if name in _ARKUS:
        return Groesse.aus_si(_ARKUS[name](wert), GRAD)
    if name in (r"\ln", r"\log", r"\lg") and wert <= 0:
        raise AusdruckFehler(f"{name[1:]} nur für positive Zahlen.")
    return Groesse(_WINKEL[name](wert))


# ===========================================================================
# Setzen
# ===========================================================================

#: Bindungsstaerke -- danach entscheidet sich, wo eine Klammer noetig ist.
_SUMME, _PRODUKT, _VORZEICHEN, _POTENZ, _ATOM = range(5)


def _staerke(knoten: Knoten) -> int:
    if isinstance(knoten, Operation):
        return _SUMME if knoten.zeichen in "+-" else _PRODUKT
    if isinstance(knoten, Gegenzahl):
        return _VORZEICHEN
    if isinstance(knoten, Potenz):
        return _POTENZ
    return _ATOM


def _ist_angabe(knoten: Knoten) -> bool:
    """Eine Zahl mit Einheit -- ``5\\,\\mathrm{kN}``, auch mit ``/\\mathrm{m}^{2}``."""
    if isinstance(knoten, (Zahl, Masseinheit)):
        return True
    if isinstance(knoten, Gegenzahl):
        return _ist_angabe(knoten.inhalt)
    if isinstance(knoten, Operation) and knoten.zeichen in "*/":
        return _ist_angabe(knoten.links) and _ist_einheit(knoten.rechts)
    return _ist_einheit(knoten)


def _ist_einheit(knoten: Knoten) -> bool:
    """Ob der Teilbaum nur aus Einheiten besteht -- ``\\mathrm{kN}/\\mathrm{m}^{2}``."""
    if isinstance(knoten, Masseinheit):
        return True
    if isinstance(knoten, Potenz):
        return _ist_einheit(knoten.basis) and isinstance(knoten.exponent, (Zahl, Gegenzahl))
    if isinstance(knoten, Operation) and knoten.zeichen in "*/":
        return _ist_einheit(knoten.links) and _ist_einheit(knoten.rechts)
    return False


def setzen(knoten: Knoten, platzhalter: Mapping[str, str]) -> str:
    """
    Der Baum als Vorlage fuer :meth:`Formelzeile.bauen` -- Namen als
    ``@platzhalter``, alles andere aus dem Baum neu geschrieben.
    """
    return _setzen(knoten, platzhalter)


def _klammer(text: str) -> str:
    return rf"\left({text}\right)"


def _setzen(knoten: Knoten, ph: Mapping[str, str]) -> str:
    if isinstance(knoten, Zahl):
        return knoten.text
    if isinstance(knoten, Konstante):
        return knoten.latex
    if isinstance(knoten, Masseinheit):
        return knoten.einheit.latex or ""
    if isinstance(knoten, Name):
        return f"@{ph[knoten.latex]}"
    if isinstance(knoten, Gegenzahl):
        inhalt = _setzen(knoten.inhalt, ph)
        return f"-{_klammer(inhalt) if _staerke(knoten.inhalt) <= _VORZEICHEN else inhalt}"
    if isinstance(knoten, Betrag):
        return rf"\left|{_setzen(knoten.inhalt, ph)}\right|"
    if isinstance(knoten, Wurzel):
        inhalt = _setzen(knoten.inhalt, ph)
        if knoten.grad is None:
            return rf"\sqrt{{{inhalt}}}"
        return rf"\sqrt[{_setzen(knoten.grad, ph)}]{{{inhalt}}}"
    if isinstance(knoten, Funktion):
        argumente = r",\ ".join(_setzen(a, ph) for a in knoten.argumente)
        return rf"{knoten.name}{_klammer(argumente)}"
    if isinstance(knoten, Potenz):
        basis = _setzen(knoten.basis, ph)
        if not isinstance(knoten.basis, (Name, Masseinheit)) and _staerke(knoten.basis) < _ATOM:
            basis = _klammer(basis)
        elif isinstance(knoten.basis, Zahl) and knoten.basis.wert < 0:
            basis = _klammer(basis)
        return f"{basis}^{{{_setzen(knoten.exponent, ph)}}}"
    if isinstance(knoten, Operation):
        return _operation(knoten, ph)
    raise AusdruckFehler("Unbekannter Ausdruck.")


def _operation(knoten: Operation, ph: Mapping[str, str]) -> str:
    links, rechts = _setzen(knoten.links, ph), _setzen(knoten.rechts, ph)
    if knoten.zeichen == "/":
        if _ist_einheit(knoten.rechts) and _ist_angabe(knoten.links):
            return f"{links}/{rechts}"
        return rf"\frac{{{links}}}{{{rechts}}}"
    if knoten.zeichen == "*":
        if _staerke(knoten.links) < _PRODUKT:
            links = _klammer(links)
        # Zahl mal Einheit ist eine Angabe, kein Produkt: 3 m, nicht 3 · m;
        # das Gradzeichen klebt an der Zahl.
        if isinstance(knoten.rechts, Masseinheit):
            return links + knoten.rechts.einheit.als_latex()
        if _ist_einheit(knoten.rechts):
            return rf"{links}\,{rechts}"
        if _staerke(knoten.rechts) < _PRODUKT:
            rechts = _klammer(rechts)
        return rf"{links} \cdot {rechts}"
    if knoten.zeichen == "-" and _staerke(knoten.rechts) <= _SUMME:
        rechts = _klammer(rechts)
    if isinstance(knoten.rechts, Gegenzahl):
        rechts = _klammer(rechts)
    return f"{links} {knoten.zeichen} {rechts}"


def namen(knoten: Knoten) -> List[str]:
    """Die Namen im Baum, in der Folge ihres ersten Auftretens."""
    gefunden: List[str] = []

    def besuchen(k: Knoten) -> None:
        if isinstance(k, Name):
            if k.latex not in gefunden:
                gefunden.append(k.latex)
        elif isinstance(k, Operation):
            besuchen(k.links)
            besuchen(k.rechts)
        elif isinstance(k, Potenz):
            besuchen(k.basis)
            besuchen(k.exponent)
        elif isinstance(k, (Gegenzahl, Betrag)):
            besuchen(k.inhalt)
        elif isinstance(k, Wurzel):
            besuchen(k.inhalt)
            if k.grad is not None:
                besuchen(k.grad)
        elif isinstance(k, Funktion):
            for a in k.argumente:
                besuchen(a)

    besuchen(knoten)
    return gefunden


def stellen(groesse: Groesse, einheit: Einheit, signifikant: int = 4) -> int:
    """Nachkommastellen fuer ``signifikant`` geltende Ziffern -- hoechstens 10."""
    zahl = abs(groesse.in_einheit(einheit))
    if zahl == 0 or not math.isfinite(zahl):
        return 0
    return min(10, max(0, signifikant - 1 - math.floor(math.log10(zahl))))
