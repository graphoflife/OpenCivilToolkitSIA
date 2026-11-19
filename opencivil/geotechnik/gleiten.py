"""
opencivil/geotechnik/gleiten.py -- das Gleiten eines Flachfundaments in seiner Sohle.

VERANTWORTUNG:
Der Nachweis :class:`Gleiten`: je Einwirkungskombination der
Gleitwiderstand in der Sohle nach SIA 267:2013, 8.5.2.2 -- drainiert
T_Rd = N_Ed · tan delta_d, mit delta_k = min(k_delta · phi_k; 35°) nach
8.4.1.1 und tan delta_d = tan delta_k / gamma_phi; undrainiert
T_Rd = b · L · s_u,d, Gl. (32). Das Fundament und seine Bemessungswerte
stehen in :mod:`~opencivil.geotechnik.fundament`.

EINHEITEN:
Alles in SI-Basis; die Winkel als Groessen in Grad.
"""

from __future__ import annotations

import math
from typing import List, Optional

from opencivil.core.berechnung import Ausfuehrung, Eingaben
from opencivil.core.einheiten import GRAD, Groesse
from opencivil.core.nachweis import NachweisUrteil
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.geotechnik.fundament import Fundamentnachweis
from opencivil.geotechnik.verhalten import Verhalten

#: Wie gross der Sohlreibungswinkel delta_k höchstens ist, in Grad -- SIA 267:2013, 8.4.1.1.
SOHLREIBUNG_GRENZE = 35.0


class Gleiten(Fundamentnachweis):
    """
    Der Gleitwiderstand in der Sohle je Kombination nach SIA 267:2013,
    8.5.2.2 -- drainiert aus der Reibung, undrainiert aus der Scherfestigkeit
    --, ohne Erdwiderstand, wie im Buch für eine geneigte Sohle.
    """

    THEMA = "Gleiten"
    ART = "GL"
    FELD = "gleiten"
    BODEN = {Verhalten.DRAINIERT: ("phi_k", "gamma_phi", "delta_faktor", "c_eff"),
             Verhalten.UNDRAINIERT: ("s_u_d",)}
    MASSE = ("b", "L")

    def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        p.titel("Gleiten")
        p.erklaerung(
            "Die Kraft T in der Sohle muss die Sohlfuge aufnehmen: drainiert durch "
            "Reibung zwischen Fundament und Boden, undrainiert durch die "
            "Scherfestigkeit des Bodens. Ein Erdwiderstand vor dem Fundament wird "
            "nicht angesetzt."
        )
        delta = (self._sohlreibung(e, p)
                 if self.fundament.verhalten is Verhalten.DRAINIERT else None)
        urteile: List[NachweisUrteil] = []
        for k in self.kombinationen:
            zw = Zwischenwerte(f"{self.id}.{k.kennung}")
            p.titel(f"Gleiten – {k.name}", ebene=3)
            N = zw.kraft("N_Ed", "N_{Ed}", k.N_Ed.si, "Einwirkung normal zur Sohle")
            T = zw.kraft("T_Ed", "T_{Ed}", k.T_Ed.si, "Einwirkung")
            T_Rd = self._widerstand(e, p, zw, N, delta)
            v, satz = self.vergleichen(p, k, T, T_Rd, ("T_Ed", "T_Rd"))
            urteile.append(self.urteil(self.d_ausnutzung[k.name], k.name, v, satz))
        return Ausfuehrung({}, urteile)

    def _sohlreibung(self, e: Eingaben, p: Protokoll) -> Wert:
        """delta_k nach SIA 267:2013, 8.4.1.1, und daraus der Bemessungswert delta_d."""
        werte = Zwischenwerte(self.id)
        phi_k, k_delta, gamma_phi = e["phi_k"], e["delta_faktor"], e["gamma_phi"]
        delta_k = werte.wert("delta_k", r"\delta_k", Groesse.aus_si(min(
            k_delta.groesse.si * phi_k.groesse.si, math.radians(SOHLREIBUNG_GRENZE)), GRAD), 2,
            "Sohlreibungswinkel, charakteristisch")
        p.formel(delta_k, rf"\min\left[@k \cdot @phi_k;\ {SOHLREIBUNG_GRENZE:g}^\circ\right]",
                 {"k": k_delta, "phi_k": phi_k}, titel="Sohlreibungswinkel, charakteristisch",
                 referenz="SIA 267:2013, 8.4.1.1, (27), (28)", name="Reibungswinkel der Sohlfuge")
        delta_d = werte.wert("delta_d", r"\delta_d", Groesse.aus_si(
            math.atan(math.tan(delta_k.groesse.si) / gamma_phi.groesse.si), GRAD), 2,
            "Sohlreibungswinkel, Bemessungswert")
        p.formel(delta_d, r"\arctan\left(\frac{\tan @delta_k}{@gamma_phi}\right)",
                 {"delta_k": delta_k, "gamma_phi": gamma_phi},
                 titel="Sohlreibungswinkel, Bemessungswert", referenz="SIA 267:2013, 8.5.2.2",
                 name="Bemessungswert des Sohlreibungswinkels")
        if e.g("c_eff").si > 0.0:
            p.text("Die Kohäsion zählt in der Sohlfuge nicht: SIA 267:2013, 8.4.1.2, lässt sie "
                   "nur zu, wo sicher ist, dass sie dauerhaft bleibt.")
        return delta_d

    @staticmethod
    def _widerstand(e: Eingaben, p: Protokoll, zw: Zwischenwerte, N: Wert,
                    delta: Optional[Wert]) -> Wert:
        """Drainiert die Reibung unter N, undrainiert die Scherfestigkeit auf der Sohlfläche."""
        if delta is None:
            b, L, s_u = e["b"], e["L"], e["s_u_d"]
            T_Rd = zw.kraft("T_Rd", "T_{Rd}", b.groesse.si * L.groesse.si * s_u.groesse.si,
                            "Widerstand")
            p.formel(T_Rd, r"@b \cdot @L \cdot @s_u", {"b": b, "L": L, "s_u": s_u},
                     titel="Gleitwiderstand, undrainiert", referenz="SIA 267:2013, 8.5.2.2, (32)",
                     name="Gleitwiderstand")
            return T_Rd
        T_Rd = zw.kraft("T_Rd", "T_{Rd}", N.groesse.si * math.tan(delta.groesse.si), "Widerstand")
        p.formel(T_Rd, r"@N \cdot \tan @delta", {"N": N, "delta": delta},
                 titel="Gleitwiderstand", referenz="SIA 267:2013, 8.5.2.2, (31)",
                 name="Gleitwiderstand")
        return T_Rd
