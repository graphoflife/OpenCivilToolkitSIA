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

import re
from dataclasses import dataclass
from typing import Iterable, Mapping, Optional, Sequence, Union

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
    """Ersetzt alle Platzhalter mittels einer Funktion ``name -> str``."""

    def _treffer(m: re.Match) -> str:
        return ersatz(m.group(1) or m.group(2))

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
    return _ersetzen(vorlage, lambda name: eingaben[name].symbol)


def einsetzen_numerisch(
    vorlage: str, eingaben: Mapping[str, Wert], kontext: str = "Formel"
) -> str:
    """
    Ersetzt die Platzhalter durch Zahlenwerte samt Einheit.

    Negative Werte werden geklammert, damit nicht ``a \\cdot -5`` entsteht.
    Besteht die Vorlage nur aus einem einzigen Platzhalter, entfaellt die
    Klammer -- dort waere sie reine Unruhe.
    """
    _pruefe_vollstaendig(vorlage, eingaben, kontext)
    nur_ein_platzhalter = _PLATZHALTER.fullmatch(vorlage.strip()) is not None

    def _wert(name: str) -> str:
        wert = eingaben[name]
        text = wert.zahl_latex()
        if wert.groesse.si < 0 and not nur_ein_platzhalter:
            return f"\\left({text}\\right)"
        return text

    return _ersetzen(vorlage, _wert)


# ===========================================================================
# Formelzeile
# ===========================================================================


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

    @classmethod
    def bauen(
        cls,
        ergebnis: Wert,
        vorlage: Optional[str] = None,
        eingaben: Optional[Mapping[str, Wert]] = None,
    ) -> "Formelzeile":
        """
        Baut die Zeile aus Resultat, analytischer Vorlage und Eingaben.

        Ohne Vorlage entsteht die schlichte Form ``symbol = wert`` -- passend
        fuer Eingaben und Vorgabewerte.
        """
        eingaben = eingaben or {}
        kontext = f"Wert '{ergebnis.id}'"
        if vorlage is None:
            return cls(
                symbol=ergebnis.symbol,
                analytisch=None,
                numerisch=None,
                ergebnis=ergebnis.zahl_latex(),
            )
        return cls(
            symbol=ergebnis.symbol,
            analytisch=einsetzen_symbolisch(vorlage, eingaben, kontext),
            numerisch=einsetzen_numerisch(vorlage, eingaben, kontext),
            ergebnis=ergebnis.zahl_latex(),
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
        return " = ".join(self._teile())

    def mehrzeilig(self) -> str:
        """Dieselbe Zeile als ``aligned``-Umgebung, fuer lange Formeln."""
        teile = self._teile()
        if len(teile) <= 2:
            return self.einzeilig()
        zeilen = [f"{teile[0]} &= {teile[1]}"]
        zeilen.extend(f"&= {t}" for t in teile[2:])
        inhalt = " \\\\\n  ".join(zeilen)
        return f"\\begin{{aligned}}\n  {inhalt}\n\\end{{aligned}}"

    def darstellen(self, mehrzeilig_ab: int = 90) -> str:
        """Waehlt automatisch zwischen ein- und mehrzeilig nach Laenge."""
        einzeilig = self.einzeilig()
        if len(einzeilig) <= mehrzeilig_ab:
            return einzeilig
        return self.mehrzeilig()

    def __str__(self) -> str:
        return self.einzeilig()


# ===========================================================================
# Weitere Bausteine
# ===========================================================================


def bedingung(links: str, zeichen: str, rechts: str, erfuellt: bool) -> str:
    """
    Setzt einen Vergleich mit sichtbarem Ergebnis, z.B. fuer Nachweise::

        M_{Ed} = 120\\,\\mathrm{kNm} \\le M_{Rd} = 145\\,\\mathrm{kNm}
        \\quad \\Rightarrow \\quad \\text{erfüllt}
    """
    urteil = r"\text{erfüllt}" if erfuellt else r"\text{NICHT erfüllt}"
    return rf"{links} {zeichen} {rechts} \quad \Rightarrow \quad {urteil}"


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


def tabelle(
    kopf: Sequence[Zelle],
    zeilen: Iterable[Sequence[Zelle]],
    ausrichtung: Optional[str] = None,
) -> str:
    """
    Eine Tabelle fuer ein LaTeX-Dokument -- ``tabular`` mit ``\\hline``.

    Kein ``array`` mehr: das ist eine Formel und keine Tabelle, und Word und
    Markdown koennen damit nichts anfangen. ``\\hline`` statt booktabs,
    damit ein kopiertes Stueck in jedem Dokument laeuft, ohne dass dort
    erst ein Paket geladen werden muss.
    """
    kopf = list(kopf)
    spalten = ausrichtung or ("r" * len(kopf))
    if len(spalten) != len(kopf):
        raise LatexFehler(
            f"Ausrichtung '{spalten}' passt nicht zu {len(kopf)} Spalten."
        )
    aufbau = [rf"\begin{{tabular}}{{{spalten}}}", r"\hline",
              " & ".join(zelle_latex(z) for z in kopf) + r" \\", r"\hline"]
    for zeile in zeilen:
        zellen = list(zeile)
        if len(zellen) != len(kopf):
            raise LatexFehler(
                f"Tabellenzeile hat {len(zellen)} Zellen, erwartet werden {len(kopf)}."
            )
        aufbau.append(" & ".join(zelle_latex(z) for z in zellen) + r" \\")
    aufbau += [r"\hline", r"\end{tabular}"]
    return "\n".join(aufbau)


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
