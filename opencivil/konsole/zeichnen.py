"""
opencivil/konsole/zeichnen.py -- Diagramme aus der App «Python», ohne matplotlib.

VERANTWORTUNG:
Die gängigen Befehle von ``matplotlib.pyplot``, unter denselben Namen:
``plot``, ``scatter``, ``bar``, ``xlabel``, ``ylabel``, ``title``,
``legend``, ``grid``, ``xlim``, ``ylim``, ``axhline``, ``axvline``,
``figure``, ``show``. Wer matplotlib kennt, schreibt::

    import zeichnen as plt
    plt.plot([0, 1, 2], [0, 1, 4], "o-", label="y = x²")
    plt.xlabel("x")
    plt.legend()
    plt.show()

GEZEICHNET WIRD NICHT HIER:
Ein Bild ist eine Beschreibung -- Reihen, Achsen, Titel --, und die
Oberfläche zeichnet sie wie ihre übrigen Diagramme (``web/js/zeichnen.js``).
Darum braucht es keinen Download und kaum Speicher; matplotlib brächte rund
10 MB mit (Benutzer, 2026-10-15: lieber ein eigenes Modul).

WOHIN EIN BILD GEHT:
``show()`` gibt das Bild an die Sitzung, die es zwischen die Ausgaben
stellt (:mod:`opencivil.konsole.sitzung`); was am Ende eines Laufs noch
offen ist, kommt von selbst dazu, wie in einem Notizbuch. Ausserhalb einer
Sitzung sammelt das Modul die Bilder, bis jemand :func:`abholen` ruft.
"""

from __future__ import annotations

import math
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence

#: Die Farben der Formatkürzel von matplotlib, als Farben für SVG: ``"r--"``
#: ist rot gestrichelt. Dieselben Töne wie dort.
FARBKUERZEL = {"b": "blue", "g": "green", "r": "red", "c": "#00bfbf", "m": "#bf00bf",
               "y": "#bfbf00", "k": "black", "w": "white"}

#: Linienarten, wie matplotlib sie schreibt -- auch ausgeschrieben.
STRICHE = {"-": "-", "--": "--", ":": ":", "-.": "-.", "solid": "-", "dashed": "--",
           "dotted": ":", "dashdot": "-.", "": "", "None": "", "none": ""}

#: Marken: Kreis, Quadrat, Dreieck, Punkt, Kreuz, Plus, Raute.
MARKEN = ("o", "s", "^", ".", "x", "+", "D")


class Figur:
    """Ein Bild im Entstehen: Reihen, Hilfslinien, Beschriftung."""

    def __init__(self) -> None:
        self.reihen: List[Dict[str, Any]] = []
        self.hilfslinien: List[Dict[str, Any]] = []
        self.titel = ""
        self.xlabel = ""
        self.ylabel = ""
        self.gitter = False
        self.legende = False
        self.xbereich: Optional[List[float]] = None
        self.ybereich: Optional[List[float]] = None
        self.kategorien: Optional[List[str]] = None

    @property
    def leer(self) -> bool:
        return not self.reihen and not self.hilfslinien

    def als_dict(self) -> Dict[str, Any]:
        return {"titel": self.titel, "xlabel": self.xlabel, "ylabel": self.ylabel,
                "gitter": self.gitter, "legende": self.legende,
                "xbereich": self.xbereich, "ybereich": self.ybereich,
                "kategorien": self.kategorien,
                "reihen": self.reihen, "hilfslinien": self.hilfslinien}


_aktuell = Figur()
_gesammelt: List[Dict[str, Any]] = []
#: Wohin ein fertiges Bild geht -- die Sitzung setzt es für die Dauer eines Laufs.
_ziel: Optional[Callable[[Dict[str, Any]], None]] = None


# ===========================================================================
# Bilder
# ===========================================================================


def figure(*_args: Any, **_kwargs: Any) -> None:
    """Beginnt ein neues Bild; ein angefangenes kommt vorher heraus. Grösse und Nummer zählen nicht."""
    show()


def show(*_args: Any, **_kwargs: Any) -> None:
    """Gibt das Bild heraus und beginnt ein neues -- ein leeres bleibt ungezeigt."""
    global _aktuell
    if _aktuell.leer:
        return
    bild = _aktuell.als_dict()
    _aktuell = Figur()
    if _ziel is not None:
        _ziel(bild)
    else:
        _gesammelt.append(bild)


def clf() -> None:
    """Verwirft das angefangene Bild."""
    global _aktuell
    _aktuell = Figur()


close = clf


def abholen() -> List[Dict[str, Any]]:
    """Die Bilder, die ausserhalb einer Sitzung herauskamen -- und dazu das offene."""
    show()
    heraus = list(_gesammelt)
    _gesammelt.clear()
    return heraus


def savefig(*_args: Any, **_kwargs: Any) -> None:
    raise NotImplementedError(
        "savefig gibt es hier nicht: das Bild steht in der Konsole, "
        "mit der rechten Maustaste lässt es sich speichern.")


# ===========================================================================
# Reihen
# ===========================================================================


def plot(*args: Any, label: Optional[str] = None, color: Optional[str] = None,
         c: Optional[str] = None, linestyle: Optional[str] = None,
         ls: Optional[str] = None, marker: Optional[str] = None,
         linewidth: Optional[float] = None, lw: Optional[float] = None,
         markersize: Optional[float] = None, ms: Optional[float] = None,
         alpha: Optional[float] = None) -> None:
    """
    Eine Linie: ``plot(y)``, ``plot(x, y)`` oder ``plot(x, y, "r--o")`` --
    mehrere Paare hintereinander geben mehrere Linien.
    """
    for x, y, fmt in _paare(args, "plot"):
        farbe, strich, marke = _format(fmt)
        _reihe("linie", x, y, name=label, farbe=_farbe(color or c) or farbe,
               strich=_strich(linestyle or ls, strich if fmt else "-"),
               marke=_marke(marker, marke), breite=linewidth or lw,
               groesse=markersize or ms, deckung=alpha, befehl="plot")


def scatter(x: Any, y: Any, s: Optional[float] = None, c: Optional[str] = None, *,
            label: Optional[str] = None, color: Optional[str] = None,
            marker: Optional[str] = None, alpha: Optional[float] = None) -> None:
    """Punkte: ``scatter(x, y)`` -- ``s`` ist die Fläche der Marke wie bei matplotlib."""
    _reihe("punkte", _folge(x, "scatter", "x"), _folge(y, "scatter", "y"), name=label,
           farbe=_farbe(color or c), strich="", marke=_marke(marker, "o"),
           groesse=math.sqrt(s) if s else None, deckung=alpha, befehl="scatter")


def bar(x: Any, height: Any, width: float = 0.8, *, label: Optional[str] = None,
        color: Optional[str] = None, alpha: Optional[float] = None) -> None:
    """Balken: ``bar(["A", "B"], [3, 5])`` -- die Stellen dürfen auch Namen sein."""
    _reihe("balken", _folge(x, "bar", "x"), _folge(height, "bar", "height"), name=label,
           farbe=_farbe(color), strich="", marke="", breite=width, deckung=alpha, befehl="bar")


def axhline(y: float = 0.0, *, color: Optional[str] = None,
            linestyle: Optional[str] = None, ls: Optional[str] = None) -> None:
    """Eine waagrechte Linie über das ganze Bild."""
    _aktuell.hilfslinien.append({"achse": "y", "wert": _zahl(y, "axhline", "y"),
                                 "farbe": _farbe(color), "strich": _strich(linestyle or ls, "-")})


def axvline(x: float = 0.0, *, color: Optional[str] = None,
            linestyle: Optional[str] = None, ls: Optional[str] = None) -> None:
    """Eine senkrechte Linie über das ganze Bild."""
    _aktuell.hilfslinien.append({"achse": "x", "wert": _zahl(x, "axvline", "x"),
                                 "farbe": _farbe(color), "strich": _strich(linestyle or ls, "-")})


# ===========================================================================
# Beschriftung
# ===========================================================================


def title(text: str, **_kwargs: Any) -> None:
    _aktuell.titel = str(text)


def xlabel(text: str, **_kwargs: Any) -> None:
    _aktuell.xlabel = str(text)


def ylabel(text: str, **_kwargs: Any) -> None:
    _aktuell.ylabel = str(text)


def legend(*_args: Any, **_kwargs: Any) -> None:
    """Zeigt die Legende -- mit den Namen aus ``label=``."""
    _aktuell.legende = True


def grid(sichtbar: bool = True, **_kwargs: Any) -> None:
    _aktuell.gitter = bool(sichtbar)


def xlim(*grenzen: Any, left: Any = None, right: Any = None) -> None:
    """``xlim(0, 10)`` oder ``xlim((0, 10))`` -- eine Grenze ``None`` bleibt frei."""
    _aktuell.xbereich = _bereich(grenzen, left, right, "xlim")


def ylim(*grenzen: Any, bottom: Any = None, top: Any = None) -> None:
    _aktuell.ybereich = _bereich(grenzen, bottom, top, "ylim")


# ===========================================================================
# Hilfen
# ===========================================================================


def _paare(args: Sequence[Any], befehl: str) -> Iterable[tuple]:
    """Die Argumente von ``plot`` in Paare (x, y, Format) zerlegt."""
    rest = list(args)
    if not rest:
        raise TypeError(f"{befehl}() braucht mindestens die y-Werte.")
    while rest:
        erstes = rest.pop(0)
        if rest and not isinstance(rest[0], str):
            x, y = _folge(erstes, befehl, "x"), _folge(rest.pop(0), befehl, "y")
        else:
            y = _folge(erstes, befehl, "y")
            x = list(range(len(y)))
        fmt = rest.pop(0) if rest and isinstance(rest[0], str) else ""
        yield x, y, fmt


def _format(fmt: str) -> tuple:
    """``"r--o"`` → (rot, ``--``, ``o``) -- wie die Formatkürzel von matplotlib."""
    farbe = strich = marke = None
    rest = fmt
    for zeichen in ("--", "-.", "-", ":"):
        if zeichen in rest:
            strich, rest = zeichen, rest.replace(zeichen, "", 1)
            break
    for zeichen in rest:
        if zeichen in FARBKUERZEL and farbe is None:
            farbe = FARBKUERZEL[zeichen]
        elif zeichen in MARKEN and marke is None:
            marke = zeichen
        else:
            raise ValueError(f"Das Formatzeichen '{zeichen}' in '{fmt}' kenne ich nicht.")
    # Nur eine Marke, keine Linie: «o» zeichnet Punkte ohne Verbindung.
    if fmt and strich is None:
        strich = "" if marke else "-"
    return farbe, strich, marke


def _strich(wunsch: Optional[str], vorgabe: Optional[str]) -> str:
    if wunsch is None:
        return vorgabe or ""
    if wunsch not in STRICHE:
        raise ValueError(f"Die Linienart '{wunsch}' kenne ich nicht "
                         f"(möglich: '-', '--', ':', '-.').")
    return STRICHE[wunsch]


def _marke(wunsch: Optional[str], vorgabe: Optional[str]) -> str:
    if wunsch is None:
        return vorgabe or ""
    if wunsch in ("", "None", "none"):
        return ""
    if wunsch not in MARKEN:
        raise ValueError(f"Die Marke '{wunsch}' kenne ich nicht "
                         f"(möglich: {', '.join(MARKEN)}).")
    return wunsch


def _reihe(art: str, x: List[Any], y: List[Any], *, befehl: str, **eigenschaften: Any) -> None:
    if len(x) != len(y):
        raise ValueError(f"{befehl}(): x hat {len(x)} Werte, y hat {len(y)}.")
    if any(isinstance(v, str) for v in x):
        x = _als_kategorien(x, befehl)
    else:
        x = [_zahl_oder_luecke(v, befehl, "x") for v in x]
    y = [_zahl_oder_luecke(v, befehl, "y") for v in y]
    _aktuell.reihen.append({"art": art, "x": x, "y": y,
                            **{k: v for k, v in eigenschaften.items() if v is not None}})


def _als_kategorien(werte: List[Any], befehl: str) -> List[float]:
    """Namen statt Zahlen: jede Kategorie bekommt ihre Stelle, alle Reihen dieselbe."""
    if _aktuell.kategorien is None:
        _aktuell.kategorien = []
    stellen = []
    for v in werte:
        if not isinstance(v, str):
            raise TypeError(f"{befehl}(): x mischt Namen und Zahlen.")
        if v not in _aktuell.kategorien:
            _aktuell.kategorien.append(v)
        stellen.append(float(_aktuell.kategorien.index(v)))
    return stellen


def _folge(werte: Any, befehl: str, name: str) -> List[Any]:
    """Eine Liste aus dem, was kommt: Liste, Tupel, range, numpy, pandas, Generator."""
    if hasattr(werte, "tolist"):
        werte = werte.tolist()
    if isinstance(werte, (str, bytes)) or not hasattr(werte, "__iter__"):
        raise TypeError(f"{befehl}(): {name} muss eine Folge von Werten sein, "
                        f"nicht {type(werte).__name__}.")
    return list(werte)


def _zahl(v: Any, befehl: str, name: str) -> float:
    """Eine endliche Zahl -- unendlich liesse sich nicht zeichnen."""
    zahl = _roh(v, befehl, name)
    if not math.isfinite(zahl):
        raise ValueError(f"{befehl}(): {name} muss endlich sein, nicht {v!r}.")
    return zahl


def _roh(v: Any, befehl: str, name: str) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        raise TypeError(f"{befehl}(): {name} muss eine Zahl sein, nicht {v!r}.") from None


def _zahl_oder_luecke(v: Any, befehl: str, name: str) -> Optional[float]:
    """Eine Zahl -- ``None``, ``nan`` und unendlich werden eine Lücke, wie bei matplotlib."""
    if v is None:
        return None
    zahl = _roh(v, befehl, name)
    return zahl if math.isfinite(zahl) else None


def _farbe(wert: Any) -> Optional[str]:
    """Eine Farbe für SVG: Name oder ``#rrggbb`` bleiben, ``(r, g, b)`` in Anteilen wird ``rgb(…)``."""
    if wert is None or isinstance(wert, str):
        return FARBKUERZEL.get(wert, wert) if wert else None
    try:
        anteile = [float(a) for a in wert]
    except (TypeError, ValueError):
        raise TypeError(f"Eine Farbe ist ein Name, «#rrggbb» oder (r, g, b), nicht {wert!r}.") from None
    if len(anteile) not in (3, 4) or not all(0.0 <= a <= 1.0 for a in anteile):
        raise ValueError(f"Eine Farbe als Tupel hat drei oder vier Anteile zwischen 0 und 1: {wert!r}.")
    r, g, b = (round(a * 255) for a in anteile[:3])
    return f"rgb({r}, {g}, {b})"


def _bereich(grenzen: Sequence[Any], unten: Any, oben: Any, befehl: str) -> List[Any]:
    if len(grenzen) == 1 and hasattr(grenzen[0], "__iter__"):
        grenzen = tuple(grenzen[0])
    if len(grenzen) == 2:
        unten, oben = grenzen
    elif grenzen:
        raise TypeError(f"{befehl}() braucht zwei Grenzen.")
    return [None if g is None else _zahl(g, befehl, "Grenze") for g in (unten, oben)]
