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

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping, Optional

from opencivil.core.einheiten import MM, Groesse
from opencivil.material.basis import Baustoff
from opencivil.material.beton import BETONSORTEN
from opencivil.material.betonstahl import STAHLSORTEN
from opencivil.nachweis.biegung_normalkraft import Erfuellungsart
from opencivil.querschnitt.platte import (
    ALPHA_MAX, ALPHA_MIN, Bewehrungsposten, Querkraftbewehrung, Richtung,
)


class ProjektFehler(Exception):
    """Die Projektbeschreibung ist in sich nicht stimmig."""


def _zahl(d: Mapping[str, Any], feld: str, vorgabe: float) -> float:
    """
    Eine Zahl aus der Beschreibung. Die Vorgabe gilt nur, wenn nichts dasteht.

    Bewusst **nicht** ``float(d.get(feld) or vorgabe)``: dieser Ausdruck kann
    eine eingegebene Null nicht von einem fehlenden Feld unterscheiden und
    ersetzt sie stillschweigend. Im Eingabefeld stand dann ``h = 0``, gerechnet
    wurde mit 300 mm, und die Herleitung schrieb 300 mm hin -- ein Widerspruch,
    den niemand sieht. Eine Platte ohne Dicke meldete «alle Nachweise erfüllt».
    """
    wert = d.get(feld)
    if wert is None or wert == "":
        return vorgabe
    try:
        return float(wert)
    except (TypeError, ValueError):
        raise ProjektFehler(
            f"Das Feld '{feld}' enthält keine Zahl, sondern {wert!r}."
        ) from None


def _pflichtfeld(d: Mapping[str, Any], feld: str, wer: str) -> str:
    """
    Ein Feld, ohne das sich nichts zusammenbauen laesst.

    Ohne diese Pruefung kam der nackte ``KeyError`` bis in die Oberflaeche --
    eine Fehlermeldung, die dem Benutzer nichts sagt und nach einem Absturz
    aussieht.
    """
    wert = d.get(feld)
    if wert in (None, ""):
        raise ProjektFehler(f"{wer} hat kein Feld '{feld}'. Die Datei ist unvollständig.")
    return str(wert)


def sorten(art: str) -> Mapping[str, Any]:
    return BETONSORTEN if art == "beton" else STAHLSORTEN


def _rissanforderung_aus(wert: Any) -> str:
    """
    Die Anforderung an die Rissbildung, oder die Vorgabe.

    Eine unbekannte Angabe wird nicht stillschweigend auf 'normal' gezogen --
    sie waere die mildeste der drei, und eine stillschweigende Milderung ist
    genau das, was ein Nachweiswerkzeug nicht tun darf.
    """
    if wert in (None, ""):
        return "normal"
    text = str(wert)
    if text not in RISSANFORDERUNGEN:
        raise ProjektFehler(
            f"Unbekannte Rissanforderung '{text}'. Möglich sind: "
            f"{', '.join(RISSANFORDERUNGEN)}.")
    return text


def _teilungen_aus(roh, vorgabe) -> List[float]:
    """
    Eine Liste von Teilungen, aufsteigend und ohne Unsinn.

    Ohne brauchbare Angabe die Vorgabe: eine leere Liste hiesse, dass die
    Suche nichts zu versuchen haette, und das ist kein Zustand, in dem man
    eine Oberflaeche stehen lassen will.
    """
    werte = []
    for x in (roh or []):
        try:
            zahl = float(x)
        except (TypeError, ValueError):
            continue
        if zahl > 0:
            werte.append(zahl)
    return sorted(set(werte)) or list(vorgabe)


def _schalter_aus(*werte: Any, vorgabe: bool = False) -> bool:
    """
    Ein Schalter aus dem, was in der Datei steht.

    Frueher war jeder dieser Nachweise eine Liste von vier Schaltern, einer je
    Lage, und die Zwaengung hatte je einen fuer x und y. Nachgewiesen wird nur
    noch x, und dort entscheidet die unguenstigere der beiden Lagen -- ein
    Schalter genuegt. Eine alte Datei bringt noch die Liste mit: war darin
    irgendein Haken gesetzt, gilt der Nachweis als eingeschaltet. Das ist die
    Lesart, die nichts wegnimmt, was jemand verlangt hat.

    Mehrere Werte, weil aus `zwaengung_x` und `zwaengung_y` einer wird.
    """
    gefunden = False
    for wert in werte:
        if wert is None:
            continue
        gefunden = True
        if any(wert) if isinstance(wert, (list, tuple)) else bool(wert):
            return True
    return False if gefunden else vorgabe


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
        kennung = _pflichtfeld(d, "kennung", "Ein Material")
        return cls(
            kennung=kennung,
            art=_pflichtfeld(d, "art", f"Das Material '{kennung}'"),
            sorte=str(d.get("sorte", "")),
            name=str(d.get("name", "")),
            eigenstaendig=bool(d.get("eigenstaendig", False)),
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
            durchmesser=_zahl(d, "durchmesser", 0.0),
            abstand=abstand_wert,
            anzahl=anzahl_wert,
        )

    def als_posten(self) -> Bewehrungsposten:
        return Bewehrungsposten(
            durchmesser=Groesse(self.durchmesser, MM),
            abstand=Groesse(self.abstand, MM) if self.abstand else None,
            anzahl=self.anzahl if not self.abstand else None,
        )


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
            stahl=str(d.get("stahl", "")),
            grund=PostenEintrag.aus_dict(d.get("grund") or {}),
            zulage=PostenEintrag.aus_dict(d.get("zulage") or {"durchmesser": 0.0}),
            # Alte Beschreibungen kennen das Feld nicht. Die unguenstige Lage
            # ist die Vorgabe -- auf der Baustelle laesst sich nicht steuern,
            # welche Kante fluchtet.
            unguenstig=bool(d.get("unguenstig", True)),
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
            durchmesser=_zahl(d, "durchmesser", 0.0),
            stahl=str(d.get("stahl", "")),
            abstand_x=wahl("abstand_x") or cls.abstand_x,
            abstand_y=abstand_y,
            anzahl_y=anzahl_y,
            alpha_min=int(_zahl(d, "alpha_min", float(ALPHA_MIN))),
            alpha_max=int(_zahl(d, "alpha_max", float(ALPHA_MAX))),
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
            name=_pflichtfeld(d, "name", "Ein Knicknachweis"),
            N_Ed=_zahl(d, "N_Ed", 0.0),
            M_Ed_1=_zahl(d, "M_Ed_1", 0.0),
            laenge=_zahl(d, "laenge", 3.0),
            knicklaenge=_zahl(d, "knicklaenge", 3.0),
            aktiv=bool(d.get("aktiv", True)),
        )


#: Wahl der Tragrichtung einer Schnittgroessenkombination -- historisch.
#:
#: Schnittgroessen gehoeren jetzt immer zur Tragrichtung x; die Wahl gibt es
#: nicht mehr. Die Konstante steht noch, um alte Dateien zu lesen.
BEIDE_RICHTUNGEN = "beide"


def _nur_x(d: Mapping[str, Any], was: str) -> None:
    """
    Alte Lastfaelle, die nur in y galten, gehen nicht mehr.

    Nachgewiesen wird ausschliesslich x. Ein Lastfall mit ``richtung: "y"``
    stillschweigend auf x umzudeuten hiesse, eine Zahl an einem anderen
    Querschnitt anzusetzen als der Benutzer gemeint hat -- genau die Art von
    stiller Aenderung, die ein Nachweiswerkzeug nicht machen darf. ``x`` und
    ``beide`` gelten unveraendert weiter.
    """
    if str(d.get("richtung") or "") == Richtung.Y.value:
        raise ProjektFehler(
            f"{was} gilt nur in y-Richtung. Nachgewiesen wird nur noch x -- "
            f"die y-Lagen stehen im Querschnitt, damit die statische Höhe und "
            f"der Bewehrungsgehalt stimmen, nachgewiesen werden sie nicht. "
            f"Bitte die Richtung auf x stellen oder den Lastfall löschen.")


#: Anforderung an die Rissbildung. Bestimmt spaeter die zulaessige
#: Stahlspannung; die Zahlen dazu stehen noch aus.
RISSANFORDERUNGEN: Dict[str, str] = {
    "normal": "Normal",
    "erhoeht": "Erhöht",
    "hoch": "Hoch",
}


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
            name=_pflichtfeld(d, "name", "Eine Spannungsanalyse"),
            art=str(d.get("art") or "schnittgroessen"),
            richtung=str(d.get("richtung") or "x"),
            N_Ed=_zahl(d, "N_Ed", 0.0),
            M_Ed=_zahl(d, "M_Ed", 0.0),
            eps_oben=_zahl(d, "eps_oben", -1.0),
            eps_unten=_zahl(d, "eps_unten", 2.0),
            aktiv=bool(d.get("aktiv", True)),
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
        _nur_x(d, f"Der {wort} Lastfall '{d.get('name')}'")
        return cls(
            name=_pflichtfeld(d, "name", f"Ein {wort}r Lastfall"),
            M_Ed=_zahl(d, "M_Ed", 0.0),
            N_Ed=_zahl(d, "N_Ed", 0.0),
            aktiv=bool(d.get("aktiv", True)),
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
        _nur_x(d, f"Die Einwirkung '{d.get('name')}'")
        return cls(
            name=_pflichtfeld(d, "name", "Eine Einwirkung"),
            M_Ed=_zahl(d, "M_Ed", 0.0),
            N_Ed=_zahl(d, "N_Ed", 0.0),
            V_Ed=_zahl(d, "V_Ed", 0.0),
            art=str(d.get("art") or Erfuellungsart.AUTOMATISCH.value),
            aktiv=bool(d.get("aktiv", True)),
        )


def _lagen_aus_altem_format(d: Mapping[str, Any]) -> List[dict]:
    """
    Rechnet eine vor dem Vier-Lagen-Modell gespeicherte Platte um.

    Frueher gab es beliebig viele Lagen je Seite, jede mit einem einzigen
    Bewehrungssatz. Uebernommen werden die beiden aeussersten je Seite:

        lagen_unten[0] -> 1. Lage      lagen_oben[0] -> 4. Lage
        lagen_unten[1] -> 2. Lage      lagen_oben[1] -> 3. Lage

    Weitere Lagen der alten Beschreibung gehen dabei verloren -- besser als eine
    gespeicherte Datei gar nicht mehr zu oeffnen, aber der Benutzer sollte sie
    nachsehen.
    """
    def umbauen(alt: Optional[Mapping[str, Any]]) -> dict:
        if not alt:
            return {"stahl": "", "grund": {"durchmesser": 0.0}, "zulage": {"durchmesser": 0.0}}
        return {
            "stahl": alt.get("stahl", ""),
            "grund": {
                "durchmesser": alt.get("durchmesser", 0.0),
                "abstand": alt.get("abstand"),
                "anzahl": alt.get("anzahl"),
            },
            "zulage": {"durchmesser": 0.0},
        }

    unten = list(d.get("lagen_unten") or [])
    oben = list(d.get("lagen_oben") or [])
    return [
        umbauen(unten[0] if len(unten) > 0 else None),   # 1. Lage
        umbauen(unten[1] if len(unten) > 1 else None),   # 2. Lage
        umbauen(oben[1] if len(oben) > 1 else None),     # 3. Lage
        umbauen(oben[0] if len(oben) > 0 else None),     # 4. Lage
    ]


