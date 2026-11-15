"""
opencivil/stabwerk3d/verlauf.py -- Schnittgroessen und Biegelinien laengs eines Stabs im Raum.

VERANTWORTUNG:
Wie :mod:`opencivil.stabwerk.verlauf`, im Raum: aus dem, was
:mod:`~opencivil.stabwerk3d.system` an den Enden jedes Teilstabs findet,
und aus seinen Lasten die Verlaeufe dazwischen -- je Teil des Stabs einmal
mit :func:`~opencivil.stabwerk.verlauf.ebener_verlauf`, dann
zusammengesetzt (:mod:`~opencivil.stabwerk3d.stab`). Die drei Teile
springen an denselben Stellen, weil jede Last in allen dreien steht.

VORZEICHEN -- M_z NACH VORGABE, NICHT NACHGESCHLAGEN:
In den Achsen des Stabs. ``N > 0`` ist Zug, ``T > 0`` dreht im Rechtssinn
um die nach aussen zeigende Normale des Schnitts. ``M_y > 0`` zieht an der
Faser auf der Seite +z, ``M_z > 0`` an der auf der Seite +y: beide Ebenen
wie die des 2D-Balkensystems, mit ``V_z = dM_y/dx`` und ``V_y = dM_z/dx``,
wo kein verteiltes Moment liegt. Die Spannung im Querschnitt ist damit
``σ = N/A + M_y·z/I_y + M_z·y/I_z``; die Rechtsschraube gaebe ``M_z`` das
andere Vorzeichen.

Verschiebungen ``u``, ``v``, ``w`` in x, y und z des Stabs, Verdrehungen
``theta_x``, ``theta_y``, ``theta_z`` im Rechtssinn um diese Achsen; dazu
``ux``, ``uy``, ``uz`` in den Achsen des Systems und die Durchbiegungen
``f_y`` und ``f_z`` gegen die Sehne zwischen den Stabenden.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from opencivil.stabwerk.verlauf import Intervall as EbenesIntervall
from opencivil.stabwerk.verlauf import NULL, Extrem, Polynom, ebener_verlauf
from opencivil.stabwerk3d import stab as st3
from opencivil.stabwerk3d.raum import Vektor, im_system, mal, minus

#: Die Schnittgroessen -- ihre Extremstellen kommen in die Proben.
SCHNITTGROESSEN = ("N", "V_y", "V_z", "T", "M_y", "M_z")

#: Was ein Intervall als Polynom traegt, ausser den Lasten.
POLYNOME = SCHNITTGROESSEN + ("u", "v", "w", "theta_x", "theta_y", "theta_z")


@dataclass
class Intervall:
    """Ein Stueck eines Stabs ohne Laststelle -- alles darauf Polynome in x ab dem Stabanfang."""

    x0: float
    x1: float
    N: Polynom
    V_y: Polynom
    V_z: Polynom
    T: Polynom
    M_y: Polynom
    M_z: Polynom
    u: Polynom
    v: Polynom
    w: Polynom
    theta_x: Polynom
    theta_y: Polynom
    theta_z: Polynom
    p_y: Polynom = field(default_factory=lambda: NULL)
    p_z: Polynom = field(default_factory=lambda: NULL)
    """Die Querlast samt Bettung in y und z des Stabs."""


def _zusammen(z: EbenesIntervall, y: EbenesIntervall, t: EbenesIntervall) -> Intervall:
    """Die drei ebenen Teile eines Stuecks als eines -- mit der Zuordnung aus :mod:`~opencivil.stabwerk3d.stab`."""
    return Intervall(z.x0, z.x1, N=z.N, V_y=y.V, V_z=z.V, T=t.N, M_y=z.M, M_z=y.M,
                     u=z.u, v=-y.v, w=-z.v, theta_x=t.u, theta_y=z.theta, theta_z=-y.theta,
                     p_y=-y.p_y, p_z=-z.p_y)


@dataclass
class Stabverlauf:
    """Ein Stab von Anfang bis Ende -- ueber alle seine Teilstaebe."""

    stab: str
    L: float
    anfang: Vektor
    achsen: Tuple[Vektor, Vektor, Vektor]
    intervalle: List[Intervall] = field(default_factory=list)

    def bei(self, x: float, links: bool = False) -> Dict[str, float]:
        """
        Die Werte an der Stelle ``x`` -- an einer Sprungstelle rechts davon,
        mit ``links`` links davon.
        """
        kandidaten = [i for i in self.intervalle if i.x0 <= x <= i.x1]
        if not kandidaten:
            kandidaten = [min(self.intervalle, key=lambda i: min(abs(i.x0 - x), abs(i.x1 - x)))]
        return self._werte(kandidaten[0] if links else kandidaten[-1], x)

    def sehne(self, groesse: str) -> Polynom:
        """Die Gerade zwischen den Werten von ``v`` oder ``w`` an den Stabenden."""
        erstes, letztes = self.intervalle[0], self.intervalle[-1]
        return Polynom.durch(0.0, getattr(erstes, groesse)(0.0),
                             self.L, getattr(letztes, groesse)(self.L))

    def _polynom(self, teil: Intervall, groesse: str) -> Polynom:
        if groesse == "f_y":
            return teil.v - self.sehne("v")
        if groesse == "f_z":
            return teil.w - self.sehne("w")
        return getattr(teil, groesse)

    def _werte(self, teil: Intervall, x: float) -> Dict[str, float]:
        werte = {"x": x}
        for groesse in POLYNOME + ("f_y", "f_z"):
            werte[groesse] = self._polynom(teil, groesse)(x)
        werte["ux"], werte["uy"], werte["uz"] = im_system(
            self.achsen, (werte["u"], werte["v"], werte["w"]))
        return werte

    def proben(self, je_stab: int = 24) -> List[Dict[str, float]]:
        """
        Werte zum Zeichnen: an beiden Seiten jeder Grenze und dazwischen so
        dicht, dass ein Stab rund ``je_stab`` Stuecke hat.
        """
        heraus = []
        for teil in self.intervalle:
            n = max(1, math.ceil(je_stab * (teil.x1 - teil.x0) / self.L))
            for i in range(n + 1):
                heraus.append(self._werte(teil, teil.x0 + (teil.x1 - teil.x0) * i / n))
        for x in self.extremstellen():
            heraus.append(self.bei(x))
        heraus.sort(key=lambda w: w["x"])
        return heraus

    def extremstellen(self) -> List[float]:
        """Wo eine Schnittgroesse im Innern eines Stuecks extrem ist."""
        return [x for teil in self.intervalle for groesse in SCHNITTGROESSEN
                for x in getattr(teil, groesse).ableitung().nullstellen(teil.x0, teil.x1)]

    def extrem(self, groesse: str) -> Extrem:
        """
        Kleinster und groesster Wert einer Groesse mit Stelle: einer
        Schnittgroesse, einer Verschiebung oder Verdrehung oder von ``f_y``
        und ``f_z``, der Durchbiegung gegen die Sehne.
        """
        werte = []
        for teil in self.intervalle:
            p = self._polynom(teil, groesse)
            stellen = [teil.x0, teil.x1] + p.ableitung().nullstellen(teil.x0, teil.x1)
            werte.extend((x, p(x)) for x in stellen)
        return Extrem(kleinst=min(werte, key=lambda w: w[1]),
                      groesst=max(werte, key=lambda w: w[1]))


def verlaeufe(fall) -> Dict[str, Stabverlauf]:
    """Je Stab sein Verlauf in diesem Fall -- aus den Teilstaeben, der Reihe nach."""
    heraus: Dict[str, Stabverlauf] = {}
    for teil in fall.teile:
        t = teil.teil
        verlauf = heraus.get(t.stab.name)
        if verlauf is None:
            verlauf = heraus[t.stab.name] = Stabverlauf(
                stab=t.stab.name, L=t.L_stab, achsen=t.achsen,
                anfang=minus(t.a.punkt, mal(t.x0, t.achsen[0])))

        def ebene(zuordnung, lasten, **steifigkeit):
            return ebener_verlauf(L=t.L, x0=t.x0, s=st3.eben(teil.s, zuordnung),
                                  d=st3.eben(teil.d, zuordnung), lasten=lasten, **steifigkeit)

        # Was eine Ebene nicht hat -- die Ebene y keine Laengskraft, die
        # Torsion keine Biegung --, rechnet mit der Steifigkeit 1: geteilt
        # wird dort nur null.
        z = ebene(st3.EBENE_Z, teil.lasten.z, EA=t.EA, EI=t.EI_y, k_quer=t.k_z,
                  k_laengs=t.k_x, laengs=t.laengs, biegung=t.biegung_z)
        y = ebene(st3.EBENE_Y, teil.lasten.y, EA=1.0, EI=t.EI_z, k_quer=t.k_y,
                  laengs=False, biegung=t.biegung_y)
        drillung = ebene(st3.TORSION, teil.lasten.t, EA=t.GI_T, EI=1.0,
                         laengs=t.torsion, biegung=False)
        verlauf.intervalle.extend(_zusammen(*teile) for teile in zip(z, y, drillung))
    for verlauf in heraus.values():
        verlauf.intervalle.sort(key=lambda i: (i.x0, i.x1))
    return heraus
