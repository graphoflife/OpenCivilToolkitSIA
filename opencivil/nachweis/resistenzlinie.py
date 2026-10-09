"""
opencivil/nachweis/resistenzlinie.py -- die Linie, gegen die der M-N-Nachweis haelt.

VERANTWORTUNG:
Eine Schnittstelle fuer beide Arten Resistenzlinie, damit der Nachweis und
alles, was an ihm mitliest -- Querkraft, sproedes Versagen, Knicken --, nicht
fragen muss, welche er vor sich hat:

* :class:`Handlinie` -- das Polygon der Handrechnung
  (:mod:`opencivil.nachweis.handrechnung`): wenige Eckpunkte, dazwischen
  geradlinig interpoliert. Jede Zahl laesst sich von Hand nachrechnen.
* :class:`Ebenenlinie` -- der Rand des Dehnungsfaechers
  (:mod:`opencivil.nachweis.dehnungsfaecher`), mit dem Spannungsblock oder
  der Parabel, die gedrueckte Bewehrung eingeschlossen. Ihr Polygon dient zum
  Zeichnen und zum Eingrenzen. Den Widerstand bei einer Normalkraft (oder
  einem Moment) sucht sie auf dem Faecher selbst, zwischen den beiden Ebenen,
  die ihn einschliessen -- nicht auf der Sehne dazwischen. So haengt keine
  Zahl im Bericht an der Schrittweite der Zeichnung.

DIE SCHNITTSTELLE:
    innerhalb(N, M)              ob ein Punkt drin liegt
    kante(achse, fest, positiv)  der aeusserste Schnitt, mit Stuetzpunkten
    moment_bei(N, positiv)       der Momentenwiderstand bei einer Normalkraft
    eckwerte()                   N und M an den Spitzen, M bei N = 0
    protokoll_treffer(...)       wie ein Widerstand gefunden wurde

WIE EIN WIDERSTAND DER EBENENLINIE IN DIE HERLEITUNG KOMMT:
Nicht die Suche, sondern ihre Probe -- wie bei der Querschnittsanalyse: die
gefundene Ebene, die Kraft jedes Teils und die Summen. Das laesst sich mit
dem Taschenrechner nachpruefen, die Suche nicht.

VORZEICHEN:
    N > 0   Zug
    M > 0   Zug an der Unterseite
Bezugsachse fuer M ist die halbe Querschnittshoehe.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from opencivil.core.einheiten import Groesse
from opencivil.core.latex import Mathe
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.nachweis import dehnungsfaecher, linie as geo
from opencivil.nachweis.dehnungsfaecher import Linienpunkt
from opencivil.nachweis.querschnittsloeser import plattenfasern, protokoll_wirksamer_modul
from opencivil.nachweis.rechenwahl import (
    Rechenart, Rechenwahl, protokoll_betongesetz,
)
from opencivil.querschnitt.interaktion import illinois
from opencivil.querschnitt.werkstoffgesetz import Stahlgesetz

#: Ab welchem Abstand eine Dehnung nicht mehr auf ihrer Grenze liegt. Die
#: gefundene Ebene haelt ihren Drehpunkt bis auf Rundung (1e-18); was naeher
#: als dies an einer Grenze liegt, liegt auf ihr.
AUF_DER_GRENZE = 1e-12

#: Schritte des Goldenen Schnitts, der eine Spitze der Linie zwischen zwei
#: Ebenen sucht: das Fenster schrumpft auf 1e-8 einer Schrittweite, und dort
#: ist die Linie flach.
GOLDSCHRITTE = 40


@dataclass(frozen=True)
class Treffer:
    """Wo eine Gerade ``achse.gegen = fest`` die Linie aeusserst trifft."""

    wert: float
    """Der Wert auf der gesuchten Achse, in SI."""

    a: Any
    b: Any
    """Die Stuetzpunkte des Polygons, zwischen denen er liegt."""

    eps_oben: Optional[float] = None
    eps_unten: Optional[float] = None
    """Die Dehnungsebene dort -- nur bei der Ebenenlinie, die ihn genau sucht."""


class Widerstandslinie:
    """Was der M-N-Nachweis von einer Resistenzlinie braucht -- siehe Dateikopf."""

    wahl: Rechenwahl
    punkte: List[Any]

    @property
    def beschriftung(self) -> str:
        return self.wahl.beschriftung

    def innerhalb(self, N: float, M: float) -> bool:
        raise NotImplementedError

    def kante(self, achse: geo.Achse, fest: float, positiv: bool) -> Optional[Treffer]:
        raise NotImplementedError

    def moment_bei(self, N: float, positiv: bool) -> Optional[float]:
        """
        Der Momentenwiderstand bei dieser Normalkraft, als Betrag -- ``None``,
        wenn sie ausserhalb der Linie liegt.
        """
        treffer = self.kante(geo.MOMENT, N, positiv=positiv)
        return None if treffer is None else abs(treffer.wert)

    def eckwerte(self) -> Dict[str, float]:
        raise NotImplementedError

    def protokoll_treffer(self, p: Protokoll, treffer: Treffer, *, achse: geo.Achse,
                          fest: float, basis: str, titel: str = "") -> None:
        raise NotImplementedError


def _eckwerte(extrem: Callable[[geo.Achse, bool], float],
              bei_null: Sequence[float]) -> Dict[str, float]:
    """
    Die Eckwerte, in SI -- bei beiden Linien in derselben Gestalt.
    ``extrem(achse, positiv)`` ist der groesste (oder kleinste) Wert der
    Linie auf einer Achse.
    """
    return {
        "N_Rd_zug": extrem(geo.NORMALKRAFT, True),
        "N_Rd_druck": extrem(geo.NORMALKRAFT, False),
        "M_Rd_max": extrem(geo.MOMENT, True),
        "M_Rd_min": extrem(geo.MOMENT, False),
        "M_Rd_N0_pos": max([m for m in bei_null if m >= 0] or [0.0]),
        "M_Rd_N0_neg": min([m for m in bei_null if m <= 0] or [0.0]),
    }


# ===========================================================================
# Handrechnung
# ===========================================================================


class Handlinie(Widerstandslinie):
    """Das Polygon der Handrechnung -- geradlinig zwischen den Eckpunkten."""

    def __init__(self, wahl: Rechenwahl, punkte: Sequence[Any]) -> None:
        self.wahl = wahl
        self.punkte = list(punkte)

    def innerhalb(self, N: float, M: float) -> bool:
        return geo.innerhalb(N, M, self.punkte)

    def kante(self, achse: geo.Achse, fest: float, positiv: bool) -> Optional[Treffer]:
        grob = geo.kante(self.punkte, achse, fest, positiv=positiv)
        return None if grob is None else Treffer(*grob)

    def eckwerte(self) -> Dict[str, float]:
        def extrem(achse: geo.Achse, positiv: bool) -> float:
            werte = [achse.von(pt) for pt in self.punkte]
            return max(werte) if positiv else min(werte)
        return _eckwerte(extrem, geo.schnitte(self.punkte, geo.MOMENT, 0.0))

    def protokoll_treffer(self, p: Protokoll, treffer: Treffer, *, achse: geo.Achse,
                          fest: float, basis: str, titel: str = "") -> None:
        """
        Zwischen welchen beiden Eckpunkten geradlinig interpoliert wurde, und
        mit welchem Anteil.

        Ohne diesen Schritt stuende in der Mitschrift eine Zahl, die zwar aus
        nachvollziehbaren Eckpunkten stammt, aber selbst vom Himmel faellt.

        Faellt die festgehaltene Groesse genau auf einen Eckpunkt -- der haeufige
        Fall ``N_Ed = 0``, und ebenso ``M_Ed = 0`` bei reiner Normalkraft --, wird
        nicht interpoliert. Dort stuende sonst ein Bruch mit null im Zaehler, der
        nichts erklaert und nur so aussieht, als waere etwas gerechnet worden.
        """
        a, b = treffer.a, treffer.b
        ziel = achse                     # was gesucht wird
        lauf = ziel.gegen                # was dabei festgehalten bleibt
        e_lauf = lauf.einheit.latex
        e_ziel = ziel.einheit.latex

        # Der Eckpunkt selbst, falls die Einwirkung genau auf ihm liegt. Geprueft
        # wird auch der Zielwert: bei einer Kante laengs der festgehaltenen Achse
        # traefen beide Stuetzpunkte zu, und nur einer davon ist der Widerstand.
        genau = next(
            (q for q in (a, b)
             if _trifft(lauf.von(q), fest) and _trifft(ziel.von(q), treffer.wert)),
            None)

        werte = Zwischenwerte(basis)

        def wert(name: str, symbol: str, si: float, achse: geo.Achse):
            return werte.wert(name, symbol, Groesse.aus_si(si, achse.einheit))

        rd = wert("Rd", f"{ziel.name}_{{{self.wahl.index}}}", treffer.wert, ziel)
        if genau is not None:
            p.formel(rd, "@P", {"P": wert("P", genau.symbol, ziel.von(genau), ziel)},
                     titel=titel or (f"Widerstand bei {lauf.name}_Ed = "
                                     f"{_k(fest)} {lauf.einheit.beschriftung} – "
                                     f"ein Eckpunkt liegt genau dort"))
            return

        p.formel(
            rd, r"@x_1 + \frac{@y_Ed - @y_1}{@y_2 - @y_1} \cdot \left(@x_2 - @x_1\right)",
            {"x_1": wert("x_1", f"{ziel.name}_1", ziel.von(a), ziel),
             "x_2": wert("x_2", f"{ziel.name}_2", ziel.von(b), ziel),
             "y_1": wert("y_1", f"{lauf.name}_1", lauf.von(a), lauf),
             "y_2": wert("y_2", f"{lauf.name}_2", lauf.von(b), lauf),
             "y_Ed": wert("y_Ed", f"{lauf.name}_{{Ed}}", fest, lauf)},
            titel=titel or (f"Widerstand bei festgehaltenem {lauf.name}_Ed = "
                            f"{_k(fest)} {lauf.einheit.beschriftung}"),
        )
        p.tabelle(
            kopf=["Punkt", Mathe(rf"{lauf.name}\ [{e_lauf}]"),
                  Mathe(rf"{ziel.name}\ [{e_ziel}]")],
            zeilen=[
                [Mathe(q.symbol), Mathe(_k(lauf.von(q))), Mathe(_k(ziel.von(q)))]
                for q in (a, b)
            ],
            titel="Stützpunkte der Interpolation",
            ausrichtung="lrr",
        )


# ===========================================================================
# Dehnungsebenen
# ===========================================================================


class Ebenenlinie(Widerstandslinie):
    """
    Der Rand des Dehnungsfaechers -- genau nachgeschaerft, siehe Dateikopf.

    ``beton`` ist das Gesetz der Wahl
    (:func:`~opencivil.nachweis.rechenwahl.betongesetz`). Der Stahl kommt je
    Lage als :class:`Stahlgesetz` -- ohne Abfall jenseits von ``eps_ud``: die
    unterste Lage liegt im Faecher genau auf dieser Grenze, und ein Gesetz,
    das dort auf null faellt, kippte an der Rundung.
    """

    def __init__(self, wahl: Rechenwahl, *, h: float, b: float,
                 beton: Callable[[float], float],
                 lagen: Sequence[Tuple[float, float, Stahlgesetz, str]],
                 eps_c1d: float, eps_c2d: float,
                 schritte: int = dehnungsfaecher.SCHRITTE,
                 fasern: int = dehnungsfaecher.FASERN) -> None:
        if wahl.art not in (Rechenart.BLOCK, Rechenart.PARABEL):
            raise ValueError(f"Eine Linie aus Dehnungsebenen gibt es mit Block oder "
                             f"Parabel, nicht mit «{wahl.art.beschriftung}».")
        self.wahl = wahl
        self.h = h
        self.lagen = list(lagen)
        self.fasern = fasern
        self.schritte = schritte
        self.querschnitt = plattenfasern(
            h=h, b=b, beton=beton,
            staebe=[(a_s, z, gesetz.spannung) for a_s, z, gesetz, _ in self.lagen],
            fasern=fasern, gemittelt=wahl.art.mit_block, verdraengt=True)
        self.grenzen, self.grenznamen = dehnungsfaecher.grenzen(
            h, [(z, gesetz.eps_ud, f"Stahl der {text}") for _, z, gesetz, text in self.lagen],
            eps_c1d=eps_c1d, eps_c2d=eps_c2d)
        self.punkte: List[Linienpunkt] = geo.ohne_wiederholungen([
            Linienpunkt(*self.kraefte(ebene.eps_oben, ebene.eps_unten),
                        eps_oben=ebene.eps_oben, eps_unten=ebene.eps_unten,
                        abschnitt=marke)
            for marke, ebene in dehnungsfaecher.faecher(
                h, [(z, gesetz.eps_ud) for _, z, gesetz, _ in self.lagen], schritte,
                eps_c1d=eps_c1d, eps_c2d=eps_c2d)])
        #: Je Achse die groesste Zahl darauf -- der Massstab, an dem die Suche
        #: «genau genug» misst.
        self._massstab = {achse.name: max(abs(achse.von(q)) for q in self.punkte) or 1.0
                          for achse in (geo.MOMENT, geo.NORMALKRAFT)}
        self._kanten: Dict[Tuple[str, float, bool], Optional[Treffer]] = {}

    def kraefte(self, eps_oben: float, eps_unten: float) -> Tuple[float, float]:
        """N und M der Ebene durch ``eps_oben`` und ``eps_unten`` -- um die halbe Hoehe."""
        k = self.querschnitt.kraefte(0.5 * (eps_oben + eps_unten),
                                     (eps_unten - eps_oben) / self.h)
        return k.N, k.M

    def kante(self, achse: geo.Achse, fest: float, positiv: bool) -> Optional[Treffer]:
        """
        Der aeusserste Schnitt, auf dem Faecher gesucht: zwischen den beiden
        Ebenen, deren Punkte ihn einschliessen. Zwei benachbarte Punkte liegen
        im selben Abschnitt des Faechers, und dort ist jede Ebene dazwischen
        selbst eine des Faechers -- die Suche bleibt auf dem Rand.

        Einmal je Frage gerechnet: das Urteil, der Grad und der Widerstand
        bei N_Ed fragen dieselbe Kante.
        """
        schluessel = (achse.name, fest, positiv)
        if schluessel not in self._kanten:
            self._kanten[schluessel] = self._kante(achse, fest, positiv)
        return self._kanten[schluessel]

    def _kante(self, achse: geo.Achse, fest: float, positiv: bool) -> Optional[Treffer]:
        grob = geo.kante(self.punkte, achse, fest, positiv=positiv)
        if grob is None:
            return None
        _, a, b = grob
        lauf = achse.gegen

        def abweichung(anteil: float):
            eps_oben = a.eps_oben + (b.eps_oben - a.eps_oben) * anteil
            eps_unten = a.eps_unten + (b.eps_unten - a.eps_unten) * anteil
            N, M = self.kraefte(eps_oben, eps_unten)
            stelle = geo.Stelle(N=N, M=M)
            return lauf.von(stelle) - fest, (stelle, eps_oben, eps_unten)

        stelle, eps_oben, eps_unten = illinois(
            abweichung, 0.0, lauf.von(a) - fest, 1.0, lauf.von(b) - fest,
            schranke_x=1e-14, schranke_f=1e-11 * self._massstab[lauf.name])
        return Treffer(wert=achse.von(stelle), a=a, b=b,
                       eps_oben=eps_oben, eps_unten=eps_unten)

    def innerhalb(self, N: float, M: float) -> bool:
        """
        Genau statt am Polygon: bei dieser Normalkraft zwischen dem linken und
        dem rechten Rand. So kann das Urteil nie dem Erfuellungsgrad
        widersprechen, der an denselben Raendern gemessen wird.
        """
        rechts = self.kante(geo.MOMENT, N, positiv=True)
        links = self.kante(geo.MOMENT, N, positiv=False)
        if rechts is None or links is None:
            return False
        return links.wert <= M <= rechts.wert

    def eckwerte(self) -> Dict[str, float]:
        """
        Auch die Spitzen liegen meist zwischen zwei Ebenen -- das groesste
        Moment, und ebenso die groesste Druckkraft: kippt die Ebene ein wenig
        um den Punkt C, fliesst die gedrueckte Bewehrung und traegt mehr als
        beim gleichmaessigen -eps_c1d. Sie werden dort gesucht, wie der
        Widerstand bei N = 0.
        """
        bei_null = [t.wert for t in (self.kante(geo.MOMENT, 0.0, True),
                                     self.kante(geo.MOMENT, 0.0, False)) if t is not None]
        return _eckwerte(self._extrem, bei_null)

    def _extrem(self, achse: geo.Achse, positiv: bool) -> float:
        """
        Der groesste (oder kleinste) Wert auf einer Achse: um den Punkt der
        Linie, der ihn traegt, ueber die Ebenen bis zu seinen beiden
        Nachbarn -- mit dem Goldenen Schnitt.
        """
        vz = 1.0 if positiv else -1.0
        anzahl = len(self.punkte)
        i = max(range(anzahl), key=lambda k: vz * achse.von(self.punkte[k]))
        mitte = self.punkte[i]
        vor, nach = self.punkte[i - 1], self.punkte[(i + 1) % anzahl]
        stelle = 0 if achse is geo.NORMALKRAFT else 1

        def wert(t: float) -> float:
            ziel, s = (vor, -t) if t < 0.0 else (nach, t)
            return vz * self.kraefte(
                mitte.eps_oben + (ziel.eps_oben - mitte.eps_oben) * s,
                mitte.eps_unten + (ziel.eps_unten - mitte.eps_unten) * s)[stelle]

        teil = (math.sqrt(5.0) - 1.0) / 2.0
        unten, oben = -1.0, 1.0
        c, d = oben - teil * (oben - unten), unten + teil * (oben - unten)
        fc, fd = wert(c), wert(d)
        for _ in range(GOLDSCHRITTE):
            if fc > fd:
                oben, d, fd = d, c, fc
                c = oben - teil * (oben - unten)
                fc = wert(c)
            else:
                unten, c, fc = c, d, fd
                d = unten + teil * (oben - unten)
                fd = wert(d)
        return vz * max(fc, fd, vz * achse.von(mitte))

    # -- Herleitung -----------------------------------------------------------

    def erreicht(self, eps_oben: float, eps_unten: float) -> List[str]:
        """Welche Grenzen diese Ebene erreicht -- die, die ihren Bruchzustand bestimmen."""
        eps_m = 0.5 * (eps_oben + eps_unten)
        chi = (eps_unten - eps_oben) / self.h
        namen: List[str] = []
        for grenze, name in zip(self.grenzen, self.grenznamen):
            eps = eps_m + chi * grenze.arm
            if ((abs(eps - grenze.eps_min) <= AUF_DER_GRENZE
                 or abs(eps - grenze.eps_max) <= AUF_DER_GRENZE) and name not in namen):
                namen.append(name)
        return namen

    def protokoll_ansatz(self, p: Protokoll, *, f_c: Wert, E_cm: Wert, phi: Wert,
                         basis: str) -> None:
        """
        Wie die Linie entsteht -- einmal je Nachweis, vor den Kombinationen.
        Den Titel setzt der Nachweis.
        """
        wahl, satz = self.wahl, self.wahl.satz
        p.erklaerung(
            "Der Querschnitt bleibt eben (Bernoulli). Zu jeder Dehnungsebene ergeben "
            "sich Normalkraft und Moment aus den Spannungen über die Höhe; Zug ist "
            "positiv, das Moment bezieht sich auf die halbe Querschnittshöhe. Die "
            "Resistenzlinie ist der Rand aller zulässigen Ebenen: an ihm erreicht der "
            "Stahl ε_ud, der Beton am gedrückten Rand −ε_c2d oder, wenn der ganze "
            "Querschnitt gedrückt ist, im Punkt C −ε_c1d."
        )
        if wahl.art is Rechenart.PARABEL:
            protokoll_wirksamer_modul(p, E_cm, phi, basis,
                                      titel="Wirksamer Modul der Parabel")
        protokoll_betongesetz(p, wahl, f_c, E_cm, basis, titel="Werkstoffgesetze")
        p.ansatz(Stahlgesetz(0.0, 0.0, 0.0, 0.0).latex(satz.stahl_zeichen,
                                                       f"{satz.stahl_zeichen}^{{-}}"),
                 titel="Werkstoffgesetze: Stahl, bilinear", referenz="SIA 262:2025, 4.2.2.4")
        p.ansatz(
            r"N = \int_A \sigma\,\mathrm{d}A \qquad "
            r"M = \int_A \sigma \cdot \left(z - \tfrac{h}{2}\right)\,\mathrm{d}A",
            titel="Schnittgrössen aus der Spannungsverteilung",
        )
        mittel = ", jede mit ihrer mittleren Spannung" if wahl.art.mit_block else ""
        p.erklaerung(
            f"Der Beton ist in {self.fasern} Fasern über die Höhe geteilt{mittel}, die "
            f"Bewehrung zählt Lage für Lage, und an ihrer Stelle zählt der Stahl statt "
            f"des Betons – auch die gedrückte Bewehrung wirkt mit. Den Widerstand bei "
            f"einer Einwirkung sucht die Rechnung auf dem Rand selbst, zwischen zwei "
            f"benachbarten Ebenen; was dort gilt, zeigt bei jeder Kombination die Probe."
        )
        p.tabelle(
            kopf=["Lage", Mathe(r"a_s\ [\mathrm{mm}^2]"), Mathe(r"z\ [\mathrm{mm}]"),
                  Mathe(rf"{satz.stahl_zeichen}\ [\mathrm{{N/mm^2}}]")],
            zeilen=[[text, Mathe(f"{a_s * 1e6:.0f}"), Mathe(f"{z * 1e3:.1f}"),
                     Mathe(f"{gesetz.f_yd / 1e6:.0f}")]
                    for a_s, z, gesetz, text in self.lagen],
            titel="Berücksichtigte Bewehrungslagen",
            ausrichtung="lrrr",
        )

    def protokoll_treffer(self, p: Protokoll, treffer: Treffer, *, achse: geo.Achse,
                          fest: float, basis: str, titel: str = "") -> None:
        """
        Die Probe des Bruchzustands, an dem der Widerstand liegt: die Ebene,
        die Kraft jedes Teils, die Summen -- und welche Grenze ihn bestimmt.

        Der Stahl mit seiner vollen Spannung, ``F = sigma_s · A_s``; der Beton
        als Resultierende ohne die Flaeche, die der Stahl einnimmt. So ist
        jede Zeile fuer sich nachzurechnen, und die Summe ist die der Fasern.
        """
        lauf = achse.gegen
        werte = Zwischenwerte(basis)
        eps_oben = werte.dehnung("eps_oben", r"\varepsilon_{oben}", treffer.eps_oben, stellen=3)
        eps_unten = werte.dehnung("eps_unten", r"\varepsilon_{unten}", treffer.eps_unten,
                                  stellen=3)
        p.gleichung(rf"{eps_oben.symbol} = {eps_oben.zahl_latex()} \qquad "
                    rf"{eps_unten.symbol} = {eps_unten.zahl_latex()}",
                    titel=titel or (f"Bruchzustand bei {lauf.name}_Ed = {_k(fest)} "
                                    f"{lauf.einheit.beschriftung} – die Dehnungsebene"))

        eps_m = 0.5 * (treffer.eps_oben + treffer.eps_unten)
        chi = (treffer.eps_unten - treffer.eps_oben) / self.h
        N, M = self.kraefte(treffer.eps_oben, treffer.eps_unten)
        stahl = []
        for a_s, z, gesetz, text in self.lagen:
            eps = eps_m + chi * (z - self.h / 2.0)
            sigma = gesetz.spannung(eps)
            stahl.append((text, eps, sigma, a_s, sigma * a_s, z))
        F_c = N - sum(s[4] for s in stahl)
        M_c = M - sum(s[4] * (s[5] - self.h / 2.0) for s in stahl)
        z_c = self.h / 2.0 + M_c / F_c if F_c else float("nan")
        p.tabelle(
            kopf=["Teil", Mathe(r"\varepsilon\ [‰]"), Mathe(r"\sigma\ [\mathrm{N/mm^2}]"),
                  Mathe(r"A\ [\mathrm{mm}^2]"), Mathe(r"F\ [\mathrm{kN}]"),
                  Mathe(r"z\ [\mathrm{mm}]")],
            zeilen=[["Beton, Resultierende", Mathe("–"), Mathe("–"), Mathe("–"),
                     Mathe(f"{F_c / 1e3:.1f}"),
                     Mathe("–" if z_c != z_c else f"{z_c * 1e3:.1f}")]]
            + [[text, Mathe(f"{eps * 1e3:.3f}"), Mathe(f"{sigma / 1e6:.1f}"),
                Mathe(f"{a_s * 1e6:.0f}"), Mathe(f"{F / 1e3:.1f}"), Mathe(f"{z * 1e3:.1f}")]
               for text, eps, sigma, a_s, F, z in stahl],
            titel="Kräfte in diesem Bruchzustand – Zug positiv, z ab Oberkante",
            ausrichtung="lrrrrr",
        )

        summen = {
            geo.NORMALKRAFT: (r"\sum F_i", N),
            geo.MOMENT: (r"\sum F_i \cdot \left(z_i - \tfrac{h}{2}\right)", M),
        }
        probe = werte.wert("probe", f"{lauf.name}_{{Ed}}",
                           Groesse.aus_si(summen[lauf][1], lauf.einheit))
        p.gleichung(rf"{summen[lauf][0]} = {probe.zahl_latex()} = {probe.symbol}",
                    titel="Probe: die Ebene trägt genau die Einwirkung")
        rd = werte.wert("Rd", f"{achse.name}_{{{self.wahl.index}}}",
                        Groesse.aus_si(summen[achse][1], achse.einheit))
        p.gleichung(rf"{rd.symbol} = {summen[achse][0]} = {rd.zahl_latex()}",
                    titel=f"{achse.widerstand} aus den Teilkräften")
        erreicht = self.erreicht(treffer.eps_oben, treffer.eps_unten)
        if erreicht:
            p.text(f"Massgebend: {' und '.join(erreicht)} auf der Grenzdehnung.")


def _trifft(a: float, b: float) -> bool:
    """
    Ob zwei SI-Werte fuer die Mitschrift als derselbe gelten.

    Die Schranke haengt an der Groesse der Werte, nicht an einer festen Zahl:
    Momente liegen im Bereich 1e5 Nm, und dort ist ein absoluter Abstand von
    1e-9 unerreichbar streng.
    """
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


def _k(si_wert: float) -> str:
    """Ein SI-Wert in Kilo-Einheiten, eine Nachkommastelle."""
    return f"{si_wert / 1e3:.1f}"
