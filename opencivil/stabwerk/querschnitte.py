"""
opencivil/stabwerk/querschnitte.py -- die Querschnitte der Staebe, nach Vorlage.

VERANTWORTUNG:
Was ein Stab von seinem Querschnitt braucht: die Flaeche ``A``, die
Flaechentraegheitsmomente ``I_y`` um die waagrechte und ``I_z`` um die
senkrechte Achse durch den Schwerpunkt und das Torsionstraegheitsmoment
``I_T``. Je Vorlage stehen die Formeln hier -- als Vorlage in Zeichen und als
Rechnung --, und aus ihnen entstehen im Rechenwerk die Formeln mit Zahlen
(:mod:`opencivil.stabwerk.rechnung`). Der ebene Rahmen nimmt davon ``A`` und
``I_y``, das Stabwerk im Raum alle vier; gerechnet wird nur, was einer
braucht.

DIE VORLAGEN:
Rechteck, Kreis, Kreisring, Rechteckrohr, T-Querschnitt (Flansch oben),
Doppel-T und Trapez. Jede ist symmetrisch zur senkrechten Achse ``z``;
``h`` ist die Hoehe, entlang ``z``, ``b`` die Breite, entlang ``y``. Die
Seiten der Formeln heissen wie bei den Stahlprofilen
(:mod:`opencivil.stabwerk.profilformen`) -- nur die von ``I_y`` ohne «um y»:
so hiessen sie, bevor es ``I_z`` gab.

Daneben: Kennwerte von Hand, der Streifen einer Platte (``b × h``, mit den
Formeln des Rechtecks) und der Bruttoquerschnitt einer Querschnittsanalyse
(``A`` und ``I_y``). Das waehlt die Beschreibung
(:mod:`opencivil.projekt.balkensystem`), je Art eine Klasse rechnet es
(:mod:`opencivil.stabwerk.stabquerschnitt`); hier stehen nur die Formeln.

TORSION -- NACH VORGABE, NICHT NACHGESCHLAGEN:
Kreis und Kreisring haben ``I_T = 2 · I_y``, wie jeder Kreisquerschnitt.
Das Rechteckrohr rechnet als duenne Wand: offen und nach Bredt geschlossen,
dieselbe Formel wie beim kaltgefertigten Rohr. Rechteck, T und Doppel-T
zerfallen in Rechtecke, und jedes traegt ``s · t³ · (1/3 - 0.21 · t/s ·
(1 - t⁴/(12 · s⁴)))`` bei, mit ``t`` der kuerzeren und ``s`` der laengeren
Seite -- die Naeherung von Roark, beim Rechteck auf weniger als ein Prozent
genau; die Verbindung von Steg und Flansch zaehlt dabei nicht. Das Trapez
rechnet als Rechteck seiner mittleren Breite. Die Norm regelt nichts davon;
das TODO fuehrt es.

EINHEITEN:
Masse in mm, ``A`` in mm², die Traegheitsmomente in 10⁶ mm⁴ -- wie in der
Querschnittsanalyse.

Die Umrisse von Rechteck, T und Kreis und was an einem T nicht geht, teilen
sich die Vorlagen hier mit denen der Querschnittsanalyse
(:mod:`opencivil.querschnitt.vorlagen`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Dict, List, Mapping, Optional, Tuple

from opencivil.core.einheiten import EINHEITSLOS, MIO_MM4, MM, MM2, Einheit, Groesse
from opencivil.querschnitt.vorlagen import kreispunkte, rechteckpunkte, t_punkte, t_pruefen

Masse = Mapping[str, float]


@dataclass(frozen=True)
class Mass:
    """Ein Mass einer Vorlage -- in mm, wo nicht ``einheit`` anderes sagt."""

    schluessel: str
    symbol: str
    beschriftung: str
    vorgabe: float
    einheit: Einheit = MM


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
    """
    In der Reihenfolge, in der gerechnet wird -- darunter ``A``, ``I_y``,
    ``I_z`` und ``I_T``, bei einer Vorlage wie bei einem Stahlprofil
    (:mod:`opencivil.stabwerk.profilformen`).
    """

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
        einheiten = {m.schluessel: m.einheit for m in self.masse}
        werte: Dict[str, Groesse] = {k: Groesse(v, einheiten.get(k, MM))
                                     for k, v in masse.items()}
        for f in self.formeln:
            werte[f.kurzname] = f.funktion(**{n: werte[n] for n in _namen(f.vorlage)})
        return werte


def _namen(vorlage: str) -> List[str]:
    # Erst hier: core.latex laedt beim Import nichts von hier, aber so bleibt
    # die Abhaengigkeit an der einen Stelle, die sie braucht.
    from opencivil.core.latex import platzhalter_namen
    return platzhalter_namen(vorlage)


#: Eins ohne Einheit -- fuer ``1 - x`` mit Groessen.
EINS = Groesse(1.0, EINHEITSLOS)

#: Was ein Rechteck zum Torsionstraegheitsmoment beitraegt, mit der kuerzeren
#: Seite ``t`` und der laengeren ``s`` -- die Naeherung von Roark (Dateikopf).
RECHTECKTORSION = (
    r"@s \cdot \left(@t\right)^{3} \cdot \left(\frac{1}{3} - 0.21 \cdot \frac{@t}{@s} \cdot "
    r"\left(1 - \frac{\left(@t\right)^{4}}{12 \cdot \left(@s\right)^{4}}\right)\right)")

#: Das Torsionstraegheitsmoment eines Rechteckrohrs: offen und geschlossen
#: (Bredt), mit dem Umfang ``p_m`` und der umschlossenen Flaeche ``A_m`` der
#: Mittellinie -- auch beim kaltgefertigten Rohr (:mod:`~opencivil.stabwerk.profilformen`).
ROHRTORSION = (
    r"\frac{\left(@t\right)^{3} \cdot @p_m}{3} + \frac{4 \cdot \left(@A_m\right)^{2} \cdot @t}"
    r"{@p_m}",
    lambda t, p_m, A_m: t ** 3 * p_m / 3 + 4 * A_m ** 2 * t / p_m)


def rechtecktorsion(t: Groesse, s: Groesse) -> Groesse:
    """:data:`RECHTECKTORSION` als Rechnung."""
    return s * t ** 3 * (EINS / 3 - 0.21 * t / s * (EINS - t ** 4 / (12 * s ** 4)))


def _flaeche(name: str, vorlage: str, funktion) -> Kennformel:
    return Kennformel("A", "A", MM2, 0, "Querschnittsfläche", vorlage, funktion,
                      f"Fläche eines {name}")


def _iy(name: str, vorlage: str, funktion) -> Kennformel:
    return Kennformel("I_y", "I_y", MIO_MM4, 2, "Flächenträgheitsmoment um y", vorlage, funktion,
                      f"Flächenträgheitsmoment eines {name}")


def _iz(name: str, vorlage: str, funktion) -> Kennformel:
    return Kennformel("I_z", "I_z", MIO_MM4, 2, "Flächenträgheitsmoment um z", vorlage, funktion,
                      f"Flächenträgheitsmoment eines {name} um z")


def _it(name: str, vorlage: str, funktion) -> Kennformel:
    return Kennformel("I_T", "I_T", MIO_MM4, 2, "Torsionsträgheitsmoment", vorlage, funktion,
                      f"Torsionsträgheitsmoment eines {name}")


Seite = Tuple[str, Callable[[Mapping[str, Groesse]], Groesse]]


def _seiten(name: str, teil: str, nummer: str, a: Seite, b: Seite) -> Tuple[Kennformel, ...]:
    """
    Die kuerzere Seite ``t`` und die laengere ``s`` eines Rechtecks mit den
    Seiten ``a`` und ``b`` -- je in Zeichen (mit ``@``) und als Rechnung aus
    den Werten. ``teil`` sagt, welches Rechteck: «des Flanschs»; ``nummer``
    haengt am Zeichen.
    """
    (za, ra), (zb, rb) = a, b
    wo = f" {teil}" if teil else ""
    return tuple(
        Kennformel(f"{zeichen}{nummer}", f"{zeichen}{nummer}", MM, 1, f"{wort} Seite{wo}",
                   rf"\{wahl.__name__}\left({za}, {zb}\right)",
                   lambda wahl=wahl, **m: wahl(ra(m), rb(m)), f"{wort} Seite{wo} eines {name}")
        for zeichen, wort, wahl in (("t", "Kürzere", min), ("s", "Längere", max)))


def _torsion(name: str, teile: Tuple[Tuple[int, str], ...]) -> Kennformel:
    """
    ``I_T`` aus Rechtecken, je mit ``t`` und ``s`` und der Nummer daran --
    ``(2, "_1")`` heisst zweimal das Rechteck mit ``t_1`` und ``s_1``.
    """
    def glied(anzahl: int, nummer: str) -> str:
        vorlage = RECHTECKTORSION.replace("@t", f"@t{nummer}").replace("@s", f"@s{nummer}")
        return f"{anzahl} \\cdot {vorlage}" if anzahl > 1 else vorlage

    def funktion(**m: Groesse) -> Groesse:
        glieder = [anzahl * rechtecktorsion(m[f"t{nummer}"], m[f"s{nummer}"])
                   for anzahl, nummer in teile]
        return sum(glieder[1:], glieder[0])

    return _it(name, " + ".join(glied(*teil) for teil in teile), funktion)


def _wie_um_y(name: str) -> Tuple[Kennformel, Kennformel]:
    """``I_z`` und ``I_T`` eines Kreisquerschnitts: um jede Achse dasselbe, polar das Doppelte."""
    return (_iz(name, "@I_y", lambda I_y: I_y),
            _it(name, r"2 \cdot @I_y", lambda I_y: 2 * I_y))


#: Rechteck: b breit, h hoch.
RECHTECK = Stabvorlage(
    schluessel="rechteck", name="Rechteck",
    masse=(Mass("b", "b", "Breite", 300.0), Mass("h", "h", "Höhe", 600.0)),
    formeln=(
        _flaeche("Rechtecks", r"@b \cdot @h", lambda b, h: b * h),
        _iy("Rechtecks", r"\frac{@b \cdot \left(@h\right)^{3}}{12}",
            lambda b, h: b * h ** 3 / 12.0),
        _iz("Rechtecks", r"\frac{@h \cdot \left(@b\right)^{3}}{12}",
            lambda b, h: h * b ** 3 / 12.0),
        *_seiten("Rechtecks", "", "", ("@b", lambda m: m["b"]), ("@h", lambda m: m["h"])),
        _torsion("Rechtecks", ((1, ""),)),
    ),
    pruefung=lambda m: None,
    umriss=lambda m: [rechteckpunkte(m["b"], m["h"])],
)

#: Kreis: Durchmesser d.
KREIS = Stabvorlage(
    schluessel="kreis", name="Kreis",
    masse=(Mass("d", "d", "Durchmesser", 400.0),),
    formeln=(
        _flaeche("Kreises", r"\frac{\pi \cdot \left(@d\right)^{2}}{4}",
                 lambda d: math.pi * d ** 2 / 4.0),
        _iy("Kreises", r"\frac{\pi \cdot \left(@d\right)^{4}}{64}",
            lambda d: math.pi * d ** 4 / 64.0),
        *_wie_um_y("Kreises"),
    ),
    pruefung=lambda m: None,
    umriss=lambda m: [kreispunkte((m["d"] / 2, m["d"] / 2), m["d"] / 2)],
)

#: Kreisring: aussen D, Wand t.
KREISRING = Stabvorlage(
    schluessel="kreisring", name="Kreisring",
    masse=(Mass("D", "D", "Aussendurchmesser", 300.0), Mass("t", "t", "Wanddicke", 20.0)),
    formeln=(
        _flaeche("Kreisrings",
                 r"\frac{\pi \cdot \left(\left(@D\right)^{2} - \left(@D - 2 \cdot @t\right)^{2}\right)}{4}",
                 lambda D, t: math.pi * (D ** 2 - (D - 2.0 * t) ** 2) / 4.0),
        _iy("Kreisrings",
            r"\frac{\pi \cdot \left(\left(@D\right)^{4} - \left(@D - 2 \cdot @t\right)^{4}\right)}{64}",
            lambda D, t: math.pi * (D ** 4 - (D - 2.0 * t) ** 4) / 64.0),
        *_wie_um_y("Kreisrings"),
    ),
    pruefung=lambda m: (None if 2.0 * m["t"] < m["D"]
                        else "Die Wand t ist zu dick: 2·t muss kleiner als D sein."),
    umriss=lambda m: [kreispunkte((m["D"] / 2, m["D"] / 2), m["D"] / 2),
                      kreispunkte((m["D"] / 2, m["D"] / 2), m["D"] / 2 - m["t"])],
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
        _iy("Rechteckrohrs",
            r"\frac{@b \cdot \left(@h\right)^{3} - \left(@b - 2 \cdot @t\right) \cdot "
            r"\left(@h - 2 \cdot @t\right)^{3}}{12}",
            lambda b, h, t: (b * h ** 3 - (b - 2.0 * t) * (h - 2.0 * t) ** 3) / 12.0),
        _iz("Rechteckrohrs",
            r"\frac{@h \cdot \left(@b\right)^{3} - \left(@h - 2 \cdot @t\right) \cdot "
            r"\left(@b - 2 \cdot @t\right)^{3}}{12}",
            lambda b, h, t: (h * b ** 3 - (h - 2.0 * t) * (b - 2.0 * t) ** 3) / 12.0),
        Kennformel("p_m", "p_m", MM, 1, "Umfang der Mittellinie",
                   r"2 \cdot \left(@b + @h - 2 \cdot @t\right)",
                   lambda b, h, t: 2 * (b + h - 2 * t), "Umfang der Mittellinie eines Rechteckrohrs"),
        Kennformel("A_m", "A_m", MM2, 0, "von der Mittellinie umschlossene Fläche",
                   r"\left(@b - @t\right) \cdot \left(@h - @t\right)",
                   lambda b, h, t: (b - t) * (h - t), "Umschlossene Fläche eines Rechteckrohrs"),
        _it("Rechteckrohrs", *ROHRTORSION),
    ),
    pruefung=lambda m: (None if 2.0 * m["t"] < min(m["b"], m["h"])
                        else "Die Wand t ist zu dick: 2·t muss kleiner als b und h sein."),
    umriss=lambda m: [rechteckpunkte(m["b"], m["h"]),
                      rechteckpunkte(m["b"] - 2 * m["t"], m["h"] - 2 * m["t"], m["t"], m["t"])],
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
        _iy(
            "T-Querschnitts",
            r"\frac{@b \cdot \left(@h_f\right)^{3}}{12} + @b \cdot @h_f \cdot "
            r"\left(@z_S - \frac{@h_f}{2}\right)^{2} + \frac{@b_w \cdot \left(@h - @h_f\right)^{3}}{12}"
            r" + @b_w \cdot \left(@h - @h_f\right) \cdot \left(\frac{@h + @h_f}{2} - @z_S\right)^{2}",
            lambda b, h, b_w, h_f, z_S: (b * h_f ** 3 / 12.0 + b * h_f * (z_S - h_f / 2.0) ** 2
                                         + b_w * (h - h_f) ** 3 / 12.0
                                         + b_w * (h - h_f) * ((h + h_f) / 2.0 - z_S) ** 2)),
        _iz("T-Querschnitts",
            r"\frac{@h_f \cdot \left(@b\right)^{3} + \left(@h - @h_f\right) \cdot "
            r"\left(@b_w\right)^{3}}{12}",
            lambda b, h, b_w, h_f: (h_f * b ** 3 + (h - h_f) * b_w ** 3) / 12.0),
        *_seiten("T-Querschnitts", "des Flanschs", "_1",
                 ("@b", lambda m: m["b"]), ("@h_f", lambda m: m["h_f"])),
        *_seiten("T-Querschnitts", "des Stegs", "_2",
                 ("@b_w", lambda m: m["b_w"]), ("@h - @h_f", lambda m: m["h"] - m["h_f"])),
        _torsion("T-Querschnitts", ((1, "_1"), (1, "_2"))),
    ),
    pruefung=lambda m: t_pruefen(m["b"], m["h"], m["b_w"], m["h_f"]),
    umriss=lambda m: [t_punkte(m["b"], m["h"], m["b_w"], m["h_f"])],
)

#: Doppel-T, symmetrisch: b breit, h hoch, Flansche t_f, Steg t_w.
DOPPEL_T = Stabvorlage(
    schluessel="doppel_t", name="Doppel-T",
    masse=(Mass("b", "b", "Flanschbreite", 200.0), Mass("h", "h", "Höhe", 400.0),
           Mass("t_f", "t_f", "Flanschdicke", 16.0), Mass("t_w", "t_w", "Stegdicke", 9.0)),
    formeln=(
        _flaeche("Doppel-T-Querschnitts",
                 r"2 \cdot @b \cdot @t_f + @t_w \cdot \left(@h - 2 \cdot @t_f\right)",
                 lambda b, h, t_f, t_w: 2.0 * b * t_f + t_w * (h - 2.0 * t_f)),
        _iy("Doppel-T-Querschnitts",
            r"\frac{@b \cdot \left(@h\right)^{3} - \left(@b - @t_w\right) \cdot "
            r"\left(@h - 2 \cdot @t_f\right)^{3}}{12}",
            lambda b, h, t_f, t_w: (b * h ** 3 - (b - t_w) * (h - 2.0 * t_f) ** 3) / 12.0),
        _iz("Doppel-T-Querschnitts",
            r"\frac{2 \cdot @t_f \cdot \left(@b\right)^{3} + \left(@h - 2 \cdot @t_f\right) \cdot "
            r"\left(@t_w\right)^{3}}{12}",
            lambda b, h, t_f, t_w: (2.0 * t_f * b ** 3 + (h - 2.0 * t_f) * t_w ** 3) / 12.0),
        *_seiten("Doppel-T-Querschnitts", "eines Flanschs", "_1",
                 ("@b", lambda m: m["b"]), ("@t_f", lambda m: m["t_f"])),
        *_seiten("Doppel-T-Querschnitts", "des Stegs", "_2",
                 ("@t_w", lambda m: m["t_w"]),
                 (r"@h - 2 \cdot @t_f", lambda m: m["h"] - 2 * m["t_f"])),
        _torsion("Doppel-T-Querschnitts", ((2, "_1"), (1, "_2"))),
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
        _iy("Trapezes",
            r"\frac{\left(@h\right)^{3} \cdot \left(\left(@b_o\right)^{2} + 4 \cdot @b_o \cdot @b_u"
            r" + \left(@b_u\right)^{2}\right)}{36 \cdot \left(@b_o + @b_u\right)}",
            lambda b_o, b_u, h: h ** 3 * (b_o ** 2 + 4.0 * b_o * b_u + b_u ** 2)
            / (36.0 * (b_o + b_u))),
        _iz("Trapezes",
            r"\frac{@h \cdot \left(@b_o + @b_u\right) \cdot \left(\left(@b_o\right)^{2} + "
            r"\left(@b_u\right)^{2}\right)}{48}",
            lambda b_o, b_u, h: h * (b_o + b_u) * (b_o ** 2 + b_u ** 2) / 48.0),
        Kennformel("b_m", "b_m", MM, 1, "Mittlere Breite", r"\frac{@b_o + @b_u}{2}",
                   lambda b_o, b_u: (b_o + b_u) / 2, "Mittlere Breite eines Trapezes"),
        *_seiten("Trapezes", "", "", ("@b_m", lambda m: m["b_m"]), ("@h", lambda m: m["h"])),
        _torsion("Trapezes", ((1, ""),)),
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
