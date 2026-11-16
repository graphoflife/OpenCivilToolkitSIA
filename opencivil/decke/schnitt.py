"""
opencivil/decke/schnitt.py -- die Schnittkräfte längs eines Schnitts.

VERANTWORTUNG:
Ein Schnitt ist eine Strecke über die Decke, von ``a`` nach ``b``. Längs ihr
zeigt ein Ergebnisbild eine Grösse der Platte als Verlauf, wie bei einem
Balken mit den Lagern, die er kreuzt (Benutzer, 2026-11-16). Gerechnet wird
damit nichts: die Werte kommen von :func:`~opencivil.decke.feld.an_stelle`,
woher auch die Bilder der Platte und der Bericht sie nehmen.

WO DER VERLAUF HINSIEHT:
Zwischen zwei Stellen, an denen sich etwas ändert, ist jede Grösse längs
des Schnitts ein Polynom -- v_0 der Betrag zweier. Solche Stellen sind die
Grenzen der Feldstreifen, die Ränder der Unterzüge und der Platten und die
Enden der Trägerstücke, durch deren Streifen er läuft: ein Lager, eine
Last, die beginnt oder aufhört. Dort sieht der Verlauf zu beiden Seiten
hin, :data:`~opencivil.decke.feld.INNEN` daneben -- ein Sprung steht als
zwei Werte an fast derselben Stelle da. Auf eine solche Stelle selbst sieht
er nie: auf dem Rand eines Unterzugs zählten er und der Feldstreifen
daneben zugleich. Dazwischen in Schritten von höchstens einem
:data:`SCHRITTE`-tel der Länge und dort, wo ein Träger sein grösstes
Moment oder seine grösste Querkraft hat: wo seine Querkraft oder seine
Last null wird. So liegt der grösste Wert genau, wo ein Streifen allein
trägt -- wie in den Bildern der Platte (:func:`~opencivil.decke.feld.stellen`).

WAS ER KREUZT:
Linienlager als Lager, Stützen auch -- wenn er durch ihren Querschnitt geht
--, Unterzüge als Bereich. Alles in m ab ``a``.

EIN UNTERZUG:
Längs seiner Achse zeigt ein Bild auch einen Unterzug selbst: sein Moment
und seine Querkraft über die ganze Breite, nicht je Meter (Benutzer,
2026-11-16) -- so, wie er als Träger gerechnet ist (:func:`unterzug`). Hier
braucht es keine Grenzen: jedes Stück seines Trägers hat seine eigenen
Polynome, auch an den Enden.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple, Union

from opencivil.decke import geometrie as geo
from opencivil.decke.feld import INNEN, Schnittkraefte, an_stelle
from opencivil.decke.geometrie import Punkt
from opencivil.decke.modell import Decke
from opencivil.decke.rechnung import Ergebnis, Fallergebnis
from opencivil.decke.streifen import Streifen, Zerlegung
from opencivil.decke.traeger import vorderste_extreme

#: In so viele gleiche Schritte teilt der Verlauf einen Schnitt mindestens.
SCHRITTE = 120

#: Kleiner zählt eine Richtung als quer zum Schnitt -- ein Kosinus.
QUER = 1e-12

#: Was das Bild eines Unterzugs zeigt: sein Moment und seine Querkraft.
BALKENGROESSEN = ("M", "V")


@dataclass(frozen=True)
class Balkenkraefte:
    """An einer Stelle eines Unterzugs sein Moment in Nm und seine Querkraft in N -- über die ganze Breite."""

    M: float
    V: float

    def groesse(self, name: str) -> float:
        """Die Grösse ``name`` aus :data:`BALKENGROESSEN`."""
        return getattr(self, name)


@dataclass(frozen=True)
class Lagerstelle:
    """Wo ein Schnitt ein Lager kreuzt: ``u`` in m ab seinem Anfang, und was das Lager hält."""

    u: float
    art: str
    """``linienlager``, ``stuetze`` oder -- unter einem Unterzug -- ``unterzug``."""

    name: str
    vertikal: bool = True
    eingespannt: bool = False


@dataclass(frozen=True)
class Verlauf:
    """
    Die Schnittkräfte längs eines Schnitts der Länge ``L``, in m: wo er in
    einer Platte liegt (``stuecke``, von -- bis ab seinem Anfang), seine
    ``proben`` -- ``(u, Kräfte)``, aufsteigend; je Meter längs eines
    Schnitts, ganz längs eines Unterzugs --, die ``lager``, die er kreuzt,
    und die ``unterzuege`` als ``(von, bis, Name)``.
    """

    L: float
    stuecke: List[Tuple[float, float]]
    proben: List[Tuple[float, Union[Schnittkraefte, Balkenkraefte]]]
    lager: List[Lagerstelle]
    unterzuege: List[Tuple[float, float, str]]

    def extreme(self, groesse: str) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """``((u, kleinster), (u, grösster))`` der Grösse unter den Proben -- bei gleichen Werten der vordere."""
        return vorderste_extreme([(u, k.groesse(groesse)) for u, k in self.proben])


def verlauf(ergebnis: Ergebnis, fall: Fallergebnis, a: Punkt, b: Punkt) -> Verlauf:
    """Der Verlauf längs des Schnitts von ``a`` nach ``b`` im Fall ``fall`` -- ohne Länge leer."""
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    if L <= geo.TOLERANZ:
        return Verlauf(0.0, [], [], [], [])
    e = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
    z = ergebnis.zerlegung
    stuecke = geo.vereinigt([(u0 * L, u1 * L) for p in ergebnis.decke.platten
                             for u0, u1 in geo.strecke_im_vieleck(a, b, list(p.ecken))])
    unterzuege = [(u0 * L, u1 * L, s.name) for s in z.unterzuege
                  for u0, u1 in geo.strecke_im_vieleck(a, b, list(s.gebiet))]
    grenzen, spitzen = _stellen(z, fall, a, e)
    grenzen += [u * L for s in z.unterzuege for u in geo.schnittstellen(a, b, list(s.gebiet))]
    orte: List[float] = []
    for von, bis in stuecke:
        teile = _gerastert([von, *(u for u in grenzen if von < u < bis), bis])
        for p, q in zip(teile, teile[1:]):
            orte += _im_teil(p, q, L / SCHRITTE, spitzen)
    proben = [(u, an_stelle(ergebnis, fall, (a[0] + u * e[0], a[1] + u * e[1]))) for u in orte]
    return Verlauf(L, stuecke, proben, _lager(ergebnis.decke, a, b, e, L), unterzuege)


def unterzug(fall: Fallergebnis, streifen: Streifen) -> Verlauf:
    """
    Moment und Querkraft des Unterzugs ``streifen`` über seine ganze Breite,
    längs seiner Achse ab ``a`` -- aus den Stücken seiner Träger, je an
    ihren Enden, auf dem Raster und wo V oder die Last null wird. Ein Träger,
    den der Fall nicht rechnet, hat nichts: er trägt keine Last, oder er
    trägt nicht, und eine Meldung sagt es. Seine Lager sind die seiner
    Träger: Linienlager, Stützen und Unterzüge höherer Stufe. Zeigt die
    Richtung des Streifens von ``b`` nach ``a``, kehrt die Querkraft ihr
    Vorzeichen: im Bild gilt ``V = dM/du``.
    """
    a, b = streifen.unterzug.a, streifen.unterzug.b
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    n = streifen.richtung.n
    vz = 1.0 if geo.skalar((b[0] - a[0], b[1] - a[1]), n) >= 0.0 else -1.0
    sa = geo.skalar(a, n)

    def ort(s: float) -> float:
        return vz * (s - sa)

    stuecke: List[Tuple[float, float]] = []
    proben: List[Tuple[float, Union[Schnittkraefte, Balkenkraefte]]] = []
    lager: List[Lagerstelle] = []
    for t in streifen.traeger:
        u0, u1 = sorted((ort(t.s0), ort(t.s1)))
        stuecke.append((u0, u1))
        lager += [Lagerstelle(ort(t.s0 + l.s), l.art, l.name, l.vertikal, l.eingespannt) for l in t.auflager]
        traeger = fall.traeger.get(t.name)
        if traeger is None:
            proben += [(ort(s), Balkenkraefte(0.0, 0.0)) for s in (t.s0, t.s1)]
            continue
        for st in traeger.stuecke:
            nullen = st.V.nullstellen(st.a, st.b) + st.p.nullstellen(st.a, st.b)
            proben += [(ort(t.s0 + s), Balkenkraefte(st.M(s), vz * st.V(s)))
                       for s in _im_teil(st.a, st.b, L / SCHRITTE, nullen)]
    # Gegen die Richtung gesammelt: rückwärts aufsteigend, der Wert links eines Sprungs zuerst.
    if vz < 0.0:
        stuecke.reverse()
        proben.reverse()
    return Verlauf(L, stuecke, proben, sorted(lager, key=lambda x: x.u), [])


def _stellen(z: Zerlegung, fall: Fallergebnis, a: Punkt, e: Punkt) -> Tuple[List[float], List[float]]:
    """
    Längs des Schnitts ab ``a`` in Richtung ``e``, in m: wo sich etwas ändert
    -- an den Grenzen der Feldstreifen und den Enden der Trägerstücke -- und
    wo ein Träger seine grössten Werte hat. Ein Träger zählt nur, wo der
    Schnitt durch seinen Streifen läuft; einer, der quer zum Schnitt trägt,
    ändert sich längs ihm nicht.
    """
    grenzen: List[float] = []
    spitzen: List[float] = []
    for r in z.richtungen:
        quer = geo.skalar(e, r.t)
        if abs(quer) > QUER:
            ta = geo.skalar(a, r.t)
            grenzen += [(tau - ta) / quer for s in z.feldstreifen(r) for tau in (s.von, s.bis)]
    for streifen in z.streifen:
        laengs = geo.skalar(e, streifen.richtung.n)
        von, bis = _im_streifen(streifen, a, e)
        if abs(laengs) <= QUER or von > bis:
            continue
        sa = geo.skalar(a, streifen.richtung.n)
        enden: List[float] = []
        nullen: List[float] = []
        for t in streifen.traeger:
            traeger = fall.traeger.get(t.name)
            for stueck in traeger.stuecke if traeger is not None else ():
                enden += [t.s0 + s for s in (stueck.a, stueck.b)]
                nullen += [t.s0 + s for s in stueck.V.nullstellen(stueck.a, stueck.b)
                           + stueck.p.nullstellen(stueck.a, stueck.b)]
        grenzen += [u for u in ((s - sa) / laengs for s in enden) if von <= u <= bis]
        spitzen += [u for u in ((s - sa) / laengs for s in nullen) if von <= u <= bis]
    return grenzen, spitzen


def _im_streifen(streifen: Streifen, a: Punkt, e: Punkt) -> Tuple[float, float]:
    """Von wo bis wo der Schnitt quer im Streifen liegt, in m ab ``a`` -- ``von > bis``, wenn nirgends."""
    t = streifen.richtung.t
    quer, ta = geo.skalar(e, t), geo.skalar(a, t)
    if abs(quer) <= QUER:
        drin = streifen.von - geo.TOLERANZ <= ta <= streifen.bis + geo.TOLERANZ
        return (-math.inf, math.inf) if drin else (math.inf, -math.inf)
    u0, u1 = sorted(((streifen.von - ta) / quer, (streifen.bis - ta) / quer))
    return u0 - INNEN, u1 + INNEN


def _gerastert(stellen: List[float]) -> List[float]:
    """
    Aufsteigend, und was näher als :data:`~opencivil.decke.geometrie.TOLERANZ`
    bei der vorigen liegt, nicht: der Rand eines Unterzugs ist auch die Grenze
    zweier Feldstreifen, nur in der Rundung verschieden.
    """
    heraus: List[float] = []
    for u in sorted(stellen):
        if not heraus or u - heraus[-1] > geo.TOLERANZ:
            heraus.append(u)
    return heraus


def _im_teil(p: float, q: float, schritt: float, spitzen: List[float]) -> List[float]:
    """
    Die Stellen zwischen zwei Grenzen ``p`` und ``q``: knapp innen an beiden
    Enden, dazwischen höchstens ``schritt`` auseinander und an jeder Spitze
    -- keine, wenn das Stück dafür zu kurz ist.
    """
    if q - p <= 2.0 * INNEN:
        return []
    n = max(1, math.ceil((q - p) / schritt))
    innen = [p + (q - p) * i / n for i in range(1, n)] + [s for s in spitzen if p + INNEN < s < q - INNEN]
    return [p + INNEN, *sorted(set(innen)), q - INNEN]


def _lager(decke: Decke, a: Punkt, b: Punkt, e: Punkt, L: float) -> List[Lagerstelle]:
    """
    Die Lager, die der Schnitt kreuzt, nach ihrer Stelle: ein Linienlager,
    wo er es schneidet -- wer längs eines Lagers schneidet, kreuzt es nicht
    --, eine Stütze, wenn er durch ihren Querschnitt geht, dort, wo er ihrer
    Mitte am nächsten ist.
    """
    heraus: List[Lagerstelle] = []
    for l in decke.linienlager:
        kreuz = geo.kreuzung(a, b, l.a, l.b)
        if kreuz is None:
            continue
        u, k = kreuz
        rand_u = geo.TOLERANZ / L
        rand_k = geo.TOLERANZ / max(math.hypot(l.b[0] - l.a[0], l.b[1] - l.a[1]), geo.TOLERANZ)
        if -rand_u <= u <= 1.0 + rand_u and -rand_k <= k <= 1.0 + rand_k:
            heraus.append(Lagerstelle(min(max(u, 0.0), 1.0) * L, "linienlager", l.name,
                                      l.vertikal, l.eingespannt))
    for st in decke.stuetzen:
        teil = geo.strecke_in_konvex(a, b, geo.achsrechteck(st.ort, st.bx, st.by))
        if teil is not None:
            mitte = geo.skalar((st.ort[0] - a[0], st.ort[1] - a[1]), e)
            heraus.append(Lagerstelle(min(max(mitte, teil[0] * L), teil[1] * L), "stuetze", st.name))
    return sorted(heraus, key=lambda x: x.u)
