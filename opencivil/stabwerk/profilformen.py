"""
opencivil/stabwerk/profilformen.py -- die Formen der Stahlprofile, mit ihren Formeln.

VERANTWORTUNG:
Je Form eines Walzprofils oder Rohrs die Masse und die Formeln fuer ``A``,
``I_y``, ``I_z`` und ``I_T`` -- als Vorlage in Zeichen und als Rechnung, wie
bei den Vorlagen der Stabquerschnitte (:mod:`opencivil.stabwerk.querschnitte`),
deren :class:`Stabvorlage` sie sind. Welche Groessen es gibt, sagt die
Profiltabelle (:mod:`opencivil.stabwerk.profiltabelle`).

DIE FORMEN:
I-Profil (IPE, HEA, HEB, HEM), U-Profil mit parallelen Flanschen (UPE),
U-Profil mit geneigten Flanschen (UNP), kaltgefertigtes Rechteckrohr (RRK)
und Rundrohr (ROR).

ACHSEN:
Das Profil steht: der Steg senkrecht, beim U der Ruecken links. ``y`` ist
die waagrechte Achse durch den Schwerpunkt -- die starke --, ``z`` die
senkrechte. ``e_y`` ist der Abstand des Schwerpunkts vom Ruecken des U.

DIE FORMELN -- nach Vorgabe, nicht nachgeschlagen:
Die Formeln der I- und UPE-Profile und der Rohre sind die der Tabelle des
Benutzers («Festigkeitsnachweise I-Standardprofile Stahl», 2019-04-15), mit
denselben gerundeten Beiwerten der Ausrundungen (:data:`ZWICKEL`). Beim UNP
hat die Tabelle nur Werte, keine Formeln: gerechnet wird mit geneigten
Flanschen als Trapezen und den Ecken wie beim rechten Winkel. Das trifft
die Werte der Tabelle auf 0.6 % (A, I_y) und 1.4 % (e_y, I_z); das I_T des
UNP rechnet wie beim UPE, mit t_f und r_1.

EINHEITEN:
Masse in mm, ``A`` in cm², die Traegheitsmomente in cm⁴ -- wie in der
Tabelle, damit sich vergleichen laesst.
"""

from __future__ import annotations

import math
from dataclasses import replace
from typing import List, Mapping, Sequence, Tuple

from opencivil.core.einheiten import CM2, CM4, EINHEITSLOS, MIO_MM4, MM, MM2, PROZENT, Groesse
from opencivil.querschnitt.vorlagen import Mass
from opencivil.stabwerk.querschnitte import (
    EINS, KREISRING, ROHRTORSION, Kennformel, Stabvorlage,
)

Punkt = Tuple[float, float]

#: Der Zwickel zwischen zwei Kanten im rechten Winkel und einem Viertelkreis
#: mit Radius r, gerundet wie in der Tabelle: Flaeche 0.2146 r² (1 - π/4),
#: Abstand des Schwerpunkts von jeder Kante 0.2234 r ((10 - 3π)/(12 - 3π)),
#: Traegheitsmoment um den eigenen Schwerpunkt 0.00755 r⁴
#: (1/3 - π/16 - 1/(3(12 - 3π))) -- um beide Achsen dasselbe.
ZWICKEL = (0.2146, 0.2234, 0.00755)

#: Je Viertelkreis eines Umrisses so viele Ecken -- fuer das Bild genug.
BOGENECKEN = 6

_RRK = "kaltgefertigten Rechteckrohrs"


# ---------------------------------------------------------------------------
# Bausteine der Formeln
# ---------------------------------------------------------------------------

def _zwickel(r: str, abstand: str) -> str:
    """Ein Zwickel mit Radius ``@r``, um eine Achse im ``abstand`` seines Schwerpunkts."""
    return (rf"0.00755 \cdot \left(@{r}\right)^{{4}} + 0.2146 \cdot \left(@{r}\right)^{{2}} "
            rf"\cdot \left({abstand}\right)^{{2}}")


def _zw(r: Groesse, abstand: Groesse) -> Groesse:
    a, e, i = ZWICKEL
    return i * r ** 4 + a * r ** 2 * abstand ** 2


def _flaeche(form: str, vorlage: str, funktion) -> Kennformel:
    return Kennformel("A", "A", CM2, 2, "Querschnittsfläche", vorlage, funktion,
                      f"Fläche eines {form}")


def _iy(form: str, vorlage: str, funktion) -> Kennformel:
    return Kennformel("I_y", "I_y", CM4, 2, "Flächenträgheitsmoment um y", vorlage, funktion,
                      f"Flächenträgheitsmoment eines {form} um y")


def _iz(form: str, vorlage: str, funktion) -> Kennformel:
    return Kennformel("I_z", "I_z", CM4, 2, "Flächenträgheitsmoment um z", vorlage, funktion,
                      f"Flächenträgheitsmoment eines {form} um z")


def _it(form: str, vorlage: str, funktion) -> Kennformel:
    return Kennformel("I_T", "I_T", CM4, 2, "Torsionsträgheitsmoment", vorlage, funktion,
                      f"Torsionsträgheitsmoment eines {form}")


def _knoten(form: str, vorlage: str, funktion) -> Kennformel:
    return Kennformel("d_K", "d_K", MM, 2, "Durchmesser des Kreises im Knoten von Steg und Flansch",
                      vorlage, funktion, f"Kreis im Knoten eines {form}")


def _u_torsion(form: str, r: str) -> Tuple[Kennformel, Kennformel]:
    """
    ``d_K`` und ``I_T`` eines U -- beim UPE mit ``r``, beim UNP mit ``r_1``:
    zwei Flansche mit einem freien Ende, der Steg dazwischen, und je Knoten
    der Kreis, der hineinpasst.
    """
    knoten = _knoten(
        form, rf"2 \cdot \left(@t_w + @t_f + 3 \cdot @{r} - \sqrt{{2 \cdot \left(2 \cdot @{r} + "
              rf"@t_w\right) \cdot \left(2 \cdot @{r} + @t_f\right)}}\right)",
        lambda t_w, t_f, **k: 2 * (t_w + t_f + 3 * k[r]
                                   - (2 * (2 * k[r] + t_w) * (2 * k[r] + t_f)).wurzel()))
    torsion = _it(
        form, r"\frac{2}{3} \cdot @b \cdot \left(@t_f\right)^{3} \cdot \left(1 - 0.315 \cdot "
              r"\frac{@t_f}{@b}\right) + \frac{1}{3} \cdot \left(@t_w\right)^{3} \cdot "
              r"\left(@h - 2 \cdot @t_f\right) + 2 \cdot \left(0.07 + 0.075 \cdot "
              rf"\frac{{@{r}}}{{@t_f}}\right) \cdot \frac{{@t_w}}{{@t_f}} \cdot \left(@d_K\right)^{{4}}",
        lambda b, t_f, t_w, h, d_K, **k: (
            2 / 3 * b * t_f ** 3 * (EINS - 0.315 * t_f / b) + t_w ** 3 * (h - 2 * t_f) / 3
            + 2 * (Groesse(0.07, EINHEITSLOS) + 0.075 * k[r] / t_f) * t_w / t_f * d_K ** 4))
    return knoten, torsion


def _rohr_traegheit(achse, quer: str, laengs: str) -> Kennformel:
    """
    ``I_y`` oder ``I_z`` eines Rechteckrohrs: ``quer`` steht senkrecht zur
    Achse, ``laengs`` laeuft mit ihr. Aussen fehlen vier Zwickel mit ``r_o``,
    innen kommen vier mit ``r_i`` hinzu -- das Loch hat runde Ecken.
    """
    vorlage = (rf"\frac{{@{laengs} \cdot \left(@{quer}\right)^{{3}} - \left(@{laengs} - 2 \cdot "
               rf"@t\right) \cdot \left(@{quer} - 2 \cdot @t\right)^{{3}}}}{{12}} - 4 \cdot \left("
               + _zwickel("r_o", rf"\frac{{@{quer}}}{{2}} - 0.2234 \cdot @r_o")
               + r"\right) + 4 \cdot \left("
               + _zwickel("r_i", rf"\frac{{@{quer}}}{{2}} - @t - 0.2234 \cdot @r_i") + r"\right)")

    def funktion(t: Groesse, r_o: Groesse, r_i: Groesse, **masse: Groesse) -> Groesse:
        q, l = masse[quer], masse[laengs]
        return ((l * q ** 3 - (l - 2 * t) * (q - 2 * t) ** 3) / 12
                - 4 * _zw(r_o, q / 2 - ZWICKEL[1] * r_o) + 4 * _zw(r_i, q / 2 - t - ZWICKEL[1] * r_i))

    return achse(_RRK, vorlage, funktion)


# ---------------------------------------------------------------------------
# Umrisse: ein Vieleck, die Ecken ausgerundet
# ---------------------------------------------------------------------------

def ausgerundet(ecken: Sequence[Punkt], radien: Sequence[float]) -> List[Punkt]:
    """
    Das Vieleck ``ecken`` -- jede Ecke mit einem Radius durch einen Bogen
    ersetzt, der beide Kanten beruehrt. Ob die Ecke aussen liegt oder innen,
    ob die Kanten im rechten Winkel stehen oder nicht: der Bogen liegt im
    Winkel zwischen ihnen.
    """
    punkte: List[Punkt] = []
    n = len(ecken)
    for i, ((x, y), r) in enumerate(zip(ecken, radien)):
        if r <= 0.0:
            punkte.append((x, y))
            continue
        richtungen = []
        for nachbar in (ecken[i - 1], ecken[(i + 1) % n]):
            dx, dy = nachbar[0] - x, nachbar[1] - y
            laenge = math.hypot(dx, dy)
            richtungen.append((dx / laenge, dy / laenge))
        (u1x, u1y), (u2x, u2y) = richtungen
        winkel = math.acos(max(-1.0, min(1.0, u1x * u2x + u1y * u2y)))
        bx, by = u1x + u2x, u1y + u2y
        b = math.hypot(bx, by)
        abstand = r / math.sin(winkel / 2)
        mx, my = x + abstand * bx / b, y + abstand * by / b
        d = r / math.tan(winkel / 2)
        von = math.atan2(y + d * u1y - my, x + d * u1x - mx)
        bis = math.atan2(y + d * u2y - my, x + d * u2x - mx)
        schritt = (bis - von + math.pi) % (2 * math.pi) - math.pi
        teile = max(2, round(BOGENECKEN * abs(schritt) / (math.pi / 2)))
        punkte += [(mx + r * math.cos(von + schritt * k / teile),
                    my + r * math.sin(von + schritt * k / teile)) for k in range(teile + 1)]
    return [(round(x, 3), round(y, 3)) for x, y in punkte]


def _i_umriss(m: Mapping[str, float]) -> List[List[Punkt]]:
    h, b, t_w, t_f, r = (m[k] for k in ("h", "b", "t_w", "t_f", "r"))
    links, rechts = (b - t_w) / 2, (b + t_w) / 2
    ecken = [(0, 0), (b, 0), (b, t_f), (rechts, t_f), (rechts, h - t_f), (b, h - t_f), (b, h),
             (0, h), (0, h - t_f), (links, h - t_f), (links, t_f), (0, t_f)]
    return [ausgerundet(ecken, [0, 0, 0, r, r, 0, 0, 0, 0, r, r, 0])]


def _u_umriss(h: float, b: float, t_w: float, t_1: float, t_2: float,
              r_1: float, r_2: float) -> List[List[Punkt]]:
    """Ein U, der Ruecken links -- am Steg ``t_1`` dick, an der Spitze ``t_2``."""
    ecken = [(0, 0), (b, 0), (b, t_2), (t_w, t_1), (t_w, h - t_1), (b, h - t_2), (b, h), (0, h)]
    return [ausgerundet(ecken, [0, 0, r_2, r_1, r_1, r_2, 0, 0])]


def _rohr_umriss(m: Mapping[str, float]) -> List[List[Punkt]]:
    h, b, t, r_o, r_i = (m[k] for k in ("h", "b", "t", "r_o", "r_i"))
    aussen = [(0, 0), (b, 0), (b, h), (0, h)]
    innen = [(t, t), (b - t, t), (b - t, h - t), (t, h - t)]
    return [ausgerundet(aussen, [r_o] * 4), ausgerundet(innen, [r_i] * 4)]


# ---------------------------------------------------------------------------
# Die Formen
# ---------------------------------------------------------------------------

_I = "I-Profils"

#: I-Profil -- IPE, HEA, HEB, HEM: Steg und zwei gleiche Flansche, vier Ausrundungen r.
I_PROFIL = Stabvorlage(
    schluessel="i_profil", name="I-Profil",
    masse=(Mass("h", "h", "Höhe", 300.0), Mass("b", "b", "Breite", 150.0),
           Mass("t_w", "t_w", "Stegdicke", 7.1), Mass("t_f", "t_f", "Flanschdicke", 10.7),
           Mass("r", "r", "Ausrundung", 15.0)),
    formeln=(
        _flaeche(_I, r"2 \cdot @b \cdot @t_f + \left(@h - 2 \cdot @t_f\right) \cdot @t_w + "
                     r"4 \cdot 0.2146 \cdot \left(@r\right)^{2}",
                 lambda h, b, t_w, t_f, r: (2 * b * t_f + (h - 2 * t_f) * t_w
                                            + 4 * ZWICKEL[0] * r ** 2)),
        _iy(_I, r"\frac{@t_w \cdot \left(@h - 2 \cdot @t_f\right)^{3}}{12} + \frac{@b \cdot "
                r"\left(@t_f\right)^{3}}{6} + \frac{@b \cdot @t_f \cdot \left(@h - @t_f\right)^{2}}{2}"
                r" + 4 \cdot \left(" + _zwickel("r", r"\frac{@h}{2} - @t_f - 0.2234 \cdot @r")
                + r"\right)",
            lambda h, b, t_w, t_f, r: (t_w * (h - 2 * t_f) ** 3 / 12 + b * t_f ** 3 / 6
                                       + b * t_f * (h - t_f) ** 2 / 2
                                       + 4 * _zw(r, h / 2 - t_f - ZWICKEL[1] * r))),
        _iz(_I, r"\frac{@t_f \cdot \left(@b\right)^{3}}{6} + \frac{\left(@h - 2 \cdot @t_f\right)"
                r" \cdot \left(@t_w\right)^{3}}{12} + 4 \cdot \left("
                + _zwickel("r", r"\frac{@t_w}{2} + 0.2234 \cdot @r") + r"\right)",
            lambda h, b, t_w, t_f, r: (t_f * b ** 3 / 6 + (h - 2 * t_f) * t_w ** 3 / 12
                                       + 4 * _zw(r, t_w / 2 + ZWICKEL[1] * r))),
        _knoten(_I, r"\frac{\left(@r + \frac{@t_w}{2}\right)^{2} + \left(@r + @t_f\right)^{2} - "
                    r"\left(@r\right)^{2}}{@t_f + 2 \cdot @r}",
                lambda t_w, t_f, r: ((r + t_w / 2) ** 2 + (r + t_f) ** 2 - r ** 2) / (t_f + 2 * r)),
        _it(_I, r"\frac{2}{3} \cdot @b \cdot \left(@t_f\right)^{3} \cdot \left(1 - 0.63 \cdot "
                r"\frac{@t_f}{@b}\right) + \frac{1}{3} \cdot \left(@h - 2 \cdot @t_f\right) \cdot "
                r"\left(@t_w\right)^{3} + 2 \cdot \left(0.145 + 0.1 \cdot \frac{@r}{@t_f}\right) "
                r"\cdot \frac{@t_w}{@t_f} \cdot \left(@d_K\right)^{4}",
            lambda b, t_f, h, t_w, r, d_K: (
                2 / 3 * b * t_f ** 3 * (EINS - 0.63 * t_f / b) + (h - 2 * t_f) * t_w ** 3 / 3
                + 2 * (Groesse(0.145, EINHEITSLOS) + 0.1 * r / t_f) * t_w / t_f * d_K ** 4)),
    ),
    pruefung=lambda m: None,
    umriss=_i_umriss,
)

_UPE = "U-Profils mit parallelen Flanschen"

#: U-Profil mit parallelen Flanschen -- UPE: Steg ueber die ganze Hoehe, zwei Ausrundungen r.
U_PARALLEL = Stabvorlage(
    schluessel="u_parallel", name="U-Profil mit parallelen Flanschen",
    masse=(Mass("h", "h", "Höhe", 200.0), Mass("b", "b", "Breite", 80.0),
           Mass("t_w", "t_w", "Stegdicke", 6.0), Mass("t_f", "t_f", "Flanschdicke", 11.0),
           Mass("r", "r", "Ausrundung", 13.0)),
    formeln=(
        _flaeche(_UPE, r"@h \cdot @t_w + 2 \cdot \left(@b - @t_w\right) \cdot @t_f + "
                       r"2 \cdot 0.2146 \cdot \left(@r\right)^{2}",
                 lambda h, t_w, b, t_f, r: h * t_w + 2 * (b - t_w) * t_f + 2 * ZWICKEL[0] * r ** 2),
        Kennformel(
            "e_y", "e_y", MM, 1, "Abstand des Schwerpunkts vom Rücken",
            r"\frac{@h \cdot \left(@t_w\right)^{2} / 2 + 2 \cdot \left(@b - @t_w\right) \cdot @t_f "
            r"\cdot \frac{@b + @t_w}{2} + 2 \cdot 0.2146 \cdot \left(@r\right)^{2} \cdot "
            r"\left(@t_w + 0.2234 \cdot @r\right)}{@A}",
            lambda h, t_w, b, t_f, r, A: (h * t_w ** 2 / 2 + 2 * (b - t_w) * t_f * (b + t_w) / 2
                                          + 2 * ZWICKEL[0] * r ** 2 * (t_w + ZWICKEL[1] * r)) / A,
            f"Schwerpunkt eines {_UPE}"),
        _iy(_UPE, r"\frac{@t_w \cdot \left(@h\right)^{3}}{12} + \frac{\left(@b - @t_w\right) \cdot "
                  r"\left(@t_f\right)^{3}}{6} + \frac{\left(@b - @t_w\right) \cdot @t_f \cdot "
                  r"\left(@h - @t_f\right)^{2}}{2} + 2 \cdot \left("
                  + _zwickel("r", r"\frac{@h}{2} - @t_f - 0.2234 \cdot @r") + r"\right)",
            lambda t_w, h, b, t_f, r: (t_w * h ** 3 / 12 + (b - t_w) * t_f ** 3 / 6
                                       + (b - t_w) * t_f * (h - t_f) ** 2 / 2
                                       + 2 * _zw(r, h / 2 - t_f - ZWICKEL[1] * r))),
        _iz(_UPE, r"\frac{@h \cdot \left(@t_w\right)^{3}}{12} + \frac{@t_f \cdot \left(@b - @t_w"
                  r"\right)^{3}}{6} + @h \cdot @t_w \cdot \left(@e_y - \frac{@t_w}{2}\right)^{2} + "
                  r"2 \cdot \left(@b - @t_w\right) \cdot @t_f \cdot \left(\frac{@b + @t_w}{2} - "
                  r"@e_y\right)^{2} + 2 \cdot \left("
                  + _zwickel("r", r"@t_w + 0.2234 \cdot @r - @e_y") + r"\right)",
            lambda h, t_w, t_f, b, e_y, r: (h * t_w ** 3 / 12 + t_f * (b - t_w) ** 3 / 6
                                            + h * t_w * (e_y - t_w / 2) ** 2
                                            + 2 * (b - t_w) * t_f * ((b + t_w) / 2 - e_y) ** 2
                                            + 2 * _zw(r, t_w + ZWICKEL[1] * r - e_y))),
        *_u_torsion(_UPE, "r"),
    ),
    pruefung=lambda m: None,
    umriss=lambda m: _u_umriss(m["h"], m["b"], m["t_w"], m["t_f"], m["t_f"], m["r"], 0.0),
)

_UNP = "U-Profils mit geneigten Flanschen"

#: U-Profil mit geneigten Flanschen -- UNP: die Flansche innen um ``p`` geneigt,
#: ``t_f`` gilt im Abstand ``c`` vom Ruecken; am Steg die Ausrundung ``r_1``, an
#: der Spitze die Rundung ``r_2``.
U_GENEIGT = Stabvorlage(
    schluessel="u_geneigt", name="U-Profil mit geneigten Flanschen",
    masse=(Mass("h", "h", "Höhe", 200.0), Mass("b", "b", "Breite", 75.0),
           Mass("t_w", "t_w", "Stegdicke", 8.5), Mass("t_f", "t_f", "Flanschdicke", 11.5),
           Mass("r_1", "r_1", "Ausrundung am Steg", 11.5),
           Mass("r_2", "r_2", "Rundung an der Flanschspitze", 6.0),
           Mass("p", "p", "Neigung der Flansche", 8.0, einheit=PROZENT),
           Mass("c", "c", "Abstand der Stelle von t_f vom Rücken", 37.5)),
    formeln=(
        Kennformel("t_1", "t_1", MM, 2, "Flanschdicke am Steg", r"@t_f + @p \cdot \left(@c - @t_w\right)",
                   lambda t_f, p, c, t_w: t_f + p * (c - t_w), "Dicke des geneigten Flanschs am Steg"),
        Kennformel("t_2", "t_2", MM, 2, "Flanschdicke an der Spitze", r"@t_f - @p \cdot \left(@b - @c\right)",
                   lambda t_f, p, b, c: t_f - p * (b - c), "Dicke des geneigten Flanschs an der Spitze"),
        _flaeche(_UNP, r"@b \cdot @h - \left(@b - @t_w\right) \cdot \left(@h - @t_1 - @t_2\right) + "
                       r"2 \cdot 0.2146 \cdot \left(\left(@r_1\right)^{2} - \left(@r_2\right)^{2}\right)",
                 lambda b, h, t_w, t_1, t_2, r_1, r_2: (b * h - (b - t_w) * (h - t_1 - t_2)
                                                        + 2 * ZWICKEL[0] * (r_1 ** 2 - r_2 ** 2))),
        Kennformel(
            "e_y", "e_y", MM, 1, "Abstand des Schwerpunkts vom Rücken",
            r"\frac{\left(@b\right)^{2} \cdot @h / 2 - \frac{@b - @t_w}{6} \cdot \left(@t_w \cdot "
            r"\left(3 \cdot @h - 4 \cdot @t_1 - 2 \cdot @t_2\right) + @b \cdot \left(3 \cdot @h - "
            r"2 \cdot @t_1 - 4 \cdot @t_2\right)\right) + 2 \cdot 0.2146 \cdot \left(@r_1\right)^{2}"
            r" \cdot \left(@t_w + 0.2234 \cdot @r_1\right) - 2 \cdot 0.2146 \cdot \left(@r_2"
            r"\right)^{2} \cdot \left(@b - 0.2234 \cdot @r_2\right)}{@A}",
            lambda b, h, t_w, t_1, t_2, r_1, r_2, A: (
                b ** 2 * h / 2
                - (b - t_w) / 6 * (t_w * (3 * h - 4 * t_1 - 2 * t_2) + b * (3 * h - 2 * t_1 - 4 * t_2))
                + 2 * ZWICKEL[0] * r_1 ** 2 * (t_w + ZWICKEL[1] * r_1)
                - 2 * ZWICKEL[0] * r_2 ** 2 * (b - ZWICKEL[1] * r_2)) / A,
            f"Schwerpunkt eines {_UNP}"),
        _iy(_UNP, r"\frac{@b \cdot \left(@h\right)^{3}}{12} - \frac{\left(@b - @t_w\right) \cdot "
                  r"\left(@h - @t_1 - @t_2\right) \cdot \left(\left(@h - 2 \cdot @t_1\right)^{2} + "
                  r"\left(@h - 2 \cdot @t_2\right)^{2}\right)}{24} + 2 \cdot \left("
                  + _zwickel("r_1", r"\frac{@h}{2} - @t_1 - 0.2234 \cdot @r_1")
                  + r"\right) - 2 \cdot \left("
                  + _zwickel("r_2", r"\frac{@h}{2} - @t_2 + 0.2234 \cdot @r_2") + r"\right)",
            lambda b, h, t_w, t_1, t_2, r_1, r_2: (
                b * h ** 3 / 12
                - (b - t_w) * (h - t_1 - t_2) * ((h - 2 * t_1) ** 2 + (h - 2 * t_2) ** 2) / 24
                + 2 * _zw(r_1, h / 2 - t_1 - ZWICKEL[1] * r_1)
                - 2 * _zw(r_2, h / 2 - t_2 + ZWICKEL[1] * r_2))),
        _iz(_UNP, r"\frac{\left(@b\right)^{3} \cdot @h}{3} - \frac{@b - @t_w}{12} \cdot \left("
                  r"\left(@h - 2 \cdot @t_1\right) \cdot \left(3 \cdot \left(@t_w\right)^{2} + 2 \cdot"
                  r" @t_w \cdot @b + \left(@b\right)^{2}\right) + \left(@h - 2 \cdot @t_2\right) \cdot "
                  r"\left(\left(@t_w\right)^{2} + 2 \cdot @t_w \cdot @b + 3 \cdot \left(@b\right)^{2}"
                  r"\right)\right) + 2 \cdot \left(" + _zwickel("r_1", r"@t_w + 0.2234 \cdot @r_1")
                  + r"\right) - 2 \cdot \left(" + _zwickel("r_2", r"@b - 0.2234 \cdot @r_2")
                  + r"\right) - @A \cdot \left(@e_y\right)^{2}",
            lambda b, h, t_w, t_1, t_2, r_1, r_2, A, e_y: (
                b ** 3 * h / 3
                - (b - t_w) / 12 * ((h - 2 * t_1) * (3 * t_w ** 2 + 2 * t_w * b + b ** 2)
                                    + (h - 2 * t_2) * (t_w ** 2 + 2 * t_w * b + 3 * b ** 2))
                + 2 * _zw(r_1, t_w + ZWICKEL[1] * r_1) - 2 * _zw(r_2, b - ZWICKEL[1] * r_2)
                - A * e_y ** 2)),
        *_u_torsion(_UNP, "r_1"),
    ),
    pruefung=lambda m: None,
    umriss=lambda m: _u_umriss(*(U_GENEIGT.kennwerte(m)[k].in_einheit(MM)
                                 for k in ("h", "b", "t_w", "t_1", "t_2", "r_1", "r_2"))),
)

#: Rechteckrohr, kaltgefertigt -- RRK: Wand ``t`` ringsum, die Ecken aussen mit
#: ``r_o``, innen mit ``r_i`` gerundet; ``h`` steht senkrecht.
RECHTECKROHR_KALT = Stabvorlage(
    schluessel="rechteckrohr_kalt", name="Rechteckrohr, kaltgefertigt",
    masse=(Mass("h", "h", "Höhe", 200.0), Mass("b", "b", "Breite", 100.0),
           Mass("t", "t", "Wanddicke", 8.0), Mass("r_o", "r_o", "Radius aussen", 20.0),
           Mass("r_i", "r_i", "Radius innen", 12.0)),
    formeln=(
        _flaeche(_RRK, r"2 \cdot @t \cdot \left(@h + @b - 2 \cdot @t\right) - 4 \cdot 0.2146 \cdot "
                       r"\left(\left(@r_o\right)^{2} - \left(@r_i\right)^{2}\right)",
                 lambda t, h, b, r_o, r_i: (2 * t * (h + b - 2 * t)
                                            - 4 * ZWICKEL[0] * (r_o ** 2 - r_i ** 2))),
        _rohr_traegheit(_iy, quer="h", laengs="b"),
        _rohr_traegheit(_iz, quer="b", laengs="h"),
        Kennformel("p_m", "p_m", MM, 1, "Umfang der Mittellinie",
                   r"2 \cdot \left(@h + @b - 2 \cdot @t\right) - \left(@r_o + @r_i\right) \cdot "
                   r"\left(4 - \pi\right)",
                   lambda h, b, t, r_o, r_i: 2 * (h + b - 2 * t) - (r_o + r_i) * (4 - math.pi),
                   f"Umfang der Mittellinie eines {_RRK}"),
        Kennformel("A_m", "A_m", CM2, 2, "von der Mittellinie umschlossene Fläche",
                   r"\left(@h - @t\right) \cdot \left(@b - @t\right) - \left(\frac{@r_o + @r_i}{2}"
                   r"\right)^{2} \cdot \left(4 - \pi\right)",
                   lambda h, t, b, r_o, r_i: (h - t) * (b - t) - ((r_o + r_i) / 2) ** 2 * (4 - math.pi),
                   f"Umschlossene Fläche eines {_RRK}"),
        # Dieselbe Formel wie beim Rechteckrohr der Vorlagen -- nur p_m und A_m
        # haben hier runde Ecken. Darum dieselbe Seite.
        _it("Rechteckrohrs", *ROHRTORSION),
    ),
    pruefung=lambda m: None,
    umriss=_rohr_umriss,
)


def _in_cm(f: Kennformel) -> Kennformel:
    """Eine Formel der Vorlagen, in den Einheiten der Profile: Flaechen in cm², Momente in cm⁴."""
    return replace(f, einheit={MM2: CM2, MIO_MM4: CM4}.get(f.einheit, f.einheit), stellen=2)


#: Rundrohr -- ROR: aussen ``D``, Wand ``t``; die Formeln und Seiten des
#: Kreisrings, nur in cm² und cm⁴.
RUNDROHR = Stabvorlage(
    schluessel="rundrohr", name="Rundrohr",
    masse=KREISRING.masse,
    formeln=tuple(_in_cm(f) for f in KREISRING.formeln),
    pruefung=KREISRING.pruefung,
    umriss=KREISRING.umriss,
)

PROFILFORMEN: Tuple[Stabvorlage, ...] = (I_PROFIL, U_PARALLEL, U_GENEIGT, RECHTECKROHR_KALT,
                                         RUNDROHR)
