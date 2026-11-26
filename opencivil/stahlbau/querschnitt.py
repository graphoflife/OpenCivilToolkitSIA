"""
opencivil/stahlbau/querschnitt.py -- ein gezeichneter Querschnitt aus Baustahl.

VERANTWORTUNG:
Was die Kennzahlen eines Stahlquerschnitts
(:mod:`opencivil.nachweis.qa_stahl_kennzahlen`) aus der Zeichnung brauchen,
ohne Rechenwerk und ohne Herleitung, in mm und N/mm²:

* die Teile, nach Baustahl und Dicke in Gruppen -- je Gruppe eine
  Fliessgrenze (:class:`Gruppe`);
* je Beanspruchung -- Druck, Biegung zu einer Seite oder ein Lastfall -- den
  Zustand jedes Blechs, plastisch ``α`` und elastisch ``ψ``, je an einer
  Nulllinie (:class:`Linie`), und daraus seine Klasse
  (:mod:`opencivil.stahlbau.klasse`);
* die plastische Nulllinie bei einer Normalkraft und die Kraefte, die ihre
  Spannungsbloecke tragen, die elastischen Werte und den wirksamen
  Querschnitt der Klasse 4.

Was ein Lastfall daraus macht, steht in :mod:`opencivil.stahlbau.widerstand`.

DIE TEILE:
Ein Polygon zaehlt in seiner Gruppe mit +1 und in der seines Elternteils mit
-1: so nimmt eine Aussparung den Stahl darum weg, und ein Polygon aus anderem
Stahl ersetzt ihn dort. Mit einem Gewicht dazwischen faellt ein Teil eines
Blechs nur anteilig weg: so mindert die Querkraft den Steg
(:meth:`Stahlquerschnitt.mit`). Die Dicke eines Profils ist die seines dicksten
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

import copy
import math
from dataclasses import dataclass
from functools import cached_property
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from opencivil.core.suche import illinois
from opencivil.material.basis import Baustoff
from opencivil.querschnitt import geometrie as geo
from opencivil.querschnitt.analyse import Flaechenteil
from opencivil.querschnitt.geometrie import Punkt
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.stahlbau import klasse as kl
from opencivil.stahlprofile.bleche import Blech, Halterung, bleche

#: Ab welcher Dicke die rechte Spalte von Tabelle 1 gilt, in mm.
DICK_AB = 40.0

#: Wie nah an einer Nulllinie ein Punkt auf ihr liegt, in mm.
TOLERANZ = 1e-3


@dataclass(frozen=True)
class Linie:
    """
    Eine Nulllinie ``n·p = v``, in mm: gezogen, wo ``n·p > v``, gedrueckt, wo
    ``n·p < v`` -- ``n`` zeigt zur gezogenen Seite. Mit ``n = (0, 0)`` liegt
    sie ausserhalb des Querschnitts: dann ist alles gedrueckt
    (:data:`DRUCK`) oder alles gezogen (:data:`ZUG`).
    """

    n: Tuple[float, float]
    v: float

    def d(self, p: Punkt) -> float:
        """Wie weit ``p`` auf der gezogenen Seite liegt -- negativ, wo es gedrueckt ist."""
        return self.n[0] * p[0] + self.n[1] * p[1] - self.v


#: Gleichmaessiger Druck und gleichmaessiger Zug -- ohne Nulllinie im Querschnitt.
DRUCK = Linie((0.0, 0.0), 1.0)
ZUG = Linie((0.0, 0.0), -1.0)


def normale(seite: Zugseite) -> Tuple[float, float]:
    """Die Richtung zur gezogenen Seite -- genau 0 oder ±1."""
    return float(round(math.cos(seite.psi))), float(round(math.sin(seite.psi)))


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
    """
    Ein Polygon mit Gewicht in einer Gruppe -- siehe Dateikopf. ``teil`` ist
    der Index des Teils, zu dem es zaehlt -- bei einer Aussparung der des
    Teils darum --, ``was`` sagt, wofuer ein Streifen weggenommen ist.
    """

    gruppe: int
    gewicht: float
    punkte: Tuple[Punkt, ...]
    teil: int
    was: str = ""

    @cached_property
    def werte(self) -> geo.Flaechenwerte:
        return geo.flaechenwerte(self.punkte)


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
    frei_plastisch: bool = False
    """Ob der freie Rand plastisch der staerker gedrueckte ist -- fuer die Grenzen mit ``α``."""

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

    n: Tuple[float, float]
    v: float
    """``n·S`` -- wo die Nulllinie bei ``N = 0`` liegt, durch den Schwerpunkt ``S``."""

    I: float
    A: float
    abstaende: Tuple[float, ...]
    """Je Gruppe der weiteste Punkt ihres Stahls von der Nulllinie -- 0 ohne Stahl."""

    schwerpunkt: Punkt

    @property
    def linie(self) -> Linie:
        """Die Nulllinie bei ``N = 0``, durch den Schwerpunkt."""
        return Linie(self.n, self.v)

    def moment(self, f: Sequence[float]) -> Tuple[float, int]:
        """
        Das Moment, bei dem die erste Faser die Spannung ihrer Gruppe erreicht,
        in N·mm, und die Gruppe, in der sie liegt: ``min f_g I/z_g``.
        """
        return min((f[g] * self.I / z, g) for g, z in enumerate(self.abstaende) if z > 0.0)


@dataclass(frozen=True)
class Block:
    """Die Kraft einer Zone eines Teils an einer plastischen Nulllinie, in N, und wo sie angreift, in mm."""

    teil: int
    was: str
    zone: str
    """«Zug» oder «Druck»."""

    F: float
    punkt: Punkt


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
        teil_von: Dict[int, int] = {}
        for i, f in enumerate(flaechen):
            if f.stoff is None:
                continue
            teil_von[i] = len(self.teile)
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
                self.stuecke.append(Stueck(eigene, 1.0, tuple(f.punkte), teil_von[i]))
            if fremde is not None:
                self.stuecke.append(Stueck(fremde, -1.0, tuple(f.punkte), teil_von[eltern[i]]))

    def mit(self, zusatz: Sequence[Stueck]) -> "Stahlquerschnitt":
        """
        Derselbe Querschnitt mit weiteren Stuecken: ein Streifen mit negativem
        Gewicht nimmt so viel Stahl weg -- ein Blech der Klasse 4 ganz, die
        Querkraft anteilig. Teile und Bleche bleiben, wie gezeichnet.
        """
        neu = copy.copy(self)
        neu.stuecke = [*self.stuecke, *zusatz]
        return neu

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
            summe[s.gruppe] += s.gewicht * s.werte.A
        return summe

    def werte(self) -> geo.Flaechenwerte:
        """Flaeche, Schwerpunkt und Traegheitsmomente des Stahls -- alle Staehle haben dasselbe ``E``."""
        return geo.summe([(s.gewicht, s.werte) for s in self.stuecke])

    # -- Plastisch -----------------------------------------------------------------

    def zugkraft(self, f: Sequence[float]) -> float:
        """Was der Querschnitt ganz gezogen traegt, in N -- ganz gedrueckt dasselbe mit Minus."""
        return sum(s.gewicht * f[s.gruppe] * s.werte.A for s in self.stuecke)

    def kraefte(self, linie: Linie, f: Sequence[float],
                bezug: Punkt) -> Tuple[float, float, float]:
        """
        Was die Spannungsbloecke an der Nulllinie tragen -- je Gruppe ``f``
        gezogen und ``-f`` gedrueckt --, als ``(N, M_y, M_z)`` in N und N·mm um
        ``bezug``: ``M_y = -∫σ (z - z_b) dA`` zieht unten, ``M_z = -∫σ (y - y_b) dA``
        links.
        """
        N = s_y = s_z = 0.0
        for s in self.stuecke:
            a, y, z = geo.jenseits(s.punkte, linie.n, linie.v)
            w = s.werte
            k = s.gewicht * f[s.gruppe]
            N += k * (2.0 * a - w.A)
            s_y += k * (2.0 * y - w.A * w.y_S)
            s_z += k * (2.0 * z - w.A * w.z_S)
        return N, -(s_z - bezug[1] * N), -(s_y - bezug[0] * N)

    def bloecke(self, linie: Linie, f: Sequence[float]) -> List["Block"]:
        """
        Je Teil -- und je weggenommenem Streifen -- die Kraft seiner gezogenen
        und seiner gedrueckten Zone an der Nulllinie, mit Angriffspunkt: die
        Probe zu :meth:`kraefte`, Teil fuer Teil.
        """
        summen: Dict[Tuple[int, str], List[float]] = {}
        for s in self.stuecke:
            a, y, z = geo.jenseits(s.punkte, linie.n, linie.v)
            w = s.werte
            k = s.gewicht * f[s.gruppe]
            summe = summen.setdefault((s.teil, s.was), [0.0] * 6)
            for i, x in enumerate((a, y, z, w.A - a, w.A * w.y_S - y, w.A * w.z_S - z)):
                summe[i] += (k if i < 3 else -k) * x
        bloecke = []
        for (teil, was), (F_z, y_z, z_z, F_d, y_d, z_d) in summen.items():
            for zone, F, y, z in (("Zug", F_z, y_z, z_z), ("Druck", F_d, y_d, z_d)):
                if abs(F) > 1e-9:
                    bloecke.append(Block(teil, was, zone, F, (y / F, z / F)))
        return bloecke

    def nulllinie(self, n: Tuple[float, float], f: Sequence[float],
                  N: float = 0.0) -> Optional[float]:
        """
        Die plastische Nulllinie ``n·p = v`` bei der Normalkraft ``N`` in N:
        so viel mehr Kraft gezogen als gedrueckt -- je Gruppe mit ``f``.
        ``None``, wo ``N`` jenseits der reinen Zug- oder Druckkraft liegt.
        Gesucht mit Illinois, bis sie auf 1e-9 mm genau liegt.
        """
        werte = [_auf(n, p) for s in self.stuecke for p in s.punkte]
        unten, oben = min(werte), max(werte)
        zug = self.zugkraft(f)
        fa, fb = zug - N, -zug - N
        if fa < 0.0 or fb > 0.0:
            return None
        if fa == 0.0 or fb == 0.0:
            return unten if fa == 0.0 else oben

        def abweichung(v: float) -> Tuple[float, float]:
            gezogen = sum(s.gewicht * f[s.gruppe] * (2.0 * geo.jenseits(s.punkte, n, v)[0]
                                                    - s.werte.A) for s in self.stuecke)
            return gezogen - N, v

        return illinois(abweichung, unten, fa, oben, fb, schranke_x=1e-9,
                        schranke_f=1e-12 * zug)

    def plastisch(self, n: Tuple[float, float], v: float) -> List[float]:
        """
        Je Gruppe ``∫|n·p - v| dA`` in mm³ -- ihr Anteil am plastischen
        Widerstandsmoment um die Nulllinie ``v``.
        """
        summe = [0.0] * len(self.gruppen)
        for s in self.stuecke:
            w = s.werte
            a, sy, sz = geo.jenseits(s.punkte, n, v)
            jenseits = n[0] * sy + n[1] * sz - v * a
            ganz = w.A * (_auf(n, (w.y_S, w.z_S)) - v)
            summe[s.gruppe] += s.gewicht * (2.0 * jenseits - ganz)
        return summe

    # -- Elastisch -----------------------------------------------------------------

    def elastisch(self, n: Tuple[float, float]) -> Elastisch:
        """Der Querschnitt elastisch, quer zu ``n`` -- alle Staehle haben dasselbe ``E``."""
        w = self.werte()
        v = _auf(n, (w.y_S, w.z_S))
        abstaende = [0.0] * len(self.gruppen)
        for t in self.teile:
            weiteste = max(abs(_auf(n, p) - v) for p in t.flaeche.punkte)
            abstaende[t.gruppe] = max(abstaende[t.gruppe], weiteste)
        I = n[0] * n[0] * w.I_z + n[1] * n[1] * w.I_y + 2.0 * n[0] * n[1] * w.I_yz
        return Elastisch(n=n, v=v, I=I, A=w.A, abstaende=tuple(abstaende),
                         schwerpunkt=(w.y_S, w.z_S))

    # -- Klassen -------------------------------------------------------------------

    def zustaende(self, pl: Linie, el: Linie, eps: Sequence[float]) -> List[Blechzustand]:
        """
        Jedes Blech jedes Profils, plastisch an der Nulllinie ``pl``,
        elastisch an ``el`` -- mit ``ε`` je Gruppe.
        """
        zustaende = []
        for teil in self.profile:
            for blech in teil.bleche:
                alpha, frei_pl = _plastisch_gedrueckt(blech, pl)
                psi, frei = _elastisch_gedrueckt(blech, el)
                grenzen = kl.grenzen(blech.halterung, eps[teil.gruppe], alpha, psi,
                                     frei_pl=frei_pl, frei_el=frei)
                zustaende.append(Blechzustand(teil, blech, alpha, psi, frei, grenzen,
                                              grenzen.klasse(blech.c / blech.t),
                                              frei_plastisch=frei_pl))
        return zustaende

    def freie_gedrueckt(self, pl: Linie, el: Linie) -> List[Teil]:
        """Die freien Flaechen, die plastisch oder elastisch gedrueckt sind -- siehe Dateikopf."""
        return [t for t in self.freie
                if min(min(pl.d(p), el.d(p)) for p in t.flaeche.punkte) < -TOLERANZ]

    # -- Klasse 4 ------------------------------------------------------------------

    def wirksamer(self, zustaende: Sequence[Blechzustand], el: Linie, eps: Sequence[float],
                  rest: Callable[[Blechzustand], float] = lambda zustand: 1.0
                  ) -> Optional[Tuple[List[Wirksam], "Stahlquerschnitt"]]:
        """
        Der wirksame Querschnitt zu diesen Zustaenden (4.5.3): die
        mitwirkenden Breiten der Bleche in Klasse 4 und der Querschnitt ohne
        ihre Streifen -- ``None`` mit einem Rundrohr darunter (siehe
        Dateikopf). ``rest`` sagt je Blech, wie viel von ihm noch zaehlt: hat
        die Querkraft schon einen Teil genommen, nimmt sein Streifen nur den
        Rest.
        """
        vierte = [z for z in zustaende if z.klasse == 4]
        if any(z.blech.halterung is Halterung.ROHR for z in vierte):
            return None
        breiten = [self.wirksam(z, el, eps[z.teil.gruppe]) for z in vierte]
        return breiten, self.mit([
            Stueck(w.zustand.teil.gruppe, -rest(w.zustand), w.streifen,
                   self.teile.index(w.zustand.teil), f"{w.zustand.blech.name}, wirksame Breite")
            for w in breiten if w.streifen])

    def wirksam(self, zustand: Blechzustand, el: Linie, eps: float) -> Wirksam:
        """
        Die mitwirkende Breite eines Blechs der Klasse 4 -- kein Rundrohr --,
        ueber seine theoretische Breite ``b``, mit ``ψ`` ueber dieselbe, an der
        elastischen Nulllinie ``el``. Siehe Dateikopf.
        """
        blech = zustand.blech
        b = blech.b
        d_0, d_1 = _null(el.d(blech.von)), _null(el.d(blech.bis))
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


def _frei(blech: Blech, linie: Linie) -> bool:
    """Ob der freie Rand eines einseitig gehaltenen Blechs an dieser Nulllinie der staerker gedrueckte ist."""
    return blech.halterung is Halterung.EINSEITIG and \
        linie.d(blech.bis) < linie.d(blech.von) - TOLERANZ


def _rohr_innen(blech: Blech, linie: Linie) -> float:
    """Wie weit der gedrueckteste Punkt eines Rundrohrs auf der gezogenen Seite liegt."""
    return linie.d(blech.von) - math.hypot(*linie.n) * blech.c / 2.0


def _plastisch_gedrueckt(blech: Blech, linie: Linie) -> Tuple[float, bool]:
    """
    ``α`` an der plastischen Nulllinie und ob der freie Rand gedrueckt ist. Ein
    Rundrohr ist gedrueckt, sobald ein Teil von ihm auf der gedrueckten Seite
    liegt; seine Grenze haengt an nichts sonst.
    """
    if blech.halterung is Halterung.ROHR:
        return (1.0 if _null(_rohr_innen(blech, linie)) < 0.0 else 0.0), False
    a, b = blech.lichte_enden
    return anteil(linie.d(a), linie.d(b)), _frei(blech, linie)


def _elastisch_gedrueckt(blech: Blech, linie: Linie) -> Tuple[Optional[float], bool]:
    """``ψ`` an der elastischen Nulllinie -- ``None``, wo nichts gedrueckt ist -- und ob der freie Rand es ist."""
    if blech.halterung is Halterung.ROHR:
        return (1.0 if _null(_rohr_innen(blech, linie)) < 0.0 else None), False
    a, b = blech.lichte_enden
    return verhaeltnis(linie.d(a), linie.d(b)), _frei(blech, linie)
