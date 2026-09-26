"""
opencivil/projekt/eintraege.py -- die Teile einer Projektbeschreibung.

VERANTWORTUNG:
Material, Bewehrungsposten und -lagen, Buegel, Lastfaelle -- jedes als
Datenklasse, die sich als JSON speichern und wieder einlesen laesst. Dazu die
Leser, mit denen ``aus_dict`` Zahlen, Pflichtfelder, Schalter und alte
Dateiformate aufnimmt.

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
from opencivil.querschnitt.platte import (
    ALPHA_MAX, ALPHA_MIN, Bewehrungsposten, Querkraftbewehrung,
)
from opencivil.projekt.lesen import (
    ProjektFehler, nur_x, pflichtfeld, sorten, vorgabe, zahl,
)


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

    Der Weg hinein bleibt je Klasse von Hand: dort stehen Vorgaben, alte
    Dateiformate und Pruefungen, und das ist Arbeit und kein Spiegel.
    """

    def als_dict(self) -> dict:
        return asdict(self)


@dataclass
class MaterialEintrag(Beschreibung):
    """Ein Baustoff, wie ihn die Oberflaeche beschreibt."""

    kennung: str
    art: str
    """``beton`` oder ``betonstahl``."""

    sorte: str
    name: str = ""
    eigenstaendig: bool = False
    """
    False = unveraenderte Normsorte, Kennwerte gesperrt, Name = Sorte.
    True  = eigenes Material, aenderbar, mit eigenem Namen.
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
        if self.art not in ("beton", "betonstahl"):
            raise ProjektFehler(
                f"Unbekannte Materialart '{self.art}'. "
                f"Möglich sind 'beton' und 'betonstahl'.")
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


    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "MaterialEintrag":
        kennung = pflichtfeld(d, "kennung", "Ein Material")
        return cls(
            kennung=kennung,
            art=pflichtfeld(d, "art", f"Das Material '{kennung}'"),
            sorte=str(d.get("sorte", "")),
            name=str(d.get("name", cls.name)),
            eigenstaendig=bool(d.get("eigenstaendig", cls.eigenstaendig)),
            abweichungen={k: float(v) for k, v in (d.get("abweichungen") or {}).items()},
            ueberschreibungen={
                k: float(v) for k, v in (d.get("ueberschreibungen") or {}).items()},
        )


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


    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "PostenEintrag":
        abstand, anzahl = d.get("abstand"), d.get("anzahl")
        anzahl_wert = None if anzahl in (None, "") else float(anzahl)
        abstand_wert = None if abstand in (None, "") else float(abstand)
        # Steht keines von beiden da -- etwa bei einer noch leeren Zulage --,
        # dann gilt die Teilung. Sonst stuende das Feld in der Oberflaeche auf
        # 'Anzahl', was bei einer Platte nie der Regelfall ist.
        if abstand_wert is None and anzahl_wert is None:
            abstand_wert = cls.abstand
        return cls(
            durchmesser=zahl(d, "durchmesser", cls.durchmesser),
            abstand=abstand_wert,
            anzahl=anzahl_wert,
        )

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


    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "LageEintrag":
        return cls(
            stahl=str(d.get("stahl", cls.stahl)),
            grund=PostenEintrag.aus_dict(d.get("grund") or vorgabe(cls, "grund").als_dict()),
            zulage=PostenEintrag.aus_dict(d.get("zulage") or vorgabe(cls, "zulage").als_dict()),
            # Alte Beschreibungen kennen das Feld nicht. Die unguenstige Lage
            # ist die Vorgabe -- auf der Baustelle laesst sich nicht steuern,
            # welche Kante fluchtet.
            unguenstig=bool(d.get("unguenstig", cls.unguenstig)),
        )


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

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "ObergrenzeEintrag":
        return cls(
            grund=PostenEintrag.aus_dict(d.get("grund") or vorgabe(cls, "grund").als_dict()),
            zulage=PostenEintrag.aus_dict(d.get("zulage") or vorgabe(cls, "zulage").als_dict()),
        )


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
        if self.durchmesser <= 0 or not (self.abstand_x and self.abstand_x > 0):
            return False
        return bool(self.abstand_y and self.abstand_y > 0) or bool(
            self.anzahl_y and self.anzahl_y > 0)


    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "QuerkraftbewehrungEintrag":
        def wahl(name: str) -> Optional[float]:
            wert = d.get(name)
            return None if wert in (None, "") else float(wert)

        abstand_y, anzahl_y = wahl("abstand_y"), wahl("anzahl_y")
        # Wie bei den Lagen: steht keines von beiden da, gilt die Teilung.
        if abstand_y is None and anzahl_y is None:
            abstand_y = cls.abstand_y
        return cls(
            durchmesser=zahl(d, "durchmesser", cls.durchmesser),
            stahl=str(d.get("stahl", cls.stahl)),
            abstand_x=wahl("abstand_x") or cls.abstand_x,
            abstand_y=abstand_y,
            anzahl_y=anzahl_y,
            alpha_min=int(zahl(d, "alpha_min", float(cls.alpha_min))),
            alpha_max=int(zahl(d, "alpha_max", float(cls.alpha_max))),
        )

    def pruefen(self, wo: str) -> None:
        """Was nicht stimmen kann, soll als Satz beim Benutzer ankommen."""
        if not self.vorhanden:
            return
        if not 1 <= self.alpha_min <= 89 or not 1 <= self.alpha_max <= 89:
            raise ProjektFehler(
                f"{wo}: die Neigung der Druckdiagonalen muss zwischen 1° und "
                f"89° liegen, angegeben sind {self.alpha_min}° und "
                f"{self.alpha_max}°.")
        if self.alpha_min > self.alpha_max:
            raise ProjektFehler(
                f"{wo}: α_min = {self.alpha_min}° ist grösser als "
                f"α_max = {self.alpha_max}°. Zwischen den beiden liegt dann "
                f"keine Neigung, für die sich ein Widerstand rechnen liesse.")

    def als_bewehrung(self, stahl: Optional[Baustoff]) -> Querkraftbewehrung:
        ueber_teilung = bool(self.abstand_y and self.abstand_y > 0)
        return Querkraftbewehrung(
            durchmesser=Groesse(self.durchmesser, MM),
            stahl=stahl,
            abstand_x=Groesse(self.abstand_x, MM) if self.abstand_x else None,
            abstand_y=Groesse(self.abstand_y, MM) if ueber_teilung else None,
            anzahl_y=None if ueber_teilung else self.anzahl_y,
            alpha_min=self.alpha_min,
            alpha_max=self.alpha_max,
        )


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


    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "KnickEintrag":
        return cls(
            name=pflichtfeld(d, "name", "Ein Knicknachweis"),
            N_Ed=zahl(d, "N_Ed", cls.N_Ed),
            M_Ed_1=zahl(d, "M_Ed_1", cls.M_Ed_1),
            laenge=zahl(d, "laenge", cls.laenge),
            knicklaenge=zahl(d, "knicklaenge", cls.knicklaenge),
            aktiv=bool(d.get("aktiv", cls.aktiv)),
        )


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
    der einen oder der anderen Seite -- aus Schnittgroessen, aus Dehnungen
    oder als ganze Momenten-Kruemmungs-Linie.
    """

    name: str
    art: str = "schnittgroessen"
    """``schnittgroessen``, ``dehnungen`` oder ``moment_kruemmung``."""

    richtung: str = "x"
    """Welche Bewehrung zaehlt. Hier keine Wahl ``beide``: ein Bild zeigt
    einen Querschnitt, und der liegt in einer Richtung."""

    N_Ed: float = 0.0
    """in kN, Zug positiv -- fuer ``schnittgroessen`` und ``moment_kruemmung``."""

    M_Ed: float = 0.0
    """in kNm -- nur fuer ``schnittgroessen``."""

    eps_oben: float = -1.0
    eps_unten: float = 2.0
    """Randdehnungen in Promille -- nur fuer ``dehnungen``."""

    aktiv: bool = True

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "SpannungsfallEintrag":
        return cls(
            name=pflichtfeld(d, "name", "Eine Spannungsanalyse"),
            art=str(d.get("art") or cls.art),
            richtung=str(d.get("richtung") or cls.richtung),
            N_Ed=zahl(d, "N_Ed", cls.N_Ed),
            M_Ed=zahl(d, "M_Ed", cls.M_Ed),
            eps_oben=zahl(d, "eps_oben", cls.eps_oben),
            eps_unten=zahl(d, "eps_unten", cls.eps_unten),
            aktiv=bool(d.get("aktiv", cls.aktiv)),
        )


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

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any],
                 wort: str = "häufige") -> "GebrauchsfallEintrag":
        """``wort`` nennt die Liste in der Meldung -- «häufige» oder «quasi-ständige»."""
        nur_x(d, f"Der {wort} Lastfall '{d.get('name')}'")
        return cls(
            name=pflichtfeld(d, "name", f"Ein {wort}r Lastfall"),
            M_Ed=zahl(d, "M_Ed", cls.M_Ed),
            N_Ed=zahl(d, "N_Ed", cls.N_Ed),
            aktiv=bool(d.get("aktiv", cls.aktiv)),
        )


def eindeutig(faelle, platte: str, was: str) -> None:
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
                f"Platte '{platte}': der Name '{f.name}' ist zweimal als {was} "
                f"vergeben. Die Nachweise legen ihre Ergebnisse unter dem "
                f"Fallnamen ab -- zwei gleiche Namen ergeben eine Zeile statt "
                f"zwei.")
        gesehen.add(f.name)


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
    """

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

    def lastfall(self, name: str, *, M_Ed: float = 0.0,
                 N_Ed: float = 0.0) -> GebrauchsfallEintrag:
        """Einen eigenen Lastfall anfuegen -- kNm und kN, Zug positiv."""
        eintrag = GebrauchsfallEintrag(name=name, M_Ed=M_Ed, N_Ed=N_Ed)
        self.faelle.append(eintrag)
        return eintrag

    def pruefen(self, platte: str, kombinationen: List["KombinationEintrag"],
                wort: str) -> None:
        """
        Was an dieser Liste nicht stimmen kann -- ``wort`` ist «häufige» oder
        «quasi-ständige» und steht in der Meldung.

        Je Liste fuer sich: die beiden Listen landen in getrennten Nachweisen
        und damit in getrennten ID-Raeumen. Ein Fall «Dauer» darf in beiden
        stehen.
        """
        # Null ergaebe Lastfaelle ohne Last -- ein Nachweis, der immer
        # aufgeht und nichts sagt. Ueber hundert waere keine Gebrauchslast
        # mehr. Gemeldet statt begrenzt: wer 700 statt 70 tippt, soll es
        # erfahren und nicht mit 100 weiterrechnen.
        if not 0.0 < self.anteil <= 100.0:
            raise ProjektFehler(
                f"Platte '{platte}': der Anteil für die {wort}n Lastfälle muss "
                f"zwischen 0 und 100 % liegen, angegeben sind "
                f"{self.anteil:g} %.")

        eindeutig(self.faelle, platte, f"{wort}r Lastfall")

        # Die abgeleiteten Faelle tragen den Namen ihrer Kombination mit
        # angehaengtem Anteil. Wer einen eigenen Lastfall genau so nennt,
        # traefe denselben Schluessel.
        abgeleitet = [abgeleiteter_fallname(k.name, self.anteil)
                      for k in kombinationen]
        for f in self.faelle:
            if f.name in abgeleitet:
                raise ProjektFehler(
                    f"Platte '{platte}': der {wort} Lastfall '{f.name}' heisst "
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
                    f"Platte '{platte}': die {wort}n Lastfälle '{frueher}' und "
                    f"'{name}' unterscheiden sich nur in Satz- oder "
                    f"Leerzeichen. Im Bericht fielen sie auf denselben Eintrag "
                    f"-- bitte einen davon anders benennen.")

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any], *, wort: str,
                 vorgabe: float) -> "Gebrauchsliste":
        return cls(
            anteil=zahl(d, "anteil", vorgabe),
            aus_tragsicherheit=bool(d.get("aus_tragsicherheit", cls.aus_tragsicherheit)),
            faelle=[GebrauchsfallEintrag.aus_dict(x, wort)
                    for x in (d.get("faelle") or [])],
        )


@dataclass
class KombinationEintrag(Beschreibung):
    """Eine zu pruefende Schnittgroessenkombination."""

    name: str
    M_Ed: float = 0.0
    N_Ed: float = 0.0
    V_Ed: float = 0.0
    """Querkraft in kN/m -- für den Querkraftnachweis."""

    art: str = Erfuellungsart.AUTOMATISCH.value

    aktiv: bool = True
    """Ob dieser Lastfall gerechnet wird. Ausgeschaltet bleibt er stehen."""

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "KombinationEintrag":
        nur_x(d, f"Die Einwirkung '{d.get('name')}'")
        return cls(
            name=pflichtfeld(d, "name", "Eine Einwirkung"),
            M_Ed=zahl(d, "M_Ed", cls.M_Ed),
            N_Ed=zahl(d, "N_Ed", cls.N_Ed),
            V_Ed=zahl(d, "V_Ed", cls.V_Ed),
            art=str(d.get("art") or cls.art),
            aktiv=bool(d.get("aktiv", cls.aktiv)),
        )


