"""
opencivil/verbund/stuetze.py -- eine Verbundstuetze nach SIA 264:2014, 5.3.

VERANTWORTUNG:
Was der Nachweis einer Verbundstuetze braucht, ohne Herleitung, in N, mm und
N/mm²; die Herleitung schreibt :mod:`opencivil.nachweis.qa_verbund_stuetze`.
Der Stab hat den gezeichneten Querschnitt; ein Fall gibt ihm die Druckkraft
und ihren staendigen Anteil, die groessten Momente 1. Ordnung, die
Verhaeltnisse ψ der Endmomente, die Knicklaengen und die Laenge der Stuetze
(:class:`~opencivil.stahlbau.stabilitaet.Stabfall`).

DER QUERSCHNITT -- einmal je Analyse (:class:`Stuetze`):
* Die Art nach Tabelle 7 (:func:`querschnittsart`): ein einziges I-Profil
  oder Rohr aus der Profiltabelle, ganz einbetoniert, kammerbetoniert oder
  mit Beton gefuellt (5.3.1.1). Andere -- ein Rohr mit einem Profil darin,
  zwei Profile, ein Traeger unter einer Platte -- kennt Tabelle 7 nicht.
* Doppelsymmetrisch und konstant (5.3.2.1), ``0.2 ≤ h/b ≤ 5`` (5.3.2.3)
  und die Grenzen der Tabelle 6 gegen das lokale Beulen (5.3.1.7) -- das
  ganz einbetonierte Profil braucht keine.
* Je Gruppe Flaeche und Traegheitsmomente um die Mitte des Profils
  (:class:`Werkstoff`); der Betonstahl zaehlt hoechstens mit 6 % der
  Betonflaeche (5.3.2.2).
* ``N_pl,Rd`` (14) -- im gefuellten Rohr mit 1.0 statt 0.85 (5.3.2.5) --,
  ``N_pl,Rk`` mit γ = 1 (16) und ``δ`` (13) zwischen 0.2 und 0.9 (5.3.1.2).

JE FALL (:func:`rechnen`):
* ``E_c,eff`` (19) mit dem staendigen Anteil der Normalkraft und der
  Kriechzahl der Analyse.
* Die Achse ohne Moment knickt (:class:`Knicken`): ``(EI)_eff,λ`` (17),
  ``N_cr`` (20), ``λ̄`` (16) hoechstens 2.0, ``χ_K`` nach SIA 263 (8) mit
  der Kurve der Tabelle 7, ``N_Ed ≤ χ_K N_pl,Rd`` (15) -- 5.3.4.2.
* Die Achse mit Moment (:class:`Biegeachse`): ``(EI)_eff,d`` (22),
  ``N_cr,eff`` (23) mit der Laenge der Stuetze, ``k`` (24) mit ``ω`` nach
  SIA 263, die Ersatzimperfektion ``e_0`` der Tabelle 7:
  ``M_Ed,II = k |M_Ed| + k_0 |N_Ed| e_0``; ``μ_d = M_pl,N,Rd/M_pl,Rd`` aus
  rechteckigen Spannungsbloecken (Figur 7, 5.3.4.4) und (25) mit 0.9, fuer
  S420 und S460 0.8. Zweiachsig linear (5.3.5).

NACH VORGABE, NICHT NACHGESCHLAGEN:
* Doppelsymmetrisch heisst: je Gruppe liegt der Schwerpunkt keinen
  Millimeter neben der Mitte des Profils, und ``|I_yz|`` um sie erreicht
  kein Hundertstel von ``√(I_y I_z)``.
* Ganz einbetoniert heisst: acht Punkte einen Millimeter ausserhalb des
  umschreibenden Rechtecks des Profils -- Ecken und Mitten der Seiten --
  liegen im Beton. Kammerbetoniert: Beton deckt den Steg beidseits und
  jeden Flansch innen
  (:meth:`~opencivil.verbund.querschnitt.Verbundquerschnitt.kammerbetoniert`),
  ausserhalb des Profils liegt nichts. Gefuellt: in der Mitte des Rohrs
  liegt Beton, ausserhalb nichts.
* Der Betonstahl ueber 6 % der Betonflaeche zaehlt in jedem Stab
  gleichmaessig weniger -- auch in ``M_pl`` und ``EI``.
* Die Imperfektion waechst mit ``k_0 = 1/(1 - N_Ed/N_cr,eff)``, also mit
  ``ω = 1`` wie unter einer Querlast; zweiachsig wirkt sie in beiden Achsen
  zugleich.
* Zweiachsig: ``Σ M_Ed,II/(μ_d M_pl,Rd) ≤ 0.9`` (0.8) -- 5.3.5 nennt die
  lineare Interaktion, aber keine Grenze; die von (25) liegt auf der
  sicheren Seite.
* ``μ_d`` hoechstens eins: ob das Moment aus der Normalkraft selbst
  entsteht, weiss das Werkzeug nicht (5.3.4.6).
* Ein Rohr mit mehr als 6 % Betonstahl rechnet mit Kurve b, wie bis 6 %:
  Tabelle 7 endet dort, und mehr zaehlt nach 5.3.2.2 nicht.
* Die Theorie 2. Ordnung rechnet es immer, auch wo (21) sie erliesse.
* Eine Knicklaenge null heisst gehalten: um diese Achse knickt die Stuetze
  nicht, und ein Moment um sie waechst nicht.

VORZEICHEN:
N < 0 Druck; M_y > 0 zieht unten, M_z > 0 links -- um die Mitte des
Profils, die bei einer doppelsymmetrischen Stuetze der Schwerpunkt ist.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.material.basis import Baustoffart
from opencivil.querschnitt import geometrie as geo
from opencivil.querschnitt.geometrie import Punkt
from opencivil.querschnitt.plastisch import Starrplastisch
from opencivil.stahlbau import stabilitaet as st
from opencivil.stahlbau.querschnitt import Teil, normale
from opencivil.stahlprofile import tabelle
from opencivil.stahlprofile.formen import I_PROFIL, RECHTECKROHR_GERUNDET, RUNDROHR
from opencivil.verbund.querschnitt import NEBEN, Verbundquerschnitt

REFERENZ_ART = "SIA 264:2014, 5.3.1.1; 5.3.2.1; Tabelle 7"
REFERENZ_HB = "SIA 264:2014, 5.3.2.3"
REFERENZ_BEULEN = "SIA 264:2014, 5.3.1.7, Tabelle 6"
REFERENZ_BEWEHRUNG = "SIA 264:2014, 5.3.2.2"
#: (14) im gefuellten Rohr -- ohne Rohr gilt ``qa_verbund_kennzahlen.REFERENZ_14``.
REFERENZ_N_PL_ROHR = "SIA 264:2014, 5.3.2.4, (14); 5.3.2.5"
REFERENZ_N_PL_K = "SIA 264:2014, 5.3.2.7, (16)"
REFERENZ_DELTA = "SIA 264:2014, 5.3.1.2, (13)"
REFERENZ_KURVE = "SIA 264:2014, 5.3.2.6, Tabelle 7"
REFERENZ_15 = "SIA 264:2014, 5.3.2.6, (15); SIA 263:2013, 4.5.1.4, (8)"
REFERENZ_LAMBDA = "SIA 264:2014, 5.3.2.7, (16); 5.3.2.1"
REFERENZ_EI = "SIA 264:2014, 5.3.2.8, (17)"
REFERENZ_E_C = "SIA 264:2014, 5.3.2.9, (19)"
REFERENZ_N_CR = "SIA 264:2014, 5.3.2.10, (20)"
REFERENZ_EI_D = "SIA 264:2014, 5.3.3.2, (22)"
REFERENZ_N_CR_EFF = "SIA 264:2014, 5.3.3.3, (23); 5.3.4.1"
REFERENZ_K = "SIA 264:2014, 5.3.4.1, (24); SIA 263:2013, 5.1.9.1"
REFERENZ_E_0 = "SIA 264:2014, 5.3.1.4; Tabelle 7"
REFERENZ_MU = "SIA 264:2014, 5.3.4.3; 5.3.4.4; 5.3.4.6; Figur 7"
REFERENZ_25 = "SIA 264:2014, 5.3.4.6, (25)"
REFERENZ_ZWEIACHSIG = "SIA 264:2014, 5.3.5"

#: (13): wo δ liegen muss.
DELTA_AB, DELTA_BIS = 0.2, 0.9

#: 5.3.2.1 und (16): die groesste bezogene Schlankheit.
LAMBDA_BIS = 2.0

#: 5.3.2.2: der Betonstahl zaehlt hoechstens mit diesem Anteil der Betonflaeche.
BEWEHRUNG_BIS = 0.06

#: 5.3.2.3: wo ``h/b`` liegen muss.
HB_AB, HB_BIS = 0.2, 5.0

#: 5.3.2.5 und 5.3.4.4: der Umrechnungsfaktor der Betondruckfestigkeit im gefuellten Rohr.
ROHR_FAKTOR = 1.0

#: (17): wie der Beton in ``(EI)_eff,λ`` zaehlt; (22): wie in ``(EI)_eff,d``, und der Beiwert davor.
BETON_LAMBDA = 0.6
BETON_D, BEIWERT_D = 0.5, 0.9

#: (25): die Grenze -- fuer S420 und S460 die kleinere.
ALPHA_M, ALPHA_M_HOCHFEST = 0.9, 0.8

#: Tabelle 7: bis zu welchem ``ρ_s`` ein gefuelltes Rohr mit Kurve a rechnet.
ROHR_RHO = 0.03

#: Tabelle 6: die Grenzen gegen das lokale Beulen, durch ``ε²`` beim runden Rohr, sonst ``ε``.
BEULEN_RUND, BEULEN_RECHTECK, BEULEN_FLANSCH = 90.0, 52.0, 44.0

#: Wie weit ein Schwerpunkt neben der Mitte liegen und welchen Teil von ``√(I_y I_z)`` ``|I_yz|``
#: erreichen darf, damit eine Gruppe als doppelsymmetrisch gilt -- siehe Dateikopf.
SYMMETRIE_VERSATZ = 1.0
SYMMETRIE_I_YZ = 0.01

#: Ab wie viel mm² Beton oder Betonstahl ausserhalb des Profils liegen.
AUSSEN_AB = 1.0

#: Warum ein Querschnitt nicht als Verbundstuetze rechnet.
NICHT_IN_TABELLE = (
    "Tabelle 7 kennt diesen Querschnitt nicht. Als Verbundstütze rechnet das Werkzeug ein "
    "einziges I-Profil oder Rohr aus der Profiltabelle: ganz einbetoniert, nur zwischen den "
    "Flanschen betoniert oder als Rohr mit Beton gefüllt, ohne Beton daneben.")

#: Warum ein Rohr nicht als gefuellt rechnet: in seiner Mitte liegt kein Beton.
LEERES_ROHR = ("Das Rohr «{name}» ist innen leer. Als Verbundstütze rechnet ein gefülltes Rohr: "
               "Beton ganz in seinem Loch und keiner daneben.")


class Art(Enum):
    """Wie Profil und Beton nach Tabelle 7 zusammen liegen -- siehe Dateikopf."""

    EINBETONIERT = "ganz einbetoniert"
    KAMMERBETONIERT = "kammerbetoniert"
    ROHR = "mit Beton gefüllt"


def _art_bei(verbund: Verbundquerschnitt, p: Punkt) -> Optional[Baustoffart]:
    """Die Art des Materials an ``p`` -- ``None`` in einer Aussparung oder daneben."""
    i = geo.innerstes(p, [f.punkte for f in verbund.flaechen])
    stoff = verbund.flaechen[i].stoff if i is not None else None
    return stoff.art if stoff is not None else None


def _rundum(teil: Teil) -> List[Punkt]:
    """Acht Punkte ``NEBEN`` ausserhalb des umschreibenden Rechtecks -- Ecken und Seitenmitten."""
    ys = [p[0] for p in teil.flaeche.punkte]
    zs = [p[1] for p in teil.flaeche.punkte]
    y0, y1, z0, z1 = min(ys) - NEBEN, max(ys) + NEBEN, min(zs) - NEBEN, max(zs) + NEBEN
    ym, zm = (y0 + y1) / 2.0, (z0 + z1) / 2.0
    return [(y, z) for y in (y0, ym, y1) for z in (z0, zm, z1) if (y, z) != (ym, zm)]


def querschnittsart(verbund: Verbundquerschnitt) -> Tuple[Optional[Art], str]:
    """
    Die Art nach Tabelle 7 (siehe Dateikopf) -- oder ``None`` und warum
    Tabelle 7 den Querschnitt nicht kennt.
    """
    teile = verbund.stahl.teile
    lage = teile[0].flaeche.profil if len(teile) == 1 else None
    if lage is None:
        return None, NICHT_IN_TABELLE
    teil, form = teile[0], tabelle.profil(lage.name).form
    aussen = sum(s.gewicht * s.werte.A for s in verbund.fuge[0]) > AUSSEN_AB
    if form in (RUNDROHR, RECHTECKROHR_GERUNDET):
        if _art_bei(verbund, lage.mitte) is not Baustoffart.BETON:
            return None, LEERES_ROHR.format(name=lage.name)
        return (None, NICHT_IN_TABELLE) if aussen else (Art.ROHR, "")
    if form is I_PROFIL:
        if all(_art_bei(verbund, p) is Baustoffart.BETON for p in _rundum(teil)):
            return Art.EINBETONIERT, ""
        if not aussen and all(verbund.kammerbetoniert(teil, b) for b in teil.bleche):
            return Art.KAMMERBETONIERT, ""
    return None, NICHT_IN_TABELLE


@dataclass(frozen=True)
class Werkstoff:
    """
    Eine Gruppe als Teil der Stuetze, um die Mitte des Profils: Flaeche in
    mm², wie weit ihr Schwerpunkt neben der Mitte liegt, in mm, und ihre
    Traegheitsmomente in mm⁴.
    """

    gruppe: int
    name: str
    art: Baustoffart
    A: float
    versatz: float
    I_y: float
    I_z: float
    I_yz: float

    def I(self, achse: str) -> float:
        return self.I_y if achse == "y" else self.I_z


def _werkstoffe(verbund: Verbundquerschnitt, mitte: Punkt) -> Tuple[Werkstoff, ...]:
    """Je Gruppe ihre Werte um ``mitte`` -- Beton ohne, was Stahl und Staebe verdraengen."""
    summen = [[0.0] * 6 for _ in verbund.gruppen]
    for s in verbund.stuecke():
        w, k = s.werte, s.gewicht
        dy, dz = w.y_S - mitte[0], w.z_S - mitte[1]
        x = summen[s.gruppe]
        x[0] += k * w.A
        x[1] += k * w.A * dy
        x[2] += k * w.A * dz
        x[3] += k * (w.I_y + w.A * dz * dz)
        x[4] += k * (w.I_z + w.A * dy * dy)
        x[5] += k * (w.I_yz + w.A * dy * dz)
    return tuple(
        Werkstoff(g, verbund.gruppen[g].name, verbund.art(g), A,
                  math.hypot(S_y / A, S_z / A) if A > 0.0 else 0.0, I_y, I_z, I_yz)
        for g, (A, S_y, S_z, I_y, I_z, I_yz) in enumerate(summen))


@dataclass(frozen=True)
class Festigkeiten:
    """
    Je Gruppe in N/mm²: gezogen und gedrueckt mit der Wahl der
    Tragsicherheit, gedrueckt charakteristisch -- der Beton beide Male mit
    seinem Umrechnungsfaktor -- und der Elastizitaetsmodul: ``E_a``,
    ``E_cm`` oder ``E_s``.
    """

    zug: Tuple[float, ...]
    druck: Tuple[float, ...]
    druck_k: Tuple[float, ...]
    E: Tuple[float, ...]


class Stuetze:
    """
    Der Querschnitt als Verbundstuetze -- siehe Dateikopf. ``eps`` ist ``ε``
    des Profils, ``hochfest``, ob es S420 oder S460 ist.
    """

    def __init__(self, verbund: Verbundquerschnitt, art: Art, f: Festigkeiten, eps: float,
                 hochfest: bool) -> None:
        self.verbund, self.art, self.f, self.eps = verbund, art, f, eps
        self.teil = verbund.stahl.teile[0]
        self.lage = self.teil.flaeche.profil
        self.profil = tabelle.profil(self.lage.name)
        self.mitte: Punkt = self.lage.mitte
        self.werkstoffe = _werkstoffe(verbund, self.mitte)
        self.alpha_M = ALPHA_M_HOCHFEST if hochfest else ALPHA_M

    # -- Flaechen und Anteile ---------------------------------------------------------

    def der_art(self, art: Baustoffart) -> List[Werkstoff]:
        return [w for w in self.werkstoffe if w.art is art]

    def flaeche(self, art: Baustoffart) -> float:
        return sum(w.A for w in self.der_art(art))

    @cached_property
    def rho_s(self) -> float:
        """``A_s/A_c``, wie gezeichnet."""
        A_c = self.flaeche(Baustoffart.BETON)
        return self.flaeche(Baustoffart.BETONSTAHL) / A_c if A_c > 0.0 else 0.0

    @cached_property
    def anteil_s(self) -> float:
        """Mit welchem Anteil der Betonstahl zaehlt: hoechstens 6 % der Betonflaeche (5.3.2.2)."""
        return min(1.0, BEWEHRUNG_BIS / self.rho_s) if self.rho_s > 0.0 else 1.0

    def zaehlt(self, w: Werkstoff) -> float:
        return self.anteil_s if w.art is Baustoffart.BETONSTAHL else 1.0

    # -- Was 5.3.1 und 5.3.2 verlangen -------------------------------------------------

    @cached_property
    def unsymmetrisch(self) -> str:
        """Warum die Stuetze nicht doppelsymmetrisch ist -- leer, wo sie es ist (Dateikopf)."""
        for w in self.werkstoffe:
            if w.versatz > SYMMETRIE_VERSATZ:
                return (f"Doppelsymmetrisch muss die Stütze sein (5.3.2.1): der Schwerpunkt von "
                        f"«{w.name}» liegt {w.versatz:.1f} mm neben der Mitte des Profils.")
            if abs(w.I_yz) > SYMMETRIE_I_YZ * math.sqrt(w.I_y * w.I_z):
                return (f"Doppelsymmetrisch muss die Stütze sein (5.3.2.1): «{w.name}» liegt "
                        f"nicht symmetrisch zu y und z, I_yz ist nicht null.")
        return ""

    @cached_property
    def masse(self) -> Tuple[float, float]:
        """Hoehe ``h`` in z und Breite ``b`` in y, ueber alles, in mm."""
        punkte = [p for f in self.verbund.flaechen if f.stoff is not None for p in f.punkte]
        ys, zs = [p[0] for p in punkte], [p[1] for p in punkte]
        return max(zs) - min(zs), max(ys) - min(ys)

    @property
    def hb(self) -> float:
        h, b = self.masse
        return h / b

    @cached_property
    def beulen(self) -> Optional[Tuple[str, float, float, str]]:
        """
        Tabelle 6: das Verhaeltnis, seine Zahl, seine Grenze und wie sie
        steht -- ``None`` beim ganz einbetonierten Profil.
        """
        m, e = self.profil.masse, self.eps
        if self.art is Art.EINBETONIERT:
            return None
        if self.profil.form is RUNDROHR:
            return "d/t", m["D"] / m["t"], BEULEN_RUND * e * e, f"{BEULEN_RUND:g} ε²"
        if self.profil.form is RECHTECKROHR_GERUNDET:
            h = max(m["h"], m["b"])
            return "h/t", h / m["t"], BEULEN_RECHTECK * e, f"{BEULEN_RECHTECK:g} ε"
        return "b/t_f", m["b"] / m["t_f"], BEULEN_FLANSCH * e, f"{BEULEN_FLANSCH:g} ε"

    @cached_property
    def N_a(self) -> float:
        """``A_a f_y/γ_a`` in N."""
        return sum(w.A * self.f.druck[w.gruppe] for w in self.der_art(Baustoffart.BAUSTAHL))

    def N_pl(self, charakteristisch: bool = False) -> float:
        """``N_pl,Rd`` (14) in N -- oder ``N_pl,Rk`` mit γ = 1 (16)."""
        f = self.f.druck_k if charakteristisch else self.f.druck
        return sum(self.zaehlt(w) * w.A * f[w.gruppe] for w in self.werkstoffe)

    @property
    def delta(self) -> float:
        """(13)."""
        return self.N_a / self.N_pl()

    @cached_property
    def fehlt(self) -> str:
        """
        Warum die Stuetze nicht nach 5.3 rechnet, der erste Grund -- leer,
        wo sie es tut: die Symmetrie, ``h/b``, Tabelle 6, ``δ``.
        """
        if self.unsymmetrisch:
            return self.unsymmetrisch
        h, b = self.masse
        if not HB_AB <= self.hb <= HB_BIS:
            return (f"h/b = {h:.0f}/{b:.0f} = {self.hb:.2f} liegt nicht zwischen {HB_AB:g} und "
                    f"{HB_BIS:g} (5.3.2.3).")
        if self.beulen is not None:
            zeichen, wert, grenze, _ = self.beulen
            if wert > grenze:
                return (f"{zeichen} = {wert:.1f} über {grenze:.1f} nach Tabelle 6: das lokale "
                        f"Beulen rechnet das Werkzeug bei Verbundstützen nicht (5.3.1.6).")
        if not DELTA_AB <= self.delta <= DELTA_BIS:
            wie = "Stahlbetonstütze" if self.delta < DELTA_AB else "Stahlstütze"
            return (f"δ = {self.delta:.2f} liegt nicht zwischen {DELTA_AB:g} und {DELTA_BIS:g}: "
                    f"als {wie} nachweisen (5.3.1.2).")
        return ""

    # -- Steifigkeit und Kurven ----------------------------------------------------------

    @cached_property
    def stark(self) -> Optional[str]:
        """Die starke Achse des Profils -- ``None`` beim runden und beim quadratischen Rohr."""
        return st.starke_achse({a: sum(w.I(a) for w in self.der_art(Baustoffart.BAUSTAHL))
                                for a in ("y", "z")})

    def kurve(self, achse: str) -> Tuple[str, float, str]:
        """Tabelle 7 um ``achse``: die Kurve, der Nenner von ``e_0 = L/Nenner`` und warum."""
        if self.art is Art.ROHR:
            rho = f"ρ_s = {100.0 * self.rho_s:.1f} %"
            if self.rho_s <= ROHR_RHO:
                return "a", 300.0, f"{self.art.value}, {rho} bis 3 %"
            return "b", 200.0, f"{self.art.value}, {rho} über 3 %"
        stark = self.stark == achse
        kurve, nenner = ("b", 200.0) if stark else ("c", 150.0)
        return kurve, nenner, f"{self.art.value}, um die {'starke' if stark else 'schwache'} Achse"

    def EI(self, achse: str, E_c: Mapping[int, float], beton: float) -> float:
        """``Σ E I`` um ``achse`` in N mm², der Beton mit ``beton · E_c``, ``E_c`` je Gruppe."""
        summe = 0.0
        for w in self.werkstoffe:
            E = beton * E_c[w.gruppe] if w.art is Baustoffart.BETON else self.f.E[w.gruppe]
            summe += self.zaehlt(w) * E * w.I(achse)
        return summe

    def E_c_eff(self, staendig: float, kriechzahl: float) -> Dict[int, float]:
        """(19) je Beton, in N/mm² -- ``staendig`` ist ``N_G,Ed/N_Ed``."""
        return {w.gruppe: self.f.E[w.gruppe] / (1.0 + staendig * kriechzahl)
                for w in self.der_art(Baustoffart.BETON)}

    # -- Plastisch ----------------------------------------------------------------------

    @cached_property
    def starr(self) -> Starrplastisch:
        """Der Querschnitt in rechteckigen Spannungsbloecken -- der Betonstahl mit seinem Anteil."""
        anteil = [self.zaehlt(w) for w in self.werkstoffe]
        return self.verbund.starr([a * z for a, z in zip(anteil, self.f.zug)],
                                  [a * d for a, d in zip(anteil, self.f.druck)])

    def M_pl(self, achse: str, M: float, N: float) -> Tuple[float, Optional[float]]:
        """
        Der plastische Biegewiderstand um ``achse`` bei ``N`` in N, zur
        Seite, die ``M`` zieht: sein Betrag in N mm und wie weit die
        Nulllinie von der Mitte zur gezogenen Seite liegt, in mm --
        ``(0, None)``, wo der Querschnitt ``N`` nicht traegt.
        """
        if not self.starr.traegt(N):
            return 0.0, None
        n = normale(st.seite_von(achse, M))
        z = self.starr.bei(n, N, self.mitte)
        return (abs(z.M_y if achse == "y" else z.M_z),
                z.linie.v - (n[0] * self.mitte[0] + n[1] * self.mitte[1]))


# -- Ein Fall -------------------------------------------------------------------------------


@dataclass(frozen=True)
class Knicken:
    """
    Die Achse ohne Moment, nach (15): in N und mm -- gehalten mit
    ``L_K = 0``, ``N_cr`` unendlich und ``χ_K = 1``.
    """

    achse: str
    L_K: float
    EI: float
    N_cr: float
    lam: float
    kurve: str
    grund: str
    phi: float
    chi: float
    N_K_Rd: float

    @property
    def gehalten(self) -> bool:
        return self.L_K == 0.0


@dataclass(frozen=True)
class Biegeachse:
    """
    Die Achse mit Moment, nach (25): in N und mm. Gehalten, mit ``L_K = 0``,
    waechst das Moment nicht: ``k = 1``, ohne Imperfektion.
    """

    achse: str
    gehalten: bool
    M: float
    """``|M_Ed|`` 1. Ordnung."""

    psi: float
    omega: float
    EI_d: float
    N_cr_eff: float
    """``math.inf``, wo die Achse gehalten oder die Stuetze null lang ist."""

    k: float
    k_0: float
    nenner: float
    e_0: float
    M_II: float
    """``math.inf``, wo ``|N_Ed|`` ``N_cr,eff`` erreicht: die Stuetze knickt aus."""

    M_pl: float
    M_pl_N: float
    lage: Tuple[Optional[float], Optional[float]]
    """Wie weit die Nulllinie ohne und mit ``N_Ed`` von der Mitte zur gezogenen Seite liegt."""

    mu: float
    """``μ_d``, hoechstens eins."""

    @property
    def knickt_aus(self) -> bool:
        return self.M_II == math.inf

    @property
    def nutzung(self) -> float:
        """``M_Ed,II/(μ_d M_pl,Rd)``."""
        widerstand = self.mu * self.M_pl
        return math.inf if widerstand == 0.0 else self.M_II / widerstand


@dataclass(frozen=True)
class Ergebnis:
    """Ein Fall der Stuetze -- in N und mm."""

    fall: st.Stabfall
    E_c: Dict[int, float]
    """(19) je Beton."""

    knicken: Dict[str, Knicken]
    biegung: Dict[str, Biegeachse]
    alpha_M: float
    fehlt: str = ""

    @property
    def N(self) -> float:
        return self.fall.N

    @property
    def summe(self) -> float:
        """Zweiachsig: ``Σ M_Ed,II/(μ_d M_pl,Rd)`` -- 5.3.5, siehe Dateikopf."""
        return sum(b.nutzung for b in self.biegung.values())

    @property
    def grade(self) -> List[Tuple[str, float]]:
        """Je Nachweis, was er sagt, und sein Erfuellungsgrad."""
        N = abs(self.N)
        grade = [(f"(15) um {a}", k.N_K_Rd / N) for a, k in self.knicken.items()]
        aus = [b for b in self.biegung.values() if b.knickt_aus]
        if aus:
            grade += [(f"(24) um {b.achse}: N_Ed erreicht N_cr,eff", b.N_cr_eff / N) for b in aus]
        elif self.biegung:
            was = ("(25) zweiachsig" if len(self.biegung) > 1
                   else f"(25) um {next(iter(self.biegung))}")
            grade.append((was, self.alpha_M / self.summe))
        return grade

    @property
    def massgebend(self) -> Tuple[str, float]:
        return min(self.grade, key=lambda x: x[1])


def rechnen(stuetze: Stuetze, fall: st.Stabfall, kriechzahl: float,
            momente: Mapping[str, float]) -> Ergebnis:
    """
    Ein Fall mit Druck -- ``momente`` je Achse in N mm, wie sie zaehlen
    (einachsig ohne ``M_z``), ``kriechzahl`` ``φ(t,t_0)``.
    """
    E_c = stuetze.E_c_eff(fall.staendig, kriechzahl)
    biegung = {a: _biegeachse(stuetze, fall, a, M, E_c) for a, M in momente.items() if M}
    knicken = {a: _knicken(stuetze, fall, a, E_c) for a in ("y", "z") if a not in biegung}
    fehlt = next((_zu_lang(fall, a) for a in biegung if _zu_lang(fall, a)), "")
    fehlt = fehlt or next((_zu_schlank(k) for k in knicken.values() if _zu_schlank(k)), "")
    return Ergebnis(fall, E_c, knicken, biegung, stuetze.alpha_M, fehlt)


def _zu_lang(fall: st.Stabfall, achse: str) -> str:
    """Warum die Knicklaenge um ``achse`` nicht zur Stuetze passt -- leer, wo sie passt."""
    L_K = fall.knicklaenge(achse) / 1e3
    if L_K <= fall.L:
        return ""
    return (f"Die Knicklänge L_K,{achse} = {L_K:.2f} m ist länger als die Stütze, L = "
            f"{fall.L:.2f} m: unverschieblich gehalten, wie (24) es verlangt, ist sie höchstens so "
            f"lang (5.3.4.1). Die Länge der Stütze angeben.")


def _zu_schlank(k: Knicken) -> str:
    if k.lam <= LAMBDA_BIS:
        return ""
    return (f"λ̄_{k.achse} = {k.lam:.2f} liegt über {LAMBDA_BIS:g}: dort endet das vereinfachte "
            f"Verfahren der Norm (5.3.2.1), ein anderes rechnet das Werkzeug nicht.")


def _knicken(stuetze: Stuetze, fall: st.Stabfall, achse: str, E_c: Mapping[int, float]) -> Knicken:
    kurve, _, grund = stuetze.kurve(achse)
    L_K = fall.knicklaenge(achse)
    EI = stuetze.EI(achse, E_c, BETON_LAMBDA)
    N_pl = stuetze.N_pl()
    if L_K == 0.0:
        return Knicken(achse, 0.0, EI, math.inf, 0.0, kurve, grund, 0.0, 1.0, N_pl)
    N_cr = math.pi ** 2 * EI / L_K ** 2
    lam = math.sqrt(stuetze.N_pl(charakteristisch=True) / N_cr)
    phi, chi = st.abminderung(lam, st.ALPHA_K[kurve], st.LAMBDA_0_KNICKEN)
    return Knicken(achse, L_K, EI, N_cr, lam, kurve, grund, phi, chi, chi * N_pl)


def _biegeachse(stuetze: Stuetze, fall: st.Stabfall, achse: str, M: float,
                E_c: Mapping[int, float]) -> Biegeachse:
    N = abs(fall.N)
    psi = fall.psi(achse)
    omega = st.omega(psi)
    _, nenner, _ = stuetze.kurve(achse)
    EI_d = BEIWERT_D * stuetze.EI(achse, E_c, BETON_D)
    (M_pl, lage_0), (M_pl_N, lage_N) = stuetze.M_pl(achse, M, 0.0), stuetze.M_pl(achse, M, fall.N)
    plastisch = (M_pl, M_pl_N, (lage_0, lage_N), min(1.0, M_pl_N / M_pl))
    if fall.knicklaenge(achse) == 0.0:
        return Biegeachse(achse, True, abs(M), psi, omega, EI_d, math.inf, 1.0, 0.0, nenner, 0.0,
                          abs(M), *plastisch)
    L = fall.L * 1e3
    N_cr_eff = math.pi ** 2 * EI_d / L ** 2 if L > 0.0 else math.inf
    e_0 = L / nenner
    if N >= N_cr_eff:
        return Biegeachse(achse, False, abs(M), psi, omega, EI_d, N_cr_eff, math.inf, math.inf,
                          nenner, e_0, math.inf, *plastisch)
    k_0 = 1.0 / (1.0 - N / N_cr_eff)
    k = max(1.0, omega * k_0)
    return Biegeachse(achse, False, abs(M), psi, omega, EI_d, N_cr_eff, k, k_0, nenner, e_0,
                      k * abs(M) + k_0 * N * e_0, *plastisch)


def momente(biegung_wirkt: Sequence[float]) -> Dict[str, float]:
    """Die Momente eines Falls je Achse in N mm -- aus ``Biegung.wirkt`` in Nm."""
    return {a: 1e3 * M for a, M in zip(("y", "z"), biegung_wirkt)}
