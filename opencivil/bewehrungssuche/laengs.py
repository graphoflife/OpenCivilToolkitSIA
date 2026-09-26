"""
opencivil/bewehrungssuche/laengs.py -- die Laengsbewehrung suchen.

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

DER MINDESTDURCHMESSER:
Die Grundbewehrung jeder Lage ist mindestens so dick -- in x beginnt die
Suche dort und nicht bei null, und eine y-Lage, die duenner ist oder fehlt,
hebt sie darauf an (:func:`_y_ableiten`). Eine Platte hat oben und unten
in beiden Richtungen ein Netz; eine Lage, die kein Nachweis verlangt, blieb
sonst leer. Die Zulage darf weiter fehlen. Ohne Mindestdurchmesser (null)
darf auch eine Lage leer bleiben.

DIE OBERGRENZE:
Mehr Querschnitt als ``automatik_grenze`` (Grund und Zulage zusammen, in
mm²/m) bekommt keine x-Lage -- einen Schritt darueber nimmt die Suche gar
nicht erst in Betracht. Damit auch ⌀30@150 erreichbar ist, reicht die Liste
der Durchmesser bis ⌀40; die Grenze haelt die Suche im Zaum.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, List, Optional, Sequence, Tuple

from opencivil.bewehrungssuche.bewertung import Bewertung, arbeitskopie, bewerte
from opencivil.querschnitt.platte import Richtung

if TYPE_CHECKING:
    from opencivil.projekt import LageEintrag

#: Lieferbare Stabdurchmesser in mm, aufsteigend. Die Suche geht sie der
#: Reihe nach durch; was nicht in der Liste steht, kommt nicht heraus. Wie
#: dick es wird, begrenzt die Obergrenze der Platte (``automatik_grenze``).
DURCHMESSER: Tuple[float, ...] = (8, 10, 12, 14, 16, 18, 20, 22, 26, 30, 34, 40)
#: Teilungen in mm, die ohne eigene Angabe versucht werden. Die eine
#: uebliche -- jede weitere kostet einen vollstaendigen Suchlauf.
TEILUNGEN: Tuple[float, ...] = (150.0,)

#: Kleinster Durchmesser, den die Suche einbaut -- und den die
#: Grundbewehrung jeder Lage mindestens hat. Duenner lohnt sich nicht: die
#: Ersparnis ist gering, und auf der Baustelle will niemand vier
#: Stabdurchmesser auseinanderhalten.
MINDESTDURCHMESSER = 10.0

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

    DICKE_GRUND_MIT = "dicke_grund_mit"
    """Die duennste Platte, bei der :attr:`GRUND_MIT` eine Loesung findet."""

    DICKE_GRUND_OHNE_ZULAGE_MIT = "dicke_grund_ohne_zulage_mit"
    """Dasselbe mit :attr:`GRUND_OHNE_ZULAGE_MIT`."""

    @property
    def beschriftung(self) -> str:
        return {
            Suchmodus.GRUND_OHNE: "Grundbew. ohne Kräfte",
            Suchmodus.GRUND_MIT: "Grundbew. mit Kräften",
            Suchmodus.GRUND_OHNE_ZULAGE_MIT:
                "Grundbew. ohne Kräfte, Zulage mit Kräften",
            Suchmodus.DICKE_GRUND_MIT:
                "Plattendicke optimieren, Grundbew. mit Kräften",
            Suchmodus.DICKE_GRUND_OHNE_ZULAGE_MIT:
                "Plattendicke optimieren, Grundbew. ohne Kräfte, Zulage mit Kräften",
        }[self]

    @property
    def bewehrung(self) -> "Suchmodus":
        """Wonach je Dicke die Bewehrung gesucht wird -- sonst der Modus selbst."""
        return {
            Suchmodus.DICKE_GRUND_MIT: Suchmodus.GRUND_MIT,
            Suchmodus.DICKE_GRUND_OHNE_ZULAGE_MIT: Suchmodus.GRUND_OHNE_ZULAGE_MIT,
        }.get(self, self)

    @property
    def mit_dicke(self) -> bool:
        """Ob auch die Plattendicke gesucht wird."""
        return self.bewehrung is not self


#: Ein gesuchter Posten: Lagennummer (1..4) und Art ('grund' oder 'zulage').
Posten = Tuple[int, str]


@dataclass
class Loesung:
    """Was fuer eine Teilung herauskam."""

    teilung: float
    gefunden: bool = False
    lagen: List["LageEintrag"] = field(default_factory=list)
    """
    Die vier Lagen, wie die Suche sie hinterlaesst -- die Platte selbst,
    nicht eine Beschreibung davon.

    Frueher stand hier ein Woerterbuch aus Marken (``'2g'``, ``'3z'``) auf
    Durchmesser. :func:`uebernehmen` musste die Marken wieder zerlegen, eine
    eigene Funktion Luecken mit null fuellen, und jede Regel fuer die y-Lagen
    -- «wie x», «mindestens» -- brauchte dort noch einmal einen Sonderfall.
    Die Suche hat die fertige Platte aber ohnehin in der Hand.
    """

    stahlflaeche: float = 0.0
    """Summe der Bewehrungsquerschnitte aller Lagen, in mm² ueber die
    Breite ``b`` -- das Mass, nach dem die Teilungen verglichen werden."""

    schlechtester: float = 0.0
    nachweis: str = ""
    begruendung: str = ""


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

    duktilitaet_erfuellt: Optional[bool] = None
    """Dasselbe als Ja/Nein -- ``None``: nichts zu sagen, keine x-Lage bewehrt."""

    @property
    def gefunden(self) -> bool:
        return self.beste is not None


# ===========================================================================
# Zugriff auf einen Posten
# ===========================================================================

def _posten(eintrag, lage: int, art: str) -> dict:
    return getattr(eintrag.lagen[lage - 1], art)


def _gesuchte(eintrag, *, arten: Sequence[str]) -> List[Posten]:
    """
    Welche Posten die Suche anfasst: die der Tragrichtung x.

    Auch die, die gerade auf null stehen. Frueher blieben die draussen -- eine
    leere Lage galt als Entscheidung ueber die Anordnung, die die Suche nicht
    treffen sollte. Das war zu vorsichtig: wer die Bewehrung ermitteln laesst,
    will wissen, *wo* welche hingehoert, und nicht bloss, wie dick die schon
    eingetragene wird.

    Die y-Lagen bleiben, wie sie sind. Nachgewiesen wird in y nichts, also
    gaebe es dort auch kein Mass, an dem sich ein Durchmesser bemessen liesse
    -- die Suche wuerde sie auf null ziehen, und genau das waere falsch: die
    y-Bewehrung liegt aussen und bestimmt, wieviel statische Hoehe der
    x-Bewehrung bleibt. Was dort liegt, sagt der Benutzer -- oder er laesst
    die y-Grundbewehrung der x-Grundbewehrung folgen. Duenner als der
    Mindestdurchmesser bleibt sie aber nicht (beides :func:`_y_ableiten`).

    Null ist der Anfang der Zulage -- und der Grundbewehrung nur ohne
    Mindestdurchmesser (siehe :func:`suche`).
    """
    return [(lage, art)
            for lage in range(1, len(eintrag.lagen) + 1)
            if eintrag.richtung_von(lage) is Richtung.X
            for art in arten]


def stufen(durchmesser: Sequence[float], mindest: float, *,
           leer: bool = True) -> List[float]:
    """
    Die Durchmesser, die zur Auswahl stehen -- mit der Null davor, wenn der
    Posten fehlen darf (``leer``).

    Die Null heisst «nicht vorhanden» und ist dann die unterste Stufe; von ihr
    aus steigt die Suche. Darueber kommt nichts unter ``mindest``: ein aktiver
    Stab soll nicht duenner sein als das, was man verlegen will.
    """
    grosse = sorted(d for d in durchmesser if d >= max(mindest, 0.0) and d > 0)
    if not grosse:
        grosse = [max(mindest, min(DURCHMESSER))]
    return [0.0, *grosse] if leer else grosse


@dataclass(frozen=True)
class Stufen:
    """
    Welche Durchmesser ein Posten der Reihe nach annimmt -- je Art eine
    Liste, jede beginnt mit ihrer untersten Stufe.

    Die Zulage darf fehlen: ihre Liste beginnt bei null. Die Grundbewehrung
    beginnt mit Mindestdurchmesser bei ihm, eine Lage ohne Grundbewehrung gibt
    es dann nicht (siehe «Der Mindestdurchmesser» oben). Vorher lag das in
    einem Index, der durch vier Funktionen gereicht wurde: bei welcher Stufe
    die Grundbewehrung anfaengt.
    """

    grund: Tuple[float, ...]
    zulage: Tuple[float, ...]

    @classmethod
    def aus(cls, durchmesser: Sequence[float], mindest: float) -> "Stufen":
        return cls(grund=tuple(stufen(durchmesser, mindest, leer=mindest <= 0)),
                   zulage=tuple(stufen(durchmesser, mindest)))

    def von(self, posten: Posten) -> Tuple[float, ...]:
        return self.grund if posten[1] == "grund" else self.zulage

    @property
    def mindest(self) -> float:
        """Der duennste Grundstab -- null, wenn eine Lage leer bleiben darf."""
        return self.grund[0]


def _seiten(eintrag) -> List[Tuple[int, int]]:
    """Je Seite das Paar (x-Lage, y-Lage): unten 1 und 2, oben 3 und 4."""
    return [(a, b) if eintrag.richtung_von(a) is Richtung.X else (b, a)
            for a, b in ((1, 2), (3, 4))]


def _y_ableiten(eintrag, mindest: float, teilung: float) -> None:
    """
    Was die Suche an den y-Lagen tut -- die eine Regel dafuer.

    Folgt y der x-Grundbewehrung (``automatik_y_wie_x``), bekommt jede Seite
    die x-Grundbewehrung dieser Seite. Sonst wird eine y-Grundbewehrung, die
    duenner ist als der Mindestdurchmesser oder fehlt, auf ihn gehoben, mit
    der gesuchten Teilung; eine dickere bleibt, wie sie ist -- mindestens
    heisst nicht genau.

    Nach jedem Setzen und nicht erst beim Uebernehmen: liegt y aussen, kostet
    ihr Durchmesser x die statische Hoehe, und gesucht werden soll mit der
    Bewehrung, die hinterher dasteht.
    """
    if eintrag.automatik_y_wie_x:
        for x, y in _seiten(eintrag):
            vorbild, folger = _posten(eintrag, x, "grund"), _posten(eintrag, y, "grund")
            folger.durchmesser = vorbild.durchmesser
            folger.abstand = vorbild.abstand
            folger.anzahl = vorbild.anzahl
        return
    for nummer, lage in enumerate(eintrag.lagen, start=1):
        if eintrag.richtung_von(nummer) is not Richtung.X and lage.grund.durchmesser < mindest:
            lage.grund.durchmesser = mindest
            lage.grund.abstand = teilung
            lage.grund.anzahl = None


def _ueber_grenze(eintrag, grenze: float) -> bool:
    """Ob eine x-Lage mehr Querschnitt traegt, als die Obergrenze erlaubt (mm²/m)."""
    return any(
        lage.grund.je_meter(eintrag.b) + lage.zulage.je_meter(eintrag.b) > grenze * (1 + 1e-9)
        for nummer, lage in enumerate(eintrag.lagen, start=1)
        if eintrag.richtung_von(nummer) is Richtung.X)


def _stahlflaeche(eintrag) -> float:
    """Stahlquerschnitt aller Lagen, in mm² ueber die Breite ``b``."""
    return sum(lage.grund.je_meter(eintrag.b) + lage.zulage.je_meter(eintrag.b)
               for lage in eintrag.lagen) * eintrag.b / 1000.0


# ===========================================================================
# Suchen
# ===========================================================================

def _eine_teilung(projekt, kennung: str, teilung: float,
                  posten: Sequence[Posten], stufen: Stufen) -> Loesung:
    """
    Die kleinste Bewehrung bei dieser Teilung -- oder die Auskunft, dass es
    keine gibt.

    Aufgestiegen wird von unten: jeder Posten auf der untersten Stufe seiner
    Liste (:class:`Stufen`), dann Runde fuer Runde den Schritt nehmen, der am
    meisten bringt.

    Ohne Mindestdurchmesser ist der Anfang darum ein Querschnitt, den es so
    gar nicht geben kann; er liefert keinen Rueckstand, sondern einen Fehler,
    und das ist kein Abbruch, sondern der Grund, ueberhaupt einen Schritt zu
    suchen.
    """
    eintrag = projekt.querschnitt(kennung)
    loesung = Loesung(teilung=teilung)
    grenze = eintrag.automatik_grenze.je_meter

    # Wie viele Urteile die voll bewehrte Platte faellt. Weniger darf am Ende
    # nicht herauskommen -- siehe Bewertung.erfuellt.
    stand = {p: len(stufen.von(p)) - 1 for p in posten}

    def setzen() -> None:
        for (lage, art), i in stand.items():
            _posten(eintrag, lage, art).durchmesser = stufen.von((lage, art))[i]
        # Die Teilung gilt fuer beide Posten einer gesuchten Lage gleich --
        # sonst liessen sich Grundbewehrung und Zulage nicht gemeinsam
        # verlegen. Auch fuer den, der gerade nicht gesucht wird.
        for lage in {lage for lage, _ in posten}:
            for art in ("grund", "zulage"):
                _posten(eintrag, lage, art).abstand = teilung
                _posten(eintrag, lage, art).anzahl = None
        _y_ableiten(eintrag, stufen.mindest, teilung)

    setzen()
    erwartet = bewerte(projekt).anzahl
    for p in posten:
        stand[p] = 0
    setzen()
    if _ueber_grenze(eintrag, grenze):
        loesung.begruendung = (
            f"Schon die Grundbewehrung mit Mindestdurchmesser liegt über der "
            f"Obergrenze {grenze:.0f} mm²/m je Lage.")
        return loesung
    bewertung = bewerte(projekt)
    for _ in range(RUNDEN):
        if bewertung.erfuellt(erwartet):
            bewertung = _absteigen(projekt, posten, stand,
                                   setzen, bewertung, erwartet)
            loesung.gefunden = True
            loesung.lagen = copy.deepcopy(eintrag.lagen)
            loesung.stahlflaeche = _stahlflaeche(eintrag)
            loesung.schlechtester = bewertung.grad
            loesung.nachweis = bewertung.nachweis
            return loesung

        # Jeden Posten einzeln einen Schritt groesser probieren. Genommen wird
        # der, der den schlechtesten Erfuellungsgrad am weitesten hebt -- und
        # nur, wenn er ihn ueberhaupt hebt. Beim Duktilitaetsnachweis tut das
        # keiner, denn dort ist mehr Stahl das Problem.
        bester: Optional[Tuple[float, Posten, Bewertung]] = None
        an_der_grenze = False
        for p in posten:
            if stand[p] + 1 >= len(stufen.von(p)):
                continue
            stand[p] += 1
            setzen()
            if _ueber_grenze(eintrag, grenze):
                # Ueber die Obergrenze gar nicht erst rechnen.
                stand[p] -= 1
                an_der_grenze = True
                continue
            versuch = bewerte(projekt)
            stand[p] -= 1
            abstand = versuch.abstand(erwartet)
            if bester is None or abstand < bester[0]:
                bester = (abstand, p, versuch)
        setzen()

        if bester is None:
            ausgeschoepft = (f"Obergrenze {grenze:.0f} mm²/m je Lage erreicht"
                             if an_der_grenze else "Alle Durchmesser ausgeschöpft")
            loesung.begruendung = bewertung.fehler or (
                f"{ausgeschoepft}; schlechtester Grad "
                f"{bewertung.grad:.2f} ({bewertung.nachweis}).")
            return loesung
        if bester[0] >= bewertung.abstand(erwartet):
            loesung.begruendung = (
                f"Mehr Stahl hilft nicht: «{bewertung.nachweis}» bleibt bei "
                f"{bewertung.grad:.2f} → dickere Platte oder festerer Beton.")
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
          durchmesser: Sequence[float] = DURCHMESSER,
          mindestdurchmesser: float = MINDESTDURCHMESSER) -> Suchergebnis:
    """
    Die kleinste Bewehrung, mit der alle eingeschalteten Nachweise aufgehen.

    Mit ``mindestdurchmesser`` hat die Grundbewehrung jeder Lage wenigstens
    ihn -- siehe «Der Mindestdurchmesser» oben. Null: eine Lage darf leer
    bleiben.

    Zurueck kommt ein :class:`Suchergebnis`; das Projekt selbst bleibt
    unberuehrt. Wer die gefundene Bewehrung uebernehmen will, ruft
    :func:`uebernehmen`.
    """
    ergebnis = Suchergebnis(modus=Suchmodus(modus))
    teilungen = [t for t in teilungen if t > 0] or list(TEILUNGEN)
    je_art = Stufen.aus(durchmesser, mindestdurchmesser)

    for teilung in sorted(teilungen):
        loesung = _fuer_teilung(projekt, kennung, teilung,
                                ergebnis.modus.bewehrung, je_art)
        ergebnis.loesungen.append(loesung)

    gefunden = [l for l in ergebnis.loesungen if l.gefunden]
    if not gefunden:
        ergebnis.begruendung = (
            "Mit keiner Teilung gehen alle eingeschalteten Nachweise auf.")
        return ergebnis
    # Kleinste Stahlflaeche gewinnt. Bei Gleichstand die groessere Teilung:
    # weniger Staebe bei gleichem Querschnitt ist weniger Arbeit.
    ergebnis.beste = min(gefunden, key=lambda l: (l.stahlflaeche, -l.teilung))
    ergebnis.begruendung = (
        f"Teilung {ergebnis.beste.teilung:.0f} mm, "
        f"{ergebnis.beste.stahlflaeche:.0f} mm² – kleinste Stahlfläche von "
        f"{len(gefunden)} Lösungen.")
    ergebnis.duktilitaet, ergebnis.duktilitaet_erfuellt = _duktilitaetsbefund(
        projekt, kennung, ergebnis.beste)
    return ergebnis


def _duktilitaetsbefund(projekt, kennung: str,
                        loesung: "Loesung") -> Tuple[str, Optional[bool]]:
    """Ob die gefundene Bewehrung die Druckzone noch genuegend begrenzt."""
    probe = copy.deepcopy(projekt)
    uebernehmen(probe, kennung, loesung)
    probe.querschnitte = [q for q in probe.querschnitte if q.kennung == kennung]
    eintrag = probe.querschnitt(kennung)
    # Unabhaengig vom Schalter: die Suche geht dem Nachweis aus dem Weg, also
    # schuldet sie eine Auskunft ueber ihn -- auch dort, wo er gerade nicht
    # gefuehrt wird.
    #
    # Traegt keine x-Lage Bewehrung, gibt es nichts zu sagen: eine leere Lage
    # kann nicht duktil sein, und «geht nicht auf» waere dort keine Auskunft
    # ueber die gefundene Bewehrung, sondern darueber, dass es keine gibt.
    eintrag.duktilitaet = any(
        lage.grund.durchmesser > 0 or lage.zulage.durchmesser > 0
        for nummer, lage in enumerate(eintrag.lagen, start=1)
        if eintrag.richtung_von(nummer) is Richtung.X)
    if not eintrag.duktilitaet:
        return "", None
    eintrag.ohne_lastfaelle()
    bewertung = bewerte(probe)
    if bewertung.erfuellt():
        return "Duktilität erfüllt.", True
    return (f"Duktilität nicht erfüllt: «{bewertung.nachweis}» bei "
            f"{bewertung.grad:.2f} → dickere Platte; gesucht ohne Duktilität.", False)


def _absteigen(projekt, posten, stand, setzen,
               bewertung: Bewertung, erwartet: int) -> Bewertung:
    """
    Wieder hinunter, solange es noch aufgeht.

    Der Aufstieg nimmt in jeder Runde den Schritt, der den Rueckstand am
    weitesten senkt -- und der kann ueber das Ziel hinausgehen: ein Posten
    landet zwei Stufen hoeher, obwohl eine gereicht haette, weil die zweite
    unterwegs am meisten gebracht hat. Hier wird das zurueckgenommen, Stufe um
    Stufe, solange alle Nachweise aufgehen.

    Ohne diesen Abstieg waere «die kleinste Bewehrung» eine Zusage, die das
    Werkzeug nicht haelt: es gaebe Ergebnisse, aus denen sich noch ein
    Durchmesser herausnehmen liesse. Hinunter geht es bis zur untersten Stufe
    des Postens -- unter den Mindestdurchmesser nicht (:class:`Stufen`).
    """
    geaendert = True
    while geaendert:
        geaendert = False
        for p in posten:
            if stand[p] == 0:
                continue
            stand[p] -= 1
            setzen()
            versuch = bewerte(projekt)
            if versuch.erfuellt(erwartet):
                bewertung, geaendert = versuch, True
            else:
                stand[p] += 1
                setzen()
    return bewertung


def _fuer_teilung(projekt, kennung: str, teilung: float, modus: Suchmodus,
                  stufen: Stufen) -> Loesung:
    """
    Eine Teilung, je nach Modus in einem oder zwei Schritten.

    Die Arbeitsplatte hat die x-Lagen leer (siehe :func:`arbeitskopie`); was
    nicht gesucht wird -- in den Grund-Modi die Zulage --, bleibt also
    ausdruecklich null und steht so auch in der Loesung.
    """
    if modus in (Suchmodus.GRUND_MIT, Suchmodus.GRUND_OHNE):
        arbeit = arbeitskopie(projekt, kennung,
                               kraefte=modus is Suchmodus.GRUND_MIT)
        posten = _gesuchte(arbeit.querschnitt(kennung), arten=("grund",))
        return _eine_teilung(arbeit, kennung, teilung, posten, stufen)

    # Zwei Schritte: erst die Grundbewehrung ohne Kraefte, dann die Zulage
    # gegen alles. Der zweite Schritt uebernimmt die Grundbewehrung des ersten.
    ohne = arbeitskopie(projekt, kennung, kraefte=False)
    grund_posten = _gesuchte(ohne.querschnitt(kennung), arten=("grund",))
    erst = _eine_teilung(ohne, kennung, teilung, grund_posten, stufen)
    if not erst.gefunden:
        erst.begruendung = (
            "Grundbewehrung ohne Kräfte geht nicht auf: "
            + erst.begruendung)
        return erst

    # Die Grundbewehrung aus dem ersten Schritt bleibt stehen; gesucht wird
    # jetzt nur noch die Zulage.
    arbeit = arbeitskopie(projekt, kennung, kraefte=True, leeren=False)
    eintrag = arbeit.querschnitt(kennung)
    for lage in eintrag.lagen:
        lage.zulage.durchmesser = 0
    for lage, _ in grund_posten:
        eintrag.lagen[lage - 1].grund = copy.deepcopy(erst.lagen[lage - 1].grund)
    # Eine Zulage gehoert zu einer bewehrten Lage, nicht zu einer leeren --
    # gesucht wird sie darum ueberall dort, wo Grundbewehrung liegen koennte.
    zulage_posten = [(lage, "zulage") for lage, _ in grund_posten]
    return _eine_teilung(arbeit, kennung, teilung, zulage_posten, stufen)


def uebernehmen(projekt, kennung: str, loesung: Loesung) -> None:
    """Die gefundenen Lagen in die Platte schreiben."""
    projekt.querschnitt(kennung).lagen = copy.deepcopy(loesung.lagen)
