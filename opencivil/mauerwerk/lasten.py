"""
opencivil/mauerwerk/lasten.py -- wie die Lasten einer Wand zu ihren Pfeilern kommen.

VERANTWORTUNG:
Die lotrechten Lasten einer Wand -- Linien- und Punktlasten mit ihrer
Ausmitte quer zur Wand, dazu ihr Eigengewicht -- je Lastfall auf Pfeiler und
Stürze verteilt (:func:`abtragen`): je Pfeiler die Normalkraft an seinem Fuss,
die der Lasten allein und das Moment ihrer Ausmitten an seinem Kopf; je
Sturzauflager seine Kraft; und wie weit die Lasten in der Ebene der Wand
neben den Mitten der Pfeiler stehen, als ein Moment. Was in der Ebene der
Wand daraus wird und was die waagrechten Lasten dazugeben, rechnet
:mod:`~opencivil.mauerwerk.scheibe` in denselben Abtrag. Die Querlasten
stehen dort als zwei Zahlen je m² Wand: die von Hand mit ihrer Richtung, die
des Erdbebens als Betrag, denn sie wirkt in beiden.
Eine Kombination summiert die Lastfälle mit ihren Beiwerten
(:func:`kombinieren`). Die Norm regelt das nicht; so rechnet das Werkzeug
(nach Vorgabe, nicht nachgeschlagen):

- Was über einem Pfeiler liegt, trägt er -- auch sein eigenes Gewicht.
- Was über einer Öffnung liegt, trägt ihr Sturz: was über einem seiner
  Auflager liegt, ganz dieses; was über der Öffnung liegt, teilt er als
  einfacher Balken zwischen den Mitten seiner Auflager. Die Kraft eines
  Auflagers geht weiter nach unten, in den Pfeiler darunter oder auf den
  nächsten Sturz.
- Was unter einer Öffnung liegt, etwa eine Brüstung, geht neben den
  Pfeilern in den Fuss der Wand.
- Das Eigengewicht ist ρ · g · t_w je m² Wand, mit g = 10 m/s² wie überall
  im Werkzeug; ein Sturz wiegt wie Mauerwerk.
- Eine Last wirkt mit ihrer Ausmitte am Kopf der Pfeiler, die sie trägt,
  wo sie auch liegt; das Eigengewicht mittig. Die Ausmitte am Kopf ist
  darum die der Lasten allein, M / N_L: das Eigengewicht, das erst darunter
  dazukommt, verkleinert sie nicht.
- In der Ebene der Wand erreicht eine Last den Pfeiler, wo sie über ihm
  liegt, von einem Sturz in der Mitte seines Auflagers: ihr Hebel zur
  Mitte des Pfeilers, über alle Pfeiler summiert, ist das Moment M_v.

Die Lasten selbst beschreibt :mod:`~opencivil.mauerwerk.modell`.

EINHEITEN:
SI: N, m und N·m; Druck positiv.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.mauerwerk.modell import TOLERANZ, Oeffnung, Pfeiler, Rechteck, Wandlast

#: Die beiden Auflager eines Sturzes.
SEITEN = ("links", "rechts")


@dataclass
class Abtrag:
    """
    Was ein Fall den Pfeilern und Stürzen gibt: je Pfeiler die Normalkraft
    am Fuss ``N``, die der Lasten allein ``N_L`` und das Moment ihrer
    Ausmitten ``M``; je Sturzauflager ``(Öffnung, Seite)`` die Kraft ``R``,
    und was neben den Pfeilern in den Fuss geht (``unten``). In der Ebene
    der Wand ``M_v``, wie weit die Lasten neben den Mitten der Pfeiler
    stehen, und je Pfeiler die Querkraft ``V``, nach rechts positiv, was die
    waagrechten Lasten zu seiner Normalkraft geben, ``N_H`` -- schon in
    ``N`` und ``N_L`` --, und das Moment an seinem Fuss ``M_z``. Beide
    Momente sind positiv, wenn sie die Resultierende nach rechts schieben.
    Quer zur Wand je m² ``p``, von Hand, positiv zur Seite, von der aus man
    die Ansicht sieht, und ``p_E`` aus dem Erdbeben, ein Betrag.
    """

    N: Dict[str, float] = field(default_factory=dict)
    N_L: Dict[str, float] = field(default_factory=dict)
    M: Dict[str, float] = field(default_factory=dict)
    R: Dict[Tuple[str, str], float] = field(default_factory=dict)
    unten: float = 0.0
    M_v: float = 0.0
    V: Dict[str, float] = field(default_factory=dict)
    N_H: Dict[str, float] = field(default_factory=dict)
    M_z: Dict[str, float] = field(default_factory=dict)
    p: float = 0.0
    p_E: float = 0.0

    def je_pfeiler(self) -> Tuple[Dict[str, float], ...]:
        """Was je Pfeiler eine Zahl hat -- die eine Liste, die :func:`kombinieren` summiert."""
        return self.N, self.N_L, self.M, self.V, self.N_H, self.M_z


def leer(pfeiler: Sequence[Pfeiler], oeffnungen: Sequence[Oeffnung]) -> Abtrag:
    """Ein Abtrag ohne Last: je Pfeiler und Auflager eine Null, damit jeder dasteht."""
    abtrag = Abtrag(R={(o.name, s): 0.0 for o in oeffnungen if o.rechteck is not None
                       for s in SEITEN})
    for je_pfeiler in abtrag.je_pfeiler():
        je_pfeiler.update((p.name, 0.0) for p in pfeiler)
    return abtrag


def kombinieren(name_faktoren: Mapping[str, float], je_fall: Mapping[str, Abtrag],
                pfeiler: Sequence[Pfeiler], oeffnungen: Sequence[Oeffnung]) -> Abtrag:
    """Die Summe der Lastfälle mit ihren Beiwerten -- ``je_fall`` nach dem Namen des Lastfalls."""
    summe = leer(pfeiler, oeffnungen)
    for fall, beiwert in name_faktoren.items():
        a = je_fall.get(fall)
        if a is None or beiwert == 0.0:
            continue
        for je_pfeiler, dazu in zip(summe.je_pfeiler(), a.je_pfeiler()):
            for k, v in dazu.items():
                je_pfeiler[k] = je_pfeiler.get(k, 0.0) + beiwert * v
        for k, v in a.R.items():
            summe.R[k] = summe.R.get(k, 0.0) + beiwert * v
        summe.unten += beiwert * a.unten
        summe.M_v += beiwert * a.M_v
        summe.p += beiwert * a.p
        # Das Erdbeben wirkt in beiden Richtungen: ein negativer Beiwert dreht es nur.
        summe.p_E += abs(beiwert) * a.p_E
    return summe


class _Wand:
    """Die Wand, wie der Abtrag sie braucht: ihre Pfeiler und die Stürze über den Öffnungen."""

    def __init__(self, flaeche: Rechteck, oeffnungen: Sequence[Oeffnung],
                 pfeiler: Sequence[Pfeiler]) -> None:
        self.flaeche = flaeche
        self.pfeiler = list(pfeiler)
        self.stuerze = [(o, o.rechteck) for o in oeffnungen if o.rechteck is not None]
        grenzen = {flaeche.x0, flaeche.x1}
        for o, r in self.stuerze:
            grenzen |= {r.x0, r.x1, r.x0 - o.a, r.x1 + o.a}
        self.grenzen = sorted(x for x in grenzen
                              if flaeche.x0 - TOLERANZ <= x <= flaeche.x1 + TOLERANZ)
        """Wo sich zwischen Wandenden, Öffnungen und Stürzen etwas ändert, von links nach rechts."""

    def sturz_unter(self, x0: float, x1: float, y: float) -> Optional[Tuple[Oeffnung, Rechteck]]:
        """Der höchste Sturz unter ``y``, der von ``x0`` bis ``x1`` ganz durchgeht, oder keiner."""
        unter = [(o, r) for o, r in self.stuerze if r.y1 <= y + TOLERANZ
                 and r.x0 - o.a - TOLERANZ <= x0 and x1 <= r.x1 + o.a + TOLERANZ]
        return max(unter, key=lambda e: e[1].y1, default=None)

    def pfeiler_bei(self, x0: float, x1: float) -> Optional[Pfeiler]:
        return next((p for p in self.pfeiler
                     if p.x0 - TOLERANZ <= x0 and x1 <= p.x1 + TOLERANZ), None)

    def stuecke(self, last: Wandlast) -> List[Wandlast]:
        """Eine Last, geteilt an den Grenzen -- jedes Stück liegt ganz über einem Teil der Wand."""
        laenge = last.x1 - last.x0
        if laenge <= TOLERANZ:
            return [last]
        teile = [last.x0, *(x for x in self.grenzen if last.x0 + TOLERANZ < x < last.x1 - TOLERANZ),
                 last.x1]
        return [Wandlast(last.name, a, b, last.y, last.Q * (b - a) / laenge, last.e)
                for a, b in zip(teile, teile[1:])]

    def mauerwerk(self, je_m2: float) -> List[Wandlast]:
        """
        Das Eigengewicht, in Stücken: je Streifen zwischen den Grenzen das
        Mauerwerk zwischen Öffnungen und Sturzunterkanten, jedes als Last an
        seiner Unterkante.
        """
        heraus = []
        for a, b in zip(self.grenzen, self.grenzen[1:]):
            mitte = (a + b) / 2
            offen = [r for _, r in self.stuerze if r.x0 < mitte < r.x1]
            hoehen = {self.flaeche.y0, self.flaeche.y1}
            hoehen |= {y for r in offen for y in (r.y0, r.y1)}
            hoehen |= {r.y1 for o, r in self.stuerze if r.x0 - o.a < mitte < r.x1 + o.a}
            stufen = sorted(y for y in hoehen if self.flaeche.y0 <= y <= self.flaeche.y1)
            for unten, oben in zip(stufen, stufen[1:]):
                if any(r.y0 - TOLERANZ <= unten and oben <= r.y1 + TOLERANZ for r in offen):
                    continue
                heraus.append(Wandlast("Eigengewicht", a, b, unten,
                                       je_m2 * (b - a) * (oben - unten)))
        return heraus


def abtragen(flaeche: Rechteck, oeffnungen: Sequence[Oeffnung], pfeiler: Sequence[Pfeiler],
             lasten: Sequence[Wandlast], eigengewicht: float = 0.0) -> Abtrag:
    """
    Die Lasten eines Lastfalls auf Pfeiler und Stürze -- ``eigengewicht`` in
    N/m² der Wand, null ohne. Siehe Dateikopf.
    """
    wand = _Wand(flaeche, oeffnungen, pfeiler)
    abtrag = leer(pfeiler, oeffnungen)

    def verteilen(x0: float, x1: float, y: float, Q: float, e: float, last: bool) -> None:
        """``last``: eine Last, nicht das Eigengewicht -- sie zählt auch am Kopf."""
        treffer = wand.sturz_unter(x0, x1, y)
        if treffer is None:
            p = wand.pfeiler_bei(x0, x1)
            if p is None:
                abtrag.unten += Q
            else:
                abtrag.N[p.name] += Q
                abtrag.M_v += Q * ((x0 + x1) - (p.x0 + p.x1)) / 2
                if last:
                    abtrag.N_L[p.name] += Q
                    abtrag.M[p.name] += Q * e
            return
        o, r = treffer
        x_l, x_r = r.x0 - o.a / 2, r.x1 + o.a / 2
        if x1 <= r.x0 + TOLERANZ:
            links = Q
        elif x0 >= r.x1 - TOLERANZ:
            links = 0.0
        else:
            links = Q * (x_r - (x0 + x1) / 2) / (x_r - x_l)
        for seite, x, R in (("links", x_l, links), ("rechts", x_r, Q - links)):
            if R == 0.0:
                continue
            abtrag.R[(o.name, seite)] += R
            # Unter der Unterkante des Sturzes weiter: nicht noch einmal auf ihn selbst.
            verteilen(x, x, r.y1 - 2 * TOLERANZ, R, e, last)

    for s in (s for last in lasten for s in wand.stuecke(last)):
        verteilen(s.x0, s.x1, s.y, s.Q, s.e, True)
    for s in (wand.mauerwerk(eigengewicht) if eigengewicht else []):
        verteilen(s.x0, s.x1, s.y, s.Q, 0.0, False)
    return abtrag
