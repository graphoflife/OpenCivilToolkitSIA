"""
opencivil/querschnitt/gesetzwahl.py -- womit ein Querschnitt rechnet.

VERANTWORTUNG:
Die Wahl der Werkstoffgesetze: der Wertesatz (:class:`Werkstoffsatz`), die
Rechenart des Betons (:class:`Rechenart`) und die des Holzes
(:class:`Holzrechnung`), mit der Kriechzahl zusammen eine
:class:`Rechenwahl` -- und die Stellen, die daraus die Gesetze bauen: den
Beton (:func:`betongesetz`), mit dem wirksamen Modul (:func:`wirksamer_modul`),
und das Holz (:func:`holzgesetz`).
Das gehoert dem Querschnitt: die Platte, der gezeichnete Querschnitt und die
Spannung-Dehnung-Analyse fragen hier, ohne dafuer einen Nachweis zu laden.
Was ein Nachweis-Kapitel davon anbietet, steht bei den Nachweisen
(:mod:`opencivil.nachweis.rechenwahl`). Bis 2026-10-17 stand alles dort und
im Loeser, und der gezeichnete Querschnitt importierte darum aus den
Nachweisen.

DIE RECHENARTEN:
* **Handrechnung** -- im Loeser derselbe Querschnitt wie in der
  Resistenzlinie aus Handrechnung: der Spannungsblock, die Bewehrung nur auf
  Zug, je Seite zu einer Lage im Schwerpunkt zusammengefasst -- beide mit
  :func:`~opencivil.nachweis.querschnittsloeser.je_seite` --, und der Beton
  auch dort gezaehlt, wo der Stahl liegt. Die gedrueckte Bewehrung zaehlt
  nicht -- in keiner anderen Rechenart fehlt sie.
* **0.85·x-Vereinfachung** -- derselbe Spannungsblock, ueber die Hoehe
  integriert, jede Faser mit ihrer mittleren Spannung. Die gedrueckte
  Bewehrung wirkt mit und verdraengt den Beton an ihrer Stelle.
* **Praezise ohne Vereinfachung** -- die Parabel-Rechteck-Beziehung, ihr
  Anstieg mit dem wirksamen Modul ``E_cm/(1+phi)``, ``k_sigma`` nie unter 1.

Die Namen hat der Benutzer am 2026-10-12 gewaehlt; vorher hiessen sie
«Handrechnung Block 0.85·x», «Block 0.85·x genau» und «Parabel». Bis
2026-11-25 gab es fuer die Stahlspannungen dazu «elastisch»: der Beton linear
mit ``E_cm/(1+phi)``, hoechstens ``f_c``. Der Benutzer hat es gestrichen: im
Gebrauch ist die Parabel beinahe eine Gerade, und die Stahlspannung lag um
etwa ein Prozent neben der praezisen -- bei phi = 2 etwa 344 statt
340 N/mm².

Die Kriechzahl wirkt nur bei praezise: an den anderen Gesetzen haengt kein
Modul. Der Wertesatz bestimmt, wo die Plateaus liegen
(:class:`Werkstoffsatz`), und wie ein Widerstand heisst -- ``R_d`` oder
``R_k``.

JE MATERIAL:
Den Wertesatz waehlt ein Kapitel je Material (:class:`Wertesaetze`), wie
die Tragsicherheit der Querschnittsanalyse es schon tat -- in jedem Modul
dieselbe Wahl (Benutzer, 2026-11-20). Bis dahin galt in der Platte, beim
Knicken, in den Stahlspannungen, den Analysen und beim E_eq eines Stabs ein
Satz fuer alle Materialien. Rechnen Beton und Stahl mit verschiedenen
Saetzen, ist ein Widerstand weder ``R_d`` noch ``R_k``; er heisst dann
schlicht ``R`` (nach Vorgabe, nicht nachgeschlagen).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, FrozenSet, Mapping, Sequence, Tuple

from opencivil.core.wahl import Wahl
from opencivil.material.basis import Baustoffart
from opencivil.querschnitt.werkstoffgesetz import (
    BLOCKANTEIL, Betongesetz, BetonUngerissen, Gesetz, Holzgesetz, HolzPlastisch, Spannungsblock,
)


class Werkstoffsatz(Wahl):
    """
    Mit welchen Festigkeiten die Werkstoffgesetze rechnen.

    **Bemessung** -- ``f_cd`` und ``f_yd``. Fuer die Tragsicherheit: gefragt
    ist, was der Querschnitt *darf*, und dahinein gehoert der
    Teilsicherheitsbeiwert.

    **Charakteristisch** -- ``f_ck`` und ``f_yk``. Fuer die
    Gebrauchstauglichkeit: gefragt ist, was der Querschnitt *tut*, und Stahl
    fliesst bei ``f_yk``, nicht bei ``f_yd``. Mit dem Plateau bei ``f_yd``
    laege jede Stahlspannung unter 435 N/mm², und eine Grenze darueber --
    ``f_yk`` bei normaler Rissanforderung -- waere nie zu ueberschreiten: ein
    Nachweis, der per Konstruktion immer aufgeht.

    Der Satz bestimmt, **wo die Plateaus liegen**, und sonst nichts. Die
    Moduln und Dehnungsgrenzen sind in beiden Saetzen dieselben. Er steht hier
    als Name und nicht als zwei Zahlen an jeder Aufrufstelle: welche Werte ein
    Nachweis ansetzt, ist eine Entscheidung, und eine Entscheidung soll man
    lesen koennen, statt sie aus ``f_sd=...`` erschliessen zu muessen. Jeder
    Nutzer des Loesers nennt darum seinen Satz -- der Knicknachweis
    ``BEMESSUNG``, die Spannungsbegrenzung ``CHARAKTERISTISCH``; die
    Spannung-Dehnung-Analyse waehlt ihn je Analyse.
    """

    BEMESSUNG = "bemessung"
    CHARAKTERISTISCH = "charakteristisch"

    @property
    def beschriftung(self) -> str:
        return "Bemessungswerte" if self is Werkstoffsatz.BEMESSUNG else "charakteristisch"

    @property
    def kurz(self) -> str:
        """Fuer schmale Zeilen."""
        return "Bemessung" if self is Werkstoffsatz.BEMESSUNG else "charakteristisch"

    @property
    def kuerzel(self) -> str:
        """Der Buchstabe am Index: ``d`` (design) oder ``k`` (charakteristisch)."""
        return "d" if self is Werkstoffsatz.BEMESSUNG else "k"

    @property
    def widerstandsindex(self) -> str:
        """Der Index an einem Widerstand: ``M_{Rd}`` oder ``M_{Rk}``."""
        return "Rd" if self is Werkstoffsatz.BEMESSUNG else "Rk"

    @property
    def stahl_druck(self) -> str:
        """Kurzname der Stahlfestigkeit auf Druck -- dort beginnt das Plateau."""
        return "f_yd_druck" if self is Werkstoffsatz.BEMESSUNG else "f_yk_druck"

    @property
    def stahl(self) -> str:
        """Kurzname der Stahlfestigkeit -- dort beginnt das Fliessplateau."""
        return "f_yd" if self is Werkstoffsatz.BEMESSUNG else "f_yk"

    @property
    def beton(self) -> str:
        """Kurzname der Betonfestigkeit -- dort endet der Anstieg im Druck."""
        return "f_cd" if self is Werkstoffsatz.BEMESSUNG else "f_ck"

    @property
    def stahl_zeichen(self) -> str:
        """Das Formelzeichen dazu, fuer die Herleitung -- ``f_{yd}``."""
        return "f_{yd}" if self is Werkstoffsatz.BEMESSUNG else "f_{yk}"

    @property
    def stahl_druck_zeichen(self) -> str:
        """Das Zeichen des Plateaus auf Druck -- ``f_{yd}^{-}``."""
        return f"{self.stahl_zeichen}^{{-}}"

    @property
    def beton_zeichen(self) -> str:
        """Das Formelzeichen dazu, fuer die Herleitung -- ``f_{cd}``."""
        return "f_{cd}" if self is Werkstoffsatz.BEMESSUNG else "f_{ck}"

    @property
    def betonkennwerte(self) -> Dict[str, str]:
        """
        Je Rolle eines Betongesetzes
        (:data:`~opencivil.querschnitt.werkstoffgesetz.Werte`) der Kurzname
        seines Kennwerts in diesem Satz -- ``E_c`` als ``E_cm``, ohne Kriechen.
        """
        return {"f_c": self.beton, "E_c": "E_cm", "eps_c1d": "eps_c1d", "eps_c2d": "eps_c2d"}

    @property
    def stahlkennwerte(self) -> Dict[str, str]:
        """Dasselbe fuer ein Stahlgesetz."""
        return {"f_s": self.stahl, "f_s_druck": self.stahl_druck, "E_s": "E_s",
                "eps_ud": "eps_ud"}

    @property
    def baustahl(self) -> str:
        """
        Kurzname der Streckgrenze des Baustahls -- dort beginnt sein Plateau:
        ``f_yd = f_y/γ_M1`` oder ``f_y`` (SIA 263:2013, 4.1.1).
        """
        return "f_yd" if self is Werkstoffsatz.BEMESSUNG else "f_y"

    @property
    def baustahlkennwerte(self) -> Dict[str, str]:
        """Dasselbe fuer das Gesetz des Baustahls, in Zug und Druck dieselbe Streckgrenze."""
        return {"f_s": self.baustahl, "E_s": "E_a", "eps_ud": "eps_ud"}

    @property
    def profilblech(self) -> str:
        """
        Kurzname der Streckgrenze des Profilblechstahls -- dort beginnt sein
        Plateau: ``f_ypd = f_yp/γ_ap`` oder ``f_yp`` (SIA 264:2014, 4.1.3).
        """
        return "f_ypd" if self is Werkstoffsatz.BEMESSUNG else "f_yp"

    @property
    def profilblechkennwerte(self) -> Dict[str, str]:
        """Dasselbe fuer das Gesetz des Profilblechstahls -- wie beim Baustahl."""
        return {"f_s": self.profilblech, "E_s": "E_a", "eps_ud": "eps_ud"}

    @property
    def spannstahl(self) -> str:
        """
        Kurzname der Fliessgrenze des Spannstahls -- dort beginnt sein Plateau:
        ``f_pd`` oder ``f_p01k`` (SIA 262:2025, Figur 17).
        """
        return "f_pd" if self is Werkstoffsatz.BEMESSUNG else "f_p01k"

    def festigkeit(self, art: Baustoffart) -> str:
        """
        Der Kurzname der Festigkeit, deren Plateau dieser Satz waehlt, je Art
        des Baustoffs -- ``f_cd`` oder ``f_ck`` beim Beton, ``f_yd`` oder
        ``f_y`` beim Baustahl. Das Holz hat keinen Satz (:data:`HOLZKENNWERTE`);
        fuer den Titel des Schalters (:mod:`opencivil.web.api`, ``satztitel``).
        """
        return {Baustoffart.BETON: self.beton, Baustoffart.BETONSTAHL: self.stahl,
                Baustoffart.SPANNSTAHL: self.spannstahl, Baustoffart.BAUSTAHL: self.baustahl,
                Baustoffart.PROFILBLECH: self.profilblech}[art]

    @property
    def spannstahlkennwerte(self) -> Dict[str, str]:
        """
        Dasselbe fuer das Gesetz des Spannstahls, mit dem Modul der Draehte und
        Staebe -- ein Spannglied aus Litzen nimmt seinen eigenen
        (:mod:`opencivil.querschnitt.spannglieder`).
        """
        return {"f_p": self.spannstahl, "E_p": "E_p", "eps_ud": "eps_ud"}


#: Je Rolle der Gesetze des Holzes der Kurzname seines Kennwerts -- die
#: Bemessungswerte in Faserrichtung und der mittlere Modul (SIA 265:2012,
#: Tabellen 6 und 7), dazu die Grenzstauchung des elastisch-plastischen
#: (:class:`~opencivil.querschnitt.werkstoffgesetz.HolzPlastisch`).
HOLZKENNWERTE = {"f_t": "f_t_0_d", "f_c": "f_c_0_d", "E": "E_0_mean", "eps_cu": "eps_cu"}


class Holzrechnung(Wahl):
    """
    Wie das Holz rechnet: linear bis zum Bruch (SIA 265:2012, 3.1.2.1) oder
    auf Druck elastisch-plastisch (3.1.2.2). Eine Wahl nur in den
    Spannung-Dehnung-Analysen (Benutzer, 2026-11-25): die Nachweise rechnen
    linear (4.1.2). Die Grenzstauchung des plastischen ist nach Vorgabe,
    nicht nachgeschlagen (:data:`~opencivil.material.holz.STAUCHBARKEIT`).
    """

    LINEAR = "linear"
    PLASTISCH = "plastisch"

    @property
    def beschriftung(self) -> str:
        return {Holzrechnung.LINEAR: "Linear bis zum Bruch",
                Holzrechnung.PLASTISCH: "Auf Druck elastisch-plastisch"}[self]

    @property
    def kurz(self) -> str:
        """Fuer schmale Zeilen -- im Schalter unter dem Holz."""
        return {Holzrechnung.LINEAR: "linear",
                Holzrechnung.PLASTISCH: "elastisch-plastisch"}[self]


class Rechenart(Wahl):
    """Wie der Querschnitt gerechnet wird -- siehe Dateikopf."""

    HANDRECHNUNG = "handrechnung"
    BLOCK = "block"
    PARABEL = "parabel"

    @property
    def beschriftung(self) -> str:
        return {
            Rechenart.HANDRECHNUNG: "Handrechnung",
            Rechenart.BLOCK: f"{BLOCKANTEIL}·x-Vereinfachung",
            Rechenart.PARABEL: "Präzise ohne Vereinfachung",
        }[self]

    @property
    def kurz(self) -> str:
        """Fuer schmale Zeilen -- etwa die Auswahl auf der Karte einer Analyse."""
        return {
            Rechenart.HANDRECHNUNG: "Hand",
            Rechenart.BLOCK: f"{BLOCKANTEIL}·x",
            Rechenart.PARABEL: "präzise",
        }[self]

    @property
    def latex(self) -> str:
        """Der Name als Formeltext -- fuer die Zeile «Rechenwahl» der Herleitung."""
        return {
            Rechenart.HANDRECHNUNG: r"\text{Handrechnung}",
            Rechenart.BLOCK: rf"{BLOCKANTEIL} \cdot x\text{{-Vereinfachung}}",
            Rechenart.PARABEL: r"\text{Präzise ohne Vereinfachung}",
        }[self]

    @property
    def mit_kriechzahl(self) -> bool:
        """Ob ``phi`` etwas aendert -- nur, wo ein Gesetz am Modul haengt."""
        return self is Rechenart.PARABEL

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


@dataclass(frozen=True)
class JeBaustoff:
    """
    Je Baustoff eines Bauteils eine Wahl: der Wertesatz (:class:`Wertesaetze`)
    oder beim Beton die Rechenart (:class:`Rechenarten`). ``je_baustoff``
    nennt die Baustoffe mit ihrer Wahl, nach Baustoff-ID geordnet; ein anderer
    rechnet mit ``vorgabe`` -- so auch jeder, wo ein Kapitel eine Wahl fuer
    alle festlegt (:meth:`alle`).
    Unveraenderlich und vergleichbar: eine Wahl ist Schluessel von
    Zwischenspeichern, und zwei gleiche Wahlen teilen sich eine Linie. Darum
    wird eine Wahl fuer alle immer zu :meth:`alle` (:meth:`je`) -- sonst
    rechneten die Kennzahlen, die mit Bemessungswerten fest waehlen, ihre
    eigene Linie neben der gleichen der Tragsicherheit.
    """

    vorgabe: Any
    je_baustoff: Tuple[Tuple[str, Any], ...] = ()

    @classmethod
    def alle(cls, wahl):
        """Jeder Baustoff mit derselben Wahl."""
        return cls(vorgabe=wahl)

    @classmethod
    def je(cls, wahlen: Mapping[str, Any], vorgabe: Any = None):
        """
        Aus Baustoff-ID und Wahl -- je Baustoff des Bauteils eine. Haben alle
        dieselbe, ist es :meth:`alle` mit ihr; ohne Baustoff die ``vorgabe``,
        ohne Angabe die der Klasse.
        """
        if vorgabe is None:
            vorgabe = cls().vorgabe
        verschieden = set(wahlen.values())
        if len(verschieden) <= 1:
            return cls.alle(next(iter(verschieden), vorgabe))
        return cls(vorgabe, tuple(sorted(wahlen.items())))

    def von(self, stoff):
        """Die Wahl eines Baustoffs (:attr:`~opencivil.material.basis.Baustoff.id`)."""
        for kennung, wahl in self.je_baustoff:
            if kennung == stoff.id:
                return wahl
        return self.vorgabe

    @property
    def gewaehlt(self) -> FrozenSet:
        """Die Wahlen, mit denen gerechnet wird."""
        return frozenset(w for _, w in self.je_baustoff) or frozenset((self.vorgabe,))

    @property
    def einheitlich(self):
        """Die Wahl, wenn alle Baustoffe dieselbe haben -- sonst ``None``."""
        return next(iter(self.gewaehlt)) if len(self.gewaehlt) == 1 else None


@dataclass(frozen=True)
class Wertesaetze(JeBaustoff):
    """Je Baustoff sein Wertesatz (:class:`Werkstoffsatz`)."""

    vorgabe: Werkstoffsatz = Werkstoffsatz.BEMESSUNG

    @property
    def index(self) -> str:
        """
        Wie ein Widerstand heisst: ``Rd`` mit Bemessungswerten, ``Rk`` mit
        charakteristischen -- gemischt weder das eine noch das andere,
        ``R`` (nach Vorgabe, nicht nachgeschlagen).
        """
        satz = self.einheitlich
        return satz.widerstandsindex if satz else "R"

    @property
    def kuerzel(self) -> str:
        """Der Buchstabe am Index, ``d`` oder ``k`` -- gemischt keiner."""
        satz = self.einheitlich
        return satz.kuerzel if satz else ""

    @property
    def kurz(self) -> str:
        """Fuer Legenden: «Bemessung», «charakteristisch» -- oder «gemischt»."""
        satz = self.einheitlich
        return satz.kurz if satz else "gemischt"

    @property
    def beschriftung(self) -> str:
        """Ueber einem Bild: «Bemessungswerte», «charakteristisch» -- oder «gemischte Werte»."""
        satz = self.einheitlich
        return satz.beschriftung if satz else "gemischte Werte"


@dataclass(frozen=True)
class Rechenarten(JeBaustoff):
    """
    Je Beton seine Rechenart (:class:`Rechenart`) -- ein Stahl hat keine,
    er rechnet in jeder Art mit seinem Gesetz. Wo ein Kapitel mehrere Betone
    rechnet, fragt es hier, ob einer von ihnen am Modul haengt oder als
    Block rechnet.
    """

    vorgabe: Rechenart = Rechenart.HANDRECHNUNG

    @property
    def mit_kriechzahl(self) -> bool:
        """Ob ``phi`` bei einem der Betone etwas aendert (:attr:`Rechenart.mit_kriechzahl`)."""
        return any(a.mit_kriechzahl for a in self.gewaehlt)

    @property
    def mit_block(self) -> bool:
        """Ob einer der Betone als Spannungsblock rechnet (:attr:`Rechenart.mit_block`)."""
        return any(a.mit_block for a in self.gewaehlt)

    @property
    def ohne_ebene(self) -> str:
        """
        Was dasteht, wenn die Suche ihre Ebene verfehlt
        (:attr:`Rechenart.ohne_ebene`): rechnet ein Beton als Block, der Rat,
        praezise zu rechnen.
        """
        block = [a for a in Rechenart if a in self.gewaehlt and a.mit_block]
        return (block[0] if block else Rechenart.PARABEL).ohne_ebene


@dataclass(frozen=True)
class Holzrechnungen(JeBaustoff):
    """Je Holz, wie es rechnet (:class:`Holzrechnung`) -- ohne Wahl linear."""

    vorgabe: Holzrechnung = Holzrechnung.LINEAR


@dataclass(frozen=True)
class Rechenwahl:
    """
    Was ein Kapitel waehlt: Kriechzahl, je Baustoff den Wertesatz und je
    Beton die Rechenart, in den Spannung-Dehnung-Analysen dazu je Holz, wie
    es rechnet. Die Rechenart je Beton seit 2026-11-25 (Benutzer:
    unter dem Beton, in jedem Modul); bis dahin galt in einem Kapitel eine
    fuer alle Betone, und nur die Tragsicherheit der Querschnittsanalyse
    waehlte je Beton -- mit einer eigenen Wahl fuer jeden Baustoff.
    """

    kriechzahl: float = 0.0
    saetze: Wertesaetze = Wertesaetze()
    arten: Rechenarten = Rechenarten()
    holz: Holzrechnungen = Holzrechnungen()
    modul: str = "E_cm"
    """
    Der Kurzname des Elastizitaetsmoduls, an dem der Beton haengt: ``E_cm``,
    bei der Verformung des Knickens ``E_cd`` (SIA 262:2025, 4.2.1.17). Keine
    Wahl des Benutzers -- das Kapitel setzt ihn.
    """

    def satz(self, stoff) -> Werkstoffsatz:
        """Der Wertesatz eines Baustoffs (:meth:`JeBaustoff.von`)."""
        return self.saetze.von(stoff)

    def art_von(self, beton) -> Rechenart:
        """Die Rechenart eines Betons (:meth:`JeBaustoff.von`)."""
        return self.arten.von(beton)

    def holz_von(self, holz) -> Holzrechnung:
        """Wie ein Holz rechnet (:meth:`JeBaustoff.von`)."""
        return self.holz.von(holz)

    @property
    def art(self) -> Rechenart:
        """
        Die Rechenart, wo alle Betone dieselbe haben -- in einem Bauteil mit
        einem Beton immer, in der Platte etwa. Rechnen mehrere Betone
        verschieden, gibt es die eine nicht: dann fragt man je Beton
        (:meth:`art_von`), und hier zu fragen ist ein Fehler im Programm.
        """
        art = self.arten.einheitlich
        if art is None:
            raise ValueError("Die Betone rechnen verschieden – die Rechenart je Beton erfragen.")
        return art

    def betonkennwerte(self, beton) -> Dict[str, str]:
        """Die Kennwerte des Betongesetzes (:attr:`Werkstoffsatz.betonkennwerte`) dieses Betons, mit dem Modul der Wahl."""
        return {**self.satz(beton).betonkennwerte, "E_c": self.modul}

    def kennwerte(self, stoff) -> Dict[str, str]:
        """
        Je Rolle des Gesetzes eines Baustoffs der Kurzname seines Kennwerts --
        nach der Art des Baustoffs, die eine Stelle dafuer: Beton
        (:meth:`betonkennwerte`), Betonstahl, Spannstahl, Baustahl und Holz.
        Das Holz kennt keinen Wertesatz: SIA 265:2012 nennt nur
        Bemessungswerte (:data:`HOLZKENNWERTE`).
        """
        if stoff.art is Baustoffart.BETON:
            return self.betonkennwerte(stoff)
        if stoff.art is Baustoffart.HOLZ:
            return HOLZKENNWERTE
        satz = self.satz(stoff)
        return {Baustoffart.SPANNSTAHL: satz.spannstahlkennwerte,
                Baustoffart.BAUSTAHL: satz.baustahlkennwerte,
                Baustoffart.PROFILBLECH: satz.profilblechkennwerte,
                Baustoffart.BETONSTAHL: satz.stahlkennwerte}[stoff.art]

    @property
    def index(self) -> str:
        """``Rd``, ``Rk`` oder gemischt ``R`` -- wie ein Widerstand dieser Wahl heisst (:attr:`Wertesaetze.index`)."""
        return self.saetze.index

    def beschriftung(self, betone: Sequence = ()) -> str:
        """
        Fuer Legenden: «Präzise ohne Vereinfachung, φ = 2, Bemessung» -- phi
        nur, wo es wirkt. Rechnen die ``betone`` verschieden, steht jede Art
        mit dem Namen ihres Betons da (:func:`arten_text`).
        """
        teile = [arten_text(self, betone)]
        if self.arten.mit_kriechzahl:
            teile.append(f"φ = {self.kriechzahl:g}")
        return ", ".join(teile + [self.saetze.kurz])

    def gleiche_linie(self, andere: "Rechenwahl") -> bool:
        """
        Ob ``andere`` dieselbe Resistenzlinie ergibt: dieselben Rechenarten,
        Wertesaetze und Gesetze des Holzes, dazu Kriechzahl und Modul, wo ein
        Gesetz am Modul haengt (:attr:`Rechenarten.mit_kriechzahl`). Bis
        2026-11-20 eine freie Funktion der M-N-Interaktion, die den Modul
        nicht verglich: eine Parabel mit ``E_cd`` haette die Linie einer mit
        ``E_cm`` bekommen.
        """
        return (self.arten == andere.arten and self.saetze == andere.saetze
                and self.holz == andere.holz
                and (not self.arten.mit_kriechzahl
                     or (self.kriechzahl, self.modul) == (andere.kriechzahl, andere.modul)))


def arten_text(wahl: Rechenwahl, betone: Sequence = ()) -> str:
    """
    Die Rechenarten einer Wahl in Worten: eine fuer alle ihr Name, «Präzise
    ohne Vereinfachung»; sonst je Beton aus ``betone`` mit seinem Namen,
    «C30/37 präzise, C50/60 0.85·x».
    """
    art = wahl.arten.einheitlich
    if art is not None:
        return art.beschriftung
    return ", ".join(f"{b.name} {wahl.art_von(b).kurz}" for b in betone)


def holz_text(wahl: Rechenwahl, hoelzer: Sequence) -> str:
    """
    Wie die ``hoelzer`` rechnen, in Worten -- wie :func:`arten_text`: alle
    gleich «Linear bis zum Bruch», sonst je Holz mit seinem Namen; ohne Holz
    nichts.
    """
    gewaehlt = {wahl.holz_von(h) for h in hoelzer}
    if len(gewaehlt) == 1:
        return next(iter(gewaehlt)).beschriftung
    return ", ".join(f"{h.name} {wahl.holz_von(h).kurz}" for h in hoelzer)


def holzgesetz(rechnung: Holzrechnung, *, E: float, f_t: float, f_c: float,
               eps_cu: float) -> Holzgesetz:
    """
    Das Gesetz eines Holzes, wie es rechnet -- die eine Stelle, die zwischen
    linear und elastisch-plastisch waehlt. Werte in SI, positiv.
    """
    if rechnung is Holzrechnung.PLASTISCH:
        return HolzPlastisch(E=E, f_t=f_t, f_c=f_c, eps_cu=eps_cu)
    return Holzgesetz(E=E, f_t=f_t, f_c=f_c)


#: Die Kriechdehnung ist ``phi`` mal die elastische; zusammen ``(1 + phi)``
#: mal, und daraus folgt der wirksame Modul.
REFERENZ_KRIECHEN = "SIA 262:2025, 3.1.2.6.1, (12)"


def wirksamer_modul(E_c: float, phi: float) -> float:
    """``E_c,eff = E_c / (1 + phi)`` -- das Kriechen weicht den Beton auf (:data:`REFERENZ_KRIECHEN`)."""
    return E_c / (1.0 + phi)


def betongesetz(wahl: Rechenwahl, art: Rechenart, *, f_c: float, E_c: float,
                 eps_c1d: float, eps_c2d: float, ungerissen: bool = False) -> Gesetz:
    """
    Ein Beton einer Wahl -- im gerissenen Zustand nach seiner Rechenart
    ``art`` (:meth:`Rechenwahl.art_von`), ``ungerissen`` linear in Druck und
    Zug mit dem wirksamen Modul. Die eine Stelle fuer beide: der Loeser der
    Platte, die genaue Resistenzlinie und der gezeichnete Querschnitt
    bekommen ihren Beton hier. Bis 2026-10-17 gab die Platte ihrem Loeser den
    ungerissenen Beton als eigenes Gesetz mit, und der gezeichnete
    Querschnitt baute ihn hinter einem Schalter selbst. ``E_c`` ist der Modul
    der Wahl (:attr:`Rechenwahl.modul`), ohne Kriechen.
    """
    if ungerissen:
        return BetonUngerissen(E_c=wirksamer_modul(E_c, wahl.kriechzahl))
    if art is Rechenart.PARABEL:
        return Betongesetz.mit_modul(f_c=f_c, E_c=wirksamer_modul(E_c, wahl.kriechzahl),
                                     eps_c1d=eps_c1d, eps_c2d=eps_c2d)
    return Spannungsblock(f_cd=f_c, eps_c2d=eps_c2d)
