"""
opencivil/querschnitt/interaktion.py -- Bruchzustand gezeichneter Querschnitte, auch schief.

VERANTWORTUNG:
Zu einem beliebigen Querschnitt -- Polygone aus verschiedenen Werkstoffen,
Aussparungen, Staebe -- die Dehnungsebenen des Bruchzustands, die
Interaktionslinie und den Widerstand fuer eine Einwirkung (N, M_y, M_z).

DIE EBENE, SCHRAEG:
Die Zugrichtung ist ``n = (cos ψ, sin ψ)``, ein Einheitsvektor in der
Querschnittsebene. Mit dem Bezugspunkt S (dem Schwerpunkt) heisst::

    v = n · (p - S)          Abstand in Zugrichtung
    u = t · (p - S)          Lage entlang der Nulllinie, t = (-n_z, n_y)
    eps(p) = eps_m + chi · v

Fuer eine feste Neigung ψ ist das dieselbe Aufgabe wie bei der Platte: eine
Ebene mit zwei Unbekannten ueber ``v``. Darum wird der Querschnitt je ψ in
Streifen quer zu n zerlegt (:class:`Richtung`) und mit
:class:`~opencivil.querschnitt.fasern.Faserquerschnitt` integriert.

DIE STREIFEN:
Ihre Grenzen fallen auf jede Polygonecke, dazwischen wird gleichmaessig
unterteilt. Zwischen zwei Ecken aendert sich die Breite jedes Polygons linear
-- die Breite in der Streifenmitte mal die Dicke ist also exakt die Flaeche.
Gerechnet wird die Spannung in der Streifenmitte (Mittelpunktsregel). Wo ein
Polygon in einem anderen liegt, ersetzt es dieses: es zaehlt fuer seinen
Werkstoff und wird dem des umgebenden abgezogen.

DER BRUCHZUSTAND:
Jeder Werkstoff hat einen Dehnungsbereich, ueberwacht an seinen aeussersten
Punkten. Beim Beton kommt der C-Punkt dazu (vollstaendig gedrueckt: an der
Stelle ``(1 - eps_c1d/eps_c2d) · h`` vom gedrueckten Rand hoechstens
``eps_c1d``). Zusammen begrenzen diese Grenzen in ``(eps_m, chi)`` ein
konvexes Vieleck (:class:`~opencivil.querschnitt.fasern.Dehnungsgrenzen`).
Sein Rand mit ``chi >= 0`` ist der Dehnungsfaecher: vom gleichmaessigen Zug
ueber die Drehung um den gezogensten Stab, dann um den gedrueckten Rand, dann
um den C-Punkt, bis zum gleichmaessigen Druck. Bei der Rechteckplatte sind das
genau die Abschnitte 1a, 1b und 1c aus :mod:`opencivil.nachweis.dehnungsfaecher`;
hier entstehen sie fuer jede Form, ohne dass ein Abschnitt benannt wird.

DER WIDERSTAND EINER EINWIRKUNG:
Bei festem N und fester Richtung des Moments: auf dem Faecher der Neigung ψ
der Punkt mit ``N = N_Ed`` -- und ψ so, dass sein Moment in die Richtung von
``(M_y,Ed, M_z,Ed)`` zeigt. Bei einem doppelt symmetrischen Querschnitt steht
die Nulllinie dann senkrecht zum Moment; bei einem L nicht, und genau das ist
die schiefe Biegung.

VORZEICHEN (wie in der ganzen Querschnittsanalyse):
    N > 0     Zug
    M_y > 0   Zug unten      M_y = -Σ F·(z - z_S)
    M_z > 0   Zug links      M_z = -Σ F·(y - y_S)
Ein positives Moment zieht also auf der negativen Seite seiner Achse.

EINHEITEN:
SI-Basis: Meter, Quadratmeter, Pascal, Newton.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.querschnitt import geometrie as geo
from opencivil.querschnitt.fasern import (
    Dehnungsgrenze, Dehnungsgrenzen, Fasergruppe, Faserquerschnitt, Gesetz,
    Stab,
)

Punkt = Tuple[float, float]

#: Streifen ueber die Tiefe des Querschnitts in Zugrichtung, mindestens. Die
#: Grenzen fallen zusaetzlich auf jede Ecke. 200 sind dieselbe Feinheit, mit
#: der die genaue Linie der Platte rechnet.
STREIFEN = 200

#: Stuetzstellen je Abschnitt des Faechers fuer die Zeichnung.
SCHRITTE = 24

#: Stuetzstellen je Abschnitt, um die Stelle ``N = N_Ed`` einzugrenzen. Wenige
#: genuegen: innerhalb eines Abschnitts aendert sich N glatt, und das
#: Illinois-Verfahren findet die Stelle danach in wenigen Schritten.
SUCHSCHRITTE = 4

#: Hoechstzahl der Schritte jeder Suche. Erreicht wird sie nicht; sie steht
#: da, damit keine Schleife ewig laeuft.
SUCHE_HOECHSTENS = 80

#: Groesste Zugdehnung, wo kein Werkstoff eine nennt -- ein Querschnitt ganz
#: ohne Bewehrung. Beton traegt keinen Zug; die Grenze legt nur fest, wo der
#: Faecher beginnt. Derselbe Wert wie der Suchbereich des Plattenloesers.
EPS_ZUG_OHNE_GRENZE = 0.045

#: Wann zwei Richtungen des Moments als gleich gelten, im Bogenmass. Ein
#: Zehnmillionstel verschiebt den Widerstand um weniger, als je gedruckt wird.
WINKEL_SCHRANKE = 1e-7

#: Teile einer verschmierten Stablinie: alle so viele Meter ein Stueck.
LINIENSTUECK = 0.02


# ===========================================================================
# Beschreibung des Querschnitts
# ===========================================================================


@dataclass(frozen=True)
class Werkstoff:
    """Ein Werkstoff, wie die Interaktion ihn braucht: Gesetz und Grenzen."""

    name: str
    gesetz: Gesetz
    eps_min: float
    """Groesste zulaessige Stauchung, negativ."""

    eps_max: float
    """Groesste zulaessige Dehnung; ``inf`` beim Beton, der im Zug nichts traegt."""

    c_punkt: Optional[Tuple[float, float]] = None
    """``(eps_c1d, eps_c2d)`` beim Beton: die Regel fuer den ganz gedrueckten
    Querschnitt. Sonst nichts."""

    verdraengbar: bool = False
    """Ob ein Stab ihn an seiner Stelle ersetzt -- beim Beton ja."""


@dataclass(frozen=True)
class Teil:
    """Ein Polygon des Querschnitts, Punkte in Metern."""

    punkte: Tuple[Punkt, ...]
    werkstoff: Optional[int]
    """Index in die Werkstoffe; ``None`` fuer eine Aussparung."""

    eltern: Optional[int]
    """Das Polygon, in dem es liegt und das es dort ersetzt."""


@dataclass(frozen=True)
class Bewehrung:
    """Ein Stab -- oder ein Stueck einer verschmierten Stablinie."""

    lage: Punkt
    flaeche: float
    werkstoff: int
    verdraengt: Optional[int] = None
    """Der Werkstoff, in dem der Stab liegt und den er dort ersetzt."""

    grenzpunkte: Tuple[Punkt, ...] = ()
    """Wo seine Dehnungsgrenze ueberwacht wird. Leer: an der Stablage. Ein
    Stueck einer Linie meldet die Linienenden, damit die Grenze am Ende der
    Linie gilt und nicht erst in der Mitte ihres letzten Stuecks."""


def linie_als_bewehrung(
    von: Punkt, bis: Punkt, flaeche: float, werkstoff: int,
    verdraengt: Optional[int],
) -> List[Bewehrung]:
    """
    Eine verschmierte Stablinie als Folge kurzer Stuecke.

    Die Dehnung aendert sich entlang der Linie linear; jedes Stueck sitzt in
    der Mitte seines Abschnitts (Mittelpunktsregel) und traegt seinen Anteil
    der Flaeche. Die Grenze gilt an beiden Linienenden.
    """
    laenge = math.hypot(bis[0] - von[0], bis[1] - von[1])
    stuecke = max(10, int(math.ceil(laenge / LINIENSTUECK)))
    return [
        Bewehrung(
            lage=(von[0] + (bis[0] - von[0]) * (k + 0.5) / stuecke,
                  von[1] + (bis[1] - von[1]) * (k + 0.5) / stuecke),
            flaeche=flaeche / stuecke, werkstoff=werkstoff, verdraengt=verdraengt,
            grenzpunkte=(von, bis))
        for k in range(stuecke)
    ]


# ===========================================================================
# Ergebnisse
# ===========================================================================


@dataclass(frozen=True)
class Bruchpunkt:
    """Eine Dehnungsebene des Faechers und was sie erzeugt."""

    psi: float
    """Neigung der Zugrichtung, im Bogenmass."""

    eps_m: float
    """Dehnung im Bezugspunkt."""

    chi: float
    """Kruemmung in Zugrichtung, 1/m, nie negativ."""

    N: float
    M_y: float
    M_z: float

    @property
    def zugrichtung(self) -> Punkt:
        return (math.cos(self.psi), math.sin(self.psi))

    @property
    def moment(self) -> float:
        """Betrag des Moments."""
        return math.hypot(self.M_y, self.M_z)


@dataclass(frozen=True)
class Kraftanteil:
    """Was ein Werkstoff oder ein Stab zum Bruchzustand beitraegt."""

    name: str
    N: float
    y: float
    """Angriffspunkt, absolut; bei N = 0 der Bezugspunkt."""

    z: float
    eps: Optional[float] = None
    """Dehnung -- nur bei einem Stab, beim Beton haengt sie am Ort."""

    sigma: Optional[float] = None


# ===========================================================================
# Je Neigung: Fasern und Grenzen
# ===========================================================================


@dataclass
class Richtung:
    """Der Querschnitt fuer eine Neigung ψ der Zugrichtung, fertig zum Integrieren."""

    psi: float
    n: Punkt
    t: Punkt
    fasern: Faserquerschnitt
    grenzen: Dehnungsgrenzen
    gruppen_werkstoff: Tuple[int, ...]
    """Je Fasergruppe ihr Werkstoff -- fuer die Aufschluesselung."""

    beton: Optional[Tuple[float, float]]
    """Kleinstes und groesstes v des Betons -- fuer x und d."""

    staebe_v: Tuple[float, ...]
    """Je Bewehrung ihr v."""

    def momente(self, N: float, M: float, M_quer: float) -> Tuple[float, float]:
        """
        Aus ``Σ F·v`` und ``Σ F·u`` die Momente um die Achsen.

        Mit ``z - z_S = v·n_z + u·n_y`` und ``y - y_S = v·n_y - u·n_z``::

            M_y = -(n_z · Σ F·v + n_y · Σ F·u)
            M_z = -(n_y · Σ F·v - n_z · Σ F·u)
        """
        n_y, n_z = self.n
        return -(n_z * M + n_y * M_quer), -(n_y * M - n_z * M_quer)

    def punkt(self, eps_m: float, chi: float) -> Bruchpunkt:
        k = self.fasern.kraefte(eps_m, chi)
        M_y, M_z = self.momente(k.N, k.M, k.M_quer)
        return Bruchpunkt(psi=self.psi, eps_m=eps_m, chi=chi, N=k.N, M_y=M_y, M_z=M_z)


# ===========================================================================
# Nullstellensuche
# ===========================================================================


def illinois(f, a: float, fa: float, b: float, fb: float, *,
             schranke_x: float, schranke_f: float):
    """
    Eine Nullstelle von ``f`` zwischen ``a`` und ``b``, die verschiedene
    Vorzeichen haben -- Regula falsi mit der Illinois-Abwandlung.

    Bleibt immer eingegrenzt wie eine Halbierung, konvergiert aber auf glatten
    Stuecken fast so schnell wie das Sekantenverfahren. Die Abwandlung halbiert
    den Wert am Ende, das zweimal hintereinander stehen bleibt; sonst
    kroeche die Regula falsi an einer gekruemmten Funktion nur von einer Seite
    heran. ``f`` gibt ``(Wert, Beigabe)`` zurueck; zurueck kommt die Beigabe
    der besten Stelle.
    """
    beste = None
    for _ in range(SUCHE_HOECHSTENS):
        c = b - fb * (b - a) / (fb - fa)
        fc, beigabe = f(c)
        if beste is None or abs(fc) < beste[0]:
            beste = (abs(fc), beigabe)
        if abs(fc) <= schranke_f or abs(b - a) <= schranke_x:
            break
        if (fc > 0) != (fb > 0):
            a, fa = b, fb
        else:
            fa = fa / 2.0
        b, fb = c, fc
    return beste[1]


# ===========================================================================
# Der Querschnitt
# ===========================================================================


class Querschnitt:
    """
    Ein gezeichneter Querschnitt im Bruchzustand.

    ``bezug`` ist der Punkt, auf den sich N und die Momente beziehen -- in der
    Querschnittsanalyse der Schwerpunkt des Bruttoquerschnitts.
    """

    def __init__(
        self, *, werkstoffe: Sequence[Werkstoff], teile: Sequence[Teil],
        bewehrung: Sequence[Bewehrung], bezug: Punkt, streifen: int = STREIFEN,
    ) -> None:
        if not teile:
            raise ValueError("Ein Querschnitt ohne Fläche hat keinen Widerstand.")
        self.werkstoffe = tuple(werkstoffe)
        self.teile = tuple(teile)
        self.bewehrung = tuple(bewehrung)
        self.bezug = bezug
        self.streifen = streifen
        self._richtungen: Dict[float, Richtung] = {}

    # -- Je Neigung ---------------------------------------------------------

    def richtung(self, psi: float) -> Richtung:
        """Fasern und Grenzen fuer diese Neigung -- gerechnet einmal je ψ."""
        psi = math.remainder(psi, 2.0 * math.pi)
        schluessel = round(psi, 12)
        gespeichert = self._richtungen.get(schluessel)
        if gespeichert is None:
            gespeichert = self._richtungen[schluessel] = self._zerlegen(psi)
        return gespeichert

    def _zerlegen(self, psi: float) -> Richtung:
        n = (math.cos(psi), math.sin(psi))
        t = (-n[1], n[0])
        sy, sz = self.bezug
        v_von = lambda p: n[0] * (p[0] - sy) + n[1] * (p[1] - sz)
        n_s = n[0] * sy + n[1] * sz  # n·S: die Gerade v = c ist n·p = c + n·S
        t_s = t[0] * sy + t[1] * sz

        # -- Streifen: Grenzen auf jeder Ecke, dazwischen gleichmaessig ------
        ecken = sorted({v_von(p) for teil in self.teile for p in teil.punkte})
        tiefe = ecken[-1] - ecken[0]
        hoechstens = tiefe / self.streifen
        mitten: List[float] = []
        dicken: List[float] = []
        for a, b in zip(ecken, ecken[1:]):
            if b - a <= geo.TOLERANZ * 1e-3:
                continue
            k = max(1, int(math.ceil((b - a) / hoechstens - 1e-9)))
            d = (b - a) / k
            for i in range(k):
                mitten.append(a + (i + 0.5) * d)
                dicken.append(d)

        # -- Je Werkstoff Breite und Lage entlang der Nulllinie --------------
        gewichte: List[Tuple[int, Dict[int, float]]] = []
        for i, teil in enumerate(self.teile):
            eigen = teil.werkstoff
            fremd = (self.teile[teil.eltern].werkstoff
                     if teil.eltern is not None else None)
            g: Dict[int, float] = {}
            if eigen is not None:
                g[eigen] = g.get(eigen, 0.0) + 1.0
            if fremd is not None:
                g[fremd] = g.get(fremd, 0.0) - 1.0
            g = {w: x for w, x in g.items() if x != 0.0}
            if g:
                gewichte.append((i, g))

        sammlung: Dict[int, Tuple[List[float], List[float], List[float]]] = {}
        for v, d in zip(mitten, dicken):
            breite: Dict[int, float] = {}
            moment: Dict[int, float] = {}
            for i, g in gewichte:
                abschnitte = geo.schnitt_mit_gerade(self.teile[i].punkte, n, v + n_s)
                if not abschnitte:
                    continue
                b_i = sum(bis - von for von, bis in abschnitte)
                m_i = sum(((bis - t_s) ** 2 - (von - t_s) ** 2) / 2.0
                          for von, bis in abschnitte)
                for w, x in g.items():
                    breite[w] = breite.get(w, 0.0) + x * b_i
                    moment[w] = moment.get(w, 0.0) + x * m_i
            for w, b_w in breite.items():
                if b_w <= 1e-12:
                    continue
                arme, flaechen, quer = sammlung.setdefault(w, ([], [], []))
                arme.append(v)
                flaechen.append(b_w * d)
                quer.append(moment[w] / b_w)

        gruppen = []
        gruppen_werkstoff = []
        for w in sorted(sammlung):
            arme, flaechen, quer = sammlung[w]
            gruppen.append(Fasergruppe(gesetz=self.werkstoffe[w].gesetz,
                                       arme=tuple(arme), flaechen=tuple(flaechen),
                                       quer=tuple(quer)))
            gruppen_werkstoff.append(w)

        staebe = []
        staebe_v = []
        for s in self.bewehrung:
            v = v_von(s.lage)
            u = t[0] * (s.lage[0] - sy) + t[1] * (s.lage[1] - sz)
            verdraengt = (self.werkstoffe[s.verdraengt].gesetz
                          if s.verdraengt is not None
                          and self.werkstoffe[s.verdraengt].verdraengbar else None)
            staebe.append(Stab(arm=v, flaeche=s.flaeche,
                               gesetz=self.werkstoffe[s.werkstoff].gesetz,
                               verdraengt=verdraengt, quer=u))
            staebe_v.append(v)

        grenzen, beton = self._grenzen(v_von)
        return Richtung(
            psi=psi, n=n, t=t, fasern=Faserquerschnitt(gruppen, staebe),
            grenzen=Dehnungsgrenzen(grenzen), gruppen_werkstoff=tuple(gruppen_werkstoff),
            beton=beton, staebe_v=tuple(staebe_v))

    def _grenzen(self, v_von) -> Tuple[List[Dehnungsgrenze], Optional[Tuple[float, float]]]:
        """
        Die Dehnungsgrenzen fuer diese Neigung: je Werkstoff an seinen
        aeussersten Punkten, beim Beton dazu die C-Punkte.
        """
        lagen: Dict[int, List[float]] = {}
        for teil in self.teile:
            if teil.werkstoff is not None:
                lagen.setdefault(teil.werkstoff, []).extend(v_von(p) for p in teil.punkte)
        for s in self.bewehrung:
            lagen.setdefault(s.werkstoff, []).extend(
                v_von(p) for p in (s.grenzpunkte or (s.lage,)))

        grenzen: List[Dehnungsgrenze] = []
        beton: Optional[Tuple[float, float]] = None
        for w, vs in sorted(lagen.items()):
            stoff = self.werkstoffe[w]
            v_min, v_max = min(vs), max(vs)
            for v in {v_min, v_max}:
                grenzen.append(Dehnungsgrenze(arm=v, eps_min=stoff.eps_min,
                                              eps_max=stoff.eps_max))
            if stoff.c_punkt is not None:
                eps_c1d, eps_c2d = stoff.c_punkt
                anteil = 1.0 - eps_c1d / eps_c2d
                hoehe = v_max - v_min
                for v in (v_min + anteil * hoehe, v_max - anteil * hoehe):
                    grenzen.append(Dehnungsgrenze(arm=v, eps_min=-eps_c1d,
                                                  eps_max=math.inf))
                beton = (v_min, v_max) if beton is None else (
                    min(beton[0], v_min), max(beton[1], v_max))

        if not any(math.isfinite(g.eps_max) for g in grenzen):
            # Nichts nennt eine Zuggrenze: ein Querschnitt ohne Bewehrung.
            # Der Faecher braucht trotzdem einen Anfang.
            alle = [v for vs in lagen.values() for v in vs]
            for v in {min(alle), max(alle)}:
                grenzen.append(Dehnungsgrenze(arm=v, eps_min=-math.inf,
                                              eps_max=EPS_ZUG_OHNE_GRENZE))
        return grenzen, beton

    # -- Der Faecher ----------------------------------------------------------

    @staticmethod
    def _knicke(grenzen: Dehnungsgrenzen, chi_max: float, oben: bool) -> List[float]:
        """
        Wo die massgebende Grenze wechselt, entlang einer Kette des Vielecks.

        Die obere Kette ist ``min(eps_max - chi·arm)`` (der gezogenste Punkt
        bestimmt), die untere ``max(eps_min - chi·arm)``. Beide sind stueckweise
        linear in chi; zurueck kommen die Knicke von 0 bis ``chi_max``.
        """
        linien = [(g.eps_max if oben else g.eps_min, g.arm) for g in grenzen.grenzen
                  if math.isfinite(g.eps_max if oben else g.eps_min)]
        wert = lambda l, c: l[0] - c * l[1]
        knicke = [0.0]
        chi = 0.0
        if oben:
            aktiv = min(linien, key=lambda l: (wert(l, 0.0), -l[1]))
        else:
            aktiv = max(linien, key=lambda l: (wert(l, 0.0), -l[1]))
        while True:
            naechst, wechsel = chi_max, None
            for l in linien:
                if (l[1] > aktiv[1]) if oben else (l[1] < aktiv[1]):
                    c = (l[0] - aktiv[0]) / (l[1] - aktiv[1])
                    if chi + 1e-15 < c < naechst:
                        naechst, wechsel = c, l
            if wechsel is None:
                break
            knicke.append(naechst)
            chi, aktiv = naechst, wechsel
        knicke.append(chi_max)
        return knicke

    def faecher(self, psi: float, schritte: int = SCHRITTE) -> List[Bruchpunkt]:
        """
        Die Ebenen des Faechers fuer diese Neigung, von gleichmaessigem Zug
        bis zu gleichmaessigem Druck -- je Abschnitt ``schritte`` Stuetzstellen.
        """
        r = self.richtung(psi)
        return [r.punkt(eps_m, chi) for eps_m, chi in self._faecherebenen(r, schritte)]

    def _faecherebenen(self, r: Richtung, schritte: int) -> List[Tuple[float, float]]:
        chi_max = r.grenzen.kruemmungsgrenze(positiv=True)
        ebenen: List[Tuple[float, float]] = []
        for oben in (True, False):
            knicke = self._knicke(r.grenzen, chi_max, oben)
            if not oben:
                knicke = list(reversed(knicke))
            for von, bis in zip(knicke, knicke[1:]):
                for i in range(schritte):
                    chi = von + (bis - von) * i / schritte
                    ebenen.append((self._auf_kette(r, chi, oben), chi))
        ebenen.append((self._auf_kette(r, 0.0, False), 0.0))
        return ebenen

    @staticmethod
    def _auf_kette(r: Richtung, chi: float, oben: bool) -> float:
        """Die Dehnung im Bezugspunkt auf der oberen oder unteren Kette."""
        fenster = r.grenzen.fenster(chi)
        if fenster is None:
            # Nur knapp ueber der groessten Kruemmung, durch Rundung: dort
            # fallen beide Ketten zusammen.
            unten = max(g.eps_min - chi * g.arm for g in r.grenzen.grenzen)
            oben_ = min(g.eps_max - chi * g.arm for g in r.grenzen.grenzen)
            return 0.5 * (unten + oben_)
        return fenster[1] if oben else fenster[0]

    # -- Reine Normalkraft --------------------------------------------------

    def normalkraft_grenzen(self) -> Tuple[float, float]:
        """
        Groesste Zug- und groesste Druckkraft -- gleichmaessige Dehnung, also
        fuer jede Neigung dieselbe.
        """
        r = self.richtung(-math.pi / 2.0)
        zug = r.punkt(self._auf_kette(r, 0.0, True), 0.0).N
        druck = r.punkt(self._auf_kette(r, 0.0, False), 0.0).N
        return zug, druck

    # -- N = N_Ed auf dem Faecher -------------------------------------------

    def bei_normalkraft(self, psi: float, N: float) -> Optional[Bruchpunkt]:
        """
        Die Ebene des Faechers mit ``N_int = N``, fuer diese Neigung.

        Erst eingegrenzt zwischen zwei Stuetzstellen -- vom Zug her die
        erste, zwischen denen N die Seite wechselt --, dann mit dem
        Illinois-Verfahren auf der Strecke dazwischen. Zwei benachbarte
        Stuetzstellen liegen im selben Abschnitt des Faechers, und dort ist die
        Ebene linear in ihren beiden Groessen: die Strecke dazwischen bleibt
        auf dem Faecher. ``None``, wenn N jenseits der reinen Zug- oder
        Druckkraft liegt.
        """
        r = self.richtung(psi)
        ebenen = self._faecherebenen(r, SUCHSCHRITTE)
        werte = [r.fasern.kraefte(eps_m, chi).N for eps_m, chi in ebenen]
        if not (werte[-1] <= N <= werte[0]):
            return None
        for i in range(len(ebenen) - 1):
            if werte[i] >= N >= werte[i + 1]:
                break
        a, b = ebenen[i], ebenen[i + 1]
        if werte[i] == N:
            return r.punkt(*a)
        if werte[i + 1] == N:
            return r.punkt(*b)

        def ebene(anteil: float) -> Tuple[float, float]:
            return (a[0] + (b[0] - a[0]) * anteil, a[1] + (b[1] - a[1]) * anteil)

        def abweichung(anteil: float):
            punkt = r.punkt(*ebene(anteil))
            return punkt.N - N, punkt

        massstab = max(abs(werte[0]), abs(werte[-1]), 1.0)
        return illinois(abweichung, 0.0, werte[i] - N, 1.0, werte[i + 1] - N,
                        schranke_x=1e-14, schranke_f=1e-11 * massstab)

    # -- Widerstand in einer Momentenrichtung ---------------------------------

    @staticmethod
    def neigung_fuer(M_y: float, M_z: float) -> float:
        """
        Die Zugrichtung, die zu einem Moment gehoert, wenn der Querschnitt
        symmetrisch waere: das Moment ``(M_y, M_z)`` zieht auf der Seite
        ``-(sin φ, cos φ)``. M_y > 0 zieht unten, M_z > 0 links.
        """
        phi = math.atan2(M_z, M_y)
        return math.atan2(-math.cos(phi), -math.sin(phi))

    def in_richtung(self, N: float, M_y: float, M_z: float) -> Optional[Bruchpunkt]:
        """
        Der Bruchzustand bei dieser Normalkraft, dessen Moment in die Richtung
        von ``(M_y, M_z)`` zeigt.

        Die Richtung φ des Moments nimmt ab, wenn die Zugrichtung ψ zunimmt --
        bei Symmetrie ist ``φ = -90° - ψ``. Bei einem L laeuft das in Stufen:
        ueber weite Bereiche von ψ kaum eine Aenderung, dann ein Sprung. Ein
        Sekantenverfahren verliert dort die Spur. Darum: von der Neigung aus,
        die bei Symmetrie gaelte, in die richtige Richtung mit wachsenden
        Schritten, bis die Abweichung das Vorzeichen wechselt -- dann
        Illinois. ``None``, wenn N jenseits der reinen Zug- oder Druckkraft
        liegt.
        """
        ziel = math.atan2(M_z, M_y)

        def abweichung(psi: float):
            punkt = self.bei_normalkraft(psi, N)
            if punkt.moment == 0.0:
                return 0.0, punkt
            return math.remainder(math.atan2(punkt.M_z, punkt.M_y) - ziel,
                                  2.0 * math.pi), punkt

        if self.bei_normalkraft(0.0, N) is None:
            return None
        a = self.neigung_fuer(M_y, M_z)
        fa, punkt = abweichung(a)
        if abs(fa) <= WINKEL_SCHRANKE:
            return punkt
        # φ zu gross heisst: ψ vergroessern.
        richtung = 1.0 if fa > 0 else -1.0
        schritt = math.radians(5.0)
        gegangen = 0.0
        while gegangen < 2.0 * math.pi:
            b = a + richtung * schritt
            fb, punkt = abweichung(b)
            if abs(fb) <= WINKEL_SCHRANKE:
                return punkt
            if (fb > 0) != (fa > 0) and abs(fb - fa) < math.pi:
                return illinois(abweichung, a, fa, b, fb,
                                schranke_x=1e-12, schranke_f=WINKEL_SCHRANKE)
            gegangen += schritt
            a, fa = b, fb
            schritt = min(2.0 * schritt, math.radians(45.0))
        return punkt  # nicht eingegrenzt -- kommt bei einem Querschnitt nicht vor

    # -- Aufschluesselung ---------------------------------------------------

    def anteile(self, punkt: Bruchpunkt) -> List[Kraftanteil]:
        """
        Was jeder Werkstoff und jeder Stab zu diesem Bruchzustand beitraegt --
        fuer die Probe in der Herleitung.

        Der Werkstoff als Resultierende mit Angriffspunkt, jeder Stab mit
        Dehnung, Spannung und Kraft. Die Summe der Kraefte ist N, die Summe
        der Momente M_y und M_z -- das laesst sich von Hand nachrechnen.
        """
        r = self.richtung(punkt.psi)
        sy, sz = self.bezug
        anteile: List[Kraftanteil] = []
        for gruppe, w in zip(r.fasern.gruppen, r.gruppen_werkstoff):
            teil = Faserquerschnitt([gruppe], []).kraefte(punkt.eps_m, punkt.chi)
            anteile.append(self._anteil(r, self.werkstoffe[w].name, teil.N, teil.M,
                                        teil.M_quer))
        for s, stab in zip(self.bewehrung, r.fasern.staebe):
            eps = punkt.eps_m + punkt.chi * stab.arm
            sigma = stab.gesetz(eps)
            kraft = (sigma - (stab.verdraengt(eps) if stab.verdraengt else 0.0)) * stab.flaeche
            anteile.append(Kraftanteil(name=self.werkstoffe[s.werkstoff].name,
                                       N=kraft, y=s.lage[0], z=s.lage[1],
                                       eps=eps, sigma=sigma))
        return anteile

    def _anteil(self, r: Richtung, name: str, N: float, M: float,
                M_quer: float) -> Kraftanteil:
        sy, sz = self.bezug
        if N == 0.0:
            return Kraftanteil(name=name, N=0.0, y=sy, z=sz)
        M_y, M_z = r.momente(N, M, M_quer)
        # M_y = -N·(z - z_S) und M_z = -N·(y - y_S), nach dem Ort aufgeloest.
        return Kraftanteil(name=name, N=N, y=sy - M_z / N, z=sz - M_y / N)

    def dehnung(self, punkt: Bruchpunkt, p: Punkt) -> float:
        """Die Dehnung dieser Ebene an einem Ort des Querschnitts."""
        n = punkt.zugrichtung
        return punkt.eps_m + punkt.chi * (n[0] * (p[0] - self.bezug[0])
                                          + n[1] * (p[1] - self.bezug[1]))

    def druckzone(self, punkt: Bruchpunkt) -> Tuple[float, float]:
        """
        Druckzonenhoehe x und statische Hoehe d dieser Ebene, beide senkrecht
        zur Nulllinie und ab dem gedrueckten Betonrand gemessen.

        d gehoert zum entferntesten gezogenen Stab. Ohne gezogenen Stab ist d
        null, ohne Beton beides null.
        """
        r = self.richtung(punkt.psi)
        if r.beton is None:
            return 0.0, 0.0
        rand = r.beton[0]  # chi >= 0: gedrueckt ist die Seite kleiner v
        if punkt.chi > 0.0:
            nulllinie = -punkt.eps_m / punkt.chi
            x = min(max(nulllinie - rand, 0.0), r.beton[1] - rand)
        else:
            x = (r.beton[1] - rand) if punkt.eps_m < 0.0 else 0.0
        gezogen = [v for v in r.staebe_v if punkt.eps_m + punkt.chi * v > 0.0]
        d = (max(gezogen) - rand) if gezogen else 0.0
        return x, d
