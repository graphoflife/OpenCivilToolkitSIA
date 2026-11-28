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
Derselbe Schnittpunkt an jedem Schnitt, um die Stütze, an jeder Stufe
(:mod:`.stufen`) und durch verschiedene Dicken (:mod:`.weg`), je mit seinem
ΔV; es gilt der kleinste. Der Schnitt durch verschiedene Dicken wird bei
jeder Stützenkraft neu gesucht, mit ihrem ψ -- wie im Nachweis. Die
Kennzahl ist die Querkraft im Schnitt um die Stütze bei dieser Stützenkraft
-- so bleibt sie mit der Querkraft eines Nachweises vergleichbar. Liegt der
Schnittpunkt an einem anderen Schnitt, ist sie kleiner als V_Rd,c um die
Stütze.

EINHEITEN:
SI-Basis.
"""

from __future__ import annotations

import math
from typing import Callable, Dict, Optional, Tuple, Union

from opencivil.core.berechnung import Eingabebezug, Eingaben, Kennzahlprozedur
from opencivil.core.einheiten import KN, Groesse
from opencivil.core.protokoll import Protokoll, StillesProtokoll, Zwischenwerte
from opencivil.core.sprache import aufgezaehlt
from opencivil.durchstanzen import herleitung, weg
from opencivil.durchstanzen.herleitung import STUETZE
from opencivil.durchstanzen.nachweis import Stuetzenrechnung, Stuetzenschnitt, Widerstand
from opencivil.durchstanzen.stelle import Durchstanzstelle, Naeherungsstufe, wirksame_stufe
from opencivil.durchstanzen.stufen import REFERENZ, Stufe
from opencivil.durchstanzen.weg import Wegschnitt

#: Wie genau die Stützenkraft am Schnittpunkt feststeht, in N.
GENAUIGKEIT = 1.0

#: Was nur der Nachweis liest: die Stützenkraft sucht die Kennzahl selbst.
NUR_IM_NACHWEIS = ("V_d",)

Schnittort = Optional[Union[Stufe, Wegschnitt]]
"""Wo der Schnittpunkt liegt: an einer Stufe oder durch verschiedene Dicken -- ``None``: um die
Stütze."""


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
        if g.stufen or g.netz is not None:
            orte = ["um die Stütze", *(["an jeder Stufe"] if g.stufen else []),
                    *([weg.NAME] if g.netz is not None else [])]
            p.text(f"Dasselbe gilt an jedem Schnitt, {aufgezaehlt(orte)}, je mit seinem ΔV; es "
                   f"gilt die kleinste Stützenkraft. Massgebend ist hier der Schnitt "
                   f"{'um die Stütze' if massgebend is None else massgebend.wo}.")
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
        if g.netz is not None:
            ws = g.netz.schnitt(*_beiwerte(r))
            if ws is not None:
                self._weg_schreiben(e, p, w, g, r, ws, V_d=V_d)
            else:
                p.titel(f"Schnitt {weg.NAME}", ebene=3)
                p.text(g.netz.warum_keiner)
        if massgebend is None:
            return {definition.id: r.V_Rd_c.groesse}
        p.titel("Durchstanzwiderstand am Schnittpunkt", ebene=3)
        kennzahl = definition.belegen(Groesse.aus_si(V.groesse.si, definition.einheit))
        # Der Name steht fest: aus dem Titel würde er mit dem Ort des
        # Schnittpunkts länger als 100 Zeichen, und die Formelsammlung brach
        # ab (bis 2026-11-28, wo eine Stufe massgebend war).
        p.formel(kennzahl, "@V", {"V": V},
                 titel=f"Die Querkraft im Nachweisschnitt um die Stütze, bei der der Schnitt "
                       f"{massgebend.wo} gerade hält",
                 referenz=REFERENZ, name="Durchstanzwiderstand am Schnittpunkt")
        return {definition.id: kennzahl.groesse}

    def _schnittpunkt(self, e: Eingaben, w: Zwischenwerte,
                      g: Stuetzenschnitt) -> Tuple[float, Schnittort]:
        """
        Die grösste Stützenkraft in N, bei der jeder Schnitt hält, und wo
        ihr Schnittpunkt liegt. Je Schnitt still mit den Schritten des
        Nachweises; der Schnitt durch verschiedene Dicken zuletzt, nur bis
        zur kleinsten Kraft der anderen.
        """
        still = StillesProtokoll()

        def widerstand(V: float) -> Widerstand:
            return self._widerstand(e, still, w, g, w.kraft("V_d", "V_d", V))

        def an_der_stufe(st: Stufe) -> Callable[[float], float]:
            return lambda V: st.V_Rd_c(*_beiwerte(widerstand(V))) + st.pruefung.abzug - V

        punkte = [(_halbieren(lambda V: widerstand(V).V_Rd_c.groesse.si + g.innen.abzug - V),
                   None)]
        punkte += [(_halbieren(an_der_stufe(st)), st) for st in g.stufen if st.pruefung is not None]
        V, massgebend = min(punkte, key=lambda x: (x[0], x[1] is not None))
        if g.netz is None:
            return V, massgebend

        def am_weg(V: float) -> float:
            werte = _beiwerte(widerstand(V))
            ws = g.netz.schnitt(*werte)
            return math.inf if ws is None else ws.V_Rd_c(*werte) + ws.last.abzug - V

        if am_weg(V) >= 0.0:
            return V, massgebend
        V_W = _halbieren(am_weg, V)
        ws = g.netz.schnitt(*_beiwerte(widerstand(V_W)))
        return (V, massgebend) if ws is None else (V_W, ws)


def _beiwerte(r: Widerstand) -> Tuple[float, float, float]:
    """ψ, k_g und τ_cd an der Stütze -- was jeder Schnitt für seinen Widerstand braucht."""
    return r.psi.groesse.si, r.k_g.groesse.si, r.tau_cd.groesse.si


def _halbieren(rest: Callable[[float], float], oben: Optional[float] = None) -> float:
    """
    Die Stützenkraft in N, bei der ``rest(V)`` null wird -- der Widerstand
    eines Schnitts und ΔV, weniger V --, durch Halbieren zwischen 0 und
    ``oben``. Ohne ``oben`` bis zum Rest bei V = 0: dort ist er sicher
    aufgebraucht, denn der Widerstand sinkt nie mit V (Dateikopf).
    """
    unten, oben = 0.0, rest(0.0) if oben is None else oben
    while oben - unten > GENAUIGKEIT:
        mitte = (unten + oben) / 2.0
        if rest(mitte) > 0.0:
            unten = mitte
        else:
            oben = mitte
    return (unten + oben) / 2.0
