"""
opencivil/nachweis/richtungsnachweise.py -- Duktilitaet und sproedes Versagen des gezeichneten Querschnitts.

VERANTWORTUNG:
Zwei Nachweise, die wie bei der Platte dem Querschnitt gehoeren und keinem
Lastfall: Duktilitaet (``x/d``) und sproedes Versagen (``M_Rd >= M_Riss``).
Wo die Platte je Lage fragt, fragt der gezeichnete Querschnitt je Richtung:
Zug unten, oben, links, rechts -- einachsig nur unten und oben. In der
Zusammenfassung steht die unguenstigere.

Gerechnet wird bei reiner Biegung, ``N = 0``, mit dem Bruchzustand aus
:mod:`opencivil.querschnitt.interaktion`. Eine Richtung ohne Bewehrung auf
ihrer gezogenen Seite des Schwerpunkts hat keinen solchen Nachweis -- dort
steht ein Satz und kein Urteil, wie bei einer unbewehrten Lage der Platte.

ANNAHMEN:
Das Rissmoment gehoert dem ungerissenen Bruttoquerschnitt, gerechnet mit
``I_yz`` fuer die unsymmetrische Biegung; ``k_t`` mit einem Drittel der Hoehe
in Biegerichtung -- die Regel der Platte, uebertragen. Nach Vorgabe, nicht
nachgeschlagen (TODO.md).
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Eingabebezug, Eingaben, Nachweis, NachweisUrteil, grad_def, grad_formel,
)
from opencivil.core.einheiten import EINHEITSLOS, MIO_MM3, MIO_MM4, MM, Groesse
from opencivil.core.latex import Mathe, als_text, vergleich
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import WertDef, kennung_aus
from opencivil.nachweis.sproedes_versagen import (
    MOMENTENTEILER, beiwert_dicke, protokoll_zugfestigkeit,
)
from opencivil.querschnitt.analyse import Querschnittsanalyse
from opencivil.querschnitt.interaktion import Bruchpunkt, Querschnitt

#: Die Richtungen: Name, und das Moment, das so zieht (M_y, M_z).
RICHTUNGEN: Tuple[Tuple[str, float, float], ...] = (
    ("Zug unten", 1.0, 0.0),
    ("Zug oben", -1.0, 0.0),
    ("Zug links", 0.0, 1.0),
    ("Zug rechts", 0.0, -1.0),
)


def richtungen(einachsig: bool) -> Tuple[Tuple[str, float, float], ...]:
    """Einachsig nur unten und oben -- um z wird dann nicht nachgewiesen."""
    return RICHTUNGEN[:2] if einachsig else RICHTUNGEN


def bei_reiner_biegung(q: Querschnitt, M_y: float, M_z: float,
                       einachsig: bool) -> Bruchpunkt:
    """Der Bruchzustand bei N = 0 in dieser Richtung -- einachsig mit waagrechter Nulllinie."""
    if einachsig:
        return q.bei_normalkraft(-math.pi / 2.0 if M_y > 0 else math.pi / 2.0, 0.0)
    return q.in_richtung(0.0, M_y, M_z)


def _defs(basis: str, symbol: str, beschreibung: str, referenz: str,
          einachsig: bool) -> Dict[str, WertDef]:
    return {name: grad_def(f"{basis}.{kennung_aus(name)}.erfuellungsgrad",
                           rf"\alpha_{{eff,{symbol},{als_text(name)}}}",
                           f"{beschreibung} – {name}", referenz)
            for name, _, _ in richtungen(einachsig)}


class DuktilitaetQA(Nachweis):
    """``x/d <= Grenze`` bei reiner Biegung, je Richtung."""

    THEMA = "Duktilität je Richtung"
    LANGNAME = "Duktilität"

    def __init__(self, analyse: Querschnittsanalyse, *, einachsig: bool,
                 grenze: float) -> None:
        self.analyse = analyse
        self.einachsig = einachsig
        self.grenze = grenze
        basis = f"{analyse.id}.nachweis.duktilitaet"
        self.d_ausnutzung = _defs(basis, "x/d", "Erfüllungsgrad Duktilität",
                                  "SIA 262:2025, 4.1.4.2.5", einachsig)
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()),
                         bezuege=analyse.grundbezuege(),
                         titel=f"Duktilität – {analyse.name}",
                         referenz="SIA 262:2025, 4.1.4.2.5", abschnitt=analyse.abschnitt)

    def pruefe(self, e: Eingaben, p: Protokoll):
        q, _ = self.analyse.interaktion(e)
        p.erklaerung(
            "Ein Querschnitt kündigt sein Versagen an, wenn die Bewehrung fliesst, "
            "bevor der Beton bricht -- dann ist die Druckzone klein. Gemessen wird "
            "das an x/d bei reiner Biegung: x ist der Abstand der Nulllinie vom "
            "gedrücktesten Betonpunkt, d der des entferntesten gezogenen Stabs, "
            "beide senkrecht zur Nulllinie.")
        p.ansatz(r"\frac{x}{d} \le \left(\frac{x}{d}\right)_{max}",
                 titel="Duktilität", referenz="SIA 262:2025, 4.1.4.2.5")
        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        for name, M_y, M_z in richtungen(self.einachsig):
            werte = Zwischenwerte(f"{self.id}.{kennung_aus(name)}")
            d_grad = self.d_ausnutzung[name]
            punkt = bei_reiner_biegung(q, M_y, M_z, self.einachsig)
            x, d = q.druckzone(punkt)
            p.titel(name, ebene=3)
            if d <= 0.0 or not q.zugseite_bewehrt(punkt):
                p.text("Keine Bewehrung auf der gezogenen Seite → kein Nachweis.")
                ergebnis[d_grad.id] = Groesse(math.inf, EINHEITSLOS)
                continue
            verhaeltnis = x / d
            erfuellt = verhaeltnis <= self.grenze
            x_d = werte.zahl("x_d", "x/d", verhaeltnis)
            grenze = werte.zahl("grenze", r"\left(x/d\right)_{max}", self.grenze, stellen=2)
            p.formel(x_d, r"\frac{@x}{@d}",
                     {"x": werte.laenge("x", "x", x), "d": werte.laenge("d", "d", d)},
                     titel="Bezogene Druckzonenhöhe bei reiner Biegung",
                     nachsatz=vergleich(r"\le", f"{self.grenze:g}", erfuellt))
            grad = self.grenze / verhaeltnis if verhaeltnis > 0 else math.inf
            if math.isinf(grad):
                grad = 1e9
            grad_formel(p, d_grad, grad, grenze, x_d, erfuellt)
            ergebnis[d_grad.id] = Groesse(grad, EINHEITSLOS)
            urteile.append(NachweisUrteil(
                art="x/d", ziel=d_grad.id, fall=name, erfuellt=erfuellt,
                erfuellungsgrad=Groesse(grad, EINHEITSLOS),
                begruendung=f"x/d = {verhaeltnis:.3f} gegen {self.grenze:g}.",
                einwirkung=x_d, widerstand=grenze))
        self.protokoll_massgebend(p, urteile)
        return ergebnis, self.teilurteile(urteile)


class SproedesVersagenQA(Nachweis):
    """``M_Rd(N = 0) >= M_Riss`` je Richtung."""

    THEMA = "Sprödes Versagen je Richtung"
    LANGNAME = "Sprödes Versagen"

    def __init__(self, analyse: Querschnittsanalyse, *, einachsig: bool) -> None:
        self.analyse = analyse
        self.einachsig = einachsig
        basis = f"{analyse.id}.nachweis.sproede"
        self.d_ausnutzung = _defs(basis, "Riss", "Erfüllungsgrad sprödes Versagen",
                                  "SIA 262:2025, 4.4.1.3", einachsig)
        bezuege = list(analyse.grundbezuege()) + [
            Eingabebezug(k, analyse.id_von(k)) for k in ("I_y", "I_z", "I_yz")]
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()),
                         bezuege=bezuege, titel=f"Sprödes Versagen – {analyse.name}",
                         referenz="SIA 262:2025, 4.4.1.3", abschnitt=analyse.abschnitt)

    def pruefe(self, e: Eingaben, p: Protokoll):
        q, _ = self.analyse.interaktion(e)
        y_S, z_S = e.g("y_S").si, e.g("z_S").si
        I_y, I_z, I_yz = e.g("I_y").si, e.g("I_z").si, e.g("I_yz").si
        nenner = I_y * I_z - I_yz * I_yz
        p.erklaerung(
            "Ein zu schwach bewehrter Querschnitt reisst und versagt im selben "
            "Augenblick. Darum muss der bewehrte Querschnitt mehr tragen als der "
            "unbewehrte im Augenblick des Risses: M_Rd bei N = 0 mindestens das "
            "Rissmoment. Das Rissmoment gehört dem ungerissenen "
            "Bruttoquerschnitt; bei unsymmetrischer Form mit dem "
            "Deviationsmoment.")
        p.ansatz(r"\sigma(y, z) = -\frac{M_y\,(I_z z' - I_{yz} y') + "
                 r"M_z\,(I_y y' - I_{yz} z')}{I_y I_z - I_{yz}^2}"
                 r"\qquad y' = y - y_S,\ z' = z - z_S",
                 titel="Spannung im ungerissenen Querschnitt")
        p.ansatz(r"M_{Rd}(N = 0) \ge M_{Riss} = f_{ct,eff} \cdot W",
                 titel="Sprödes Versagen", referenz="SIA 262:2025, 4.4.1.3")

        ecken = self.analyse.beton_ecken
        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        for name, M_y, M_z in richtungen(self.einachsig):
            werte = Zwischenwerte(f"{self.id}.{kennung_aus(name)}")
            d_grad = self.d_ausnutzung[name]
            p.titel(name, ebene=3)
            punkt = bei_reiner_biegung(q, M_y, M_z, self.einachsig)
            _, d = q.druckzone(punkt)
            if d <= 0.0 or not q.zugseite_bewehrt(punkt):
                p.text("Keine Bewehrung auf der gezogenen Seite → kein Nachweis.")
                ergebnis[d_grad.id] = Groesse(math.inf, EINHEITSLOS)
                continue

            # Der gezogenste Betonpunkt bei einem Moment von eins in dieser Richtung.
            def einheitsspannung(p_mm) -> float:
                y_, z_ = p_mm[0] * 1e-3 - y_S, p_mm[1] * 1e-3 - z_S
                return -(M_y * (I_z * z_ - I_yz * y_) + M_z * (I_y * y_ - I_yz * z_)) / nenner
            ecke, stoff = max(ecken, key=lambda es: einheitsspannung(es[0]))
            sigma = einheitsspannung(ecke)
            W = 1.0 / sigma
            hoehe = self._hoehe(M_y != 0.0)
            k_t = beiwert_dicke(hoehe / MOMENTENTEILER)
            f_ctm_si = abs(self.analyse.kennwert(e, stoff, "f_ctm"))
            f_ct_eff_si = k_t * f_ctm_si
            M_Riss_si = f_ct_eff_si * W
            M_Rd_si = abs(punkt.M_y) if self.einachsig else punkt.moment

            p.text(f"Gezogenster Betonpunkt: y = {ecke[0]:g} mm, z = {ecke[1]:g} mm "
                   f"({stoff.name}).")
            h = werte.laenge("h", "h", hoehe)
            f_ct_eff = protokoll_zugfestigkeit(
                p, werte, k_t=k_t, f_ct_eff=f_ct_eff_si, h=h,
                f_ctm=e[self.analyse._name(stoff, "f_ctm")], teiler=MOMENTENTEILER,
                referenz="SIA 262:2025, 4.4.1.3",
                titel="Beiwert für die Höhe in Biegerichtung")
            W_wert = werte.wert("W", "W", Groesse.aus_si(W, MIO_MM3), 2)
            p.formel(W_wert, self._w_vorlage(M_y, M_z), {
                "Iy": werte.wert("Iy", "I_y", Groesse.aus_si(I_y, MIO_MM4), 1),
                "Iz": werte.wert("Iz", "I_z", Groesse.aus_si(I_z, MIO_MM4), 1),
                "Iyz": werte.wert("Iyz", "I_{yz}", Groesse.aus_si(I_yz, MIO_MM4), 1),
                "y": werte.laenge("y", "y'", ecke[0] * 1e-3 - y_S),
                "z": werte.laenge("z", "z'", ecke[1] * 1e-3 - z_S),
            }, titel="Widerstandsmoment zum gezogensten Betonpunkt")
            M_Riss = werte.moment("M_Riss", "M_{Riss}", M_Riss_si)
            p.formel(M_Riss, r"@f \cdot @W", {"f": f_ct_eff, "W": W_wert},
                     titel="Rissmoment des ungerissenen Querschnitts")
            M_Rd = werte.moment("M_Rd", "M_{Rd}", M_Rd_si)
            p.wert(M_Rd, titel="Biegewiderstand bei N = 0 in dieser Richtung")
            grad = M_Rd_si / M_Riss_si
            erfuellt = grad >= 1.0
            grad_formel(p, d_grad, grad, M_Rd, M_Riss, erfuellt)
            ergebnis[d_grad.id] = Groesse(grad, EINHEITSLOS)
            urteile.append(NachweisUrteil(
                art="Riss", ziel=d_grad.id, fall=name, erfuellt=erfuellt,
                erfuellungsgrad=Groesse(grad, EINHEITSLOS),
                begruendung="M_Rd bei N = 0 gegen das Rissmoment.",
                einwirkung=M_Riss, widerstand=M_Rd))
        self.protokoll_massgebend(p, urteile)
        return ergebnis, self.teilurteile(urteile)

    def _hoehe(self, um_y: bool) -> float:
        """Die Ausdehnung des Betons in Biegerichtung, in m: z bei M_y, y bei M_z."""
        werte = [p[1] if um_y else p[0] for p, _ in self.analyse.beton_ecken]
        return (max(werte) - min(werte)) * 1e-3

    @staticmethod
    def _w_vorlage(M_y: float, M_z: float) -> str:
        """``W = 1/σ`` bei einem Moment von eins -- je Richtung ausgeschrieben."""
        zaehler = r"@Iy \cdot @Iz - @Iyz^{2}"
        nenner = {
            (1.0, 0.0): r"@Iyz \cdot @y - @Iz \cdot @z",
            (-1.0, 0.0): r"@Iz \cdot @z - @Iyz \cdot @y",
            (0.0, 1.0): r"@Iyz \cdot @z - @Iy \cdot @y",
            (0.0, -1.0): r"@Iy \cdot @y - @Iyz \cdot @z",
        }[(M_y, M_z)]
        return rf"\frac{{{zaehler}}}{{{nenner}}}"
