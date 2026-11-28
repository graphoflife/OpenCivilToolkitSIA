"""
opencivil/durchstanzen/weg.py -- ein Schnitt um die Stütze durch verschiedene Dicken.

VERANTWORTUNG:
Liegt ein Plattenbereich neben der Stütze, ohne sie zu umschliessen
(:mod:`.bereiche`), kann ein Schnitt massgebend sein, der durch verschiedene
Dicken läuft -- etwa durch einen dünneren Bereich, wo d kleiner ist.
SIA 262:2025, 4.3.6.2.7 verlangt, alle möglichen Schnitte zu rechnen; es
gilt der schwächste. Hier steht, was an jedem Punkt um die Stütze gilt
(:class:`Karte`), wie der schwächste dieser Schnitte gesucht wird
(:class:`Netz`), was er ergibt (:class:`Wegschnitt`) und wie die Herleitung
ihn zeigt (:func:`schreiben`).

DER WIDERSTAND::

    V_Rd,c,W = τ_cd · k_e · Σ k_r,i · d_v,i · u_red,i

über die Stellen i mit eigenem d -- die Platte und jeder Bereich, durch den
der Schnitt läuft: (58) je Stelle, k_r,i nach (59) mit ihrem d und dem ψ der
Stütze (:mod:`.stufen`), k_e des ganzen Schnitts.

NACH VORGABE, NICHT NACHGESCHLAGEN -- die Norm regelt diese Schnitte nicht
im Einzelnen:

- Der Schnitt hält an jeder Stelle mindestens 0.5·d_v ihres d von der Stütze,
  wie der Schnitt um sie, und von jedem Bereich, der auf der Druckseite
  weiter vorsteht als die Stelle selbst -- wie ausserhalb eines Stützenkopfs
  (Figur 24a).
- In einem Bereich, der auf der Gegenseite dicker ist, gilt sein d nur, wo er
  mindestens 0.5·d_v über die Stelle hinausreicht; sonst endete der Riss
  jenseits seiner Stufe (:meth:`.bereiche.Dicken.wirksam`).
- Von der Stütze zählt nur, was höchstens 1.5·d_v ihres d von ihren Ecken
  liegt (Figur 23a), wie um sie; an den Ecken der Bereiche zählt alles.
- Gesucht wird auf :data:`RICHTUNGEN` Strahlen von der Stützenachse, bis
  :data:`REICHWEITE`·d über die Stütze und die Bereiche um sie hinaus. Wo auf
  einem Strahl eine neue Stelle beginnt, liegt ein Knoten, und ein Schnitt
  verbindet je einen Knoten jedes Strahls zu einem Ring. Massgebend ist der
  Ring mit der kleinsten Summe V_Rd,c + q_d·A, der mit der kleinsten Reserve
  (:meth:`Netz.ring`). Gesucht wird mit k_e der Stütze; den gefundenen Ring
  wertet :mod:`.schnitt` genau aus, mit seinem k_e.
- Ein Ring, der überall mit demselben d rechnet, ist kein Schnitt durch
  verschiedene Dicken: er ist der Schnitt um die Stütze oder an einer Stufe,
  nur gröber gerechnet, und fällt weg.

EINHEITEN:
SI-Basis; Kräfte in N.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import Eingaben
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.durchstanzen import herleitung
from opencivil.durchstanzen.bereiche import Dicken, Plattenbereich
from opencivil.durchstanzen.herleitung import Index
from opencivil.durchstanzen.pruefung import KeRegel, Schnittlast, beiwert_k_r
from opencivil.durchstanzen.schnitt import (
    ECKENBEREICH, Halbebene, Nachweisschnitt, Punkt, Schatten, Strecke, Stuetzenflaeche,
    auswerten, kandidat_ring,
)
from opencivil.querschnitt.geometrie import (
    TOLERANZ, abstand_zum_rand, abstand_zur_strecke, flaeche, lage, naechster_auf_strecke,
)

#: In wie viele Richtungen die Strahlen von der Stützenachse gehen -- je 5°.
RICHTUNGEN = 72

#: Wie weit die Suche über die Stütze und die Bereiche um sie hinaus reicht, in d der Platte.
REICHWEITE = 4.0

#: Wie fein ein Strahl abgetastet wird, in Teilen des kleinsten d.
SCHRITT = 0.1

#: Wie genau eine Grenze auf einem Strahl oder einer Strecke feststeht, in m.
GENAUIGKEIT = 1e-4

#: Wie fein die Strecken des gefundenen Schnitts abgetastet werden, bevor sie
#: an den Grenzen der Stellen geteilt werden, in m.
TEILUNG = 5e-3

#: Wie der Schnitt in Sätzen heisst: «am Schnitt durch verschiedene Dicken».
NAME = "durch verschiedene Dicken"

#: Wie seine Werte heissen: u_{0,W}, V_{Rd,c,W}.
INDEX = Index("W")

#: Wo die Norm verlangt, alle Schnitte zu rechnen.
REFERENZ = "SIA 262:2025, 4.3.6.2.7"

Stelle = Optional[Plattenbereich]
"""Wessen d an einem Punkt gilt -- ``None``: das der Platte."""

Schluessel = Tuple[Stelle, bool]
"""Was an einem Punkt gilt: wessen d und ob ein Schnitt dort zählt."""

Box = Tuple[float, float, float, float]


# ===========================================================================
# Was an einem Punkt gilt
# ===========================================================================


class Karte:
    """
    Was an einem Punkt um die Stütze gilt: wessen d, ob ein Schnitt dort liegen
    darf und ob er dort zählt -- siehe Dateikopf. Aussparungen zählen mit den
    Schatten, die der Schnitt um die Stütze von ihnen hat (Figur 23d); die
    genaue Auswertung misst sie am gefundenen Schnitt neu.
    """

    def __init__(self, dicken: Dicken, stuetze: Stuetzenflaeche, *, raender: Sequence[Halbebene],
                 aussparungen: Sequence[Sequence[Punkt]], schatten: Sequence[Schatten]) -> None:
        self.dicken = dicken
        self.stuetze = stuetze
        self.achse = stuetze.achse
        self.raender = tuple(raender)
        self.aussparungen = tuple((_box(a), tuple(a)) for a in aussparungen)
        self.schatten = tuple(schatten)
        # Der kleinste zuerst: der erste, in dem ein Punkt liegt, ist der innerste.
        self.bereiche = tuple(sorted(dicken.bereiche, key=lambda b: abs(flaeche(b.ecken))))
        self.boxen: Dict[str, Box] = {b.name: _box(b.ecken) for b in dicken.bereiche}
        self.druck: Dict[str, float] = {b.name: dicken.versatz(b).druck for b in dicken.bereiche}
        kern = list(stuetze.kern)
        self.seiten: Tuple[Tuple[Punkt, Punkt], ...] = (
            () if len(kern) == 1 else ((kern[0], kern[1]),) if len(kern) == 2
            else tuple(zip(kern, kern[1:] + kern[:1])))

    def in_der_platte(self, p: Punkt) -> bool:
        return all(h.enthaelt(p) for h in self.raender)

    def innerster(self, p: Punkt) -> Stelle:
        """Der innerste Bereich, in dem ``p`` liegt -- auf seinem Rand zählt als darin."""
        for b in self.bereiche:
            if _in_box(p, self.boxen[b.name]) and lage(p, b.ecken) >= 0:
                return b
        return None

    def wo(self, p: Punkt, innerster: Stelle) -> Stelle:
        """Wessen d an ``p`` gilt: ein Bereich auf der Gegenseite nur, wo er d/2 weiter reicht."""
        return self.dicken.wirksam(
            innerster, lambda d, b: abstand_zum_rand(p, b.ecken) >= d / 2.0 - TOLERANZ)

    def abstand_zur_stuetze(self, p: Punkt) -> float:
        kern = self.stuetze.kern
        if len(kern) >= 3 and lage(p, kern) >= 0:
            return 0.0
        kante = (math.dist(p, kern[0]) if not self.seiten
                 else min(abstand_zur_strecke(p, a, b) for a, b in self.seiten))
        return max(0.0, kante - self.stuetze.radius)

    def neben_ecke(self, p: Punkt, d: float) -> bool:
        """Ob ``p`` höchstens 1.5·d von einer Ecke der Stütze liegt, an ihrer nächsten Seite."""
        if not self.seiten:
            return True
        a, b = min(self.seiten, key=lambda s: abstand_zur_strecke(p, *s))
        q = naechster_auf_strecke(p, a, b)
        grenze = ECKENBEREICH * d + TOLERANZ
        return math.dist(a, q) <= grenze or math.dist(q, b) <= grenze

    def schluessel(self, p: Punkt) -> Optional[Schluessel]:
        """
        Was an ``p`` gilt -- oder nichts, wo ein Schnitt nicht liegen darf.
        Ausserhalb der Platte darf er überall liegen und zählt nicht.
        """
        if not self.in_der_platte(p):
            return None, False
        innen = self.innerster(p)
        wo = self.wo(p, innen)
        d = self.dicken.d_von(wo)
        halb = d / 2.0 - TOLERANZ
        if self.abstand_zur_stuetze(p) < halb:
            return None
        druck = 0.0 if innen is None else self.druck[innen.name]
        for b in self.bereiche:
            if (self.druck[b.name] > druck + TOLERANZ
                    and _abstand_zur_box(p, self.boxen[b.name]) < halb
                    and lage(p, b.ecken) < 0 and abstand_zum_rand(p, b.ecken) < halb):
                return None
        zaehlt = (self.neben_ecke(p, d)
                  and not any(s.enthaelt(math.atan2(p[1] - self.achse[1], p[0] - self.achse[0]))
                              for s in self.schatten)
                  and not any(_in_box(p, box) and lage(p, a) >= 0 for box, a in self.aussparungen))
        return wo, zaehlt

    def stueckschluessel(self, p: Punkt) -> Tuple[Stelle, bool]:
        """
        Was ein Stück des gefundenen Schnitts an ``p`` braucht: wessen d und ob
        die Regel der Ecken es zählen lässt. Platte, Aussparungen und Schatten
        prüft die Auswertung selbst (:func:`.schnitt.auswerten`).
        """
        wo = self.wo(p, self.innerster(p))
        return wo, self.neben_ecke(p, self.dicken.d_von(wo))


def _box(punkte: Sequence[Punkt]) -> Box:
    xs, ys = [p[0] for p in punkte], [p[1] for p in punkte]
    return min(xs), min(ys), max(xs), max(ys)


def _in_box(p: Punkt, box: Box) -> bool:
    return (box[0] - TOLERANZ <= p[0] <= box[2] + TOLERANZ
            and box[1] - TOLERANZ <= p[1] <= box[3] + TOLERANZ)


def _abstand_zur_box(p: Punkt, box: Box) -> float:
    """Wie weit ``p`` vom Rechteck ``box`` liegt -- höchstens so weit wie vom Polygon darin."""
    dx = max(box[0] - p[0], 0.0, p[0] - box[2])
    dy = max(box[1] - p[1], 0.0, p[1] - box[3])
    return math.hypot(dx, dy)


def _gleich(a: Optional[Schluessel], b: Optional[Schluessel]) -> bool:
    return a is not None and b is not None and a[0] is b[0] and a[1] == b[1]


def reichweite(dicken: Dicken, um: Sequence[Plattenbereich], stuetze: Stuetzenflaeche) -> float:
    """
    Wie weit die Suche von der Stützenachse reicht, in m: über die Stütze und
    die Bereiche um sie hinaus :data:`REICHWEITE`·d der Platte.
    """
    achse = stuetze.achse
    kern = [*stuetze.umriss(), *(q for b in um for q in b.ecken)]
    return max(math.dist(achse, q) for q in kern) + REICHWEITE * dicken.d


def neben(dicken: Dicken, um: Sequence[Plattenbereich], stuetze: Stuetzenflaeche
          ) -> Tuple[Tuple[Plattenbereich, ...], Tuple[Plattenbereich, ...]]:
    """
    Die Bereiche, die die Stütze nicht umschliessen: die nahen, durch die ein
    Schnitt um sie laufen kann, und die fernen, ausser :func:`reichweite`.
    """
    weit = reichweite(dicken, um, stuetze)
    ausser = [b for b in dicken.bereiche if b not in um]
    nah = tuple(b for b in ausser if abstand_zum_rand(stuetze.achse, b.ecken) <= weit)
    return nah, tuple(b for b in ausser if b not in nah)


# ===========================================================================
# Das Netz und die Suche
# ===========================================================================


@dataclass(frozen=True)
class Knoten:
    """Ein Punkt auf einem Strahl, wo eine neue Stelle beginnt."""

    p: Punkt
    wo: Stelle
    d: float
    zaehlt: bool


@dataclass(frozen=True)
class Wegstelle:
    """Wie viel vom Schnitt an einer Stelle zählt, und ihr d -- in m."""

    wo: Stelle
    d: float
    u_red: float


@dataclass(frozen=True)
class Wegschnitt:
    """
    Der gefundene Schnitt, genau ausgewertet: was an ihm von der Last abhängt
    und je Stelle, was von ihm zählt -- die Platte zuerst, dann die Bereiche
    nach ihrem Namen.
    """

    last: Schnittlast
    stellen: Tuple[Wegstelle, ...]

    #: Wo er liegt, für Sätze: «der Schnitt durch verschiedene Dicken».
    wo = NAME

    def V_Rd_c(self, psi: float, k_g: float, tau_cd: float) -> float:
        """Der Widerstand, still -- siehe Dateikopf."""
        return tau_cd * self.last.k_e * sum(beiwert_k_r(psi, s.d, k_g) * s.d * s.u_red
                                            for s in self.stellen)


class Netz:
    """
    Die Knoten auf den Strahlen um die Stütze und je Paar benachbarter Knoten
    Länge und Fläche -- alles, was nicht von ψ abhängt. :meth:`ring` sucht den
    schwächsten Ring bei einem ψ, :meth:`schnitt` wertet ihn aus; beide gelten
    für Nachweis und Kennzahl.

    ``um`` sind die Bereiche, die die Stütze umschliessen, ``schatten`` die der
    Aussparungen am Schnitt um sie. ``d_v`` ist das der Stütze: mit ihm misst
    die Auswertung, welche Aussparungen den Schnitt mindern (Figur 23d). ``k_e``
    ist das am Schnitt um die Stütze -- mit ihm wird gesucht.
    """

    def __init__(self, dicken: Dicken, um: Sequence[Plattenbereich], stuetze: Stuetzenflaeche,
                 *, raender: Sequence[Halbebene], aussparungen: Sequence[Sequence[Punkt]],
                 schatten: Sequence[Schatten], d_v: float, k_e: float, regel: KeRegel,
                 V_d: float, q_d: float) -> None:
        karte = Karte(dicken, stuetze, raender=raender, aussparungen=aussparungen,
                      schatten=schatten)
        self.karte = karte
        self.d_v, self.k_e, self.regel, self.V_d, self.q_d = d_v, k_e, regel, V_d, q_d
        weit = reichweite(dicken, um, stuetze)
        d_min = min([dicken.d, *(dicken.d_von(b) for b in dicken.bereiche)])
        schritt = SCHRITT * d_min
        strahlen = [_strahl(karte, 2.0 * math.pi * k / RICHTUNGEN, weit, schritt)
                    for k in range(RICHTUNGEN)]
        # Gesucht wird ab dem Strahl mit den wenigsten Knoten: von jedem eine Suche.
        erster = min(range(RICHTUNGEN), key=lambda k: len(strahlen[k]))
        self.strahlen: Tuple[Tuple[Knoten, ...], ...] = tuple(
            tuple(strahlen[(erster + k) % RICHTUNGEN]) for k in range(RICHTUNGEN))
        self.kanten = tuple(self._kanten(k) for k in range(RICHTUNGEN))
        self._ausgewertet: Dict[Tuple[int, ...], Optional[Wegschnitt]] = {}

    @property
    def vollstaendig(self) -> bool:
        """Ob jeder Strahl einen Knoten hat -- sonst schliesst kein Ring."""
        return all(self.strahlen)

    @property
    def warum_keiner(self) -> str:
        """Warum :meth:`schnitt` keinen Schnitt gibt -- für die Herleitung."""
        if not self.vollstaendig:
            return ("Um die Stütze schliesst kein Schnitt durch verschiedene Dicken: auf einem "
                    "Strahl von ihr hält kein Punkt den Abstand zur Stütze und zu dickeren Teilen.")
        return ("Der schwächste Schnitt um die Stütze rechnet überall mit demselben d: er läuft "
                "nicht durch verschiedene Dicken, und die Schnitte oben decken ihn.")

    def _kanten(self, k: int) -> Tuple[Tuple[Tuple[float, float], ...], ...]:
        """Je Knoten auf Strahl ``k`` und auf dem nächsten: Länge und Fläche in der Platte."""
        a_ = self.strahlen[k]
        b_ = self.strahlen[(k + 1) % RICHTUNGEN]
        achse, raender = self.karte.achse, self.karte.raender
        return tuple(tuple((math.dist(a.p, b.p), _dreieck(achse, a.p, b.p, raender)) for b in b_)
                     for a in a_)

    def ring(self, psi: float, k_g: float, tau_cd: float) -> Optional[Tuple[int, ...]]:
        """
        Je Strahl der Knoten des schwächsten Rings bei ``psi`` -- der mit der
        kleinsten Summe V_Rd,c + q_d·A, gesucht mit k_e der Stütze. Bei
        gleicher Summe gilt der kürzere. Nichts, wo kein Ring schliesst.
        """
        if not self.vollstaendig:
            return None
        faktor = tau_cd * self.k_e / 2.0
        gewichte = [[beiwert_k_r(psi, n.d, k_g) * n.d if n.zaehlt else 0.0 for n in strahl]
                    for strahl in self.strahlen]
        # Fast nichts kostet ein Stück, das nicht zählt; der Zuschlag macht den Ring kurz.
        kurz = 1e-6 * tau_cd * self.karte.dicken.d
        bester: Optional[Tuple[float, Tuple[int, ...]]] = None
        for s in range(len(self.strahlen[0])):
            kosten = [math.inf] * len(self.strahlen[0])
            kosten[s] = 0.0
            zurueck: List[List[int]] = []
            for k in range(RICHTUNGEN - 1):
                kosten, von = self._schritt(k, kosten, gewichte, faktor, kurz)
                zurueck.append(von)
            # Zum Schluss zurück zum Anfang.
            g_s, letzte = gewichte[0][s], self.kanten[RICHTUNGEN - 1]
            summe, i = min(
                (kosten[i] + faktor * l * (gewichte[-1][i] + g_s) + self.q_d * A + kurz * l, i)
                for i, (l, A) in ((i, letzte[i][s]) for i in range(len(kosten))))
            if bester is not None and summe >= bester[0]:
                continue
            weg = [i]
            for von in reversed(zurueck):
                weg.append(von[weg[-1]])
            bester = (summe, tuple(reversed(weg)))
        return None if bester is None or math.isinf(bester[0]) else bester[1]

    def _schritt(self, k: int, kosten: List[float], gewichte: List[List[float]], faktor: float,
                 kurz: float) -> Tuple[List[float], List[int]]:
        """Von Strahl ``k`` zum nächsten: je Knoten dort die kleinste Summe und woher sie kommt."""
        kanten, g_a, g_b = self.kanten[k], gewichte[k], gewichte[k + 1]
        neu, von = [math.inf] * len(g_b), [0] * len(g_b)
        for i, c in enumerate(kosten):
            if math.isinf(c):
                continue
            for j, (l, A) in enumerate(kanten[i]):
                x = c + faktor * l * (g_a[i] + g_b[j]) + self.q_d * A + kurz * l
                if x < neu[j]:
                    neu[j], von[j] = x, i
        return neu, von

    def schnitt(self, psi: float, k_g: float, tau_cd: float) -> Optional[Wegschnitt]:
        """
        Der schwächste Schnitt durch verschiedene Dicken bei ``psi``, genau
        ausgewertet -- nichts, wo kein Ring schliesst oder der schwächste
        überall mit demselben d rechnet (Dateikopf).
        """
        ring = self.ring(psi, k_g, tau_cd)
        if ring is None:
            return None
        if ring not in self._ausgewertet:
            self._ausgewertet[ring] = self._auswerten(ring)
        return self._ausgewertet[ring]

    def _auswerten(self, ring: Tuple[int, ...]) -> Optional[Wegschnitt]:
        punkte = [self.strahlen[k][i].p for k, i in enumerate(ring)]
        stuecke: List[Strecke] = []
        stellen: List[Stelle] = []
        for a, b in zip(punkte, punkte[1:] + punkte[:1]):
            for (p, q), (wo, zaehlt) in _geteilt(self.karte, a, b):
                stuecke.append(Strecke(p, q) if zaehlt else Strecke(p, q, 0.0, 0.0))
                stellen.append(wo)
        kandidat = kandidat_ring(f"Schnitt {NAME}", stuecke, self.karte.raender)
        a = auswerten(kandidat, d_v=self.d_v, achse=self.karte.achse,
                      aussparungen=[x for _, x in self.karte.aussparungen])
        je: Dict[Optional[str], float] = {}
        nach_name: Dict[Optional[str], Stelle] = {}
        for wo, laenge in zip(stellen, a.je_stueck):
            schluessel = None if wo is None else wo.name
            je[schluessel] = je.get(schluessel, 0.0) + laenge
            nach_name[schluessel] = wo
        dicken = self.karte.dicken
        gezaehlt = [Wegstelle(nach_name[n], dicken.d_von(nach_name[n]), je[n])
                    for n in sorted(je, key=lambda n: (n is not None, n or "")) if je[n] > 1e-6]
        if len({round(s.d, 9) for s in gezaehlt}) < 2:
            return None
        last = Schnittlast(Nachweisschnitt(a, (a,)), self.regel, self.V_d, self.q_d)
        return Wegschnitt(last, tuple(gezaehlt))


def _strahl(karte: Karte, winkel: float, weit: float, schritt: float) -> List[Knoten]:
    """Die Knoten auf einem Strahl: je der erste Punkt, wo eine neue Stelle beginnt."""
    ax, ay = karte.achse
    c, s = math.cos(winkel), math.sin(winkel)

    def bei(t: float) -> Punkt:
        return ax + t * c, ay + t * s

    knoten: List[Knoten] = []
    n = max(1, math.ceil(weit / schritt))
    vorher = karte.schluessel(bei(0.0))
    t_vorher = 0.0
    for i in range(1, n + 1):
        t = weit * i / n
        jetzt = karte.schluessel(bei(t))
        if jetzt is not None and not _gleich(jetzt, vorher):
            unten, oben = t_vorher, t
            while oben - unten > GENAUIGKEIT:
                mitte = (unten + oben) / 2.0
                if _gleich(karte.schluessel(bei(mitte)), jetzt):
                    oben = mitte
                else:
                    unten = mitte
            wo, zaehlt = jetzt
            knoten.append(Knoten(bei(oben), wo, karte.dicken.d_von(wo), zaehlt))
        vorher, t_vorher = jetzt, t
    return knoten


def _dreieck(achse: Punkt, a: Punkt, b: Punkt, raender: Sequence[Halbebene]) -> float:
    """Die Fläche zwischen der Achse und der Strecke a–b, soweit sie in der Platte liegt."""
    punkte = [achse, a, b]
    for h in raender:
        neu: List[Punkt] = []
        for i, p in enumerate(punkte):
            q = punkte[(i + 1) % len(punkte)]
            fp = h.n[0] * p[0] + h.n[1] * p[1] - h.c
            fq = h.n[0] * q[0] + h.n[1] * q[1] - h.c
            if fp <= 0.0:
                neu.append(p)
            if (fp < 0.0 < fq) or (fq < 0.0 < fp):
                t = fp / (fp - fq)
                neu.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
        punkte = neu
        if len(punkte) < 3:
            return 0.0
    return abs(flaeche(punkte))


def _geteilt(karte: Karte, a: Punkt, b: Punkt
             ) -> List[Tuple[Tuple[Punkt, Punkt], Tuple[Stelle, bool]]]:
    """
    Die Strecke a–b, geteilt, wo sich ändert, wessen d gilt oder ob die Regel
    der Ecken zählen lässt -- je Teil mit dem, was in ihm gilt.
    """
    laenge = math.dist(a, b)
    n = max(1, math.ceil(laenge / TEILUNG))

    def bei(t: float) -> Punkt:
        return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t

    teile = []
    t_anfang, t_vorher = 0.0, 0.0
    anfang = karte.stueckschluessel(a)
    for i in range(1, n + 1):
        t = i / n
        jetzt = karte.stueckschluessel(bei(t))
        if _gleich(jetzt, anfang):
            t_vorher = t
            continue
        unten, oben = t_vorher, t
        while (oben - unten) * laenge > GENAUIGKEIT:
            mitte = (unten + oben) / 2.0
            if _gleich(karte.stueckschluessel(bei(mitte)), anfang):
                unten = mitte
            else:
                oben = mitte
        teile.append(((bei(t_anfang), bei(oben)), anfang))
        t_anfang, t_vorher, anfang = oben, t, jetzt
    teile.append(((bei(t_anfang), b), anfang))
    return [x for x in teile if math.dist(*x[0]) > 1e-9]


# ===========================================================================
# Herleitung
# ===========================================================================


def schreiben(p: Protokoll, w: Zwischenwerte, e: Eingaben, ws: Wegschnitt, *, d: Wert,
              h_B: Dict[str, Wert], psi: Wert, k_g: Wert, tau_cd: Wert, k_e_stuetze: Wert,
              last: str, V_d: Optional[Wert] = None) -> Tuple[Wert, Wert]:
    """
    Der Schnitt durch verschiedene Dicken mit denselben Schritten wie um die
    Stütze, dazu je Stelle ihr Teil des Widerstands: zurück kommen die
    Querkraft in ihm und sein Widerstand. ``d`` ist das d der Platte, ``h_B``
    sind die Dicken der Bereiche, ``V_d`` die Stützenkraft, wo es nicht die
    eingegebene ist (die Kennzahl).
    """
    p.titel(f"Schnitt {NAME}", ebene=3)
    p.erklaerung(
        "Neben der Stütze liegt ein Bereich mit eigener Dicke: ein Schnitt um sie kann durch "
        "verschiedene Dicken laufen. Hier steht der schwächste. Jedes Stück zählt mit k_r·d_v "
        "seiner Stelle, und der Schnitt hält 0.5·d_v Abstand zur Stütze und zu Teilen, die auf "
        "der Druckseite weiter vorstehen. Die Norm verlangt, alle möglichen Schnitte zu rechnen "
        "(4.3.6.2.7), regelt diese aber nicht im Einzelnen – nach Vorgabe, nicht nachgeschlagen.")
    a = ws.last.auswertung
    u_0 = herleitung.rand(p, w, a, ix=INDEX, titel=f"Schnitt {NAME}, soweit er in der Platte liegt",
                          referenz=REFERENZ)
    herleitung.abzuege(
        p, w, a, u_0, ix=INDEX,
        ecken_text="Von einer Seite der Stütze zählt nur, was höchstens 1.5·d_v von ihren Ecken "
                   "liegt, mit d_v der Stelle – wie um die Stütze.",
        ecken_referenz="SIA 262:2025, 4.3.6.2.3, Figur 23a")
    k_e = herleitung.k_e(p, w, ws.last, ix=INDEX, an_der_stuetze=k_e_stuetze)
    teile = {f"V_{i}": _stelle_schreiben(p, w, e, s, d=d, h_B=h_B, psi=psi, k_g=k_g,
                                         tau_cd=tau_cd, k_e=k_e)
             for i, s in enumerate(ws.stellen)}
    V_Rd_c = w.kraft(INDEX.name("V_Rd_c"), INDEX.symbol("V", "Rd", "c"),
                     sum(t.groesse.si for t in teile.values()),
                     f"Durchstanzwiderstand am Schnitt {NAME}")
    p.formel(V_Rd_c, " + ".join(f"@{n}" for n in teile), teile,
             titel=f"Durchstanzwiderstand am Schnitt {NAME}: die Summe der Stellen",
             referenz=REFERENZ, name="Durchstanzwiderstand durch verschiedene Dicken")
    V = herleitung.querkraft(p, w, e, ws.last, ix=INDEX, V_d=V_d,
                             titel_last=f"{last} innerhalb des Schnitts {NAME}",
                             titel=f"Querkraft im Schnitt {NAME}")
    return V, V_Rd_c


def _stelle_schreiben(p: Protokoll, w: Zwischenwerte, e: Eingaben, s: Wegstelle, *, d: Wert,
                      h_B: Dict[str, Wert], psi: Wert, k_g: Wert, tau_cd: Wert,
                      k_e: Wert) -> Wert:
    """Was der Schnitt an einer Stelle trägt: (58) mit ihrem d und ihrem Teil des Schnitts."""
    ix = Index(f"W,{'Pl' if s.wo is None else s.wo.name}")
    wo = "in der Platte" if s.wo is None else f"im {s.wo.titel}"
    d_s = d if s.wo is None else herleitung.d_im_bereich(
        p, w, e, h_B, d, s.wo, ix.name("d"), ix.symbol("d"), titel="Statische Höhe",
        referenz=REFERENZ)
    u_red = w.laenge(ix.name("u_red"), ix.symbol("u", "red"), s.u_red, stellen=0)
    p.wert(u_red, titel=f"Was vom Schnitt {wo} zählt", referenz=REFERENZ)
    u = herleitung.wirksam(p, w, k_e, u_red, ix=ix, titel=f"Wirksamer Umfang {wo}")
    k_r = herleitung.k_r(p, w, psi, d_s, k_g, ix=ix, titel=f"Beiwert k_r {wo}, mit dem d dort")
    V = w.kraft(ix.name("V_Rd_c"), ix.symbol("V", "Rd", "c"),
                k_r.groesse.si * tau_cd.groesse.si * d_s.groesse.si * u.groesse.si,
                f"Durchstanzwiderstand {wo}")
    p.formel(V, r"@k_r \cdot @tau_cd \cdot @d_v \cdot @u",
             {"k_r": k_r, "tau_cd": tau_cd, "d_v": d_s, "u": u},
             titel=f"Durchstanzwiderstand {wo}", referenz="SIA 262:2025, 4.3.6.3.1, (58)",
             name="Durchstanzwiderstand ohne Durchstanzbewehrung")
    return V
