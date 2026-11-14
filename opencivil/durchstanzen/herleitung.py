"""
opencivil/durchstanzen/herleitung.py -- wie ein Nachweisschnitt in der Herleitung steht.

VERANTWORTUNG:
Die Schritte, die jeder Schnitt durchläuft -- was von ihm nicht zählt, k_e
nach (57), der wirksame Umfang, die Querkraft und der Widerstand (58) --, einmal
geschrieben: für den Schnitt um die Stütze (:mod:`.nachweis`), um die
äussersten Anker und um einen Stahlpilz (:mod:`.mit_bewehrung`). Die Zahlen
kommen aus der :class:`~.pruefung.Schnittpruefung`, sie werden hier nicht
gerechnet. Weil es dieselben Formeln sind, hat jede in der Formelsammlung
eine Seite, gleich an welchem Schnitt sie steht.

DIE ZEICHEN (:class:`Index`):
Um die Stütze u_0, u_red, u, V_{d,red} und V_{Rd,c}; aussen um die Anker mit
«out», um den Pilz mit «P», der Index zuletzt: u_{red,out}, V_{d,P} ...

EINHEITEN:
SI-Basis.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

from opencivil.core.berechnung import Eingaben
from opencivil.core.einheiten import M2, Groesse
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.durchstanzen.pruefung import Schnittpruefung, beiwert_k_e, kreisdurchmesser
from opencivil.durchstanzen.schnitt import Auswertung


@dataclass(frozen=True)
class Index:
    """
    Wie die Werte eines Schnitts heissen: ``zeichen`` hängt am Symbol -- leer um
    die Stütze, «out» aussen um die Anker, «P» um den Pilz --, ``vorsilbe`` an
    den Namen der Zwischenwerte, damit die Leisten um die Stütze und um den
    Pilz nebeneinander stehen können.
    """

    zeichen: str = ""
    vorsilbe: str = ""

    def name(self, grund: str) -> str:
        return f"{self.vorsilbe}{self.zeichen}_{grund}" if self.zeichen else f"{self.vorsilbe}{grund}"

    def unten(self, *teile: str) -> str:
        """Der Index eines Symbols, der eigene zuletzt: ``unten("red")`` -- «red» oder «red,out»."""
        return ",".join(t for t in (*teile, self.zeichen) if t)

    def symbol(self, grund: str, *teile: str) -> str:
        """``symbol("V", "d")`` -- «V_{d,out}»; ohne Index «V_d», «u»."""
        unten = self.unten(*teile)
        if not unten:
            return grund
        return f"{grund}_{{{unten}}}" if "," in unten or len(unten) > 1 else f"{grund}_{unten}"


STUETZE = Index()


def rand(p: Protokoll, w: Zwischenwerte, a: Auswertung, *, ix: Index, titel: str,
         referenz: str) -> Wert:
    """u_0: der Schnitt, soweit er in der Platte liegt."""
    u_0 = w.laenge(ix.name("u_0"), ix.symbol("u", "0"), a.in_der_platte, stellen=0)
    p.wert(u_0, titel=titel, referenz=referenz)
    return u_0


def abzuege(p: Protokoll, w: Zwischenwerte, a: Auswertung, u_0: Wert, *, ix: Index,
            ecken_text: str, ecken_referenz: str, ecken: bool = True) -> Wert:
    """
    Was vom Schnitt nicht zählt -- neben den Ecken und hinter Aussparungen
    (Figur 23) -- und was bleibt, u_red. ``ecken`` falsch, wo u_0 die Ecken
    schon nicht mitzählt (die Formeln um Wandende und Wandecke). Die Zahl ist
    die der Auswertung, mit der auch die Prüfung rechnet.
    """
    teile = [("u_0", u_0)]
    if ecken and a.an_ecken > 1e-6:
        du_E = w.laenge(ix.name("du_E"), rf"\Delta {ix.symbol('u', 'E')}", a.an_ecken, stellen=0)
        p.erklaerung(ecken_text)
        p.wert(du_E, titel="Was neben den Ecken nicht zählt", referenz=ecken_referenz)
        teile.append(("du_E", du_E))
    if a.hinter_aussparungen > 1e-6:
        du_A = w.laenge(ix.name("du_A"), rf"\Delta {ix.symbol('u', 'A')}", a.hinter_aussparungen,
                        stellen=0)
        p.erklaerung(
            "Hinter einer Aussparung, die näher als 5·d_v am Schnitt liegt, zählt nicht, "
            "was zwischen den beiden Strahlen von der Stützenachse an ihr vorbei liegt.")
        p.wert(du_A, titel="Was hinter Aussparungen nicht zählt",
               referenz="SIA 262:2025, 4.3.6.2.3, Figur 23d")
        teile.append(("du_A", du_A))
    u_red = w.laenge(ix.name("u_red"), ix.symbol("u", "red"), a.u, stellen=0)
    p.formel(u_red, " - ".join(f"@{n}" for n, _ in teile), dict(teile),
             titel="Nachweisschnitt ohne das, was nicht zählt" if len(teile) > 1
             else "Nichts mindert den Schnitt",
             referenz="SIA 262:2025, 4.3.6.2.3", name="Nachweisschnitt ohne das, was nicht zählt")
    return u_red


def k_e(p: Protokoll, w: Zwischenwerte, a: Auswertung, e_u: Tuple[float, float], *,
        ix: Index) -> Wert:
    """
    k_e nach (57): b aus der Fläche im Schnitt, e_u von seinem Schwerpunkt
    zur Resultierenden der Auflagerkraft -- je Komponente, in m.
    """
    A = w.wert(ix.name("A_u"), ix.symbol("A", "u"), Groesse.aus_si(a.flaeche, M2), 3,
               "Fläche innerhalb des Nachweisschnitts")
    p.wert(A, titel="Fläche innerhalb des Nachweisschnitts", referenz="SIA 262:2025, Figur 22")
    b = w.laenge(ix.name("b"), ix.symbol("b"), kreisdurchmesser(a.flaeche), stellen=0)
    p.formel(b, r"\sqrt{\frac{4 \cdot @A_u}{\pi}}", {"A_u": A},
             titel="Durchmesser des flächengleichen Kreises", referenz="SIA 262:2025, 4.3.6.2.4")
    e_u_si = math.hypot(*e_u)
    e_u_w = w.laenge(ix.name("e_u"), ix.symbol("e", "u"), e_u_si, stellen=0)
    p.wert(e_u_w, titel="Exzentrizität zum Schwerpunkt des Nachweisschnitts",
           referenz="SIA 262:2025, 4.3.6.2.4")
    ergebnis = w.zahl(ix.name("k_e"), ix.symbol("k", "e"), beiwert_k_e(e_u_si, b.groesse.si),
                      stellen=3)
    p.formel(ergebnis, r"\frac{1}{1 + \frac{@e_u}{@b}}", {"e_u": e_u_w, "b": b},
             titel="Beiwert der Momentenübertragung", referenz="SIA 262:2025, 4.3.6.2.4, (57)")
    return ergebnis


def wirksam(p: Protokoll, w: Zwischenwerte, k_e: Wert, u_red: Wert, *, ix: Index,
            titel: str) -> Wert:
    """Der wirksame Umfang u = k_e · u_red."""
    u = w.laenge(ix.name("u"), ix.symbol("u"), k_e.groesse.si * u_red.groesse.si, stellen=0)
    p.formel(u, r"@k_e \cdot @u_red", {"k_e": k_e, "u_red": u_red}, titel=titel,
             referenz="SIA 262:2025, 4.3.6.2.3", name="Wirksamer Umfang des Nachweisschnitts")
    return u


def querkraft(p: Protokoll, w: Zwischenwerte, e: Eingaben, s: Schnittpruefung, *, ix: Index,
              titel_last: str, titel: str) -> Wert:
    """
    Die Querkraft, die den Schnitt kreuzt: V_d ohne die Flächenlast darin
    (4.3.6.2.6). ``titel_last`` sagt, was die Flächenlast ist.
    """
    V_d, q_d = e["V_d"], e["q_d"]
    symbol = ix.symbol("V", "d") if ix.zeichen else "V_{d,red}"
    if q_d.groesse.si <= 0.0:
        ergebnis = w.kraft(ix.name("V_d_red"), symbol, s.V_d_red)
        p.formel(ergebnis, "@V_d", {"V_d": V_d}, titel=f"{titel}: keine Flächenlast abgezogen",
                 referenz="SIA 262:2025, 4.3.6.2.6",
                 name="Bemessungswert der Querkraft im Nachweisschnitt")
        return ergebnis
    A = w.wert(ix.name("A_q"), ix.symbol("A", "q"), Groesse.aus_si(s.flaeche, M2), 3,
               "Fläche innerhalb des Schnitts, ohne Aussparungen")
    p.wert(A, titel="Fläche innerhalb des Schnitts, ohne Aussparungen")
    dV = w.kraft(ix.name("dV"), rf"\Delta {ix.symbol('V', 'd')}", q_d.groesse.si * s.flaeche)
    p.formel(dV, r"@q_d \cdot @A_q", {"q_d": q_d, "A_q": A}, titel=titel_last,
             referenz="SIA 262:2025, 4.3.6.2.6", name="Flächenlast innerhalb des Nachweisschnitts")
    ergebnis = w.kraft(ix.name("V_d_red"), symbol, s.V_d_red)
    p.formel(ergebnis, r"@V_d - @dV", {"V_d": V_d, "dV": dV}, titel=titel,
             referenz="SIA 262:2025, 4.3.6.2.6", name="Bemessungswert der Querkraft im Nachweisschnitt")
    return ergebnis


def widerstand(p: Protokoll, w: Zwischenwerte, s: Schnittpruefung, *, ix: Index, k_r: Wert,
               tau_cd: Wert, d_v: Wert, u: Wert, titel: str, referenz: str) -> Wert:
    """V_Rd,c nach (58) an diesem Schnitt."""
    V_Rd_c = w.kraft(ix.name("V_Rd_c"), ix.symbol("V", "Rd", "c"),
                     s.V_Rd_c(k_r.groesse.si, tau_cd.groesse.si), titel)
    p.formel(V_Rd_c, r"@k_r \cdot @tau_cd \cdot @d_v \cdot @u",
             {"k_r": k_r, "tau_cd": tau_cd, "d_v": d_v, "u": u}, titel=titel, referenz=referenz,
             name="Durchstanzwiderstand ohne Durchstanzbewehrung")
    return V_Rd_c
