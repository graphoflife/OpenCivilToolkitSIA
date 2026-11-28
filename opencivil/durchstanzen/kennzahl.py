"""
opencivil/durchstanzen/kennzahl.py -- was eine Durchstanzstelle ohne Durchstanzbewehrung trägt.

VERANTWORTUNG:
Die Kennzahl einer Durchstanzstelle (:class:`Durchstanzkennzahl`): der
Durchstanzwiderstand V_Rd,c am Schnittpunkt -- dort, wo die Querkraft im
Schnitt um die Stütze so gross ist wie der Widerstand, den sie selbst
zulässt. Gerechnet immer, auch ohne Einwirkung (Benutzer, 2026-11-27); der
Nachweis (:mod:`.nachweis`) bleibt, wie er ist. Ohne Stahlpilz und ohne
Durchstanzbewehrung.

DER SCHNITTPUNKT:
In Näherungsstufe 2 wachsen die Momente im Stützstreifen mit der Stützenkraft
V_d (4.3.6.4.7), mit ihnen ψ (60), und k_r (59) sinkt. Bei V_d = 0 wären ψ = 0
und k_r = 2: ein Widerstand, der nur ohne Last gilt -- im Beispiel mit C30/37
866.7 kN statt 503.6 kN. Gesucht ist darum V_d mit::

    V_d − ΔV = V_Rd,c(ψ(V_d))

ΔV ist die Flächenlast im Schnitt (4.3.6.2.6). Die linke Seite wächst mit
V_d, die rechte sinkt nie: es gibt genau einen Schnittpunkt, zwischen 0 und
V_Rd,c(ψ = 0) + ΔV. Gesucht wird er durch Halbieren, gerechnet still mit
denselben Schritten wie der Nachweis (:class:`~.nachweis.Stuetzenrechnung`);
geschrieben wird nur der letzte. Darum gilt: liegt die Querkraft eines
Nachweises bei der Kennzahl oder darunter, geht er ohne Durchstanzbewehrung
auf, sonst nicht.

In den Stufen 1 und 3 hängt ψ nicht von V_d ab, V_Rd,c gilt für jede
Stützenkraft. Gesucht wird gleich: so steht in der Herleitung auch dort, bis
zu welcher Stützenkraft es ohne Durchstanzbewehrung geht.

MIT PLATTENBEREICHEN (4.3.6.2.7):
Derselbe Schnittpunkt an jedem Schnitt, um die Stütze und an jeder Stufe
(:mod:`.stufen`), je mit seinem ΔV; es gilt der kleinste. Die Kennzahl ist
die Querkraft im Schnitt um die Stütze bei dieser Stützenkraft -- so bleibt
sie mit der Querkraft eines Nachweises vergleichbar. Liegt der Schnittpunkt
an einer Stufe, ist sie kleiner als V_Rd,c um die Stütze.

EINHEITEN:
SI-Basis.
"""

from __future__ import annotations

from typing import Callable, Dict, Optional, Tuple

from opencivil.core.berechnung import Eingabebezug, Eingaben, Kennzahlprozedur
from opencivil.core.einheiten import KN, Groesse
from opencivil.core.protokoll import Protokoll, StillesProtokoll, Zwischenwerte
from opencivil.durchstanzen import herleitung
from opencivil.durchstanzen.herleitung import STUETZE
from opencivil.durchstanzen.nachweis import Stuetzenrechnung, Stuetzenschnitt
from opencivil.durchstanzen.stelle import Durchstanzstelle, Naeherungsstufe, wirksame_stufe
from opencivil.durchstanzen.stufen import REFERENZ, Stufe

#: Wie genau die Stützenkraft am Schnittpunkt feststeht, in N.
GENAUIGKEIT = 1.0

#: Was nur der Nachweis liest: die Stützenkraft sucht die Kennzahl selbst.
NUR_IM_NACHWEIS = ("V_d",)


class Durchstanzkennzahl(Stuetzenrechnung, Kennzahlprozedur):
    """Die Kennzahl einer Durchstanzstelle -- siehe Dateikopf."""

    THEMA = "Durchstanzen"

    def __init__(self, stelle: Durchstanzstelle) -> None:
        self.stelle = stelle
        self.stufe = wirksame_stufe(stelle.flaeche, stelle.stufe)
        basis = f"{stelle.id}.kennzahlen"
        dazu = self.anlegen(basis)
        # Am Schnittpunkt heisst sie, weil der Nachweis daneben sein eigenes
        # V_Rd,c zeigt, mit ψ aus der eingegebenen Kraft.
        dazu("V_Rd_c", r"V_{Rd,c}", KN, "Durchstanzwiderstand am Schnittpunkt",
             "Durchstanzwiderstand am Schnittpunkt",
             "die grösste Querkraft im Nachweisschnitt ohne Durchstanzbewehrung, mit ψ aus "
             "derselben Stützenkraft" if self.stufe is Naeherungsstufe.ZWEI else
             f"die grösste Querkraft im Nachweisschnitt ohne Durchstanzbewehrung; ψ hängt in "
             f"{self.stufe.beschriftung} nicht von der Stützenkraft ab",
             referenz="SIA 262:2025, 4.3.6.3.1")
        bezuege = [Eingabebezug(n, stelle.id_von(n)) for n in stelle.eingaben()
                   if n not in NUR_IM_NACHWEIS]
        bezuege += [stelle.beton.bezug(k) for k in ("f_ck", "f_cd", "tau_cd")]
        bezuege += [stelle.stahl.bezug(k) for k in ("f_yd", "E_s")]
        super().__init__(basis, bezuege=bezuege, titel=f"Kennzahlen – {stelle.name}",
                         abschnitt=stelle.abschnitt)

    # -- Rechnen ------------------------------------------------------------

    def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]:
        w = Zwischenwerte(self.id)
        p.titel("Durchstanzwiderstand am Schnittpunkt")
        p.erklaerung(
            "Wie viel Querkraft der Schnitt um die Stütze ohne Durchstanzbewehrung trägt, "
            "gleich welche Einwirkung es gibt: dort, wo die Querkraft so gross ist wie der "
            "Widerstand, den sie selbst zulässt. Geht die Querkraft eines Nachweises nicht "
            "darüber, braucht er keine Durchstanzbewehrung.")
        # Die Stützenkraft sucht sie erst: vom Schnitt braucht sie hier nur ΔV.
        g = self._schnitt(e, p, w, 0.0)
        p.titel("Stützenkraft am Schnittpunkt", ebene=3)
        if self.stufe is Naeherungsstufe.ZWEI:
            p.text(
                "In Näherungsstufe 2 wachsen die Momente im Stützstreifen mit der Stützenkraft "
                "V_d, mit ihnen die Plattenrotation ψ, und V_Rd,c sinkt. Gesucht ist V_d mit "
                "V_d − ΔV = V_Rd,c(ψ(V_d)), durch Halbieren zwischen 0 und dem Widerstand bei "
                "ψ = 0, auf 1 N genau.")
        else:
            p.text(
                f"In {self.stufe.beschriftung} hängt ψ nicht von der Stützenkraft ab, V_Rd,c "
                f"gilt für jede. Hier steht, bis zu welcher Stützenkraft V_d es ohne "
                f"Durchstanzbewehrung geht: V_d − ΔV = V_Rd,c.")
        V_si, massgebend = self._schnittpunkt(e, w, g)
        if g.stufen:
            p.text("Dasselbe gilt an jedem Schnitt, um die Stütze und an jeder Stufe, je mit "
                   "seinem ΔV; es gilt die kleinste Stützenkraft. Massgebend ist hier der Schnitt "
                   + ("um die Stütze." if massgebend is None
                      else f"an der Stufe von {massgebend.bereich.titel}."))
        V_d = w.kraft("V_d", "V_d", V_si, "Stützenkraft am Schnittpunkt")
        p.wert(V_d, titel="Die grösste Stützenkraft ohne Durchstanzbewehrung", referenz="")
        definition = self.d["V_Rd_c"]
        r = self._widerstand(e, p, w, g, V_d, ergebnis=definition if massgebend is None else None)
        p.titel("Querkraft im Nachweisschnitt am Schnittpunkt", ebene=3)
        V = herleitung.querkraft(
            p, w, e, g.innen, ix=STUETZE, V_d=V_d,
            titel_last=f"{self.stelle.plattenart.last} innerhalb des Nachweisschnitts",
            titel="Querkraft im Nachweisschnitt, so gross wie V_Rd,c" if massgebend is None
            else "Querkraft im Nachweisschnitt um die Stütze")
        for st in g.stufen:
            self._stufe_schreiben(e, p, w, g, r, st, V_d=V_d)
        if massgebend is None:
            return {definition.id: r.V_Rd_c.groesse}
        p.titel("Durchstanzwiderstand am Schnittpunkt", ebene=3)
        kennzahl = definition.belegen(Groesse.aus_si(V.groesse.si, definition.einheit))
        p.formel(kennzahl, "@V", {"V": V},
                 titel=f"Die Querkraft im Nachweisschnitt um die Stütze, bei der der Schnitt an "
                       f"der Stufe von {massgebend.bereich.titel} gerade hält",
                 referenz=REFERENZ)
        return {definition.id: kennzahl.groesse}

    def _schnittpunkt(self, e: Eingaben, w: Zwischenwerte,
                      g: Stuetzenschnitt) -> Tuple[float, Optional[Stufe]]:
        """
        Die grösste Stützenkraft in N, bei der jeder Schnitt hält, und wo
        ihr Schnittpunkt liegt -- ``None``: um die Stütze. Je Schnitt still
        mit den Schritten des Nachweises.
        """
        still = StillesProtokoll()

        def widerstand(V: float, st: Optional[Stufe] = None) -> float:
            r = self._widerstand(e, still, w, g, w.kraft("V_d", "V_d", V))
            if st is None:
                return r.V_Rd_c.groesse.si
            return st.V_Rd_c(r.psi.groesse.si, r.k_g.groesse.si, r.tau_cd.groesse.si)

        punkte = [(_halbieren(g.innen.abzug, widerstand), None)]
        punkte += [(_halbieren(st.pruefung.abzug, lambda V, st=st: widerstand(V, st)), st)
                   for st in g.stufen if st.pruefung is not None]
        return min(punkte, key=lambda x: (x[0], x[1] is not None))


def _halbieren(abzug: float, widerstand: Callable[[float], float]) -> float:
    """Die Stützenkraft in N mit V_d − ΔV = V_Rd,c(V_d) an einem Schnitt -- durch Halbieren."""
    unten, oben = 0.0, widerstand(0.0) + abzug
    while oben - unten > GENAUIGKEIT:
        mitte = (unten + oben) / 2.0
        if mitte - abzug < widerstand(mitte):
            unten = mitte
        else:
            oben = mitte
    return (unten + oben) / 2.0
