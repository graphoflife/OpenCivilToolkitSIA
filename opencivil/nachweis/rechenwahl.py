"""
opencivil/nachweis/rechenwahl.py -- womit ein Kapitel rechnet.

VERANTWORTUNG:
Was ein Nachweis-Kapitel waehlt -- die Kriechzahl, den Wertesatz und die
Rechenart -- und die eine Stelle, die daraus die Werkstoffgesetze, die
Bewehrungslagen und den Querschnittsloeser baut. Die Kapitel der Platte und
die Spannung-Dehnung-Analyse fragen hier, keines baut seine Gesetze oder
Lagen selbst.

JEDE LAGE MIT IHREM STAHL:
Der Editor laesst je Seite einen eigenen Stahl waehlen. Jede Lage traegt
darum ihren Stahl (:class:`Stahllage`), angemeldet wird je Sorte unter
``{kennwert}__{sorte}`` (:func:`lagenbezuege`), gebaut von
:func:`stahllagen`. Bis 2026-10-12 nahmen Stahlspannung, Knicken, Querkraft
und Analyse den Stahl der ersten Lage fuer alle.

DIE RECHENARTEN:
* **Handrechnung** -- im Loeser derselbe Querschnitt wie in der
  Resistenzlinie aus Handrechnung: der Spannungsblock, die Bewehrung nur auf
  Zug, je Seite zu einer Lage im Schwerpunkt zusammengefasst, und der Beton
  auch dort gezaehlt, wo der Stahl liegt. Die gedrueckte Bewehrung zaehlt
  nicht -- in keiner anderen Rechenart fehlt sie.
* **0.85·x-Vereinfachung** -- derselbe Spannungsblock, ueber die Hoehe
  integriert, jede Faser mit ihrer mittleren Spannung. Die gedrueckte
  Bewehrung wirkt mit und verdraengt den Beton an ihrer Stelle.
* **Praezise ohne Vereinfachung** -- die Parabel-Rechteck-Beziehung, ihr
  Anstieg mit dem wirksamen Modul ``E_cm/(1+phi)``, ``k_sigma`` nie unter 1.
* **elastisch** -- nur fuer die Stahlspannungen: der Beton linear mit
  ``E_cm/(1+phi)``, hoechstens ``f_c``. So rechneten sie bis 2026-10-09 fest.

Die Namen hat der Benutzer am 2026-10-12 gewaehlt; vorher hiessen sie
«Handrechnung Block 0.85·x», «Block 0.85·x genau» und «Parabel».

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

Die Kriechzahl wirkt nur bei praezise und elastisch: an den anderen Gesetzen
haengt kein Modul. Der Wertesatz bestimmt, wo die Plateaus liegen
(:class:`Werkstoffsatz`), und wie ein Widerstand heisst -- ``R_d`` oder
``R_k``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Sequence, Type

from opencivil.core.berechnung import Eingabebezug, Eingaben
from opencivil.core.latex import angabe
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, kennung_aus
from opencivil.nachweis.querschnittsloeser import (
    Querschnittsloeser, Stahllage, Werkstoffsatz, beton_elastisch,
    beton_nichtlinear, bilinear, lagen_je_seite, stahl_nur_zug, wirksamer_modul,
)
from opencivil.querschnitt.werkstoffgesetz import (
    BLOCKANTEIL, K_SIGMA_LATEX, Betongesetz, Spannungsblock, Stahlgesetz, k_sigma,
)

Gesetz = Callable[[float], float]


class Rechenart(str, Enum):
    """Wie der Querschnitt gerechnet wird -- siehe Dateikopf."""

    HANDRECHNUNG = "handrechnung"
    BLOCK = "block"
    PARABEL = "parabel"
    ELASTISCH = "elastisch"

    @property
    def beschriftung(self) -> str:
        return {
            Rechenart.HANDRECHNUNG: "Handrechnung",
            Rechenart.BLOCK: f"{BLOCKANTEIL}·x-Vereinfachung",
            Rechenart.PARABEL: "Präzise ohne Vereinfachung",
            Rechenart.ELASTISCH: "elastisch",
        }[self]

    @property
    def kurz(self) -> str:
        """Fuer schmale Zeilen -- etwa die Auswahl auf der Karte einer Analyse."""
        return {
            Rechenart.HANDRECHNUNG: "Hand",
            Rechenart.BLOCK: f"{BLOCKANTEIL}·x",
            Rechenart.PARABEL: "präzise",
            Rechenart.ELASTISCH: "elastisch",
        }[self]

    @property
    def latex(self) -> str:
        """Der Name als Formeltext -- fuer die Zeile «Rechenwahl» der Herleitung."""
        return {
            Rechenart.HANDRECHNUNG: r"\text{Handrechnung}",
            Rechenart.BLOCK: rf"{BLOCKANTEIL} \cdot x\text{{-Vereinfachung}}",
            Rechenart.PARABEL: r"\text{Präzise ohne Vereinfachung}",
            Rechenart.ELASTISCH: r"\text{elastisch}",
        }[self]

    @property
    def mit_kriechzahl(self) -> bool:
        """Ob ``phi`` etwas aendert -- nur, wo ein Gesetz am Modul haengt."""
        return self in (Rechenart.PARABEL, Rechenart.ELASTISCH)

    @property
    def mit_block(self) -> bool:
        """Ob der Beton als Spannungsblock rechnet."""
        return self in (Rechenart.HANDRECHNUNG, Rechenart.BLOCK)

    @property
    def ohne_ebene(self) -> str:
        """
        Was statt der Probe dasteht, wenn die Suche ihre Ebene verfehlt
        (:attr:`~opencivil.nachweis.querschnittsloeser.Ebene.verfehlt`) --
        mit dem Spannungsblock bei viel Druck und wenig Moment. Mit der
        Parabel gibt es die Ebene dort.
        """
        if self.mit_block:
            return (f"Mit der {self.beschriftung} gibt es zu dieser Einwirkung keine "
                    f"Dehnungsebene – präzise rechnen.")
        return "Die gefundene Dehnungsebene erzeugt diese Einwirkung nicht."


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

#: Was eine alte Datei dort noch waehlen durfte, wo es die Wahl heute nicht
#: mehr gibt -- und was daraus wird, Schritt fuer Schritt zur genaueren, bis es
#: die Wahl gibt: aus der Handrechnung beim Knicken und in den Analysen der
#: Spannungsblock, ueber die Fasern gerechnet (seit 2026-10-12); die
#: Druckbewehrung zaehlt dann mit, der Widerstand steigt darum leicht. Aus dem
#: Spannungsblock bei der Verformung des Knickens die Parabel (seit
#: 2026-10-15), aus der Handrechnung dort also auch.
ERSATZ_ALTER_WAHL = {Rechenart.HANDRECHNUNG.value: Rechenart.BLOCK.value,
                     Rechenart.BLOCK.value: Rechenart.PARABEL.value}

#: Die Seite im Notizbuch fuer den Stahl der Handrechnung, der nur Zug traegt.
STAHL_NUR_ZUG = "Betonstahl nur auf Zug"


@dataclass(frozen=True)
class Rechenwahl:
    """Was ein Kapitel waehlt: Kriechzahl, Wertesatz, Rechenart."""

    kriechzahl: float = 0.0
    satz: Werkstoffsatz = Werkstoffsatz.BEMESSUNG
    art: Rechenart = Rechenart.HANDRECHNUNG

    @classmethod
    def aus(cls, kriechzahl: float, werkstoffsatz: str, rechenart: str) -> "Rechenwahl":
        """Aus den Feldern einer Beschreibung -- Zahl und zwei Namen."""
        return cls(kriechzahl=float(kriechzahl), satz=Werkstoffsatz(werkstoffsatz),
                   art=Rechenart(rechenart))

    @property
    def index(self) -> str:
        """``Rd`` oder ``Rk`` -- wie ein Widerstand dieser Wahl heisst."""
        return self.satz.widerstandsindex

    @property
    def beschriftung(self) -> str:
        """Fuer Legenden: «Präzise ohne Vereinfachung, φ = 2, Bemessung» -- phi nur, wo es wirkt."""
        teile = [self.art.beschriftung]
        if self.art.mit_kriechzahl:
            teile.append(f"φ = {self.kriechzahl:g}")
        return ", ".join(teile + [self.satz.kurz])


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


def staehle(posten) -> List:
    """Die Staehle der Posten, jeder einmal, in der Reihenfolge der Posten."""
    return list({lage.stahl.id: lage.stahl for lage, *_ in posten}.values())


def stahlname(kennwert: str, stahl) -> str:
    """Der Name, unter dem ein Kennwert dieses Stahls eingeht: ``E_s__s1``."""
    return f"{kennwert}__{kennung_aus(stahl.id)}"


def stahlbezuege(posten, kennwerte: Sequence[str]) -> List[Eingabebezug]:
    """Je Stahl der Posten diese Kennwerte, unter :func:`stahlname`."""
    return [Eingabebezug(stahlname(kennwert, stahl), stahl.id_von(kennwert))
            for stahl in staehle(posten) for kennwert in kennwerte]


def lagenbezuege(posten, satz: Werkstoffsatz) -> List[Eingabebezug]:
    """
    Was :func:`stahllagen` liest: je Posten Flaeche und Tiefe, je Stahl
    seine Kennwerte im Wertesatz der Wahl.
    """
    bezuege = []
    for lage, art, _, as_id, z_id in posten:
        marke = f"{lage.nummer}{art.kuerzel}"
        bezuege += [Eingabebezug(f"a_s_{marke}", as_id), Eingabebezug(f"z_{marke}", z_id)]
    return bezuege + stahlbezuege(posten, ("E_s", satz.stahl, satz.stahl_druck, "eps_ud"))


def werte_nach_id(e: Eingaben) -> Callable[[str], float]:
    """Die Zahl einer Eingabe in SI, nach ihrer Wert-ID -- fuer :func:`stahllagen`."""
    nach_id = {w.id: w.groesse.si for w in e.values()}
    return nach_id.__getitem__


def stahllagen(posten, satz: Werkstoffsatz, wert: Callable[[str], float]) -> List[Stahllage]:
    """
    Je Bewehrungsposten eine Lage, mit dem Stahl ihrer Lage im Wertesatz der
    Wahl -- die eine Stelle, die Lagen baut.

    ``wert`` liefert zu einer Wert-ID die Zahl in SI: in einem Nachweis aus
    seinen Eingaben (:func:`werte_nach_id` ueber :func:`lagenbezuege`), in
    der Spannung-Dehnung-Analyse aus der Loesung.
    """
    gesetze: Dict[str, Stahlgesetz] = {}
    lagen = []
    for lage, art, _, as_id, z_id in posten:
        stahl = lage.stahl
        if stahl.id not in gesetze:
            gesetze[stahl.id] = Stahlgesetz(
                E_s=wert(stahl.id_von("E_s")),
                f_yd=abs(wert(stahl.id_von(satz.stahl))),
                f_yd_druck=abs(wert(stahl.id_von(satz.stahl_druck))),
                eps_ud=abs(wert(stahl.id_von("eps_ud"))))
        lagen.append(Stahllage(
            a_s=wert(as_id), z=wert(z_id), stahl=gesetze[stahl.id],
            sorte=kennung_aus(stahl.id), nummer=lage.nummer, von_unten=lage.von_unten,
            text=f"{lage.nummer}. Lage {art.beschriftung}"))
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


def betongesetz(wahl: Rechenwahl, *, f_c: float, E_cm: float, eps_c1d: float,
                 eps_c2d: float) -> Gesetz:
    """
    Der Beton im gerissenen Zustand -- je Rechenart. Die eine Stelle fuer
    die Parabel und den Block: der Loeser und die genaue Resistenzlinie
    bekommen ihren Beton beide hier.
    """
    if wahl.art is Rechenart.ELASTISCH:
        return beton_elastisch(E_c=wirksamer_modul(E_cm, wahl.kriechzahl), f_c=f_c)
    if wahl.art is Rechenart.PARABEL:
        return beton_nichtlinear(f_cd=f_c, E_c=wirksamer_modul(E_cm, wahl.kriechzahl),
                                 eps_c1d=eps_c1d, eps_c2d=eps_c2d)
    return Spannungsblock(f_cd=f_c, eps_c2d=eps_c2d)


@dataclass(frozen=True)
class Gesetze:
    """Was zu einer Wahl gehoert -- Gesetze, Lagen, und wie die Fasern rechnen."""

    wahl: Rechenwahl
    beton: Gesetz

    def stahl(self, s: Stahlgesetz) -> Gesetz:
        """Der Stahl einer Lage, wie der Loeser ihn rechnet -- in der Handrechnung nur auf Zug."""
        if self.wahl.art is Rechenart.HANDRECHNUNG:
            return stahl_nur_zug(E_s=s.E_s, f_sd=s.f_yd, eps_ud=s.eps_ud)
        return bilinear(s)

    @property
    def gemittelt(self) -> bool:
        """Der Block springt: ueber jede Faser gemittelt, sonst springt N mit."""
        return self.wahl.art.mit_block

    @property
    def verdraengt(self) -> bool:
        """Die Handrechnung zaehlt den Beton auch, wo der Stahl liegt."""
        return self.wahl.art is not Rechenart.HANDRECHNUNG

    def lagen(self, lagen: Sequence[Stahllage], h: float) -> List[Stahllage]:
        """Die Lagen, mit denen gerechnet wird -- in der Handrechnung je Seite eine."""
        if self.wahl.art is Rechenart.HANDRECHNUNG:
            return lagen_je_seite(lagen, h)
        return list(lagen)

    def loeser(self, *, h: float, b: float, lagen: Sequence[Stahllage],
               beton: Gesetz = None, klasse: Type[Querschnittsloeser] = Querschnittsloeser,
               **fenster) -> Querschnittsloeser:
        """
        Der Loeser zu dieser Wahl. ``fenster`` sind die Grenzen der Suche
        (``eps_druck``, ``eps_zug``, ``grenzen``) -- die bringt jeder Nutzer
        selbst mit. ``beton`` ersetzt das Betongesetz, etwa durch den
        ungerissenen Zustand; alles andere bleibt. ``klasse`` waehlt, wie
        gesucht wird -- das Knicken nimmt
        :class:`~opencivil.nachweis.querschnittsloeser.QuerschnittsloeserIllinois`.
        """
        return klasse(
            h=h, b=b, lagen=self.lagen(lagen, h), beton=beton or self.beton,
            stahl=self.stahl, gemittelt=self.gemittelt and beton is None,
            verdraengt=self.verdraengt, **fenster)


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
    Die Werkstoffgesetze der Wahl, mit den Zeichen ihres Wertesatzes.

    Der Stahl steht mit der Festigkeit jeder Sorte der Posten da; bei einer
    Sorte mit ihrem Zeichen, bei mehreren mit dem allgemeinen und je Sorte
    einer Angabe dahinter.

    Der wirksame Modul steht nicht hier: wo er gebraucht wird, schreibt ihn
    das Kapitel an der Stelle, an der er erklaert wird
    (:func:`~opencivil.nachweis.querschnittsloeser.protokoll_wirksamer_modul`).
    """
    satz = wahl.satz
    f_c = e[satz.beton]
    festigkeiten = [e[stahlname(satz.stahl, s)] for s in staehle(posten)]
    f_s = festigkeiten[0].symbol if len(festigkeiten) == 1 else satz.stahl_zeichen
    angaben = r" \quad ".join(angabe(w) for w in festigkeiten)
    if wahl.art is Rechenart.ELASTISCH:
        p.gleichung(
            rf"\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ {f_s}\right]"
            rf" \quad {angaben} \qquad "
            rf"\sigma_c = \max\left[E_{{c,eff}} \cdot \varepsilon_c;\ -{f_c.symbol}\right]"
            rf" \quad {angabe(f_c)}",
            titel=titel)
        return
    if wahl.art is Rechenart.HANDRECHNUNG:
        p.erklaerung(
            "Mit der Handrechnung rechnet der Querschnitt wie die Resistenzlinie "
            "aus Handrechnung: der Beton als Spannungsblock, die gedrückte "
            "Bewehrung weggelassen, die Bewehrung jeder Seite zu einer Lage in "
            "ihrem Schwerpunkt zusammengefasst, und der Beton auch dort gezählt, "
            "wo der Stahl liegt.")
    protokoll_betongesetz(p, wahl, f_c, e["E_cm"], basis, titel=titel)
    if wahl.art is Rechenart.HANDRECHNUNG:
        p.ansatz(
            r"\sigma_s = \begin{cases} \min\left(E_s \cdot \varepsilon_s;\ "
            + f_s + r"\right) & \varepsilon_s > 0 \\[1ex]"
            r" 0 & \varepsilon_s \le 0 \quad (\text{gedrückt: weggelassen})"
            r" \end{cases}",
            titel=f"{titel}: Stahl, nur auf Zug", name=STAHL_NUR_ZUG)
    else:
        p.gleichung(
            rf"\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ {f_s}\right]"
            rf" \quad {angaben}", titel=f"{titel}: Stahl")


def protokoll_betongesetz(p: Protokoll, wahl: Rechenwahl, f_c: Wert, E_cm: Wert, basis: str,
                          *, titel: str) -> None:
    """
    Der Beton einer Wahl mit Block oder Parabel -- bei der Parabel samt ihrem
    Beiwert aus dem wirksamen Modul ``E_cm/(1+phi)``. ``f_c`` ist die
    Festigkeit des Wertesatzes, ``f_cd`` oder ``f_ck``.
    """
    if wahl.art is Rechenart.PARABEL:
        werte = Zwischenwerte(basis)
        E_c_eff = werte.spannung("E_c_eff", "E_{c,eff}",
                                 wirksamer_modul(E_cm.groesse.si, wahl.kriechzahl))
        p.formel(werte.zahl("k_sigma", r"k_{\sigma}", k_sigma(E_c_eff.groesse.si, f_c.groesse.si),
                            stellen=2),
                 K_SIGMA_LATEX, {"E_c": E_c_eff, "f_c": f_c},
                 titel="Beiwert der Parabel, mit dem wirksamen Modul")
        p.ansatz(Betongesetz(0.0, 1.0, 1.0, 0.0).latex(f_c.symbol),
                 titel=f"{titel}: Beton, Parabel-Rechteck", referenz="SIA 262:2025, 4.2.1.6",
                 name=Betongesetz.NAME)
    else:
        p.ansatz(Spannungsblock(0.0, 1.0).latex(f_c.symbol),
                 titel=f"{titel}: Beton, Spannungsblock {BLOCKANTEIL}·x",
                 name=Spannungsblock.NAME)


def gesetze(wahl: Rechenwahl, w: Betonkennwerte) -> Gesetze:
    """
    Die Gesetze zu einer Wahl. Der Stahl kommt je Lage dazu, samt seinem
    ``eps_ud`` -- bis 2026-10-12 rechneten die Stahlspannungen fest mit 4.5 %,
    das Knicken und die Analysen mit dem der ersten Lage.
    """
    return Gesetze(wahl=wahl, beton=betongesetz(wahl, f_c=w.f_c, E_cm=w.E_cm,
                                                eps_c1d=w.eps_c1d, eps_c2d=w.eps_c2d))
