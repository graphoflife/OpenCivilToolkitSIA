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
(:class:`~opencivil.nachweis.querschnittsloeser.Faserloeser`, mit Illinois).
Uebrig bleibt das Moment entlang der Nulllinie, und ψ wird gedreht, bis auch
es stimmt (:func:`gebrauchsebene`): der Sekante nach, dann Illinois, und wo
die Sekante wegliefe, mit wachsenden Schritten nach beiden Seiten
eingegrenzt (:func:`neigung_suchen`). Bei einem symmetrischen Querschnitt
trifft schon die Neigung, die zum Moment gehoert. Einachsig bleibt die
Nulllinie waagrecht, und M_z zaehlt nicht -- wie in der Tragsicherheit.

Dieselbe Suche dreht die Nulllinie in der Spannung-Dehnung-Analyse des
gezeichneten Querschnitts (:class:`~opencivil.spannungsanalyse.schnitt.KippendeNulllinie`);
dort ist je Neigung eine andere Aufgabe zu loesen, gesucht wird ψ gleich.

WAS ES KOSTET:
Jede Neigung ist eine ganze Suche ueber die Fasern. Halbiert brauchte die
schiefe Biegung am Unterzug des Beispiels zwanzig Neigungen zu je 85 ms;
mit Sekante und Illinois sind es eine Handvoll zu je wenigen ms.

EINHEITEN:
SI-Basis.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Callable, Optional, Tuple, TypeVar

from opencivil.core.latex import angabe, fest
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.suche import ILLINOIS, illinois
from opencivil.nachweis.querschnittsloeser import Faserloeser, probenschranken, wie_gesucht
from opencivil.querschnitt.interaktion import Querschnitt, Richtung
from opencivil.querschnitt.zugseite import Zugseite

#: Wie weit sich die Neigung ψ der Ebene unter Gebrauchslast von der
#: entfernen darf, die bei Symmetrie gaelte -- nach jeder Seite, in Grad.
#: Weiter als 90° laege die Gegenrichtung, und die gehoert zur negativen
#: Kruemmung.
NEIGUNGSSCHRITTE = (2.0, 5.0, 10.0, 20.0, 35.0, 55.0, 75.0, 90.0)

#: Wann das Moment entlang der Nulllinie als getroffen gilt, als Teil der
#: groessten Schnittgroesse -- N mit einem Hebel von einem Meter gezaehlt.
QUER_SCHRANKE = 1e-7

#: Was eine Neigung ergibt -- die Ebene, wie der Fragende sie braucht.
E = TypeVar("E")

#: Wie oft zwischen einer Neigung mit Ebene und einer ohne halbiert wird, um
#: den Rand des Gleichgewichts zu finden -- auf ein Millionstel des Schritts.
RANDSCHRITTE = 20


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

    verfehlt: bool = False
    """
    Ob die Suche an einem Sprung haengen blieb, statt eine Ebene zu finden --
    wie :attr:`~opencivil.nachweis.querschnittsloeser.Ebene.verfehlt`.
    """


#: Wenn sich keine Ebene findet.
KEINE = Gebrauchsebene(psi=0.0, eps_m=0.0, chi=0.0, N=0.0, M_y=0.0, M_z=0.0,
                       eps_s=(), sigma_s=(), konvergiert=False)

#: Wenn die Suche ihre Ebene verfehlt -- mit dem Spannungsblock bei viel
#: Druck und wenig Moment.
VERFEHLT = replace(KEINE, verfehlt=True)


def _loeser(r: Richtung) -> Faserloeser:
    """
    Der Loeser in einer Zugrichtung -- mit Illinois, wo kein Gesetz springt.
    Die Ebene sucht er, :func:`suche_der_ebene` liest von ihm, wie.
    """
    return Faserloeser(querschnitt=r.fasern, grenzen=r.grenzen, suche=ILLINOIS)


def _bei_neigung(q: Querschnitt, psi: float, N: float, M_y: float,
                 M_z: float) -> Tuple[Gebrauchsebene, float]:
    """
    Die Ebene bei dieser Neigung, die N und das Moment in Zugrichtung traegt
    -- und was ihr am Moment entlang der Nulllinie noch fehlt. Mit
    ``M = -(n_z·M_y + n_y·M_z)`` und ``M_quer = -(n_y·M_y - n_z·M_z)``, den
    Umkehrungen von :meth:`~opencivil.querschnitt.interaktion.Richtung.momente`.
    Ohne Ebene :data:`KEINE` oder :data:`VERFEHLT`, und es fehlt ``nan``.
    """
    r = q.richtung(psi)
    n_y, n_z = r.n
    loesung = _loeser(r).loese(N_Ed=N, M_Ed=-(n_z * M_y + n_y * M_z))
    if not loesung.konvergiert:
        return (VERFEHLT if loesung.verfehlt else KEINE), math.nan
    k = r.fasern.kraefte(loesung.eps_m, loesung.chi)
    m_y, m_z = r.momente(k.N, k.M, k.M_quer)
    ebene = Gebrauchsebene(psi=r.psi, eps_m=loesung.eps_m, chi=loesung.chi, N=k.N,
                           M_y=m_y, M_z=m_z, eps_s=loesung.eps_s, sigma_s=loesung.sigma_s)
    return ebene, k.M_quer + (n_y * M_y - n_z * M_z)


def neigung_suchen(abweichung: Callable[[float], Tuple[float, Optional[E]]], mitte: float,
                   schranke: float, *, geprueft: Callable[[E], E] = lambda e: e) -> Optional[E]:
    """
    Die Neigung ψ, bei der ``abweichung`` null wird -- und was sie dort ergibt.

    ``abweichung(ψ)`` loest die Aufgabe bei dieser Neigung und gibt zurueck,
    was am Moment entlang der Nulllinie noch fehlt, mit der Ebene; ohne Ebene
    ``(nan, None)``. Gesucht wird von ``mitte`` aus: trifft schon sie, bleibt
    es bei ihr. Sonst der Sekante nach, bis die Abweichung das Vorzeichen
    wechselt, dann Illinois; was Illinois findet, geht durch ``geprueft``.
    Laeuft die Sekante weg, wird nach beiden Seiten mit wachsenden Schritten
    eingegrenzt (:data:`NEIGUNGSSCHRITTE`). ``None``, wo ``mitte`` keine Ebene
    hat oder sich keine Neigung findet.

    Hat ein Schritt keine Ebene, liegt zwischen ihm und dem letzten mit Ebene
    der Rand des Gleichgewichts -- und dort kann das Vorzeichen schon
    gewechselt haben. Darum wird der Rand gesucht (:data:`RANDSCHRITTE`) und
    an ihm gefragt; danach geht es auf dieser Seite nicht weiter. Bis
    2026-10-17 sprang die Suche ueber ihn hinweg: an der kippenden Nulllinie
    des Unterzugs im Beispiel, bei Zug links unter Zug, lag die Neigung bei
    -38°, Ebenen gab es bis -42°, und nach -35° kam der Schritt nach -55°.
    Wo jeder Schritt eine Ebene hat, aendert das nichts.
    """
    fa, ebene = abweichung(mitte)
    if ebene is None:
        return None
    if abs(fa) <= schranke:
        return ebene

    def eingegrenzt(a: float, fa: float, b: float, fb: float) -> Optional[E]:
        gefunden = illinois(abweichung, a, fa, b, fb, schranke_x=1e-12, schranke_f=schranke)
        return None if gefunden is None else geprueft(gefunden)

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
    am_rand = {1.0: False, -1.0: False}
    for weite in NEIGUNGSSCHRITTE:
        for seite in (1.0, -1.0):
            if am_rand[seite]:
                continue
            b = mitte + seite * math.radians(weite)
            fb, ebene = abweichung(b)
            if ebene is None:
                am_rand[seite] = True
                b, fb, ebene = _rand(abweichung, zuletzt[seite][0], b)
                if ebene is None:
                    continue
            if abs(fb) <= schranke:
                return ebene
            x, fx = zuletzt[seite]
            if (fb > 0.0) != (fx > 0.0):
                return eingegrenzt(x, fx, b, fb)
            zuletzt[seite] = (b, fb)
    return None


def _rand(abweichung: Callable[[float], Tuple[float, Optional[E]]], mit: float,
          ohne: float) -> Tuple[float, float, Optional[E]]:
    """
    Die letzte Neigung mit Ebene zwischen ``mit`` (hat eine) und ``ohne``
    (hat keine) -- durch Halbieren, mit ihrer Abweichung und Ebene. ``None``
    als Ebene, wo sich ausser ``mit`` selbst keine findet.
    """
    gefunden: Tuple[float, float, Optional[E]] = (mit, math.nan, None)
    for _ in range(RANDSCHRITTE):
        mitte = 0.5 * (mit + ohne)
        fm, ebene = abweichung(mitte)
        if ebene is None:
            ohne = mitte
        else:
            mit, gefunden = mitte, (mitte, fm, ebene)
    return gefunden


def gebrauchsebene(q: Querschnitt, *, N: float, M_y: float, M_z: float,
                   einachsig: bool, start: Optional[float] = None) -> Gebrauchsebene:
    """
    Die Dehnungsebene, die ``N``, ``M_y`` und ``M_z`` im Gleichgewicht haelt.

    Einachsig mit waagrechter Nulllinie, ``M_z`` zaehlt nicht. Sonst wird die
    Neigung gesucht, bei der auch das Moment entlang der Nulllinie stimmt
    (:func:`neigung_suchen`) -- von ``start`` aus oder von der, die bei
    Symmetrie gaelte; bei einem symmetrischen Querschnitt trifft schon sie.
    Eingegrenzt wird wie beim Widerstand in einer Momentenrichtung
    (:meth:`~opencivil.querschnitt.interaktion.Querschnitt.in_richtung`).
    Ohne Ebene :data:`KEINE` -- oder :data:`VERFEHLT`, wo die Suche an einem
    Sprung haengen blieb.
    """
    if einachsig:
        return _bei_neigung(q, Zugseite.aus_moment(M_y).psi, N, M_y, 0.0)[0]

    schranke = QUER_SCHRANKE * max(abs(M_y), abs(M_z), abs(N) * 1.0, 1.0)
    # Was am Ende ohne Ebene dasteht: verfehlt, sobald eine Neigung an einem
    # Sprung haengen blieb.
    ohne = KEINE

    def abweichung(psi: float):
        nonlocal ohne
        ebene, fehlt = _bei_neigung(q, psi, N, M_y, M_z)
        if not ebene.konvergiert:
            ohne = VERFEHLT if ebene.verfehlt else ohne
            return math.nan, None
        return fehlt, ebene

    def geprueft(ebene: Gebrauchsebene) -> Gebrauchsebene:
        # Auch die Neigung hat ihre Probe, an dem, was dasteht: endet die
        # Suche an einem Sprung, verfehlt die Ebene M_y oder M_z um mehr, als
        # Neigung und Ebene verfehlen duerfen.
        r = q.richtung(ebene.psi)
        erlaubt = schranke + probenschranken(r.fasern, r.grenzen)[1]
        if abs(ebene.M_y - M_y) <= erlaubt and abs(ebene.M_z - M_z) <= erlaubt:
            return ebene
        return VERFEHLT

    mitte = Querschnitt.neigung_fuer(M_y, M_z) if start is None else start
    gefunden = neigung_suchen(abweichung, mitte, schranke, geprueft=geprueft)
    return ohne if gefunden is None else gefunden


def suche_der_ebene(q: Querschnitt) -> str:
    """
    Wie die Ebene unter Gebrauchslast gefunden wird -- bei schiefer Biegung,
    mit der Suche, mit der :func:`_bei_neigung` an diesem Querschnitt
    wirklich sucht: der Loeser sagt sie selbst. Bis 2026-10-17 stand hier
    «zwei geschachtelte Halbierungen», auch wo mit Illinois gesucht wurde.
    """
    suche = _loeser(q.richtung(0.0)).suche
    return (
        f"Gesucht wird die Ebene, die N, M_y und M_z zugleich trägt. Zu einer "
        f"festen Zugrichtung n ist es dieselbe Aufgabe wie bei der Platte: zwei "
        f"geschachtelte Suchen finden ε_0 und κ, mit denen N und das Moment um "
        f"die Nulllinie stimmen, {wie_gesucht(suche)}. Übrig bleibt das Moment "
        f"entlang der Nulllinie; die Zugrichtung wird gedreht, bis auch es "
        f"stimmt – bei einem symmetrischen Querschnitt steht sie senkrecht zum "
        f"Moment, bei einem unsymmetrischen nicht. Nachgewiesen wird das "
        f"Ergebnis: die Probe, dass die Ebene die Einwirkung erzeugt.")

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
