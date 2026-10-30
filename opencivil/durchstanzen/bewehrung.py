"""
opencivil/durchstanzen/bewehrung.py -- wo die Durchstanzbewehrung liegt, und welche reicht.

VERANTWORTUNG:
Die Leisten um die gestützte Fläche und ihre Anker (:func:`leisten_anordnen`),
der äussere Nachweisschnitt um die äussersten Anker (:func:`aeussere_kandidaten`,
Figur 26) und die Suche nach dem kleinsten ancoPLUS, das alle Bedingungen
erfüllt (:func:`bemessen`). Hier steht keine Herleitung: der Nachweis
(:mod:`.nachweis`) schreibt sie für die Bewehrung, die hier gefunden wird.

DIE ANORDNUNG:
Die Leisten stehen senkrecht auf dem Rand der gestützten Fläche, an Ecken und
Rundungen radial. Ihre zweiten Anker liegen auf der Linie im Abstand r_2 um
die gestützte Fläche; entlang dieser Linie stehen zwei Leisten höchstens
e_max auseinander, als Sehne gemessen. Auf jeder geraden Seite steht an
beiden Enden eine Leiste und dazwischen gleichmässig so viele wie nötig, auf
den Rundungen ebenso. Das ist der Grundriss der Herstellerunterlagen, die
Regeln dazu sind die des Produkts (:mod:`.produkte`) -- nach Vorgabe, nicht
nachgeschlagen. Eine Leiste, deren Anker nicht mindestens die Überdeckung
tief in der Platte liegen, fällt weg; ebenso eine, deren Anker in eine
Aussparung fallen.

DER ÄUSSERE SCHNITT (Figur 26):
Er läuft im Abstand 0.5·d_v,out um die äussersten Anker; von einer geraden
Strecke zwischen zwei äussersten Ankern zählen höchstens 1.5·d_v,out von
jedem Ende her. Das ist die Regel der Ecken grosser Stützen (Figur 23a), mit
den äussersten Ankern als Ecken -- gebaut wird er darum wie der Schnitt um
eine Stütze, deren Kern die konvexe Hülle der äussersten Anker und der
Stütze ist (:func:`~.schnitt.kandidaten_stuetze`). Am Plattenrand endet er
wie der innere, wenn er so kürzer wird.

EINHEITEN:
SI-Basis, Längen in m, Kräfte in N.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import accumulate
from typing import Callable, List, Optional, Sequence, Tuple

from opencivil.durchstanzen import produkte
from opencivil.durchstanzen.schnitt import (
    Bogen, Halbebene, Kandidat, Nachweisschnitt, Punkt, Strecke, Stuetzenflaeche, Stueck,
    konvexe_huelle, kandidaten_stuetze, nachweisschnitt,
)
from opencivil.querschnitt.geometrie import lage

#: Angerechnet wird die Durchstanzbewehrung zwischen 0.35·d_v und d_v vom Rand
#: der gestützten Fläche (SIA 262:2025, 4.3.6.5.4, Gleichung (68)).
BEREICH_VON = 0.35

#: Von einer Strecke des äusseren Schnitts zwischen zwei äussersten Ankern
#: zählen höchstens 1.5·d_v,out von jedem Ende (SIA 262:2025, Figur 26).
ECKENBEREICH_AUSSEN = 1.5

#: Wie dicht die Suche die Leisten stellt, in Teilen von e_max: erst so weit
#: wie erlaubt, dann enger, wenn kein Durchmesser reicht.
DICHTEN = (1.0, 0.75, 0.5)


@dataclass(frozen=True)
class Leiste:
    """Eine Leiste: wo sie am Rand der gestützten Fläche ansetzt und wohin sie läuft."""

    wurzel: Punkt
    richtung: Punkt

    def anker(self, radien: Sequence[float]) -> List[Punkt]:
        """Die Anker im Abstand ``radien`` vom Rand der gestützten Fläche."""
        return [(self.wurzel[0] + r * self.richtung[0], self.wurzel[1] + r * self.richtung[1])
                for r in radien]


def _normale(a: Punkt, b: Punkt) -> Punkt:
    """Nach aussen, für einen Rand gegen den Uhrzeigersinn."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    return (dy / L, -dx / L)


def leisten_anordnen(stuecke: Sequence[Stueck], r_2: float, e_max: float) -> List[Leiste]:
    """
    Die Leisten um eine gestützte Fläche -- ``stuecke`` ist der geschlossene
    Schnitt im Abstand ``r_2`` um sie (siehe Dateikopf).
    """
    orte: List[Tuple[Punkt, Punkt]] = []
    for st in stuecke:
        if isinstance(st, Strecke):
            n = max(1, math.ceil(st.laenge / e_max - 1e-9))
            richtung = _normale(st.a, st.b)
            orte += [((st.a[0] + (st.b[0] - st.a[0]) * i / n, st.a[1] + (st.b[1] - st.a[1]) * i / n),
                      richtung) for i in range(n + 1)]
        elif isinstance(st, Bogen):
            # So viele Teile, dass die Sehne zwischen zwei Leisten höchstens e_max ist.
            schritt = 2.0 * math.asin(min(1.0, e_max / (2.0 * st.radius)))
            n = max(1, math.ceil((st.bis - st.von) / schritt - 1e-9))
            for i in range(n + 1):
                w = st.von + (st.bis - st.von) * i / n
                orte.append((st.punkt(w), (math.cos(w), math.sin(w))))
    leisten: List[Leiste] = []
    gesehen: List[Punkt] = []
    for p, r in orte:
        if any(math.dist(p, q) < 1e-6 for q in gesehen):
            continue
        gesehen.append(p)
        leisten.append(Leiste((p[0] - r_2 * r[0], p[1] - r_2 * r[1]), r))
    return leisten


def in_der_platte(leisten: Sequence[Leiste], radien: Sequence[float], raender: Sequence[Halbebene],
                  aussparungen: Sequence[Sequence[Punkt]], ueberdeckung: float) -> List[Leiste]:
    """Nur die Leisten, deren Anker alle um die Überdeckung in der Platte liegen und keine Aussparung treffen."""
    def gut(p: Punkt) -> bool:
        return (all(h.n[0] * p[0] + h.n[1] * p[1] <= h.c - ueberdeckung for h in raender)
                and not any(lage(p, a) >= 0 for a in aussparungen))
    return [l for l in leisten if all(gut(p) for p in l.anker(radien))]


def aeussere_kandidaten(leisten: Sequence[Leiste], radien: Sequence[float],
                        umriss: Sequence[Punkt], raender: Sequence[Halbebene],
                        d_v_out: float) -> List[Kandidat]:
    """Die Kandidaten des äusseren Schnitts (Figur 26) -- siehe Dateikopf."""
    aussen = [l.anker(radien)[-1] for l in leisten]
    huelle = konvexe_huelle(list(aussen) + list(umriss))
    return kandidaten_stuetze(Stuetzenflaeche(tuple(huelle)), 0.5 * d_v_out,
                              ECKENBEREICH_AUSSEN * d_v_out, raender)


# ===========================================================================
# Die Suche
# ===========================================================================


@dataclass(frozen=True)
class Vorschlag:
    """
    Eine Durchstanzbewehrung, die alle Bedingungen erfüllt -- oder die stärkste,
    die sich finden liess (``reicht`` falsch). Kräfte in N.
    """

    typ: produkte.Ankertyp
    h_A: float
    abstaende: Tuple[float, ...]
    leisten: Tuple[Leiste, ...]
    anrechenbar: int
    """Wie viele Anker je Leiste zwischen 0.35·d_v und d_v liegen (Gleichung (68))."""

    aussen: Nachweisschnitt
    reicht: bool

    @property
    def radien(self) -> Tuple[float, ...]:
        """Die Abstände der Anker vom Rand der gestützten Fläche."""
        return tuple(accumulate(self.abstaende))

    @property
    def A_sw(self) -> float:
        """Die anrechenbare Durchstanzbewehrung: Leisten mal Anker im Bereich mal Fläche."""
        return len(self.leisten) * self.anrechenbar * self.typ.flaeche

    @property
    def name(self) -> str:
        """«12 × ancoPLUS DA3-0215»."""
        return (f"{len(self.leisten)} × ancoPLUS "
                f"{produkte.typname(self.typ, len(self.abstaende), self.h_A)}")


def anrechenbar(radien: Sequence[float], d_v: float) -> int:
    """Die Anker zwischen 0.35·d_v und d_v vom Rand der gestützten Fläche (Gleichung (68))."""
    return sum(1 for r in radien if BEREICH_VON * d_v - 1e-9 <= r <= d_v + 1e-9)


def bemessen(*, d: float, d_v: float, d_v_out: float, h_A: float,
             r_2_zu: Callable[[float], Sequence[Stueck]], umriss: Sequence[Punkt],
             raender: Sequence[Halbebene], aussparungen: Sequence[Sequence[Punkt]], achse: Punkt,
             ueberdeckung: float, noetig: Callable[[produkte.Ankertyp, float], bool],
             aussen_reicht: Callable[[Nachweisschnitt], bool]) -> Optional[Vorschlag]:
    """
    Das kleinste ancoPLUS, das reicht: der kleinste Durchmesser, mit dem die
    Bewehrung im Bereich ``noetig`` erfüllt, und dazu die kleinste Zahl Anker
    je Leiste, mit der der äussere Schnitt ``aussen_reicht``. Erst wenn kein
    Durchmesser genügt, stehen die Leisten dichter (:data:`DICHTEN`).
    ``noetig(typ, A_sw)`` und ``aussen_reicht(schnitt)`` rechnet der
    Nachweis; ``r_2_zu(r)`` gibt den geschlossenen Schnitt im Abstand r um die
    gestützte Fläche.

    Reicht nichts, kommt der stärkste Versuch mit ``reicht`` falsch zurück --
    die dichtesten Leisten mit dem grössten Durchmesser und neun Ankern.
    ``None`` nur, wo es kein ancoPLUS gibt: die Platte ist zu dünn, keine
    Höhe ist lieferbar, oder keine Leiste findet Platz.
    """
    groesster = produkte.groesster_durchmesser(d)
    typen = [t for t in produkte.ANKERTYPEN
             if groesster is not None and t.durchmesser <= groesster + 1e-9
             and t.h_min - 1e-9 <= h_A <= t.h_max + 1e-9]
    if not typen:
        return None
    r_2 = sum(produkte.abstaende(d, 2))

    # Der äussere Schnitt hängt nur an den Leisten, nicht am Durchmesser: einmal je Anordnung.
    gerechnet: dict = {}

    def aussen(leisten: Tuple[Leiste, ...], radien: Tuple[float, ...]) -> Nachweisschnitt:
        schluessel = (leisten, radien)
        if schluessel not in gerechnet:
            gerechnet[schluessel] = nachweisschnitt(
                aeussere_kandidaten(leisten, radien, umriss, raender, d_v_out),
                d_v=d_v_out, achse=achse, aussparungen=aussparungen)
        return gerechnet[schluessel]

    def versuch(alle: Sequence[Leiste], typ: produkte.Ankertyp, anzahl: int,
                pruefen: bool) -> Optional[Vorschlag]:
        folge = produkte.abstaende(d, anzahl)
        radien = tuple(accumulate(folge))
        leisten = tuple(in_der_platte(alle, radien, raender, aussparungen, ueberdeckung))
        im_bereich = anrechenbar(radien, d_v)
        if not leisten or (pruefen and not noetig(typ, len(leisten) * im_bereich * typ.flaeche)):
            return None
        schnitt = aussen(leisten, radien)
        return Vorschlag(typ, h_A, folge, leisten, im_bereich, schnitt,
                         pruefen and aussen_reicht(schnitt))

    bester: Optional[Vorschlag] = None
    for dichte in DICHTEN:
        alle = leisten_anordnen(r_2_zu(r_2), r_2, dichte * produkte.TANGENTIAL * d)
        for typ in typen:
            for anzahl in produkte.ANKER_JE_LEISTE:
                vorschlag = versuch(alle, typ, anzahl, pruefen=True)
                if vorschlag is None:
                    # Mehr Anker heben den Bereich nicht -- der nächste Durchmesser.
                    break
                if vorschlag.reicht:
                    return vorschlag
                bester = vorschlag
    if bester is not None:
        return bester
    dichteste = leisten_anordnen(r_2_zu(r_2), r_2, DICHTEN[-1] * produkte.TANGENTIAL * d)
    return versuch(dichteste, typen[-1], produkte.ANKER_JE_LEISTE[-1], pruefen=False)
