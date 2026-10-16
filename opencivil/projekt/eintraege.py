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
    ProjektFehler, kriechzahl_aus, nur_x, pflichtfeld, sorten, vorgabe, zahl,
)
from opencivil.nachweis.querschnittsloeser import Werkstoffsatz
from opencivil.nachweis.rechenwahl import (
    ERSATZ_ALTER_WAHL, FASERARTEN, RECHENARTEN, SPANNUNGSARTEN, Rechenart, Rechenwahl,
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


    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "QuerkraftbewehrungEintrag":
        def wahl(name: str) -> Optional[float]:
            wert = d.get(name)
            return None if wert in (None, "") else float(wert)

        abstand_x = wahl("abstand_x")
        abstand_y, anzahl_y = wahl("abstand_y"), wahl("anzahl_y")
        # Wie bei den Lagen: steht keines von beiden da, gilt die Teilung.
        if abstand_y is None and anzahl_y is None:
            abstand_y = cls.abstand_y
        return cls(
            durchmesser=zahl(d, "durchmesser", cls.durchmesser),
            stahl=str(d.get("stahl", cls.stahl)),
            # Nur was fehlt, bekommt die Vorgabe. Eine Null bleibt eine Null --
            # pruefen() meldet sie; frueher wurde sie still zu 200 mm.
            abstand_x=cls.abstand_x if abstand_x is None else abstand_x,
            abstand_y=abstand_y,
            anzahl_y=anzahl_y,
            alpha_min=int(zahl(d, "alpha_min", float(cls.alpha_min))),
            alpha_max=int(zahl(d, "alpha_max", float(cls.alpha_max))),
        )

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

    zugseite: str = "unten"
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

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "VerformungsfallEintrag":
        return cls(
            name=pflichtfeld(d, "name", "Ein Verformungsfall"),
            w=zahl(d, "w", cls.w),
            laenge=zahl(d, "laenge", cls.laenge),
            zugseite=str(d.get("zugseite") or cls.zugseite),
            aktiv=bool(d.get("aktiv", cls.aktiv)),
        )


@dataclass
class VerformungEintrag(Beschreibung):
    """
    Der Verformungsnachweis einer Platte: die Kriechzahl seines
    Vergroesserungsfaktors und die Faelle.

    phi gilt fuer die Platte und nicht je Fall -- der Faktor wird je Seite
    einmal gerechnet (:mod:`opencivil.nachweis.verformung`).
    """

    kriechzahl: float = VERFORMUNG_KRIECHZAHL
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
        if self.kriechzahl < 0.0:
            raise ProjektFehler(f"{wo}, Verformung: die Kriechzahl kann nicht negativ sein.")
        eindeutig(self.faelle, bauteil, "Verformungsfall")
        # Verschiedene Namen koennen dieselbe Wert-ID ergeben -- wie bei den
        # Gebrauchslisten.
        kennungen: Dict[str, str] = {}
        for f in self.faelle:
            if f.zugseite not in ZUGSEITEN:
                raise ProjektFehler(
                    f"{wo}, Verformungsfall '{f.name}': unbekannte Zugseite "
                    f"'{f.zugseite}'. Möglich sind: {', '.join(ZUGSEITEN)}.")
            frueher = kennungen.setdefault(kennung_aus(f.name), f.name)
            if frueher != f.name:
                raise ProjektFehler(
                    f"{wo}: die Verformungsfälle '{frueher}' und '{f.name}' "
                    f"unterscheiden sich nur in Satz- oder Leerzeichen. Im Bericht "
                    f"fielen sie auf denselben Eintrag -- bitte einen davon anders "
                    f"benennen.")

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any], *,
                 kriechzahl_alt: float = VERFORMUNG_KRIECHZAHL) -> "VerformungEintrag":
        """``kriechzahl_alt``: das phi, das bis 2026-10-16 an der Platte stand."""
        return cls(
            kriechzahl=kriechzahl_aus(d, "kriechzahl", alt=kriechzahl_alt,
                                      wo="Verformung"),
            faelle=[VerformungsfallEintrag.aus_dict(x) for x in (d.get("faelle") or [])],
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
    der einen oder der anderen Seite -- aus Schnittgroessen, aus Dehnungen,
    als Momenten-Kruemmungs- oder als Normalkraft-Dehnungs-Linie.

    Womit gerechnet wird, waehlt jede Analyse fuer sich: die Kriechzahl, den
    Wertesatz und die Rechenart (:class:`~opencivil.nachweis.rechenwahl.Rechenwahl`).
    In Dateien von vor 2026-10-09 fehlt die Kriechzahl oder steht leer --
    sie hiess dort «die der Platte», und das bleibt sie beim Lesen
    (``kriechzahl_alt``). Die Rechenart hiess dort ``betongesetz``.
    """

    name: str
    art: str = "schnittgroessen"
    """``schnittgroessen``, ``dehnungen``, ``moment_kruemmung`` oder
    ``normalkraft_dehnung`` -- siehe :class:`~opencivil.spannungsanalyse.Analyseart`."""

    richtung: str = "x"
    """Welche Bewehrung zaehlt. Hier keine Wahl ``beide``: ein Bild zeigt
    einen Querschnitt, und der liegt in einer Richtung."""

    N_Ed: float = 0.0
    """in kN, Zug positiv -- fuer ``schnittgroessen`` und ``moment_kruemmung``."""

    M_Ed: float = 0.0
    """in kNm -- fuer ``schnittgroessen`` und ``normalkraft_dehnung``."""

    eps_oben: float = -1.0
    eps_unten: float = 2.0
    """Randdehnungen in Promille -- nur fuer ``dehnungen``."""

    kriechzahl: float = 0.0
    """Die Kriechzahl φ dieser Analyse."""

    werkstoffsatz: str = WERKSTOFFSAETZE[0]
    """``bemessung`` (f_cd, f_yd) oder ``charakteristisch`` (f_ck, f_yk)."""

    rechenart: str = Rechenart.PARABEL.value
    """``block`` oder ``parabel`` -- siehe
    :class:`~opencivil.nachweis.rechenwahl.Rechenart`. Die Handrechnung gibt
    es hier nicht (:data:`~opencivil.nachweis.rechenwahl.FASERARTEN`); eine
    Datei von vor 2026-10-12, die sie noch waehlt, liest sich als ``block``."""

    aktiv: bool = True

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any], *,
                 kriechzahl_alt: float = 0.0) -> "SpannungsfallEintrag":
        """``kriechzahl_alt`` gilt, wo die Kriechzahl fehlt -- siehe Klasse."""
        name = pflichtfeld(d, "name", "Eine Spannungsanalyse")
        wo = f"Spannung-Dehnung-Analyse '{name}'"

        def gewaehlt(feld: str, vorgabe: str, moeglich, roh: Any = None) -> str:
            wert = str((roh if roh is not None else d.get(feld)) or vorgabe)
            if wert not in moeglich:
                raise ProjektFehler(f"{wo}: «{wert}» gibt es als {feld} nicht. "
                                    f"Möglich sind: {', '.join(moeglich)}.")
            return wert

        return cls(
            name=name,
            art=gewaehlt("art", cls.art, tuple(a.value for a in Analyseart)),
            richtung=str(d.get("richtung") or cls.richtung),
            N_Ed=zahl(d, "N_Ed", cls.N_Ed),
            M_Ed=zahl(d, "M_Ed", cls.M_Ed),
            eps_oben=zahl(d, "eps_oben", cls.eps_oben),
            eps_unten=zahl(d, "eps_unten", cls.eps_unten),
            kriechzahl=kriechzahl_aus(d, "kriechzahl", alt=kriechzahl_alt, wo=wo),
            werkstoffsatz=gewaehlt("werkstoffsatz", cls.werkstoffsatz, WERKSTOFFSAETZE),
            rechenart=gewaehlt("rechenart", cls.rechenart,
                               tuple(a.value for a in FASERARTEN),
                               roh=_ersetzt(d.get("rechenart") or d.get("betongesetz"),
                                            FASERARTEN)),
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
    gehoert dem Verformungsnachweis (:class:`VerformungEintrag`). In einer
    Datei von vor 2026-10-09 fehlt die Wahl -- dann gilt, was damals fest
    galt: die Rechenart und der Wertesatz des Kapitels (``vorgabe``) und das
    phi, das damals an der Platte stand (``kriechzahl_alt``).
    """

    kriechzahl: float = 0.0
    werkstoffsatz: str = WERKSTOFFSAETZE[0]
    rechenart: str = Rechenart.HANDRECHNUNG.value

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
        """Was es nicht gibt, meldet sich -- ``arten`` sagt, welche Rechenarten gelten."""
        if self.kriechzahl < 0.0:
            raise ProjektFehler(f"{wo}: die Kriechzahl kann nicht negativ sein.")
        if self.werkstoffsatz not in WERKSTOFFSAETZE:
            raise ProjektFehler(f"{wo}: «{self.werkstoffsatz}» gibt es als Werte nicht. "
                                f"Möglich sind: {', '.join(WERKSTOFFSAETZE)}.")
        moeglich = [a.value for a in arten]
        if self.rechenart not in moeglich:
            raise ProjektFehler(f"{wo}: die Rechenart «{self.rechenart}» gibt es dort nicht. "
                                f"Möglich sind: {', '.join(moeglich)}.")

    @classmethod
    def aus_dict(cls, d: Optional[Mapping[str, Any]], *,
                 vorgabe: Optional["RechenwahlEintrag"] = None,
                 kriechzahl_alt: Optional[float] = None,
                 wo: str = "Rechenwahl", arten=RECHENARTEN) -> "RechenwahlEintrag":
        """Fehlt ``d`` oder ein Feld darin, gilt ``vorgabe`` -- und fuer phi ``kriechzahl_alt``."""
        vorgabe = vorgabe or cls()
        d = d or {}
        eintrag = cls(
            kriechzahl=kriechzahl_aus(
                d, "kriechzahl", wo=wo,
                alt=vorgabe.kriechzahl if kriechzahl_alt is None else kriechzahl_alt),
            werkstoffsatz=str(d.get("werkstoffsatz") or vorgabe.werkstoffsatz),
            rechenart=_ersetzt(d.get("rechenart") or vorgabe.rechenart, arten),
        )
        eintrag.pruefen(wo, arten)
        return eintrag


def _ersetzt(rechenart: Any, arten) -> Any:
    """
    Die Rechenart, wie sie heute heisst: was eine alte Datei dort waehlt, wo
    es die Wahl nicht mehr gibt, wird zu ihrem Ersatz -- und der, wo es auch
    ihn nicht gibt, zu seinem
    (:data:`~opencivil.nachweis.rechenwahl.ERSATZ_ALTER_WAHL`). Alles andere
    bleibt -- auch Unbekanntes, das die Pruefung danach meldet.
    """
    moeglich = {a.value for a in arten}
    while rechenart is not None and rechenart not in moeglich:
        ersatz = ERSATZ_ALTER_WAHL.get(str(rechenart))
        if ersatz is None:
            break
        rechenart = ersatz
    return rechenart


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
        eintrag = self.FALL(name=name, **werte)
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

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any], *, wort: str, vorgabe: float,
                 kriechzahl_alt: Optional[float] = None) -> "Gebrauchsliste":
        """``kriechzahl_alt``: das phi der Platte, fuer eine Datei ohne Wahl."""
        return cls(
            anteil=zahl(d, "anteil", vorgabe),
            aus_tragsicherheit=bool(d.get("aus_tragsicherheit", cls.aus_tragsicherheit)),
            faelle=[cls.FALL.aus_dict(x, wort) for x in (d.get("faelle") or [])],
            wahl=RechenwahlEintrag.aus_dict(
                d.get("wahl"), vorgabe=RechenwahlEintrag.gebrauch(),
                kriechzahl_alt=kriechzahl_alt, arten=cls.ARTEN,
                wo=f"Rechenwahl der {wort}n Lastfälle"),
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


