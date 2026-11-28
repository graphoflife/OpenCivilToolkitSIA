"""
opencivil/mauerwerk/scheibe.py -- wie die waagrechten Lasten einer Wand zu ihren Pfeilern kommen.

VERANTWORTUNG:
Die Wand als Scheibe unter Lasten in ihrer Ebene (:func:`abtragen`): je
Pfeiler die Querkraft, die Normalkraft, die das Kippen der Wand in ihm
weckt, und das Moment in der Wandebene an seinem Fuss -- in den Abtrag der
lotrechten Lasten (:class:`~opencivil.mauerwerk.lasten.Abtrag`), dazu das
Moment, mit dem diese neben den Mitten der Pfeiler stehen. Die Norm regelt
das nicht; so rechnet das Werkzeug (nach Vorgabe, nicht nachgeschlagen):

- Über den Öffnungen ist die Wand starr: Stürze, Mauerwerk und Decke halten
  dort zusammen. Die waagrechten Lasten greifen an diesem starren Teil an,
  mit ihrem Hebel; tiefer lässt sie
  :func:`~opencivil.mauerwerk.pruefen.lasten_pruefen` nicht zu
  (:func:`starr_ab`).
- Jeder Pfeiler ist am Fuss der Wand eingespannt und oben an den starren
  Teil angeschlossen (:func:`koepfe`): am oberen Rand der höchsten Öffnung
  neben ihm, ohne Öffnung an der Krone. Eine Brüstung zählt nicht.
- Ein Pfeiler wirkt ungerissen mit seiner Steifigkeit auf Biegung,
  E_xd · I, auf Schub, G_d · A / 1.2, und längs, E_xd · A, mit A = b · t_w
  (:func:`steifigkeit`).
- Das Moment M_v der lotrechten Lasten neben den Mitten der Pfeiler gleicht
  der starre Teil aus: er gibt es den Pfeilern nach ihrer Biegesteifigkeit,
  je b³, an den Fuss (:func:`anteile`). Die Normalkräfte des Lastabtrags
  bleiben, und das Gleichgewicht stimmt: ein Weg, den das Mauerwerk gehen
  kann, nicht der einzige.

Steht nur ein Pfeiler da, ist er ein Kragarm: oben dreht er sich frei. Mit
mehreren hält der starre Teil ihre Köpfe gegen das Drehen, soweit sie längs
steif sind: die Wand kippt, und ein Pfeiler wird gedrückt, ein anderer
entlastet. Gerechnet wird das Gleichgewicht des starren Teils mit seinen
drei Bewegungen -- waagrecht, lotrecht, Drehung --, je Pfeiler mit der
Steifigkeit eines Balkens mit Schubverformung, unten eingespannt.

VORZEICHEN:
Kräfte nach rechts und oben positiv, Drehungen im Gegenuhrzeigersinn; die
Normalkraft eines Pfeilers Druck positiv, das Moment an seinem Fuss
positiv, wenn es die Resultierende nach rechts schiebt.

EINHEITEN:
SI: N, m und N·m.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Sequence, Tuple

from opencivil.mauerwerk.lasten import Abtrag
from opencivil.mauerwerk.modell import Oeffnung, Pfeiler, Rechteck, Wandlast
from opencivil.stabwerk.matrix import Profilmatrix, Zerlegung

#: Um so viel ist die Fläche, die auf Schub wirkt, kleiner als A: ein Rechteck, A / 1.2.
SCHUBFLAECHE = 1.2


def starr_ab(flaeche: Rechteck, oeffnungen: Sequence[Oeffnung]) -> float:
    """Ab welcher Höhe die Wand starr ist, in m: über der höchsten Öffnung -- ohne eine ganz."""
    return max((o.rechteck.y1 for o in oeffnungen if o.rechteck is not None), default=flaeche.y0)


def koepfe(flaeche: Rechteck, oeffnungen: Sequence[Oeffnung],
           pfeiler: Sequence[Pfeiler]) -> Dict[str, float]:
    """
    Je Pfeiler die Höhe seines Kopfs, in m: der obere Rand der höchsten
    Öffnung neben ihm -- ohne eine die Krone der Wand.
    """
    oben = {o.name: o.rechteck.y1 for o in oeffnungen if o.rechteck is not None}
    return {p.name: max((oben[n] for n in (*p.links, *p.rechts) if n in oben),
                        default=flaeche.y1) for p in pfeiler}


@dataclass(frozen=True)
class Steifigkeit:
    """
    Ein Pfeiler, unten eingespannt, an seinem Kopf: waagrecht ``uu``,
    waagrecht und gedreht gekoppelt ``up``, gedreht ``pp``, längs ``a``.
    """

    uu: float
    up: float
    pp: float
    a: float


def steifigkeit(b: float, h: float, t: float, E: float, G: float) -> Steifigkeit:
    """Ein Pfeiler ``b`` breit, ``h`` hoch und ``t`` dick -- ein Balken mit Schubverformung."""
    EI = E * t * b ** 3 / 12.0
    phi = 12.0 * EI * SCHUBFLAECHE / (G * b * t * h ** 2)
    return Steifigkeit(uu=12.0 * EI / (h ** 3 * (1.0 + phi)), up=6.0 * EI / (h ** 2 * (1.0 + phi)),
                       pp=(4.0 + phi) * EI / (h * (1.0 + phi)), a=E * b * t / h)


def antworten(pfeiler: Sequence[Pfeiler], koepfe_: Dict[str, float], y0: float,
              lasten: Sequence[Wandlast], E: float, G: float,
              t: float) -> Dict[str, Tuple[float, float, float]]:
    """
    Je Pfeiler ``(V, N, M_z)`` unter den waagrechten Lasten ``lasten`` --
    ``koepfe_`` nach :func:`koepfe`, ``y0`` der Fuss der Wand. Siehe Dateikopf.
    """
    # Bezogen auf die Mitte der Pfeiler am Fuss: u = U − Θ · a, w = W + Θ · c.
    x_r = sum((p.x0 + p.x1) / 2.0 for p in pfeiler) / len(pfeiler)
    K = Profilmatrix(3, [0, 0, 0])
    teile = []
    for p in pfeiler:
        a, c = koepfe_[p.name] - y0, (p.x0 + p.x1) / 2.0 - x_r
        k = steifigkeit(p.b, a, t, E, G)
        K.addiere_block((0, 1, 2), ((k.uu, 0.0, k.up - a * k.uu),
                                    (0.0, k.a, c * k.a),
                                    (k.up - a * k.uu, c * k.a,
                                     k.pp - 2.0 * a * k.up + a * a * k.uu + c * c * k.a)))
        teile.append((p.name, a, c, k))
    zerlegung = Zerlegung(K)
    if zerlegung.singulaer:
        raise ArithmeticError("Die Pfeiler halten die Wand nicht -- jeder ist steif, das kann "
                              "nicht sein.")
    U, W, Theta = zerlegung.loese([sum(l.H for l in lasten), 0.0,
                                   -sum(l.H * (l.y - y0) for l in lasten)])
    ergebnis = {}
    for name, a, c, k in teile:
        u, w = U - Theta * a, W + Theta * c
        V, M = k.uu * u + k.up * Theta, k.up * u + k.pp * Theta
        ergebnis[name] = (V, -k.a * w, a * V - M)
    return ergebnis


def anteile(pfeiler: Sequence[Pfeiler]) -> Dict[str, float]:
    """Je Pfeiler sein Anteil am Moment M_v: b³ durch die Summe -- siehe Dateikopf."""
    summe = sum(p.b ** 3 for p in pfeiler)
    return {p.name: p.b ** 3 / summe for p in pfeiler}


def abtragen(abtrag: Abtrag, flaeche: Rechteck, oeffnungen: Sequence[Oeffnung],
             pfeiler: Sequence[Pfeiler], lasten: Sequence[Wandlast], E: float, G: float,
             t: float) -> None:
    """
    In ``abtrag``, was die Scheibe den Pfeilern gibt: ihren Anteil an M_v
    und was die waagrechten unter ``lasten`` bewirken -- deren Normalkraft
    zählt am Kopf wie am Fuss. ``E`` und ``G`` sind E_xd und G_d der Wand in
    N/m², ``t`` ihre Dicke in m.
    """
    if not pfeiler:
        return
    for name, anteil in anteile(pfeiler).items():
        abtrag.M_z[name] += anteil * abtrag.M_v
    schieben = [last for last in lasten if last.H]
    if not schieben:
        return
    for name, (V, N, M_z) in antworten(pfeiler, koepfe(flaeche, oeffnungen, pfeiler), flaeche.y0,
                                       schieben, E, G, t).items():
        abtrag.V[name] += V
        abtrag.N[name] += N
        abtrag.N_L[name] += N
        abtrag.N_H[name] += N
        abtrag.M_z[name] += M_z
