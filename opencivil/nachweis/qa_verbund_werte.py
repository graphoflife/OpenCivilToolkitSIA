"""
opencivil/nachweis/qa_verbund_werte.py -- was Kennzahlen und Nachweise im Verbund teilen.

VERANTWORTUNG:
Die Kennzahlen (:mod:`opencivil.nachweis.qa_verbund_kennzahlen`) und die
Nachweise je Lastfall (:mod:`opencivil.nachweis.qa_verbund`) lesen dieselben
Festigkeiten und schreiben dieselben Tabellen; beides steht hier, je einmal:

* je Gruppe die Festigkeit gezogen und gedrueckt (:class:`Verbundwerte`);
* die Tabelle dieser Festigkeiten mit ihrem Ansatz (:func:`festigkeiten`);
* die Tabelle der Bleche mit ihren Klassen (:func:`klassen`);
* ``β`` nach 5.1.2.2 mit ``x_p`` und ``h`` (:func:`beta`).

DIE FESTIGKEITEN (SIA 264:2014, 4.1.3 und 5.1.2.1):
Baustahl ``f_y/γ_a`` gezogen und gedrueckt, je Dicke wie im Stahl
(:class:`~opencivil.nachweis.qa_stahl_werte.Stahlwerte`); ``γ_a`` ist
``γ_M1`` des Baustahls -- 4.1.5 nennt 1.05, wie SIA 263. Beton gedrueckt
``0.85 η_fc f_ck/γ_c`` mit ``η_fc = 1`` und ohne ``η_t``, also nicht ``f_cd``
der SIA 262; gezogen nichts (4.3.2.1). Betonstahl ``f_sd`` seines Materials,
gedrueckt mit dem Wert fuer Druck.

BEMESSUNG ODER CHARAKTERISTISCH:
Wie beim Stahl je Material der Wertesatz, den die Tragsicherheit waehlt:
charakteristisch ohne ``γ``, der Beton dann mit ``0.85 f_ck``. Die
Widerstaende heissen in beiden Faellen ``Rd`` (nach Vorgabe, nicht
nachgeschlagen).
"""

from __future__ import annotations

import math
from functools import cached_property
from typing import List, Optional, Sequence, Tuple

from opencivil.core.berechnung import Eingabebezug, Eingaben
from opencivil.core.latex import Mathe, fest
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.material.basis import Baustoffart
from opencivil.nachweis.qa_stahl_werte import KENNWERTE, Stahlwerte
from opencivil.querschnitt.gesetzwahl import Rechenwahl, Werkstoffsatz
from opencivil.stahlbau.querschnitt import Blechzustand, Teil
from opencivil.stahlprofile.bleche import Halterung
from opencivil.verbund import widerstand as vw
from opencivil.verbund.querschnitt import Verbundquerschnitt

REFERENZ_FESTIGKEIT = "SIA 264:2014, 4.1.3, (1); 4.1.5; 4.3.2.1; 5.1.2.1"

#: Der Umrechnungsfaktor der Betondruckfestigkeit im plastischen Widerstand (5.1.2.1).
BETON_FAKTOR = 0.85

#: Was je Material gelesen wird, nach seiner Art.
_KENNWERTE = {
    Baustoffart.BAUSTAHL: KENNWERTE,
    Baustoffart.BETON: ("f_ck", "gamma_c"),
    Baustoffart.BETONSTAHL: ("f_yk", "f_yk_druck", "gamma_s", "f_yd", "f_yd_druck"),
}

#: Der Beiwert je Art -- beim Baustahl ``γ_M1``, im Verbund ``γ_a`` genannt.
_GAMMA = {Baustoffart.BAUSTAHL: "gamma_M1", Baustoffart.BETON: "gamma_c",
          Baustoffart.BETONSTAHL: "gamma_s"}

#: Je Art der Teil des Ansatzes, mit und ohne Beiwert.
_ANSATZ = {
    Baustoffart.BAUSTAHL: (r"f_{yd} = \frac{f_y}{\gamma_a}", r"f_{yd} = f_y"),
    Baustoffart.BETON: (r"0.85\, f_{cd} = 0.85\, \frac{\eta_{fc}\, f_{ck}}{\gamma_c},\ "
                        r"\eta_{fc} = 1", r"0.85\, f_{ck}"),
    Baustoffart.BETONSTAHL: (r"f_{sd} = \frac{f_{sk}}{\gamma_s}", r"f_{sd} = f_{sk}"),
}

SPANNUNG = r"\ [\mathrm{N}/\mathrm{mm}^2]"

#: Wie die Formel mit ``β`` in der Formelsammlung heisst -- in den Kennzahlen und je Lastfall.
MIT_BETA = "Plastischer Biegewiderstand mit β"


def stoffbezuege(verbund: Verbundquerschnitt) -> List[Eingabebezug]:
    """Die Kennwerte aller Materialien des Querschnitts, als Eingaben."""
    stoffe = {g.stoff.id: g.stoff for g in verbund.gruppen}.values()
    return [stoff.bezug(k) for stoff in stoffe for k in _KENNWERTE[stoff.art]]


class Verbundwerte:
    """Die Festigkeiten der Gruppen eines Verbundquerschnitts -- siehe Dateikopf."""

    def __init__(self, verbund: Verbundquerschnitt, e: Eingaben, wahl: Rechenwahl) -> None:
        self.verbund = verbund
        self.e = e
        self.stahl = Stahlwerte(verbund.stahl, e, wahl)
        self.bemessung = [wahl.satz(g.stoff) is Werkstoffsatz.BEMESSUNG for g in verbund.gruppen]

    def zahl(self, g: int, kurz: str) -> float:
        """Ein Kennwert des Materials der Gruppe ``g``: Spannungen in N/mm², Beiwerte rein."""
        stoff = self.verbund.gruppen[g].stoff
        si = self.e[stoff.eingabename(kurz)].groesse.si
        return si if kurz.startswith("gamma") else si / 1e6

    def gamma(self, g: int) -> float:
        """Der Beiwert der Gruppe ``g`` -- eins mit charakteristischen Werten."""
        return self.zahl(g, _GAMMA[self.verbund.art(g)]) if self.bemessung[g] else 1.0

    def kennwert(self, g: int) -> float:
        """Die charakteristische Festigkeit: ``f_y`` in der Dicke der Gruppe, ``f_ck``, ``f_sk``."""
        art = self.verbund.art(g)
        if art is Baustoffart.BAUSTAHL:
            return self.stahl.zahl(g, "f_y")
        return self.zahl(g, "f_ck" if art is Baustoffart.BETON else "f_yk")

    @cached_property
    def festigkeiten(self) -> List[Tuple[float, float]]:
        """Je Gruppe ``(zug, druck)`` in N/mm² -- siehe Dateikopf."""
        werte = []
        for g in range(len(self.verbund.gruppen)):
            art = self.verbund.art(g)
            if art is Baustoffart.BAUSTAHL:
                werte.append((self.stahl.f[g], self.stahl.f[g]))
            elif art is Baustoffart.BETON:
                werte.append((0.0, BETON_FAKTOR * self.zahl(g, "f_ck") / self.gamma(g)))
            else:
                zug, druck = ("f_yd", "f_yd_druck") if self.bemessung[g] else ("f_yk", "f_yk_druck")
                werte.append((self.zahl(g, zug), self.zahl(g, druck)))
        return werte

    @property
    def zug(self) -> List[float]:
        return [z for z, _ in self.festigkeiten]

    @property
    def druck(self) -> List[float]:
        return [d for _, d in self.festigkeiten]

    @property
    def eps(self) -> List[float]:
        """Je Gruppe des Stahls ``ε``."""
        return self.stahl.eps

    @cached_property
    def hochfest(self) -> bool:
        """Ob ein Baustahl S420 oder S460 ist (:data:`~opencivil.verbund.widerstand.HOCHFEST`)."""
        return any(self.zahl(g, "f_y") >= vw.HOCHFEST
                   for g in self.verbund.gruppen_der(Baustoffart.BAUSTAHL))

    def kurz(self) -> str:
        """Die Festigkeiten in einem Satz, fuer die Nachweise: sie stehen in den Kennzahlen."""
        teile = []
        for g, (zug, druck) in enumerate(self.festigkeiten):
            name = self.verbund.gruppen[g].name
            teile.append(f"{name} gedrückt {druck:.1f} N/mm²" if zug == 0.0 else
                         f"{name} {zug:.1f} N/mm²" if zug == druck else
                         f"{name} gezogen {zug:.1f}, gedrückt {druck:.1f} N/mm²")
        return "Festigkeiten wie in den Kennzahlen: " + ", ".join(teile) + "."


def festigkeiten(p: Protokoll, werte: Verbundwerte) -> None:
    """Die Festigkeiten je Gruppe als Tabelle, mit dem Ansatz fuer die Arten, die vorkommen."""
    verbund = werte.verbund
    teile = []
    for art in (Baustoffart.BAUSTAHL, Baustoffart.BETON, Baustoffart.BETONSTAHL):
        gruppen = verbund.gruppen_der(art)
        if gruppen:
            mit, ohne = _ANSATZ[art]
            teile.append(mit if any(werte.bemessung[g] for g in gruppen) else ohne)
    p.ansatz(r" \qquad ".join(teile),
             titel="Festigkeiten im plastischen Zustand – der Beton nur gedrückt",
             referenz=REFERENZ_FESTIGKEIT, name="Festigkeiten im Verbundquerschnitt")
    p.tabelle(
        kopf=["Werkstoff", "Art", Mathe(r"f_k" + SPANNUNG), Mathe(r"\gamma"),
              Mathe(r"\text{gezogen}" + SPANNUNG), Mathe(r"\text{gedrückt}" + SPANNUNG)],
        zeilen=[[gruppe.name, verbund.art(g).beschriftung, Mathe(fest(werte.kennwert(g), 0)),
                 Mathe(fest(werte.gamma(g), 2)), Mathe(fest(zug, 1)), Mathe(fest(druck, 1))]
                for g, (gruppe, (zug, druck)) in enumerate(zip(verbund.gruppen,
                                                               werte.festigkeiten))],
        titel="Festigkeiten je Werkstoff", ausrichtung="llrrrr")
    p.text("f_k ist f_y in der Dicke der Gruppe, f_ck oder f_sk; γ ist γ_a = γ_M1 des "
           "Baustahls, γ_c oder γ_s.")
    ohne = [g.name for g, b in zip(verbund.gruppen, werte.bemessung) if not b]
    if ohne:
        p.text(f"Mit charakteristischen Werten, ohne γ: {', '.join(ohne)} – so wählt es die "
               f"Tragsicherheit.")


def klassen(p: Protokoll, zustaende: Sequence[Blechzustand], freie: Sequence[Teil],
            titel: str) -> Tuple[int, str]:
    """
    Ob jedes Blech in Klasse 1 oder 2 liegt, als Tabelle -- und die Klasse
    des Querschnitts, die unguenstigste, mit dem Namen dessen, was sie
    bestimmt (ohne Namen in Klasse 1). 3 heisst «über 2»; gedrueckte freie
    Flaechen zaehlen so.
    """
    if zustaende:
        p.tabelle(
            kopf=["Blech", "Grenzen nach", Mathe(r"c/t"), Mathe(r"\alpha"),
                  Mathe(r"\text{Grenzen}\ 1 / 2"), "Klasse"],
            zeilen=[_zeile(z) for z in zustaende], titel=titel, ausrichtung="llrrrr")
    kandidaten = ([(z.klasse, z.name) for z in zustaende]
                  + [(3, f"«{f.flaeche.name}»") for f in freie])
    klasse = max((k for k, _ in kandidaten), default=1)
    wer = next((name for k, name in kandidaten if k == klasse), "") if klasse > 1 else ""
    if freie:
        p.text("Gedrückt und frei gezeichnet: " + ", ".join(f"«{f.flaeche.name}»" for f in freie)
               + " – wie sie gehalten sind, weiss das Werkzeug nicht: über Klasse 2.")
    return klasse, wer


def klasse_text(klasse: int) -> str:
    """Eine Klasse im Verbund: 1, 2 oder «über 2»."""
    return "über 2" if klasse > 2 else f"{klasse}"


def _zeile(z: Blechzustand) -> List:
    rohr = z.blech.halterung is Halterung.ROHR
    tabelle = z.tabelle or f"SIA 263, {z.blech.halterung.tabelle}" + (", D/t" if rohr else "")
    return [z.name, tabelle,
            Mathe(rf"{fest(z.blech.c, 1)}/{fest(z.blech.t, 1)} = {fest(z.schlankheit, 1)}"),
            Mathe("–" if rohr else fest(z.alpha, 2)),
            Mathe(" / ".join("–" if math.isinf(g) else fest(g, 1) for g in z.grenzen.werte[:2])),
            klasse_text(z.klasse)]


def beta(p: Protokoll, werte: Zwischenwerte, b: vw.Beta) -> Optional[Wert]:
    """
    ``β`` nach 5.1.2.2 an einer Nulllinie, mit ``x_p`` und ``h`` -- ``None``,
    wo es eins ist und nichts mindert. Ueber 0.4 rechnet der Fall nicht
    (:data:`~opencivil.verbund.widerstand.UEBER_FIGUR_1`) und kommt nicht
    hierher.
    """
    if b.verhaeltnis <= vw.BETA_AB:
        p.text(f"Ein Baustahl ist S420 oder S460, aber x_p/h = {b.x_p:.1f}/{b.h:.1f} = "
               f"{b.verhaeltnis:.3f} ≤ {vw.BETA_AB:g}: β = 1.")
        return None
    x_p = werte.laenge("x_p", "x_p", b.x_p * 1e-3,
                       "Abstand der Nulllinie vom gedrückten Rand des Betons")
    h = werte.laenge("h", "h", b.h * 1e-3, "Höhe des Querschnitts quer zur Nulllinie")
    wert = werte.zahl("beta", r"\beta", b.beta, "Abminderungsbeiwert für S420 und S460")
    p.formel(wert, rf"1 - {1.0 - vw.BETA_ENDE:g} \cdot \frac{{@x_p / @h - {vw.BETA_AB:g}}}"
                   rf"{{{vw.BETA_BIS:g} - {vw.BETA_AB:g}}}", {"x_p": x_p, "h": h},
             titel=f"Abminderung für S420 und S460, x_p/h über {vw.BETA_AB:g}",
             referenz=vw.REFERENZ_BETA, name="Abminderungsbeiwert β nach Figur 1")
    return wert
