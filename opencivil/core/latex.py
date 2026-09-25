"""
opencivil/core/latex.py -- Bausteine fuer die LaTeX-Ausgabe von Berechnungen.

VERANTWORTUNG:
Nimmt einer Berechnung die *mechanische* Haelfte der LaTeX-Arbeit ab. Von Hand
geschrieben wird nur die **analytische** Form einer Formel; die Fassung "mit
Zahlen und Einheiten" wird daraus automatisch erzeugt, indem die Platzhalter
durch die tatsaechlichen Werte ersetzt werden.

Damit verschwindet die schlimmste Doppelspurigkeit des alten Codes, in dem
jede Formel zweimal getippt wurde -- einmal symbolisch, einmal numerisch --
und beide Fassungen unbemerkt auseinanderlaufen konnten.

PLATZHALTER:
In der Vorlage steht ``@name`` fuer eine Eingabe. Wo der Name an ein Zeichen
grenzt, das noch zum Namen gehoeren koennte, schreibt man ``@{name}``::

    r"\\frac{@eta_fc \\cdot @f_ck}{@gamma_c}"

    symbolisch -> \\frac{\\eta_{fc} \\cdot f_{ck}}{\\gamma_c}
    numerisch  -> \\frac{0.933 \\cdot 30\\,\\mathrm{N/mm^2}}{1.5}

EIGENSTAENDIG NUTZBAR::

    from opencivil.core.latex import Formelzeile
    zeile = Formelzeile.bauen(ergebnis, r"@a \\cdot @b", {"a": wert_a, "b": wert_b})
    print(zeile.einzeilig())
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Iterable, Mapping, Optional, Sequence, Union

from opencivil.core.einheiten import EINHEITSLOS, Einheit
from opencivil.core.wert import Wert

#: ``@name`` oder ``@{name}``
_PLATZHALTER = re.compile(r"@\{([A-Za-z_][A-Za-z0-9_]*)\}|@([A-Za-z_][A-Za-z0-9_]*)")

_SONDERZEICHEN = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "^": r"\textasciicircum{}",
    "~": r"\textasciitilde{}",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


class LatexFehler(Exception):
    """Fehler beim Aufbau einer LaTeX-Ausgabe."""


def text_latex(text: str) -> str:
    """
    Maskiert Sonderzeichen fuer den Fliesstext.

    Umlaute bleiben unangetastet -- die Praeambel des Berichts stellt UTF-8
    ein, damit 'Ueberdeckung' auch als 'Überdeckung' gesetzt werden kann.
    """
    return "".join(_SONDERZEICHEN.get(z, z) for z in text)


def als_text(text: str) -> str:
    """
    Verpackt deutschen Klartext fuer die Mathematikumgebung.

    **Immer hierdurch**, nie ``\\text{...}`` von Hand um eine Zeichenkette
    legen, die nicht buchstabiert im Quelltext steht. Namen kommen aus dem
    Projekt oder aus einer Berechnung und enthalten Zeichen wie ``_``, die auch
    im Textmodus Befehle sind: ``M_Rd(N=0)`` bringt KaTeX zum Abbruch, und
    dann steht im Bericht der rohe Quelltext statt der Beschriftung.
    """
    return rf"\text{{{text_latex(text)}}}"


def platzhalter_namen(vorlage: str) -> list[str]:
    """Liefert alle in einer Vorlage vorkommenden Platzhalternamen."""
    namen: list[str] = []
    for geklammert, blank in _PLATZHALTER.findall(vorlage):
        name = geklammert or blank
        if name not in namen:
            namen.append(name)
    return namen


def _ersetzen(vorlage: str, ersatz) -> str:
    """
    Ersetzt alle Platzhalter mittels einer Funktion ``(name, hoch) -> str``.

    ``hoch`` sagt, ob hinter dem Platzhalter ein Exponent steht: ``@h^{2}``
    braucht mit Zahl und Einheit eine Klammer, ``(300 mm)^2`` und nicht
    ``300 mm^2``.
    """

    def _treffer(m: re.Match) -> str:
        return ersatz(m.group(1) or m.group(2), vorlage.startswith("^", m.end()))

    return _PLATZHALTER.sub(_treffer, vorlage)


def _pruefe_vollstaendig(vorlage: str, eingaben: Mapping[str, Wert], kontext: str) -> None:
    fehlend = [n for n in platzhalter_namen(vorlage) if n not in eingaben]
    if fehlend:
        raise LatexFehler(
            f"{kontext}: Die Vorlage verwendet Platzhalter {fehlend}, zu denen keine "
            f"Eingabe uebergeben wurde. Bekannt sind: {sorted(eingaben)}."
        )


def einsetzen_symbolisch(
    vorlage: str, eingaben: Mapping[str, Wert], kontext: str = "Formel"
) -> str:
    """Ersetzt die Platzhalter durch die Symbole der Eingaben."""
    _pruefe_vollstaendig(vorlage, eingaben, kontext)

    def _symbol(name: str, hoch: bool) -> str:
        # Ein Symbol mit eigenem Hochindex vertraegt keinen zweiten.
        symbol = eingaben[name].symbol
        return f"{{{symbol}}}" if hoch and "^" in symbol else symbol

    return _ersetzen(vorlage, _symbol)


def _blank(wert: Wert, einheit: Einheit) -> str:
    """
    Die Zahl eines Werts in einer anderen Einheit, ohne diese dazuzuschreiben.

    Die Stellen wandern mit: 248.1 mm auf eine Stelle sind in Metern 0.2481,
    nicht 0.2 -- sonst ginge in der Herleitung Genauigkeit verloren, die die
    Rechnung hatte.
    """
    verschiebung = round(math.log10(wert.einheit.faktor / einheit.faktor))
    return wert.groesse.formatiert(max(0, wert.stellen - verschiebung), einheit)


def einsetzen_numerisch(
    vorlage: str, eingaben: Mapping[str, Wert], kontext: str = "Formel",
    *, empirisch: Optional[Mapping[str, Einheit]] = None,
) -> str:
    """
    Ersetzt die Platzhalter durch Zahlenwerte samt Einheit.

    Negative Werte werden geklammert, damit nicht ``a \\cdot -5`` entsteht.
    Besteht die Vorlage nur aus einem einzigen Platzhalter, entfaellt die
    Klammer -- dort waere sie reine Unruhe.

    ``empirisch`` nennt die Eingaben einer dimensionell inhomogenen
    Normformel mit der Einheit, in der die Norm sie verlangt. Sie stehen als
    blanke Zahl in dieser Einheit da: ``\\sqrt{30}`` und nicht
    ``\\sqrt{30\\,\\mathrm{N}/\\mathrm{mm}^{2}}`` -- die Wurzel einer
    Spannung gibt es nicht, und so zu tun waere falsch.
    """
    _pruefe_vollstaendig(vorlage, eingaben, kontext)
    nur_ein_platzhalter = _PLATZHALTER.fullmatch(vorlage.strip()) is not None
    empirisch = empirisch or {}

    def _wert(name: str, hoch: bool) -> str:
        wert = eingaben[name]
        blank = name in empirisch or wert.einheit is EINHEITSLOS
        text = _blank(wert, empirisch[name]) if name in empirisch else wert.zahl_latex()
        if (wert.groesse.si < 0 and not nur_ein_platzhalter) or (hoch and not blank):
            return f"\\left({text}\\right)"
        return text

    return _ersetzen(vorlage, _wert)


# ===========================================================================
# Formelzeile
# ===========================================================================


# ===========================================================================
# Sichtbare Breite
# ===========================================================================

#: Wie breit eine Formel gesetzt hoechstens sein darf, damit sie auf einer
#: Zeile steht -- in Zeichen, wie :func:`sichtbare_breite` sie zaehlt. Etwa
#: das, was auf einer A4-Seite und in der rechten Tafel noch Platz hat.
ZEILENBREITE = 60.0

#: Befehle ohne eigene Breite: Formatierung, oder ihr Argument steht fuer sie.
_OHNE_BREITE = {"left", "right", "mathrm", "text", "operatorname", "mathbf",
                "mathit", "displaystyle", "textstyle", "big", "Big", "bigl",
                "bigr", "Bigl", "Bigr", "limits", "nolimits"}
#: Operatoren, die mit ihren Buchstaben dastehen.
_WOERTER = {"min", "max", "sin", "cos", "tan", "cot", "log", "ln", "exp",
            "lim", "sup", "inf"}
#: Zwischenraeume, in Zeichen.
_RAEUME = {",": 0.2, ":": 0.25, ";": 0.3, "!": 0.0, " ": 0.3,
           "quad": 1.0, "qquad": 2.0}
#: Relationen und Pfeile stehen mit Luft auf beiden Seiten, Rechenzeichen
#: mit etwas weniger.
_RELATIONEN = {"le", "ge", "leq", "geq", "approx", "neq", "equiv",
               "Rightarrow", "Leftarrow", "rightarrow", "leftarrow", "to"}
_BINAER = {"cdot", "times", "pm", "mp"}
_BEFEHL = re.compile(r"\\([A-Za-z]+|.)")


def _gruppe(s: str, i: int) -> tuple[str, int]:
    """Das Argument ab ``i``: eine ``{...}``-Gruppe oder ein einzelnes Zeichen."""
    while i < len(s) and s[i] == " ":
        i += 1
    if i >= len(s):
        return "", i
    if s[i] == "\\":
        treffer = _BEFEHL.match(s, i)
        return treffer.group(0), treffer.end()
    if s[i] != "{":
        return s[i], i + 1
    tiefe = 0
    for j in range(i, len(s)):
        if s[j] == "\\":
            continue
        if s[j] == "{" and (j == 0 or s[j - 1] != "\\"):
            tiefe += 1
        elif s[j] == "}" and s[j - 1] != "\\":
            tiefe -= 1
            if tiefe == 0:
                return s[i + 1:j], j + 1
    return s[i + 1:], len(s)


def sichtbare_breite(latex: str) -> float:
    """
    Ungefaehr, wie breit eine Formel gesetzt wird -- in Zeichen.

    Gezaehlt wird, was man sieht: ein Bruch so breit wie sein breiterer Teil,
    Hoch- und Tiefgestelltes kleiner, ``\\alpha`` oder ``\\cdot`` als ein
    Zeichen, Formatierung (``\\left``, ``\\,``, ``\\mathrm``, die Klammern
    einer Gruppe) fast nichts. Eine Umgebung mit Zeilen ist so breit wie ihre
    breiteste Zeile.
    """
    breite = 0.0
    i = 0
    while i < len(latex):
        zeichen = latex[i]
        if zeichen == "\\":
            treffer = _BEFEHL.match(latex, i)
            name, i = treffer.group(1), treffer.end()
            if name in ("frac", "tfrac", "dfrac"):
                oben, i = _gruppe(latex, i)
                unten, i = _gruppe(latex, i)
                faktor = 0.8 if name == "tfrac" else 1.0
                breite += faktor * max(sichtbare_breite(oben), sichtbare_breite(unten)) + 0.4
            elif name == "sqrt":
                if i < len(latex) and latex[i] == "[":
                    i = latex.index("]", i) + 1
                inhalt, i = _gruppe(latex, i)
                breite += sichtbare_breite(inhalt) + 1.0
            elif name == "begin":
                umgebung, i = _gruppe(latex, i)
                if umgebung == "array":
                    _, i = _gruppe(latex, i)
                ende = latex.find(rf"\end{{{umgebung}}}", i)
                ende = len(latex) if ende < 0 else ende
                zeilen = latex[i:ende].split("\\\\")
                breite += max(sichtbare_breite(z) for z in zeilen)
                breite += 1.0 if umgebung == "cases" else 0.0
                i = ende + len(rf"\end{{{umgebung}}}")
            elif name in _OHNE_BREITE:
                pass
            elif name in _RAEUME:
                breite += _RAEUME[name]
            elif name in _WOERTER:
                breite += len(name)
            elif name in _RELATIONEN:
                breite += 2.0
            elif name in _BINAER:
                breite += 1.6
            else:
                breite += 1.0
        elif zeichen in "^_":
            inhalt, i = _gruppe(latex, i + 1)
            breite += 0.7 * sichtbare_breite(inhalt)
        else:
            i += 1
            if zeichen in "=<>":
                breite += 2.0
            elif zeichen in "+-":
                breite += 1.6
            elif zeichen not in "{} &":
                breite += 1.0
    return breite


@dataclass(frozen=True)
class Formelzeile:
    """
    Die vier Bestandteile einer ausgeschriebenen Formel.

    Wird strukturiert gehalten statt als fertiger String, damit der Bericht
    selbst entscheiden kann, ob er ein- oder mehrzeilig setzt. Das alte
    Vorgehen -- den fertigen String an ``" = "`` wieder auseinanderzuschneiden --
    ging kaputt, sobald in einer Formel ein Gleichheitszeichen vorkam.
    """

    symbol: str
    """Linke Seite, z.B. ``f_{cd}``."""

    analytisch: Optional[str]
    """Von Hand geschriebene Formel mit Symbolen. None bei reinen Eingaben."""

    numerisch: Optional[str]
    """Dieselbe Formel mit eingesetzten Zahlen und Einheiten."""

    ergebnis: str
    """Resultat mit Einheit, z.B. ``18.7\\,\\mathrm{MPa}``."""

    nachsatz: str = ""
    """Was hinter dem Resultat steht: ein Vergleich mit Urteil, ein Hinweis."""

    @classmethod
    def bauen(
        cls,
        ergebnis: Wert,
        vorlage: Optional[str] = None,
        eingaben: Optional[Mapping[str, Wert]] = None,
        *,
        empirisch: Optional[Mapping[str, Einheit]] = None,
        nachsatz: str = "",
    ) -> "Formelzeile":
        """
        Baut die Zeile aus Resultat, analytischer Vorlage und Eingaben.

        Ohne Vorlage entsteht die schlichte Form ``symbol = wert`` -- passend
        fuer Eingaben und Vorgabewerte. Zu ``empirisch`` siehe
        :func:`einsetzen_numerisch`; welche Einheiten dort vorausgesetzt sind,
        steht am Ende der Zeile, sonst liessen sich die blanken Zahlen nicht
        lesen.
        """
        eingaben = eingaben or {}
        kontext = f"Wert '{ergebnis.id}'"
        if vorlage is None:
            return cls(
                symbol=ergebnis.symbol,
                analytisch=None,
                numerisch=None,
                ergebnis=ergebnis.zahl_latex(),
                nachsatz=nachsatz,
            )
        einheiten = [rf"{eingaben[name].symbol}\ \text{{in}}\ {einheit.latex}"
                     for name, einheit in (empirisch or {}).items()
                     if einheit is not EINHEITSLOS and name in eingaben]
        if einheiten:
            trenner = r",\ "
            hinweis = rf"\quad \left({trenner.join(einheiten)}\right)"
            nachsatz = f"{nachsatz} {hinweis}".strip()
        return cls(
            symbol=ergebnis.symbol,
            analytisch=einsetzen_symbolisch(vorlage, eingaben, kontext),
            numerisch=einsetzen_numerisch(vorlage, eingaben, kontext,
                                          empirisch=empirisch),
            ergebnis=ergebnis.zahl_latex(),
            nachsatz=nachsatz,
        )

    # -- Darstellung --------------------------------------------------------

    def _teile(self) -> list[str]:
        """Die darzustellenden Abschnitte, ohne sinnlose Wiederholungen."""
        teile = [self.symbol]
        for kandidat in (self.analytisch, self.numerisch):
            if kandidat is None:
                continue
            # Eine Fassung, die schon identisch dasteht, wird nicht wiederholt.
            if kandidat == teile[-1] or kandidat == self.ergebnis:
                continue
            teile.append(kandidat)
        teile.append(self.ergebnis)
        return teile

    def einzeilig(self) -> str:
        """``f_{cd} = \\frac{...} = \\frac{...} = 18.7\\,\\mathrm{MPa}``"""
        return " ".join(filter(None, [" = ".join(self._teile()), self.nachsatz]))

    def mehrzeilig(self) -> str:
        """Dieselbe Zeile als ``aligned``-Umgebung, fuer lange Formeln."""
        teile = self._teile()
        if len(teile) <= 2:
            return self.einzeilig()
        zeilen = [f"{teile[0]} &= {teile[1]}"]
        zeilen.extend(f"&= {t}" for t in teile[2:])
        if self.nachsatz:
            zeilen[-1] += f" {self.nachsatz}"
        inhalt = " \\\\\n  ".join(zeilen)
        return f"\\begin{{aligned}}\n  {inhalt}\n\\end{{aligned}}"

    def darstellen(self, mehrzeilig_ab: float = ZEILENBREITE) -> str:
        """
        Eine Zeile, solange sie gesetzt hineinpasst, sonst untereinander.

        Gemessen wird, was man sieht (:func:`sichtbare_breite`), nicht der
        Quelltext. Mit dessen Laenge standen kurze Formeln auf drei Zeilen,
        weil ``\\left``, ``\\,\\mathrm{mm}`` und die Klammern der Gruppen
        mitzaehlten.
        """
        einzeilig = self.einzeilig()
        if sichtbare_breite(einzeilig) <= mehrzeilig_ab:
            return einzeilig
        return self.mehrzeilig()

    def __str__(self) -> str:
        return self.einzeilig()


# ===========================================================================
# Weitere Bausteine
# ===========================================================================


def urteil(erfuellt: bool) -> str:
    """Das Urteil hinter einem Nachweis -- ein Wortlaut fuer alle."""
    return r"\text{erfüllt}" if erfuellt else r"\text{NICHT erfüllt}"


def angabe(wert: Wert) -> str:
    """``Symbol = Zahl Einheit`` -- ein Wert, wie er in einem Vergleich steht."""
    return f"{wert.symbol} = {wert.zahl_latex()}"


def bedingung(links: str, zeichen: str, rechts: str, erfuellt: bool) -> str:
    """
    Setzt einen Vergleich mit sichtbarem Ergebnis, z.B. fuer Nachweise::

        M_{Ed} = 120\\,\\mathrm{kNm} \\quad \\le \\quad M_{Rd} = 145\\,\\mathrm{kNm}
        \\quad \\Rightarrow \\quad \\text{erfüllt}
    """
    return (rf"{links} \quad {zeichen} \quad {rechts}"
            rf" \quad \Rightarrow \quad {urteil(erfuellt)}")


def vergleich(zeichen: str, rechts: str, erfuellt: bool) -> str:
    """
    Der Nachsatz einer Formel, deren Resultat gegen etwas gehalten wird::

        \\quad \\ge \\quad N_{Riss} = 378.3\\,\\mathrm{kN}
        \\quad \\Rightarrow \\quad \\text{NICHT erfüllt}
    """
    return rf"\quad {zeichen} \quad {rechts} \quad \Rightarrow \quad {urteil(erfuellt)}"


@dataclass(frozen=True)
class Mathe:
    """
    Eine Tabellenzelle, die Mathematik ist -- Symbol, Einheit, Formel.

    Nicht ``Formel``: so heisst schon die deklarative Berechnung in
    :mod:`opencivil.core.berechnung`, und die beiden sind verschiedene Dinge.

    Eine Zahl ist ebenfalls Mathe: ihr Minus ist ein Minuszeichen und kein
    Bindestrich, und sie steht in derselben Schrift wie in den Gleichungen.

    Jede andere Zelle ist Text: ein ``str``. Vorher war jede Zelle LaTeX,
    und reiner Text stand als ``\\text{...}`` darin. Die Konsole druckte das
    so ab, der Word-Knopf lieferte eine Formelmatrix statt einer Tabelle, und
    die Oberflaeche las den Text per regulaerem Ausdruck wieder heraus.
    Welche Art eine Zelle hat, weiss nur, wer sie schreibt -- also sagt sie
    es.
    """

    latex: str


#: Eine Tabellenzelle: Text oder :class:`Mathe`.
Zelle = Union[str, Mathe]


def zelle_latex(zelle: Zelle) -> str:
    """Eine Zelle fuer ein LaTeX-Dokument: Text maskiert, Formel in ``$...$``."""
    if isinstance(zelle, Mathe):
        return f"${zelle.latex}$"
    return text_latex(zelle)


#: Eine Spalte, die links steht und umbrechen darf -- ``L`` in der Ausrichtung.
UMBRUCHSPALTE = r">{\raggedright\arraybackslash}X"


def tabelle(
    kopf: Sequence[Zelle],
    zeilen: Iterable[Sequence[Zelle]],
    ausrichtung: Optional[str] = None,
    *,
    lang: bool = False,
) -> str:
    """
    Eine Tabelle fuer ein LaTeX-Dokument.

    ``ausrichtung`` je Spalte ``l``, ``c`` oder ``r`` wie in LaTeX, dazu
    ``L``: links, und die Spalte darf umbrechen. Das braucht eine Textspalte,
    die sonst die Tabelle ueber den Rand schoebe -- welche das ist, weiss nur,
    wer die Tabelle schreibt.

    Ohne ``lang`` ein ``tabular`` mit ``\\hline``, fuer die Kopierknoepfe:
    es laeuft in jedem Dokument, ohne dass dort erst ein Paket geladen werden
    muss, und ``L`` gilt darin als ``l``. Kein ``array`` mehr: das ist eine
    Formel und keine Tabelle, und Word und Markdown koennen damit nichts
    anfangen.

    Mit ``lang`` fuer den Bericht: die Tabelle darf ueber Seiten laufen und
    wiederholt dort ihren Kopf (``longtable``). Hat sie eine ``L``-Spalte,
    nimmt sie die Zeilenbreite ein, und nur diese Spalten brechen um
    (``xltabular``).
    """
    kopf = list(kopf)
    spalten = ausrichtung or ("r" * len(kopf))
    if len(spalten) != len(kopf) or set(spalten) - set("lcrL"):
        raise LatexFehler(
            f"Ausrichtung '{spalten}' passt nicht zu {len(kopf)} Spalten "
            f"(je Spalte l, c, r oder L)."
        )

    def zeile(zellen: Sequence[Zelle]) -> str:
        if len(zellen) != len(kopf):
            raise LatexFehler(
                f"Tabellenzeile hat {len(zellen)} Zellen, erwartet werden {len(kopf)}."
            )
        return " & ".join(zelle_latex(z) for z in zellen) + r" \\"

    koerper = [zeile(list(z)) for z in zeilen]
    if not lang:
        return "\n".join([
            rf"\begin{{tabular}}{{{spalten.replace('L', 'l')}}}", r"\hline",
            zeile(kopf), r"\hline", *koerper, r"\hline", r"\end{tabular}",
        ])
    if "L" in spalten:
        umgebung = "xltabular"
        anfang = (rf"\begin{{xltabular}}{{\linewidth}}"
                  rf"{{{spalten.replace('L', UMBRUCHSPALTE)}}}")
    else:
        umgebung = "longtable"
        anfang = rf"\begin{{longtable}}{{{spalten}}}"
    return "\n".join([
        anfang, r"\hline", zeile(kopf), r"\hline", r"\endhead",
        *koerper, r"\hline", rf"\end{{{umgebung}}}",
    ])


def fallunterscheidung(faelle: Sequence[tuple[str, str]], gewaehlt: int = -1) -> str:
    """
    Setzt eine ``cases``-Umgebung und hebt den zutreffenden Fall hervor.

    Genau dafuer gedacht, dass eine Formel je nach Eingaben anders lautet: der
    Leser sieht alle Zweige und erkennt, welcher gegriffen hat.

    :param faelle: Paare aus (Ausdruck, Bedingung).
    :param gewaehlt: Index des zutreffenden Falls, oder -1 fuer keine Hervorhebung.
    """
    zeilen = []
    for i, (ausdruck, bed) in enumerate(faelle):
        markierung = r"\quad \leftarrow" if i == gewaehlt else ""
        zeilen.append(rf"{ausdruck} & {bed}{markierung}")
    inhalt = " \\\\\n  ".join(zeilen)
    return f"\\begin{{cases}}\n  {inhalt}\n\\end{{cases}}"
