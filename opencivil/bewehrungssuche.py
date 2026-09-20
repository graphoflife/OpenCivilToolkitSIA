"""
opencivil/bewehrungssuche.py -- die Bewehrung suchen statt sie zu setzen.

VERANTWORTUNG:
Findet zu einer Platte die kleinste Bewehrung, mit der alle *eingeschalteten*
Nachweise aufgehen. Gesucht wird ueber Durchmesser und Teilung; die Anordnung
-- welche Lage es gibt und in welche Richtung sie traegt -- bleibt, wie sie
eingegeben wurde.

WARUM ES SUCHEN UND NICHT RECHNEN IST:
Eine Bewehrung liesse sich fuer einen einzelnen Nachweis geschlossen
bestimmen. Fuer alle zusammen nicht: der Duktilitaetsnachweis wird durch mehr
Stahl *schlechter*, die uebrigen besser. Zwischen beiden liegt ein Fenster,
und ob es offen ist, weiss man erst, wenn man hineingeschaut hat.

DAS VERFAHREN::

    fuer jede Teilung s aus der Liste:
        alle gesuchten Posten auf den kleinsten Durchmesser
        wiederhole:
            rechnen, alle eingeschalteten Urteile einsammeln
            gehen alle auf -> fertig
            sonst: jeden Posten einzeln einen Durchmesser groesser probieren
                   und den Schritt nehmen, der den schlechtesten
                   Erfuellungsgrad am weitesten hebt
            hebt kein Schritt ihn -> mit dieser Teilung geht es nicht
    von allen Loesungen die mit der kleinsten Stahlflaeche

Der Schritt wird also nicht geraten, sondern ausprobiert. Das kostet je Runde
eine Rechnung pro Posten -- bei rund dreissig Millisekunden je Rechnung ist
das der guenstigere Handel gegenueber einer Regel, die bei
Duktilitaetsversagen in die falsche Richtung liefe.

WELCHE NACHWEISE ZAEHLEN:
Die, die gebaut werden -- und gebaut wird nur, was eingeschaltet ist. Die
Schalter der Oberflaeche steuern also unmittelbar die Suche, ohne dass hier
eine zweite Liste gepflegt werden muesste. :class:`Suchmodus` nimmt zusaetzlich
die Einwirkungen weg, wo ohne Kraefte gesucht werden soll.
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Sequence, Tuple

#: Lieferbare Stabdurchmesser in mm, aufsteigend. Die Suche geht sie der
#: Reihe nach durch; was nicht in der Liste steht, kommt nicht heraus.
DURCHMESSER: Tuple[float, ...] = (8, 10, 12, 14, 16, 18, 20, 22, 26)

#: Teilungen in mm, die ohne eigene Angabe versucht werden.
TEILUNGEN: Tuple[float, ...] = (100.0, 150.0)

#: Obergrenze der Runden je Teilung. Mehr Runden als Posten mal Durchmesser
#: kann es nicht geben -- die Zahl ist der Riegel gegen einen Denkfehler.
RUNDEN = 60


class Suchmodus(str, Enum):
    """Was gesucht wird und wogegen."""

    GRUND_OHNE = "grund_ohne"
    """
    Nur die Grundbewehrung, ohne Einwirkungen.

    Es bleiben die Nachweise, die keine Schnittgroessen brauchen:
    Duktilitaet, sproedes Versagen und die Rissbreitenbegrenzung unter
    Zwaengung. Das ist die Bewehrung, die eine Platte unabhaengig von der
    Belastung braucht.
    """

    GRUND_MIT = "grund_mit"
    """Nur die Grundbewehrung, aber gegen alle Nachweise."""

    GRUND_OHNE_ZULAGE_MIT = "grund_ohne_zulage_mit"
    """
    Zwei Schritte: erst die Grundbewehrung ohne Kraefte, dann die Zulage
    gegen alle Nachweise. So traegt die Grundbewehrung die Anforderungen der
    Platte und die Zulage die der Belastung -- getrennt sichtbar.
    """

    @property
    def beschriftung(self) -> str:
        return {
            Suchmodus.GRUND_OHNE: "Grundbewehrung ohne Kräfte",
            Suchmodus.GRUND_MIT: "Grundbewehrung mit Kräften",
            Suchmodus.GRUND_OHNE_ZULAGE_MIT:
                "Grundbewehrung ohne Kräfte, Zulage mit Kräften",
        }[self]


#: Ein gesuchter Posten: Lagennummer (1..4) und Art ('grund' oder 'zulage').
Posten = Tuple[int, str]


@dataclass
class Schritt:
    """Eine Runde der Suche -- fuer die Mitschrift in der Oberflaeche."""

    runde: int
    durchmesser: Dict[str, float]
    schlechtester: float
    """Kleinster Erfuellungsgrad dieser Runde."""

    nachweis: str
    """Welcher Nachweis ihn hatte."""


@dataclass
class Loesung:
    """Was fuer eine Teilung herauskam."""

    teilung: float
    gefunden: bool = False
    durchmesser: Dict[str, float] = field(default_factory=dict)
    """Posten (``'1g'``, ``'4z'``, …) auf Durchmesser in mm."""

    stahlflaeche: float = 0.0
    """Summe der Bewehrungsquerschnitte in mm²/Streifen."""

    schlechtester: float = 0.0
    nachweis: str = ""
    begruendung: str = ""
    schritte: List[Schritt] = field(default_factory=list)


@dataclass
class Suchergebnis:
    """Das Ganze: je Teilung eine Loesung, und welche gewonnen hat."""

    modus: Suchmodus
    loesungen: List[Loesung] = field(default_factory=list)
    beste: Optional[Loesung] = None
    begruendung: str = ""
    duktilitaet: str = ""
    """
    Was der Duktilitaetsnachweis zur gefundenen Bewehrung sagt.

    Gesucht wird ohne ihn -- er wird durch mehr Stahl schlechter, und eine
    Suche, die von unten aufsteigt, hat gegen ihn kein Mittel. Verschwiegen
    wird er deshalb nicht: hier steht, ob er mit dem Ergebnis noch aufgeht.
    """

    @property
    def gefunden(self) -> bool:
        return self.beste is not None


# ===========================================================================
# Zugriff auf einen Posten
# ===========================================================================

def _posten(eintrag, lage: int, art: str) -> dict:
    return getattr(eintrag.lagen[lage - 1], art)


def _marke(lage: int, art: str) -> str:
    return f"{lage}{'g' if art == 'grund' else 'z'}"


def _gesuchte(eintrag, *, arten: Sequence[str]) -> List[Posten]:
    """
    Welche Posten die Suche anfasst.

    Nur solche, die es schon gibt: ein Durchmesser von null heisst, dass diese
    Lage nicht bewehrt werden soll, und das ist eine Entscheidung ueber die
    Anordnung. Die trifft die Suche nicht -- sie wuerde sonst Lagen erfinden,
    die niemand bestellt hat.
    """
    gefunden = []
    for lage in range(1, len(eintrag.lagen) + 1):
        for art in arten:
            if _posten(eintrag, lage, art).durchmesser > 0:
                gefunden.append((lage, art))
    return gefunden


def _flaeche(eintrag, posten: Sequence[Posten], teilung: float,
             breite: float) -> float:
    """Stahlquerschnitt aller gesuchten Posten, in mm²."""
    summe = 0.0
    for lage, art in posten:
        d = _posten(eintrag, lage, art).durchmesser
        if d <= 0:
            continue
        summe += math.pi * d * d / 4.0 * (breite / teilung)
    return summe


# ===========================================================================
# Bewerten
# ===========================================================================

@dataclass
class Bewertung:
    """Wie weit eine Bewehrung von der Erfuellung entfernt ist."""

    rueckstand: float
    """
    Summe der Fehlbetraege, ``sum(max(0, 1 - alpha))`` ueber alle Nachweise.

    **Nicht** der schlechteste Grad. Der war die erste Fassung, und er hat die
    Suche zum Stehen gebracht: halten zwei Nachweise gleichzeitig das Minimum
    -- etwa sproedes Versagen in der 1. und in der 4. Lage bei gleicher
    Bewehrung --, dann hebt kein einzelner Schritt es, weil der jeweils andere
    stehen bleibt. Die Suche sah eine Ebene und gab auf, obwohl der naechste
    Durchmesser offensichtlich geholfen haette.

    Die Summe der Fehlbetraege kennt diese Ebene nicht: sie faellt, sobald
    *irgendein* unerfuellter Nachweis besser wird. Null heisst genau, dass
    alle aufgehen.
    """

    grad: float
    """Der schlechteste Erfuellungsgrad -- nur zum Berichten."""

    nachweis: str
    anzahl: int
    """Wie viele Urteile ueberhaupt gefaellt wurden."""

    fehler: str = ""

    @property
    def erfuellt(self) -> bool:
        return not self.fehler and self.rueckstand <= 0.0


def bewerte(projekt) -> Bewertung:
    """
    Rechnen und sagen, wie weit es noch ist.

    Gezaehlt wird jedes Urteil, das entsteht -- und es entsteht nur, was
    eingeschaltet ist. Eine zweite Liste, welche Nachweise zaehlen, gaebe es
    hier also nur, um mit der ersten auseinanderzulaufen; der
    Duktilitaetsnachweis wird darum nicht hier uebergangen, sondern in
    :func:`_arbeitskopie` abgeschaltet.
    """
    try:
        aufbau = projekt.aufbauen(schnell=True)
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
    except Exception as fehler:      # Eine unmoegliche Bewehrung ist kein
        return Bewertung(math.inf, 0.0, "", 0, str(fehler))  # Absturz, sondern ein Nein.

    rueckstand, schlechtester, name = 0.0, math.inf, ""
    for u in loesung.urteile:
        grad = u.erfuellungsgrad.si
        rueckstand += max(0.0, 1.0 - grad)
        if grad < schlechtester:
            schlechtester, name = grad, f"{u.langname or u.art}: {u.fall}"
    return Bewertung(rueckstand, schlechtester, name, len(loesung.urteile))


# ===========================================================================
# Suchen
# ===========================================================================

def _arbeitskopie(projekt, kennung: str, *, kraefte: bool):
    """
    Die Platte, gegen die gesucht wird -- ohne das, was die Suche nicht fuehren
    kann.

    **Ohne Duktilitaet, immer.** Sie ist der einzige Nachweis, der durch mehr
    Bewehrung *schlechter* wird: er begrenzt die Druckzonenhoehe, und die
    waechst mit der Stahlflaeche. Eine Suche, die von unten aufsteigt, kann ihn
    darum nicht erfuellen, sondern nur verletzen -- sie haette gegen ihn kein
    Mittel ausser aufzugeben. Also bleibt er draussen, und das Ergebnis sagt
    hinterher, ob er mit der gefundenen Bewehrung noch aufgeht.

    Ohne ``kraefte`` fallen zusaetzlich Kombinationen, Knickfaelle und
    haeufige Lastfaelle weg. Uebrig bleiben die Nachweise, die eine Platte
    unabhaengig von der Belastung erfuellen muss.

    Abgeschaltet wird hier und nicht beim Bewerten: gebaut wird nur, was
    eingeschaltet ist, und gezaehlt wird, was gebaut wurde. An dieser einen
    Regel soll die Suche nichts vorbeischmuggeln.
    """
    kopie = copy.deepcopy(projekt)
    # **Nur diese Platte.** Die anderen kann die Suche nicht beeinflussen; ihre
    # Nachweise wuerden den Rueckstand trotzdem mittragen, und eine Platte, die
    # aus ganz eigenen Gruenden nicht aufgeht, liesse jede Suche im Projekt
    # scheitern. Genau daran ist die erste Fassung gestorben: an einer
    # frischen Platte, neben der eine andere stand.
    kopie.querschnitte = [q for q in kopie.querschnitte if q.kennung == kennung]
    eintrag = kopie.querschnitt(kennung)
    eintrag.duktilitaet = [False] * len(eintrag.duktilitaet)
    if not kraefte:
        eintrag.kombinationen = []
        eintrag.knickfaelle = []
        eintrag.haeufige = []
    return kopie


def _eine_teilung(projekt, kennung: str, teilung: float,
                  posten: Sequence[Posten],
                  durchmesser: Sequence[float]) -> Loesung:
    """
    Die kleinste Bewehrung bei dieser Teilung -- oder die Auskunft, dass es
    keine gibt.

    Aufgestiegen wird von unten: alle Posten auf den kleinsten Durchmesser,
    dann Runde fuer Runde den Schritt nehmen, der am meisten bringt.
    """
    eintrag = projekt.querschnitt(kennung)
    loesung = Loesung(teilung=teilung)
    if not posten:
        loesung.begruendung = (
            "Keine Bewehrung zum Suchen: alle Lagen stehen auf null. Wer eine "
            "Lage bewehrt haben will, gibt ihr einen Durchmesser.")
        return loesung

    stand = {p: 0 for p in posten}

    def setzen() -> None:
        for (lage, art), i in stand.items():
            eintrag_posten = _posten(eintrag, lage, art)
            eintrag_posten.durchmesser = durchmesser[i]
            # Die Teilung gilt fuer beide Posten einer Lage gleich -- sonst
            # liessen sich Grundbewehrung und Zulage nicht gemeinsam verlegen.
            eintrag_posten.abstand = teilung
            eintrag_posten.anzahl = None

    def stand_als_dict() -> Dict[str, float]:
        return {_marke(l, a): durchmesser[i] for (l, a), i in stand.items()}

    setzen()
    bewertung = bewerte(projekt)
    for runde in range(1, RUNDEN + 1):
        loesung.schritte.append(Schritt(
            runde=runde, durchmesser=stand_als_dict(),
            schlechtester=bewertung.grad, nachweis=bewertung.nachweis))

        if bewertung.fehler:
            loesung.begruendung = bewertung.fehler
            return loesung
        if bewertung.erfuellt:
            loesung.gefunden = True
            loesung.durchmesser = stand_als_dict()
            loesung.schlechtester = bewertung.grad
            loesung.nachweis = bewertung.nachweis
            loesung.stahlflaeche = _flaeche(eintrag, posten, teilung,
                                            eintrag.b)
            return loesung

        # Jeden Posten einzeln einen Schritt groesser probieren. Genommen wird
        # der, der den schlechtesten Erfuellungsgrad am weitesten hebt -- und
        # nur, wenn er ihn ueberhaupt hebt. Beim Duktilitaetsnachweis tut das
        # keiner, denn dort ist mehr Stahl das Problem.
        bester: Optional[Tuple[float, Posten, Bewertung]] = None
        for p in posten:
            if stand[p] + 1 >= len(durchmesser):
                continue
            stand[p] += 1
            setzen()
            versuch = bewerte(projekt)
            stand[p] -= 1
            if versuch.fehler:
                continue
            if bester is None or versuch.rueckstand < bester[0]:
                bester = (versuch.rueckstand, p, versuch)
        setzen()

        if bester is None:
            loesung.begruendung = (
                f"Alle Durchmesser der Liste ausgeschöpft; der schlechteste "
                f"Erfüllungsgrad bleibt bei {bewertung.grad:.2f} "
                f"({bewertung.nachweis}).")
            return loesung
        if bester[0] >= bewertung.rueckstand:
            loesung.begruendung = (
                f"Mehr Stahl bringt nichts mehr: «{bewertung.nachweis}» steht "
                f"bei {bewertung.grad:.2f} und wird durch keinen grösseren "
                f"Durchmesser besser. Hier hilft nur eine dickere Platte oder "
                f"ein festerer Beton.")
            loesung.schlechtester = bewertung.grad
            loesung.nachweis = bewertung.nachweis
            return loesung

        stand[bester[1]] += 1
        setzen()
        bewertung = bester[2]

    loesung.begruendung = f"Nach {RUNDEN} Runden keine Lösung."
    return loesung


def suche(projekt, kennung: str, *,
          modus: Suchmodus = Suchmodus.GRUND_OHNE,
          teilungen: Sequence[float] = TEILUNGEN,
          durchmesser: Sequence[float] = DURCHMESSER) -> Suchergebnis:
    """
    Die kleinste Bewehrung, mit der alle eingeschalteten Nachweise aufgehen.

    Zurueck kommt ein :class:`Suchergebnis`; das Projekt selbst bleibt
    unberuehrt. Wer die gefundene Bewehrung uebernehmen will, ruft
    :func:`uebernehmen`.
    """
    ergebnis = Suchergebnis(modus=Suchmodus(modus))
    teilungen = [t for t in teilungen if t > 0] or list(TEILUNGEN)
    durchmesser = sorted(d for d in durchmesser if d > 0) or list(DURCHMESSER)

    for teilung in sorted(teilungen):
        loesung = _fuer_teilung(projekt, kennung, teilung,
                                ergebnis.modus, durchmesser)
        ergebnis.loesungen.append(loesung)

    gefunden = [l for l in ergebnis.loesungen if l.gefunden]
    if not gefunden:
        ergebnis.begruendung = (
            "Mit keiner der angegebenen Teilungen gehen alle eingeschalteten "
            "Nachweise auf." + _leere_lagen(projekt.querschnitt(kennung)))
        return ergebnis
    if gefunden:
        # Kleinste Stahlflaeche gewinnt. Bei Gleichstand die groessere
        # Teilung: weniger Staebe bei gleichem Querschnitt ist weniger Arbeit.
        ergebnis.beste = min(gefunden, key=lambda l: (l.stahlflaeche, -l.teilung))
        ergebnis.begruendung = (
            f"Teilung {ergebnis.beste.teilung:.0f} mm mit "
            f"{ergebnis.beste.stahlflaeche:.0f} mm² – die kleinste "
            f"Stahlfläche unter den {len(gefunden)} Lösungen.")
    ergebnis.duktilitaet = _duktilitaetsbefund(projekt, kennung, ergebnis.beste)
    return ergebnis


def _leere_lagen(eintrag) -> str:
    """
    Der haeufigste Grund fuer ein Nein -- und einer, der nicht nach einem
    Rechenproblem aussieht.

    Wo kein Durchmesser steht, legt die Suche keinen an: welche Lage es gibt
    und wohin sie traegt, ist eine Anordnung und keine Suche. Ein Nachweis in
    einer unbewehrten Richtung kann darum nie aufgehen, und die Meldung soll
    das sagen statt ueber Durchmesser zu klagen.
    """
    leer = [nummer for nummer in (1, 2, 3, 4)
            if eintrag.lagen[nummer - 1].grund.durchmesser <= 0]
    # Nur melden, wenn eine ganze Tragrichtung leer ist. Eine einzelne leere
    # Lage neben einer bewehrten in derselben Richtung ist der Normalfall und
    # kein Grund fuer irgendetwas.
    ohne = [r for r in ("x", "y")
            if all(eintrag.richtung_von(n).value != r or n in leer
                   for n in (1, 2, 3, 4))]
    if not ohne:
        return ""
    welche = " und ".join(ohne)
    return (f" In {welche}-Richtung trägt keine Lage einen Durchmesser – dort "
            f"legt die Suche keine Bewehrung an, weil die Anordnung eine "
            f"Entscheidung ist und keine Rechnung. Ein Nachweis in dieser "
            f"Richtung kann so nicht aufgehen.")


def _duktilitaetsbefund(projekt, kennung: str, loesung: "Loesung") -> str:
    """Ob die gefundene Bewehrung die Druckzone noch genuegend begrenzt."""
    probe = copy.deepcopy(projekt)
    uebernehmen(probe, kennung, loesung)
    probe.querschnitte = [q for q in probe.querschnitte if q.kennung == kennung]
    eintrag = probe.querschnitt(kennung)
    if not any(eintrag.duktilitaet):
        return ""
    eintrag.kombinationen = []
    eintrag.knickfaelle = []
    eintrag.haeufige = []
    bewertung = bewerte(probe)
    if bewertung.erfuellt:
        return "Der Duktilitätsnachweis geht damit auf."
    return (f"Achtung: der Duktilitätsnachweis geht damit **nicht** auf – "
            f"«{bewertung.nachweis}» bei {bewertung.grad:.2f}. Gegen ihn hilft "
            f"keine stärkere Bewehrung, sondern nur eine dickere Platte; "
            f"gesucht wurde deshalb ohne ihn.")


def _fuer_teilung(projekt, kennung: str, teilung: float, modus: Suchmodus,
                  durchmesser: Sequence[float]) -> Loesung:
    """Eine Teilung, je nach Modus in einem oder zwei Schritten."""
    if modus is Suchmodus.GRUND_MIT:
        arbeit = _arbeitskopie(projekt, kennung, kraefte=True)
        posten = _gesuchte(arbeit.querschnitt(kennung), arten=("grund",))
        return _eine_teilung(arbeit, kennung, teilung, posten, durchmesser)

    if modus is Suchmodus.GRUND_OHNE:
        arbeit = _arbeitskopie(projekt, kennung, kraefte=False)
        posten = _gesuchte(arbeit.querschnitt(kennung), arten=("grund",))
        return _eine_teilung(arbeit, kennung, teilung, posten, durchmesser)

    # Zwei Schritte: erst die Grundbewehrung ohne Kraefte, dann die Zulage
    # gegen alles. Der zweite Schritt uebernimmt die Durchmesser des ersten.
    ohne = _arbeitskopie(projekt, kennung, kraefte=False)
    grund_posten = _gesuchte(ohne.querschnitt(kennung), arten=("grund",))
    erst = _eine_teilung(ohne, kennung, teilung, grund_posten, durchmesser)
    if not erst.gefunden:
        erst.begruendung = (
            "Schon die Grundbewehrung ohne Kräfte geht nicht auf: "
            + erst.begruendung)
        return erst

    arbeit = _arbeitskopie(projekt, kennung, kraefte=True)
    eintrag = arbeit.querschnitt(kennung)
    for lage, art in grund_posten:
        p = _posten(eintrag, lage, art)
        p.durchmesser = erst.durchmesser[_marke(lage, art)]
        p.abstand = teilung
        p.anzahl = None
    # Eine Zulage gehoert zu einer bewehrten Lage, nicht zu einer leeren --
    # gesucht wird sie darum ueberall dort, wo eine Grundbewehrung liegt. Die
    # Null steht in der Liste vorne: keine Zulage ist ein gueltiges Ergebnis
    # und zugleich der Anfang der Suche.
    zulage_posten = [(lage, "zulage") for lage, _ in grund_posten]
    zweit = _eine_teilung(arbeit, kennung, teilung, zulage_posten,
                          [0.0, *durchmesser])
    zweit.durchmesser = {**erst.durchmesser, **zweit.durchmesser}
    zweit.stahlflaeche = _flaeche(eintrag, grund_posten + zulage_posten,
                                  teilung, eintrag.b)
    zweit.schritte = erst.schritte + zweit.schritte
    return zweit


# ===========================================================================
# Querkraftbewehrung
# ===========================================================================

@dataclass
class Buegelloesung:
    """Was die Suche nach den Buegeln gefunden hat."""

    gefunden: bool = False
    durchmesser: float = 0.0
    teilung: float = 0.0
    """Teilung in beiden Richtungen -- ein Buegelraster ist quadratisch."""

    stahlvolumen: float = 0.0
    """Buegelquerschnitt je Flaecheneinheit, in mm²/m² -- das Mass, nach dem
    verglichen wird. Bei Buegeln zaehlt nicht die Flaeche je Streifen, sondern
    wie dicht sie stehen."""

    begruendung: str = ""


def buegel_suchen(projekt, kennung: str, *,
                  teilungen: Sequence[float] = TEILUNGEN,
                  durchmesser: Sequence[float] = DURCHMESSER) -> Buegelloesung:
    """
    Die duennsten Buegel, mit denen der Querkraftnachweis aufgeht.

    Gesucht wird ueber Durchmesser und Rasterweite; das Raster ist quadratisch
    (``s_x = s_y``), weil eine Platte in beiden Richtungen gleich durchstanzt
    wird. Verglichen wird ueber den Buegelquerschnitt je Flaecheneinheit --
    ein dicker Stab weit auseinander kann weniger Stahl sein als ein duenner
    eng, und teurer ist er trotzdem seltener.

    Geht es ohne Buegel, kommt das heraus: Durchmesser null.
    """
    teilungen = sorted(t for t in teilungen if t > 0) or list(TEILUNGEN)
    durchmesser = sorted(d for d in durchmesser if d > 0) or list(DURCHMESSER)

    arbeit = _arbeitskopie(projekt, kennung, kraefte=True)
    eintrag = arbeit.querschnitt(kennung)
    buegel = eintrag.querkraftbewehrung

    # Erst ohne: was man nicht braucht, soll nicht eingebaut werden.
    buegel.durchmesser = 0
    if bewerte(arbeit).erfuellt:
        return Buegelloesung(
            gefunden=True, durchmesser=0.0, teilung=0.0,
            begruendung="Ohne Querkraftbewehrung geht es auf.")

    beste: Optional[Buegelloesung] = None
    for teilung in teilungen:
        buegel.abstand_x = teilung
        buegel.abstand_y = teilung
        buegel.anzahl_y = None
        for d in durchmesser:
            buegel.durchmesser = d
            if not bewerte(arbeit).erfuellt:
                continue
            volumen = math.pi * d * d / 4.0 / (teilung * teilung) * 1e6
            if beste is None or volumen < beste.stahlvolumen:
                beste = Buegelloesung(
                    gefunden=True, durchmesser=d, teilung=teilung,
                    stahlvolumen=volumen,
                    begruendung=(f"⌀{d:.0f}@{teilung:.0f} – "
                                 f"{volumen:.0f} mm²/m²."))
            break        # Groessere Durchmesser bei derselben Teilung sind
                         # nur mehr Stahl fuer dieselbe Aussage.
    if beste is None:
        return Buegelloesung(begruendung=(
            "Mit keinem Durchmesser der Liste und keiner der angegebenen "
            "Teilungen geht der Querkraftnachweis auf."))
    return beste


def buegel_uebernehmen(projekt, kennung: str, loesung: Buegelloesung) -> None:
    """Die gefundenen Buegel in die Platte schreiben."""
    buegel = projekt.querschnitt(kennung).querkraftbewehrung
    buegel.durchmesser = loesung.durchmesser
    if loesung.teilung > 0:
        buegel.abstand_x = loesung.teilung
        buegel.abstand_y = loesung.teilung
        buegel.anzahl_y = None


def uebernehmen(projekt, kennung: str, loesung: Loesung) -> None:
    """Die gefundenen Durchmesser und die Teilung in die Platte schreiben."""
    eintrag = projekt.querschnitt(kennung)
    for marke, d in loesung.durchmesser.items():
        lage = int(marke[:-1])
        art = "grund" if marke[-1] == "g" else "zulage"
        p = _posten(eintrag, lage, art)
        p.durchmesser = d
        p.abstand = loesung.teilung
        p.anzahl = None
