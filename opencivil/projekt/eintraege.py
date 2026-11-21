"""
opencivil/projekt/eintraege.py -- die Teile einer Projektbeschreibung.

VERANTWORTUNG:
Material, Lastfaelle, Rechenwahlen und was Platte und gezeichneter
Querschnitt gleich angeben -- jedes als Datenklasse, die sich als JSON
speichern und wieder einlesen laesst. Gelesen und geprueft wird jeder Eintrag
ueber seine Felder: was eines annehmen darf, steht an ihm
(:mod:`opencivil.projekt.lesen`).

Was nur die Platte hat -- Posten, Lagen, Buegel --, steht bei ihr in
:mod:`opencivil.projekt.platte`; bis 2026-11-20 stand es hier. Das ganze
Projekt steht in :mod:`opencivil.projekt.projekt`.
"""

from __future__ import annotations

import functools
import inspect
from dataclasses import KW_ONLY, MISSING, asdict, dataclass, field, fields
from typing import Any, ClassVar, Dict, Iterable, List, Mapping, Optional

from opencivil.core.einheiten import (
    GRAD, KN, KN_PRO_M, KNM, M, MM, PROMILLE, PROZENT,
)
from opencivil.material.arten import MATERIALARTEN
from opencivil.material.basis import Baustoff, Baustoffart
from opencivil.nachweis.biegung_normalkraft import Erfuellungsart
from opencivil.nachweis.duktilitaet import BEIWERT as X_D_BEIWERT, HOECHSTENS as X_D_HOECHSTENS
from opencivil.querschnitt.platte import ALPHA_MAX, ALPHA_MIN, K_C, Richtung
from opencivil.projekt.fallnamen import Fallnamen
from opencivil.projekt.lesen import (
    ProjektFehler, als_groesse, bereich, einer_von, je_material, lesen, ort, teil,
    unbekanntes_feld, vorgabe_je_material, wahl_aus_text,
)
from opencivil.querschnitt.gesetzwahl import Rechenart, Rechenwahl, Werkstoffsatz, Wertesaetze
from opencivil.nachweis.rechenwahl import (
    FASERARTEN, RECHENARTEN, SPANNUNGSARTEN, VERFORMUNGSARTEN,
)
from opencivil.nachweis.rissanforderung import Rissanforderung
from opencivil.nachweis.verformung import KRIECHZAHL as VERFORMUNG_KRIECHZAHL
from opencivil.querschnitt.zugseite import UM_Y, Zugseite
from opencivil.spannungsanalyse import Analyseart


# ===========================================================================
# Material
# ===========================================================================


@functools.lru_cache(maxsize=None)
def _feldnamen(klasse: type) -> frozenset:
    """Die Namen der Felder einer Beschreibungsklasse -- je Klasse einmal gesucht."""
    return frozenset(f.name for f in fields(klasse))


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
    die Oberflaeche: «Platte 'Decke'». ``IM_ORT`` nennt ein Element einer
    Liste mit dem Wort der Maske: mit Namen «Wand 'W1'», ohne mit seiner
    Nummer, «Lage 2».

    Ein Wahlfeld haelt das Mitglied seiner Wahl; wer Text zuweist -- die
    Datei, der Konstruktor, die Fassade --, bekommt hier das Mitglied
    (:func:`~opencivil.projekt.lesen.wahl_aus_text`).

    Was ueber mehrere Felder gilt, steht in :meth:`regeln` -- geprueft vor
    dem Rechnen, nach den Bereichen der Felder
    (:func:`~opencivil.projekt.lesen.inhalt_pruefen`).
    """

    ERSTE_MATERIALIEN: ClassVar[Mapping[str, str]] = {}
    """
    Was ein neuer Eintrag vom Projekt nimmt (:meth:`frisch`): je Feld, als
    Pfad wie ``stabmaterialien/0/stoff``, die Art des Materials, von der er
    das erste bekommt. «+» in der Oberflaeche liest es aus dem Katalog,
    damit die Regel an einer Stelle steht. Ohne eigene keines.
    """

    STAMM: ClassVar[str] = ""
    """
    Wie ein neuer Eintrag einer App heisst, vor seiner Nummer: «Platte» in
    «Platte 1» (:func:`~opencivil.projekt.projekt.naechster_name`). Nur die
    Klassen der Apps haben einen (:data:`~opencivil.projekt.projekt.APPLISTEN`),
    und das Projekt: «Projekt 2». Die Oberflaeche liest ihn aus dem Katalog.
    """

    def __setattr__(self, name: str, wert: Any) -> None:
        # Nur Felder (2026-10-25): eine Zuweisung an einen Namen, den es nicht
        # gibt, legte still ein neues Attribut an -- ein Tippfehler im
        # Baukasten blieb ohne Wirkung, und drei Tests setzten Felder, die es
        # nicht mehr gab, und prüften nichts mehr.
        if name not in _feldnamen(type(self)):
            raise unbekanntes_feld(type(self).__name__, name, _feldnamen(type(self)))
        super().__setattr__(name, wahl_aus_text(type(self), name, wert))

    def regeln(self, wo: str) -> None:
        """Die Regeln ueber mehrere Felder -- ohne eigene keine. ``wo`` nennt den Eintrag."""

    def fallnamen(self) -> List[Fallnamen]:
        """
        Die Listen von Faellen, deren Namen sich unterscheiden muessen
        (:mod:`~opencivil.projekt.fallnamen`) -- ohne eigene keine. Geprueft
        vor den Regeln (:func:`~opencivil.projekt.lesen.inhalt_pruefen`) und
        vom Namensfeld, bevor es einen Namen uebernimmt.
        """
        return []

    def si(self, feld: str) -> float:
        """
        Die Zahl eines Feldes in SI, mit der Einheit seines Bereichs
        (:func:`~opencivil.projekt.lesen.als_groesse`) -- der, in der die
        Maske sie zeigt. Wer rechnet, nimmt sie so, statt die Einheit noch
        einmal anzuschreiben.
        """
        return als_groesse(self, feld).si

    def als_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def frisch(cls, materialien: Iterable[Any] = ()) -> Any:
        """
        Ein frischer Eintrag dieser Klasse, wie die Oberflaeche ihn anlegt:
        ueber ``neu``, wo die Klasse eines hat -- eine Platte mit ihren
        Lagen, ein Grundbruch mit einer Kombination --, sonst mit ihren
        Vorgaben. Aus ``materialien`` bekommt jedes Feld in
        :attr:`ERSTE_MATERIALIEN` das erste seiner Art. Kennung und Name
        bleiben leer: sie setzt, wer anlegt.
        """
        neu = getattr(cls, "neu", None)
        if neu is not None:
            pflicht = [n for n, p in inspect.signature(neu).parameters.items()
                       if p.default is inspect.Parameter.empty]
            eintrag = neu(**{n: "" for n in pflicht})
        else:
            eintrag = cls(**{f.name: "" for f in fields(cls)
                             if f.init and f.default is MISSING and f.default_factory is MISSING})
        vorhanden = list(materialien)
        for pfad, art in cls.ERSTE_MATERIALIEN.items():
            *weg, feld = pfad.split("/")
            ziel = eintrag
            for schritt in weg:
                ziel = ziel[int(schritt)] if isinstance(ziel, list) else getattr(ziel, schritt)
            setattr(ziel, feld, next((m.kennung for m in vorhanden if m.art == art), ""))
        return eintrag

    @classmethod
    def aus_dict(cls, roh: Mapping[str, Any], wo: Optional[str] = None) -> Any:
        """Ein Eintrag aus der Datei -- gelesen und geprueft, siehe :mod:`opencivil.projekt.lesen`."""
        return lesen(cls, roh, wo or ort(cls, roh))


@dataclass
class BauteilEintrag(Beschreibung):
    """
    Was jedes Bauteil eines Projekts sagt -- eine Platte, eine Analyse, ein
    Fundament --: worauf es zeigt. Danach fragt das Projekt, bevor etwas
    geloescht wird (:meth:`~opencivil.projekt.projekt.Projekt.verweise`).
    Ohne eigene Angabe zeigt es auf nichts.

    Bis 2026-11-10 stand dieser Vertrag in keiner Klasse: jede Art schrieb
    beide Methoden selbst, viermal ``return []``, und eine neue Art, die sie
    vergass, fiel erst beim Loeschen eines Materials auf.
    """

    _: KW_ONLY
    vergeben: Dict[str, int] = field(default_factory=dict)
    """
    Je Vorsilbe die hoechste Nummer, die das Bauteil je vergeben hat -- an
    seine Knoten, Linien, Lastfaelle: eine Kennung kommt nie wieder
    (:func:`~opencivil.projekt.netz.neue_kennung`).
    """

    def materialien(self) -> List[str]:
        """Die Kennungen der Materialien, auf die das Bauteil zeigt."""
        return []

    def bezuege(self) -> List[str]:
        """Die Kennungen der Bauteile, deren Querschnitt es nimmt."""
        return []


@dataclass
class MaterialEintrag(Beschreibung):
    """
    Ein Baustoff, wie ihn die Oberflaeche beschreibt: eine Normsorte nach SIA,
    die bleibt, wie sie ist, oder ein eigenes Material mit einer Sorte als
    Vorlage.
    """

    BEZEICHNUNG = "Material"

    kennung: str
    art: Baustoffart

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

    def sorte_pruefen(self) -> None:
        """
        Die Sorte -- schon beim Oeffnen: aus ihr kommen die Kennwerte, ohne
        sie laesst sich das Material nicht einmal zeigen. Die Materialart
        prueft ihr Feld.
        """
        sorten = MATERIALARTEN[self.art].sorten
        if self.sorte not in sorten:
            raise ProjektFehler(
                f"Unbekannte Sorte '{self.sorte}' für {self.art}. "
                f"Verfügbar: {', '.join(sorten)}.")

    def regeln(self, wo: str) -> None:
        """
        Was eine Normsorte bleibt und wie ein eigenes Material heissen darf --
        vor dem Rechnen, nicht beim Oeffnen: ein abgelegtes Material mit
        falschem Namen soll sich oeffnen und umbenennen lassen.
        """
        if self.ist_normsorte:
            if self.abweichungen or self.ueberschreibungen:
                raise ProjektFehler(
                    f"eine Normsorte darf keine abweichenden Kennwerte haben. "
                    f"Bitte zuerst zu einem eigenen Material machen.", wo=wo)
            if self.name and self.name != self.sorte:
                raise ProjektFehler(
                    f"eine unveränderte Normsorte muss '{self.sorte}' heissen.", wo=wo)
        elif self.anzeigename in MATERIALARTEN[self.art].sorten:
            # Sonst stuende eine abgeaenderte Festigkeit unter einer
            # Normbezeichnung im Bericht.
            raise ProjektFehler(
                f"ein eigenes Material darf nicht wie die Normsorte "
                f"'{self.anzeigename}' heissen.", wo=wo)


# ===========================================================================
# Felder, die Platte und gezeichneter Querschnitt teilen
# ===========================================================================


def kleinste_neigung() -> Any:
    """
    α_min, die kleinste Neigung der Druckdiagonalen -- und nicht ueber α_max:
    bei den Buegeln der Platte wie am gezeichneten Querschnitt. Eine
    groessere weist schon das Feld ab (:attr:`~opencivil.projekt.lesen.Bereich.bis_feld`).
    """
    return _neigung(ALPHA_MIN, "α_min", bis_feld="alpha_max")


def groesste_neigung() -> Any:
    """α_max, die groesste -- eine unter α_min weist ihr Feld ebenso ab."""
    return _neigung(ALPHA_MAX, "α_max")


def _neigung(vorgabe: int, heisst: str, bis_feld: Optional[str] = None) -> Any:
    """Eine Grenze der Druckfeldneigung -- in ganzen Grad, 1° bis 89°."""
    return bereich(vorgabe, heisst=heisst, einheit=GRAD, ab=1, bis=89, bis_feld=bis_feld)


def druckfeld() -> Any:
    """Die Abminderung k_c der Druckdiagonalen -- eine Festigkeit mal k_c, also groesser als null."""
    return bereich(K_C, heisst="k_c", ueber=0.0)


def x_d_grenze() -> Any:
    """
    Der Beiwert k der Grenze ``x/d <= k * 435 N/mm^2 / f_yd`` im
    Duktilitaetsnachweis -- Vorgabe und Hoechstwert stehen beim Nachweis
    (``duktilitaet.BEIWERT``, ``duktilitaet.HOECHSTENS``).
    """
    return bereich(X_D_BEIWERT, heisst="k der Grenze x/d",
                   ueber=0.0, bis=X_D_HOECHSTENS)


@dataclass
class KnickEintrag(Beschreibung):
    """
    Ein Knicknachweis: Druckkraft, Moment 1. Ordnung, Laenge, Knicklaenge.

    Nur in x-Richtung -- eine Knicklaenge gehoert zu einer Tragrichtung, und
    in y waere die Breite der Platte die Laenge.
    """

    IM_ORT = "Knicknachweis"

    name: str
    N_Ed: float = bereich(0.0, heisst="Normalkraft N_Ed", einheit=KN)
    """Druck negativ."""

    M_Ed_1: float = bereich(0.0, heisst="Moment 1. Ordnung M_Ed,1", einheit=KNM)
    laenge: float = bereich(3.0, heisst="Höhe des Druckglieds", einheit=M, ueber=0.0)
    """
    Hoehe des Druckglieds in m, bei mehreren uebereinander ihre ganze Hoehe
    (SIA 262:2025, 4.1.3.2.3) -- sie bestimmt die Schiefstellung. Bis
    2026-11-14 hiess sie Systemlaenge; bis 2026-10-16 rechnete eine Laenge von
    null und hiess «erfuellt».
    """

    knicklaenge: float = bereich(3.0, heisst="Knicklänge", einheit=M, ueber=0.0)
    """Knicklaenge in m."""

    aktiv: bool = True
    """Ob der Fall gerechnet wird. Ausgeschaltet bleibt er stehen -- eine
    geloeschte Zeile muesste man neu eintippen, um sie wieder anzusehen."""


@dataclass
class VerformungsfallEintrag(Beschreibung):
    """
    Ein Verformungsfall: die Durchbiegung, mit der Steifigkeit E_cm
    ermittelt, ihre Spannweite und die Seite, die er zieht.

    Wie ein Knickfall nur in x-Richtung.
    """

    IM_ORT = "Verformungsfall"

    name: str
    w: float = bereich(0.0, heisst="Durchbiegung w", einheit=MM, ab=0.0)
    """Durchbiegung in mm, mit E_cm ermittelt -- ein Betrag."""

    laenge: float = bereich(5.0, heisst="Spannweite L", einheit=M, ueber=0.0)
    """Spannweite L in m -- der Grenzwert ist L/350."""

    zugseite: Zugseite = einer_von(UM_Y, Zugseite.UNTEN)
    """``unten`` im Feld, ``oben`` am Kragarm -- welches rho gilt."""

    aktiv: bool = True
    """Ob der Fall gerechnet wird. Ausgeschaltet bleibt er stehen."""


@dataclass
class VerformungEintrag(Beschreibung):
    """
    Der Verformungsnachweis einer Platte: die Kriechzahl seines
    Vergroesserungsfaktors und die Faelle.

    phi gilt fuer die Platte und nicht je Fall -- der Faktor wird je Seite
    einmal gerechnet (:mod:`opencivil.nachweis.verformung`).
    """

    kriechzahl: float = bereich(VERFORMUNG_KRIECHZAHL, heisst="Kriechzahl φ", ab=0.0)
    """phi im Vergroesserungsfaktor omega_w, Vorgabe 2."""

    faelle: List[VerformungsfallEintrag] = field(default_factory=list)

    def fall(self, name: str, *, w: float, laenge: float,
             zugseite: Zugseite = VerformungsfallEintrag.zugseite) -> VerformungsfallEintrag:
        """Einen Fall anfuegen -- w in mm, die Spannweite in m."""
        eintrag = VerformungsfallEintrag(name=name, w=w, laenge=laenge, zugseite=zugseite)
        self.faelle.append(eintrag)
        return eintrag



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


class JeMaterial:
    """
    Was die Werte je Material waehlt (Benutzer, 2026-11-20): im Feld
    ``werkstoffsaetze`` (:func:`~opencivil.projekt.lesen.je_material`) je
    Kennung eines Materials sein Wertesatz. Ein Material ohne eigene Wahl
    rechnet mit der Vorgabe des Feldes -- die Stahlspannungen
    charakteristisch, alles andere mit Bemessungswerten. Fuer die Rechnung
    wird daraus je Baustoff des Bauteils sein Satz (:meth:`wertesaetze`).
    Bis dahin waehlte nur die Querschnittsanalyse je Material, jedes andere
    Kapitel einen Satz fuer alle.
    """

    def von(self, feld: str, material: str) -> Any:
        """Die Wahl eines Materials in diesem Feld -- die Vorgabe des Feldes, wenn es keine eigene hat."""
        return getattr(self, feld).get(material, vorgabe_je_material(type(self), feld))

    def wertesaetze(self, stoffe: Mapping[str, Baustoff]) -> Wertesaetze:
        """Je Baustoff eines Bauteils -- ``stoffe`` nach ihrer Kennung im Projekt -- sein Wertesatz."""
        return Wertesaetze.je({b.id: self.von("werkstoffsaetze", kennung)
                               for kennung, b in stoffe.items()},
                              vorgabe_je_material(type(self), "werkstoffsaetze"))


@dataclass
class SpannungsfallEintrag(Beschreibung, JeMaterial):
    """
    Eine Auswertung am Querschnitt -- kein Nachweis.

    Es wird nichts gegen etwas gehalten: kein Erfuellungsgrad, kein Urteil.
    Gefragt wird, was im Querschnitt geschieht, und je nach :attr:`art` von
    der einen oder der anderen Seite -- aus Schnittgroessen, aus Dehnungen,
    als Momenten-Kruemmungs- oder als Normalkraft-Dehnungs-Linie.

    Womit gerechnet wird, waehlt jede Analyse fuer sich: die Kriechzahl, je
    Material den Wertesatz (:class:`JeMaterial`) und die Rechenart
    (:class:`~opencivil.querschnitt.gesetzwahl.Rechenwahl`).
    """

    IM_ORT = "Diagramm"

    name: str
    art: Analyseart = Analyseart.SCHNITTGROESSEN
    """Was gefragt wird -- siehe :class:`~opencivil.spannungsanalyse.Analyseart`."""

    richtung: Richtung = Richtung.X
    """Welche Bewehrung zaehlt. Hier keine Wahl ``beide``: ein Bild zeigt
    einen Querschnitt, und der liegt in einer Richtung."""

    N_Ed: float = bereich(0.0, heisst="N_Ed", einheit=KN)
    """Zug positiv. Welche Frage welches Feld braucht, sagt :attr:`Analyseart.eingaben`."""

    M_Ed: float = bereich(0.0, heisst="M_Ed", einheit=KNM)
    eps_oben: float = bereich(-1.0, heisst="ε oben", einheit=PROMILLE)
    eps_unten: float = bereich(2.0, heisst="ε unten", einheit=PROMILLE)
    """Die Randdehnungen."""

    kriechzahl: float = bereich(0.0, heisst="Kriechzahl φ", ab=0.0)
    """Die Kriechzahl φ dieser Analyse."""

    werkstoffsaetze: Dict[str, Werkstoffsatz] = je_material(Werkstoffsatz.BEMESSUNG)
    """Je Material ``bemessung`` (f_cd, f_yd) oder ``charakteristisch`` (f_ck, f_yk)."""

    rechenart: Rechenart = einer_von(FASERARTEN, Rechenart.PARABEL)
    """``block`` oder ``parabel`` -- siehe
    :class:`~opencivil.querschnitt.gesetzwahl.Rechenart`. Die Handrechnung gibt
    es hier nicht (:data:`~opencivil.nachweis.rechenwahl.FASERARTEN`)."""

    def wahl(self, stoffe: Mapping[str, Baustoff]) -> Rechenwahl:
        """Womit die Analyse an einem Bauteil aus diesen Baustoffen rechnet (:meth:`JeMaterial.wertesaetze`)."""
        return Rechenwahl(kriechzahl=self.kriechzahl, saetze=self.wertesaetze(stoffe),
                          art=self.rechenart)

    aktiv: bool = True


def spannungsfallnamen(faelle: Iterable[SpannungsfallEintrag]) -> Fallnamen:
    """
    Die Namen der Spannung-Dehnung-Analysen, bei der Platte wie am
    gezeichneten Querschnitt -- eine Liste fuer sechs Fenster, darum sagt die
    Meldung, in welchem der andere steht.
    """
    return Fallnamen.aus("spannungsfaelle", "Spannung-Dehnung-Analyse", faelle,
                         ort=lambda f: f", im Fenster «{f.art.beschriftung}»")


@dataclass
class GebrauchsfallEintrag(Beschreibung):
    """
    Eine Schnittgroessenkombination unter Gebrauchslast.

    Wie :class:`KombinationEintrag`, aber ohne Querkraft: begrenzt wird die
    Stahlspannung, und dafuer zaehlen Moment und Normalkraft. Ob der Fall
    haeufig oder quasi-staendig ist, sagt die Liste, in der er steht.
    """

    IM_ORT = "Lastfall"

    name: str
    M_Ed: float = bereich(0.0, heisst="Moment M_Ed", einheit=KNM)
    N_Ed: float = bereich(0.0, heisst="Normalkraft N_Ed", einheit=KN)
    aktiv: bool = True
    """Ob dieser Lastfall gerechnet wird. Ausgeschaltet bleibt er stehen."""


@dataclass
class RechenwahlEintrag(Beschreibung, JeMaterial):
    """
    Womit ein Nachweis-Kapitel rechnet: Kriechzahl, je Material der
    Wertesatz (:class:`JeMaterial`), Rechenart -- siehe
    :class:`~opencivil.querschnitt.gesetzwahl.Rechenwahl`. So steht sie in
    der Tragsicherheit.

    Jedes andere Kapitel hat seine Unterklasse, und welche Rechenarten es
    anbietet, steht an deren Feld: der Leser prueft es wie jede Wahl. Bis
    2026-10-17 prueften fuenf Aufrufer je mit ihrer Liste nach dem Lesen.
    Die Kriechzahl des Vergroesserungsfaktors gehoert dem Verformungsnachweis
    (:class:`VerformungEintrag`).
    """

    kriechzahl: float = bereich(0.0, heisst="Kriechzahl φ", ab=0.0)
    werkstoffsaetze: Dict[str, Werkstoffsatz] = je_material(Werkstoffsatz.BEMESSUNG)
    rechenart: Rechenart = einer_von(RECHENARTEN, Rechenart.HANDRECHNUNG)

    def wahl(self, stoffe: Mapping[str, Baustoff]) -> Rechenwahl:
        """Was der Kern daraus rechnet, an einem Bauteil aus diesen Baustoffen (:meth:`JeMaterial.wertesaetze`)."""
        return Rechenwahl(kriechzahl=self.kriechzahl, saetze=self.wertesaetze(stoffe),
                          art=self.rechenart)


@dataclass
class Gebrauchswahl(RechenwahlEintrag):
    """Die Stahlspannungen: elastisch, mit charakteristischen Werten -- dazu die Rechenarten der Tragsicherheit."""

    werkstoffsaetze: Dict[str, Werkstoffsatz] = je_material(Werkstoffsatz.CHARAKTERISTISCH)
    rechenart: Rechenart = einer_von(SPANNUNGSARTEN, Rechenart.ELASTISCH)


@dataclass
class KnickVerformungswahl(RechenwahlEintrag):
    """Die Ausmitte e_2d beim Knicken: nur praezise ohne Vereinfachung."""

    rechenart: Rechenart = einer_von(VERFORMUNGSARTEN, Rechenart.PARABEL)


@dataclass
class KnickWiderstandswahl(RechenwahlEintrag):
    """
    Der Widerstand beim Knicken: ueber die Fasern, vorgegeben die
    0.85·x-Vereinfachung. Bis 2026-10-12 war es die Handrechnung, die es
    dort nicht mehr gibt; die Vereinfachung kommt ihr am naechsten.
    """

    rechenart: Rechenart = einer_von(FASERARTEN, Rechenart.BLOCK)


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
    darin steht (:attr:`FALL`), welche Rechenarten sie anbietet (der Typ
    ihres Feldes :attr:`wahl`) und wie ihr Bauteil heisst, wo ein Fall ohne
    Bauteil gelesen wird (:attr:`BAUTEIL`).
    """

    FALL = GebrauchsfallEintrag
    BAUTEIL = "Platte"

    anteil: float = bereich(heisst="Anteil aus der Tragsicherheit", einheit=PROZENT,
                            ueber=0.0, bis=100.0)
    """
    Welcher Anteil der Tragsicherheitseinwirkungen abgeleitet wird, in %.

    Null ergaebe Lastfaelle ohne Last -- ein Nachweis, der immer aufgeht und
    nichts sagt. Ueber hundert waere keine Gebrauchslast mehr. Gemeldet
    statt begrenzt: wer 700 statt 70 tippt, soll es erfahren und nicht mit
    100 weiterrechnen.
    """

    aus_tragsicherheit: bool = False
    """
    Ob die abgeleiteten Faelle *gefuehrt* werden.

    Gebildet werden sie immer; ausgeschaltet rechnen sie still mit. Der
    Anteil ist eine bequeme Abschaetzung und keine Norm, darum stehen die
    Faelle nur auf Verlangen in der Tabelle.
    """

    faelle: List[GebrauchsfallEintrag] = field(default_factory=list)
    """Eigene Lastfaelle -- neben den abgeleiteten, nicht statt ihrer."""

    wahl: Gebrauchswahl = teil(Gebrauchswahl, heisst="Rechenwahl")
    """Womit die Stahlspannung gerechnet wird -- Vorgabe elastisch, charakteristisch."""

    def lastfall(self, name: str, **werte: float):
        """Einen eigenen Lastfall anfuegen -- kNm und kN, Zug positiv."""
        eintrag = self.FALL.aus_dict({"name": name, **werte}, f"{self.BAUTEIL}, faelle")
        self.faelle.append(eintrag)
        return eintrag

    def namensliste(self, feld: str, kombinationen: List[Any], wort: str) -> Fallnamen:
        """
        Die Namen dieser Liste (:class:`~opencivil.projekt.fallnamen.Fallnamen`),
        unter ``feld`` im Bauteil. Je Liste fuer sich: die beiden Listen
        landen in getrennten Nachweisen und damit in getrennten ID-Raeumen,
        ein Fall «Dauer» darf in beiden stehen. Schon vergeben sind die aus
        den ``kombinationen`` der Tragsicherheit abgeleiteten: sie tragen den
        Namen ihrer Kombination mit angehaengtem Anteil, und wer einen eigenen
        Fall genau so nennt, traefe denselben Schluessel.
        """
        return Fallnamen.aus(f"{feld}.faelle", f"{wort}r Lastfall", self.faelle, vergeben=[
            (abgeleiteter_fallname(k.name, self.anteil), ", aus der Tragsicherheit abgeleitet")
            for k in kombinationen])


@dataclass
class Querschnittsangaben(BauteilEintrag):
    """
    Was die Platte (:class:`~opencivil.projekt.platte.QuerschnittEintrag`) und
    der gezeichnete Querschnitt
    (:class:`~opencivil.projekt.querschnittsanalyse.QuerschnittsanalyseEintrag`)
    gleich angeben: die Rissanforderung, die Schalter der Zwaengungen, des
    sproeden Versagens und der Duktilitaet mit ihren Werten, womit das Knicken
    rechnet, die Abminderung im Druckfeld und den freien Text. Bis 2026-10-17
    stand jedes dieser Felder zweimal da, je mit eigener Beschreibung.

    Wo nachgewiesen wird, sagt die Geometrie: die Platte je x-Lage, der
    gezeichnete Querschnitt je Richtung oder am ganzen Querschnitt. Die Felder
    hier sind nur mit Namen anzugeben (``KW_ONLY``): so duerfen die Felder der
    Geometrie ohne Vorgabe dahinter folgen -- der Beton der Platte.
    """

    kennung: str
    name: str
    _: KW_ONLY

    rissanforderung: Rissanforderung = Rissanforderung.NORMAL
    """Anforderung an die Rissbildung -- ``normal``, ``erhoeht`` oder ``hoch``."""

    zwaengung: bool = False
    """
    Ob die Zwaengung auf Normalkraft nachgewiesen wird -- an der Platte je
    x-Lage, am gezeichneten Querschnitt am ganzen Querschnitt.

    Vorgabe aus: eine Zwaengung ist eine Annahme ueber das Tragwerk, keine
    Eigenschaft des Querschnitts. Wer sie braucht, schaltet sie ein. An der
    Platte ein Schalter, nicht zwei: nachgewiesen wird nur die Tragrichtung x.
    Die y-Lagen stehen im Querschnitt, weil sie die statische Hoehe von x
    bestimmen und zum Bewehrungsgehalt zaehlen -- nachgewiesen werden sie
    nicht.
    """

    zwaengung_begrenzt: bool = False
    """Ob die rissaktive Dicke der Zwaengung auf Normalkraft hoechstens 500 mm betraegt."""

    zwaengung_biegung: bool = False
    """
    Ob die Zwaengung auf Biegung nachgewiesen wird -- an der Platte je
    x-Lage, am gezeichneten Querschnitt je Richtung.
    """

    zwaengung_biegung_kriechzahl: float = bereich(0.0, heisst="Kriechzahl φ", ab=0.0)
    """
    Die Kriechzahl φ der Zwaengung auf Biegung: der Beton mit ``E_cm/(1+φ)``,
    an der Platte als Wertigkeit ``n = (E_s/E_cm)·(1+φ)``.
    """

    sproede: bool = False
    """Ob der Nachweis gegen sproedes Versagen gefuehrt wird."""

    duktilitaet: bool = False
    """
    Ob der Duktilitaetsnachweis gefuehrt wird.

    Ein Schalter fuer das Bauteil und nicht einer je Lage. An der Platte
    werden beide x-Lagen gerechnet -- die obere traegt das Stuetz-, die untere
    das Feldmoment --, und in der Zusammenfassung steht die unguenstigere.
    Vier Schalter fuer einen Nachweis waren vier Gelegenheiten, den falschen
    zu vergessen; die Frage ist ohnehin, ob der Querschnitt sein Versagen
    ankuendigt, und die beantwortet die schlechtere Lage.
    """

    x_d_max: float = x_d_grenze()
    """
    Der Beiwert k der Grenze ``x/d <= k * 435 N/mm^2 / f_yd`` im
    Duktilitaetsnachweis. Bis 2026-11-14 war er selbst die Grenze; bei B500
    sind beide gleich, darum heisst das Feld weiter so, und alte Dateien
    lesen sich ohne Umweg.
    """

    knicken_wahl_verformung: KnickVerformungswahl = teil(
        KnickVerformungswahl, heisst="Knicken, Verformung (e_2d)")
    """
    Womit die Ausmitte e_2d gerechnet wird -- immer praezise ohne
    Vereinfachung (:data:`~opencivil.nachweis.rechenwahl.VERFORMUNGSARTEN`),
    Vorgabe Bemessungswerte.
    """

    knicken_wahl_widerstand: KnickWiderstandswahl = teil(
        KnickWiderstandswahl, heisst="Knicken, Widerstand (N_Rd)")
    """
    Womit N_Rd(M_Ed = N_Ed·e_tot) gerechnet wird -- Vorgabe die
    0.85·x-Vereinfachung, ohne Handrechnung. Mit derselben Wahl wie die
    Tragsicherheit ist es deren Linie.
    """

    k_c: float = druckfeld()
    """Abminderung der Betondruckfestigkeit in der Druckdiagonalen."""

    beschreibung: str = ""
    """
    Freier Text zum Bauteil -- was sonst nirgends hinpasst.

    Wo es liegt, woher die Schnittgroessen stammen, was noch zu klaeren ist.
    Geht in keine Rechnung ein und steht in keinem Nachweis; er wird
    gespeichert und wieder angezeigt, mehr nicht. Genau dafuer gibt es ihn:
    ohne ein solches Feld landen solche Saetze im Namen.
    """


@dataclass
class KombinationEintrag(Beschreibung):
    """Eine zu pruefende Schnittgroessenkombination."""

    IM_ORT = "Einwirkung"

    name: str
    M_Ed: float = bereich(0.0, heisst="Moment M_Ed", einheit=KNM)
    N_Ed: float = bereich(0.0, heisst="Normalkraft N_Ed", einheit=KN)
    V_Ed: float = bereich(0.0, heisst="Querkraft V_Ed", einheit=KN_PRO_M)
    """Je Meter, nicht je Streifen b -- für den Querkraftnachweis."""

    art: Erfuellungsart = Erfuellungsart.AUTOMATISCH

    aktiv: bool = True
    """Ob dieser Lastfall gerechnet wird. Ausgeschaltet bleibt er stehen."""
