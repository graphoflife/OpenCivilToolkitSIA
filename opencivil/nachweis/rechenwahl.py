"""
opencivil/nachweis/rechenwahl.py -- womit ein Kapitel rechnet.

VERANTWORTUNG:
Was ein Nachweis-Kapitel aus seiner Wahl macht -- der Kriechzahl, dem
Wertesatz und der Rechenart (:mod:`opencivil.querschnitt.gesetzwahl`): die
eine Stelle, die daraus die Werkstoffgesetze, die Bewehrungslagen und den
Querschnitt der Platte samt Loeser baut, und welche Rechenarten ein Kapitel
anbietet. Die
Kapitel der Platte und die Spannung-Dehnung-Analyse fragen hier, keines baut
seine Gesetze oder Lagen selbst.

JE MATERIAL SEIN WERTESATZ:
Ein Kapitel waehlt den Wertesatz je Baustoff
(:class:`~opencivil.querschnitt.gesetzwahl.Wertesaetze`): der Beton liest
``f_cd`` oder ``f_ck`` nach seinem, jeder Stahl ``f_yd`` oder ``f_yk``
nach seinem (Benutzer, 2026-11-20). Die Herleitung nennt ihn einmal, wenn
alle denselben haben, sonst je Baustoff (:func:`protokoll_rechenwahl`).

JEDE LAGE MIT IHREM STAHL:
Der Editor laesst je Seite einen eigenen Stahl waehlen. Jede Lage traegt
darum ihren Stahl (:class:`Stahllage`), angemeldet wird je Sorte unter
``{kennwert}__{sorte}`` (:func:`lagenbezuege`,
:meth:`~opencivil.material.basis.Baustoff.eingabename`), gebaut von
:func:`stahllagen`. Bis 2026-10-12 nahmen Stahlspannung, Knicken, Querkraft
und Analyse den Stahl der ersten Lage fuer alle.

WER WAS ANBIETET:
Die Handrechnung gibt es nur, wo ein Polygon aus Eckpunkten Sinn ergibt: in
der Tragsicherheit und bei den Stahlspannungen. Beim Knicken und in den
Spannung-Dehnung-Analysen wird die Normalkraft genau gerechnet, Ebene fuer
Ebene -- dort waere die Handrechnung nur der Spannungsblock mit
weggelassener Druckbewehrung, also eine schlechtere 0.85·x-Vereinfachung
(:data:`FASERARTEN`). Der gezeichnete Querschnitt rechnet immer ueber die
Fasern: auch seine Stahlspannungen bieten darum keine Handrechnung an. Bis
2026-11-25 boten die Stahlspannungen dazu «elastisch» an
(:mod:`opencivil.querschnitt.gesetzwahl`).

Die Verformung beim Knicken rechnet nur praezise (:data:`VERFORMUNGSARTEN`,
Benutzer, 2026-10-15). Mit dem Spannungsblock hat das Moment ueber der
Kruemmung flache Stuecke: dort traegt jede Kruemmung dasselbe Moment, die
Ausmitte zweiter Ordnung ist nicht eindeutig, und nahe der Grenzkraft hing
N_Rd davon ab, wie gesucht wurde -- an der Stuetze des Pruefprojekts
4099.5 kN halbiert, 4200 kN mit Warmstart.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Dict, List, Sequence, Tuple

from opencivil.core.berechnung import Eingabebezug, Eingaben
from opencivil.core.latex import als_text, angabe
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.suche import HALBIEREN, Suche
from opencivil.core.wert import Wert, kennung_aus
from opencivil.material.basis import Baustoffart
from opencivil.nachweis.querschnittsloeser import (
    Faserloeser, Stahllage, je_seite, protokoll_wirksamer_modul, wirksamer_modul_wert,
)
from opencivil.querschnitt.analyse import Querschnittsanalyse
from opencivil.querschnitt.fasern import FASERN
from opencivil.querschnitt.gesetzwahl import Rechenart, Rechenwahl, Werkstoffsatz, betongesetz
from opencivil.querschnitt.interaktion import Bewehrung, Querschnitt, Teil, Werkstoff
from opencivil.querschnitt.lagenaufbau import Postenbezug
from opencivil.querschnitt.werkstoffgesetz import Gesetz, Stahlgesetz, StahlNurZug
from opencivil.querschnitt.zugseite import Zugseite


#: Was die Tragsicherheit anbietet.
RECHENARTEN = (Rechenart.HANDRECHNUNG, Rechenart.BLOCK, Rechenart.PARABEL)

#: Was das Knicken und die Spannung-Dehnung-Analysen anbieten: nur, was ueber
#: die Fasern rechnet -- siehe «Wer was anbietet» oben.
FASERARTEN = (Rechenart.BLOCK, Rechenart.PARABEL)

#: Was die Verformung beim Knicken anbietet: nur praezise -- siehe «Wer was
#: anbietet» oben.
VERFORMUNGSARTEN = (Rechenart.PARABEL,)


# ===========================================================================
# Die Gesetze zu einer Wahl
# ===========================================================================


@dataclass(frozen=True)
class Betonkennwerte:
    """
    Die Zahlen, aus denen das Betongesetz entsteht -- SI, im Wertesatz des
    Betons. Den Stahl traegt jede Lage selbst (:func:`stahllagen`).
    """

    f_c: float
    """``f_cd`` oder ``f_ck``."""

    E_c: float
    """Der Modul der Wahl, ohne Kriechen: ``E_cm``, beim Knicken ``E_cd``."""

    eps_c1d: float
    eps_c2d: float

    name: str = ""
    """Der Name des Betons («C30/37») -- so heissen die Grenzen seiner Dehnung."""

    @classmethod
    def aus_eingaben(cls, e: Eingaben, wahl: Rechenwahl, beton) -> "Betonkennwerte":
        """Aus den Eingaben, die :func:`betonbezuege` fuer ``beton`` anmeldet."""
        return cls(f_c=e.g(wahl.satz(beton).beton).si, E_c=e.g(wahl.modul).si,
                   eps_c1d=e.g("eps_c1d").si, eps_c2d=e.g("eps_c2d").si, name=beton.name)


def betonbezuege(satz: Werkstoffsatz, beton, *, modul: str = "E_cm") -> List[Eingabebezug]:
    """
    Was das Betongesetz einer Wahl braucht -- unter den Kurznamen des
    Wertesatzes dieses Betons, ``f_cd`` oder ``f_ck``, und des Moduls der Wahl
    (:attr:`~opencivil.querschnitt.gesetzwahl.Rechenwahl.modul`). So steht in
    der Herleitung das Zeichen, mit dem gerechnet wird. Die Reihenfolge ist
    die, in der die Werte in der Herleitung der Baustoffe erscheinen.
    """
    return [
        Eingabebezug(satz.beton, beton.id_von(satz.beton)),
        Eingabebezug("eps_c1d", beton.id_von("eps_c1d")),
        Eingabebezug("eps_c2d", beton.id_von("eps_c2d")),
        Eingabebezug(modul, beton.id_von(modul)),
    ]


def staehle(posten: Sequence[Postenbezug]) -> List:
    """Die Staehle der Posten, jeder einmal, in der Reihenfolge der Posten."""
    return list({q.lage.stahl.id: q.lage.stahl for q in posten}.values())


def stahlbezuege(posten: Sequence[Postenbezug], kennwerte: Sequence[str]) -> List[Eingabebezug]:
    """Je Stahl der Posten diese Kennwerte, unter seinem :meth:`~opencivil.material.basis.Baustoff.eingabename`."""
    return [stahl.bezug(kennwert) for stahl in staehle(posten) for kennwert in kennwerte]


def lagenbezuege(posten: Sequence[Postenbezug], wahl: Rechenwahl) -> List[Eingabebezug]:
    """
    Was :func:`stahllagen` liest: je Posten Flaeche und Tiefe, je Stahl
    seine Kennwerte in seinem Wertesatz.
    """
    bezuege = [b for q in posten for b in q.bezuege("a_s", "z")]
    return bezuege + [stahl.bezug(kennwert) for stahl in staehle(posten)
                      for kennwert in ("E_s", wahl.satz(stahl).stahl,
                                       wahl.satz(stahl).stahl_druck, "eps_ud")]


def stahllagen(posten: Sequence[Postenbezug], wahl: Rechenwahl,
               wert: Callable[[str], float]) -> List[Stahllage]:
    """
    Je Bewehrungsposten eine Lage, mit dem Stahl ihrer Lage in dessen
    Wertesatz -- die eine Stelle, die Lagen baut.

    ``wert`` liefert zu einer Wert-ID die Zahl in SI: in einem Nachweis aus
    seinen Eingaben (``Eingaben.si_nach_id`` ueber :func:`lagenbezuege`), in
    der Spannung-Dehnung-Analyse aus der Loesung.
    """
    gesetze: Dict[str, Stahlgesetz] = {}
    lagen = []
    for q in posten:
        stahl = q.lage.stahl
        if stahl.id not in gesetze:
            satz = wahl.satz(stahl)
            gesetze[stahl.id] = Stahlgesetz(
                E_s=wert(stahl.id_von("E_s")),
                f_yd=abs(wert(stahl.id_von(satz.stahl))),
                f_yd_druck=abs(wert(stahl.id_von(satz.stahl_druck))),
                eps_ud=abs(wert(stahl.id_von("eps_ud"))))
        lagen.append(Stahllage(
            a_s=wert(q.as_def.id), z=wert(q.z_def.id), stahl=gesetze[stahl.id],
            sorte=kennung_aus(stahl.id), stahlname=stahl.name, nummer=q.lage.nummer,
            seite=q.lage.seite,
            text=q.bezeichnung, index=q.index))
    return lagen


def bezuege_vereinen(*listen: Sequence[Eingabebezug]) -> List[Eingabebezug]:
    """
    Mehrere Listen von Eingaben zu einer -- jeder Name einmal.

    Derselbe Name mit derselben Wert-ID ist dieselbe Eingabe und wird einmal
    angemeldet. Derselbe Name mit einer anderen ID waere eine Verwechslung:
    die Rechnung laese dann die eine Zahl unter dem Namen der anderen.
    """
    vorhanden = {}
    heraus: List[Eingabebezug] = []
    for liste in listen:
        for b in liste:
            if b.name not in vorhanden:
                vorhanden[b.name] = b.wert_id
                heraus.append(b)
            elif vorhanden[b.name] != b.wert_id:
                raise ValueError(
                    f"Die Eingabe '{b.name}' steht einmal als {vorhanden[b.name]} "
                    f"und einmal als {b.wert_id} da.")
    return heraus


@dataclass(frozen=True)
class Gesetze:
    """Was zu einer Wahl gehoert -- Gesetze, Lagen, und wie die Fasern rechnen."""

    wahl: Rechenwahl
    beton: Gesetz
    kennwerte: Betonkennwerte
    """Die Zahlen des Betons -- seine Grenzdehnungen begrenzen die Suche (:meth:`grenzen`)."""

    def stahl(self, s: Stahlgesetz) -> Stahlgesetz:
        """Der Stahl einer Lage, wie der Loeser ihn rechnet -- in der Handrechnung nur auf Zug."""
        return StahlNurZug.aus(s) if self.wahl.art is Rechenart.HANDRECHNUNG else s

    @property
    def verdraengt(self) -> bool:
        """Die Handrechnung zaehlt den Beton auch, wo der Stahl liegt."""
        return self.wahl.art is not Rechenart.HANDRECHNUNG

    def lagen(self, lagen: Sequence[Stahllage]) -> List[Stahllage]:
        """Die Lagen, mit denen gerechnet wird -- in der Handrechnung je Seite eine (:func:`je_seite`)."""
        if self.wahl.art is Rechenart.HANDRECHNUNG:
            return list(je_seite(lagen).values())
        return list(lagen)

    def querschnitt(self, *, h: float, b: float, lagen: Sequence[Stahllage],
                    streifen: int = FASERN) -> Querschnitt:
        """
        Die Platte als Querschnitt der Interaktion, wie der gezeichnete und der
        Pfahl (:class:`~opencivil.querschnitt.interaktion.Querschnitt`): ein
        Rechteck b·h um die halbe Hoehe, darin je Lage, mit der gerechnet wird
        (:meth:`lagen`), ein Stab in ihrer Tiefe. Der Beton gedrueckt bis
        ``-eps_c2d`` samt Punkt C, jeder Stahl bis ``±eps_ud``: die Grenzen
        zieht die Interaktion an beiden Raendern, an den Punkten C und an den
        aeussersten Lagen jedes Stahls -- benannt nach Beton und Stahl. Eine
        Lage ist ein Band ueber die ganze Breite: der Beton, den sie
        verdraengt, so dick wie ihr Stahl ueber b verschmiert.

        ``streifen`` wie beim gezeichneten Querschnitt: so viele, wie ein
        Loeser Fasern hat (:data:`~opencivil.querschnitt.fasern.FASERN`), ohne
        Angabe; die genaue Resistenzlinie nimmt mehr. Bis 2026-11-20 baute
        die Platte ihre Fasern, Grenzen und Faecher selbst.
        """
        k = self.kennwerte
        werkstoffe = [Werkstoff(k.name, self.beton, -k.eps_c2d, math.inf,
                                c_punkt=(k.eps_c1d, k.eps_c2d), verdraengbar=self.verdraengt)]
        je_stahl: Dict[Tuple[str, Stahlgesetz], int] = {}
        bewehrung = []
        for l in self.lagen(lagen):
            schluessel = (l.sorte, l.stahl)
            if schluessel not in je_stahl:
                je_stahl[schluessel] = len(werkstoffe)
                werkstoffe.append(Werkstoff(l.stahlname, self.stahl(l.stahl),
                                            -l.stahl.eps_ud, l.stahl.eps_ud))
            bewehrung.append(Bewehrung(lage=(0.0, h / 2.0 - l.z), flaeche=l.a_s,
                                       werkstoff=je_stahl[schluessel], verdraengt=0,
                                       dicke=l.a_s / b))
        y, z = b / 2.0, h / 2.0
        rechteck = Teil(((-y, -z), (y, -z), (y, z), (-y, z)), werkstoff=0, eltern=None)
        return Querschnitt(werkstoffe=werkstoffe, teile=[rechteck], bewehrung=bewehrung,
                           bezug=(0.0, 0.0), streifen=streifen)

    def loeser(self, *, h: float, b: float, lagen: Sequence[Stahllage],
               suche: Suche = HALBIEREN) -> Faserloeser:
        """
        Der Loeser zu dieser Wahl: der Querschnitt (:meth:`querschnitt`) mit
        Zug unten, im Fenster seiner Grenzen. Ein Fenster fuer jeden Loeser
        der Platte -- Stahlspannung, Knicken, Analysen. Bis 2026-10-18
        suchten die Stahlspannungen den Beton fest bis 3 ‰ und den Stahl am
        Betonrand, das Knicken mit ``eps_c2d``, aber den Stahl ebenso am Rand
        (Benutzer, 2026-10-18). ``suche`` sagt, wie gesucht wird -- das
        Knicken nimmt :data:`~opencivil.core.suche.ILLINOIS`.
        """
        r = self.querschnitt(h=h, b=b, lagen=lagen).richtung(Zugseite.UNTEN.psi)
        oben, unten = r.beton
        return Faserloeser(querschnitt=r.fasern, grenzen=r.grenzen, oben=oben, unten=unten,
                           lagen=self.lagen(lagen), beton=lambda arm, eps: self.beton(eps),
                           suche=suche)


def protokoll_rechenwahl(p: Protokoll, wahl: Rechenwahl, basis: str, stoffe: Sequence, *,
                         titel: str = "Rechenwahl") -> Wert:
    """
    Womit das Kapitel rechnet, in einer Zeile: phi (nur wo es wirkt), Werte,
    Rechenart. Rechnen alle ``stoffe`` mit demselben Wertesatz, steht er
    einmal da, sonst je Baustoff mit seinem Namen -- ebenso die Rechenart je
    Beton. Zurueck kommt phi als Wert -- fuer die Formeln danach.
    """
    phi = Zwischenwerte(basis).zahl("phi", r"\varphi", wahl.kriechzahl, stellen=2)
    satz = wahl.saetze.einheitlich
    if satz is not None:
        werte = rf"\text{{{satz.beschriftung}}}\ {satz.beton_zeichen},\ {satz.stahl_zeichen}"
    else:
        werte = r",\ ".join(
            rf"{als_text(f'{s.name}: {wahl.satz(s).beschriftung}')}\ "
            rf"{wahl.satz(s).beton_zeichen if s.art is Baustoffart.BETON else wahl.satz(s).stahl_zeichen}"
            for s in stoffe)
    art = wahl.arten.einheitlich
    arten = (art.latex if art is not None else r",\ ".join(
        als_text(f"{s.name}: {wahl.art_von(s).beschriftung}")
        for s in stoffe if s.art is Baustoffart.BETON))
    teile = ([angabe(phi)] if wahl.arten.mit_kriechzahl else []) + [werte, arten]
    p.gleichung(r" \qquad ".join(teile), titel=titel)
    return phi


def protokoll_gesetze(p: Protokoll, wahl: Rechenwahl, e: Eingaben, basis: str, *,
                      titel: str, beton, posten) -> None:
    """
    Die Werkstoffgesetze der Wahl, so wie gerechnet wird: jedes Gesetz
    schreibt sich selbst
    (:meth:`~opencivil.querschnitt.werkstoffgesetz.Gesetz.protokoll`), mit den
    Werten, mit denen es rechnet -- der Beton mit dem wirksamen Modul, jeder
    Stahl der Posten mit seinen, jeder in seinem Wertesatz; bei mehreren
    Staehlen mit dem Namen im Titel.

    Der wirksame Modul selbst steht nicht hier: wo er gebraucht wird, schreibt
    ihn das Kapitel an der Stelle, an der er erklaert wird
    (:func:`~opencivil.nachweis.querschnittsloeser.protokoll_wirksamer_modul`).
    """
    g = gesetze(wahl, Betonkennwerte.aus_eingaben(e, wahl, beton))
    if wahl.art is Rechenart.HANDRECHNUNG:
        p.erklaerung(
            "Mit der Handrechnung rechnet der Querschnitt wie die Resistenzlinie "
            "aus Handrechnung: der Beton als Spannungsblock, die gedrückte "
            "Bewehrung weggelassen, die Bewehrung jeder Seite zu einer Lage in "
            "ihrem Schwerpunkt zusammengefasst, und der Beton auch dort gezählt, "
            "wo der Stahl liegt.")
    werte = {rolle: e[name] for rolle, name in wahl.betonkennwerte(beton).items()}
    werte["E_c"] = wirksamer_modul_wert(werte["E_c"], wahl.kriechzahl, basis)
    g.beton.protokoll(p, werte, titel=titel, basis=basis)

    sorten = staehle(posten)
    gesetz_von = {l.sorte: l.stahl for l in stahllagen(posten, wahl, e.si_nach_id())}
    for stahl in sorten:
        g.stahl(gesetz_von[kennung_aus(stahl.id)]).protokoll(
            p, {rolle: e[stahl.eingabename(name)]
                for rolle, name in wahl.satz(stahl).stahlkennwerte.items()},
            titel=titel if len(sorten) == 1 else f"{titel}, {stahl.name}")


def protokoll_gesetze_nach_wahl(p: Protokoll, e: Eingaben, analyse: Querschnittsanalyse,
                                wahl: Rechenwahl, basis: str, *, titel: str) -> None:
    """
    Die Werkstoffgesetze einer Wahl, je Material eines gezeichneten
    Querschnitts -- die von
    :meth:`~opencivil.querschnitt.analyse.Querschnittsanalyse.querschnitt`;
    jedes schreibt sich selbst, mit seinen Werten, wie bei der Platte
    (:func:`protokoll_gesetze`). Vor jedem Beton sein wirksamer Modul, wo ein
    Gesetz an ihm haengt. Fuer die Gebrauchsnachweise und das Knicken des
    gezeichneten Querschnitts.
    """
    phi = Zwischenwerte(basis).zahl("phi", r"\varphi", wahl.kriechzahl, stellen=2)
    werkstoffe, index = analyse.werkstoffe(e.si_nach_id(), wahl)
    for stoff in analyse.baustoffe:
        unter = f"{basis}.{kennung_aus(stoff.id)}"
        if stoff.art is Baustoffart.BETON:
            werte = {rolle: e[stoff.eingabename(name)]
                     for rolle, name in wahl.betonkennwerte(stoff).items()}
            if wahl.art_von(stoff).mit_kriechzahl:
                protokoll_wirksamer_modul(p, werte["E_c"], phi, unter,
                                          titel=f"Wirksamer Elastizitätsmodul {stoff.name}")
            werte["E_c"] = wirksamer_modul_wert(werte["E_c"], wahl.kriechzahl, unter)
        else:
            werte = {rolle: e[stoff.eingabename(name)]
                     for rolle, name in wahl.satz(stoff).stahlkennwerte.items()}
        werkstoffe[index(stoff)].gesetz.protokoll(p, werte, titel=f"{titel}, {stoff.name}",
                                                  basis=unter)


def gesetze(wahl: Rechenwahl, w: Betonkennwerte, *, ungerissen: bool = False) -> Gesetze:
    """
    Die Gesetze zu einer Wahl, ``ungerissen`` mit dem ungerissenen Beton
    (:func:`~opencivil.querschnitt.gesetzwahl.betongesetz`) -- fuer ein
    Bauteil mit einem Beton, der Platte: seine Rechenart ist die der Wahl
    (:attr:`~opencivil.querschnitt.gesetzwahl.Rechenwahl.art`). Der Stahl kommt
    je Lage dazu, samt seinem ``eps_ud`` -- bis 2026-10-12 rechneten die
    Stahlspannungen fest mit 4.5 %, das Knicken und die Analysen mit dem der
    ersten Lage.
    """
    return Gesetze(wahl=wahl, beton=betongesetz(wahl, wahl.art, f_c=w.f_c, E_c=w.E_c,
                                                eps_c1d=w.eps_c1d, eps_c2d=w.eps_c2d,
                                                ungerissen=ungerissen),
                   kennwerte=w)
