"""
opencivil/stabwerk/querschnitte.py -- die Querschnitte der Staebe, nach Vorlage.

VERANTWORTUNG:
Was ein Stab des ebenen Rahmens von seinem Querschnitt braucht: die Flaeche
``A`` und das Flaechentraegheitsmoment ``I`` um die Achse senkrecht zur
Ebene des Rahmens. Je Vorlage stehen die Formeln hier -- als Vorlage in
Zeichen und als Rechnung --, und aus ihnen entstehen im Rechenwerk die
Formeln mit Zahlen (:mod:`opencivil.stabwerk.rechnung`).

DIE VORLAGEN:
Rechteck, Kreis, Kreisring, Rechteckrohr, T-Querschnitt (Flansch oben),
Doppel-T und Trapez. Jede ist symmetrisch zur Ebene des Rahmens, damit die
Biegung in ihr bleibt. Gebogen wird um die waagrechte Achse durch den
Schwerpunkt; ``h`` ist die Hoehe in der Ebene des Rahmens.

Daneben: Kennwerte von Hand, der Streifen einer Platte (``b × h``, mit den
Formeln des Rechtecks) und der Bruttoquerschnitt einer Querschnittsanalyse
(``A`` und ``I_y``). Das waehlt die Beschreibung
(:mod:`opencivil.projekt.balkensystem`); hier stehen nur die Formeln.

EINHEITEN:
Masse in mm, ``A`` in mm², ``I`` in 10⁶ mm⁴ -- wie in der Querschnittsanalyse.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.einheiten import MIO_MM4, MM, MM2, Einheit, Groesse

Masse = Mapping[str, float]


@dataclass(frozen=True)
class Mass:
    """Ein Mass einer Vorlage -- in mm."""

    schluessel: str
    symbol: str
    beschriftung: str
    vorgabe: float


@dataclass(frozen=True)
class Kennformel:
    """
    Eine Formel einer Vorlage: was sie liefert, ihre Vorlage in Zeichen
    (``@name`` fuer ein Mass oder einen frueheren Kennwert) und die Rechnung
    dazu, mit Groessen.
    """

    kurzname: str
    symbol: str
    einheit: Einheit
    stellen: int
    beschreibung: str
    vorlage: str
    funktion: Callable[..., Groesse]
    name: str
    """Die Seite im Notizbuch."""


@dataclass(frozen=True)
class Stabvorlage:
    schluessel: str
    name: str
    masse: Tuple[Mass, ...]
    formeln: Tuple[Kennformel, ...]
    """In der Reihenfolge, in der gerechnet wird -- am Ende ``A`` und ``I``."""

    pruefung: Callable[[Masse], Optional[str]]
    umriss: Callable[[Masse], List[List[Tuple[float, float]]]]
    """Die Umrisse fuer das Bild, in mm -- der erste aussen, die weiteren Loecher."""

    def vorgaben(self) -> Dict[str, float]:
        return {m.schluessel: m.vorgabe for m in self.masse}

    def pruefen(self, masse: Masse) -> Optional[str]:
        """Was an den Massen nicht geht -- ``None``, wenn alles geht."""
        for m in self.masse:
            if masse.get(m.schluessel, 0.0) <= 0.0:
                return f"{m.beschriftung} {m.symbol} muss grösser als null sein."
        return self.pruefung(masse)

    def kennwerte(self, masse: Masse) -> Dict[str, Groesse]:
        """Alle Kennwerte, der Reihe nach gerechnet -- ohne Herleitung."""
        werte: Dict[str, Groesse] = {k: Groesse(v, MM) for k, v in masse.items()}
        for f in self.formeln:
            werte[f.kurzname] = f.funktion(**{n: werte[n] for n in _namen(f.vorlage)})
        return werte


def _namen(vorlage: str) -> List[str]:
    # Erst hier: core.latex laedt beim Import nichts von hier, aber so bleibt
    # die Abhaengigkeit an der einen Stelle, die sie braucht.
    from opencivil.core.latex import platzhalter_namen
    return platzhalter_namen(vorlage)


def _rechteck(b: float, h: float, x: float = 0.0, z: float = 0.0) -> List[Tuple[float, float]]:
    return [(x, z), (x + b, z), (x + b, z + h), (x, z + h)]


def _kreis(d: float, mitte: Tuple[float, float], ecken: int = 48) -> List[Tuple[float, float]]:
    r = d / 2.0
    return [(mitte[0] + r * math.cos(2 * math.pi * i / ecken),
             mitte[1] + r * math.sin(2 * math.pi * i / ecken)) for i in range(ecken)]


def _flaeche(name: str, vorlage: str, funktion) -> Kennformel:
    return Kennformel("A", "A", MM2, 0, "Querschnittsfläche", vorlage, funktion,
                      f"Fläche eines {name}")


def _traegheit(name: str, vorlage: str, funktion) -> Kennformel:
    return Kennformel("I", "I", MIO_MM4, 2, "Flächenträgheitsmoment", vorlage, funktion,
                      f"Flächenträgheitsmoment eines {name}")


#: Rechteck: b breit, h hoch.
RECHTECK = Stabvorlage(
    schluessel="rechteck", name="Rechteck",
    masse=(Mass("b", "b", "Breite", 300.0), Mass("h", "h", "Höhe", 600.0)),
    formeln=(
        _flaeche("Rechtecks", r"@b \cdot @h", lambda b, h: b * h),
        _traegheit("Rechtecks", r"\frac{@b \cdot \left(@h\right)^{3}}{12}",
                   lambda b, h: b * h ** 3 / 12.0),
    ),
    pruefung=lambda m: None,
    umriss=lambda m: [_rechteck(m["b"], m["h"])],
)

#: Kreis: Durchmesser d.
KREIS = Stabvorlage(
    schluessel="kreis", name="Kreis",
    masse=(Mass("d", "d", "Durchmesser", 400.0),),
    formeln=(
        _flaeche("Kreises", r"\frac{\pi \cdot \left(@d\right)^{2}}{4}",
                 lambda d: math.pi * d ** 2 / 4.0),
        _traegheit("Kreises", r"\frac{\pi \cdot \left(@d\right)^{4}}{64}",
                   lambda d: math.pi * d ** 4 / 64.0),
    ),
    pruefung=lambda m: None,
    umriss=lambda m: [_kreis(m["d"], (m["d"] / 2, m["d"] / 2))],
)

#: Kreisring: aussen D, Wand t.
KREISRING = Stabvorlage(
    schluessel="kreisring", name="Kreisring",
    masse=(Mass("D", "D", "Aussendurchmesser", 300.0), Mass("t", "t", "Wanddicke", 20.0)),
    formeln=(
        _flaeche("Kreisrings",
                 r"\frac{\pi \cdot \left(\left(@D\right)^{2} - \left(@D - 2 \cdot @t\right)^{2}\right)}{4}",
                 lambda D, t: math.pi * (D ** 2 - (D - 2.0 * t) ** 2) / 4.0),
        _traegheit("Kreisrings",
                   r"\frac{\pi \cdot \left(\left(@D\right)^{4} - \left(@D - 2 \cdot @t\right)^{4}\right)}{64}",
                   lambda D, t: math.pi * (D ** 4 - (D - 2.0 * t) ** 4) / 64.0),
    ),
    pruefung=lambda m: (None if 2.0 * m["t"] < m["D"]
                        else "Die Wand t ist zu dick: 2·t muss kleiner als D sein."),
    umriss=lambda m: [_kreis(m["D"], (m["D"] / 2, m["D"] / 2)),
                      _kreis(m["D"] - 2 * m["t"], (m["D"] / 2, m["D"] / 2))],
)

#: Rechteckrohr: b breit, h hoch, Wand t ringsum.
RECHTECKROHR = Stabvorlage(
    schluessel="rechteckrohr", name="Rechteckrohr",
    masse=(Mass("b", "b", "Breite", 200.0), Mass("h", "h", "Höhe", 300.0),
           Mass("t", "t", "Wanddicke", 12.0)),
    formeln=(
        _flaeche("Rechteckrohrs",
                 r"@b \cdot @h - \left(@b - 2 \cdot @t\right) \cdot \left(@h - 2 \cdot @t\right)",
                 lambda b, h, t: b * h - (b - 2.0 * t) * (h - 2.0 * t)),
        _traegheit("Rechteckrohrs",
                   r"\frac{@b \cdot \left(@h\right)^{3} - \left(@b - 2 \cdot @t\right) \cdot "
                   r"\left(@h - 2 \cdot @t\right)^{3}}{12}",
                   lambda b, h, t: (b * h ** 3 - (b - 2.0 * t) * (h - 2.0 * t) ** 3) / 12.0),
    ),
    pruefung=lambda m: (None if 2.0 * m["t"] < min(m["b"], m["h"])
                        else "Die Wand t ist zu dick: 2·t muss kleiner als b und h sein."),
    umriss=lambda m: [_rechteck(m["b"], m["h"]),
                      _rechteck(m["b"] - 2 * m["t"], m["h"] - 2 * m["t"], m["t"], m["t"])],
)

#: T-Querschnitt, Flansch oben: b breit, h hoch, Steg b_w, Flansch h_f.
T_QUERSCHNITT = Stabvorlage(
    schluessel="t", name="T-Querschnitt",
    masse=(Mass("b", "b", "Flanschbreite", 1000.0), Mass("h", "h", "Höhe", 600.0),
           Mass("b_w", "b_w", "Stegbreite", 300.0), Mass("h_f", "h_f", "Flanschdicke", 200.0)),
    formeln=(
        _flaeche("T-Querschnitts", r"@b \cdot @h_f + @b_w \cdot \left(@h - @h_f\right)",
                 lambda b, h, b_w, h_f: b * h_f + b_w * (h - h_f)),
        Kennformel(
            "z_S", "z_S", MM, 1, "Abstand des Schwerpunkts vom oberen Rand",
            r"\frac{@b \cdot \left(@h_f\right)^{2} / 2 + @b_w \cdot \left(@h - @h_f\right) \cdot "
            r"\left(@h + @h_f\right) / 2}{@A}",
            lambda b, h, b_w, h_f, A: (b * h_f ** 2 / 2.0 + b_w * (h - h_f) * (h + h_f) / 2.0) / A,
            "Schwerpunkt eines T-Querschnitts"),
        _traegheit(
            "T-Querschnitts",
            r"\frac{@b \cdot \left(@h_f\right)^{3}}{12} + @b \cdot @h_f \cdot "
            r"\left(@z_S - \frac{@h_f}{2}\right)^{2} + \frac{@b_w \cdot \left(@h - @h_f\right)^{3}}{12}"
            r" + @b_w \cdot \left(@h - @h_f\right) \cdot \left(\frac{@h + @h_f}{2} - @z_S\right)^{2}",
            lambda b, h, b_w, h_f, z_S: (b * h_f ** 3 / 12.0 + b * h_f * (z_S - h_f / 2.0) ** 2
                                         + b_w * (h - h_f) ** 3 / 12.0
                                         + b_w * (h - h_f) * ((h + h_f) / 2.0 - z_S) ** 2)),
    ),
    pruefung=lambda m: (
        "Der Steg b_w ist breiter als der Flansch b." if m["b_w"] > m["b"]
        else "Der Flansch h_f muss dünner sein als die Höhe h." if m["h_f"] >= m["h"]
        else None),
    umriss=lambda m: [[((m["b"] - m["b_w"]) / 2, 0.0), ((m["b"] + m["b_w"]) / 2, 0.0),
                       ((m["b"] + m["b_w"]) / 2, m["h"] - m["h_f"]), (m["b"], m["h"] - m["h_f"]),
                       (m["b"], m["h"]), (0.0, m["h"]), (0.0, m["h"] - m["h_f"]),
                       ((m["b"] - m["b_w"]) / 2, m["h"] - m["h_f"])]],
)

#: Doppel-T, symmetrisch: b breit, h hoch, Flansche t_f, Steg t_w.
DOPPEL_T = Stabvorlage(
    schluessel="doppel_t", name="Doppel-T",
    masse=(Mass("b", "b", "Flanschbreite", 200.0), Mass("h", "h", "Höhe", 400.0),
           Mass("t_f", "t_f", "Flanschdicke", 16.0), Mass("t_w", "t_w", "Stegdicke", 9.0)),
    formeln=(
        _flaeche("Doppel-T",
                 r"2 \cdot @b \cdot @t_f + @t_w \cdot \left(@h - 2 \cdot @t_f\right)",
                 lambda b, h, t_f, t_w: 2.0 * b * t_f + t_w * (h - 2.0 * t_f)),
        _traegheit("Doppel-T",
                   r"\frac{@b \cdot \left(@h\right)^{3} - \left(@b - @t_w\right) \cdot "
                   r"\left(@h - 2 \cdot @t_f\right)^{3}}{12}",
                   lambda b, h, t_f, t_w: (b * h ** 3 - (b - t_w) * (h - 2.0 * t_f) ** 3) / 12.0),
    ),
    pruefung=lambda m: (
        "Der Steg t_w ist breiter als der Flansch b." if m["t_w"] > m["b"]
        else "Die Flansche sind zusammen dicker als die Höhe h." if 2 * m["t_f"] >= m["h"]
        else None),
    umriss=lambda m: [[(0.0, 0.0), (m["b"], 0.0), (m["b"], m["t_f"]),
                       ((m["b"] + m["t_w"]) / 2, m["t_f"]), ((m["b"] + m["t_w"]) / 2, m["h"] - m["t_f"]),
                       (m["b"], m["h"] - m["t_f"]), (m["b"], m["h"]), (0.0, m["h"]),
                       (0.0, m["h"] - m["t_f"]), ((m["b"] - m["t_w"]) / 2, m["h"] - m["t_f"]),
                       ((m["b"] - m["t_w"]) / 2, m["t_f"]), (0.0, m["t_f"])]],
)

#: Trapez: oben b_o, unten b_u, h hoch.
TRAPEZ = Stabvorlage(
    schluessel="trapez", name="Trapez",
    masse=(Mass("b_o", "b_o", "Breite oben", 400.0), Mass("b_u", "b_u", "Breite unten", 250.0),
           Mass("h", "h", "Höhe", 500.0)),
    formeln=(
        _flaeche("Trapezes", r"\frac{\left(@b_o + @b_u\right) \cdot @h}{2}",
                 lambda b_o, b_u, h: (b_o + b_u) * h / 2.0),
        _traegheit("Trapezes",
                   r"\frac{\left(@h\right)^{3} \cdot \left(\left(@b_o\right)^{2} + 4 \cdot @b_o \cdot @b_u"
                   r" + \left(@b_u\right)^{2}\right)}{36 \cdot \left(@b_o + @b_u\right)}",
                   lambda b_o, b_u, h: h ** 3 * (b_o ** 2 + 4.0 * b_o * b_u + b_u ** 2)
                   / (36.0 * (b_o + b_u))),
    ),
    pruefung=lambda m: None,
    umriss=lambda m: [[((max(m["b_o"], m["b_u"]) - m["b_u"]) / 2, 0.0),
                       ((max(m["b_o"], m["b_u"]) + m["b_u"]) / 2, 0.0),
                       ((max(m["b_o"], m["b_u"]) + m["b_o"]) / 2, m["h"]),
                       ((max(m["b_o"], m["b_u"]) - m["b_o"]) / 2, m["h"])]],
)

VORLAGEN: Tuple[Stabvorlage, ...] = (RECHTECK, KREIS, KREISRING, RECHTECKROHR, T_QUERSCHNITT,
                                     DOPPEL_T, TRAPEZ)


def vorlage(schluessel: str) -> Stabvorlage:
    for v in VORLAGEN:
        if v.schluessel == schluessel:
            return v
    raise KeyError(f"Eine Vorlage «{schluessel}» gibt es nicht. Möglich sind: "
                   f"{', '.join(v.schluessel for v in VORLAGEN)}.")
