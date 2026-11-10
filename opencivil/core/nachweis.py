"""
opencivil/core/nachweis.py -- der Nachweis: Einwirkung gegen Widerstand, mit Urteil.

VERANTWORTUNG:
Die Berechnung, die einen Vergleich zieht und ein Urteil faellt
(:class:`Nachweis`), und was sie dafuer braucht: den Vergleich selbst mit
Erfuellungsgrad und Zeile der Herleitung (:class:`Vergleich`,
:class:`KeinVergleich` fuer Faelle ohne Vergleich), das Urteil
(:class:`NachweisUrteil`, :class:`Fallausgang`), die Definition eines
Erfuellungsgrads (:func:`grad_def`) und den Befund eines Nachweises, der je
Fall rechnet (:class:`Fallbefund`).

Ein Grad, den kein Urteil traegt, ist unbeschraenkt: das setzt
:meth:`Nachweis.rechne` fuer jeden Nachweis. Was eine Berechnung allgemein
ist, steht in :mod:`opencivil.core.berechnung`; bis 2026-11-10 stand der
Nachweis dort mit, und die Datei war ueber tausend Zeilen lang.
"""

from __future__ import annotations

import math
from abc import abstractmethod
from dataclasses import dataclass, field, replace
from typing import Any, Iterable, Optional, Sequence, Union

from opencivil.core import latex as tex
from opencivil.core.berechnung import Ausfuehrung, Berechnung, BerechnungsFehler, Eingaben
from opencivil.core.einheiten import EINHEITSLOS, Groesse
from opencivil.core.protokoll import Protokoll
from opencivil.core.wert import Wert, WertDef, grad_als_text


@dataclass
class Fallbefund:
    """
    Der Befund eines Nachweises, der je Fall oder je Lage rechnet: was er
    dabei fand, in der Reihenfolge seiner Urteile.
    """

    ergebnisse: list = field(default_factory=list)


def grad_def(id: str, symbol: str, beschreibung: str, referenz: str = "") -> WertDef:
    """
    Die Definition eines Erfuellungsgrads -- fuer jeden Nachweis dieselbe.

    Frueher legte jeder Nachweis seine eigene an, mit eigener Stellenzahl, und
    die Werttabelle rundete an :func:`grad_als_text` vorbei: dort stand 0.996
    als «1», neben «nicht erfuellt».
    """
    return WertDef(id=id, symbol=symbol, einheit=EINHEITSLOS,
                   beschreibung=beschreibung, referenz=referenz,
                   erfuellungsgrad=True)


@dataclass(frozen=True)
class Vergleich:
    """
    Was ein Nachweis gegeneinander haelt: die Einwirkung gegen den Widerstand.

    Die Regeln dazu stehen hier, fuer jeden Nachweis dieselben. Der
    Erfuellungsgrad ist R / E: um welchen Faktor die Einwirkung noch wachsen
    duerfte. Der Widerstand gibt die Richtung vor, in der begrenzt wird; wirkt
    nichts in dieser Richtung -- E ist null oder wirkt ihr entgegen, etwa ein
    gedrueckter Stahl unter der Grenze seiner Zugspannung --, ist der Grad
    unbeschraenkt, ∞. Erfuellt ist ein Grad ab eins.

    Bis 2026-10-25 schrieb jeder Nachweis beides selbst; zwei setzten statt ∞
    eine 1e9, und in der Zusammenfassung stand «1000000000.00».
    """

    einwirkung: Wert
    widerstand: Wert

    entscheid: Optional[bool] = None
    """
    Das Urteil, wo nicht der Grad entscheidet, sondern die Geometrie: bei
    Biegung mit Normalkraft, ob die Einwirkung innerhalb der Resistenzlinie
    liegt -- der Grad misst dort nur, wie weit. Sonst ``None``.
    """

    @property
    def grad(self) -> float:
        e, r = self.einwirkung.groesse.si, self.widerstand.groesse.si
        if e == 0.0 or e * r < 0.0:
            return math.inf
        return abs(r) / abs(e)

    @property
    def erfuellt(self) -> bool:
        return self.grad >= 1.0 if self.entscheid is None else self.entscheid

    def benannt(self, *, einwirkung: Optional[Wert] = None,
                widerstand: Optional[Wert] = None) -> "Vergleich":
        """
        Derselbe Vergleich unter anderen Zeichen -- in der Tabelle steht der
        Widerstand mit seiner Bedingung, ``M_Rd,x(N_Ed = -300 kN)``, in der
        Herleitung kurz. Die Zahlen bleiben; wer andere unterschiebt, bekommt
        einen Fehler.
        """
        neu = replace(self, einwirkung=einwirkung or self.einwirkung,
                      widerstand=widerstand or self.widerstand)
        if (neu.einwirkung.groesse.si, neu.widerstand.groesse.si) != (
                self.einwirkung.groesse.si, self.widerstand.groesse.si):
            raise ValueError("Ein Vergleich unter anderen Zeichen behält seine Zahlen.")
        return neu

    def bedingung(self, p: Protokoll, titel: str) -> None:
        """«E ≤ R» als Zeile, ohne Urteil -- das steht in der Zeile des Grads (:meth:`zeile`)."""
        p.gleichung(tex.bedingung(tex.angabe(self.einwirkung), r"\le", tex.angabe(self.widerstand),
                                  self.erfuellt, mit_urteil=False), titel=titel)

    def zeile(self, p: Protokoll, definition: WertDef, *, mit_urteil: bool = False) -> None:
        """
        Die Zeile mit dem Erfuellungsgrad -- in jedem Nachweis dieselbe Form,
        Widerstand durch Einwirkung.

        Der Grad setzt sich selbst (:func:`grad_als_text`). Stuende im Nenner
        eine Null, bleibt es bei den Symbolen. Ohne Normverweis -- den traegt
        die Zeile, aus der Widerstand und Einwirkung kommen.
        """
        widerstand, einwirkung = self.widerstand, self.einwirkung
        if einwirkung.formatiert() == "0":
            vorlage, eingaben = rf"\frac{{{widerstand.symbol}}}{{{einwirkung.symbol}}}", {}
        else:
            vorlage, eingaben = r"\frac{@R}{@E}", {"R": widerstand, "E": einwirkung}
        p.formel(definition.belegen(Groesse(self.grad, EINHEITSLOS)), vorlage, eingaben,
                 titel="Erfüllungsgrad", referenz="",
                 nachsatz=tex.folgerung(self.erfuellt) if mit_urteil else "")


@dataclass(frozen=True)
class KeinVergleich:
    """
    Der Ausgang eines Falls, in dem nichts gegeneinander steht: der Nachweis
    liess sich nicht fuehren (:data:`NICHT_FUEHRBAR`) -- es fehlt der
    Widerstand, etwa an einer Lage ohne Bewehrung --, oder es gibt nichts zu
    begrenzen (:data:`UNBESCHRAENKT`), etwa ohne Druck beim Knicken. Was sich
    trotzdem zeigen laesst, darf mitkommen.
    """

    grad: float
    erfuellt: bool
    einwirkung: Optional[Wert] = None
    widerstand: Optional[Wert] = None


NICHT_FUEHRBAR = KeinVergleich(0.0, False)
UNBESCHRAENKT = KeinVergleich(math.inf, True)

#: Wie ein Fall ausgeht: verglichen, oder ohne Vergleich.
Ausgang = Union[Vergleich, KeinVergleich]


class Fallausgang:
    """
    Was ein Fallergebnis aus seinem Ausgang liest -- fuer Herleitung,
    Diagramme und Urteil dieselben Zahlen. Wer erbt, fuehrt das Feld
    ``ausgang`` mit der Vorgabe :data:`NICHT_FUEHRBAR`.
    """

    ausgang: Ausgang

    @property
    def machbar(self) -> bool:
        """Ob etwas gegeneinander steht."""
        return isinstance(self.ausgang, Vergleich)

    @property
    def erfuellt(self) -> bool:
        return self.ausgang.erfuellt

    @property
    def erfuellungsgrad(self) -> float:
        return self.ausgang.grad



@dataclass(frozen=True)
class NachweisUrteil:
    """
    Ergebnis eines Nachweises.

    ``erfuellungsgrad`` ist das Verhaeltnis Widerstand/Einwirkung: um welchen
    Faktor die Einwirkung noch wachsen duerfte. Werte ab 1 bedeuten erfuellt.

    Bewusst nur diese eine Kennzahl -- die Ausnutzung als Kehrwert waere
    dieselbe Aussage in anderer Richtung und muesste an jeder Stelle mitgepflegt
    und mitgelesen werden.
    """

    erfuellt: bool
    erfuellungsgrad: Groesse
    name: str = ""
    """
    Wie das Urteil heisst: Langname, Richtung und Fall, «Biegung und
    Normalkraft x – Feld». Gestempelt von :meth:`Nachweis.rechne` aus
    :attr:`langname` und :attr:`fall` -- ein Nachweis baut ihn nicht selbst.
    Frueher tat das jeder, und jeder etwas anders («M-N-Nachweis x – Feld»,
    «Duktilität – 2. Lage», «Stahlspannung (Rissbreite) x – …»).
    """

    begruendung: str = ""
    einwirkung: Optional[Wert] = None
    widerstand: Optional[Wert] = None

    art: str = ""
    """
    Kurzzeichen der Nachweisart -- ``M-N`` oder ``V``.

    Zusammen mit :attr:`fall` ergibt es die knappe Bezeichnung fuer die
    Zusammenfassung. Getrennt gefuehrt und nicht aus :attr:`name`
    herausgeschnitten: den langen Namen zu zerlegen hiesse, aus Anzeigetext auf
    Bedeutung zu schliessen -- genau der Fehler, der die Nachweise mehrerer
    Platten schon einmal in dieselbe Tabelle gepackt hat.
    """

    langname: str = ""
    """
    Die Nachweisart ausgeschrieben -- ``Biegung und Normalkraft (x)``.

    Steht in der Zusammenfassung in einer eigenen Spalte neben
    :attr:`fall`. Sie wird hier gefuehrt und nicht in der Schnittstelle aus
    :attr:`art` nachgeschlagen: eine Tabelle von Kuerzeln auf Klartext waere
    eine zweite Stelle, an der jeder neue Nachweis eingetragen werden muss --
    und die eine, die man vergisst.

    Die Tragrichtung gehoert hier hinein, wo eine da ist. In der Zeile steht
    sie sonst nirgends, und zwei Kombinationen gleichen Namens in x und y
    saehen in der Tabelle gleich aus.
    """

    fall: str = ""
    """
    Bezeichnung dieses einen Falls -- der eingestellte Name, wo es einen gibt.

    Bei einer Einwirkungskombination ist das ihr Name, bei einem Nachweis je
    Lage die Lage. Ohne Richtung: die steht in :attr:`langname`.
    """

    hinweis: str = ""
    """
    Was in der Zusammenfassung sichtbar dabeistehen muss.

    Fuer den Fall, dass sich gar kein Widerstand bestimmen liess -- keine
    Bewehrung auf der gezogenen Seite, eine Buegeldefinition ohne Bezug in
    dieser Richtung, eine Lage, die es nicht gibt. Dann steht in der Tabelle
    eine Null oder ein Strich, und eine Null erklaert sich nicht von selbst.

    Getrennt von :attr:`begruendung`: die traegt jedes Urteil, auch das
    erfuellte, und gehoert in den Tooltip. Dieses Feld setzt nur, wer etwas zu
    melden hat -- die Pruefung weiss es, die Schnittstelle soll es nicht aus
    einer Null erraten muessen.
    """

    ziel: str = ""
    """
    Wert-ID des Erfuellungsgrads, der dieses Urteil traegt.

    Das Ziel, mit dem sich genau dieser Nachweis samt allem, was er braucht,
    nachrechnen laesst -- das Auge in der Zusammenfassung. Gesetzt von der
    Pruefung: nur sie weiss, welcher ihrer Grade zu welchem Fall gehoert.
    """

    sammel: bool = False
    """
    Ob dieses Urteil eines von mehreren zur selben Frage ist.

    Die Nachweise, die je Bewehrungslage rechnen, faellen ein Urteil je Lage.
    Beantwortet ist die Frage aber von der schlechtesten: geht die auf, gehen
    die anderen erst recht auf. In Tabelle und Bericht steht darum nur sie --
    siehe :attr:`Loesung.gefuehrte_urteile`.

    Gerechnet und *gezaehlt* werden trotzdem alle. Die Bewehrungssuche misst
    ihren Fortschritt an der Summe der Rueckstaende; saehe sie nur das
    Minimum, stuende sie, sobald zwei Lagen gleich schlecht sind -- kein
    einzelner Schritt hebt dann das Minimum, und die Suche gaebe auf, obwohl
    der naechste Durchmesser offensichtlich hilft.
    """

    still: bool = False
    """
    Ob dieses Urteil aus einem ausgeschalteten Nachweis stammt.

    Es zaehlt dann nicht in der Zusammenfassung und nicht im Gesamturteil --
    sichtbar wird es nur als Hinweis darunter, und auch nur, wenn es nicht
    aufgeht.
    """

    raum: str = ""
    """
    Namensraum des Nachweises, der dieses Urteil gefaellt hat.

    Wird von :meth:`Nachweis.rechne` gesetzt, nicht beim Erzeugen -- so kann
    kein Nachweis ihn vergessen oder falsch angeben. Die Oberflaeche gruppiert
    danach; ohne ihn muesste sie aus dem Anzeigetext zurueckschliessen, welche
    Platte gemeint ist, und das geht schief, sobald zwei Platten dieselben
    Richtungen tragen.
    """

    @property
    def meldenswert(self) -> bool:
        """
        Ob dieses stille Urteil einen Hinweis wert ist.

        Nur was still ist und nicht aufgeht -- und nur, wenn es ueberhaupt
        einen Widerstand gibt. Ohne ihn liess sich der Nachweis gar nicht
        fuehren (etwa an einer unbewehrten Lage); das ist keine Auskunft
        ueber die Bewehrung, sondern darueber, dass es keine gibt.

        Die Regel steht hier und nicht in der Schnittstelle: Tabelle,
        Konsolenbericht und LaTeX-Dokument stellen dieselbe Frage, und drei
        Antworten darauf waeren drei Gelegenheiten, auseinanderzulaufen.
        """
        return self.still and not self.erfuellt and self.widerstand is not None

    def gradtext(self, *, latex: bool = False) -> str:
        """Der Erfuellungsgrad als Text -- siehe :func:`grad_als_text`."""
        return grad_als_text(self.erfuellungsgrad.si, self.erfuellt, latex=latex)

    def __str__(self) -> str:
        urteil = "erfüllt" if self.erfuellt else "NICHT erfüllt"
        return f"{self.name}: {urteil} (Erfüllungsgrad {self.gradtext()})"


class Nachweis(Berechnung):
    """
    Vergleicht Einwirkung und Widerstand und faellt ein Urteil.

    Unterklassen implementieren :meth:`pruefe` statt :meth:`rechne`. Die
    Urteile gehen mit der :class:`Ausfuehrung` in die Loesung
    (:attr:`~opencivil.core.rechenwerk.Loesung.urteile`) -- der Bericht baut
    daraus die Nachweistabelle. Am Objekt bleibt nichts: es beschreibt den
    Nachweis, die Loesung haelt fest, wie er ausging.
    """

    still: bool = False
    """
    Ob der Nachweis mitrechnet, ohne in die Herleitung zu kommen.

    Ausgeschaltete Nachweise verschwinden nicht, sie werden still: gerechnet
    wird weiter, in der Zusammenfassung stehen sie nicht, und wenn einer von
    ihnen nicht aufgeht, steht darunter ein Hinweis. Das ist der Unterschied
    zwischen «interessiert mich gerade nicht» und «gilt nicht» -- und nur das
    erste trifft auf einen Schalter zu, den jemand umgelegt hat.
    """

    LANGNAME: str = ""
    """
    Wie der Nachweis in der Zusammenfassung heisst, Spalte «Nachweis».
    Leer: sein Thema.

    Getrennt vom Thema, weil beide anders ordnen. Die Formelsammlung ordnet
    nach dem, was gerechnet wird -- «Zwängung auf Biegung». Die
    Zusammenfassung ordnet nach der Frage, die beantwortet wird -- «Risse:
    Zwängung Biegung», bei den anderen Rissnachweisen.
    """

    @property
    def langname(self) -> str:
        return self.LANGNAME or self.thema

    ART: str = ""
    """Das Kurzzeichen der Nachweisart in jedem Urteil -- siehe :attr:`NachweisUrteil.art`."""

    richtung = None
    """Die Tragrichtung, in der nachgewiesen wird -- ``None``, wo es keine gibt."""

    def urteilsname(self, langname: str, fall: str) -> str:
        """«Biegung und Normalkraft x – Feld»: Langname, Richtung, Fall."""
        kopf = f"{langname} {self.richtung.value}" if self.richtung is not None else langname
        return " – ".join(teil for teil in (kopf, fall) if teil)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.stille_faelle: set = set()
        """
        Welche einzelnen Faelle still bleiben, obwohl der Nachweis laeuft.

        Ein Nachweis deckt oft mehrere Faelle ab -- vier Lagen, mehrere
        Lastfaelle --, und eingeschaltet wird jeder fuer sich. Ohne diese
        Menge haette ein einzelner Haken alle vier Lagen in die Tabelle
        gehoben; der Schalter neben den anderen dreien waere wirkungslos
        geworden, ohne es zu zeigen.

        Worauf sich die Schluessel beziehen, entscheidet der Nachweis --
        Lagennummer oder Fallname. Gefragt wird ueber :meth:`leise`, und
        gefuellt ueber :meth:`stillstellen`.
        """

    def leise(self, schluessel: Any) -> bool:
        """Ob dieser Fall nur mitrechnet: einzeln oder mit dem ganzen Nachweis."""
        return self.still or schluessel in self.stille_faelle

    @staticmethod
    def massgebend(
        urteile: Sequence[NachweisUrteil],
    ) -> List[NachweisUrteil]:
        """
        Von mehreren Teilurteilen das schlechteste -- als Liste.

        Wer eine Tabelle baut, meint dieses eine; leer bleibt leer.
        """
        if not urteile:
            return []
        return [min(urteile, key=lambda u: u.erfuellungsgrad.si)]

    def protokoll_massgebend(self, p: Protokoll,
                             urteile: Sequence[NachweisUrteil]) -> None:
        """
        Welcher Teil entscheidet, wo es mehrere gibt -- etwa zwei Lagen.

        In der Zusammenfassung steht nur der schlechteste; ohne diese Zeile
        muesste man die Zahlen der Herleitung selbst vergleichen, um zu wissen,
        welcher dort gelandet ist.
        """
        massgebend = self.massgebend(urteile)
        if len(urteile) >= 2 and massgebend:
            p.text(f"Massgebend: {massgebend[0].fall} (kleinster Erfüllungsgrad).")

    def urteil(self, ziel: WertDef, fall: str, ausgang: Ausgang, begruendung: str, *,
               hinweis: str = "", art: str = "", langname: str = "",
               still: bool = False) -> NachweisUrteil:
        """
        Das Urteil eines Falls aus seinem Ausgang: erfuellt, Grad, Einwirkung
        und Widerstand. ``ziel`` ist der Erfuellungsgrad, der es traegt.

        Steht nichts gegeneinander, kommt der Grund als Hinweis in die
        Zusammenfassung -- dort fehlen sonst die Zahlen, und ein Strich
        erklaert sich nicht von selbst. Bis 2026-10-25 baute jeder Nachweis
        sein Urteil selbst, und «nicht fuehrbar» stand auf vier Arten da.
        """
        if not hinweis and isinstance(ausgang, KeinVergleich):
            hinweis = begruendung
        return NachweisUrteil(
            erfuellt=ausgang.erfuellt, erfuellungsgrad=Groesse(ausgang.grad, EINHEITSLOS),
            ziel=ziel.id, fall=fall, art=art or self.ART, langname=langname,
            begruendung=begruendung, hinweis=hinweis,
            einwirkung=ausgang.einwirkung, widerstand=ausgang.widerstand, still=still)

    @staticmethod
    def ohne_bewehrung(nummer: int) -> str:
        """Die Begruendung einer Lage ohne Stahl -- in jedem Lagennachweis dieselbe."""
        return f"{nummer}. Lage ohne Bewehrung → kein Nachweis."

    @staticmethod
    def teilurteile(
        urteile: Sequence[NachweisUrteil],
    ) -> List[NachweisUrteil]:
        """
        Dieselben Urteile, jedes als Teil derselben Frage gekennzeichnet.

        Zurueck kommt alles: gezaehlt und gerechnet wird jede Lage. Erst die
        Darstellung nimmt daraus das schlechteste -- siehe
        :attr:`NachweisUrteil.sammel`.
        """
        return [replace(u, sammel=True) for u in urteile]

    def stillstellen(self, alle: Iterable[Any], laut: Iterable[Any]) -> None:
        """
        Festlegen, welche Faelle in der Herleitung stehen und welche nur
        mitrechnen.

        Sind *alle* still, schweigt der Nachweis ganz -- sonst stuende seine
        Ueberschrift samt Ansatz ueber einer Herleitung ohne einen einzigen
        Fall darunter.

        Ein Schluessel in ``laut``, den ``alle`` nicht kennt, ist ein
        Aufbaufehler und wird gemeldet. Stillschweigend uebergangen waere er
        die unangenehmste Art von Fehler: der Nachweis verschwaende aus
        Tabelle und Herleitung, ohne dass irgendwo etwas danebenstuende --
        und gesucht wuerde er dann beim Nachweis und nicht beim Tippfehler.
        """
        alle, laut = set(alle), set(laut)
        fremd = laut - alle
        if fremd:
            raise BerechnungsFehler(
                self.id,
                f"die Fälle "
                f"{', '.join(repr(f) for f in sorted(map(str, fremd)))} "
                f"sollen laut sein, kommen aber nicht vor. Bekannt sind "
                f"{', '.join(repr(f) for f in sorted(map(str, alle)))}.")
        self.stille_faelle = alle - laut
        self.still = not (alle & laut)

    @abstractmethod
    def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        """
        Fuehrt den Nachweis und liefert Ausgabewerte samt Urteilen -- und
        einen Befund, wo jemand nach dem Lauf mehr lesen will als Zahlen.

        :return: :class:`Ausfuehrung` mit ``{Wert-ID: Groesse}``, den Urteilen
            und dem Befund
        """

    def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        pruefung = self.pruefe(e, p)
        # Der Namensraum wird hier gestempelt und nicht von den Unterklassen
        # mitgegeben: er ist immer derselbe, naemlich der des Nachweises.
        # Ebenso Langname und Name, wo die Pruefung keine eigenen nennt. Still
        # ist ein Urteil, wenn der ganze Nachweis es ist oder wenn die Pruefung
        # es einzeln so gestempelt hat -- sie kennt ihre Faelle.
        urteile = []
        for u in pruefung.urteile:
            langname = u.langname or self.langname
            urteile.append(replace(
                u, raum=self.id, langname=langname,
                name=u.name or self.urteilsname(langname, u.fall),
                still=self.still or u.still))
        # Der Grad eines Urteils ist zugleich die Ausgabe, die es traegt: die
        # Pruefung nennt ihn einmal, im Urteil. Vorher schrieb sie ihn zweimal.
        ausgaben = {**pruefung.ausgaben, **{u.ziel: u.erfuellungsgrad for u in urteile if u.ziel}}
        # Ein Grad, den kein Urteil traegt, ist unbeschraenkt: sein Fall kam in
        # dieser Rechnung nicht vor -- eine Seite ohne Bewehrung, ein Lastfall
        # ohne Last, eine Durchstanzstelle, die keine Bewehrung braucht. Bis
        # 2026-11-09 schrieb das jede Pruefung selbst, auf drei Arten.
        unbeschraenkt = Groesse(math.inf, EINHEITSLOS)
        for d in self.ausgaben:
            if d.erfuellungsgrad and d.id not in ausgaben:
                ausgaben[d.id] = unbeschraenkt
        return replace(pruefung, ausgaben=ausgaben, urteile=tuple(urteile))

    # Ein `alle_erfuellt` gab es hier einmal. Es hatte keinen Aufrufer und
    # zaehlte die stillen Urteile mit -- also das Gegenteil von dem, was
    # `Loesung.alle_nachweise_erfuellt` sagt. Zwei gleichnamige Antworten auf
    # dieselbe Frage, von denen die unbenutzte die falsche war.
