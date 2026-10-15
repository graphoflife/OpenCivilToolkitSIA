"""
opencivil/nachweis/gebrauchsebene.py -- die Dehnungsebene des gezeichneten Querschnitts unter Gebrauchslast.

VERANTWORTUNG:
Ein Lastfall traegt N, M_y und M_z; gesucht ist die Ebene, die alle drei
haelt -- am Querschnitt mit den Gesetzen einer Rechenwahl, fuer die
Stahlspannungen und die Zwaengung auf Biegung
(:mod:`opencivil.nachweis.qa_gebrauch`).

DIE SUCHE:
Zu einer Neigung ψ der Zugrichtung ist es die Aufgabe der Platte: N und das
Moment in Zugrichtung bestimmen ``eps_m`` und ``chi``
(:class:`~opencivil.nachweis.querschnittsloeser.FaserloeserIllinois`).
Uebrig bleibt das Moment entlang der Nulllinie, und ψ wird gedreht, bis auch
es stimmt (:func:`gebrauchsebene`): der Sekante nach, dann Illinois, und wo
die Sekante wegliefe, mit wachsenden Schritten nach beiden Seiten
eingegrenzt. Bei einem symmetrischen Querschnitt trifft schon die Neigung,
die zum Moment gehoert. Einachsig bleibt die Nulllinie waagrecht, und M_z
zaehlt nicht -- wie in der Tragsicherheit.

WAS ES KOSTET:
Jede Neigung ist eine ganze Suche ueber die Fasern. Halbiert brauchte die
schiefe Biegung am Unterzug des Beispiels zwanzig Neigungen zu je 85 ms;
mit Sekante und Illinois sind es eine Handvoll zu je wenigen ms.

EINHEITEN:
SI-Basis.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

from opencivil.core.latex import angabe, fest
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.nachweis.querschnittsloeser import FaserloeserIllinois
from opencivil.querschnitt.interaktion import Querschnitt, illinois

#: Wie weit sich die Neigung ψ der Ebene unter Gebrauchslast von der
#: entfernen darf, die bei Symmetrie gaelte -- nach jeder Seite, in Grad.
#: Weiter als 90° laege die Gegenrichtung, und die gehoert zur negativen
#: Kruemmung.
NEIGUNGSSCHRITTE = (2.0, 5.0, 10.0, 20.0, 35.0, 55.0, 75.0, 90.0)

#: Wann das Moment entlang der Nulllinie als getroffen gilt, als Teil der
#: groessten Schnittgroesse -- N mit einem Hebel von einem Meter gezaehlt.
QUER_SCHRANKE = 1e-7


@dataclass(frozen=True)
class Gebrauchsebene:
    """Die Dehnungsebene zu einem Lastfall -- und was sie erzeugt."""

    psi: float
    """Neigung der Zugrichtung, wie :class:`~opencivil.querschnitt.interaktion.Querschnitt` sie nimmt."""

    eps_m: float
    """Dehnung im Schwerpunkt."""

    chi: float
    """Kruemmung in Zugrichtung, 1/m."""

    N: float
    M_y: float
    M_z: float
    """Was die Ebene erzeugt -- die Probe."""

    eps_s: Tuple[float, ...]
    sigma_s: Tuple[float, ...]
    """Dehnung und Spannung je Bewehrung des Querschnitts."""

    konvergiert: bool = True


#: Wenn sich keine Ebene findet.
KEINE = Gebrauchsebene(psi=0.0, eps_m=0.0, chi=0.0, N=0.0, M_y=0.0, M_z=0.0,
                       eps_s=(), sigma_s=(), konvergiert=False)


def _bei_neigung(q: Querschnitt, psi: float, N: float, M_y: float,
                 M_z: float) -> Optional[Tuple[Gebrauchsebene, float]]:
    """
    Die Ebene bei dieser Neigung, die N und das Moment in Zugrichtung traegt
    -- und was ihr am Moment entlang der Nulllinie noch fehlt. Mit
    ``M = -(n_z·M_y + n_y·M_z)`` und ``M_quer = -(n_y·M_y - n_z·M_z)``, den
    Umkehrungen von :meth:`~opencivil.querschnitt.interaktion.Richtung.momente`.
    """
    r = q.richtung(psi)
    n_y, n_z = r.n
    loesung = FaserloeserIllinois(querschnitt=r.fasern, grenzen=r.grenzen).loese(
        N_Ed=N, M_Ed=-(n_z * M_y + n_y * M_z))
    if not loesung.konvergiert:
        return None
    k = r.fasern.kraefte(loesung.eps_m, loesung.chi)
    m_y, m_z = r.momente(k.N, k.M, k.M_quer)
    ebene = Gebrauchsebene(psi=r.psi, eps_m=loesung.eps_m, chi=loesung.chi, N=k.N,
                           M_y=m_y, M_z=m_z, eps_s=loesung.eps_s, sigma_s=loesung.sigma_s)
    return ebene, k.M_quer + (n_y * M_y - n_z * M_z)


def gebrauchsebene(q: Querschnitt, *, N: float, M_y: float, M_z: float,
                   einachsig: bool, start: Optional[float] = None) -> Gebrauchsebene:
    """
    Die Dehnungsebene, die ``N``, ``M_y`` und ``M_z`` im Gleichgewicht haelt.

    Einachsig mit waagrechter Nulllinie, ``M_z`` zaehlt nicht. Sonst wird die
    Neigung gesucht, bei der auch das Moment entlang der Nulllinie stimmt --
    von ``start`` aus oder von der, die bei Symmetrie gaelte; bei einem
    symmetrischen Querschnitt trifft schon sie. Sonst der Sekante nach, bis
    die Abweichung das Vorzeichen wechselt, dann Illinois. Laeuft die Sekante
    weg, wird nach beiden Seiten mit wachsenden Schritten eingegrenzt
    (:data:`NEIGUNGSSCHRITTE`), wie beim Widerstand in einer Momentenrichtung
    (:meth:`~opencivil.querschnitt.interaktion.Querschnitt.in_richtung`).
    """
    if einachsig:
        gefunden = _bei_neigung(q, -math.pi / 2.0 if M_y >= 0.0 else math.pi / 2.0,
                                N, M_y, 0.0)
        return gefunden[0] if gefunden else KEINE

    schranke = QUER_SCHRANKE * max(abs(M_y), abs(M_z), abs(N) * 1.0, 1.0)

    def abweichung(psi: float):
        gefunden = _bei_neigung(q, psi, N, M_y, M_z)
        return (math.nan, None) if gefunden is None else (gefunden[1], gefunden[0])

    def eingegrenzt(a: float, fa: float, b: float, fb: float) -> Gebrauchsebene:
        return illinois(abweichung, a, fa, b, fb, schranke_x=1e-12,
                        schranke_f=schranke) or KEINE

    mitte = Querschnitt.neigung_fuer(M_y, M_z) if start is None else start
    fa, ebene = abweichung(mitte)
    if ebene is None:
        return KEINE
    if abs(fa) <= schranke:
        return ebene

    # Der Sekante nach: zwischen zwei Knicken ist die Abweichung beinahe eine
    # Gerade in ψ.
    a, b = mitte, mitte + math.radians(1.0)
    fb, ebene = abweichung(b)
    for _ in range(8):
        if ebene is None or abs(b - mitte) > math.pi / 2.0:
            break
        if abs(fb) <= schranke:
            return ebene
        if (fb > 0.0) != (fa > 0.0):
            return eingegrenzt(a, fa, b, fb)
        if fb == fa:
            break
        a, fa, b = b, fb, b - fb * (b - a) / (fb - fa)
        fb, ebene = abweichung(b)

    # Eingrenzen, nach beiden Seiten.
    fa = abweichung(mitte)[0]
    zuletzt = {1.0: (mitte, fa), -1.0: (mitte, fa)}
    for weite in NEIGUNGSSCHRITTE:
        for seite in (1.0, -1.0):
            b = mitte + seite * math.radians(weite)
            fb, ebene = abweichung(b)
            if ebene is None:
                continue
            if abs(fb) <= schranke:
                return ebene
            x, fx = zuletzt[seite]
            if (fb > 0.0) != (fx > 0.0):
                return eingegrenzt(x, fx, b, fb)
            zuletzt[seite] = (b, fb)
    return KEINE


#: Wie die Ebene unter Gebrauchslast gefunden wird -- bei schiefer Biegung.
SUCHE_DER_EBENE = (
    "Gesucht wird die Ebene, die N, M_y und M_z zugleich trägt. Zu einer "
    "festen Zugrichtung n ist es dieselbe Aufgabe wie bei der Platte: zwei "
    "geschachtelte Halbierungen finden ε_0 und κ, mit denen N und das Moment "
    "um die Nulllinie stimmen. Übrig bleibt das Moment entlang der Nulllinie; "
    "die Zugrichtung wird gedreht, bis auch es stimmt – bei einem "
    "symmetrischen Querschnitt steht sie senkrecht zum Moment, bei einem "
    "unsymmetrischen nicht. Nachgewiesen wird das Ergebnis: die Probe, dass "
    "die Ebene die Einwirkung erzeugt.")

#: Dasselbe, einachsig.
EINACHSIG = ("Einachsig bleibt die Nulllinie waagrecht, und M_z zählt nicht – wie "
             "in der Tragsicherheit.")


def protokoll_ebene(p: Protokoll, werte: Zwischenwerte, ebene: Gebrauchsebene,
                     einachsig: bool) -> None:
    """Die gefundene Ebene und ihre Probe."""
    eps = werte.dehnung("eps_0", r"\varepsilon_0", ebene.eps_m, stellen=4)
    kappa = werte.kruemmung("kappa", r"\kappa", ebene.chi)
    p.gleichung(rf"\psi = {fest(math.degrees(ebene.psi), 1)}^\circ \qquad {angabe(eps)}"
                rf" \qquad {angabe(kappa)}",
                titel="Gefundene Dehnungsebene: Zugrichtung, Dehnung im Schwerpunkt, "
                      "Krümmung")
    probe = [werte.kraft("N_int", "N_{int}", ebene.N),
             werte.moment("M_y_int", "M_{y,int}", ebene.M_y)]
    if not einachsig:
        probe.append(werte.moment("M_z_int", "M_{z,int}", ebene.M_z))
    p.gleichung(r" \qquad ".join(rf"{angabe(w)} \;\checkmark" for w in probe),
                titel="Probe: die Ebene erzeugt die Einwirkung")
