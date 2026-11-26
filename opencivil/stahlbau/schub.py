"""
opencivil/stahlbau/schub.py -- der Querkraftwiderstand eines Stahlprofils nach SIA 263:2013.

VERANTWORTUNG:
Je Profil und Richtung, was der Querkraft widersteht: die Schubflaeche
``A_v`` nach 5.1.4.1, Gleichung (41), und wo ein Steg schlank ist, das
Schubbeulen nach 4.5.4, Gleichung (13). Die Querkraft wirkt allein: ohne
Normalkraft und Biegung ist kein Blech gedrueckt, und der Querschnitt
rechnet plastisch (5.1.4).

DIE SCHUBFLAECHEN:
* I-Profil in Stegrichtung: (41a).
* Die anderen nach Vorgabe, nicht nachgeschlagen -- die Norm verweist dafuer
  auf SN EN 1993-1-1, die hier nicht vorliegt: das U in Stegrichtung
  ``A - 2 b t_f + (t_w + r) t_f``, I und U quer dazu ``2 b t_f``, das
  Rundrohr ``2 t (D - t)``. So rechnen auch die Excel-Dateien des Benutzers.
* Das Rechteckrohr: je Wand in der Richtung (13), ``b`` zwischen den
  Mittellinien der beiden anderen Waende. Ohne Beulen sind das
  ``2 τ_y t (h - t)/γ_M1``, wie in den Excel-Dateien.

DAS SCHUBBEULEN:
Beim I und beim U genuegt (42); haelt der Steg es nicht ein, widersteht er
nach (13) mit ``b t = (h - t_f) t_w``. Der Beulwert ist der des langen Felds,
``k_τ = 5.34``: wo Quersteifen stehen, weiss das Werkzeug nicht (nach
Vorgabe, nicht nachgeschlagen). Flansche und Rundrohre beulen hier nicht --
nach Vorgabe, nicht nachgeschlagen: gewalzte sind dafuer zu gedrungen.

RICHTUNG:
``z`` ist die Richtung, in der das ungedrehte Profil steht -- beim I und U
die des Stegs, beim Rechteckrohr die von ``h``. Um 90° oder 270° gedreht,
traegt es dasselbe in ``y``.

WO DIE QUERKRAFT STEHT (:func:`streifen`):
Die Bleche parallel zu ihr: beim I und U in Stegrichtung der Steg zwischen
den Flanschen, ``h_w = h - 2 t_f`` wie in (43); quer dazu die Flansche
ganz, ``2 b t_f`` wie ihre Schubflaeche; beim Rechteckrohr die beiden Waende
in ihrer Richtung, je ``h - 3 t`` wie in 5.1.5.3. Das Rundrohr hat keine
solchen Bleche: dort steht die Schubflaeche gleichmaessig ueber den Ring
verteilt, ``A_v/A`` von jedem Teil (nach Vorgabe, nicht nachgeschlagen).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

from opencivil.querschnitt import geometrie as geo
from opencivil.stahlprofile import tabelle
from opencivil.stahlprofile.bleche import Punkt, bleche
from opencivil.stahlprofile.lage import Profillage

REFERENZ_SCHUB = "SIA 263:2013, 5.1.4.1, (41)"
REFERENZ_41A = "SIA 263:2013, 5.1.4.1, (41a)"
REFERENZ_42 = "SIA 263:2013, 5.1.4.2, (42)"
REFERENZ_BEULEN = "SIA 263:2013, 4.5.4.1, (13); Figur 8"
NACH_VORGABE = "nach Vorgabe, nicht nachgeschlagen"

#: Der Schubbeulwert des langen Felds ohne Quersteifen (Figur 8, α gross) --
#: siehe Dateikopf.
K_TAU = 5.34


@dataclass(frozen=True)
class Schubwiderstand:
    """
    Was ein Profil in einer Richtung traegt, in mm und N/mm²: die Flaeche,
    auf der die Schubspannung ``tau`` wirkt -- ``A_v`` nach (41) oder ``b t``
    der Bleche nach (13) -- und woher beides kommt.
    """

    flaeche: float
    tau: float
    formel: str
    """Die Flaeche als LaTeX, mit Zahlen: «A - 2 b t_f + ...» oder «2 \\cdot 92 \\cdot 4»."""

    herkunft: str
    """Die Stelle der Flaeche -- eine Normstelle oder «nach Vorgabe»."""

    beulen: Optional["Schubbeulen"] = None
    """Wie das Blech nach (13) beult -- ``None`` bei (41)."""

    steg: Optional[Tuple[float, float]] = None
    """Beim I und U in Stegrichtung (42): ``(h - t_f)/t_w`` und seine Grenze ``√(4 E/f_y)``."""

    def V_Rd(self, gamma_M1: float) -> float:
        """Der Widerstand in N."""
        return self.tau * self.flaeche / gamma_M1


@dataclass(frozen=True)
class Schubbeulen:
    """Die Werte von (13) fuer ein Blech der Breite ``b`` und der Dicke ``t``, in mm und N/mm²."""

    b: float
    t: float
    tau_cr: float


def tau_beulen(b: float, t: float, *, E: float, tau_y: float) -> float:
    """Die Schubspannung, bis zu der ein Blech nach (13) traegt: ``0.9 √(τ_cr τ_y) ≤ τ_y``."""
    return min(0.9 * math.sqrt(kritisch(b, t, E=E) * tau_y), tau_y)


def kritisch(b: float, t: float, *, E: float) -> float:
    """Die kritische Schubspannung ``τ_cr = k_τ · 0.9 E (t/b)²`` (4.5.4.1)."""
    return K_TAU * 0.9 * E * (t / b) ** 2


def widerstand(lage: Profillage, flaeche: float, richtung: str, *, f_y: float, tau_y: float,
               E: float) -> Schubwiderstand:
    """
    Der Querkraftwiderstand eines Profils in ``richtung`` («y» oder «z») --
    ``flaeche`` ist seine Flaeche ``A`` in mm², wie gezeichnet. Siehe Dateikopf.
    """
    masse = tabelle.profil(lage.name).masse
    form = tabelle.profil(lage.name).form.schluessel
    steg = (richtung == "z") == (lage.drehung % 180 == 0)
    if form == "rundrohr":
        D, t = masse["D"], masse["t"]
        return Schubwiderstand(2.0 * t * (D - t), tau_y, rf"2 \cdot {t:g} \cdot ({D:g} - {t:g})",
                               NACH_VORGABE)
    if form == "rechteckrohr_kalt":
        lang, t = (masse["h"] if steg else masse["b"]), masse["t"]
        b = lang - t
        tau = tau_beulen(b, t, E=E, tau_y=tau_y)
        return Schubwiderstand(2.0 * b * t, tau, rf"2 \cdot ({lang:g} - {t:g}) \cdot {t:g}",
                               REFERENZ_BEULEN, Schubbeulen(b, t, kritisch(b, t, E=E)))
    h, b, t_w, t_f = (masse[k] for k in ("h", "b", "t_w", "t_f"))
    if not steg:
        return Schubwiderstand(2.0 * b * t_f, tau_y, rf"2 \cdot {b:g} \cdot {t_f:g}", NACH_VORGABE)
    steg_b = h - t_f
    pruefung = (steg_b / t_w, math.sqrt(4.0 * E / f_y))
    if pruefung[0] > pruefung[1]:
        return Schubwiderstand(
            steg_b * t_w, tau_beulen(steg_b, t_w, E=E, tau_y=tau_y),
            rf"({h:g} - {t_f:g}) \cdot {t_w:g}", REFERENZ_BEULEN,
            Schubbeulen(steg_b, t_w, kritisch(steg_b, t_w, E=E)), pruefung)
    if form == "i_profil":
        r = masse["r"]
        return Schubwiderstand(
            flaeche - 2.0 * b * t_f + (t_w + 2.0 * r) * t_f, tau_y,
            rf"{flaeche:.0f} - 2 \cdot {b:g} \cdot {t_f:g} + ({t_w:g} + 2 \cdot {r:g}) \cdot {t_f:g}",
            REFERENZ_41A, steg=pruefung)
    r = masse["r"] if form == "u_parallel" else masse["r_1"]
    return Schubwiderstand(
        flaeche - 2.0 * b * t_f + (t_w + r) * t_f, tau_y,
        rf"{flaeche:.0f} - 2 \cdot {b:g} \cdot {t_f:g} + ({t_w:g} + {r:g}) \cdot {t_f:g}",
        NACH_VORGABE, steg=pruefung)


def rund(lage: Profillage) -> bool:
    """Ob das Profil in jeder Richtung gleich traegt -- das Rundrohr."""
    return tabelle.profil(lage.name).form.schluessel == "rundrohr"


def _parallel(von: Punkt, bis: Punkt, richtung: str) -> bool:
    """Ob die Strecke von ``von`` nach ``bis`` in ``richtung`` laeuft, «y» oder «z»."""
    dy, dz = abs(bis[0] - von[0]), abs(bis[1] - von[1])
    return dz > dy if richtung == "z" else dy > dz


def streifen(lage: Profillage, richtung: str) -> List[Tuple[str, float, Tuple[Punkt, ...]]]:
    """
    Wo die Querkraft in ``richtung`` im Profil steht -- siehe Dateikopf: je
    Streifen der Name seines Blechs, sein Anteil und sein Umriss in der
    Zeichnung. Beim Rundrohr der Ring mit ``A_v/A``: der Umriss aussen mit
    diesem Anteil, das Loch mit dem negativen.
    """
    profil = tabelle.profil(lage.name)
    masse, form = profil.masse, profil.form.schluessel
    if form == "rundrohr":
        aussen, loch = lage.umrisse
        D, t = masse["D"], masse["t"]
        anteil = 2.0 * t * (D - t) / (geo.flaechenwerte(aussen).A - geo.flaechenwerte(loch).A)
        return [("Wand", anteil, tuple(aussen)), ("Wand", -anteil, tuple(loch))]
    teile = []
    for blech in bleche(lage):
        if not _parallel(blech.von, blech.bis, richtung):
            continue
        rolle = blech.name.split()[0]
        if rolle == "Steg":
            von, bis = masse["t_f"] / 2.0, blech.b - masse["t_f"] / 2.0
        elif rolle == "Flansch":
            # Beim U reicht der Flansch vom Ruecken aus, nicht von der Mitte des Stegs.
            von, bis = (0.0 if form == "i_profil" else -masse["t_w"] / 2.0), blech.b
        else:
            von, bis = blech.vor, blech.vor + blech.c
        teile.append((blech.name, 1.0, blech.streifen(von, bis)))
    return teile
