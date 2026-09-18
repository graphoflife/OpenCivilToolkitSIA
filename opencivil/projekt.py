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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, KN_PRO_M, MM, Groesse
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.basis import Baustoff
from opencivil.material.beton import BETONSORTEN, beton
from opencivil.material.betonstahl import STAHLSORTEN, betonstahl
from opencivil.nachweis.biegung_normalkraft import (
    BiegungNormalkraft, Erfuellungsart, Schnittgroessen,
)
from opencivil.nachweis.duktilitaet import Duktilitaet
from opencivil.nachweis.fehlende_bewehrung import Ausgefallen, FehlendeBewehrung
from opencivil.nachweis.querkraft import Querkraft, Querkraftfall
from opencivil.querschnitt.platte import (
    ALPHA_MAX, ALPHA_MIN, K_C, LAGENZAHL, Bewehrungslage, Bewehrungsposten,
    Plattenquerschnitt, Querkraftbewehrung, Richtung,
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


#: Fuer welche Lagen der Duktilitaetsnachweis vorgegeben ist -- die beiden
#: aeusseren. Sie tragen Feld- und Stuetzmoment; dort entscheidet sich, ob der
#: Querschnitt sein Versagen ankuendigt.
DUKTILITAET_VORGABE = (True, False, False, True)


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


def _duktilitaet_aus(wert: Any) -> List[bool]:
    """
    Genau vier Schalter, egal was in der Datei steht.

    Eine Beschreibung aus der Zeit vor diesem Nachweis hat das Feld nicht --
    dann gilt die Vorgabe. Eine zu kurze oder zu lange Liste wird auf vier
    gebracht, statt spaeter beim Zugriff auf Lage 4 zu stolpern.
    """
    if not isinstance(wert, (list, tuple)):
        return list(DUKTILITAET_VORGABE)
    schalter = [bool(x) for x in wert[:LAGENZAHL]]
    schalter += list(DUKTILITAET_VORGABE[len(schalter):])
    return schalter


# ===========================================================================
# Material
# ===========================================================================


@dataclass
class MaterialEintrag:
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

    def als_dict(self) -> dict:
        return {
            "kennung": self.kennung, "art": self.art, "sorte": self.sorte,
            "name": self.anzeigename, "eigenstaendig": self.eigenstaendig,
            "abweichungen": dict(self.abweichungen),
            "ueberschreibungen": dict(self.ueberschreibungen),
        }

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
class PostenEintrag:
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

    def als_dict(self) -> dict:
        return {"durchmesser": self.durchmesser, "abstand": self.abstand,
                "anzahl": self.anzahl}

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
class LageEintrag:
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

    def als_dict(self) -> dict:
        return {"stahl": self.stahl, "grund": self.grund.als_dict(),
                "zulage": self.zulage.als_dict(), "unguenstig": self.unguenstig}

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
class QuerkraftbewehrungEintrag:
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

    def als_dict(self) -> dict:
        return {
            "durchmesser": self.durchmesser, "stahl": self.stahl,
            "abstand_x": self.abstand_x, "abstand_y": self.abstand_y,
            "anzahl_y": self.anzahl_y,
            "alpha_min": self.alpha_min, "alpha_max": self.alpha_max,
        }

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


#: Wahl der Tragrichtung einer Schnittgroessenkombination.
BEIDE_RICHTUNGEN = "beide"


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
class HaeufigEintrag:
    """
    Eine Schnittgroessenkombination unter haeufiger Einwirkung.

    Wie :class:`KombinationEintrag`, aber ohne Querkraft: begrenzt wird die
    Stahlspannung, und dafuer zaehlen Moment und Normalkraft.
    """

    name: str
    M_Ed: float = 0.0
    N_Ed: float = 0.0
    richtung: str = BEIDE_RICHTUNGEN

    def gilt_fuer(self, richtung: Richtung) -> bool:
        return self.richtung in (BEIDE_RICHTUNGEN, richtung.value)

    def als_dict(self) -> dict:
        return {"name": self.name, "M_Ed": self.M_Ed, "N_Ed": self.N_Ed,
                "richtung": self.richtung}

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "HaeufigEintrag":
        return cls(
            name=_pflichtfeld(d, "name", "Ein häufiger Lastfall"),
            M_Ed=_zahl(d, "M_Ed", 0.0),
            N_Ed=_zahl(d, "N_Ed", 0.0),
            richtung=str(d.get("richtung") or BEIDE_RICHTUNGEN),
        )


@dataclass
class KombinationEintrag:
    """Eine zu pruefende Schnittgroessenkombination."""

    name: str
    M_Ed: float = 0.0
    N_Ed: float = 0.0
    V_Ed: float = 0.0
    """Querkraft in kN/m -- für den Querkraftnachweis."""

    art: str = Erfuellungsart.AUTOMATISCH.value
    richtung: str = BEIDE_RICHTUNGEN
    """``x``, ``y`` oder ``beide``.

    In der Regel gehoert eine Schnittgroesse zu einer Tragrichtung -- M_Ed,x
    und M_Ed,y sind verschiedene Zahlen. ``beide`` prueft dieselben Werte in
    beiden Richtungen und ist die Vorgabe fuer Beschreibungen aus der Zeit vor
    dieser Wahlmoeglichkeit, damit dort kein Nachweis stillschweigend wegfaellt.
    """

    def gilt_fuer(self, richtung: Richtung) -> bool:
        return self.richtung in (BEIDE_RICHTUNGEN, richtung.value)

    def als_dict(self) -> dict:
        return {"name": self.name, "M_Ed": self.M_Ed, "N_Ed": self.N_Ed,
                "V_Ed": self.V_Ed, "art": self.art, "richtung": self.richtung}

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "KombinationEintrag":
        return cls(
            name=_pflichtfeld(d, "name", "Eine Einwirkung"),
            M_Ed=_zahl(d, "M_Ed", 0.0),
            N_Ed=_zahl(d, "N_Ed", 0.0),
            V_Ed=_zahl(d, "V_Ed", 0.0),
            art=str(d.get("art") or Erfuellungsart.AUTOMATISCH.value),
            richtung=str(d.get("richtung") or BEIDE_RICHTUNGEN),
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
class QuerschnittEintrag:
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

    zwaengung_x: bool = False
    zwaengung_y: bool = False
    """
    Ob in dieser Tragrichtung mit einer Normalkraft-Zwaengung zu rechnen ist.

    Vorgabe aus: eine Zwaengung ist eine Annahme ueber das Tragwerk, keine
    Eigenschaft der Platte. Wer sie braucht, schaltet sie ein.
    """

    zwaengung_begrenzt: bool = False
    """Ob die Zwaengung auf 500 mm Plattendicke begrenzt angesetzt wird."""

    haeufige: List[HaeufigEintrag] = field(default_factory=list)
    """Eigene haeufige Lastfaelle; leer, solange die 70-%-Regel gilt."""

    haeufige_aus_tragsicherheit: bool = True
    """
    Ob die haeufigen Lastfaelle aus den Tragsicherheitsfaellen abgeleitet
    werden -- mit :data:`HAEUFIG_ANTEIL`. Der uebliche Fall, darum die Vorgabe.
    """

    duktilitaet: List[bool] = field(
        default_factory=lambda: list(DUKTILITAET_VORGABE))
    """
    Je Lage, ob der Duktilitaetsnachweis gefuehrt wird. Index 0 = 1. Lage.

    Vorgabe sind die beiden aeusseren Lagen: sie tragen das Feld- und das
    Stuetzmoment, und dort entscheidet sich, ob der Querschnitt sein Versagen
    ankuendigt.
    """

    lagen: List[LageEintrag] = field(default_factory=list)
    """Genau vier, Index 0 = 1. Lage (unterste)."""

    richtung_lage1: str = "x"
    """Richtung der 1. Lage; die 2. bekommt die Gegenrichtung."""

    richtung_lage4: str = "x"
    """Richtung der 4. Lage; die 3. bekommt die Gegenrichtung."""

    kombinationen: List[KombinationEintrag] = field(default_factory=list)

    def __post_init__(self) -> None:
        while len(self.lagen) < LAGENZAHL:
            self.lagen.append(LageEintrag())
        del self.lagen[LAGENZAHL:]
        self.duktilitaet = _duktilitaet_aus(self.duktilitaet)

    def richtung_von(self, nummer: int) -> Richtung:
        """Richtung der Lage 1..4 -- die Paare (1,2) und (3,4) sind gekoppelt."""
        eins = Richtung(self.richtung_lage1)
        vier = Richtung(self.richtung_lage4)
        return {1: eins, 2: eins.gegenrichtung, 3: vier.gegenrichtung, 4: vier}[nummer]

    def als_dict(self) -> dict:
        return {
            "kennung": self.kennung, "name": self.name, "beton": self.beton,
            "h": self.h, "b": self.b,
            "ueberdeckung_unten": self.ueberdeckung_unten,
            "ueberdeckung_oben": self.ueberdeckung_oben,
            "d_max": self.d_max,
            "einlagenhoehe": self.einlagenhoehe,
            "k_c": self.k_c,
            "querkraftbewehrung": self.querkraftbewehrung.als_dict(),
            "duktilitaet": list(self.duktilitaet),
            "rissanforderung": self.rissanforderung,
            "zwaengung_x": self.zwaengung_x,
            "zwaengung_y": self.zwaengung_y,
            "zwaengung_begrenzt": self.zwaengung_begrenzt,
            "haeufige_aus_tragsicherheit": self.haeufige_aus_tragsicherheit,
            "haeufige": [h.als_dict() for h in self.haeufige],
            "richtung_lage1": self.richtung_lage1,
            "richtung_lage4": self.richtung_lage4,
            "lagen": [l.als_dict() for l in self.lagen],
            "kombinationen": [k.als_dict() for k in self.kombinationen],
        }

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
            duktilitaet=_duktilitaet_aus(d.get("duktilitaet")),
            rissanforderung=_rissanforderung_aus(d.get("rissanforderung")),
            zwaengung_x=bool(d.get("zwaengung_x", False)),
            zwaengung_y=bool(d.get("zwaengung_y", False)),
            zwaengung_begrenzt=bool(d.get("zwaengung_begrenzt", False)),
            haeufige_aus_tragsicherheit=bool(
                d.get("haeufige_aus_tragsicherheit", True)),
            haeufige=[HaeufigEintrag.aus_dict(x) for x in (d.get("haeufige") or [])],
            richtung_lage1=str(d.get("richtung_lage1") or "x"),
            richtung_lage4=str(d.get("richtung_lage4") or "x"),
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
    """Schluessel ist ``<querschnitt>.<richtung>``, weil je Richtung geprueft wird."""

    querkraft: Dict[str, Querkraft] = field(default_factory=dict)
    duktilitaet: Dict[str, Duktilitaet] = field(default_factory=dict)
    """Schluessel ist die Querschnittskennung -- ein Nachweis je Platte."""

    fehlende: Dict[str, FehlendeBewehrung] = field(default_factory=dict)
    """
    Je Richtung ohne Bewehrung, fuer die dennoch Einwirkungen angegeben sind.

    Sie rechnen nichts; sie sorgen dafuer, dass in der Zusammenfassung eine
    Zeile mit Erfuellungsgrad null steht statt gar nichts.
    """

    warnungen: List[str] = field(default_factory=list)

    def alle_nachweisziele(self) -> List[str]:
        return ([d.id for n in self.nachweise.values() for d in n.d_ausnutzung.values()]
                + [d.id for q in self.querkraft.values() for d in q.d_grad.values()]
                + [d.id for k in self.duktilitaet.values()
                   for d in k.d_ausnutzung.values()]
                + [d.id for f in self.fehlende.values()
                   for d in f.d_ausnutzung.values()])

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
class Projekt:
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

    # -- Aufbau -------------------------------------------------------------

    def aufbauen(self) -> Aufbau:
        """
        Baut aus der Beschreibung ein vollstaendiges Rechenwerk.

        Wirft :class:`ProjektFehler`, wenn die Beschreibung nicht stimmig ist --
        etwa wenn ein Querschnitt auf ein geloeschtes Material verweist.
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

            # Die Duktilitaet haengt an der Bewehrung, nicht an den
            # Schnittgroessen -- sie laeuft auch ohne Einwirkung.
            gewaehlte_lagen = [i + 1 for i, an in enumerate(eintrag.duktilitaet) if an]
            if gewaehlte_lagen:
                duktilitaet = Duktilitaet(querschnitt, gewaehlte_lagen)
                werk.registriere(duktilitaet)
                aufbau.duktilitaet[eintrag.kennung] = duktilitaet

            if not eintrag.kombinationen:
                aufbau.warnungen.append(
                    f"Platte '{eintrag.name}': keine Schnittgrössen angegeben, "
                    f"also kein Nachweis möglich.")
                continue

            bewehrt = set(querschnitt.richtungen_mit_bewehrung)
            for richtung in Richtung:
                passend = [k for k in eintrag.kombinationen if k.gilt_fuer(richtung)]
                if not passend:
                    # Keine Kombination fuer diese Richtung ist eine Entscheidung
                    # des Benutzers, kein Mangel -- also auch keine Warnung.
                    continue
                if richtung not in bewehrt:
                    # Ohne Bewehrung laesst sich hier nichts aufstellen. Der
                    # Nachweis entfiel frueher stillschweigend; wer eine
                    # Einwirkung angegeben hatte, fand sie nirgends wieder.
                    fehlend = FehlendeBewehrung(
                        querschnitt, richtung, self._ausgefallene(passend, richtung))
                    werk.registriere(fehlend)
                    aufbau.fehlende[f"{eintrag.kennung}.{richtung.value}"] = fehlend
                    continue
                nachweis = BiegungNormalkraft(
                    querschnitt, [self._kombination(k) for k in passend], richtung)
                werk.registriere(nachweis)
                aufbau.nachweise[f"{eintrag.kennung}.{richtung.value}"] = nachweis

                mit_querkraft = [k for k in passend if k.V_Ed]
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
                    aufbau.querkraft[f"{eintrag.kennung}.{richtung.value}"] = querkraft

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
            querkraftbewehrung=(buegel.als_bewehrung(buegelstahl)
                                if buegel.vorhanden else None),
            praefix=f"querschnitt.{eintrag.kennung}",
        )

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
                art="M-N", fall=k.name,
                symbol=f"M_{{Rd,{r}}}",
                einwirkung_symbol=f"M_{{Ed,{r}}}",
                einwirkung=Groesse(k.M_Ed, KNM), einheit=KNM)
            for k in kombinationen
        ] + [
            Ausgefallen(
                art="V", fall=k.name,
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

    def als_dict(self) -> dict:
        return {
            "name": self.name,
            "materialien": [m.als_dict() for m in self.materialien],
            "querschnitte": [q.als_dict() for q in self.querschnitte],
        }

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
                # 1. Lage in x (Haupttragrichtung unten), 2. Lage damit in y;
                # 4. Lage in x, 3. Lage in y.
                richtung_lage1="x", richtung_lage4="x",
                lagen=[
                    lage(18.0, zulage=12.0),   # 1. Lage x, mit Zulage
                    lage(16.0),                # 2. Lage y
                    lage(12.0),                # 3. Lage y
                    lage(12.0),                # 4. Lage x
                ],
                # Dieselbe Kombination wird in beiden Tragrichtungen geprüft.
                # Die Werte sind so gewählt, dass beide Richtungen aufgehen --
                # das Beispiel soll grün starten.
                kombinationen=[
                    KombinationEintrag(name="Feld", M_Ed=100.0, N_Ed=0.0),
                    KombinationEintrag(name="Feld mit Druck", M_Ed=100.0, N_Ed=-300.0),
                    KombinationEintrag(name="Stütze", M_Ed=-50.0, N_Ed=0.0),
                ])],
        )
