"""
opencivil/projekt/eintraege.py -- die Teile einer Projektbeschreibung.

VERANTWORTUNG:
Material, Bewehrungsposten und -lagen, Buegel, Lastfaelle -- jedes als
Datenklasse, die sich als JSON speichern und wieder einlesen laesst. Gelesen
und geprueft wird jeder Eintrag ueber seine Felder: was eines annehmen darf,
steht an ihm (:mod:`opencivil.projekt.lesen`).

Die Platte, die diese Teile zusammenhaelt, steht in
:mod:`opencivil.projekt.platte`; das ganze Projekt in
:mod:`opencivil.projekt.projekt`.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping, Optional

from opencivil.core.einheiten import MM, MM2, Groesse
from opencivil.core.wert import kennung_aus
from opencivil.material.basis import Baustoff
from opencivil.nachweis.biegung_normalkraft import Erfuellungsart
from opencivil.nachweis.duktilitaet import HOECHSTENS as X_D_HOECHSTENS
from opencivil.querschnitt.platte import (
    ALPHA_MAX, ALPHA_MIN, Bewehrungsposten, Querkraftbewehrung, Richtung,
)
from opencivil.projekt.lesen import ProjektFehler, einer_von, lesen, nicht_negativ, ort, sorten
from opencivil.nachweis.querschnittsloeser import Werkstoffsatz
from opencivil.nachweis.rechenwahl import (
    FASERARTEN, RECHENARTEN, SPANNUNGSARTEN, Rechenart, Rechenwahl,
)
from opencivil.nachweis.verformung import KRIECHZAHL as VERFORMUNG_KRIECHZAHL, ZUGSEITEN
from opencivil.spannungsanalyse import Analyseart

#: Mit welchen Festigkeiten ein Werkstoffgesetz rechnen kann, siehe
#: :class:`~opencivil.nachweis.querschnittsloeser.Werkstoffsatz`. Gewaehlt in
#: der Querschnittsanalyse und in jeder Spannung-Dehnung-Analyse.
WERKSTOFFSAETZE = tuple(s.value for s in Werkstoffsatz)

#: Welche Spannungs-Dehnungs-Beziehung der Beton der Querschnittsanalyse haben
#: kann: Parabel-Rechteck oder der Spannungsblock 0.85·x -- die beiden genauen
#: Rechenarten (:class:`~opencivil.nachweis.rechenwahl.Rechenart`).
BETONGESETZE = (Rechenart.PARABEL.value, Rechenart.BLOCK.value)


# ===========================================================================
# Material
# ===========================================================================


@dataclass
class Beschreibung:
    """
    Gemeinsamer Boden aller Beschreibungsteile.

    Der Weg nach draussen sind die Felder der Datenklasse, nicht mehr. Von
    Hand geschrieben war ``als_dict`` ein Spiegel, der nur stimmt, solange
    jemand ihn nachfuehrt -- neun Stueck, zusammen gut hundert Zeilen, deren
    ganze Aufgabe war, identisch zu etwas zu sein, das die Standardbibliothek
    schon kann.

    Seit der Zwischenspeicher (:mod:`opencivil.web.speicher`) seinen Abdruck
    daraus bildet, waere ein vergessenes Feld auch nicht mehr bloss eine
    unvollstaendige Datei: die Aenderung faende sich im Abdruck nicht wieder,
    das Bauteil gaelte als unveraendert, und die Oberflaeche zeigte eine alte
    Zahl. Von allen Fehlern der schlimmste -- und mit dieser Zeile gibt es ihn
    nicht.

    Der Weg hinein ebenso: :func:`~opencivil.projekt.lesen.lesen` liest
    jeden Eintrag aus seinen Feldern, streng, und prueft ihn mit
    :func:`~opencivil.projekt.lesen.felder_pruefen` -- was ein Feld annehmen
    darf, steht an ihm. Von Hand waren es 39 Leser, jeder mit eigenen
    Vorgaben, Pruefungen und alten Formaten, und die Fassade ging an ihnen
    vorbei: ein «festt» aus Python wurde still zur Feder (2026-10-16).

    ``BEZEICHNUNG``, wo es sie gibt, nennt den Eintrag in Meldungen so wie
    die Oberflaeche: «Platte 'Decke'».
    """

    def als_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def aus_dict(cls, roh: Mapping[str, Any], wo: Optional[str] = None) -> Any:
        """Ein Eintrag aus der Datei -- gelesen und geprueft, siehe :mod:`opencivil.projekt.lesen`."""
        return lesen(cls, roh, wo or ort(cls, roh))


#: Womit die Namen eigener Materialien beginnen: BE1, BE2 ... beim Beton,
#: S1, S2 ... beim Betonstahl (Benutzer, 2026-10-16).
EIGENE_VORSILBE = {"beton": "BE", "betonstahl": "S"}


@dataclass
class MaterialEintrag(Beschreibung):
    """
    Ein Baustoff, wie ihn die Oberflaeche beschreibt: eine Normsorte nach SIA,
    die bleibt, wie sie ist, oder ein eigenes Material mit einer Sorte als
    Vorlage.
    """

    BEZEICHNUNG = "Material"

    kennung: str
    art: str = einer_von(("beton", "betonstahl"))

    sorte: str
    """Die Normsorte -- bei einem eigenen Material die Vorlage seiner Kennwerte."""

    name: str = ""
    eigenstaendig: bool = False
    """
    False = Normsorte, Kennwerte gesperrt, Name = Sorte -- nie aenderbar.
    True  = eigenes Material, aenderbar, mit eigenem Namen (BE1, S1 ...).
    """

    abweichungen: Dict[str, float] = field(default_factory=dict)
    ueberschreibungen: Dict[str, float] = field(default_factory=dict)

    @property
    def anzeigename(self) -> str:
        return self.name or self.sorte

    @property
    def ist_normsorte(self) -> bool:
        return not self.eigenstaendig

    def pruefen(self) -> None:
        """Sorte und Name -- die Materialart prueft ihr Feld."""
        if self.sorte not in sorten(self.art):
            raise ProjektFehler(
                f"Unbekannte Sorte '{self.sorte}' für {self.art}. "
                f"Verfügbar: {', '.join(sorten(self.art))}.")
        if self.ist_normsorte:
            if self.abweichungen or self.ueberschreibungen:
                raise ProjektFehler(
                    f"'{self.anzeigename}' ist als Normsorte geführt und darf keine "
                    f"abweichenden Kennwerte haben. Bitte zuerst zu einem eigenen "
                    f"Material machen.")
            if self.name and self.name != self.sorte:
                raise ProjektFehler(
                    f"Eine unveränderte Normsorte muss '{self.sorte}' heissen, "
                    f"nicht '{self.name}'.")
        elif self.anzeigename in sorten(self.art):
            # Sonst stuende eine abgeaenderte Festigkeit unter einer
            # Normbezeichnung im Bericht.
            raise ProjektFehler(
                f"Ein eigenes Material darf nicht wie die Normsorte "
                f"'{self.anzeigename}' heissen.")


# ===========================================================================
# Bewehrung
# ===========================================================================


@dataclass
class PostenEintrag(Beschreibung):
    """Grundbewehrung oder Zulage einer Lage."""

    durchmesser: float = 0.0
    """in mm; 0 bedeutet: nicht vorhanden."""

    abstand: Optional[float] = 150.0
    """Teilung in mm. Genau eines von ``abstand`` und ``anzahl`` ist gesetzt."""

    anzahl: Optional[float] = None

    @property
    def vorhanden(self) -> bool:
        if self.durchmesser <= 0:
            return False
        return bool(self.abstand and self.abstand > 0) or bool(self.anzahl and self.anzahl > 0)

    def pruefen(self, wo: str) -> None:
        """
        Ein Posten mit Durchmesser braucht eine Teilung oder eine Stabzahl
        groesser als null. Bis 2026-10-16 hiess eine Teilung von null still
        «kein Stab»: die Maske zeigte ⌀16, gerechnet wurde ohne. Ohne
        Durchmesser ist der Posten leer, was sonst auch dasteht.
        """
        if self.durchmesser < 0.0:
            raise ProjektFehler(f"{wo}: der Durchmesser kann nicht negativ sein "
                                f"({self.durchmesser:g} mm).")
        if self.durchmesser == 0.0:
            return
        if self.abstand is not None:
            if self.abstand <= 0.0:
                raise ProjektFehler(f"{wo}: die Teilung muss grösser als null sein, "
                                    f"angegeben sind {self.abstand:g} mm.")
        elif self.anzahl is None or self.anzahl <= 0.0:
            raise ProjektFehler(f"{wo}: ⌀{self.durchmesser:g} braucht eine Teilung oder "
                                f"eine Stabzahl grösser als null.")

    def als_posten(self) -> Bewehrungsposten:
        return Bewehrungsposten(
            durchmesser=Groesse(self.durchmesser, MM),
            abstand=Groesse(self.abstand, MM) if self.abstand else None,
            anzahl=self.anzahl if not self.abstand else None,
        )

    def je_meter(self, b: float = 1000.0) -> float:
        """
        Bewehrungsquerschnitt in mm²/m. Ueber die Teilung haengt er an keiner
        Breite; bei einer Stabzahl liegen die Staebe auf der Breite ``b`` (mm).
        """
        return self.als_posten().flaeche(Groesse(b, MM)).in_einheit(MM2) * 1000.0 / b


@dataclass
class LageEintrag(Beschreibung):
    """Eine der vier Lagen."""

    stahl: str = ""
    grund: PostenEintrag = field(default_factory=PostenEintrag)
    zulage: PostenEintrag = field(default_factory=lambda: PostenEintrag(durchmesser=0.0))

    unguenstig: bool = True
    """Ob die inneren Kanten von Grundbewehrung und Zulage fluchten -- siehe
    :class:`opencivil.querschnitt.platte.Bewehrungslage`."""

    @property
    def vorhanden(self) -> bool:
        return self.grund.vorhanden or self.zulage.vorhanden


@dataclass
class ObergrenzeEintrag(Beschreibung):
    """
    Die Obergrenze der automatischen Bewehrung: keine Lage bekommt von der
    Suche mehr Querschnitt als Grund und Zulage hier zusammen.

    Eingegeben wie eine Lage, je als ⌀ @ Teilung -- es zaehlt aber nur die
    Summe in mm²/m. Wie die Suche sie auf Grund und Zulage verteilt, ist frei:
    bei ⌀26@150 + ⌀20@150 (5634 mm²/m) darf eine Lage auch ⌀30 + ⌀12 tragen.
    Beide ohne Durchmesser heisst: keine Obergrenze.
    """

    grund: PostenEintrag = field(default_factory=lambda: PostenEintrag(durchmesser=30.0))
    zulage: PostenEintrag = field(default_factory=lambda: PostenEintrag(durchmesser=0.0))

    @property
    def je_meter(self) -> float:
        """Die Obergrenze in mm²/m -- unendlich, wenn keine gesetzt ist."""
        summe = self.grund.je_meter() + self.zulage.je_meter()
        return summe if summe > 0 else math.inf


@dataclass
class QuerkraftbewehrungEintrag(Beschreibung):
    """
    Die Bügel einer Platte -- ein Raster, ein Durchmesser, zwei Teilungen.

    In y darf statt der Teilung eine Stabzahl über die betrachtete Breite
    stehen; in x nicht. Siehe
    :class:`opencivil.querschnitt.platte.Querkraftbewehrung`.
    """

    durchmesser: float = 0.0
    """in mm; 0 bedeutet: keine Querkraftbewehrung."""

    stahl: str = ""
    abstand_x: Optional[float] = 200.0
    abstand_y: Optional[float] = 200.0
    anzahl_y: Optional[float] = None
    alpha_min: int = ALPHA_MIN
    alpha_max: int = ALPHA_MAX

    @property
    def vorhanden(self) -> bool:
        """
        Ob Buegel liegen -- das sagt allein der Durchmesser. Eine Teilung von
        null heisst nicht «keine Buegel», sondern ist ein Fehler, und
        :meth:`pruefen` sagt es.
        """
        return self.durchmesser > 0

    @property
    def ueber_teilung_y(self) -> bool:
        """In y eine Teilung -- sonst eine Stabzahl. Wie in der Maske: es zaehlt, was dasteht."""
        return self.abstand_y is not None

    def pruefen(self, wo: str) -> None:
        """Was nicht stimmen kann, soll als Satz beim Benutzer ankommen."""
        if not self.vorhanden:
            return
        angegeben = (lambda wert, einheit="":
                     "nichts" if wert is None else f"{wert:g}{einheit}")
        if self.abstand_x is None or self.abstand_x <= 0:
            raise ProjektFehler(
                f"{wo}: die Bügelteilung in x muss grösser als null sein, "
                f"angegeben ist {angegeben(self.abstand_x, ' mm')}.")
        if self.ueber_teilung_y and self.abstand_y <= 0:
            raise ProjektFehler(
                f"{wo}: die Bügelteilung in y muss grösser als null sein, "
                f"angegeben ist {angegeben(self.abstand_y, ' mm')}.")
        if not self.ueber_teilung_y and (self.anzahl_y is None or self.anzahl_y <= 0):
            raise ProjektFehler(
                f"{wo}: die Bügelzahl in y muss grösser als null sein, "
                f"angegeben ist {angegeben(self.anzahl_y)}.")
        neigungen_pruefen(self.alpha_min, self.alpha_max, wo)

    def als_bewehrung(self, stahl: Baustoff) -> Querkraftbewehrung:
        """Die Buegel fuer den Querschnitt -- erst nach :meth:`pruefen`."""
        return Querkraftbewehrung(
            durchmesser=Groesse(self.durchmesser, MM),
            stahl=stahl,
            abstand_x=Groesse(self.abstand_x, MM),
            abstand_y=Groesse(self.abstand_y, MM) if self.ueber_teilung_y else None,
            anzahl_y=None if self.ueber_teilung_y else self.anzahl_y,
            alpha_min=self.alpha_min,
            alpha_max=self.alpha_max,
        )


def neigungen_pruefen(alpha_min: int, alpha_max: int, wo: str) -> None:
    """
    Die Grenzen der Druckfeldneigung -- bei den Buegeln der Platte wie bei den
    Schubwaenden des gezeichneten Querschnitts.
    """
    if not 1 <= alpha_min <= 89 or not 1 <= alpha_max <= 89:
        raise ProjektFehler(
            f"{wo}: die Neigung der Druckdiagonalen muss zwischen 1° und "
            f"89° liegen, angegeben sind {alpha_min}° und {alpha_max}°.")
    if alpha_min > alpha_max:
        raise ProjektFehler(
            f"{wo}: α_min = {alpha_min}° ist grösser als α_max = {alpha_max}°. "
            f"Zwischen den beiden liegt dann keine Neigung, für die sich ein "
            f"Widerstand rechnen liesse.")


def druckfeld_pruefen(k_c: float, wo: str) -> None:
    """Die Abminderung der Druckdiagonalen -- eine Festigkeit mal k_c, also groesser als null."""
    if k_c <= 0.0:
        raise ProjektFehler(f"{wo}: k_c muss grösser als null sein, angegeben ist {k_c:g}.")


def x_d_max_pruefen(x_d_max: float, wo: str) -> None:
    """Die Grenze der bezogenen Druckzonenhoehe im Duktilitaetsnachweis."""
    if not 0.0 < x_d_max <= X_D_HOECHSTENS:
        raise ProjektFehler(
            f"{wo}: max. x/d muss grösser als null und höchstens "
            f"{X_D_HOECHSTENS:g} sein, angegeben ist {x_d_max:g}.")


@dataclass
class KnickEintrag(Beschreibung):
    """
    Ein Knicknachweis: Druckkraft, Moment 1. Ordnung, Laenge, Knicklaenge.

    Nur in x-Richtung -- eine Knicklaenge gehoert zu einer Tragrichtung, und
    in y waere die Breite der Platte die Laenge.
    """

    name: str
    N_Ed: float = 0.0
    """in kN, Druck negativ."""

    M_Ed_1: float = 0.0
    laenge: float = 3.0
    """Systemlaenge in m -- geht in die Schiefstellung ein."""

    knicklaenge: float = 3.0
    """Knicklaenge in m."""

    aktiv: bool = True
    """Ob der Fall gerechnet wird. Ausgeschaltet bleibt er stehen -- eine
    geloeschte Zeile muesste man neu eintippen, um sie wieder anzusehen."""

    def zahlen_pruefen(self, wo: str) -> None:
        """
        Laenge und Knicklaenge -- erst beim Bauen gefragt, wie die Masse der
        Platte. Bis 2026-10-16 rechnete eine Laenge von null und hiess
        «erfuellt».
        """
        for feld, wert in (("Systemlänge", self.laenge), ("Knicklänge", self.knicklaenge)):
            if wert <= 0.0:
                raise ProjektFehler(
                    f"{wo}, Knicknachweis '{self.name}': die {feld} muss grösser als "
                    f"null sein, angegeben sind {wert:g} m.")


@dataclass
class VerformungsfallEintrag(Beschreibung):
    """
    Ein Verformungsfall: die Durchbiegung, mit der Steifigkeit E_cm
    ermittelt, ihre Spannweite und die Seite, die er zieht.

    Wie ein Knickfall nur in x-Richtung.
    """

    name: str
    w: float = 0.0
    """Durchbiegung in mm, mit E_cm ermittelt -- ein Betrag."""

    laenge: float = 5.0
    """Spannweite L in m -- der Grenzwert ist L/350."""

    zugseite: str = einer_von(ZUGSEITEN, "unten")
    """``unten`` im Feld, ``oben`` am Kragarm -- welches rho gilt."""

    aktiv: bool = True
    """Ob der Fall gerechnet wird. Ausgeschaltet bleibt er stehen."""

    def zahlen_pruefen(self, wo: str) -> None:
        """
        w und L -- erst beim Bauen gefragt, wie die Masse der Platte: eine
        abgelegte Platte mit L = 0 soll sich oeffnen und korrigieren lassen.
        """
        if self.w < 0.0:
            raise ProjektFehler(
                f"{wo}, Verformungsfall '{self.name}': w ist der Betrag der "
                f"Durchbiegung und kann nicht negativ sein ({self.w:g} mm).")
        if self.laenge <= 0.0:
            raise ProjektFehler(
                f"{wo}, Verformungsfall '{self.name}': die Spannweite L muss "
                f"grösser als null sein, angegeben ist {self.laenge:g} m.")


@dataclass
class VerformungEintrag(Beschreibung):
    """
    Der Verformungsnachweis einer Platte: die Kriechzahl seines
    Vergroesserungsfaktors und die Faelle.

    phi gilt fuer die Platte und nicht je Fall -- der Faktor wird je Seite
    einmal gerechnet (:mod:`opencivil.nachweis.verformung`).
    """

    kriechzahl: float = nicht_negativ(VERFORMUNG_KRIECHZAHL)
    """phi im Vergroesserungsfaktor omega_w, Vorgabe 2."""

    faelle: List[VerformungsfallEintrag] = field(default_factory=list)

    def fall(self, name: str, *, w: float, laenge: float,
             zugseite: str = VerformungsfallEintrag.zugseite) -> VerformungsfallEintrag:
        """Einen Fall anfuegen -- w in mm, die Spannweite in m."""
        eintrag = VerformungsfallEintrag(name=name, w=w, laenge=laenge, zugseite=zugseite)
        self.faelle.append(eintrag)
        return eintrag

    def pruefen(self, bauteil: str) -> None:
        wo = f"Platte '{bauteil}'"
        eindeutig(self.faelle, bauteil, "Verformungsfall")
        # Verschiedene Namen koennen dieselbe Wert-ID ergeben -- wie bei den
        # Gebrauchslisten.
        kennungen: Dict[str, str] = {}
        for f in self.faelle:
            frueher = kennungen.setdefault(kennung_aus(f.name), f.name)
            if frueher != f.name:
                raise ProjektFehler(
                    f"{wo}: die Verformungsfälle '{frueher}' und '{f.name}' "
                    f"unterscheiden sich nur in Satz- oder Leerzeichen. Im Bericht "
                    f"fielen sie auf denselben Eintrag -- bitte einen davon anders "
                    f"benennen.")


#: Anteil der Tragsicherheitseinwirkungen, der als haeufiger Lastfall gilt --
#: in Prozent, wie die Maske ihn zeigt. Eine Vorgabe, einstellbar je Platte.
HAEUFIG_ANTEIL = 70.0

#: Dasselbe fuer die quasi-staendigen Lastfaelle.
QUASISTAENDIG_ANTEIL = 60.0


def abgeleiteter_fallname(name: str, anteil: float) -> str:
    """
    Wie ein aus der Tragsicherheit abgeleiteter Lastfall heisst.

    Die eine Stelle dafuer: der Aufbau benennt die Faelle so, und die
    Namenspruefung muss genau denselben Namen bilden, um einen gleichlautenden
    eigenen Fall zu erkennen. ``70.0`` wird zu «70 %», ``62.5`` zu «62.5 %».
    """
    return f"{name} ({anteil:g} %)"


@dataclass
class SpannungsfallEintrag(Beschreibung):
    """
    Eine Auswertung am Querschnitt -- kein Nachweis.

    Es wird nichts gegen etwas gehalten: kein Erfuellungsgrad, kein Urteil.
    Gefragt wird, was im Querschnitt geschieht, und je nach :attr:`art` von
    der einen oder der anderen Seite -- aus Schnittgroessen, aus Dehnungen,
    als Momenten-Kruemmungs- oder als Normalkraft-Dehnungs-Linie.

    Womit gerechnet wird, waehlt jede Analyse fuer sich: die Kriechzahl, den
    Wertesatz und die Rechenart (:class:`~opencivil.nachweis.rechenwahl.Rechenwahl`).
    """

    name: str
    art: str = einer_von((a.value for a in Analyseart), Analyseart.SCHNITTGROESSEN.value)
    """Was gefragt wird -- siehe :class:`~opencivil.spannungsanalyse.Analyseart`."""

    richtung: str = einer_von((r.value for r in Richtung), Richtung.X.value)
    """Welche Bewehrung zaehlt. Hier keine Wahl ``beide``: ein Bild zeigt
    einen Querschnitt, und der liegt in einer Richtung."""

    N_Ed: float = 0.0
    """in kN, Zug positiv -- fuer ``schnittgroessen`` und ``moment_kruemmung``."""

    M_Ed: float = 0.0
    """in kNm -- fuer ``schnittgroessen`` und ``normalkraft_dehnung``."""

    eps_oben: float = -1.0
    eps_unten: float = 2.0
    """Randdehnungen in Promille -- nur fuer ``dehnungen``."""

    kriechzahl: float = nicht_negativ(0.0)
    """Die Kriechzahl φ dieser Analyse."""

    werkstoffsatz: str = einer_von(WERKSTOFFSAETZE, WERKSTOFFSAETZE[0])
    """``bemessung`` (f_cd, f_yd) oder ``charakteristisch`` (f_ck, f_yk)."""

    rechenart: str = einer_von((a.value for a in FASERARTEN), Rechenart.PARABEL.value)
    """``block`` oder ``parabel`` -- siehe
    :class:`~opencivil.nachweis.rechenwahl.Rechenart`. Die Handrechnung gibt
    es hier nicht (:data:`~opencivil.nachweis.rechenwahl.FASERARTEN`)."""

    aktiv: bool = True


@dataclass
class GebrauchsfallEintrag(Beschreibung):
    """
    Eine Schnittgroessenkombination unter Gebrauchslast.

    Wie :class:`KombinationEintrag`, aber ohne Querkraft: begrenzt wird die
    Stahlspannung, und dafuer zaehlen Moment und Normalkraft. Ob der Fall
    haeufig oder quasi-staendig ist, sagt die Liste, in der er steht.
    """

    name: str
    M_Ed: float = 0.0
    N_Ed: float = 0.0
    aktiv: bool = True
    """Ob dieser Lastfall gerechnet wird. Ausgeschaltet bleibt er stehen."""


def eindeutig(faelle, platte: str, was: str, *, bauteil: str = "Platte") -> None:
    """
    Lastfallnamen muessen je Platte und Liste eindeutig sein.

    Die Nachweise legen ihre Ergebniswerte unter dem Fallnamen ab -- M-N,
    Querkraft und Stahlspannung alle drei. Zwei Kombinationen gleichen
    Namens fielen darum auf einen Eintrag zusammen: der zweite ueberschrieb
    den ersten, und in der Tabelle fehlte eine Zeile. Kein Fehler, keine
    Warnung, eine Zahl weniger.

    Gemeldet statt umbenannt: welcher der beiden gemeint war, weiss nur der
    Benutzer, und ein automatisch angehaengtes «(2)» stuende danach in seinem
    Bericht.
    """
    gesehen = set()
    for f in faelle:
        if f.name in gesehen:
            raise ProjektFehler(
                f"{bauteil} '{platte}': der Name '{f.name}' ist zweimal als {was} "
                f"vergeben. Die Nachweise legen ihre Ergebnisse unter dem "
                f"Fallnamen ab -- zwei gleiche Namen ergeben eine Zeile statt "
                f"zwei.")
        gesehen.add(f.name)


@dataclass
class RechenwahlEintrag(Beschreibung):
    """
    Womit ein Nachweis-Kapitel rechnet: Kriechzahl, Wertesatz, Rechenart --
    siehe :class:`~opencivil.nachweis.rechenwahl.Rechenwahl`.

    Jedes Kapitel hat seine eigene; die Kriechzahl des Vergroesserungsfaktors
    gehoert dem Verformungsnachweis (:class:`VerformungEintrag`). Welche
    Rechenarten ein Kapitel anbietet, weiss das Kapitel -- es prueft sie
    (:meth:`pruefen`); das Feld kennt nur, welche es ueberhaupt gibt.
    """

    kriechzahl: float = nicht_negativ(0.0)
    werkstoffsatz: str = einer_von(WERKSTOFFSAETZE, WERKSTOFFSAETZE[0])
    rechenart: str = einer_von((a.value for a in Rechenart), Rechenart.HANDRECHNUNG.value)

    @classmethod
    def gebrauch(cls) -> "RechenwahlEintrag":
        """Die Stahlspannungen: elastisch, mit charakteristischen Werten."""
        return cls(werkstoffsatz=Werkstoffsatz.CHARAKTERISTISCH.value,
                   rechenart=Rechenart.ELASTISCH.value)

    @classmethod
    def knicken_verformung(cls) -> "RechenwahlEintrag":
        """Die Ausmitte e_2d: praezise ohne Vereinfachung, mit Bemessungswerten."""
        return cls(rechenart=Rechenart.PARABEL.value)

    @classmethod
    def knicken_widerstand(cls) -> "RechenwahlEintrag":
        """
        Der Widerstand beim Knicken: die 0.85·x-Vereinfachung, mit
        Bemessungswerten. Bis 2026-10-12 war es die Handrechnung, die es dort
        nicht mehr gibt; die Vereinfachung kommt ihr am naechsten.
        """
        return cls(rechenart=Rechenart.BLOCK.value)

    @property
    def wahl(self) -> Rechenwahl:
        """Was der Kern daraus rechnet."""
        return Rechenwahl.aus(self.kriechzahl, self.werkstoffsatz, self.rechenart)

    def pruefen(self, wo: str, arten=RECHENARTEN) -> None:
        """Ob das Kapitel diese Rechenart anbietet -- ``arten`` sagt, welche es gibt."""
        moeglich = [a.value for a in arten]
        if self.rechenart not in moeglich:
            raise ProjektFehler(f"{wo}: die Rechenart «{self.rechenart}» gibt es dort nicht. "
                                f"Möglich sind: {', '.join(moeglich)}.")


@dataclass
class Gebrauchsliste(Beschreibung):
    """
    Die Lastfaelle eines Stahlspannungsnachweises: eigene und abgeleitete.

    Eine Platte hat zwei davon, eine haeufige und eine quasi-staendige. Beide
    werden gleich gebildet -- die eigenen Faelle, dazu die
    Tragsicherheitseinwirkungen mal ``anteil`` Prozent -- und unterscheiden
    sich nur darin, wogegen der Nachweis sie haelt.

    Frueher waren das sechs flache Felder an der Platte, und jede Stelle, die
    damit arbeitete, setzte die drei zusammengehoerigen wieder ueber ihre
    Namen zusammen. Welche Liste haeufig und welche quasi-staendig ist, sagt
    das Feld der Platte, in dem sie steht; die Liste selbst weiss es nicht.

    Der gezeichnete Querschnitt hat dieselbe Liste mit anderen Faellen
    (:class:`~opencivil.projekt.querschnittsanalyse.QAGebrauchsliste`): was
    darin steht (:attr:`FALL`), welche Rechenarten sie anbietet
    (:attr:`ARTEN`) und wie ihr Bauteil in den Meldungen heisst
    (:attr:`BAUTEIL`).
    """

    FALL = GebrauchsfallEintrag
    ARTEN = SPANNUNGSARTEN
    BAUTEIL = "Platte"

    anteil: float
    """Welcher Anteil der Tragsicherheitseinwirkungen abgeleitet wird, in %."""

    aus_tragsicherheit: bool = False
    """
    Ob die abgeleiteten Faelle *gefuehrt* werden.

    Gebildet werden sie immer; ausgeschaltet rechnen sie still mit. Der
    Anteil ist eine bequeme Abschaetzung und keine Norm, darum stehen die
    Faelle nur auf Verlangen in der Tabelle.
    """

    faelle: List[GebrauchsfallEintrag] = field(default_factory=list)
    """Eigene Lastfaelle -- neben den abgeleiteten, nicht statt ihrer."""

    wahl: RechenwahlEintrag = field(default_factory=RechenwahlEintrag.gebrauch)
    """Womit die Stahlspannung gerechnet wird -- Vorgabe elastisch, charakteristisch."""

    def lastfall(self, name: str, **werte: float):
        """Einen eigenen Lastfall anfuegen -- kNm und kN, Zug positiv."""
        eintrag = self.FALL.aus_dict({"name": name, **werte}, f"{self.BAUTEIL}, faelle")
        self.faelle.append(eintrag)
        return eintrag

    def pruefen(self, bauteil: str, kombinationen: List[Any], wort: str) -> None:
        """
        Was an dieser Liste nicht stimmen kann -- ``wort`` ist «häufige» oder
        «quasi-ständige» und steht in der Meldung.

        Je Liste fuer sich: die beiden Listen landen in getrennten Nachweisen
        und damit in getrennten ID-Raeumen. Ein Fall «Dauer» darf in beiden
        stehen. ``kombinationen`` sind die Faelle der Tragsicherheit, aus
        denen abgeleitet wird -- gelesen wird nur ihr Name.
        """
        wo = f"{self.BAUTEIL} '{bauteil}'"
        # Null ergaebe Lastfaelle ohne Last -- ein Nachweis, der immer
        # aufgeht und nichts sagt. Ueber hundert waere keine Gebrauchslast
        # mehr. Gemeldet statt begrenzt: wer 700 statt 70 tippt, soll es
        # erfahren und nicht mit 100 weiterrechnen.
        if not 0.0 < self.anteil <= 100.0:
            raise ProjektFehler(
                f"{wo}: der Anteil für die {wort}n Lastfälle muss "
                f"zwischen 0 und 100 % liegen, angegeben sind "
                f"{self.anteil:g} %.")

        eindeutig(self.faelle, bauteil, f"{wort}r Lastfall", bauteil=self.BAUTEIL)
        self.wahl.pruefen(f"{wo}, {wort} Lastfälle", self.ARTEN)

        # Die abgeleiteten Faelle tragen den Namen ihrer Kombination mit
        # angehaengtem Anteil. Wer einen eigenen Lastfall genau so nennt,
        # traefe denselben Schluessel.
        abgeleitet = [abgeleiteter_fallname(k.name, self.anteil)
                      for k in kombinationen]
        for f in self.faelle:
            if f.name in abgeleitet:
                raise ProjektFehler(
                    f"{wo}: der {wort} Lastfall '{f.name}' heisst "
                    f"wie der aus der Tragsicherheit abgeleitete. Bitte anders "
                    f"benennen -- sonst lässt sich nicht auseinanderhalten, "
                    f"welcher gerechnet wurde.")

        # Verschiedene Namen koennen dieselbe Wert-ID ergeben: «Feld A» und
        # «Feld-A» werden beide zu «Feld_A». Das Rechenwerk wiese den zweiten
        # zurueck, aber mit einer Meldung ueber Wert-IDs, die niemand an der
        # Maske versteht.
        kennungen: Dict[str, str] = {}
        for name in abgeleitet + [f.name for f in self.faelle]:
            frueher = kennungen.setdefault(kennung_aus(name), name)
            if frueher != name:
                raise ProjektFehler(
                    f"{wo}: die {wort}n Lastfälle '{frueher}' und "
                    f"'{name}' unterscheiden sich nur in Satz- oder "
                    f"Leerzeichen. Im Bericht fielen sie auf denselben Eintrag "
                    f"-- bitte einen davon anders benennen.")


@dataclass
class KombinationEintrag(Beschreibung):
    """Eine zu pruefende Schnittgroessenkombination."""

    name: str
    M_Ed: float = 0.0
    N_Ed: float = 0.0
    V_Ed: float = 0.0
    """Querkraft in kN/m -- für den Querkraftnachweis."""

    art: str = einer_von((a.value for a in Erfuellungsart), Erfuellungsart.AUTOMATISCH.value)

    aktiv: bool = True
    """Ob dieser Lastfall gerechnet wird. Ausgeschaltet bleibt er stehen."""
