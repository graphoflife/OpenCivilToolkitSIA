"""
opencivil/mauerwerk/schub.py -- die Nachweise des Schubs in der Ebene einer Wand.

VERANTWORTUNG:
Je Pfeiler und Kombination die beiden Bedingungen des einfachen Nachweises
nach SIA 266:2015, 4.3.2.2: die geneigte Druckstrebe (:class:`Schub`,
Gl. (13)) und das Gleiten in der Lagerfuge (:class:`Gleiten`, Gl. (14)).
Querkraft, Normalkraft und Moment am Fuss kommen aus dem Abtrag der Wand
(:mod:`~opencivil.mauerwerk.lasten`, :mod:`~opencivil.mauerwerk.scheibe`);
ohne Querkraft gibt es keinen Nachweis. Wie bei der Normalkraft lässt sich
keiner führen, wo der Pfeiler nicht gedrückt ist (4.1.2).

DIE DRUCKSTREBE (Gl. (13)):
Die Resultierende aus N_xd und V_d geht als Strebe durch den Pfeiler,
geneigt um tan α = V_d / N_xd. Geneigt trägt das Mauerwerk nur f_yd
(Figur 7), am Fuss auf der gedrückten Länge l_2 = l_w − 2 · M_z2d / N_xd:
N_xd ≤ f_yd · l_2 · t · cos² α. Steht die Normalkraft quer zur Wand
ausmittig, gilt 4.3.3.1: die Strebe trägt nur auf der Dicke
t_nom = t_w − 2 · e_z, mit e_z der grössten Ausmitte der verformten Wand
unter N_xd auf der Länge l_2 (4.3.1.3, :mod:`~opencivil.mauerwerk.knicken`);
findet die Wand dort kein Gleichgewicht, gilt vereinfacht
t_nom = 0.25 · t_w. Die Norm verlangt mit t_nom den Nachweis nach Figur 9
(Gl. (18)); das Werkzeug rechnet ihn mit dem einfachen der Gl. (13), denn
der erweiterte nach 4.3.2.3 legt der Strebe nur Druck zu (Gl. (15)) -- nach
Vorgabe, nicht nachgeschlagen, auf der sicheren Seite.

DAS GLEITEN (Gl. (14)):
Steiler als arctan μ_d kann die Strebe nicht stehen: V_d / N_xd ≤ μ_d,
nach V_d aufgelöst V_d ≤ V_Rd = μ_d · N_xd.

EINHEITEN:
SI-Basis.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from opencivil.core.einheiten import GRAD, Groesse
from opencivil.core.nachweis import NICHT_FUEHRBAR
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.mauerwerk import knicken
from opencivil.mauerwerk.lasten import Abtrag
from opencivil.mauerwerk.modell import Pfeiler
from opencivil.mauerwerk.nachweise import (
    NULL, Stelle, Stellenausgang, Wandnachweis, ausmitten, ausmittig, gedrueckte_laenge,
    knicken_unter, ohne_einwirkung, pfeiler_von, zug,
)

if TYPE_CHECKING:
    from opencivil.mauerwerk.werk import Wandbefund

#: Wo die Regeln stehen.
REFERENZ_GL_13 = "SIA 266:2015, 4.3.2.2, Gl. (13), Figur 7 und 8"
REFERENZ_GL_14 = "SIA 266:2015, 4.3.2.2, Gl. (14)"
REFERENZ_T_NOM = "SIA 266:2015, 4.3.3.1"

#: So dünn rechnet eine Wand mit ausmittiger Normalkraft höchstens, in Dicken -- 4.3.3.1.
T_NOM_MIN = 0.25


class Schubnachweis(Wandnachweis):
    """
    Was beide teilen: Querkraft und Normalkraft am Fuss -- ohne Querkraft
    kein Nachweis, ohne Druck keiner, der sich führen lässt.
    """

    def stelle(self, p: Protokoll, befund: "Wandbefund", s: Stelle) -> Stellenausgang:
        pf = pfeiler_von(befund, s.ort)
        a = befund.kombinationen[s.kombination]
        zw = Zwischenwerte(f"{self.id}.{s.kennung}")
        p.titel(f"{self.LANGNAME} – {s.name}", ebene=3)
        V = zw.kraft("V_d", "V_d", abs(a.V[pf.name]), "Querkraft in der Wandebene, Betrag")
        p.wert(V, titel="Querkraft des Pfeilers in der Wandebene, aus dem Lastabtrag – ihr Betrag")
        if V.groesse.si <= NULL:
            return ohne_einwirkung(p, s)
        N = zw.kraft("N_xd", "N_{xd}", a.N[pf.name], "Normalkraft am Fuss des Pfeilers")
        p.wert(N, titel="Normalkraft am Fuss des Pfeilers, aus dem Lastabtrag")
        ohne_druck = zug(p, s, pf, a)
        if ohne_druck is not None:
            return ohne_druck
        if N.groesse.si <= NULL:
            grund = (f"Der Pfeiler {pf.name} ist nicht gedrückt: ohne Normalkraft trägt "
                     f"unbewehrtes Mauerwerk keinen Schub – der Nachweis lässt sich nicht führen.")
            p.warnung(grund)
            return Stellenausgang(stelle=s, ausgang=NICHT_FUEHRBAR, begruendung=grund)
        return self.gedrueckt(p, befund, s, pf, a, zw, V, N)

    def gedrueckt(self, p: Protokoll, befund: "Wandbefund", s: Stelle, pf: Pfeiler, a: Abtrag,
                  zw: Zwischenwerte, V: Wert, N: Wert) -> Stellenausgang:
        """Der Nachweis eines gedrückten Pfeilers mit Querkraft."""
        raise NotImplementedError


class Schub(Schubnachweis):
    """Die geneigte Druckstrebe -- siehe Dateikopf."""

    LANGNAME = "Schub"
    ART = "V"
    FELD = "schub"

    def ansatz(self, p: Protokoll, befund: "Wandbefund") -> None:
        p.erklaerung(
            "Die Querkraft geht mit der Normalkraft als geneigte Druckstrebe durch den Pfeiler. "
            "Geneigt trägt Mauerwerk nur f_yd (Figur 7), und am Fuss nur auf der gedrückten "
            "Länge l_2, wo die Resultierende hinkommt. Darum vergleicht der Nachweis "
            "Normalkräfte: je schräger die Strebe, desto weniger Normalkraft trägt sie.")
        p.annahme("N_xd, V_d und M_z2d gelten am Fuss des Pfeilers. Steht die Normalkraft quer "
                  "zur Wand ausmittig, rechnet das Werkzeug den einfachen Nachweis der Gl. (13) "
                  "mit der Dicke t_nom nach 4.3.3.1 statt mit Figur 9: der erweiterte Nachweis "
                  "nach 4.3.2.3 legt der Strebe nur Druck zu – nach Vorgabe, nicht "
                  "nachgeschlagen, auf der sicheren Seite.")

    def gedrueckt(self, p: Protokoll, befund: "Wandbefund", s: Stelle, pf: Pfeiler, a: Abtrag,
                  zw: Zwischenwerte, V: Wert, N: Wert) -> Stellenausgang:
        alpha = zw.wert("alpha", r"\alpha",
                        Groesse.aus_si(math.atan(V.groesse.si / N.groesse.si), GRAD), 1,
                        "Neigung der Druckstrebe")
        p.formel(alpha, r"\arctan\frac{@V}{@N}", {"V": V, "N": N},
                 titel="Neigung der Druckstrebe gegen die Lotrechte, in Grad",
                 referenz=REFERENZ_GL_13, name="Neigung der Druckstrebe in einem Pfeiler")
        l_w = zw.laenge("l_w", "l_w", pf.b, "Breite des Pfeilers", stellen=0)
        l_2 = gedrueckte_laenge(p, zw, a, pf, N, l_w)
        if l_2.groesse.si <= 0.0:
            p.text("l_2 ≤ 0: die Resultierende liegt ausserhalb des Pfeilers – er kippt, und "
                   "die Strebe trägt nichts.")
            N_Rd = zw.kraft("N_Rd", "N_{Rd}", 0.0, "Widerstand der Druckstrebe")
        else:
            t_nom = self._dicke(p, zw, befund, a, pf, N, l_2)
            f_yd = zw.spannung("f_yd", "f_{yd}", befund.werte.f_yd * 1e6,
                               "Druckfestigkeit der Wand parallel zu den Lagerfugen", stellen=2)
            N_Rd = zw.kraft("N_Rd", "N_{Rd}", f_yd.groesse.si * l_2.groesse.si
                            * t_nom.groesse.si * math.cos(alpha.groesse.si) ** 2,
                            "Widerstand der Druckstrebe")
            p.formel(N_Rd, r"@f \cdot @l \cdot @t \cdot \cos^{2} @a",
                     {"f": f_yd, "l": l_2, "t": t_nom, "a": alpha}, referenz=REFERENZ_GL_13,
                     name="Widerstand der Druckstrebe in einem Pfeiler")
        v = self.vergleichen(p, N, N_Rd, self.d_ausnutzung[s.name])
        return Stellenausgang(stelle=s, ausgang=v, begruendung=self.satz(v, ("N_xd", "N_Rd")))

    @staticmethod
    def _dicke(p: Protokoll, zw: Zwischenwerte, befund: "Wandbefund", a: Abtrag, pf: Pfeiler,
               N: Wert, l_2: Wert) -> Wert:
        """t_nom: auf dieser Dicke trägt die Strebe -- t_w, wo die Normalkraft mittig steht."""
        t = befund.t
        t_w = zw.laenge("t_w", "t_w", t, "Dicke der Wand", stellen=0)
        e_o, e_u = ausmitten(p, zw, befund, a, pf)
        if not ausmittig(e_o, e_u):
            p.text("Quer zur Wand steht die Normalkraft mittig: die Strebe trägt auf der ganzen "
                   "Dicke, t_nom = t_w (4.3.2).")
            return zw.laenge("t_nom", "t_{nom}", t, "Dicke, auf der die Strebe trägt", stellen=0)
        erg = knicken_unter(befund, l_2.groesse.si, N.groesse.si, e_o, e_u)
        if erg.bei_n_d is None:
            p.text("Auf der Länge l_2 findet die Wand unter N_xd kein Gleichgewicht – siehe den "
                   "Nachweis der Normalkraft: vereinfacht t_nom = 0.25 · t_w (4.3.3.1).")
            t_nom = zw.laenge("t_nom", "t_{nom}", T_NOM_MIN * t, "Dicke, auf der die Strebe trägt",
                              stellen=1)
            p.formel(t_nom, r"0.25 \cdot @t", {"t": t_w}, referenz=REFERENZ_T_NOM,
                     name="Dicke einer Schubwand mit ausmittiger Normalkraft, vereinfacht")
            return t_nom
        e_z = zw.laenge("e_z", "e_z", abs(erg.bei_n_d.e_max) * t,
                        "Grösste Ausmitte quer zur Wand unter N_xd", stellen=1)
        p.wert(e_z, titel="Grösste Ausmitte der verformten Wand unter N_xd, auf der Länge l_2 "
                          "nach Theorie 2. Ordnung gerechnet", referenz=knicken.REFERENZ_FIGUR_3)
        t_nom = zw.laenge("t_nom", "t_{nom}", t - 2.0 * e_z.groesse.si,
                          "Dicke, auf der die Strebe trägt", stellen=1)
        p.formel(t_nom, r"@t - 2 \cdot @e", {"t": t_w, "e": e_z}, referenz=REFERENZ_T_NOM,
                 name="Dicke einer Schubwand mit ausmittiger Normalkraft")
        return t_nom


class Gleiten(Schubnachweis):
    """Das Gleiten in der Lagerfuge -- siehe Dateikopf."""

    LANGNAME = "Gleiten"
    ART = "G"
    FELD = "gleiten"

    def ansatz(self, p: Protokoll, befund: "Wandbefund") -> None:
        p.erklaerung(
            "Steiler als arctan μ_d kann die Druckstrebe nicht stehen: sonst gleitet der "
            "Pfeiler in einer Lagerfuge. Die Reibung trägt μ_d · N_xd.")

    def gedrueckt(self, p: Protokoll, befund: "Wandbefund", s: Stelle, pf: Pfeiler, a: Abtrag,
                  zw: Zwischenwerte, V: Wert, N: Wert) -> Stellenausgang:
        mu = zw.zahl("mu_d", r"\mu_d", befund.werte.mu_d, "Reibungsbeiwert der Lagerfugen",
                     stellen=2)
        p.wert(mu, titel="Bemessungswert des Reibungsbeiwerts in den Lagerfugen, aus dem "
                         "Mauerwerk", referenz="SIA 266:2015, 4.2.1.3")
        V_Rd = zw.kraft("V_Rd", "V_{Rd}", mu.groesse.si * N.groesse.si, "Widerstand gegen Gleiten")
        p.formel(V_Rd, r"@mu \cdot @N", {"mu": mu, "N": N},
                 titel="Widerstand gegen Gleiten: Gl. (14), V_d / N_xd ≤ μ_d, nach V_d aufgelöst",
                 referenz=REFERENZ_GL_14, name="Widerstand eines Pfeilers gegen Gleiten")
        v = self.vergleichen(p, V, V_Rd, self.d_ausnutzung[s.name])
        return Stellenausgang(stelle=s, ausgang=v, begruendung=self.satz(v, ("V_d", "V_Rd")))
