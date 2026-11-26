"""
opencivil/stahlbau/querschnitt.py -- ein gezeichneter Querschnitt aus Baustahl.

VERANTWORTUNG:
Was die Kennzahlen eines Stahlquerschnitts
(:mod:`opencivil.nachweis.qa_stahl_kennzahlen`) aus der Zeichnung brauchen,
ohne Rechenwerk und ohne Herleitung, in mm und N/mm²:

* die Teile, nach Baustahl und Dicke in Gruppen -- je Gruppe eine
  Fliessgrenze (:class:`Gruppe`);
* je Beanspruchung -- Druck oder Biegung zu einer Seite -- den Zustand jedes
  Blechs, plastisch ``α`` und elastisch ``ψ``, und daraus seine Klasse
  (:mod:`opencivil.stahlbau.klasse`);
* die plastische Nulllinie und das plastische Moment, die elastischen Werte
  und den wirksamen Querschnitt der Klasse 4.

DIE TEILE:
Ein Polygon zaehlt in seiner Gruppe mit +1 und in der seines Elternteils mit
-1: so nimmt eine Aussparung den Stahl darum weg, und ein Polygon aus anderem
Stahl ersetzt ihn dort. Die Dicke eines Profils ist die seines dicksten
Blechs, die einer frei gezeichneten Flaeche ihre kleinste Breite -- die ihrer
konvexen Huelle. Nach Vorgabe, nicht nachgeschlagen: das ganze Profil
rechnet so mit der Fliessgrenze seines dicksten Blechs, und eine freie
Flaeche nie mit einer zu grossen. Ueber 40 mm gelten die Werte der rechten
Spalte von Tabelle 1, auch ueber 100 mm, wo die Tabelle endet.

HAUPTACHSEN:
y und z gelten als Hauptachsen, wie im Balkensystem
(:data:`~opencivil.stabwerk.stabquerschnitt.KOPPLUNG`): die Nulllinie einer
Biegung um y liegt waagrecht, plastisch wie elastisch.

FREIE FLAECHEN:
Wie ein frei gezeichnetes Blech gehalten ist, weiss das Werkzeug nicht. Wo
eines gedrueckt ist, rechnet der Querschnitt darum hoechstens elastisch, in
Klasse 3, ohne sein Beulen zu pruefen (Plan vom 2026-11-25, Punkt 7).

DIE WIRKSAME BREITE (4.5.3), IN EINEM SCHRITT:
Je Blech der Klasse 4 faellt ein Streifen weg, so dick wie das Blech, aus
der gedrueckten Zone ``b_c`` seiner theoretischen Breite, wie Tabelle 10 ihn
legt: beim beidseitig gestuetzten in der Mitte, sodass je ``b_eff/2`` an
den Enden der Zone bleiben; beim einseitig gestuetzten am freien Ende,
sodass ``b_eff`` am gehaltenen bleibt -- Tabelle 10 zeigt das nur fuer
gleichmaessigen Druck (nach Vorgabe, nicht nachgeschlagen). ``ψ`` kommt aus
den Spannungen des Bruttoquerschnitts; dass die Nulllinie des wirksamen
sich verschiebt, aendert die Streifen nicht mehr (nach Vorgabe, nicht
nachgeschlagen). Ein Rundrohr hat keine mitwirkende Breite: in Klasse 4
rechnet das Werkzeug es nicht.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.material.basis import Baustoff
from opencivil.querschnitt import geometrie as geo
from opencivil.querschnitt.analyse import Flaechenteil
from opencivil.querschnitt.geometrie import Punkt
from opencivil.stahlbau import klasse as kl
from opencivil.stahlprofile.bleche import Blech, Halterung, bleche

#: Ab welcher Dicke die rechte Spalte von Tabelle 1 gilt, in mm.
DICK_AB = 40.0

#: Wie nah an einer Nulllinie ein Punkt auf ihr liegt, in mm.
TOLERANZ = 1e-3

#: Eine Richtung, zur gezogenen Seite hin -- ``None`` bei gleichmaessigem Druck.
Normale = Optional[Tuple[float, float]]


@dataclass(frozen=True)
class Gruppe:
    """Ein Baustahl in einer Dicke: alle Teile, die mit derselben Fliessgrenze rechnen."""

    stoff: Baustoff
    dick: bool

    @property
    def name(self) -> str:
        return f"{self.stoff.name}, t > 40 mm" if self.dick else self.stoff.name

    def kennwert(self, kurz: str) -> str:
        """Der Kennwert in dieser Dicke: ``f_y`` oder ``f_y_dick``."""
        return f"{kurz}_dick" if self.dick else kurz


@dataclass(frozen=True)
class Teil:
    """Ein Polygon aus Baustahl, mit seiner Dicke -- ein Profil mit seinen Blechen."""

    flaeche: Flaechenteil
    gruppe: int
    dicke: float
    netto: float
    """Seine Flaeche in mm², ohne was in ihm liegt."""

    bleche: Tuple[Blech, ...]

    @property
    def name(self) -> str:
        f = self.flaeche
        return f"{f.name} ({f.herkunft})" if f.herkunft else f.name


@dataclass(frozen=True)
class Stueck:
    """Ein Polygon mit Vorzeichen in einer Gruppe -- siehe Dateikopf."""

    gruppe: int
    vorzeichen: float
    punkte: Tuple[Punkt, ...]


@dataclass(frozen=True)
class Blechzustand:
    """
    Wie ein Blech unter einer Beanspruchung gedrueckt ist und in welche Klasse
    es damit faellt -- gemessen ueber ``c``: ``alpha`` der plastisch
    gedrueckte Anteil, ``psi`` das Verhaeltnis der elastischen Spannungen
    (``None``: elastisch nicht gedrueckt), ``frei`` ob der freie Rand der
    staerker gedrueckte ist.
    """

    teil: Teil
    blech: Blech
    alpha: float
    psi: Optional[float]
    frei: bool
    grenzen: kl.Grenzen
    klasse: int

    @property
    def name(self) -> str:
        return f"{self.teil.flaeche.name}: {self.blech.name}"

    @property
    def schlankheit(self) -> float:
        return self.blech.c / self.blech.t


@dataclass(frozen=True)
class Wirksam:
    """Die mitwirkende Breite eines Blechs der Klasse 4 -- in mm, ueber seine theoretische Breite."""

    zustand: Blechzustand
    psi: float
    k: float
    lambda_p: float
    rho: float
    b_c: float
    streifen: Optional[Tuple[Punkt, ...]]
    """Was wegfaellt -- ``None``, wo das ganze Blech mitwirkt."""

    @property
    def b_eff(self) -> float:
        return self.rho * self.b_c


@dataclass(frozen=True)
class Elastisch:
    """Ein Querschnitt elastisch, quer zu einer Richtung ``n``: in mm und mm⁴."""

    v: float
    """``n·S`` -- wo die Nulllinie bei ``N = 0`` liegt, durch den Schwerpunkt ``S``."""

    I: float
    A: float
    abstaende: Tuple[float, ...]
    """Je Gruppe der weiteste Punkt ihres Stahls von der Nulllinie -- 0 ohne Stahl."""

    schwerpunkt: Punkt

    def moment(self, f: Sequence[float]) -> Tuple[float, int]:
        """
        Das Moment, bei dem die erste Faser die Spannung ihrer Gruppe erreicht,
        in N·mm, und die Gruppe, in der sie liegt: ``min f_g I/z_g``.
        """
        return min((f[g] * self.I / z, g) for g, z in enumerate(self.abstaende) if z > 0.0)


def kleinste_breite(punkte: Sequence[Punkt]) -> float:
    """Die kleinste Breite eines Polygons -- die seiner konvexen Huelle, quer zu einer ihrer Kanten."""
    huelle = _huelle(punkte)
    beste = math.inf
    for a, b in zip(huelle, huelle[1:] + huelle[:1]):
        laenge = math.dist(a, b)
        if laenge > 0.0:
            beste = min(beste, max(abs(_kreuz(a, b, q)) / laenge for q in huelle))
    return beste


def _kreuz(o: Punkt, a: Punkt, b: Punkt) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _huelle(punkte: Sequence[Punkt]) -> List[Punkt]:
    """Die konvexe Huelle, linksherum (Andrew)."""
    sortiert = sorted(set(punkte))
    unten: List[Punkt] = []
    oben: List[Punkt] = []
    for liste, folge in ((unten, sortiert), (oben, sortiert[::-1])):
        for q in folge:
            while len(liste) >= 2 and _kreuz(liste[-2], liste[-1], q) <= 0.0:
                liste.pop()
            liste.append(q)
    return unten[:-1] + oben[:-1]


def _auf(n: Tuple[float, float], p: Punkt) -> float:
    return n[0] * p[0] + n[1] * p[1]


def _null(d: float) -> float:
    """Eine Entfernung von der Nulllinie -- null, wo sie auf ihr liegt."""
    return 0.0 if abs(d) <= TOLERANZ else d


def anteil(d_1: float, d_2: float) -> float:
    """Der gedrueckte Anteil einer Strecke, deren Enden ``d`` von der Nulllinie liegen -- gedrueckt, wo ``d < 0``."""
    d_1, d_2 = _null(d_1), _null(d_2)
    if d_1 >= 0.0 and d_2 >= 0.0:
        return 0.0
    if d_1 <= 0.0 and d_2 <= 0.0:
        return 1.0
    return -min(d_1, d_2) / abs(d_1 - d_2)


def verhaeltnis(d_1: float, d_2: float) -> Optional[float]:
    """``ψ`` ueber eine Strecke: die Spannung am anderen Ende durch die am staerker gedrueckten -- ``None`` ohne Druck."""
    d_1, d_2 = _null(d_1), _null(d_2)
    if min(d_1, d_2) >= 0.0:
        return None
    return max(d_1, d_2) / min(d_1, d_2)


class Stahlquerschnitt:
    """Die Polygone einer Querschnittsanalyse aus Baustahl -- siehe Dateikopf."""

    def __init__(self, flaechen: Sequence[Flaechenteil],
                 eltern: Sequence[Optional[int]]) -> None:
        self.gruppen: List[Gruppe] = []
        self.teile: List[Teil] = []
        self.stuecke: List[Stueck] = []
        gruppe_von: Dict[int, int] = {}
        for i, f in enumerate(flaechen):
            if f.stoff is None:
                continue
            platten = tuple(bleche(f.profil)) if f.profil is not None else ()
            dicke = max(b.t for b in platten) if platten else kleinste_breite(f.punkte)
            gruppe = Gruppe(f.stoff, dicke > DICK_AB)
            if gruppe not in self.gruppen:
                self.gruppen.append(gruppe)
            gruppe_von[i] = self.gruppen.index(gruppe)
            innen = sum(geo.flaechenwerte(flaechen[k].punkte).A
                        for k, e in enumerate(eltern) if e == i)
            self.teile.append(Teil(f, gruppe_von[i], dicke,
                                   geo.flaechenwerte(f.punkte).A - innen, platten))
        for i, f in enumerate(flaechen):
            eigene = gruppe_von.get(i)
            fremde = gruppe_von.get(eltern[i]) if eltern[i] is not None else None
            if eigene == fremde:
                continue
            if eigene is not None:
                self.stuecke.append(Stueck(eigene, 1.0, tuple(f.punkte)))
            if fremde is not None:
                self.stuecke.append(Stueck(fremde, -1.0, tuple(f.punkte)))

    # -- Was gezeichnet ist -------------------------------------------------------

    @property
    def profile(self) -> List[Teil]:
        return [t for t in self.teile if t.flaeche.profil is not None]

    @property
    def freie(self) -> List[Teil]:
        """Die frei gezeichneten Flaechen aus Baustahl -- siehe Dateikopf."""
        return [t for t in self.teile if t.flaeche.profil is None]

    def flaechen(self) -> List[float]:
        """Je Gruppe ihre Flaeche in mm²."""
        summe = [0.0] * len(self.gruppen)
        for s in self.stuecke:
            summe[s.gruppe] += s.vorzeichen * geo.flaechenwerte(s.punkte).A
        return summe

    # -- Plastisch -----------------------------------------------------------------

    def nulllinie(self, n: Tuple[float, float], f: Sequence[float]) -> float:
        """
        Die plastische Nulllinie ``n·p = v`` bei ``N = 0``: so viel Kraft
        gezogen wie gedrueckt, je Gruppe mit ``f``. Halbiert, bis sie auf
        1e-9 mm genau liegt.
        """
        ziel = 0.5 * sum(fg * a for fg, a in zip(f, self.flaechen()))
        werte = [_auf(n, p) for s in self.stuecke for p in s.punkte]
        unten, oben = min(werte), max(werte)
        while oben - unten > 1e-9:
            mitte = 0.5 * (unten + oben)
            gezogen = sum(f[s.gruppe] * s.vorzeichen * geo.jenseits(s.punkte, n, mitte)[0]
                          for s in self.stuecke)
            unten, oben = (mitte, oben) if gezogen > ziel else (unten, mitte)
        return 0.5 * (unten + oben)

    def plastisch(self, n: Tuple[float, float], v: float) -> List[float]:
        """
        Je Gruppe ``∫|n·p - v| dA`` in mm³ -- ihr Anteil am plastischen
        Widerstandsmoment um die Nulllinie ``v``.
        """
        summe = [0.0] * len(self.gruppen)
        for s in self.stuecke:
            w = geo.flaechenwerte(s.punkte)
            a, sy, sz = geo.jenseits(s.punkte, n, v)
            jenseits = n[0] * sy + n[1] * sz - v * a
            ganz = w.A * (_auf(n, (w.y_S, w.z_S)) - v)
            summe[s.gruppe] += s.vorzeichen * (2.0 * jenseits - ganz)
        return summe

    # -- Elastisch -----------------------------------------------------------------

    def elastisch(self, n: Tuple[float, float],
                  abzug: Sequence[Tuple[int, Tuple[Punkt, ...]]] = ()) -> Elastisch:
        """
        Der Querschnitt elastisch, ohne die Streifen in ``abzug`` (je Gruppe
        und Umriss) -- alle Staehle haben dasselbe ``E``.
        """
        teile = [(s.vorzeichen, geo.flaechenwerte(s.punkte)) for s in self.stuecke]
        teile += [(-1.0, geo.flaechenwerte(punkte)) for _, punkte in abzug]
        w = geo.summe(teile)
        v = _auf(n, (w.y_S, w.z_S))
        abstaende = [0.0] * len(self.gruppen)
        for s in self.stuecke:
            if s.vorzeichen > 0.0:
                weiteste = max(abs(_auf(n, p) - v) for p in s.punkte)
                abstaende[s.gruppe] = max(abstaende[s.gruppe], weiteste)
        I = n[0] * n[0] * w.I_z + n[1] * n[1] * w.I_y + 2.0 * n[0] * n[1] * w.I_yz
        return Elastisch(v=v, I=I, A=w.A, abstaende=tuple(abstaende), schwerpunkt=(w.y_S, w.z_S))

    # -- Klassen -------------------------------------------------------------------

    def zustaende(self, n: Normale, eps: Sequence[float], v_pl: float = 0.0,
                  v_el: float = 0.0) -> List[Blechzustand]:
        """
        Jedes Blech jedes Profils unter Druck (``n`` ``None``) oder unter
        Biegung mit den Nulllinien ``v_pl`` und ``v_el`` -- mit ``ε`` je Gruppe.
        """
        zustaende = []
        for teil in self.profile:
            for blech in teil.bleche:
                alpha, psi, frei = self._zustand(blech, n, v_pl, v_el)
                grenzen = kl.grenzen(blech.halterung, eps[teil.gruppe], alpha, psi, frei)
                zustaende.append(Blechzustand(teil, blech, alpha, psi, frei, grenzen,
                                              grenzen.klasse(blech.c / blech.t)))
        return zustaende

    @staticmethod
    def _zustand(blech: Blech, n: Normale, v_pl: float,
                 v_el: float) -> Tuple[float, Optional[float], bool]:
        if n is None:
            return 1.0, 1.0, False
        if blech.halterung is Halterung.ROHR:
            # Ein Rohr ist gedrueckt, sobald ein Teil von ihm auf der
            # gedrueckten Seite liegt; seine Grenze haengt an nichts sonst.
            innen = _auf(n, blech.von) - blech.c / 2.0
            return (1.0 if _null(innen - v_pl) < 0.0 else 0.0,
                    1.0 if _null(innen - v_el) < 0.0 else None, False)
        a, b = blech.lichte_enden
        frei = blech.halterung is Halterung.EINSEITIG and \
            _auf(n, blech.bis) < _auf(n, blech.von) - TOLERANZ
        return (anteil(_auf(n, a) - v_pl, _auf(n, b) - v_pl),
                verhaeltnis(_auf(n, a) - v_el, _auf(n, b) - v_el), frei)

    def freie_gedrueckt(self, n: Normale, v_pl: float = 0.0,
                        v_el: float = 0.0) -> List[Teil]:
        """Die freien Flaechen, die plastisch oder elastisch gedrueckt sind -- siehe Dateikopf."""
        if n is None:
            return self.freie
        grenze = max(v_pl, v_el) - TOLERANZ
        return [t for t in self.freie if min(_auf(n, p) for p in t.flaeche.punkte) < grenze]

    # -- Klasse 4 ------------------------------------------------------------------

    def wirksam(self, zustand: Blechzustand, n: Normale, eps: float,
                v_el: float = 0.0) -> Wirksam:
        """
        Die mitwirkende Breite eines Blechs der Klasse 4 -- kein Rundrohr --,
        ueber seine theoretische Breite ``b``, mit ``ψ`` ueber dieselbe. Siehe
        Dateikopf.
        """
        blech = zustand.blech
        b = blech.b
        if n is None:
            d_0 = d_1 = -1.0
        else:
            d_0, d_1 = _null(_auf(n, blech.von) - v_el), _null(_auf(n, blech.bis) - v_el)
        psi = verhaeltnis(d_0, d_1)
        if psi is None:
            raise ValueError(f"{zustand.name} ist nicht gedrückt.")
        # Die gedrueckte Zone [von, bis], ab dem Anfang der theoretischen Breite.
        if d_0 < 0.0 and d_1 < 0.0:
            von, bis = 0.0, b
        elif d_0 < 0.0:
            von, bis = 0.0, b * d_0 / (d_0 - d_1)
        else:
            von, bis = b * d_0 / (d_0 - d_1), b
        frei = blech.halterung is Halterung.EINSEITIG and zustand.frei
        k = kl.beulwert(blech.halterung, psi, frei)
        lambda_p = kl.plattenschlankheit(b, blech.t, eps, k)
        rho = kl.abminderung_kasten(lambda_p, psi) if blech.kasten else kl.abminderung(lambda_p)
        b_eff = rho * (bis - von)
        if rho >= 1.0:
            streifen = None
        elif blech.halterung is Halterung.EINSEITIG:
            streifen = blech.streifen(von + b_eff, bis)
        else:
            streifen = blech.streifen(von + b_eff / 2.0, bis - b_eff / 2.0)
        return Wirksam(zustand, psi, k, lambda_p, rho, bis - von, streifen)
