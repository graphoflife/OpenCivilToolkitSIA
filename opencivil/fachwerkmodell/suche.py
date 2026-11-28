"""
opencivil/fachwerkmodell/suche.py -- das leichteste Fachwerk, Runde um Runde.

VERANTWORTUNG:
Die Suche des Verfahrens Ground Structure nach He, Gilbert & Song (2019),
Abschnitt 3: eine Optimierung über einen Teil der möglichen Stäbe
(:mod:`~opencivil.fachwerkmodell.optimierung`), dann die Stäbe dazu, die
das Fachwerk leichter machten -- bis keiner mehr fehlt (:func:`runde`).
Dann ist es das Fachwerk, das die Optimierung über alle möglichen Stäbe
fände. Jede Runde gibt ein Fachwerk im Gleichgewicht (:func:`nachbearbeiten`);
wer die Suche anhält, hat das der letzten.

DIE RUNDEN:
- In der ersten die kurzen Stäbe, höchstens 1.5 h lang: je Knoten seine
  Nachbarn im Raster, auch schräg (nach Vorgabe, nicht nachgeschlagen).
- Nach jeder Optimierung je Stab ausserhalb seine Dehnung im Feld der
  virtuellen Verschiebungen. Liegt sie über w_Z oder unter −w_D, verletzt
  er die Bedingung, und das Fachwerk würde mit ihm leichter. Die am
  stärksten verletzen, kommen dazu -- so viele, wie Gl. (7) sagt, mit
  α = β = 0.05.
- Fertig, wenn keiner mehr verletzt.

ZUG NUR WAAGRECHT UND SENKRECHT:
Ein Schalter des Verfahrens (:data:`ZUG_ACHSPARALLEL`): dann tragen nur
waagrechte und senkrechte Stäbe Zug, wie eine Bewehrung in x und y, und
ein geneigter nur Druck -- in der Optimierung hat er keine Kraft q⁺, und
seine Dehnung verletzt die Bedingung nur, wo sie unter −w_D liegt. Geht so
kein Fachwerk auf, bleibt ein Rest, und die Nachrechnung nennt die Last,
die offen bleibt (:func:`~opencivil.fachwerkmodell.werk.offen_meldungen`).

DER ZUSTAND:
Zwischen zwei Runden: welche Stäbe im Modell sind, zu welchem Modell
(:class:`Suchzustand`). Die Seite hält ihn und schickt ihn mit der nächsten
Anfrage zurück. Die Grundstruktur bleibt hier im Speicher
(:func:`_grundstruktur`): sie folgt aus dem Modell und der Rasterweite.

DIE NACHBEARBEITUNG:
Ein Innere-Punkte-Verfahren endet innen: jeder Stab trägt ein wenig, und wo
mehrere Fachwerke gleich leicht sind, trägt jedes einen Teil. Darum fallen
die Stäbe unter N_min der grössten Kraft weg, und die Optimierung sucht das
Gleichgewicht ohne sie neu -- und wieder, bis keiner mehr wegfällt. Geht
es ohne sie nicht auf, versucht sie es mit der halben Schwelle: was dann
bleibt, braucht das Gleichgewicht (:func:`_ohne_duenne`). Zuletzt werden
zwei Stäbe in einer Flucht einer, wo zwischen ihnen nur ein Knoten ohne
Last und Lager liegt.

DER ABDRUCK:
Woran ein gefundenes Fachwerk sein Modell erkennt (:func:`abdruck`): die
ganze Scheibe mit Lagern und Lasten, die drei Zahlen des Verfahrens und
sein Schalter.
Ändert sich eines, gehört das Fachwerk zu einem früheren Stand.
"""

from __future__ import annotations

import hashlib
import math
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.einheiten import EINHEITSLOS, M, PROZENT
from opencivil.core.vorgaben import Feld, Gruppe
from opencivil.decke import geometrie as geo
from opencivil.decke.geometrie import Punkt
from opencivil.fachwerkmodell.grundstruktur import HOECHSTENS_KNOTEN, Grundstruktur, grundstruktur
from opencivil.fachwerkmodell.modell import Modell
from opencivil.fachwerkmodell.optimierung import Gleichgewicht, Optimum, optimieren

#: Wo die Suche nachzulesen ist.
QUELLE = "He, Gilbert & Song (2019), Abschnitt 3, Gl. (7)"

#: Die Zahlen des Verfahrens, in der Maske eine Kachel, in der Herleitung ein Kasten.
VORGABEN = (Gruppe("Verfahren", lambda: (
    Feld("rasterweite", "h", M, "Abstand der Knoten im Raster", 2, beschriftung="Rasterweite",
         schritt=0.05, hinweis=f"feiner sucht genauer und länger – mehr als {HOECHSTENS_KNOTEN} "
                               f"Knoten sucht das Werkzeug nicht"),
    Feld("w_Z", "w_Z", EINHEITSLOS, "Gewicht des Zugs gegenüber dem Druck", 2,
         beschriftung="Zug : Druck", schritt=0.1,
         hinweis="1: beide zählen gleich – grösser: das Fachwerk meidet Zug, kleiner: Druck"),
    Feld("N_min", "N_{min}", PROZENT, "Kleinste Stabkraft, bezogen auf die grösste", 1,
         beschriftung="Kleinste Stabkraft", schritt=0.5,
         hinweis="dünnere Stäbe fallen weg, dann sucht die Optimierung das Gleichgewicht neu"),
)),)

#: Wie lang die Stäbe der ersten Runde höchstens sind, in Rasterweiten -- nach Vorgabe.
KURZ = 1.5

#: α und β aus Gl. (7): wie viele der verletzenden Stäbe je Runde dazukommen.
ALPHA = BETA = 0.05

#: Ab wann ein Stab die Bedingung verletzt: 1 + diese Zahl.
VERLETZT_AB = 1e-4

#: Das Gewicht des Drucks: die Einheit, gegen die w_Z zählt.
W_DRUCK = 1.0

#: Der Schalter des Verfahrens, der Zug nur in waagrechten und senkrechten Stäben
#: zulässt -- wie er heisst und was er bewirkt (Dateikopf).
ZUG_ACHSPARALLEL = "Zug nur waagrecht und senkrecht"
ZUG_ACHSPARALLEL_ERKLAERUNG = ("Geneigte Stäbe tragen nur Druck – den Zug nehmen waagrechte und "
                               "senkrechte Stäbe auf, wie eine Bewehrung in x und y")

#: Was vom Gleichgewicht offen bleiben darf, bezogen auf die grösste Last -- nach Vorgabe.
#: Mit derselben Grenze prüft die Nachrechnung das gefundene Fachwerk.
OFFEN_HOECHSTENS = 1e-6

#: Unter diesem Teil der grössten Kraft -- eines Stabs oder einer Last -- trägt ein Stab nichts.
NULL = 1e-9

#: Wie oft die Nachbearbeitung höchstens neu optimiert -- nach Vorgabe, nicht nachgeschlagen.
NEU_HOECHSTENS = 30


@dataclass(frozen=True)
class Einstellung:
    """Das Verfahren: seine drei Zahlen in SI und sein Schalter."""

    weite: float
    """Die Rasterweite h in m."""

    w_Z: float
    """Das Gewicht des Zugs; Druck zählt 1."""

    N_min: float
    """Die kleinste Stabkraft als Teil der grössten: 0.01 ist 1 %."""

    zug_achsparallel: bool = False
    """Ob nur waagrechte und senkrechte Stäbe Zug tragen (:data:`ZUG_ACHSPARALLEL`)."""


@dataclass(frozen=True)
class Suchzustand:
    """Was von einer Runde zur nächsten geht."""

    abdruck: str
    runde: int
    """Die Nummer der Runde, die ihn gab."""

    aktiv: Tuple[int, ...]
    """Die Stäbe im Modell der nächsten Runde, als Platz in der Grundstruktur."""


@dataclass(frozen=True)
class Fachwerk:
    """Ein Fachwerk im Gleichgewicht: Knoten in m, Stäbe von Knoten zu Knoten mit der Kraft in N, Zug positiv."""

    knoten: Tuple[Punkt, ...]
    staebe: Tuple[Tuple[int, int, float], ...]


@dataclass(frozen=True)
class Suchergebnis:
    """Das Fachwerk einer Runde und woher es kommt -- so steht es im Projekt."""

    fachwerk: Fachwerk
    abdruck: str
    runden: int
    """Die Nummer der Runde, die es gab."""

    fertig: bool
    """Ob die Suche zu Ende kam -- sonst wurde sie angehalten."""

    moeglich: int
    """Wie viele Stäbe die Grundstruktur hat."""

    im_modell: int
    """Wie viele Stäbe in dieser Runde im Modell waren."""


@dataclass(frozen=True)
class Runde:
    """Was eine Runde gibt."""

    ergebnis: Suchergebnis
    zustand: Suchzustand
    """Für die nächste -- nach der letzten ohne Bedeutung."""

    dazu: int
    """Wie viele Stäbe für die nächste dazukommen."""


def abdruck(modell: Modell, einstellung: Einstellung) -> str:
    """Siehe Dateikopf: 16 Zeichen, gleich für gleiche Eingaben -- auch in Pyodide."""
    return hashlib.sha256(repr((modell, einstellung)).encode("utf-8")).hexdigest()[:16]


def runde(modell: Modell, einstellung: Einstellung, zustand: Optional[Suchzustand]) -> Runde:
    """
    Die nächste Runde der Suche -- die erste, wenn ``zustand`` fehlt oder
    nicht zu Modell und Verfahren passt: ein anderer Abdruck, Stäbe, die es
    nicht gibt, einer doppelt. Das Modell ist geprüft; wirft
    :class:`~opencivil.fachwerkmodell.grundstruktur.ZuVieleKnoten`, wenn das
    Raster zu fein ist.
    """
    gs = _grundstruktur(modell, einstellung.weite)
    marke = abdruck(modell, einstellung)
    n = len(gs.staebe)
    if (zustand is None or zustand.abdruck != marke or len(set(zustand.aktiv)) < len(zustand.aktiv)
            or any(i >= n for i in zustand.aktiv)):
        grenze = KURZ * einstellung.weite * (1.0 + 1e-9)
        aktiv = tuple(i for i, l in enumerate(gs.laengen) if l <= grenze)
        nummer = 1
    else:
        aktiv, nummer = zustand.aktiv, zustand.runde + 1
    skala = max(map(abs, gs.last))
    opt = _optimum(gs, aktiv, einstellung, skala)
    verletzt = _verletzt(gs, aktiv, opt.u, einstellung)
    rest = n - len(aktiv)
    m_v = len(verletzt)
    if m_v >= BETA * rest:
        dazu = ALPHA * m_v
    elif m_v > ALPHA * BETA * rest:
        dazu = ALPHA * BETA * rest
    else:
        dazu = m_v
    neu = tuple(sorted(verletzt, key=verletzt.get, reverse=True)[:math.ceil(dazu)])
    ergebnis = Suchergebnis(fachwerk=nachbearbeiten(gs, aktiv, opt, einstellung, skala, not neu),
                            abdruck=marke, runden=nummer, fertig=not neu, moeglich=n,
                            im_modell=len(aktiv))
    return Runde(ergebnis=ergebnis, zustand=Suchzustand(marke, nummer, aktiv + neu), dazu=len(neu))


def ganz_suchen(modell: Modell, einstellung: Einstellung) -> Suchergebnis:
    """Runde um Runde bis zum Ende, wie die Seite sucht -- nur ohne Bild dazwischen."""
    zustand = None
    while True:
        r = runde(modell, einstellung, zustand)
        if r.ergebnis.fertig:
            return r.ergebnis
        zustand = r.zustand


def _optimum(gs: Grundstruktur, aktiv: Sequence[int], einstellung: Einstellung,
             skala: float) -> Optimum:
    """Die Optimierung über die Stäbe ``aktiv``, die Lasten bezogen auf die grösste."""
    gl = Gleichgewicht(len(gs.zeilen), [gs.spalten[i] for i in aktiv])
    return optimieren(gl, [w / skala for w in gs.last],
                      [einstellung.w_Z * gs.laengen[i] if _traegt_zug(gs, i, einstellung) else None
                       for i in aktiv],
                      [W_DRUCK * gs.laengen[i] for i in aktiv], _strafe(gs, einstellung))


def _traegt_zug(gs: Grundstruktur, i: int, einstellung: Einstellung) -> bool:
    """Ob der Stab ``i`` Zug tragen darf: jeder -- mit :data:`ZUG_ACHSPARALLEL` nur ein solcher."""
    return not einstellung.zug_achsparallel or gs.achsparallel[i]


def _strafe(gs: Grundstruktur, einstellung: Einstellung) -> float:
    """
    Was ein Rest des Gleichgewichts je Einheit kostet: tausendmal mehr, als
    die Kraft der Einheit über die Diagonale der Scheibe zu tragen kostet --
    so viel kostet kein Weg durch die Stäbe (nach Vorgabe).
    """
    xs, ys = [p[0] for p in gs.knoten], [p[1] for p in gs.knoten]
    diagonale = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    return 1000.0 * max(einstellung.w_Z, W_DRUCK) * diagonale


def _verletzt(gs: Grundstruktur, aktiv: Sequence[int], u: Sequence[float],
              einstellung: Einstellung) -> Dict[int, float]:
    """Je Stab ausserhalb, der die Bedingung verletzt, um wie viel: seine Dehnung durch die erlaubte."""
    drin = set(aktiv)
    verletzt = {}
    for i, spalte in enumerate(gs.spalten):
        if i in drin:
            continue
        dehnung = sum(w * u[k] for k, w in spalte) / gs.laengen[i]
        zug = dehnung / einstellung.w_Z if _traegt_zug(gs, i, einstellung) else -math.inf
        v = max(zug, -dehnung / W_DRUCK)
        if v > 1.0 + VERLETZT_AB:
            verletzt[i] = v
    return verletzt


def nachbearbeiten(gs: Grundstruktur, aktiv: Sequence[int], opt: Optimum, einstellung: Einstellung,
                   skala: float, gruendlich: bool) -> Fachwerk:
    """
    Das Fachwerk der Runde, wie der Dateikopf es beschreibt: ohne die
    dünnen Stäbe, im Gleichgewicht neu gesucht, und mit einem Stab statt
    zweien in einer Flucht. Nur ``gruendlich`` -- in der letzten Runde --
    wird neu gesucht, bis keiner mehr wegfällt; sonst einmal, und geht es
    ohne die dünnen nicht auf, bleiben sie: die Runden davor zeigen nur,
    wie die Suche vorankommt, und jede weitere Optimierung kostete in jeder
    Runde Zeit.
    """
    kraefte = dict(zip(aktiv, opt.q))
    if max(map(abs, opt.rest), default=0.0) <= OFFEN_HOECHSTENS:
        kraefte = _ohne_duenne(gs, kraefte, einstellung, skala, NEU_HOECHSTENS if gruendlich else 1)
    # Bezogen auf die grösste Last, die 1 ist: trägt kein Stab, bleibt keiner.
    gross = max(1.0, max(map(abs, kraefte.values()), default=0.0))
    staebe = [(*gs.staebe[i], q * skala) for i, q in kraefte.items() if abs(q) > NULL * gross]
    fest = {gs.knoten_bei(l.ort) for l in gs.modell.lager} | {gs.knoten_bei(f.ort) for f in gs.modell.lasten}
    return _gefasst(gs.knoten, _zusammengelegt(gs.knoten, staebe, fest))


def _ohne_duenne(gs: Grundstruktur, kraefte: Dict[int, float], einstellung: Einstellung,
                 skala: float, hoechstens: int) -> Dict[int, float]:
    """
    Die Kräfte je Stab ohne die dünnen: die unter der Schwelle fallen weg,
    und die Optimierung sucht das Gleichgewicht ohne sie neu -- mit N_min
    wieder von vorn, bis keiner mehr wegfällt. Geht es ohne sie nicht auf,
    gilt die halbe Schwelle. Höchstens ``hoechstens`` Mal neu gesucht.
    Beispiel: die Wandscheibe im Raster von
    0.4 m geht ohne die Stäbe unter 1 % nicht auf, ohne die unter 0.25 %
    schon -- 74 statt 89 Stäbe, gleich leicht.
    """
    schwelle = einstellung.N_min
    for _ in range(hoechstens):
        gross = max(map(abs, kraefte.values()), default=0.0)
        bleiben = [i for i, q in kraefte.items() if abs(q) >= schwelle * gross]
        if gross == 0.0 or len(bleiben) == len(kraefte):
            break
        neu = _optimum(gs, bleiben, einstellung, skala)
        if max(map(abs, neu.rest)) <= OFFEN_HOECHSTENS:
            kraefte, schwelle = dict(zip(bleiben, neu.q)), einstellung.N_min
        else:
            schwelle /= 2
    return kraefte


def _zusammengelegt(knoten: Sequence[Punkt], staebe: List[Tuple[int, int, float]],
                    fest: set) -> List[Tuple[int, int, float]]:
    """
    Zwei Stäbe in einer Flucht als einer, wo zwischen ihnen nur ein Knoten
    ohne Last und Lager liegt -- ihre Kräfte sind im Gleichgewicht gleich;
    der eine trägt ihr Mittel.
    """
    staebe = list(staebe)
    while True:
        an: Dict[int, List[int]] = {}
        for s, (a, b, _) in enumerate(staebe):
            an.setdefault(a, []).append(s)
            an.setdefault(b, []).append(s)
        paar = next(((k, s) for k, s in an.items() if len(s) == 2 and k not in fest
                     and _in_flucht(knoten, k, staebe[s[0]], staebe[s[1]])), None)
        if paar is None:
            return staebe
        k, (s1, s2) = paar
        enden = [a if a != k else b for a, b, _ in (staebe[s1], staebe[s2])]
        kraft = 0.5 * (staebe[s1][2] + staebe[s2][2])
        staebe = [x for s, x in enumerate(staebe) if s not in (s1, s2)] + [(*enden, kraft)]


def _in_flucht(knoten: Sequence[Punkt], k: int, s1: Tuple[int, int, float],
               s2: Tuple[int, int, float]) -> bool:
    """Ob zwei Stäbe an Knoten ``k`` in einer Flucht weiterlaufen."""
    p = knoten[k]
    e1, e2 = (knoten[a if a != k else b] for a, b, _ in (s1, s2))
    u = (e1[0] - p[0], e1[1] - p[1])
    v = (e2[0] - p[0], e2[1] - p[1])
    kreuz = u[0] * v[1] - u[1] * v[0]
    return u[0] * v[0] + u[1] * v[1] < 0.0 \
        and abs(kreuz) <= geo.TOLERANZ * math.hypot(*u) * math.hypot(*v)


def _gefasst(knoten: Sequence[Punkt], staebe: Sequence[Tuple[int, int, float]]) -> Fachwerk:
    """Nur die Knoten, an denen ein Stab hängt, neu gezählt; die Stäbe nach der Grösse ihrer Kraft."""
    folge = sorted(staebe, key=lambda s: -abs(s[2]))
    platz: Dict[int, int] = {}
    for a, b, _ in folge:
        for k in (a, b):
            platz.setdefault(k, len(platz))
    neu = [None] * len(platz)
    for k, p in platz.items():
        neu[p] = knoten[k]
    return Fachwerk(knoten=tuple(neu), staebe=tuple((platz[a], platz[b], q) for a, b, q in folge))


# ===========================================================================
# Die Grundstruktur im Speicher
# ===========================================================================

#: Die zuletzt gebauten Grundstrukturen, nach Modell und Rasterweite.
_GEBAUT: "OrderedDict[str, Grundstruktur]" = OrderedDict()

#: Wie viele es höchstens behält.
_PLAETZE = 2


def _grundstruktur(modell: Modell, weite: float) -> Grundstruktur:
    """Die Grundstruktur, aus dem Speicher, wenn sie zu Modell und Rasterweite schon gebaut ist."""
    marke = repr((modell, weite))
    if marke in _GEBAUT:
        _GEBAUT.move_to_end(marke)
        return _GEBAUT[marke]
    gs = grundstruktur(modell, weite)
    _GEBAUT[marke] = gs
    while len(_GEBAUT) > _PLAETZE:
        _GEBAUT.popitem(last=False)
    return gs
