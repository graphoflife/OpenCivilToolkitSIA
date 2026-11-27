"""
opencivil/stahlbau/stabilitaet.py -- Knicken und Kippen eines Stabs aus Baustahl.

VERANTWORTUNG:
Was die Stabilitaet eines Stahlstabs nach SIA 263:2013 braucht, ohne
Rechenwerk und ohne Herleitung, in N, mm und N/mm² (:func:`rechnen`). Die
Herleitung schreibt :mod:`opencivil.nachweis.qa_stahl_stabilitaet`. Der Stab
hat den gezeichneten Querschnitt; ein Fall gibt ihm die Druckkraft, die
groessten Momente 1. Ordnung, die Verhaeltnisse ψ seiner Endmomente und die
Knick- und Kipplaengen (:class:`Stabfall`).

DIE WIDERSTAENDE NACH DER KLASSE:
Die Klasse im Fall wie in der Tragsicherheit
(:func:`~opencivil.stahlbau.widerstand.rechnen`), bei ``N_Ed`` und den
Momenten 1. Ordnung. Dann je Achse plastisch in den Klassen 1 und 2,
elastisch in Klasse 3 (5.2.9) und am wirksamen Querschnitt in Klasse 4 --
je einmal mit der Festigkeit, mit der gerechnet wird, und einmal mit
``f_y`` fuer die Schlankheiten.

KNICKEN (4.5.1, 5.3.8):
Je Achse ``N_cr = π² E I/L_K²``, ``λ̄_K = √(f_y A/N_cr)`` -- mit einem
Baustahl genau ``√(f_y/σ_cr,K)`` -- und ``χ_K`` nach (8) mit der Kurve aus
Figur 7 (:func:`kurve`): ``N_K,Rd = χ_K f_y A/γ_M1`` (7). In Klasse 4 mit
``A_eff`` statt ``A``, ``N_cr`` am ganzen Querschnitt (5.3.8). Eine
Knicklaenge null heisst: gehalten, ``N_cr`` unendlich.

KIPPEN (4.5.2, ANHANG B):
Um die starke Achse, wo ein Moment um sie wirkt und eine Kipplaenge
``L_D`` da ist: ``σ_cr,D = √(σ_Dv² + σ_Dw²)`` nach (91) bis (93), mit ``η``
nach (94) und dem Druckgurt nach Figur 40 (:func:`druckgurt`);
``M_cr = W_el σ_cr,D`` (90), ``λ̄_D = √(W f_y/M_cr)`` und ``χ_D`` nach (10)
mit ``α_D = 0.21`` der Walzprofile; ``M_D,Rd = χ_D W f_y/γ_M1`` (9), ``W``
nach der Klasse. In Klasse 4 ohne den Anteil nach Saint-Venant (B.4). Wo
gekippt wird, gilt (9) immer auch allein.

DAS ZUSAMMENWIRKEN:
* Klassen 1 bis 3: (50), in Klasse 3 mit elastischen Widerstaenden (5.2.9).
* Klassen 1 und 2, I-Walzprofil, Knicken aus der Ebene und Kippen nicht
  verhindert: auch (51) (5.1.10.2, 5.1.10.4).
* Klasse 4: (62) und (63), mit den Ersatzimperfektionen der Spalte EE von
  Figur 3 -- ohne Moment und ohne Versatz des wirksamen Schwerpunkts nur
  5.3.8.

DER ERFUELLUNGSGRAD -- wie in der Tragsicherheit
(:mod:`opencivil.stahlbau.widerstand`): die Normalkraft bleibt, die Momente
wachsen in ihrer Richtung, bis die Gleichung aufgeht. (50) ist in den
Momenten linear, ``α = (1 - N_Ed/N_K,Rd)/Σ m``; (51) mit der Potenz β,
``α = (a^β + b^β)^(-1/β)``. Ohne Moment ``N_K,Rd/|N_Ed|``. Wo schon die
Normalkraft allein nicht traegt, misst ``α`` sie (:attr:`Ergebnis.alpha_N`).
Wo zwei Gleichungen gelten duerfen -- (50) und (51) --, zaehlt die
guenstigere; wo beide gelten muessen -- (62) und (63), oder das
Zusammenwirken und (9) --, die unguenstigere.

WAS DAS WERKZEUG NICHT KANN -- der Fall sagt es grau (:attr:`Ergebnis.fehlt`):
* Kurve und Druckgurt kennt es nur fuer einen Querschnitt aus einem einzigen
  Profil. Fuer jeden anderen waehlt der Benutzer die Kurve je Achse; kippen
  laesst es ihn nicht.
* Anhang B gilt fuer doppelsymmetrische Querschnitte (B.3): das I und das
  Rechteckrohr. Ein U mit Kipplaenge und Moment um die starke Achse ist
  nicht fuehrbar.
* Biegedrillknicken (4.5.1.2), die Vergroesserung ξ (5.1.9.2) und die
  kritischen Kipplaengen der Tabelle 6 rechnet es nicht.

NACH VORGABE, NICHT NACHGESCHLAGEN:
* Das Rundrohr gilt als warmgefertigt, Kurve a -- wie in den Excel-Dateien
  des Benutzers. Fuer ein kaltgefertigtes waehlt er c.
* Unter ψ = -0.5 bleibt η bei 2.35, dem Wert bei -0.5: (94) gilt erst ab
  dort, und darunter waere η groesser.
* Der Druckgurt ohne Ausrundungen, die gedrueckte Steghoehe die Haelfte der
  Hoehe zwischen den Flanschen -- unter Biegung allein; beim Rechteckrohr
  mit beiden Stegen: Figur 40 zeigt nur das I.
* Rohre kippen mit dem ``α_D`` der Walzprofile.
* Mit mehreren Baustaehlen ``λ̄_K = √(Σ f_y A/N_cr)``.
* ``w_0`` nach Figur 3 mit der Knicklaenge als Stablaenge.
* In Klasse 4 mindert ``χ_D`` in (62) und (63) den Widerstand um die starke
  Achse: (67) nennt das Kippen nur fuer die Biegung allein.
* ψ gilt fuer ``ω`` und fuer ``η`` -- dieselben Endmomente.

AUF DER SICHEREN SEITE:
In Klasse 4 zaehlt der ganze Druckgurt, obwohl B.5 und 5.6.2.3 nur die
mitwirkenden Teile zulassen. Ohne die uebrigen waere sein
Traegheitsradius groesser: im Flansch eines I-Walzprofils wirkt alles mit,
und was fehlte -- ein Stegstreifen, die Mitte des Flanschs eines
Rechteckrohrs --, liegt nahe seiner Achse.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.wahl import Wahl
from opencivil.core.wert import kennung_aus
from opencivil.querschnitt.biegung import Biegung
from opencivil.querschnitt.geometrie import Punkt
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.stahlbau import widerstand as wd
from opencivil.stahlbau.querschnitt import Stahlquerschnitt, normale
from opencivil.stahlprofile import tabelle
from opencivil.stahlprofile.formen import I_PROFIL, RECHTECKROHR_GERUNDET
from opencivil.stahlprofile.lage import Profillage

REFERENZ_KNICKEN = "SIA 263:2013, 4.5.1.3, (7); 4.5.1.4, (8); Tabelle 8"
REFERENZ_KURVE = "SIA 263:2013, 4.5.1.5; 4.5.1.6; Figur 7"
REFERENZ_KLASSE_4 = "SIA 263:2013, 4.5.1.3; 5.3.8"
REFERENZ_SCHLANKHEIT = "SIA 263:2013, 4.5.1.7"
REFERENZ_KIPPEN = "SIA 263:2013, 4.5.2.2, (9); 4.5.2.3, (10)"
REFERENZ_DRUCKGURT = "SIA 263:2013, Anhang B.5, (93); Figur 40"
REFERENZ_ETA = "SIA 263:2013, Anhang B.6, (94); Figur 41"
REFERENZ_OMEGA = "SIA 263:2013, 5.1.9.1; 5.1.10.3"
REFERENZ_50 = "SIA 263:2013, 5.1.10.1, (50); 5.2.9"
REFERENZ_51 = "SIA 263:2013, 5.1.10.2, (51); 5.1.10.4"
REFERENZ_62 = "SIA 263:2013, 5.3.9, (62), (63); 4.2.3.2, Figur 3"


class Knickkurve(Wahl):
    """Die Knickspannungskurve einer Achse: die des Profils nach Figur 7 oder eine gewaehlte."""

    PROFIL = "profil"
    A = "a"
    B = "b"
    C = "c"
    D = "d"

    @property
    def beschriftung(self) -> str:
        return "aus dem Profil" if self is Knickkurve.PROFIL else self.value

    @property
    def erklaerung(self) -> str:
        if self is Knickkurve.PROFIL:
            return ("Die Kurve, die Figur 7 dem Profil zuweist – nur für einen Querschnitt aus "
                    "einem einzigen Profil")
        return f"Kurve {self.value}: α_K = {ALPHA_K[self.value]:.2f} (Tabelle 8)"


#: Tabelle 8: der Imperfektionsbeiwert je Kurve.
ALPHA_K = {"a": 0.21, "b": 0.34, "c": 0.49, "d": 0.76}

#: Bis wohin nichts gemindert wird: λ̄_0 in (8) und in (10).
LAMBDA_0_KNICKEN = 0.2
LAMBDA_0_KIPPEN = 0.4

#: 4.5.2.3: α_D der Walzprofile -- geschweisste haben 0.49, die kippen hier nicht.
ALPHA_D_GEWALZT = 0.21

#: 4.5.1.7: die Schlankheit, die ein Haupttragelement in der Regel nicht ueberschreitet.
SCHLANKHEIT = 200.0

#: Figur 3, Spalte EE: ``w_0 = L/Nenner`` je Kurve.
W0_NENNER = {"a": 300.0, "b": 250.0, "c": 200.0, "d": 150.0}

#: 5.1.9.1: das kleinste ω.
OMEGA_MIN = 0.4

#: Ab wo (94) gilt -- darunter bleibt η beim Wert dort (Dateikopf).
PSI_ETA_MIN = -0.5

#: Um so viel muss ein Traegheitsmoment groesser sein, damit seine Achse die starke ist.
STARK = 1.0 + 1e-6

#: Ab welchem Versatz in mm der wirksame Schwerpunkt neben dem ganzen liegt.
VERSATZ = 1e-6

#: Figur 7 ohne die I-Walzprofile: je Reihe die Kurve um beide Achsen und warum
#: -- nach der Reihe, nicht nach der Form: RRK und RRW haben dieselbe Form,
#: das eine kalt-, das andere warmgefertigt.
_KURVE_DER_REIHE: Dict[str, Tuple[str, str]] = {
    "ROR": ("a", "warmgefertigtes Hohlprofil"),
    "RRW": ("a", "warmgefertigtes Hohlprofil"),
    "RRK": ("c", "kaltgefertigtes Hohlprofil"),
    "UPE": ("c", "U-Profil"),
    "UNP": ("c", "U-Profil"),
    "VKT": ("c", "Vollquerschnitt"),
    "RND": ("c", "Vollquerschnitt"),
    "FL": ("c", "Vollquerschnitt"),
}

#: Was fehlt -- Saetze fuer die Herleitung und die Zusammenfassung.
KURVE_FEHLT = ("{was}: Figur 7 kennt das Werkzeug nur für einen Querschnitt aus einem einzigen "
               "Profil – {wahl}.")
KIPPEN_FEHLT = ("Kippen rechnet das Werkzeug nur für einen Querschnitt aus einem einzigen I-Profil "
                "oder Rechteckrohr: Anhang B gilt für doppelsymmetrische Querschnitte. Ist der "
                "Stab gehalten, ist die Kipplänge null.")


def abminderung(lam: float, alpha: float, lam_0: float) -> Tuple[float, float]:
    """``Φ`` und ``χ`` nach (8) mit ``λ̄_0 = 0.2`` oder (10) mit 0.4 -- ``χ`` hoechstens eins."""
    phi = 0.5 * (1.0 + alpha * (lam - lam_0) + lam * lam)
    return phi, min(1.0, 1.0 / (phi + math.sqrt(phi * phi - lam * lam)))


def eta(psi: float) -> float:
    """``η`` nach (94); unter ψ = -0.5 der Wert dort (Dateikopf)."""
    psi = max(psi, PSI_ETA_MIN)
    return 1.75 - 1.05 * psi + 0.3 * psi * psi


def omega(psi: float) -> float:
    """``ω`` nach 5.1.9.1, mindestens 0.4."""
    return max(OMEGA_MIN, 0.6 + 0.4 * psi)


def kurve(profil: tabelle.Profil, stark: bool) -> Tuple[str, str]:
    """
    Die Kurve eines Profils nach Figur 7 fuer das Knicken um seine starke oder
    schwache Achse -- und in Worten, warum.
    """
    if profil.form is not I_PROFIL:
        return _KURVE_DER_REIHE[profil.reihe]
    m = profil.masse
    h, b, t_f = m["h"], m["b"], m["t_f"]
    if t_f > 100.0:
        return "d", "Walzprofil mit t_f über 100 mm"
    achse = "starke" if stark else "schwache"
    if (h - t_f) / b > 1.2 and t_f <= 40.0:
        return ("a" if stark else "b"), (f"schmales Walzprofil, (h − t_f)/b = "
                                         f"{(h - t_f) / b:.2f} > 1.2, um die {achse} Achse")
    return ("b" if stark else "c"), f"Walzprofil um die {achse} Achse"


@dataclass(frozen=True)
class Druckgurt:
    """
    Der Druckgurt nach Figur 40, in mm: der Flansch ``b × t_f`` und je Steg
    ein Drittel seiner gedrueckten Hoehe ``h_c`` -- beim Rechteckrohr zwei
    Stege im Abstand ``e`` von der Mitte.
    """

    b: float
    t_f: float
    t_w: float
    h_c: float
    stege: int
    e: float

    @property
    def A(self) -> float:
        return self.b * self.t_f + self.stege * self.t_w * self.h_c / 3.0

    @property
    def I(self) -> float:
        """Um die Achse in der Mitte des Flanschs, quer zu ihm."""
        steg = self.h_c / 3.0
        return (self.t_f * self.b ** 3 / 12.0
                + self.stege * (steg * self.t_w ** 3 / 12.0 + self.t_w * steg * self.e ** 2))

    @property
    def i(self) -> float:
        return math.sqrt(self.I / self.A)


def druckgurt(profil: tabelle.Profil) -> Optional[Druckgurt]:
    """
    Der Druckgurt eines doppelsymmetrischen Profils mit starker Achse: beim
    I und beim Rechteckrohr -- sonst ``None``. Die gedrueckte Steghoehe ist
    bei reiner Biegung die Haelfte der Hoehe zwischen den Flanschen.
    """
    m = profil.masse
    if profil.form is I_PROFIL:
        return Druckgurt(m["b"], m["t_f"], m["t_w"], (m["h"] - 2.0 * m["t_f"]) / 2.0, 1, 0.0)
    if profil.form is RECHTECKROHR_GERUNDET and m["h"] != m["b"]:
        hoch, breit, t = max(m["h"], m["b"]), min(m["h"], m["b"]), m["t"]
        return Druckgurt(breit, t, t, (hoch - 2.0 * t) / 2.0, 2, (breit - t) / 2.0)
    return None


def einzelprofil(teile: Iterable[Tuple[str, Optional[Profillage]]]) -> Optional[tabelle.Profil]:
    """
    Das Profil, wenn der Querschnitt nur aus ihm besteht -- mit seinen
    Loechern, die seine Kennung tragen, ohne jede andere Flaeche; sonst
    ``None``. ``teile`` je Flaeche ihre Kennung und, beim Umriss eines
    Profils, seine Lage: aus der Analyse wie aus der Zeichnung
    (:mod:`opencivil.web.zeichengeometrie`) -- eine Regel fuer beide.
    """
    kennungen, lagen = set(), []
    for kennung, lage in teile:
        kennungen.add(kennung)
        if lage is not None:
            lagen.append(lage)
    if len(kennungen) != 1 or len(lagen) != 1:
        return None
    return tabelle.profil(lagen[0].name)


def starke_achse(I: Mapping[str, float]) -> Optional[str]:
    """Die Achse mit dem groesseren Traegheitsmoment -- ``None``, wo beide gleich sind."""
    if I["y"] > STARK * I["z"]:
        return "y"
    if I["z"] > STARK * I["y"]:
        return "z"
    return None


def kurven_des_profils(profil: tabelle.Profil,
                       I: Mapping[str, float]) -> Dict[str, Tuple[str, str]]:
    """Je Achse die Kurve, die Figur 7 dem Profil zuweist, und warum -- ``I`` je Achse."""
    s = starke_achse(I)
    return {a: kurve(profil, s == a) for a in ("y", "z")}


def rechenkurven(wahl: Mapping[str, Knickkurve], profil: Optional[tabelle.Profil],
                 I: Mapping[str, float]) -> Dict[str, Optional[Tuple[str, str]]]:
    """
    Je Achse die Kurve, mit der gerechnet wird, und warum: die gewaehlte, sonst
    die des einzigen Profils (:func:`einzelprofil`) -- ``None``, wo es keines
    gibt.
    """
    eigene = kurven_des_profils(profil, I) if profil is not None else {}
    return {a: (w.value, "gewählt") if w is not Knickkurve.PROFIL else eigene.get(a)
            for a, w in wahl.items()}


def fehlende_kurven(kurven: Mapping[str, Optional[Tuple[str, str]]],
                    faelle: Iterable[Stabfall]) -> str:
    """
    Welche Kurve den ``faelle`` fehlt, als Satz: um eine Achse, um die einer
    von ihnen knickt, ohne Kurve (:func:`rechenkurven`) -- leer, wo keine
    fehlt. Eine Regel fuer den Fall und die Kachel davor
    (:mod:`opencivil.web.zeichengeometrie`).
    """
    faelle = list(faelle)
    fehlt = [a for a in ("y", "z")
             if kurven[a] is None and any(f.knicklaenge(a) > 0.0 for f in faelle)]
    if not fehlt:
        return ""
    if len(fehlt) == 1:
        return KURVE_FEHLT.format(was=f"Die Knickspannungskurve um {fehlt[0]} fehlt",
                                  wahl="eine wählen")
    return KURVE_FEHLT.format(was="Die Knickspannungskurven um y und um z fehlen",
                              wahl="je eine wählen")


def seite_von(achse: str, M: float) -> Zugseite:
    """Die Seite, die ein Moment um ``achse`` zieht: ``M_y ≥ 0`` unten, ``M_z ≥ 0`` links."""
    if achse == "y":
        return Zugseite.UNTEN if M >= 0.0 else Zugseite.OBEN
    return Zugseite.LINKS if M >= 0.0 else Zugseite.RECHTS


def quer(achse: str) -> str:
    return "z" if achse == "y" else "y"


# -- Der Stab und sein Fall -----------------------------------------------------------


@dataclass(frozen=True)
class Stab:
    """Was jeder Fall vom Querschnitt braucht -- in mm, mm⁴ und N/mm²."""

    stahl: Stahlquerschnitt
    f: Sequence[float]
    """Je Gruppe die Fliessgrenze, mit der gerechnet wird -- ``f_y/γ_M1`` oder ``f_y``."""

    f_k: Sequence[float]
    """Je Gruppe ``f_y`` -- fuer die Schlankheiten."""

    eps: Sequence[float]
    E: float
    G: float
    I: Dict[str, float]
    I_T: float
    bezug: Punkt
    """Der Schwerpunkt -- um ihn wirken die Momente."""

    biegung: Biegung
    kurven: Dict[str, Knickkurve]
    profil: Optional[tabelle.Profil]
    """Das einzige Profil des Querschnitts -- ``None``, wo er mehr hat (:func:`einzelprofil`)."""

    @property
    def stark(self) -> Optional[str]:
        return starke_achse(self.I)

    @property
    def A(self) -> float:
        return self.stahl.werte().A

    def i(self, achse: str) -> float:
        return math.sqrt(self.I[achse] / self.A)

    def kurve(self, achse: str) -> Optional[Tuple[str, str]]:
        """Die Kurve um ``achse`` und warum -- ``None``, wo sie fehlt (:func:`rechenkurven`)."""
        return rechenkurven(self.kurven, self.profil, self.I)[achse]


@dataclass(frozen=True)
class Stabfall:
    """
    Ein Fall des Stabs, in SI wie ein Lastfall der Analyse: ``N`` in N,
    negativ Druck, die Momente in Nm um den Schwerpunkt, die Laengen in m --
    eine Laenge null heisst gehalten. Nur im Verbund zaehlen ``staendig``
    und ``L`` (:mod:`opencivil.verbund.stuetze`).
    """

    name: str
    N: float = 0.0
    M_y: float = 0.0
    M_z: float = 0.0
    psi_y: float = 1.0
    psi_z: float = 1.0
    L_K_y: float = 0.0
    L_K_z: float = 0.0
    L_D: float = 0.0
    staendig: float = 1.0
    """Der staendige Anteil der Normalkraft, ``N_G,Ed/N_Ed``: er kriecht."""

    L: float = 0.0
    """Die Laenge der Stuetze, fuer ``k`` (24) und die Ersatzimperfektion."""

    @property
    def kennung(self) -> str:
        return kennung_aus(self.name)

    def psi(self, achse: str) -> float:
        return self.psi_y if achse == "y" else self.psi_z

    def knicklaenge(self, achse: str) -> float:
        """In mm."""
        return 1e3 * (self.L_K_y if achse == "y" else self.L_K_z)


# -- Die Ergebnisse -----------------------------------------------------------------------


@dataclass(frozen=True)
class Knicken:
    """Das Knicken um eine Achse, in N und mm -- ohne Kurve, wo der Stab gehalten ist."""

    achse: str
    L_K: float
    N_cr: float
    """``math.inf``, wo der Stab gehalten ist."""

    lam: float
    kurve: str
    grund: str
    phi: float
    chi: float
    N_K_Rd: float
    schlankheit: float
    """``λ_K = L_K/i`` nach 4.5.1.7."""

    @property
    def gehalten(self) -> bool:
        return self.L_K == 0.0

    def rest(self, N: float) -> float:
        """``1 - |N|/N_cr``."""
        return 1.0 - abs(N) / self.N_cr


@dataclass(frozen=True)
class Kippen:
    """Das Kippen um die starke Achse, in N, mm und N/mm²."""

    achse: str
    seite: Zugseite
    eta: float
    gurt: Druckgurt
    L_K: float
    """``L_D/√η``, die Knicklaenge des Druckgurts."""

    sigma_Dv: float
    sigma_Dw: float
    sigma_cr: float
    W_el: float
    M_cr: float
    M_Rk: float
    lam: float
    phi: float
    chi: float
    M_D_Rd: float


@dataclass(frozen=True)
class Glied50:
    """Ein Moment in (50): ``ω/(1 - N/N_cr) · |M_Ed|/M_Rd``."""

    achse: str
    omega: float
    rest: float
    """``1 - |N_Ed|/N_cr``."""

    M_Ed: float
    M_Rd: float
    kippen: bool
    """Ob ``M_Rd`` hier ``M_D,Rd`` ist."""

    @property
    def m(self) -> float:
        return self.omega / self.rest * abs(self.M_Ed) / self.M_Rd


@dataclass(frozen=True)
class Gleichung51:
    """(51) mit ihren Teilen, in N und N·mm -- ``s`` die starke Achse, ``w`` die schwache."""

    s: str
    w: str
    beta: float
    b: float
    h: float
    t_f: float
    M_D_Rd_min: float
    """Mit ``η = 1`` bei zweiachsiger Biegung, sonst wie ``M_D,Rd``."""

    M_s_red: float
    M_w_red: float
    begrenzt: bool
    """Ob ``ω_s M_D,Rd`` ``M_s,red,Rd`` begrenzt."""

    a: float
    """``ω_s |M_s,Ed|/M_s,red,Rd``."""

    c: float
    """``ω_w |M_w,Ed|/M_w,red,Rd``."""

    @property
    def alpha(self) -> float:
        summe = self.a ** self.beta + self.c ** self.beta
        return summe ** (-1.0 / self.beta) if summe > 0.0 else math.inf


@dataclass(frozen=True)
class Gleichung62:
    """
    (62) oder (63): ``n = |N_Ed|/(f_y A_eff)`` und die Glieder des wirksamen
    Querschnitts, das der Achse ``verstaerkt`` mit ``1/(1 - N/N_cr)`` --
    leer, wo schon ``N_cr`` erreicht ist.
    """

    verstaerkt: str
    n: float
    glieder: List[wd.Glied]
    alpha: Optional[float]
    """
    Der Faktor auf die Momente -- ohne Moment auf die Normalkraft; ``None``,
    wo schon die Normalkraft nicht traegt: dann :attr:`alpha_N`.
    """

    alpha_N: Optional[float]


@dataclass
class Ergebnis:
    """Was ein Fall am Stab ergibt -- siehe Dateikopf. Kraefte in N, Momente in N·mm."""

    fall: Stabfall
    N: float
    M: Dict[str, float]
    x: wd.Fall
    """Der Fall am Querschnitt: seine Klasse und die Bleche."""

    fehlt: str = ""
    """Warum der Fall nicht fuehrbar ist -- leer, wo er es ist."""

    rd: Optional[wd.Widerstaende] = None
    rk: Optional[wd.Widerstaende] = None
    """Dieselben Widerstaende mit ``f_y`` -- fuer die Schlankheiten."""

    wirksam: Optional[wd.Wirksame] = None
    """In Klasse 4 der wirksame Querschnitt, mit dem gerechnet wird."""

    knicken: Dict[str, Knicken] = field(default_factory=dict)
    kippen: Optional[Kippen] = None
    kippen_min: Optional[Kippen] = None
    """Mit ``η = 1`` -- fuer (51) bei zweiachsiger Biegung, wo ``η`` nicht schon eins ist."""

    glieder: List[Glied50] = field(default_factory=list)
    alpha_50: Optional[float] = None
    g51: Optional[Gleichung51] = None
    alpha_9: Optional[float] = None
    g62: List[Gleichung62] = field(default_factory=list)
    w_0: Dict[str, float] = field(default_factory=dict)
    alpha: float = math.inf
    alpha_N: Optional[float] = None
    """Wo schon die Normalkraft allein nicht traegt: um welchen Faktor sie kleiner sein muesste."""

    @property
    def klasse(self) -> int:
        return self.x.klasse

    @property
    def mit_moment(self) -> bool:
        return any(m != 0.0 for m in self.M.values())

    @property
    def N_K_Rd(self) -> float:
        return min(k.N_K_Rd for k in self.knicken.values())

    @property
    def n(self) -> float:
        """``|N_Ed|/N_K,Rd``."""
        return abs(self.N) / self.N_K_Rd

    @property
    def versatz(self) -> Tuple[float, float]:
        """Wie weit der wirksame Schwerpunkt bei Druck neben dem ganzen liegt, in mm."""
        if self.wirksam is None:
            return 0.0, 0.0
        w = self.wirksam.widerstaende
        return w.druck[0] - w.zug[0], w.druck[1] - w.zug[1]

    @property
    def mit_versatz(self) -> bool:
        return any(abs(e) > VERSATZ for e in self.versatz)


# -- Rechnen -------------------------------------------------------------------------------


def rechnen(stab: Stab, fall: Stabfall) -> Ergebnis:
    """Ein Fall am Stab -- siehe Dateikopf."""
    M_y, M_z = stab.biegung.wirkt(fall.M_y * 1e3, fall.M_z * 1e3)
    M = {"y": M_y, "z": M_z}
    x = wd.rechnen(stab.stahl, stab.f, stab.eps, fall.N, M_y, M_z, (), stab.bezug, stab.biegung)
    e = Ergebnis(fall, fall.N, M, x)
    if x.rohr_klasse_4:
        e.fehlt = wd.ROHR_KLASSE_4
        return e
    e.fehlt = fehlende_kurven({a: stab.kurve(a) for a in ("y", "z")}, [fall])
    if e.fehlt:
        return e
    _widerstaende(stab, e)
    e.knicken = {a: _knicken(stab, e, a) for a in ("y", "z")}
    s = stab.stark
    if s is not None and M[s] != 0.0 and fall.L_D > 0.0:
        gurt = druckgurt(stab.profil) if stab.profil is not None else None
        if gurt is None:
            e.fehlt = KIPPEN_FEHLT
            return e
        seite = seite_von(s, M[s])
        e.kippen = _kippen(stab, e, s, seite, gurt, eta(fall.psi(s)))
        if all(M.values()) and e.kippen.eta != 1.0:
            e.kippen_min = _kippen(stab, e, s, seite, gurt, 1.0)
    if e.klasse == 4 and (e.mit_moment or e.mit_versatz):
        _gleichungen_62(e)
    else:
        _gleichung_50(e)
        if e.alpha_N is None and _mit_51(stab, e):
            _gleichung_51(stab, e)
        e.alpha = (e.alpha_N if e.alpha_N is not None
                   else max(e.alpha_50, e.g51.alpha if e.g51 is not None else 0.0))
    if e.kippen is not None and e.alpha_N is None:
        e.alpha_9 = e.kippen.M_D_Rd / abs(M[e.kippen.achse])
        e.alpha = min(e.alpha, e.alpha_9)
    return e


def _widerstaende(stab: Stab, e: Ergebnis) -> None:
    """Die Widerstaende nach der Klasse des Falls: mit der Festigkeit der Rechnung, mit ``f_y``."""
    ab = wd.abmindern(stab.stahl, ())
    for f, wohin in ((stab.f, "rd"), (stab.f_k, "rk")):
        if e.klasse <= 2:
            w = wd.plastische(stab.stahl, f)
        elif e.klasse == 3:
            w = wd.elastische(stab.stahl, f)
        else:
            wirksam = wd.wirksame(ab, f, stab.eps, tuple(Zugseite))
            assert wirksam is not None  # ein Rundrohr der Klasse 4 kam nicht bis hier
            if wohin == "rd":
                e.wirksam = wirksam
            w = wirksam.widerstaende
        setattr(e, wohin, w)


def _knicken(stab: Stab, e: Ergebnis, achse: str) -> Knicken:
    L_K = e.fall.knicklaenge(achse)
    if L_K == 0.0:
        return Knicken(achse, 0.0, math.inf, 0.0, "", "gehalten", 0.0, 1.0, e.rd.N_druck, 0.0)
    N_cr = math.pi ** 2 * stab.E * stab.I[achse] / L_K ** 2
    lam = math.sqrt(e.rk.N_druck / N_cr)
    kurve_, grund = stab.kurve(achse)
    phi, chi = abminderung(lam, ALPHA_K[kurve_], LAMBDA_0_KNICKEN)
    return Knicken(achse, L_K, N_cr, lam, kurve_, grund, phi, chi, chi * e.rd.N_druck,
                   L_K / stab.i(achse))


def _kippen(stab: Stab, e: Ergebnis, s: str, seite: Zugseite, gurt: Druckgurt,
            eta_: float) -> Kippen:
    el = stab.stahl.elastisch(normale(seite))
    W_el = el.I / max(el.abstaende)
    L_D = e.fall.L_D * 1e3
    # B.4: wo der Querschnitt Klasse 3 nicht erfuellt, ohne Saint-Venant.
    sigma_Dv = (0.0 if e.klasse == 4 else
                eta_ * math.pi / (L_D * W_el) * math.sqrt(stab.G * stab.I_T * stab.E
                                                           * stab.I[quer(s)]))
    L_K = L_D / math.sqrt(eta_)
    sigma_Dw = math.pi ** 2 * stab.E / (L_K / gurt.i) ** 2
    sigma_cr = math.hypot(sigma_Dv, sigma_Dw)
    M_cr = W_el * sigma_cr
    lam = math.sqrt(e.rk.M[seite] / M_cr)
    phi, chi = abminderung(lam, ALPHA_D_GEWALZT, LAMBDA_0_KIPPEN)
    return Kippen(s, seite, eta_, gurt, L_K, sigma_Dv, sigma_Dw, sigma_cr, W_el, M_cr,
                  e.rk.M[seite], lam, phi, chi, chi * e.rd.M[seite])


def _M_Rd(e: Ergebnis, achse: str, kippen: Optional[Kippen]) -> float:
    """Der Biegewiderstand um ``achse`` zur Seite des Moments -- um die starke mit dem Kippen."""
    if kippen is not None and kippen.achse == achse:
        return kippen.M_D_Rd
    return e.rd.M[seite_von(achse, e.M[achse])]


def _gleichung_50(e: Ergebnis) -> None:
    """(50): ``N_Ed/N_K,Rd + Σ ω/(1 - N_Ed/N_cr) · M_Ed/M_Rd ≤ 1``."""
    if e.n >= 1.0:
        e.alpha_N = 1.0 / e.n
        return
    for achse in ("y", "z"):
        if e.M[achse] != 0.0:
            e.glieder.append(Glied50(achse, omega(e.fall.psi(achse)), e.knicken[achse].rest(e.N),
                                     e.M[achse], _M_Rd(e, achse, e.kippen),
                                     e.kippen is not None and e.kippen.achse == achse))
    if not e.glieder:
        e.alpha_50 = 1.0 / e.n if e.N else math.inf
        return
    e.alpha_50 = (1.0 - e.n) / sum(g.m for g in e.glieder)


def _mit_51(stab: Stab, e: Ergebnis) -> bool:
    """
    Ob (51) gelten darf: Klasse 1 oder 2, ein I-Walzprofil, ein Moment, und
    weder das Knicken aus der Ebene noch das Kippen verhindert.
    """
    s = stab.stark
    return (e.klasse <= 2 and e.mit_moment and stab.profil is not None
            and stab.profil.form is I_PROFIL and s is not None
            and e.fall.L_D > 0.0 and e.fall.knicklaenge(quer(s)) > 0.0)


def _gleichung_51(stab: Stab, e: Ergebnis) -> None:
    """(51) mit den Achsen des Profils -- die starke heisst dort y."""
    s = stab.stark
    w = quer(s)
    m = stab.profil.masse
    b, h, t_f = m["b"], m["h"], m["t_f"]
    rest = 1.0 - e.n
    beta = max(1.0, 0.4 + abs(e.N) / e.rd.N_druck + b / (h - t_f))
    M_D_Rd = _M_Rd(e, s, e.kippen)
    M_D_Rd_min = _M_Rd(e, s, e.kippen_min or e.kippen)
    omega_s, omega_w = omega(e.fall.psi(s)), omega(e.fall.psi(w))
    roh = M_D_Rd_min * rest * e.knicken[s].rest(e.N)
    M_s_red = min(roh, omega_s * M_D_Rd)
    M_w_red = e.rd.M[seite_von(w, e.M[w])] * rest * e.knicken[w].rest(e.N)
    e.g51 = Gleichung51(s, w, beta, b, h, t_f, M_D_Rd_min, M_s_red, M_w_red, roh > M_s_red,
                        omega_s * abs(e.M[s]) / M_s_red, omega_w * abs(e.M[w]) / M_w_red)


def _gleichungen_62(e: Ergebnis) -> None:
    """(62) und (63) am wirksamen Querschnitt, je mit einem verstaerkten Glied."""
    w = e.rd
    e_y, e_z = e.versatz
    versatz = {"y": e_z, "z": e_y}  # um y wirkt der Versatz in z
    for achse in ("y", "z"):
        k = e.knicken[achse]
        e.w_0[achse] = 0.0 if k.gehalten else k.L_K / W0_NENNER[k.kurve]
    # Die Imperfektion wirkt, wohin das Moment zieht -- ohne Moment wohin der Versatz.
    richtung = {a: math.copysign(1.0, e.M[a] or e.N * versatz[a] or 1.0) for a in ("y", "z")}

    def glieder(verstaerkt: str, N: float, mit_moment: bool) -> Optional[List[wd.Glied]]:
        """Die Glieder bei ``N`` -- ``None``, wo ``N`` die Knicklast erreicht."""
        liste = []
        for achse in ("y", "z"):
            faktor = 1.0
            if achse == verstaerkt:
                faktor = e.knicken[achse].rest(N)
                if faktor <= 0.0:
                    return None
            if e.kippen is not None and e.kippen.achse == achse:
                faktor *= e.kippen.chi
            plus, minus = ((Zugseite.UNTEN, Zugseite.OBEN) if achse == "y"
                           else (Zugseite.LINKS, Zugseite.RECHTS))
            liste.append(wd.Glied(achse, e.M[achse] if mit_moment else 0.0,
                                  N * versatz[achse] + richtung[achse] * abs(N) * e.w_0[achse],
                                  faktor * w.M[plus], faktor * w.M[minus]))
        return liste

    def nutzung(verstaerkt: str, mu: float) -> float:
        """Die linke Seite ohne Moment bei ``μ N_Ed`` -- unendlich ab der Knicklast."""
        g = glieder(verstaerkt, mu * e.N, False)
        return math.inf if g is None else wd.nutzung(mu * abs(e.N) / w.N_druck, g, 0.0)

    n = abs(e.N) / w.N_druck
    for verstaerkt in ("y", "z"):
        g = glieder(verstaerkt, e.N, True)
        traegt = g is not None and wd.nutzung(n, g, 0.0) <= 1.0
        if traegt and e.mit_moment:
            alpha, alpha_N = wd.skala(n, g), None
        else:
            # Ohne Moment -- nur mit dem Versatz -- waechst die Normalkraft.
            mu = _faktor(lambda mu: nutzung(verstaerkt, mu))
            alpha, alpha_N = (mu, None) if traegt else (None, mu)
        e.g62.append(Gleichung62(verstaerkt, n, g or [], alpha, alpha_N))
    faktoren = [g.alpha_N for g in e.g62 if g.alpha_N is not None]
    if faktoren:
        e.alpha_N = min(faktoren)
        e.alpha = e.alpha_N
    else:
        e.alpha = min(g.alpha for g in e.g62)


def _faktor(nutzung: Callable[[float], float]) -> float:
    """
    Das ``μ`` mit ``nutzung(μ) = 1`` -- die linke Seite waechst mit ``μ`` und
    ist bei null kleiner als eins. Durch Halbieren, bis auf 1e-12 genau.
    """
    unten, oben = 0.0, 1.0
    while nutzung(oben) <= 1.0:
        unten, oben = oben, 2.0 * oben
    while oben - unten > 1e-12 * oben:
        mitte = 0.5 * (unten + oben)
        unten, oben = (mitte, oben) if nutzung(mitte) <= 1.0 else (unten, mitte)
    return unten
