"""
opencivil/pfahl/erdwiderstand.py -- was der Boden quer zum Pfahl hält, und wie der Pfahl quer bricht.

VERANTWORTUNG:
* :class:`Erdwiderstand` -- je Meter Pfahl die grösste Kraft, die der Boden
  quer aufnimmt, über die Tiefe: p_E,k. Als Stücke, auf denen sie linear
  verläuft (:meth:`Erdwiderstand.linien`).
* :func:`brueche` -- wie ein Pfahl quer zu seiner Achse bricht: der Boden
  längs des Pfahls gibt nach, und wo das Moment den Biegewiderstand M_R
  erreicht, knickt der Pfahl in einem Gelenk. Der kleinste Bruch ist der
  charakteristische Querwiderstand R_tr,k (SIA 267:2013, 9.4.4.2.2).

DER ERDWIDERSTAND (Kap. 9.3.5, 9.3.6, 10.8)::

    drainiert    e_p = K_p · σ'_v + 2 · c' · √K_p     e_a = K_a · σ'_v − 2 · c' · √K_a
                 K_p = (1 + sin φ') / (1 − sin φ')     K_a = 1 / K_p
    undrainiert  e_p = σ_v + 2 · s_u                   e_a = σ_v − 2 · s_u
    p_E,k = b' · (e_p − max(0; e_a))                    b' = 3 · D

Vorne, wohin sich der Pfahl schiebt, drückt der Boden passiv dagegen;
hinten drückt er nur noch aktiv nach, und wo e_a negativ würde, klafft ein
Spalt. Vor einem schmalen Körper wirkt der Erdwiderstand auf einer
breiteren Fläche als dieser, grob auf der dreifachen Breite.

DIE BRÜCHE:
s zählt ab dem Kopf. H wirkt am Kopf, beim frei drehbaren Kopf mit dem
Moment H · e dazu. Je Mechanismus leistet die Last dieselbe Arbeit, die
Boden und Gelenke verzehren; seine Lage ist die, bei der H am kleinsten
wird::

    frei drehbar
      Drehung um s_r                    H · |s_r + e| = ∫ p_E · |s − s_r| ds
      Gelenk in s_h                     H · |s_h + e| = M_R + ∫₀^s_h p_E · (s_h − s) ds
      Verschiebung                      H = ∫ p_E ds
    eingespannt
      Gelenk am Kopf, Drehung um s_r    H · s_r = M_R + ∫ p_E · |s − s_r| ds
      Gelenke am Kopf und in s_h        H · s_h = 2 · M_R + ∫₀^s_h p_E · (s_h − s) ds
      Verschiebung                      H = ∫ p_E ds

Unter einem Gelenk in s_h steht der Pfahl still. Gesucht wird auf Knoten,
höchstens :data:`SCHRITT` auseinander; zwischen ihnen ist p_E linear, und
die Integrale sind exakt.

NACH VORGABE, NICHT NACHGESCHLAGEN (notizbuch/Notizen/TODO.md):
* Hinten der aktive Erddruck abgezogen, und beide auf der Breite 3 · D. Das
  Buch gibt die wirksame Breite für den passiven Druck vor einem schmalen
  Träger. Nur so hebt sich undrainiert σ_v vorne und hinten auf, und p_E
  wächst nicht ohne Grenze mit der Tiefe.
* Rankine, ohne Reibung zwischen Pfahl und Boden.
* Die Mechanismen: der ganze Pfahl starr, oder Gelenke, unter denen er
  stillsteht -- wie für kurze und lange Pfähle üblich. Die Norm verlangt
  nur, R_tr,k aus Erdwiderstand und innerem Widerstand zu rechnen.

EINHEITEN:
SI-Basis.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

from opencivil.pfahl import buch
from opencivil.pfahl.boden import Profil

#: So weit liegen die Knoten höchstens auseinander, auf denen die Lage eines Bruchs
#: gesucht wird, in m: H ändert sich dort kaum, ein Zentimeter verschiebt es um
#: weniger, als je gedruckt wird.
SCHRITT = 0.01


@dataclass(frozen=True)
class Festigkeit:
    """Womit eine Schicht dem Pfahl quer widersteht -- in SI, φ' im Bogenmass."""

    drainiert: bool
    phi: float = 0.0
    c: float = 0.0
    s_u: float = 0.0

    @property
    def K_p(self) -> float:
        """Der Erdwiderstandsbeiwert nach Rankine, ohne Wandreibung -- undrainiert eins."""
        if not self.drainiert:
            return 1.0
        s = math.sin(self.phi)
        return (1.0 + s) / (1.0 - s)

    def erddruecke(self, sigma: float) -> Tuple[float, float]:
        """
        e_p und e_a unter der Spannung ``sigma`` -- drainiert der wirksamen,
        undrainiert der totalen, mit K_p = K_a = 1 und s_u statt c'.
        """
        K_p = self.K_p
        k = self.c if self.drainiert else self.s_u
        return (K_p * sigma + 2.0 * k * math.sqrt(K_p),
                sigma / K_p - 2.0 * k / math.sqrt(K_p))


@dataclass(frozen=True)
class Linie:
    """Ein Stück des Pfahls, auf dem p_E,k linear verläuft -- z ab Terrain, p je Meter Pfahl."""

    schicht: int
    """Die Schicht, in der es liegt: ihr Platz in der Liste, ab null."""

    oben: float
    unten: float
    p_oben: float
    p_unten: float

    def p(self, z: float) -> float:
        return self.p_oben + (self.p_unten - self.p_oben) * (z - self.oben) / (self.unten - self.oben)


class Erdwiderstand:
    """Siehe Dateikopf: p_E,k über die Tiefe, z ab Terrain."""

    def __init__(self, profil: Profil, festigkeiten: Sequence[Festigkeit], D: float) -> None:
        self.profil = profil
        self.festigkeiten = tuple(festigkeiten)
        self.breite = buch.BREITE_SCHMAL * D

    def erddruecke(self, z: float, schicht: int) -> Tuple[float, float]:
        """e_p und e_a in der Tiefe z, gerechnet mit der Schicht ``schicht``."""
        f = self.festigkeiten[schicht]
        sigma = self.profil.sigma_v_wirksam(z) if f.drainiert else self.profil.sigma_v(z)
        return f.erddruecke(sigma)

    def je_meter(self, z: float, schicht: int) -> float:
        """p_E,k = b' · (e_p − max(0; e_a)): vorne passiv, hinten aktiv oder ein Spalt."""
        e_p, e_a = self.erddruecke(z, schicht)
        return self.breite * (e_p - max(0.0, e_a))

    def bei(self, z: float) -> float:
        """p_E,k in der Tiefe z -- an der Grenze zweier Schichten der kleinere Wert."""
        return min(self.je_meter(z, i) for i, (oben, unten) in enumerate(self.profil.grenzen)
                   if oben - 1e-9 <= z <= unten + 1e-9)

    def linien(self, oben: float, unten: float) -> List[Linie]:
        """
        p_E,k von ``oben`` bis ``unten`` als lineare Stücke: je Schicht und
        Seite des Wassers eines (:meth:`~.boden.Profil.stuecke`), noch einmal
        geteilt, wo e_a das Vorzeichen wechselt.
        """
        heraus: List[Linie] = []
        for st in self.profil.stuecke(oben, unten):
            a_o = self.erddruecke(st.z_o, st.schicht)[1]
            a_u = self.erddruecke(st.z_u, st.schicht)[1]
            punkte = [st.z_o, st.z_u]
            if a_o * a_u < 0.0:
                punkte.insert(1, st.z_o + st.h * a_o / (a_o - a_u))
            heraus += [Linie(st.schicht, a, b, self.je_meter(a, st.schicht),
                             self.je_meter(b, st.schicht))
                       for a, b in zip(punkte, punkte[1:])]
        return heraus


# ===========================================================================
# Die Brüche
# ===========================================================================


@dataclass(frozen=True)
class Bruch:
    """Ein Mechanismus an seiner ungünstigsten Lage: was bricht, wo, und bei welcher Querkraft."""

    was: str
    lage: Optional[float]
    """s_r oder s_h ab Kopf, in m -- ``None`` bei der Verschiebung."""

    H: float


class _Integrale:
    """
    Vom Kopf bis zu jedem Knoten ∫ p ds und ∫ p · s ds, s ab Kopf -- exakt,
    weil p zwischen zwei Knoten linear ist.
    """

    def __init__(self, linien: Sequence[Linie], kopf: float, schritt: float) -> None:
        self.s, self.P, self.Q = [0.0], [0.0], [0.0]
        for li in linien:
            n = max(1, math.ceil((li.unten - li.oben) / schritt - 1e-9))
            for k in range(n):
                z0 = li.oben + (li.unten - li.oben) * k / n
                z1 = li.oben + (li.unten - li.oben) * (k + 1) / n
                p0, p1 = li.p(z0), li.p(z1)
                s0, s1 = z0 - kopf, z1 - kopf
                self.P.append(self.P[-1] + (s1 - s0) * (p0 + p1) / 2.0)
                self.Q.append(self.Q[-1] + (s1 - s0) / 6.0
                              * (p0 * (2.0 * s0 + s1) + p1 * (s0 + 2.0 * s1)))
                self.s.append(s1)

    def oben(self, j: int) -> float:
        """∫₀^s_j p · (s_j − s) ds: der Boden über dem Knoten, um ihn gedreht."""
        return self.s[j] * self.P[j] - self.Q[j]

    def unten(self, j: int) -> float:
        """∫_s_j^L p · (s − s_j) ds: der Boden darunter."""
        return (self.Q[-1] - self.Q[j]) - self.s[j] * (self.P[-1] - self.P[j])


def brueche(linien: Sequence[Linie], kopf: float, M_R: float, *, eingespannt: bool,
            e: float = 0.0, schritt: float = SCHRITT) -> List[Bruch]:
    """
    Die Mechanismen des Dateikopfs, jeder an seiner ungünstigsten Lage. Die
    ``linien`` reichen vom Kopf in der Tiefe ``kopf`` bis zum Fuss; ``e`` ist
    beim frei drehbaren Kopf der Hebel des Moments, M_Ed / H_Ed.
    """
    I = _Integrale(linien, kopf, schritt)

    def kleinster(was: str, werte: Iterable[Tuple[int, float]]) -> Bruch:
        j, H = min(werte, key=lambda x: x[1])
        return Bruch(was, I.s[j], H)

    knoten = range(1, len(I.s))
    verschiebung = Bruch("Verschiebung des ganzen Pfahls", None, I.P[-1])
    if eingespannt:
        return [
            kleinster("Gelenk am Kopf, darunter Drehung",
                      ((j, (M_R + I.oben(j) + I.unten(j)) / I.s[j]) for j in knoten)),
            kleinster("Gelenke am Kopf und im Pfahl",
                      ((j, (2.0 * M_R + I.oben(j)) / I.s[j]) for j in knoten)),
            verschiebung,
        ]
    hebel = [abs(s + e) for s in I.s]
    return [
        kleinster("Drehung des ganzen Pfahls",
                  ((j, (I.oben(j) + I.unten(j)) / hebel[j]) for j in range(len(I.s))
                   if hebel[j] > 1e-9)),
        kleinster("Gelenk im Pfahl",
                  ((j, (M_R + I.oben(j)) / hebel[j]) for j in knoten if hebel[j] > 1e-9)),
        verschiebung,
    ]
