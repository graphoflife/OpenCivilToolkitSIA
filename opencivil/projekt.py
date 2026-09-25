"""
opencivil/projekt.py -- Serialisierbare Beschreibung eines ganzen Projekts.

VERANTWORTUNG:
Eine Oberflaeche braucht Materialien und Querschnitte als Daten: etwas, das sich
als JSON speichern, im Browser bearbeiten und wieder zu einem :class:`Rechenwerk`
zusammenbauen laesst. Genau das ist ein :class:`Projekt` -- eine reine
Beschreibung ohne Rechenlogik.

NORMSORTE ODER EIGENES MATERIAL:
Ein Material ist entweder eine unveraenderte Normsorte oder ein eigenes. Nur die
unveraenderte darf die Sortenbezeichnung tragen: steht 'C30/37' auf einem
Bauteil, muessen die Kennwerte auch die der Norm sein. Wer abweichen will, macht
das Material mit :meth:`Projekt.material_loesen` eigenstaendig; es bekommt dann
einen eigenen Namen wie ``C30/37_1``. So kann keine abgeaenderte Festigkeit unter
dem Deckmantel einer Normbezeichnung im Bericht landen.

EINHEITEN IN DER BESCHREIBUNG:
Alle Zahlen stehen in der Anzeige-Einheit des jeweiligen Kennwerts (mm, N/mm^2,
kNm, ...) -- also so, wie der Benutzer sie eintippt. Die Umrechnung in SI
geschieht erst beim Aufbau, ueber die :class:`Groesse`.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.einheiten import (
    EINHEITSLOS, KN, KNM, KN_PRO_M, M, MM, Groesse,
)
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.basis import Baustoff
from opencivil.material.beton import BETONSORTEN, beton
from opencivil.material.betonstahl import STAHLSORTEN, betonstahl
from opencivil.nachweis.biegung_normalkraft import (
    BiegungNormalkraft, Erfuellungsart, Schnittgroessen,
)
from opencivil.nachweis.duktilitaet import Duktilitaet
from opencivil.nachweis.knicken import Knickfall, Knicken
from opencivil.nachweis.fehlende_bewehrung import Ausgefallen, FehlendeBewehrung
from opencivil.nachweis.mindestbewehrung import Rissnormalkraft, ZwaengungBiegung
from opencivil.nachweis.spannungsbegrenzung import (
    GEFORDERT, Haeufigerfall, Spannungsbegrenzung,
)
from opencivil.nachweis.sproedes_versagen import SproedesVersagen
from opencivil.nachweis.querkraft import Querkraft, Querkraftfall
from opencivil.querschnitt.platte import (
    ALPHA_MAX, ALPHA_MIN, K_C, KRIECHZAHL, LAGENZAHL, Bewehrungslage,
    Bewehrungsposten, Plattenquerschnitt, Querkraftbewehrung, Richtung,
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


def _masse_pruefen(eintrag: "QuerschnittEintrag") -> None:
    """
    Haelt unmoegliche Abmessungen auf, bevor daraus Zahlen werden.

    Bis hierher lief jede Geometrie durch: eine Platte mit ``h = -300`` wurde
    gerechnet, eine mit beidseitiger Ueberdeckung groesser als die Dicke auch.
    Heraus kamen Zahlen, die aussahen wie ein Ergebnis. Ein Tragwerksnachweis
    darf an so etwas nicht vorbeirechnen -- er muss sagen, was nicht stimmt.

    Geprueft wird nur, was geometrisch unmoeglich ist, nicht was unueblich
    waere. Ob 20 mm Ueberdeckung fuer die Expositionsklasse genuegen,
    entscheidet der Ingenieur.
    """
    name = eintrag.name
    for feld, wert, wie in (
        ("Dicke h", eintrag.h, "grösser als null"),
        ("Breite b", eintrag.b, "grösser als null"),
        ("Grösstkorn D_max", eintrag.d_max, "grösser als null"),
    ):
        if wert <= 0.0:
            raise ProjektFehler(
                f"Platte '{name}': {feld} muss {wie} sein, angegeben ist {wert:g} mm.")

    for feld, wert in (("Überdeckung unten", eintrag.ueberdeckung_unten),
                       ("Überdeckung oben", eintrag.ueberdeckung_oben),
                       ("Einlagenhöhe", eintrag.einlagenhoehe)):
        if wert < 0.0:
            raise ProjektFehler(
                f"Platte '{name}': {feld} kann nicht negativ sein "
                f"({wert:g} mm).")

    zusammen = eintrag.ueberdeckung_unten + eintrag.ueberdeckung_oben
    if zusammen >= eintrag.h:
        raise ProjektFehler(
            f"Platte '{name}': die Überdeckungen ergeben zusammen {zusammen:g} mm "
            f"und lassen in einer {eintrag.h:g} mm dicken Platte keinen Platz für "
            f"Bewehrung.")


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


#: Anteil der Tragsicherheitslastfaelle, der als haeufiger Lastfall gilt,
#: solange keine eigenen angegeben sind.
HAEUFIG_ANTEIL = 0.70



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
class HaeufigEintrag(Beschreibung):
    """
    Eine Schnittgroessenkombination unter haeufiger Einwirkung.

    Wie :class:`KombinationEintrag`, aber ohne Querkraft: begrenzt wird die
    Stahlspannung, und dafuer zaehlen Moment und Normalkraft.
    """

    name: str
    M_Ed: float = 0.0
    N_Ed: float = 0.0
    aktiv: bool = True
    """Ob dieser Lastfall gerechnet wird. Ausgeschaltet bleibt er stehen."""

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "HaeufigEintrag":
        _nur_x(d, f"Der häufige Lastfall '{d.get('name')}'")
        return cls(
            name=_pflichtfeld(d, "name", "Ein häufiger Lastfall"),
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


@dataclass
class QuerschnittEintrag(Beschreibung):
    """Eine Stahlbeton-Platte mit genau vier Bewehrungslagen."""

    kennung: str
    name: str
    beton: str
    h: float = 300.0
    b: float = 1000.0
    ueberdeckung_unten: float = 30.0
    ueberdeckung_oben: float = 30.0
    d_max: float = 32.0
    """Grösstkorndurchmesser in mm."""

    einlagenhoehe: float = 0.0
    """Höhe einer Einlage in mm."""

    k_c: float = K_C
    """Abminderung der Betondruckfestigkeit in der Druckdiagonalen."""

    querkraftbewehrung: QuerkraftbewehrungEintrag = field(
        default_factory=QuerkraftbewehrungEintrag)
    """Bügel; ohne Durchmesser heisst: keine."""

    rissanforderung: str = "normal"
    """Anforderung an die Rissbildung -- ``normal``, ``erhoeht`` oder ``hoch``."""

    beschreibung: str = ""
    """
    Freier Text zur Platte -- was sonst nirgends hinpasst.

    Wo sie liegt, woher die Schnittgroessen stammen, was noch zu klaeren ist.
    Geht in keine Rechnung ein und steht in keinem Nachweis; sie wird
    gespeichert und wieder angezeigt, mehr nicht. Genau dafuer gibt es sie:
    ohne ein solches Feld landen solche Saetze im Namen der Platte.
    """

    kriechzahl: float = KRIECHZAHL
    """
    Kriechzahl phi fuer den gerissenen Zustand.

    Geht ueber ``n = (E_s/E_cm)*(1+phi)`` in den Hebelarm ein. Ein groesseres
    phi ist dabei **immer** der konservative Fall: die Nulllinie rutscht
    tiefer, der Hebelarm schrumpft, der aufnehmbare Moment sinkt.
    """

    zwaengung: bool = False
    """
    Ob mit einer Normalkraft-Zwaengung zu rechnen ist.

    Vorgabe aus: eine Zwaengung ist eine Annahme ueber das Tragwerk, keine
    Eigenschaft der Platte. Wer sie braucht, schaltet sie ein.

    Ein Schalter, nicht zwei: nachgewiesen wird nur die Tragrichtung x. Die
    y-Lagen stehen im Querschnitt, weil sie die statische Hoehe von x
    bestimmen und zum Bewehrungsgehalt zaehlen -- nachgewiesen werden sie
    nicht.
    """

    zwaengung_begrenzt: bool = False
    """Ob die Zwaengung auf 500 mm Plattendicke begrenzt angesetzt wird."""

    haeufige: List[HaeufigEintrag] = field(default_factory=list)
    """Eigene haeufige Lastfaelle; leer, solange die 70-%-Regel gilt."""

    knickfaelle: List[KnickEintrag] = field(default_factory=list)
    """Knicknachweise; leer heisst: keiner."""

    spannungsfaelle: List[SpannungsfallEintrag] = field(default_factory=list)
    """Auswertungen am Querschnitt -- Bilder, keine Nachweise."""

    haeufige_aus_tragsicherheit: bool = False
    """
    Ob die aus den Tragsicherheitsfaellen abgeleiteten haeufigen Lastfaelle
    *gefuehrt* werden -- mit :data:`HAEUFIG_ANTEIL`.

    Gebildet werden sie immer; ausgeschaltet rechnen sie still mit. Die 70 %
    sind eine bequeme Abschaetzung und keine Norm, darum stehen sie nur auf
    Verlangen in der Tabelle.
    """

    automatik_modus: str = "grund_ohne"
    """Wonach das Bewehrungswerkzeug sucht -- siehe ``bewehrungssuche.Suchmodus``."""

    automatik_teilungen: List[float] = field(default_factory=lambda: [150.0])
    """
    Teilungen, die es versucht. Grundbewehrung und Zulage teilen sich eine.

    Vorgabe ist die eine uebliche. Wer mehrere angibt, bekommt die mit der
    kleinsten Stahlflaeche -- das kostet aber je Teilung einen ganzen
    Suchlauf, und meistens steht die Teilung ohnehin fest.
    """

    automatik_mindestdurchmesser: float = 10.0
    """
    Duennster Stab, den die Suche einbaut -- in mm.

    Null bleibt davon unberuehrt: eine Lage ganz wegzulassen ist immer
    erlaubt. Gemeint ist, dass ein *vorhandener* Stab nicht duenner wird als
    das, was man verlegen will.
    """

    automatik_querkraft: bool = False
    """Ob auch die Buegel gesucht werden."""

    automatik_querkraft_teilungen: List[float] = field(
        default_factory=lambda: [100.0, 150.0, 200.0])

    sproede: bool = False
    """Ob der Nachweis gegen sproedes Versagen gefuehrt wird."""

    zwaengung_biegung: bool = False
    """Ob die Zwaengung auf Biegung nachgewiesen wird."""

    duktilitaet: bool = False
    """
    Ob der Duktilitaetsnachweis gefuehrt wird.

    Ein Schalter fuer die Platte und nicht einer je Lage. Gerechnet werden
    beide x-Lagen -- die obere traegt das Stuetz-, die untere das Feldmoment
    --, und in der Zusammenfassung steht die unguenstigere. Vier Schalter fuer
    einen Nachweis waren vier Gelegenheiten, den falschen zu vergessen; die
    Frage ist ohnehin, ob der Querschnitt sein Versagen ankuendigt, und die
    beantwortet die schlechtere Lage.
    """

    lagen: List[LageEintrag] = field(default_factory=list)
    """Genau vier, Index 0 = 1. Lage (unterste)."""

    richtung_lage1: str = "y"
    """
    Richtung der 1. Lage; die 2. bekommt die Gegenrichtung.

    Vorgabe y, damit x auf der 2. und 3. Lage liegt -- innen. Das ist der
    unguenstigere Fall und der haeufigere: die Tragrichtung liegt selten zu
    unterst, weil die Querrichtung darunter durchlaeuft. Wer es anders
    verlegt, stellt es um.
    """

    richtung_lage4: str = "y"
    """Richtung der 4. Lage; die 3. bekommt die Gegenrichtung."""

    kombinationen: List[KombinationEintrag] = field(default_factory=list)

    def __post_init__(self) -> None:
        while len(self.lagen) < LAGENZAHL:
            self.lagen.append(LageEintrag())
        del self.lagen[LAGENZAHL:]

    def richtung_von(self, nummer: int) -> Richtung:
        """Richtung der Lage 1..4 -- die Paare (1,2) und (3,4) sind gekoppelt."""
        eins = Richtung(self.richtung_lage1)
        vier = Richtung(self.richtung_lage4)
        return {1: eins, 2: eins.gegenrichtung, 3: vier.gegenrichtung, 4: vier}[nummer]


    @classmethod
    def neu(cls, kennung: str, name: str, beton: str, stahl: str,
            durchmesser: float = 12.0) -> "QuerschnittEintrag":
        """
        Eine frische Platte, wie sie der Benutzer angelegt bekommt.

        Steht hier und nicht in der Oberflaeche. Dort stand sie einmal -- ein
        Wortschatz aus zwanzig Feldern, den jemand von Hand mit den Vorgaben
        dieser Klasse gleichhalten musste. Beim ersten Mal, als sich die
        Vorgaben aenderten, lief er auseinander: neue Platten brachten
        Nachweise eingeschaltet mit, die ueberall sonst aus waren.

        Was hier steht, sind Entscheidungen und keine Vorgaben: alle vier
        Lagen bewehrt, ein Feldmoment zum Anfangen. Alles Uebrige kommt aus
        den Vorgabewerten der Felder.
        """
        def lage(d: float) -> LageEintrag:
            return LageEintrag(
                stahl=stahl,
                grund=PostenEintrag(durchmesser=d, abstand=150.0),
                # Auch die leere Zulage wird ueber die Teilung gefuehrt --
                # das ist der Regelfall bei Platten.
                zulage=PostenEintrag(durchmesser=0.0, abstand=150.0),
            )

        return cls(
            kennung=kennung,
            name=name,
            beton=beton,
            # Alle vier Lagen bewehrt. Nachgewiesen wird nur x -- das sind
            # die beiden inneren --, aber die aeusseren y-Lagen liegen
            # darunter und darueber und druecken die statische Hoehe von x
            # nach innen. Sie leer zu lassen hiesse, mit einer Hoehe zu
            # rechnen, die es auf der Baustelle nicht gibt.
            lagen=[lage(durchmesser) for _ in range(LAGENZAHL)],
            querkraftbewehrung=QuerkraftbewehrungEintrag(
                durchmesser=0.0, stahl=stahl),
            kombinationen=[KombinationEintrag(name="Feld", M_Ed=30.0)],
        )

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "QuerschnittEintrag":
        lagen = d.get("lagen")
        if lagen is None and ("lagen_unten" in d or "lagen_oben" in d):
            lagen = _lagen_aus_altem_format(d)
        kennung = _pflichtfeld(d, "kennung", "Ein Querschnitt")
        return cls(
            kennung=kennung,
            name=str(d.get("name") or kennung),
            beton=_pflichtfeld(d, "beton", f"Der Querschnitt '{kennung}'"),
            h=_zahl(d, "h", 300.0),
            b=_zahl(d, "b", 1000.0),
            ueberdeckung_unten=_zahl(d, "ueberdeckung_unten", 30.0),
            ueberdeckung_oben=_zahl(d, "ueberdeckung_oben", 30.0),
            d_max=_zahl(d, "d_max", 32.0),
            einlagenhoehe=_zahl(d, "einlagenhoehe", 0.0),
            k_c=_zahl(d, "k_c", K_C),
            querkraftbewehrung=QuerkraftbewehrungEintrag.aus_dict(
                d.get("querkraftbewehrung") or {}),
            duktilitaet=_schalter_aus(d.get("duktilitaet")),
            automatik_modus=str(d.get("automatik_modus") or "grund_ohne"),
            automatik_teilungen=_teilungen_aus(d.get("automatik_teilungen"),
                                               (150.0,)),
            automatik_mindestdurchmesser=_zahl(
                d, "automatik_mindestdurchmesser", 10.0),
            automatik_querkraft=bool(d.get("automatik_querkraft", False)),
            automatik_querkraft_teilungen=_teilungen_aus(
                d.get("automatik_querkraft_teilungen"), (100.0, 150.0, 200.0)),
            sproede=_schalter_aus(d.get("sproede"), d.get("sproede_lagen")),
            zwaengung_biegung=_schalter_aus(
                d.get("zwaengung_biegung"), d.get("zwaengung_biegung_lagen")),
            rissanforderung=_rissanforderung_aus(d.get("rissanforderung")),
            beschreibung=str(d.get("beschreibung") or ""),
            kriechzahl=_zahl(d, "kriechzahl", KRIECHZAHL),
            # Aus x und y wird einer: nachgewiesen wird nur noch x.
            zwaengung=_schalter_aus(d.get("zwaengung"), d.get("zwaengung_x"),
                                    d.get("zwaengung_y")),
            zwaengung_begrenzt=bool(d.get("zwaengung_begrenzt", False)),
            haeufige_aus_tragsicherheit=bool(
                d.get("haeufige_aus_tragsicherheit", False)),
            haeufige=[HaeufigEintrag.aus_dict(x) for x in (d.get("haeufige") or [])],
            knickfaelle=[KnickEintrag.aus_dict(x)
                         for x in (d.get("knickfaelle") or [])],
            spannungsfaelle=[SpannungsfallEintrag.aus_dict(x)
                             for x in (d.get("spannungsfaelle") or [])],
            richtung_lage1=str(d.get("richtung_lage1") or "y"),
            richtung_lage4=str(d.get("richtung_lage4") or "y"),
            lagen=[LageEintrag.aus_dict(x) for x in (lagen or [])],
            kombinationen=[
                KombinationEintrag.aus_dict(x) for x in (d.get("kombinationen") or [])],
        )


# ===========================================================================
# Aufbau
# ===========================================================================


@dataclass
class Aufbau:
    """Was beim Zusammenbauen eines Projekts entsteht."""

    werk: Rechenwerk
    baustoffe: Dict[str, Baustoff] = field(default_factory=dict)
    querschnitte: Dict[str, Plattenquerschnitt] = field(default_factory=dict)
    nachweise: Dict[str, BiegungNormalkraft] = field(default_factory=dict)
    """
    Schluessel ist ``<querschnitt>.x``.

    Die Richtung steht noch im Schluessel, obwohl es nur eine gibt -- sie sagt
    dem Leser einer Wert-ID, welcher Querschnitt gemeint ist, und die
    Wert-IDs in abgelegten Berichten sollen nicht bei jeder Umstellung
    wechseln.
    """

    querkraft: Dict[str, Querkraft] = field(default_factory=dict)
    duktilitaet: Dict[str, Duktilitaet] = field(default_factory=dict)
    """Schluessel ist die Querschnittskennung -- ein Nachweis je Platte."""

    rissnormalkraft: Dict[str, Rissnormalkraft] = field(default_factory=dict)
    """Schluessel ist ``<querschnitt>.x``."""

    sproede: Dict[str, SproedesVersagen] = field(default_factory=dict)
    """Mindestbewehrung gegen sproedes Versagen, je ``<querschnitt>.x``."""

    zwaengung_biegung: Dict[str, ZwaengungBiegung] = field(default_factory=dict)
    """Zwaengung auf Biegung, je ``<querschnitt>.x``."""

    spannung: Dict[str, Spannungsbegrenzung] = field(default_factory=dict)
    """Stahlspannung unter haeufiger Einwirkung, je ``<querschnitt>.<richtung>``."""

    knicken: Dict[str, Knicken] = field(default_factory=dict)
    """Nachweis am verformten System, je Querschnitt -- nur in x-Richtung."""

    fehlende: Dict[str, FehlendeBewehrung] = field(default_factory=dict)
    """
    Je Richtung ohne Bewehrung, fuer die dennoch Einwirkungen angegeben sind.

    Sie rechnen nichts; sie sorgen dafuer, dass in der Zusammenfassung eine
    Zeile mit Erfuellungsgrad null steht statt gar nichts.
    """

    spannungsfaelle: Dict[str, List["SpannungsfallEintrag"]] = field(
        default_factory=dict)
    """
    Je Platte die Auswertungen am Querschnitt -- als Beschreibung, nicht als
    Nachweis. Sie laufen nicht im Rechenwerk: sie haben kein Ziel, das jemand
    anderes brauchen koennte, und nichts haengt von ihnen ab.
    """

    warnungen: List[str] = field(default_factory=list)

    #: Die Felder, in denen die Nachweise einer Platte stehen -- die eine
    #: Stelle, an der ein neuer Nachweis eingetragen wird. Alle sind nach
    #: Kennung geschluesselt (``q1`` oder ``q1.x``) und alle tragen Nachweise
    #: mit ``d_ausnutzung``. Daraus ergeben sich Rechenziele, Aufteilen nach
    #: Platte und Zwischenspeichern von selbst; frueher stand dieselbe Liste
    #: viermal da, und wer einen Nachweis hinzufuegte, musste alle vier
    #: finden.
    NACHWEISFELDER = ("nachweise", "querkraft", "duktilitaet", "fehlende",
                      "rissnormalkraft", "sproede", "zwaengung_biegung",
                      "spannung", "knicken")

    def nachweise_je_feld(self):
        """Alle Nachweise, Feld fuer Feld und in der Reihenfolge der Liste."""
        for feld in self.NACHWEISFELDER:
            yield feld, getattr(self, feld)

    def alle_nachweise(self):
        """Jeden Nachweis einmal, in derselben Reihenfolge wie im Protokoll."""
        for _, eintraege in self.nachweise_je_feld():
            yield from eintraege.values()

    def alle_nachweisziele(self) -> List[str]:
        return [d.id for n in self.alle_nachweise()
                for d in n.d_ausnutzung.values()]

    def gehoert_zu(self, schluessel: str, kennung: str) -> bool:
        """Ob ein Feldschluessel (``q1`` oder ``q1.x``) zu dieser Platte gehoert."""
        return schluessel == kennung or schluessel.startswith(f"{kennung}.")

    def teile_von(self, kennung: str) -> Dict[str, Dict[str, Any]]:
        """
        Alle Nachweisobjekte einer Platte, nach Feld geordnet.

        Gebraucht vom Zwischenspeicher: ein uebernommenes Ergebnis besteht
        nicht nur aus Zahlen, sondern auch aus dem, was die Nachweise sich
        beim Rechnen gemerkt haben -- Interaktionslinien, Fallergebnisse,
        Iterationsschritte. Die Schnittstelle liest das aus den Objekten, also
        muessen die Objekte mitwandern und nicht bloss ihre Ausgabewerte.
        """
        return {feld: {s: w for s, w in eintraege.items()
                       if self.gehoert_zu(s, kennung)}
                for feld, eintraege in self.nachweise_je_feld()}

    def teile_setzen(self, kennung: str, teile: Mapping[str, Dict[str, Any]]) -> None:
        """Die Nachweisobjekte einer Platte durch frueher gerechnete ersetzen."""
        for feld, eintraege in teile.items():
            ziel = getattr(self, feld)
            for schluessel in [s for s in ziel if self.gehoert_zu(s, kennung)]:
                del ziel[schluessel]
            ziel.update(eintraege)

    def ziele_von(self, kennung: str) -> List[str]:
        """Die Rechenziele einer einzelnen Platte -- Eckwerte und Nachweise."""
        alle = self.eckwertziele() + self.alle_nachweisziele()
        raeume = {w.id for _, eintraege in self.nachweise_je_feld()
                  for s, w in eintraege.items() if self.gehoert_zu(s, kennung)}
        return [z for z in alle if any(z.startswith(f"{r}.") for r in raeume)]

    def eckwertziele(self) -> List[str]:
        return [d.id for n in self.nachweise.values() for d in n.d_eckwerte.values()]

    def materialziele(self) -> List[str]:
        """
        Saemtliche Kennwerte aller Materialien -- Beton zuerst, dann Betonstahl.

        Gehoert zum Regellauf: ein Material, das noch keine Platte verwendet,
        waere sonst nie Ziel und bliebe ungerechnet -- im Editor staenden dann
        leere Felder, obwohl die Sorte alles hergibt.

        Die Reihenfolge bestimmt zugleich den Aufbau der Herleitung: der Loeser
        arbeitet die Ziele der Reihe nach ab, und das Protokoll folgt ihm. So
        stehen im Bericht erst die Baustoffe und dann die Bauteile.
        """
        nach_art = {"beton": [], "betonstahl": []}
        for stoff in self.baustoffe.values():
            nach_art.setdefault(stoff.art.value, []).extend(
                d.id for d in stoff.definitionen.values())
        return nach_art["beton"] + nach_art["betonstahl"]


# ===========================================================================
# Projekt
# ===========================================================================


@dataclass
class Projekt(Beschreibung):
    """Die vollstaendige, speicherbare Beschreibung eines Projekts."""

    name: str = "Neues Projekt"
    materialien: List[MaterialEintrag] = field(default_factory=list)
    querschnitte: List[QuerschnittEintrag] = field(default_factory=list)

    # -- Zugriff ------------------------------------------------------------

    def material(self, kennung: str) -> MaterialEintrag:
        for m in self.materialien:
            if m.kennung == kennung:
                return m
        raise ProjektFehler(f"Material '{kennung}' gibt es im Projekt nicht.")

    def querschnitt(self, kennung: str) -> QuerschnittEintrag:
        for q in self.querschnitte:
            if q.kennung == kennung:
                return q
        raise ProjektFehler(f"Querschnitt '{kennung}' gibt es im Projekt nicht.")

    def freie_kennung(self, vorsilbe: str) -> str:
        vergeben = {m.kennung for m in self.materialien} | {
            q.kennung for q in self.querschnitte}
        i = 1
        while f"{vorsilbe}{i}" in vergeben:
            i += 1
        return f"{vorsilbe}{i}"

    def freier_name(self, wunsch: str, ausser: str = "") -> str:
        """Haengt bei Bedarf _1, _2, ... an, bis der Name eindeutig ist."""
        vergeben = {m.anzeigename for m in self.materialien if m.kennung != ausser}
        if wunsch not in vergeben:
            return wunsch
        i = 1
        while f"{wunsch}_{i}" in vergeben:
            i += 1
        return f"{wunsch}_{i}"

    def abgeleiteter_name(self, sorte: str, ausser: str = "") -> str:
        """
        Erster freier Name der Form ``<Sorte>_1``, ``<Sorte>_2``, ...

        Nicht ueber :meth:`freier_name` mit dem Wunsch ``C30/37_1``, denn das
        haengte bei Belegung nochmals an und ergaebe ``C30/37_1_1``.
        """
        vergeben = {m.anzeigename for m in self.materialien if m.kennung != ausser}
        i = 1
        while f"{sorte}_{i}" in vergeben:
            i += 1
        return f"{sorte}_{i}"

    def material_loesen(self, kennung: str) -> MaterialEintrag:
        """
        Macht aus einer Normsorte ein eigenstaendiges, aenderbares Material.

        Der Name wird dabei zwingend geaendert -- die Sortenbezeichnung bleibt
        der unveraenderten Norm vorbehalten.
        """
        eintrag = self.material(kennung)
        if eintrag.eigenstaendig:
            return eintrag
        eintrag.eigenstaendig = True
        eintrag.name = self.abgeleiteter_name(eintrag.sorte, ausser=kennung)
        return eintrag

    # -- Pruefung -----------------------------------------------------------

    def pruefen(self) -> None:
        """Prueft die Beschreibung, bevor daraus gerechnet wird."""
        for m in self.materialien:
            m.pruefen()

        gesehen: Dict[str, str] = {}
        for m in self.materialien:
            if m.anzeigename in gesehen:
                raise ProjektFehler(
                    f"Der Name '{m.anzeigename}' ist zweimal vergeben "
                    f"({gesehen[m.anzeigename]} und {m.kennung}). Materialnamen "
                    f"müssen eindeutig sein, sonst lässt sich im Bericht nicht "
                    f"erkennen, welches gemeint ist.")
            gesehen[m.anzeigename] = m.kennung

        for eintrag in self.querschnitte:
            self._namen_pruefen(eintrag)

    @staticmethod
    def _namen_pruefen(eintrag: "QuerschnittEintrag") -> None:
        """
        Lastfallnamen muessen je Platte und Liste eindeutig sein.

        Die Nachweise legen ihre Ergebniswerte unter dem Fallnamen ab -- M-N,
        Querkraft und Stahlspannung alle drei. Zwei Kombinationen gleichen
        Namens fielen darum auf einen Eintrag zusammen: der zweite ueberschrieb
        den ersten, und in der Tabelle fehlte eine Zeile. Kein Fehler, keine
        Warnung, eine Zahl weniger.

        Gemeldet statt umbenannt: welcher der beiden gemeint war, weiss nur
        der Benutzer, und ein automatisch angehaengtes «(2)» stuende danach in
        seinem Bericht.
        """
        def eindeutig(faelle, was: str) -> None:
            gesehen = set()
            for f in faelle:
                if f.name in gesehen:
                    raise ProjektFehler(
                        f"Platte '{eintrag.name}': der Name '{f.name}' ist "
                        f"zweimal als {was} vergeben. Die Nachweise legen ihre "
                        f"Ergebnisse unter dem Fallnamen ab -- zwei gleiche "
                        f"Namen ergeben eine Zeile statt zwei.")
                gesehen.add(f.name)

        eindeutig(eintrag.kombinationen, "Tragsicherheitseinwirkung")
        eindeutig(eintrag.haeufige, "häufiger Lastfall")
        eindeutig(eintrag.knickfaelle, "Knicknachweis")
        eindeutig(eintrag.spannungsfaelle, "Spannung-Dehnung-Analyse")

        # Die abgeleiteten Faelle tragen den Namen ihrer Kombination mit
        # angehaengtem Anteil. Wer einen eigenen Lastfall genau so nennt,
        # traefe denselben Schluessel.
        abgeleitet = {f"{k.name} ({HAEUFIG_ANTEIL * 100:.0f} %)"
                      for k in eintrag.kombinationen}
        for h in eintrag.haeufige:
            if h.name in abgeleitet:
                raise ProjektFehler(
                    f"Platte '{eintrag.name}': der häufige Lastfall "
                    f"'{h.name}' heisst wie der aus der Tragsicherheit "
                    f"abgeleitete. Bitte anders benennen -- sonst lässt sich "
                    f"nicht auseinanderhalten, welcher gerechnet wurde.")

    # -- Aufbau -------------------------------------------------------------

    def aufbauen(self, *, schnell: bool = False) -> Aufbau:
        """
        Baut aus der Beschreibung ein vollstaendiges Rechenwerk.

        Wirft :class:`ProjektFehler`, wenn die Beschreibung nicht stimmig ist --
        etwa wenn ein Querschnitt auf ein geloeschtes Material verweist.

        Mit ``schnell`` lassen Nachweise teure Nebenrechnungen weg, die das
        Urteil nicht aendern -- derzeit die Suche nach der Knickgrenzkraft.
        Gedacht fuer das Bewehrungswerkzeug, das hundertfach rechnet und nur
        wissen muss, ob es aufgeht. Fuer eine Herleitung ist das nichts: dort
        soll die Zahl stehen, die auch in der Tabelle steht.
        """
        self.pruefen()
        werk = Rechenwerk()
        aufbau = Aufbau(werk=werk)

        # Nur wenn mehrere Materialien derselben Art vorkommen, braucht es
        # Indizes an den Symbolen -- sonst waere f_{cd,C30/37} bloss Ballast.
        je_art: Dict[str, int] = {}
        for m in self.materialien:
            je_art[m.art] = je_art.get(m.art, 0) + 1

        for eintrag in self.materialien:
            index = eintrag.anzeigename if je_art[eintrag.art] > 1 else ""
            aufbau.baustoffe[eintrag.kennung] = self._baustoff(eintrag, index)

        for eintrag in self.querschnitte:
            querschnitt = self._querschnitt(eintrag, aufbau.baustoffe)
            aufbau.querschnitte[eintrag.kennung] = querschnitt
            querschnitt.ins_rechenwerk(werk)

            bewehrt = set(querschnitt.richtungen_mit_bewehrung)

            # Die vier Schalter durch denselben Leser wie beim Einlesen.
            # Wer eine alte Beschreibung im Speicher haelt, traegt dort noch
            # eine Liste -- und `[False, False, False, False]` ist als Wahrheit
            # *wahr*. Der Nachweis stuende dann eingeschaltet da, obwohl jeder
            # einzelne Haken aus ist.
            an_duktil = _schalter_aus(eintrag.duktilitaet)
            an_sproede = _schalter_aus(eintrag.sproede)
            an_biegung = _schalter_aus(eintrag.zwaengung_biegung)
            an_zwang = _schalter_aus(eintrag.zwaengung)

            # Nachgewiesen wird nur die Tragrichtung x. Die y-Lagen stehen
            # im Querschnitt -- sie tragen zum Bewehrungsgehalt bei und
            # druecken die statische Hoehe von x nach innen --, aber kein
            # Nachweis fragt nach ihnen. Vorher lief hier alles doppelt,
            # einmal je Richtung, und die Haelfte der Tabelle handelte von
            # einer Richtung, fuer die niemand Schnittgroessen hatte.
            richtung = Richtung.X
            aktiv = [k for k in eintrag.kombinationen if k.aktiv]

            if richtung not in bewehrt:
                if aktiv:
                    # Ohne Bewehrung laesst sich hier nichts aufstellen. Der
                    # Nachweis entfiel frueher stillschweigend; wer eine
                    # Einwirkung angegeben hatte, fand sie nirgends wieder.
                    fehlend = FehlendeBewehrung(
                        querschnitt, richtung,
                        self._ausgefallene(aktiv, richtung))
                    werk.registriere(fehlend)
                    aufbau.fehlende[f"{eintrag.kennung}.x"] = fehlend
            else:
                # Der M-N-Nachweis entsteht auch ohne Schnittgroessen: seine
                # Eckwerte gehoeren dem Querschnitt, nicht der Einwirkung, und
                # der Nachweis gegen sproedes Versagen haelt M_Rd(N=0) dagegen.
                # Ohne die genaue Resistenzlinie, wenn schnell gerechnet wird:
                # sie kostet fast die ganze Zeit dieses Nachweises und wird
                # allein im Diagramm gebraucht. Wer schnell rechnet, sucht eine
                # Bewehrung und sieht dabei kein Diagramm an.
                nachweis = BiegungNormalkraft(
                    querschnitt, [self._kombination(k) for k in aktiv], richtung,
                    mit_linie=not schnell)
                werk.registriere(nachweis)
                aufbau.nachweise[f"{eintrag.kennung}.x"] = nachweis

                # Die beiden x-Lagen, von unten nach oben. Beide werden
                # gerechnet; in die Zusammenfassung kommt die unguenstigere.
                lagen = [l.nummer for l in querschnitt.lagen
                         if l.richtung is richtung]
                if lagen:
                    nachweis_sv = SproedesVersagen(
                        querschnitt, richtung, lagen, nachweis)
                    nachweis_sv.still = not an_sproede
                    werk.registriere(nachweis_sv)
                    aufbau.sproede[f"{eintrag.kennung}.x"] = nachweis_sv

                    biegung = ZwaengungBiegung(
                        querschnitt, richtung, lagen,
                        anforderung=eintrag.rissanforderung,
                        kriechzahl=eintrag.kriechzahl)
                    biegung.still = not an_biegung
                    werk.registriere(biegung)
                    aufbau.zwaengung_biegung[f"{eintrag.kennung}.x"] = biegung

                    zwang = Rissnormalkraft(
                        querschnitt, richtung,
                        anforderung=eintrag.rissanforderung,
                        begrenzt=eintrag.zwaengung_begrenzt)
                    zwang.still = not an_zwang
                    werk.registriere(zwang)
                    aufbau.rissnormalkraft[f"{eintrag.kennung}.x"] = zwang

                    duktilitaet = Duktilitaet(querschnitt, lagen)
                    duktilitaet.still = not an_duktil
                    werk.registriere(duktilitaet)
                    aufbau.duktilitaet[eintrag.kennung] = duktilitaet

                # Stahlspannung unter haeufiger Einwirkung. Nur bei erhoehter
                # und hoher Anforderung -- bei normaler steht in Tabelle 17
                # ein Strich.
                haeufige, laute = self._haeufige(eintrag)
                if haeufige and eintrag.rissanforderung in GEFORDERT:
                    spannung = Spannungsbegrenzung(querschnitt, richtung, haeufige)
                    spannung.stillstellen([f.name for f in haeufige], laute)
                    werk.registriere(spannung)
                    aufbau.spannung[f"{eintrag.kennung}.x"] = spannung

                mit_querkraft = [k for k in aktiv if k.V_Ed]
                if mit_querkraft:
                    querkraft = Querkraft(
                        querschnitt,
                        [Querkraftfall(name=k.name,
                                       V_Ed=Groesse(k.V_Ed, KN_PRO_M),
                                       M_Ed=Groesse(k.M_Ed, KNM),
                                       N_Ed=Groesse(k.N_Ed, KN))
                         for k in mit_querkraft],
                        richtung, nachweis)
                    werk.registriere(querkraft)
                    aufbau.querkraft[f"{eintrag.kennung}.x"] = querkraft

                knickfaelle = [k for k in eintrag.knickfaelle if k.aktiv]
                if knickfaelle:
                    knick = Knicken(
                        querschnitt,
                        [Knickfall(name=k.name,
                                   N_Ed=Groesse(k.N_Ed, KN),
                                   M_Ed_1=Groesse(k.M_Ed_1, KNM),
                                   laenge=Groesse(k.laenge, M),
                                   knicklaenge=Groesse(k.knicklaenge, M))
                         for k in knickfaelle],
                        nachweis, schnell=schnell)
                    werk.registriere(knick)
                    aufbau.knicken[eintrag.kennung] = knick
            if richtung not in bewehrt and eintrag.knickfaelle:
                aufbau.warnungen.append(
                    f"Platte '{eintrag.name}': Knicken braucht Bewehrung in "
                    f"x-Richtung; ohne sie entfällt der Nachweis.")

            aktive = [s for s in eintrag.spannungsfaelle if s.aktiv]
            if aktive:
                aufbau.spannungsfaelle[eintrag.kennung] = aktive

            if not eintrag.kombinationen:
                aufbau.warnungen.append(
                    f"Platte '{eintrag.name}': keine Schnittgrössen angegeben, "
                    f"also kein Tragsicherheitsnachweis möglich.")

        for baustoff in aufbau.baustoffe.values():
            baustoff.ins_rechenwerk(werk)

        self._ueberschreibungen_setzen(werk, aufbau)
        return aufbau

    def _baustoff(self, eintrag: MaterialEintrag, symbol_index: str) -> Baustoff:
        bauer = {"beton": beton, "betonstahl": betonstahl}[eintrag.art]
        roh = bauer(eintrag.sorte, praefix=f"{eintrag.art}.{eintrag.kennung}")
        # Jeder Kennwert dieser beiden Baustoffe ist seiner Natur nach positiv:
        # Festigkeiten, Moduln, Dehnungen, Teilsicherheitsbeiwerte. Eine Null
        # oder ein negativer Wert liefert keine falsche Zahl, sondern gar keine
        # -- gamma_c = 0 endete in einem ZeroDivisionError, ein negatives f_ck
        # in einer komplexen Wurzel. Beides kam als Absturzmeldung beim
        # Benutzer an.
        for topf, wie in ((eintrag.abweichungen, "abweichender Wert"),
                          (eintrag.ueberschreibungen, "überschriebener Wert")):
            for kurzname, zahl in topf.items():
                if zahl <= 0.0:
                    raise ProjektFehler(
                        f"'{eintrag.anzeigename}': {kurzname} muss grösser als null "
                        f"sein, angegeben ist {zahl:g} ({wie}).")
        abweichungen = {
            kurzname: Groesse(zahl, roh.definition(kurzname).einheit)
            for kurzname, zahl in eintrag.abweichungen.items()
            if kurzname in roh.definitionen
        }
        return bauer(
            eintrag.sorte,
            name=eintrag.anzeigename,
            praefix=f"{eintrag.art}.{eintrag.kennung}",
            abweichungen=abweichungen,
            symbol_index=symbol_index,
        )

    def _querschnitt(
        self, eintrag: QuerschnittEintrag, baustoffe: Mapping[str, Baustoff]
    ) -> Plattenquerschnitt:
        beton_stoff = baustoffe.get(eintrag.beton)
        if beton_stoff is None:
            raise ProjektFehler(
                f"Platte '{eintrag.name}' verweist auf das Material "
                f"'{eintrag.beton}', das es nicht (mehr) gibt.")
        _masse_pruefen(eintrag)

        lagen: List[Bewehrungslage] = []
        for nummer, lage in enumerate(eintrag.lagen, start=1):
            stahl = baustoffe.get(lage.stahl)
            if stahl is None and lage.vorhanden:
                raise ProjektFehler(
                    f"Die {nummer}. Lage von '{eintrag.name}' verweist auf den Stahl "
                    f"'{lage.stahl}', den es nicht (mehr) gibt.")
            lagen.append(Bewehrungslage(
                nummer=nummer,
                richtung=eintrag.richtung_von(nummer),
                stahl=stahl or next(iter(
                    s for s in baustoffe.values() if s.art.value == "betonstahl"), None),
                grund=lage.grund.als_posten(),
                zulage=lage.zulage.als_posten(),
                unguenstig=lage.unguenstig,
            ))

        if not any(l.vorhanden for l in lagen):
            raise ProjektFehler(
                f"Platte '{eintrag.name}': ohne Bewehrung lässt sich kein "
                f"Widerstand bestimmen.")

        buegel = eintrag.querkraftbewehrung
        buegel.pruefen(f"Platte '{eintrag.name}'")
        buegelstahl = baustoffe.get(buegel.stahl)
        if buegelstahl is None and buegel.stahl:
            raise ProjektFehler(
                f"Die Querkraftbewehrung von '{eintrag.name}' verweist auf den "
                f"Stahl '{buegel.stahl}', den es nicht (mehr) gibt.")
        if buegelstahl is None:
            # Kein Stahl angegeben -- wie bei den Lagen gilt dann der erste im
            # Projekt. Eine Beschreibung aus der Zeit vor den Buegeln nennt
            # keinen, und daran soll der ganze Lauf nicht scheitern.
            buegelstahl = next(
                (s for s in baustoffe.values() if s.art.value == "betonstahl"), None)
        if buegel.vorhanden and buegelstahl is None:
            raise ProjektFehler(
                f"Die Querkraftbewehrung von '{eintrag.name}' braucht einen "
                f"Betonstahl, im Projekt gibt es aber keinen.")

        return Plattenquerschnitt(
            name=eintrag.name,
            h=Groesse(eintrag.h, MM),
            b=Groesse(eintrag.b, MM),
            beton=beton_stoff,
            lagen=lagen,
            ueberdeckung_unten=Groesse(eintrag.ueberdeckung_unten, MM),
            ueberdeckung_oben=Groesse(eintrag.ueberdeckung_oben, MM),
            d_max=Groesse(eintrag.d_max, MM),
            einlagenhoehe=Groesse(eintrag.einlagenhoehe, MM),
            k_c=Groesse(eintrag.k_c, EINHEITSLOS),
            kriechzahl=Groesse(eintrag.kriechzahl, EINHEITSLOS),
            querkraftbewehrung=(buegel.als_bewehrung(buegelstahl)
                                if buegel.vorhanden else None),
            praefix=f"querschnitt.{eintrag.kennung}",
        )

    def _haeufige(self, eintrag: "QuerschnittEintrag",
                  ) -> Tuple[List[Haeufigerfall], List[str]]:
        """
        Die haeufigen Lastfaelle -- und welche davon laut sind.

        Die eigens angegebenen, und zusaetzlich die Tragsicherheitsfaelle mit
        :data:`HAEUFIG_ANTEIL`. Beides nebeneinander: die 70 % sind eine
        bequeme Abschaetzung, decken aber nicht den Fall ab, den es nur unter
        haeufiger Einwirkung gibt. Wer einen solchen kennt, soll ihn
        dazustellen koennen, ohne die Abschaetzung fuer alle anderen
        aufzugeben.

        Die abgeleiteten Faelle entstehen auch dann, wenn ihr Schalter aus
        ist -- dann eben still. Sie ganz wegzulassen hiesse, den Nachweis erst
        auf Verlangen zu fuehren; so steht wenigstens ein Hinweis da, wenn die
        Abschaetzung nicht aufgeht.

        **Was das kostet.** Jeder Fall ist ein Gleichgewicht am gerissenen
        Querschnitt, also ein Durchlauf des Faserloesers -- rund 8 ms, und
        damit der teuerste stille Nachweis, den es hier gibt. Gemessen an der
        Beispielplatte: bei normaler Anforderung entsteht er gar nicht (47 ms
        gesamt), bei erhoehter kostet er die Haelfte der Rechenzeit (98 ms).
        Ob der Schalter dabei an oder aus steht, macht keinen Unterschied --
        bei erhoehter Anforderung verlangt die Norm den Nachweis ohnehin, und
        ausgeschaltet ist nur die Frage, ob man ihn sehen will. Wer die Zeit
        zurueckhaben will, kommt nicht an dieser Stelle weiter, sondern am
        Loeser oder daran, die stillen Nachweise erst nach dem sichtbaren
        Ergebnis nachzuziehen.

        Die Rechnung steht hier und nicht in der Oberflaeche: dort waere sie
        eine zweite Wahrheit.
        """
        abgeleitet = [
            Haeufigerfall(
                name=f"{k.name} ({HAEUFIG_ANTEIL * 100:.0f} %)",
                M_Ed=Groesse(HAEUFIG_ANTEIL * k.M_Ed, KNM),
                N_Ed=Groesse(HAEUFIG_ANTEIL * k.N_Ed, KN))
            for k in eintrag.kombinationen if k.aktiv
        ]
        eigene = [
            Haeufigerfall(name=h.name,
                          M_Ed=Groesse(h.M_Ed, KNM),
                          N_Ed=Groesse(h.N_Ed, KN))
            for h in eintrag.haeufige if h.aktiv
        ]
        laute = [f.name for f in eigene]
        if eintrag.haeufige_aus_tragsicherheit:
            laute += [f.name for f in abgeleitet]
        return abgeleitet + eigene, laute

    def _ausgefallene(
        self, kombinationen: Sequence[KombinationEintrag], richtung: Richtung
    ) -> List[Ausgefallen]:
        """
        Welche Nachweise in dieser unbewehrten Richtung ausfallen.

        Je Kombination der M-N-Nachweis, und wo eine Querkraft angegeben ist,
        auch der Querkraftnachweis: ohne Bewehrung gibt es keine statische
        Hoehe, also auch keinen Querkraftwiderstand. Beide Zeilen gehoeren in
        die Tabelle -- eine davon wegzulassen hiesse, die Luecke nur zur
        Haelfte zu schliessen.
        """
        r = richtung.value
        # Erst alle M-N, dann alle Querkraft -- dieselbe Folge wie bei den
        # Richtungen, die wirklich gerechnet werden. Zeilen derselben Art
        # gehoeren beieinander.
        return [
            Ausgefallen(
                art="M-N", langname="Biegung und Normalkraft",
                fall=k.name,
                symbol=f"M_{{Rd,{r}}}",
                einwirkung_symbol=f"M_{{Ed,{r}}}",
                einwirkung=Groesse(k.M_Ed, KNM), einheit=KNM)
            for k in kombinationen
        ] + [
            Ausgefallen(
                art="V", langname="Querkraft", fall=k.name,
                symbol=f"V_{{Rd,{r}}}",
                einwirkung_symbol=f"V_{{Ed,{r}}}",
                einwirkung=Groesse(abs(k.V_Ed), KN_PRO_M), einheit=KN_PRO_M)
            for k in kombinationen if k.V_Ed
        ]

    def _kombination(self, eintrag: KombinationEintrag) -> Schnittgroessen:
        try:
            art = Erfuellungsart(eintrag.art)
        except ValueError:
            raise ProjektFehler(
                f"Unbekannter Massstab '{eintrag.art}'. Möglich sind: "
                f"{', '.join(a.value for a in Erfuellungsart)}.") from None
        return Schnittgroessen(
            name=eintrag.name,
            M_Ed=Groesse(eintrag.M_Ed, KNM),
            N_Ed=Groesse(eintrag.N_Ed, KN),
            art=art,
        )

    def _ueberschreibungen_setzen(self, werk: Rechenwerk, aufbau: Aufbau) -> None:
        for eintrag in self.materialien:
            baustoff = aufbau.baustoffe[eintrag.kennung]
            for kurzname, zahl in eintrag.ueberschreibungen.items():
                if kurzname not in baustoff.definitionen:
                    aufbau.warnungen.append(
                        f"Material '{baustoff.name}': Kennwert '{kurzname}' ist "
                        f"unbekannt, die Überschreibung wird übergangen.")
                    continue
                definition = baustoff.definition(kurzname)
                werk.setze(definition.id, Groesse(zahl, definition.einheit))

    # -- Speichern ----------------------------------------------------------


    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "Projekt":
        return cls(
            name=str(d.get("name") or "Neues Projekt"),
            materialien=[MaterialEintrag.aus_dict(x) for x in (d.get("materialien") or [])],
            querschnitte=[QuerschnittEintrag.aus_dict(x) for x in (d.get("querschnitte") or [])],
        )

    def speichern(self, pfad: str | Path) -> Path:
        ziel = Path(pfad)
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(
            json.dumps(self.als_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return ziel

    @classmethod
    def laden(cls, pfad: str | Path) -> "Projekt":
        return cls.aus_dict(json.loads(Path(pfad).read_text(encoding="utf-8")))

    # -- Startpunkt ---------------------------------------------------------

    @classmethod
    def beispiel(cls) -> "Projekt":
        """Ein lauffähiges Beispiel, damit die Oberfläche nicht leer startet."""
        def lage(phi: float, zulage: float = 0.0) -> LageEintrag:
            return LageEintrag(
                stahl="s1",
                grund=PostenEintrag(durchmesser=phi, abstand=150.0),
                zulage=PostenEintrag(durchmesser=zulage, abstand=150.0),
            )

        return cls(
            name="Beispiel – Decke über EG",
            materialien=[
                MaterialEintrag(kennung="b1", art="beton", sorte="C30/37", name="C30/37"),
                MaterialEintrag(kennung="s1", art="betonstahl", sorte="B500B", name="B500B"),
            ],
            querschnitte=[QuerschnittEintrag(
                kennung="q1", name="Decke über EG", beton="b1",
                h=300.0, b=1000.0,
                # Aussen y, innen x -- der übliche Fall: die Querrichtung
                # läuft unten und oben durch, die Tragrichtung liegt dazwischen
                # und verliert dadurch statische Höhe.
                richtung_lage1="y", richtung_lage4="y",
                lagen=[
                    lage(12.0),                # 1. Lage y, unten aussen
                    lage(18.0, zulage=12.0),   # 2. Lage x, mit Zulage
                    lage(12.0),                # 3. Lage x
                    lage(12.0),                # 4. Lage y, oben aussen
                ],
                # Die Werte sind so gewählt, dass das Beispiel grün startet.
                kombinationen=[
                    KombinationEintrag(name="Feld", M_Ed=100.0, N_Ed=0.0),
                    KombinationEintrag(name="Feld mit Druck", M_Ed=100.0, N_Ed=-300.0),
                    KombinationEintrag(name="Stütze", M_Ed=-50.0, N_Ed=0.0),
                ])],
        )
