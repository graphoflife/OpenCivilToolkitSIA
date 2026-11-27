"""
opencivil/decke/fem/rechnung.py -- die FEM der Decke, Fall für Fall.

VERANTWORTUNG:
Die Decke einmal vernetzt (:mod:`~opencivil.decke.fem.netz`) und ihr System
einmal zerlegt (:mod:`~opencivil.decke.fem.system`); dann je Lastfall die
Lasten auf den Knoten (:mod:`~opencivil.decke.fem.belastung`) und je
Kombination ihre Summe mit den Beiwerten -- die Platte ist linear. Je Fall:

1. die Verschiebungen ``(w, β_x, β_y)`` je Knoten;
2. die Momente jedes Dreiecks an seinen Ecken, an den Knoten geglättet
   (:mod:`~opencivil.decke.fem.glaetten`);
3. die Querkräfte aus dem Gefälle der geglätteten Momente, je Dreieck
   ``v_x = ∂m_x/∂x + ∂m_xy/∂y`` und ``v_y = ∂m_xy/∂x + ∂m_y/∂y``, ebenso
   geglättet;
4. was die Lager tragen, aus ``K·u − f`` an ihren Knoten;
5. Moment und Querkraft jedes Balkenstücks eines Trägers.

Am Ende die Probe wie in der Streifenmethode: alle Lagerkräfte zusammen
sind die Last, ohne was neben den Platten liegt oder auf einem Teil, der
sich frei bewegen könnte.

LÄNGS EINES LINIENLAGERS:
Zu jedem Knoten gehört das Stück des Lagers bis zur Mitte der Kanten
daneben, und was er trägt, verteilt sich gleichmässig darüber: ``r = F/l``.
Hält das Lager die Drehung, ist ``m`` ebenso das Moment, das der Knoten
hält, je Meter -- mit dem Vorzeichen der Platte wie in der Streifenmethode:
dem der Seite, die stärker zieht (:func:`~opencivil.decke.rechnung.gehalten`).
Liegen mehrere Lager an einem Knoten, teilen sie ihn nach der Länge ihrer
Stücke; steht eine Stütze darauf, trägt sie ihn allein.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set, Tuple

from opencivil.decke import feld
from opencivil.decke import geometrie as geo
from opencivil.decke.feld import Schnittkraefte
from opencivil.decke.fem.belastung import Knotenlasten, Raster, belasten
from opencivil.decke.fem.element import Dreieck, balkenkraefte
from opencivil.decke.fem.glaetten import Glaettung
from opencivil.decke.fem.netz import Netz, kante, schaetzung, vernetzen
from opencivil.decke.fem.system import System
from opencivil.decke.lasten import kn
from opencivil.decke.modell import Decke, Linienlager
from opencivil.decke.rechnung import Ausfall, Fall, Faelle, gehalten
from opencivil.decke.streifen import pruefen
from opencivil.stabwerk.system import Meldung

#: Mehr Knoten rechnet die Rechnung nicht: auf der Seite dauerte es zu lange (nach Vorgabe, nicht nachgeschlagen).
KNOTEN_HOECHSTENS = 3000

#: Was ein Bild der Platte in der FEM zeigen kann: die Grössen der Streifenmethode und die Durchbiegung.
GROESSEN = {**feld.GROESSEN, "w": "w"}

#: Ein Stück längs eines Linienlagers: ``(u_a, u_b, r, m)`` wie :func:`~opencivil.decke.rechnung.lagerverlauf`.
Stufe = Tuple[float, float, float, float]


@dataclass(frozen=True)
class Femwerte(Schnittkraefte):
    """An einer Ecke: die Schnittkräfte wie in der Streifenmethode und die Durchbiegung ``w`` in m, nach unten."""

    w: float = 0.0

    def groesse(self, name: str) -> float:
        """Die Grösse ``name`` aus :data:`GROESSEN`."""
        return getattr(self, GROESSEN[name])


@dataclass(frozen=True)
class Balkenwerte:
    """
    Ein Stück eines Trägers als Balken, von ``u_p`` bis ``u_q`` m ab seinem
    Anfang: die Momente an seinen Enden in Nm, positiv mit Zug unten, und
    die Querkraft ``V = dM/du`` in N dazwischen.
    """

    u_p: float
    u_q: float
    M_p: float
    M_q: float
    V: float


@dataclass
class Femfall(Fall):
    """Ein Lastfall oder eine Kombination nach der FEM."""

    name: str
    summe: float
    """Die ganze Last, in N."""

    daneben: float
    """Was davon neben den Platten liegt."""

    nicht_getragen: float = 0.0
    """Was auf Teilen liegt, die sich frei bewegen könnten."""

    verschiebungen: List[Tuple[float, float, float]] = field(default_factory=list)
    """Je Knoten ``(w, β_x, β_y)`` in m und rad."""

    sektoren: List[Femwerte] = field(default_factory=list)
    """Je Sektor der Glättung (:class:`~opencivil.decke.fem.glaetten.Glaettung`) seine Werte."""

    ecken: List[Tuple[Femwerte, ...]] = field(default_factory=list)
    """Je Dreieck die Werte an seinen drei Ecken -- dazwischen linear."""

    stuetzen: Dict[str, float] = field(default_factory=dict)
    """Je Stütze die Kraft nach unten auf sie, in N."""

    linienlager: Dict[str, Tuple[float, List[Stufe]]] = field(default_factory=dict)
    """Je Linienlager die Kraft nach unten auf es, in N, und ihr Verlauf längs."""

    traeger: Dict[str, List[Balkenwerte]] = field(default_factory=dict)
    """Je Träger mit Höhe seine Stücke als Balken, nach ihrer Stelle."""

    meldungen: List[Meldung] = field(default_factory=list)

    def stuetzenkraft(self, name: str) -> float:
        return self.stuetzen.get(name, 0.0)

    def wandkraft(self, name: str) -> float:
        return self.linienlager[name][0] if name in self.linienlager else 0.0

    def lagerstufen(self, lager: Linienlager) -> List[Stufe]:
        return self.linienlager[lager.name][1] if lager.name in self.linienlager else []


@dataclass
class Femergebnis(Faelle):
    """
    Die Decke nach der FEM: ihre Fälle und Meldungen, dazu Netz, System,
    Glättung und Raster -- ``None``, wenn eine Meldung die Rechnung aufhielt.
    """

    decke: Decke
    faelle: List[Femfall]
    meldungen: List[Meldung]
    netz: Optional[Netz] = None
    system: Optional[System] = None
    glaettung: Optional[Glaettung] = None
    raster: Optional[Raster] = None


def rechnen(decke: Decke) -> Femergebnis:
    """Die Decke nach der FEM, je Lastfall und Kombination -- oder, was dem im Weg steht."""
    meldungen = pruefen(decke)
    if any(m.haelt_an for m in meldungen) or not decke.platten:
        return Femergebnis(decke, [], meldungen)
    if decke.zonen:
        namen = tuple(z.name for z in decke.zonen)
        wer = f"Die Zone «{namen[0]}» zählt" if len(namen) == 1 else f"Die Zonen {_namen(namen)} zählen"
        meldungen.append(Meldung(f"{wer} nur in der Streifenmethode: die FEM teilt die Last nicht auf.",
                                 namen, fehler=False))
    zahl = schaetzung(decke, decke.netzweite)
    if zahl > KNOTEN_HOECHSTENS:
        meldungen.append(Meldung(
            f"Mit der Netzweite {decke.netzweite:g} m hätte das Netz etwa {zahl} Knoten – mehr als "
            f"{KNOTEN_HOECHSTENS}. Bitte die Netzweite mindestens {_weite_fuer(decke):g} m wählen."))
        return Femergebnis(decke, [], meldungen)
    netz = vernetzen(decke, decke.netzweite)
    meldungen += netz.meldungen + _daneben(decke, netz)
    system = System(decke, netz)
    glaettung = Glaettung(netz)
    raster = Raster(netz)
    teile = _teile(decke, netz, system)
    lasten = {lf.name: belasten(decke, netz, raster, lf) for lf in decke.lastfaelle}
    for k in decke.kombinationen:
        summe = Knotenlasten([0.0] * len(netz.knoten))
        for name, faktor in k.faktoren.items():
            if name in lasten and faktor:
                summe = summe.plus(lasten[name].mal(faktor))
        lasten[k.name] = summe
    faelle = [_fall(name, l, decke, system, glaettung, teile) for name, l in lasten.items()]
    for f in faelle:
        f.probe("auf den Platten")
    return Femergebnis(decke, faelle, meldungen, netz, system, glaettung, raster)


def _namen(namen: Sequence[str]) -> str:
    return ", ".join(f"«{n}»" for n in namen)


def _weite_fuer(decke: Decke) -> float:
    """Die kleinste Netzweite auf 5 cm genau, mit der das Netz etwa :data:`KNOTEN_HOECHSTENS` Knoten hat."""
    flaeche = sum(abs(geo.flaeche(list(p.ecken))) for p in decke.platten)
    return math.ceil(20.0 * math.sqrt(flaeche / (math.sqrt(3.0) / 2.0 * KNOTEN_HOECHSTENS))) / 20.0


def _daneben(decke: Decke, netz: Netz) -> List[Meldung]:
    """Was neben den Platten liegt und darum nichts trägt -- grau, der Rest rechnet."""
    heraus = []
    for s in decke.stuetzen:
        if s.name not in netz.stuetzen:
            heraus.append(Meldung(f"Die Stütze «{s.name}» steht neben den Platten – sie trägt nichts.",
                                  (s.name,), fehler=False))
    for l in decke.linienlager:
        linie = netz.linie("linienlager", l.name)
        if linie is not None and not linie.knoten:
            heraus.append(Meldung(f"Das Linienlager «{l.name}» liegt neben den Platten – es trägt nichts.",
                                  (l.name,), fehler=False))
    for u in decke.traeger:
        linie = netz.linie("traeger", u.name)
        if linie is not None and not linie.stuecke:
            heraus.append(Meldung(f"Der Träger «{u.name}» liegt auf keiner Platte.", (u.name,), fehler=False))
    return heraus


def _teile(decke: Decke, netz: Netz, system: System) -> List[Tuple[Set[int], Tuple[str, ...]]]:
    """Je Teil, der sich frei bewegen könnte, seine Knoten und die Namen seiner Platten."""
    heraus = []
    for teil in system.beweglich:
        nummern = sorted({netz.platte[e] for e, d in enumerate(netz.dreiecke) if d[0] in teil})
        heraus.append((teil, tuple(decke.platten[i].name for i in nummern)))
    return heraus


# ===========================================================================
# Ein Fall
# ===========================================================================


def _fall(name: str, lasten: Knotenlasten, decke: Decke, system: System, glaettung: Glaettung,
          teile: Sequence[Tuple[Set[int], Tuple[str, ...]]]) -> Femfall:
    netz = system.netz
    heraus = Femfall(name, lasten.summe, lasten.daneben, meldungen=list(lasten.meldungen))
    u = system.loesen(lasten.kraefte)
    heraus.verschiebungen = u
    momente = glaettung.mitteln([d.momente([v for k in ecken for v in u[k]])
                                 for d, ecken in zip(system.dreiecke, netz.dreiecke)])
    querkraefte = glaettung.mitteln([_querkraft(d, [momente[s] for s in sektoren])
                                     for d, sektoren in zip(system.dreiecke, glaettung.sektor)])
    heraus.sektoren = [Femwerte(*m, *v, w=u[k][0]) for m, v, k in zip(momente, querkraefte, glaettung.knoten)]
    heraus.ecken = [tuple(heraus.sektoren[s] for s in sektoren) for sektoren in glaettung.sektor]
    aus = {k for teil, _ in teile for k in teil}
    reste = system.reste(u, lasten.kraefte)
    genommen = _stuetzen(heraus, decke, netz, reste, aus)
    _linienlager(heraus, decke, netz, glaettung, reste, aus | genommen)
    heraus.traeger = _balken(system, u)
    for teil, platten in teile:
        F = sum(lasten.kraefte[k] for k in teil)
        heraus.nicht_getragen += F
        if F:
            grund = (f"Die Platte «{platten[0]}» ist nicht genug gehalten – sie könnte sich frei bewegen."
                     if len(platten) == 1 else
                     f"Die Platten {_namen(platten)} sind nicht genug gehalten – sie könnten sich frei bewegen.")
            heraus.meldungen.append(Ausfall(f"{grund} {kn(F)} kN fallen aus.", platten, grund=grund, F=F))
    return heraus


def _querkraft(d: Dreieck, momente: Sequence[Sequence[float]]) -> List[Tuple[float, float]]:
    """``(v_x, v_y)`` an den drei Ecken aus dem Gefälle der geglätteten Momente -- im Dreieck gleich."""
    mx_x, mx_y = d.gefaelle([m[0] for m in momente])
    my_x, my_y = d.gefaelle([m[1] for m in momente])
    mxy_x, mxy_y = d.gefaelle([m[2] for m in momente])
    v = (mx_x + mxy_y, mxy_x + my_y)
    return [v, v, v]


def _stuetzen(heraus: Femfall, decke: Decke, netz: Netz, reste: Sequence[Sequence[float]],
              aus: Set[int]) -> Set[int]:
    """Je Stütze die Kraft ihres Knotens -- zurück: die Knoten, die Stützen tragen."""
    genommen: Set[int] = set()
    for s in decke.stuetzen:
        k = netz.stuetzen.get(s.name)
        if k is None or k in aus or k in genommen:
            continue
        heraus.stuetzen[s.name] = -reste[k][0]
        genommen.add(k)
    return genommen


def _linienlager(heraus: Femfall, decke: Decke, netz: Netz, glaettung: Glaettung,
                 reste: Sequence[Sequence[float]], ohne: Set[int]) -> None:
    """Je Linienlager, was seine Knoten tragen, und wie es sich längs verteilt."""
    je_lager: Dict[str, Dict[int, List[float]]] = {}
    zusammen: Dict[int, float] = {}
    zahl: Dict[int, int] = {}
    for lager in decke.linienlager:
        linie = netz.linie("linienlager", lager.name)
        if linie is None or not (lager.vertikal or lager.eingespannt):
            continue
        lage = dict(zip(linie.knoten, linie.u))
        halb: Dict[int, List[float]] = {k: [0.0, 0.0] for k in linie.knoten if k not in ohne}
        for p, q in linie.stuecke:
            l = 0.5 * (lage[q] - lage[p])
            if p in halb:
                halb[p][1] += l
            if q in halb:
                halb[q][0] += l
        je_lager[lager.name] = halb
        for k, (links, rechts) in halb.items():
            zusammen[k] = zusammen.get(k, 0.0) + links + rechts
            zahl[k] = zahl.get(k, 0) + 1
    for lager in decke.linienlager:
        halb = je_lager.get(lager.name)
        if halb is None:
            continue
        linie = netz.linie("linienlager", lager.name)
        t = linie.richtung
        n = (-t[1], t[0])
        lage = dict(zip(linie.knoten, linie.u))
        knoten = [k for k in linie.knoten if k in halb]
        werte = []
        for k in knoten:
            links, rechts = halb[k]
            # Der Anteil des Lagers am Knoten, nach der Länge seiner Stücke.
            anteil = (links + rechts) / zusammen[k] if zusammen[k] > 0.0 else 1.0 / zahl[k]
            m = 0.0
            if lager.eingespannt:
                r_n = reste[k][1] * n[0] + reste[k][2] * n[1]
                m_links, m_rechts = _seiten(heraus, glaettung, netz, k, n)
                m = r_n if gehalten(m_links, m_rechts) * r_n >= 0.0 else -r_n
            werte.append((-anteil * reste[k][0], anteil * m))
        stuecke = {kante(p, q) for p, q in linie.stuecke}
        werte = _ausgleichen(werte, [halb[k][0] > 0.0 and halb[k][1] > 0.0 and zahl[k] == 1 for k in knoten],
                             [kante(p, q) in stuecke for p, q in zip(knoten, knoten[1:])])
        stufen = [(lage[k] - halb[k][0], lage[k] + halb[k][1], R / sum(halb[k]), M / sum(halb[k]))
                  for k, (R, M) in zip(knoten, werte) if sum(halb[k]) > 0.0]
        heraus.linienlager[lager.name] = (sum(R for R, _ in werte), _luecken(stufen, linie.laenge))


def _ausgleichen(werte: Sequence[Tuple[float, float]], innen: Sequence[bool],
                 verbunden: Sequence[bool]) -> List[Tuple[float, float]]:
    """
    Kraft und Moment der Knoten eines Lagers, ausgeglichen: jeder Knoten
    mitten im Lager gibt je ein Viertel an seine Nachbarn, wenn sie auch
    mitten im Lager liegen (``innen``) und ein Stück sie verbindet
    (``verbunden[i]``: Knoten ``i`` und ``i + 1``). Die Kräfte der Knoten
    springen sonst von Knoten zu Knoten, je nachdem, wie viele Dreiecke an
    ihnen hängen; die Summe bleibt. An den Enden, an Lücken und wo ein
    anderes Lager anstösst, bleibt die Kraft, wo sie ist: dort greift eine
    Kraft im Punkt an, etwa an der Ecke einer Platte (nach Vorgabe, nicht
    nachgeschlagen).
    """
    heraus = [list(w) for w in werte]
    for i, w in enumerate(werte):
        if not innen[i]:
            continue
        for j in (i - 1, i + 1):
            if 0 <= j < len(werte) and innen[j] and verbunden[min(i, j)]:
                for c in range(2):
                    heraus[i][c] -= 0.25 * w[c]
                    heraus[j][c] += 0.25 * w[c]
    return [(R, M) for R, M in heraus]


def _seiten(fall: Femfall, glaettung: Glaettung, netz: Netz, k: int, n: Tuple[float, float]) -> Tuple[float, float]:
    """
    Das Moment der Platte quer zu einem Lager am Knoten ``k``, ``m_n`` in
    Nm/m, links -- auf der Seite von ``n`` -- und rechts: je das Mittel der
    Sektoren auf dieser Seite, null, wo keine Platte ist.
    """
    p = netz.knoten[k]
    summen = {1: [0.0, 0.0], -1: [0.0, 0.0]}
    for s in glaettung.an.get(k, ()):
        mitte = geo.schwerpunkt([netz.knoten[j] for j in netz.dreiecke[glaettung.dreieck[s]]])
        seite = 1 if (mitte[0] - p[0]) * n[0] + (mitte[1] - p[1]) * n[1] > 0.0 else -1
        w = fall.sektoren[s]
        m_n = w.mx * n[0] * n[0] + w.my * n[1] * n[1] + 2.0 * w.mxy * n[0] * n[1]
        summen[seite][0] += glaettung.gewicht[s] * m_n
        summen[seite][1] += glaettung.gewicht[s]
    links, rechts = (summen[i][0] / summen[i][1] if summen[i][1] else 0.0 for i in (1, -1))
    return links, rechts


def _luecken(stufen: Sequence[Stufe], L: float) -> List[Stufe]:
    """Die Stufen von 0 bis ``L``: wo keine Platte ist -- über ein Loch, neben den Platten --, null."""
    heraus: List[Stufe] = []
    bei = 0.0
    for s in stufen:
        if s[0] - bei > geo.TOLERANZ:
            heraus.append((bei, s[0], 0.0, 0.0))
        heraus.append(s)
        bei = s[1]
    if L - bei > geo.TOLERANZ:
        heraus.append((bei, L, 0.0, 0.0))
    return heraus


def _balken(system: System, u: Sequence[Tuple[float, float, float]]) -> Dict[str, List[Balkenwerte]]:
    """Je Träger mit Höhe Moment und Querkraft seiner Stücke als Balken."""
    heraus: Dict[str, List[Balkenwerte]] = {}
    for b in system.balken:
        c, s = b.richtung
        (wp, xp, yp), (wq, xq, yq) = u[b.p], u[b.q]
        M_p, M_q, V = balkenkraefte(b.K4, [wp, c * xp + s * yp, wq, c * xq + s * yq])
        heraus.setdefault(b.traeger, []).append(Balkenwerte(b.u_p, b.u_q, M_p, M_q, V))
    return heraus
