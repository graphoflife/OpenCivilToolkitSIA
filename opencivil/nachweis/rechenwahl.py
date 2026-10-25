"""
opencivil/nachweis/rechenwahl.py -- womit ein Kapitel rechnet.

VERANTWORTUNG:
Was ein Nachweis-Kapitel aus seiner Wahl macht -- der Kriechzahl, dem
Wertesatz und der Rechenart (:mod:`opencivil.querschnitt.gesetzwahl`): die
eine Stelle, die daraus die Werkstoffgesetze, die Bewehrungslagen und den
Querschnittsloeser baut, und welche Rechenarten ein Kapitel anbietet. Die
Kapitel der Platte und die Spannung-Dehnung-Analyse fragen hier, keines baut
seine Gesetze oder Lagen selbst.

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
Fasern: seine Stahlspannungen bieten darum die Fasern und «elastisch» an,
ohne Handrechnung (:data:`FASERSPANNUNGSARTEN`).

Die Verformung beim Knicken rechnet nur praezise (:data:`VERFORMUNGSARTEN`,
Benutzer, 2026-10-15). Mit dem Spannungsblock hat das Moment ueber der
Kruemmung flache Stuecke: dort traegt jede Kruemmung dasselbe Moment, die
Ausmitte zweiter Ordnung ist nicht eindeutig, und nahe der Grenzkraft hing
N_Rd davon ab, wie gesucht wurde -- an der Stuetze des Pruefprojekts
4099.5 kN halbiert, 4200 kN mit Warmstart.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Dict, List, Sequence

from opencivil.core.berechnung import Eingabebezug, Eingaben
from opencivil.core.latex import angabe
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.suche import HALBIEREN, Suche
from opencivil.core.wert import Wert, kennung_aus
from opencivil.material.basis import Baustoffart
from opencivil.nachweis.querschnittsloeser import (
    Querschnittsloeser, Stahllage, lagen_je_seite, protokoll_wirksamer_modul, wirksamer_modul_wert,
)
from opencivil.nachweis import dehnungsfaecher
from opencivil.querschnitt.analyse import Querschnittsanalyse
from opencivil.querschnitt.fasern import Dehnungsgrenze
from opencivil.querschnitt.gesetzwahl import Rechenart, Rechenwahl, Werkstoffsatz, betongesetz
from opencivil.querschnitt.lagenaufbau import Postenbezug
from opencivil.querschnitt.werkstoffgesetz import Gesetz, Stahlgesetz


#: Was die Tragsicherheit anbietet.
RECHENARTEN = (Rechenart.HANDRECHNUNG, Rechenart.BLOCK, Rechenart.PARABEL)

#: Die Stahlspannungen zusaetzlich elastisch.
SPANNUNGSARTEN = RECHENARTEN + (Rechenart.ELASTISCH,)

#: Was das Knicken und die Spannung-Dehnung-Analysen anbieten: nur, was ueber
#: die Fasern rechnet -- siehe «Wer was anbietet» oben.
FASERARTEN = (Rechenart.BLOCK, Rechenart.PARABEL)

#: Die Stahlspannungen des gezeichneten Querschnitts: ueber die Fasern, dazu
#: elastisch -- eine Handrechnung gibt es dort nicht.
FASERSPANNUNGSARTEN = FASERARTEN + (Rechenart.ELASTISCH,)

#: Was die Verformung beim Knicken anbietet: nur praezise -- siehe «Wer was
#: anbietet» oben.
VERFORMUNGSARTEN = (Rechenart.PARABEL,)


# ===========================================================================
# Die Gesetze zu einer Wahl
# ===========================================================================


@dataclass(frozen=True)
class Betonkennwerte:
    """
    Die Zahlen, aus denen das Betongesetz entsteht -- SI, im Wertesatz der
    Wahl. Den Stahl traegt jede Lage selbst (:func:`stahllagen`).
    """

    f_c: float
    """``f_cd`` oder ``f_ck``."""

    E_cm: float
    eps_c1d: float
    eps_c2d: float

    @classmethod
    def aus_eingaben(cls, e: Eingaben, satz: Werkstoffsatz) -> "Betonkennwerte":
        """Aus den Eingaben, die :func:`betonbezuege` anmeldet."""
        return cls(f_c=e.g(satz.beton).si, E_cm=e.g("E_cm").si,
                   eps_c1d=e.g("eps_c1d").si, eps_c2d=e.g("eps_c2d").si)


def betonbezuege(satz: Werkstoffsatz, beton) -> List[Eingabebezug]:
    """
    Was das Betongesetz einer Wahl braucht -- unter den Kurznamen des
    Wertesatzes, ``f_cd`` oder ``f_ck``. So steht in der Herleitung das
    Zeichen, mit dem gerechnet wird. Die Reihenfolge ist die, in der die
    Werte in der Herleitung der Baustoffe erscheinen.
    """
    return [
        Eingabebezug(satz.beton, beton.id_von(satz.beton)),
        Eingabebezug("eps_c1d", beton.id_von("eps_c1d")),
        Eingabebezug("eps_c2d", beton.id_von("eps_c2d")),
        Eingabebezug("E_cm", beton.id_von("E_cm")),
    ]


def staehle(posten: Sequence[Postenbezug]) -> List:
    """Die Staehle der Posten, jeder einmal, in der Reihenfolge der Posten."""
    return list({q.lage.stahl.id: q.lage.stahl for q in posten}.values())


def stahlbezuege(posten: Sequence[Postenbezug], kennwerte: Sequence[str]) -> List[Eingabebezug]:
    """Je Stahl der Posten diese Kennwerte, unter seinem :meth:`~opencivil.material.basis.Baustoff.eingabename`."""
    return [stahl.bezug(kennwert) for stahl in staehle(posten) for kennwert in kennwerte]


def lagenbezuege(posten: Sequence[Postenbezug], satz: Werkstoffsatz) -> List[Eingabebezug]:
    """
    Was :func:`stahllagen` liest: je Posten Flaeche und Tiefe, je Stahl
    seine Kennwerte im Wertesatz der Wahl.
    """
    bezuege = [b for q in posten for b in q.bezuege("a_s", "z")]
    return bezuege + stahlbezuege(posten, ("E_s", satz.stahl, satz.stahl_druck, "eps_ud"))


def stahllagen(posten: Sequence[Postenbezug], satz: Werkstoffsatz,
               wert: Callable[[str], float]) -> List[Stahllage]:
    """
    Je Bewehrungsposten eine Lage, mit dem Stahl ihrer Lage im Wertesatz der
    Wahl -- die eine Stelle, die Lagen baut.

    ``wert`` liefert zu einer Wert-ID die Zahl in SI: in einem Nachweis aus
    seinen Eingaben (``Eingaben.si_nach_id`` ueber :func:`lagenbezuege`), in
    der Spannung-Dehnung-Analyse aus der Loesung.
    """
    gesetze: Dict[str, Stahlgesetz] = {}
    lagen = []
    for q in posten:
        stahl = q.lage.stahl
        if stahl.id not in gesetze:
            gesetze[stahl.id] = Stahlgesetz(
                E_s=wert(stahl.id_von("E_s")),
                f_yd=abs(wert(stahl.id_von(satz.stahl))),
                f_yd_druck=abs(wert(stahl.id_von(satz.stahl_druck))),
                eps_ud=abs(wert(stahl.id_von("eps_ud"))))
        lagen.append(Stahllage(
            a_s=wert(q.as_def.id), z=wert(q.z_def.id), stahl=gesetze[stahl.id],
            sorte=kennung_aus(stahl.id), nummer=q.lage.nummer, von_unten=q.lage.von_unten,
            text=q.bezeichnung))
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
        return replace(s, nur_zug=self.wahl.art is Rechenart.HANDRECHNUNG)

    @property
    def verdraengt(self) -> bool:
        """Die Handrechnung zaehlt den Beton auch, wo der Stahl liegt."""
        return self.wahl.art is not Rechenart.HANDRECHNUNG

    def lagen(self, lagen: Sequence[Stahllage], h: float) -> List[Stahllage]:
        """Die Lagen, mit denen gerechnet wird -- in der Handrechnung je Seite eine."""
        if self.wahl.art is Rechenart.HANDRECHNUNG:
            return lagen_je_seite(lagen, h)
        return list(lagen)

    def grenzen(self, lagen: Sequence[Stahllage], h: float) -> List[Dehnungsgrenze]:
        """
        Wo die Gesetze gelten, als benannte Grenzen der Suche -- die
        des Dehnungsfaechers (:func:`~opencivil.nachweis.dehnungsfaecher.grenzen`):
        der Beton an den Raendern bis ``-eps_c2d``, im Punkt C bis
        ``-eps_c1d``, jede Lage, mit der gerechnet wird, bis ``±eps_ud`` ihres
        Stahls. Jenseits davon geben die Gesetze null zurueck, und die Suche
        faende Scheinloesungen.

        Ein Fenster fuer jeden Loeser der Platte -- Stahlspannung, Knicken,
        Analysen. Bis 2026-10-18 suchten die Stahlspannungen den Beton fest
        bis 3 ‰ und den Stahl am Betonrand, das Knicken mit ``eps_c2d``, aber
        den Stahl ebenso am Rand (Benutzer, 2026-10-18).
        """
        return dehnungsfaecher.grenzen(
            h, [(l.z, l.stahl.eps_ud, f"Stahl der {l.nummer}. Lage")
                for l in self.lagen(lagen, h)],
            eps_c1d=self.kennwerte.eps_c1d, eps_c2d=self.kennwerte.eps_c2d)

    def loeser(self, *, h: float, b: float, lagen: Sequence[Stahllage],
               suche: Suche = HALBIEREN) -> Querschnittsloeser:
        """
        Der Loeser zu dieser Wahl, im Fenster der Gesetze (:meth:`grenzen`).
        ``suche`` sagt, wie gesucht wird -- das Knicken nimmt
        :data:`~opencivil.core.suche.ILLINOIS`.
        """
        return Querschnittsloeser(
            h=h, b=b, lagen=self.lagen(lagen, h), beton=self.beton,
            stahl=self.stahl, verdraengt=self.verdraengt, suche=suche,
            grenzen=self.grenzen(lagen, h))


def protokoll_rechenwahl(p: Protokoll, wahl: Rechenwahl, basis: str, *,
                         titel: str = "Rechenwahl") -> Wert:
    """
    Womit das Kapitel rechnet, in einer Zeile: phi (nur wo es wirkt), Werte,
    Rechenart. Zurueck kommt phi als Wert -- fuer die Formeln danach.
    """
    phi = Zwischenwerte(basis).zahl("phi", r"\varphi", wahl.kriechzahl, stellen=2)
    satz = wahl.satz
    teile = ([angabe(phi)] if wahl.art.mit_kriechzahl else []) + [
        rf"\text{{{satz.beschriftung}}}\ {satz.beton_zeichen},\ {satz.stahl_zeichen}",
        wahl.art.latex]
    p.gleichung(r" \qquad ".join(teile), titel=titel)
    return phi


def protokoll_gesetze(p: Protokoll, wahl: Rechenwahl, e: Eingaben, basis: str, *,
                      titel: str, posten) -> None:
    """
    Die Werkstoffgesetze der Wahl, so wie gerechnet wird: jedes Gesetz
    schreibt sich selbst
    (:meth:`~opencivil.querschnitt.werkstoffgesetz.Gesetz.protokoll`), mit den
    Werten, mit denen es rechnet -- der Beton mit dem wirksamen Modul, jeder
    Stahl der Posten mit seinen; bei mehreren Staehlen mit dem Namen im Titel.

    Der wirksame Modul selbst steht nicht hier: wo er gebraucht wird, schreibt
    ihn das Kapitel an der Stelle, an der er erklaert wird
    (:func:`~opencivil.nachweis.querschnittsloeser.protokoll_wirksamer_modul`).
    """
    satz = wahl.satz
    g = gesetze(wahl, Betonkennwerte.aus_eingaben(e, satz))
    if wahl.art is Rechenart.HANDRECHNUNG:
        p.erklaerung(
            "Mit der Handrechnung rechnet der Querschnitt wie die Resistenzlinie "
            "aus Handrechnung: der Beton als Spannungsblock, die gedrückte "
            "Bewehrung weggelassen, die Bewehrung jeder Seite zu einer Lage in "
            "ihrem Schwerpunkt zusammengefasst, und der Beton auch dort gezählt, "
            "wo der Stahl liegt.")
    beton = {rolle: e[name] for rolle, name in satz.betonkennwerte.items()}
    beton["E_c"] = wirksamer_modul_wert(e["E_cm"], wahl.kriechzahl, basis)
    g.beton.protokoll(p, beton, titel=titel, basis=basis)

    sorten = staehle(posten)
    gesetz_von = {l.sorte: l.stahl for l in stahllagen(posten, satz, e.si_nach_id())}
    for stahl in sorten:
        g.stahl(gesetz_von[kennung_aus(stahl.id)]).protokoll(
            p, {rolle: e[stahl.eingabename(name)] for rolle, name in satz.stahlkennwerte.items()},
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
    satz = wahl.satz
    phi = Zwischenwerte(basis).zahl("phi", r"\varphi", wahl.kriechzahl, stellen=2)
    werkstoffe, index = analyse.werkstoffe(e.si_nach_id(), lambda stoff: wahl)
    for stoff in analyse.baustoffe:
        unter = f"{basis}.{kennung_aus(stoff.id)}"
        if stoff.art is Baustoffart.BETON:
            werte = {rolle: e[stoff.eingabename(name)]
                     for rolle, name in satz.betonkennwerte.items()}
            if wahl.art.mit_kriechzahl:
                protokoll_wirksamer_modul(p, werte["E_c"], phi, unter,
                                          titel=f"Wirksamer Elastizitätsmodul {stoff.name}")
            werte["E_c"] = wirksamer_modul_wert(werte["E_c"], wahl.kriechzahl, unter)
        else:
            werte = {rolle: e[stoff.eingabename(name)]
                     for rolle, name in satz.stahlkennwerte.items()}
        werkstoffe[index(stoff)].gesetz.protokoll(p, werte, titel=f"{titel}, {stoff.name}",
                                                  basis=unter)


def gesetze(wahl: Rechenwahl, w: Betonkennwerte, *, ungerissen: bool = False) -> Gesetze:
    """
    Die Gesetze zu einer Wahl, ``ungerissen`` mit dem ungerissenen Beton
    (:func:`~opencivil.querschnitt.gesetzwahl.betongesetz`). Der Stahl kommt
    je Lage dazu, samt seinem ``eps_ud`` -- bis 2026-10-12 rechneten die
    Stahlspannungen fest mit 4.5 %, das Knicken und die Analysen mit dem der
    ersten Lage.
    """
    return Gesetze(wahl=wahl, beton=betongesetz(wahl, f_c=w.f_c, E_cm=w.E_cm,
                                                eps_c1d=w.eps_c1d, eps_c2d=w.eps_c2d,
                                                ungerissen=ungerissen),
                   kennwerte=w)
