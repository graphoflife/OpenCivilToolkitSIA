"""
opencivil/projekt/platte.py -- eine Platte, wie die Oberflaeche sie beschreibt.

VERANTWORTUNG:
Der :class:`QuerschnittEintrag`: Abmessungen, vier Bewehrungslagen, die
Schalter der Nachweise und die Lastfaelle -- alles, was zu einer Platte
gehoert, als eine speicherbare Datenklasse. Dazu die Vorlage einer frischen
Platte (:meth:`QuerschnittEintrag.neu`) und die Methoden, mit denen man ohne
Oberflaeche Lastfaelle anfuegt -- und die Teile, die nur sie hat: Posten und
Lage (:class:`PostenEintrag`, :class:`LageEintrag`), die Obergrenze der
Bewehrungssuche und die Buegel.

Was daraus gerechnet wird, steht in :mod:`opencivil.projekt.aufbau`.
"""

from __future__ import annotations

import functools
import math
from dataclasses import dataclass, field
from typing import Any, List, Optional

from opencivil.bewehrungssuche.laengs import Suchmodus
from opencivil.core.einheiten import KN, MM, MM2, Groesse
from opencivil.material.basis import Baustoff
from opencivil.querschnitt.geometrie import Linienart
from opencivil.querschnitt.platte import (
    LAGENZAHL, Bewehrungsposten, Querkraftbewehrung, Richtung,
)
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.projekt.eintraege import (
    HAEUFIG_ANTEIL, QUASISTAENDIG_ANTEIL, Beschreibung, Gebrauchsliste, KnickEintrag,
    KombinationEintrag, Querschnittsangaben, RechenwahlEintrag, SpannungsfallEintrag,
    VerformungEintrag, VerformungsfallEintrag, groesste_neigung, kleinste_neigung,
    spannungsfallnamen,
)
from opencivil.projekt.fallnamen import Fallnamen
from opencivil.projekt.lesen import ProjektFehler, als_groesse, bereich, einer_von, teil


# ===========================================================================
# Bewehrung
# ===========================================================================

#: Wie ein Posten der Platte seine Menge angibt -- wie eine Stablinie
#: (:class:`~opencivil.projekt.querschnittsanalyse.StablinieEintrag`), aber
#: ohne verschmierte Flaeche: als Teilung oder als Stabzahl.
MENGEN = (Linienart.TEILUNG, Linienart.ANZAHL)


@dataclass
class PostenEintrag(Beschreibung):
    """
    Grundbewehrung oder Zulage einer Lage.

    Je Art ein eigenes Feld fuer die Menge, wie bei der Stablinie: wer von der
    Teilung zur Stabzahl wechselt und zurueck, findet seine Zahl noch vor.
    Welche gilt, sagt ``art``. Bis 2026-10-18 war genau eine der beiden
    gesetzt, und beim Umschalten setzte die Oberflaeche die andere mit eigenen
    Vorgaben (5 Staebe, 150 mm).
    """

    durchmesser: float = bereich(0.0, heisst="Durchmesser", einheit=MM, ab=0.0)
    """in mm; 0 bedeutet: nicht vorhanden."""

    abstand: float = bereich(150.0, heisst="Teilung", einheit=MM, ueber=0.0)
    """
    Teilung in mm -- bei Art «Teilung». Null weist schon das Feld ab, auch
    ohne Durchmesser: bis 2026-10-16 hiess eine Teilung von null still «kein
    Stab», bis 2026-11-20 nahm das Feld sie an, und erst die ganze Platte
    rechnete nicht.
    """

    anzahl: float = bereich(5.0, heisst="Stabzahl", ueber=0.0)
    """Stabzahl auf der Breite b -- bei Art «Anzahl»."""

    art: Linienart = einer_von(MENGEN, Linienart.TEILUNG)
    """Welche der beiden gilt -- nach den Zahlen, damit ``PostenEintrag(⌀, s)`` bleibt."""

    @property
    def ueber_abstand(self) -> bool:
        return self.art is Linienart.TEILUNG

    @property
    def vorhanden(self) -> bool:
        """Ob Staebe liegen -- das sagt der Durchmesser; Teilung und Stabzahl sind nie null."""
        return self.durchmesser > 0

    def als_posten(self) -> Bewehrungsposten:
        return Bewehrungsposten(
            durchmesser=als_groesse(self, "durchmesser"),
            abstand=als_groesse(self, "abstand") if self.ueber_abstand else None,
            anzahl=None if self.ueber_abstand else self.anzahl,
        )

    def je_meter(self, b: float = 1000.0) -> float:
        """
        Bewehrungsquerschnitt in mm²/m. Ueber die Teilung haengt er an keiner
        Breite; bei einer Stabzahl liegen die Staebe auf der Breite ``b`` (mm).
        """
        return self.als_posten().flaeche(Groesse(b, MM)).in_einheit(MM2) * 1000.0 / b


@dataclass
class LageEintrag(Beschreibung):
    """Eine der vier Lagen -- ihr Stahl ist der der Platte."""

    IM_ORT = "Lage"

    grund: PostenEintrag = teil(PostenEintrag, heisst="Grund")
    zulage: PostenEintrag = teil(lambda: PostenEintrag(durchmesser=0.0), heisst="Zulage")

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

    grund: PostenEintrag = teil(lambda: PostenEintrag(durchmesser=30.0), heisst="Grund")
    zulage: PostenEintrag = teil(lambda: PostenEintrag(durchmesser=0.0), heisst="Zulage")

    @property
    def je_meter(self) -> float:
        """Die Obergrenze in mm²/m -- unendlich, wenn keine gesetzt ist."""
        summe = self.grund.je_meter() + self.zulage.je_meter()
        return summe if summe > 0 else math.inf


@dataclass
class QuerkraftbewehrungEintrag(Beschreibung):
    """
    Die Bügel einer Platte -- ein Raster, ein Durchmesser, zwei Teilungen.
    Ihr Stahl ist der der Platte (Benutzer, 2026-10-24).

    In y darf statt der Teilung eine Stabzahl über die betrachtete Breite
    stehen; in x nicht. Siehe
    :class:`opencivil.querschnitt.platte.Querkraftbewehrung`. In y je Art ein
    eigenes Feld, wie beim :class:`PostenEintrag`; welches gilt, sagt ``art_y``.
    """

    durchmesser: float = bereich(0.0, heisst="Bügeldurchmesser", einheit=MM, ab=0.0)
    """in mm; 0 bedeutet: keine Querkraftbewehrung."""

    abstand_x: float = bereich(200.0, heisst="Bügelteilung in x", einheit=MM, ueber=0.0)
    abstand_y: float = bereich(200.0, heisst="Bügelteilung in y", einheit=MM, ueber=0.0)
    anzahl_y: float = bereich(5.0, heisst="Bügelzahl in y", ueber=0.0)
    """
    Teilungen und Stabzahl weist schon ihr Feld ab, wenn sie nicht ueber
    null liegen, auch ohne Buegel -- bis 2026-11-20 erst die ganze Platte.
    """

    art_y: Linienart = einer_von(MENGEN, Linienart.TEILUNG)
    alpha_min: int = kleinste_neigung()
    alpha_max: int = groesste_neigung()

    @property
    def vorhanden(self) -> bool:
        """
        Ob Buegel liegen -- das sagt allein der Durchmesser. Eine Teilung von
        null heisst nicht «keine Buegel»: ihr Feld weist sie ab.
        """
        return self.durchmesser > 0

    @property
    def ueber_teilung_y(self) -> bool:
        """In y eine Teilung -- sonst eine Stabzahl."""
        return self.art_y is Linienart.TEILUNG

    def als_bewehrung(self, stahl: Baustoff) -> Querkraftbewehrung:
        """Die Buegel fuer den Querschnitt."""
        g = functools.partial(als_groesse, self)
        return Querkraftbewehrung(
            durchmesser=g("durchmesser"),
            stahl=stahl,
            abstand_x=g("abstand_x"),
            abstand_y=g("abstand_y") if self.ueber_teilung_y else None,
            anzahl_y=None if self.ueber_teilung_y else self.anzahl_y,
            alpha_min=self.alpha_min,
            alpha_max=self.alpha_max,
        )


# ===========================================================================
# Die Platte
# ===========================================================================


@dataclass
class QuerschnittEintrag(Querschnittsangaben):
    """
    Eine Stahlbeton-Platte mit genau vier Bewehrungslagen. Was sie mit dem
    gezeichneten Querschnitt gleich angibt, steht in der Grundlage
    (:class:`~opencivil.projekt.eintraege.Querschnittsangaben`).
    """

    BEZEICHNUNG = "Platte"
    STAMM = "Platte"
    ERSTE_MATERIALIEN = {"beton": "beton", "stahl": "betonstahl"}

    beton: str = ""
    """
    Leer, solange keiner gewaehlt ist -- etwa in der Sandbox eines Projekts
    ohne Beton: dann rechnet die Platte nicht, das Projekt schon.
    """
    stahl: str = ""
    """
    Der Betonstahl der Platte: aller vier Lagen und der Bügel -- einer für
    alle (Benutzer, 2026-10-24).
    """

    h: float = bereich(300.0, heisst="Dicke h", einheit=MM, ueber=0.0)
    b: float = bereich(1000.0, heisst="Breite b", einheit=MM, ueber=0.0)
    ueberdeckung_unten: float = bereich(30.0, heisst="Überdeckung unten", einheit=MM, ab=0.0)
    ueberdeckung_oben: float = bereich(30.0, heisst="Überdeckung oben", einheit=MM, ab=0.0)
    d_max: float = bereich(32.0, heisst="Grösstkorn D_max", einheit=MM, ueber=0.0)
    """Grösstkorndurchmesser in mm."""

    einlagenhoehe: float = bereich(0.0, heisst="Grösstes Mass der Einlage", einheit=MM, ab=0.0)
    """Grösstes Mass einer Einlage in mm, Breite oder Höhe -- der Name ist von früher."""

    querkraftbewehrung: QuerkraftbewehrungEintrag = teil(QuerkraftbewehrungEintrag,
                                                         heisst="Bügel")
    """Bügel; ohne Durchmesser heisst: keine."""

    querkraftkurve_normalkraft: Optional[float] = bereich(
        None, heisst="Normalkraft der M-V-Kurve", einheit=KN)
    """
    Fuer welche Normalkraft das Bild «Querkraft ueber Moment» gilt, in kN,
    Zug positiv -- leer: die des ersten Falls. Nur das Bild liest sie, kein
    Nachweis. Bis 2026-11-20 lebte sie in der Oberflaeche neben dem Projekt
    und sprang nach dem Neuladen still auf die Vorgabe zurueck.
    """

    haeufig: Gebrauchsliste = teil(lambda: Gebrauchsliste(anteil=HAEUFIG_ANTEIL),
                                   heisst="Fliessen häufig")
    """Die haeufigen Lastfaelle -- fuer den Nachweis gegen Fliessen."""

    quasistaendig: Gebrauchsliste = teil(lambda: Gebrauchsliste(anteil=QUASISTAENDIG_ANTEIL),
                                         heisst="Stahlspannung quasi-ständig")
    """Die quasi-staendigen Lastfaelle -- fuer die Rissbreite."""

    verformung: VerformungEintrag = teil(VerformungEintrag, heisst="Verformung")
    """Die Verformungsfaelle und das phi ihres Vergroesserungsfaktors."""

    knickfaelle: List[KnickEintrag] = field(default_factory=list)
    """Knicknachweise; leer heisst: keiner."""

    spannungsfaelle: List[SpannungsfallEintrag] = field(default_factory=list)
    """Auswertungen am Querschnitt -- Bilder, keine Nachweise."""

    automatik_modus: Suchmodus = Suchmodus.GRUND_OHNE_ZULAGE_MIT
    """Wonach das Bewehrungswerkzeug sucht -- siehe ``bewehrungssuche.Suchmodus``."""

    automatik_dicke: bool = False
    """
    Ob das Werkzeug dazu die duennste Plattendicke sucht («Plattendicke
    optimieren»). Ein Schalter neben dem Modus und nicht ein eigener Modus:
    je Dicke laeuft dieselbe Suche im gewaehlten Modus.
    """

    automatik_y_wie_x: bool = False
    """
    Ob die y-Grundbewehrung jeder Seite der x-Grundbewehrung dieser Seite
    folgt -- gleicher Durchmesser, gleiche Teilung.

    Ein Netz, wie es verlegt wird. Die Suche rechnet schon waehrend des Suchens
    damit: liegt y aussen, kostet ihr Durchmesser x die statische Hoehe.
    """

    automatik_teilungen: List[float] = bereich(
        heisst="Teilung", einheit=MM, ueber=0.0, fabrik=lambda: [150.0])
    """
    Teilungen, die es versucht. Grundbewehrung und Zulage teilen sich eine.
    Jede ueber null -- das Feld der Oberflaeche liest die Grenze von hier.

    Vorgabe ist die eine uebliche. Wer mehrere angibt, bekommt die mit der
    kleinsten Stahlflaeche -- das kostet aber je Teilung einen ganzen
    Suchlauf, und meistens steht die Teilung ohnehin fest.
    """

    automatik_mindestdurchmesser: float = bereich(10.0, heisst="Mindestdurchmesser",
                                                  einheit=MM, ab=0.0)
    """
    Duennster Stab, den die Suche einbaut -- in mm. Die Grundbewehrung jeder
    Lage hat ihn mindestens, in x wie in y; die Zulage darf fehlen.

    Null heisst: kein Mindestdurchmesser, eine Lage darf auch leer bleiben.
    """

    automatik_grenze: ObergrenzeEintrag = teil(ObergrenzeEintrag,
                                               heisst="Bewehrung suchen, Obergrenze")
    """
    Mehr Querschnitt bekommt keine x-Lage von der Suche -- in allen Modi,
    auch beim Optimieren der Plattendicke. Vorgabe ⌀30@150, 4712 mm²/m.
    """

    automatik_mindestdicke: float = bereich(150.0, heisst="Mindestdicke", einheit=MM, ueber=0.0)
    """Duenner sucht die Dickenoptimierung keine Platte -- in mm."""

    automatik_querkraft: bool = False
    """Ob auch die Buegel gesucht werden."""

    automatik_querkraft_teilungen: List[float] = bereich(
        heisst="Bügelteilung", einheit=MM, ueber=0.0, fabrik=lambda: [100.0, 150.0, 200.0])

    lagen: List[LageEintrag] = field(default_factory=list)
    """Genau vier, Index 0 = 1. Lage (unterste). Fehlen welche, sind sie leer."""

    richtung_lage1: Richtung = Richtung.Y
    """
    Richtung der 1. Lage; die 2. bekommt die Gegenrichtung.

    Vorgabe y, damit x auf der 2. und 3. Lage liegt -- innen. Das ist der
    unguenstigere Fall und der haeufigere: die Tragrichtung liegt selten zu
    unterst, weil die Querrichtung darunter durchlaeuft. Wer es anders
    verlegt, stellt es um.
    """

    richtung_lage4: Richtung = Richtung.Y
    """Richtung der 4. Lage; die 3. bekommt die Gegenrichtung."""

    kombinationen: List[KombinationEintrag] = field(default_factory=list)

    tragsicherheit_wahl: RechenwahlEintrag = teil(RechenwahlEintrag,
                                                  heisst="Tragsicherheit, Rechenwahl")
    """
    Womit die Tragsicherheit rechnet -- Vorgabe die Handrechnung mit
    Bemessungswerten. Die Querkraft und das sproede Versagen lesen ihren
    Momentenwiderstand aus derselben Linie.
    """

    def __post_init__(self) -> None:
        # Mehr als vier waeren Bewehrung, die nirgends hinkaeme -- abschneiden
        # hiesse, sie still wegzulassen.
        if len(self.lagen) > LAGENZAHL:
            raise ProjektFehler(
                f"{len(self.lagen)} Lagen angegeben, eine "
                f"Platte hat genau {LAGENZAHL}.", wo=f"Platte '{self.name}'")
        while len(self.lagen) < LAGENZAHL:
            self.lagen.append(LageEintrag())

    def richtung_von(self, nummer: int) -> Richtung:
        """Richtung der Lage 1..4 -- die Paare (1,2) und (3,4) sind gekoppelt."""
        eins, vier = self.richtung_lage1, self.richtung_lage4
        return {1: eins, 2: eins.gegenrichtung, 3: vier.gegenrichtung, 4: vier}[nummer]

    def materialien(self) -> List[str]:
        """
        Jedes Material, auf das die Platte zeigt -- Beton und Stahl --, je
        einmal. Jeder Verweis zaehlt, auch einer, der gerade nichts traegt: wer das
        Material loescht, liesse ihn ins Leere zeigen, und spaetestens die
        naechste Aenderung machte daraus einen Fehler beim Rechnen.
        Bis 2026-10-17 kannte der Loeschschutz der Oberflaeche den Buegelstahl
        nicht.
        """
        gesehen: List[str] = []
        for kennung in (self.beton, self.stahl):
            if kennung and kennung not in gesehen:
                gesehen.append(kennung)
        return gesehen

    def bezuege(self) -> List[str]:
        """Die Bauteile, deren Querschnitt die Platte nimmt -- keine."""
        return []

    # -- Pruefen und Leeren -------------------------------------------------

    def regeln(self, wo: str) -> None:
        """
        Haelt unmoegliche Abmessungen und Namen auf, bevor daraus ein
        Widerstand wird -- was mehrere Felder zusammen betrifft; wo jede Zahl
        fuer sich liegt, steht an ihrem Feld (:func:`~opencivil.projekt.lesen.bereich`).

        Bis hierher lief jede Geometrie durch: eine Platte mit ``h = -300`` wurde
        gerechnet, eine mit beidseitiger Ueberdeckung groesser als die Dicke auch.
        Heraus kamen Zahlen, die aussahen wie ein Ergebnis. Ein Tragwerksnachweis
        darf an so etwas nicht vorbeirechnen -- er muss sagen, was nicht stimmt.

        Geprueft wird nur, was geometrisch unmoeglich ist, nicht was unueblich
        waere. Ob 20 mm Ueberdeckung fuer die Expositionsklasse genuegen,
        entscheidet der Ingenieur.

        **Nicht beim Oeffnen.** Eine abgelegte Platte mit ``h = 0`` liesse sich
        sonst nicht mehr oeffnen -- und damit nicht mehr korrigieren. Gefragt
        wird vor dem Rechnen (:func:`~opencivil.projekt.lesen.inhalt_pruefen`),
        nach den Namen der Faelle (:meth:`fallnamen`).
        """
        zusammen = self.ueberdeckung_unten + self.ueberdeckung_oben
        if zusammen >= self.h:
            raise ProjektFehler(
                f"die Überdeckungen ergeben zusammen {zusammen:g} mm "
                f"und lassen in einer {self.h:g} mm dicken Platte keinen Platz für "
                f"Bewehrung.", wo=wo)

    def fallnamen(self) -> List[Fallnamen]:
        """
        Die Listen, deren Namen sich unterscheiden muessen -- die der
        Tragsicherheit zuerst: aus ihnen leiten sich die Gebrauchslisten ab.
        """
        return [
            Fallnamen.aus("kombinationen", "Tragsicherheitseinwirkung", self.kombinationen),
            self.haeufig.namensliste("haeufig", self.kombinationen, "häufige"),
            self.quasistaendig.namensliste("quasistaendig", self.kombinationen, "quasi-ständige"),
            Fallnamen.aus("knickfaelle", "Knicknachweis", self.knickfaelle),
            spannungsfallnamen(self.spannungsfaelle),
            Fallnamen.aus("verformung.faelle", "Verformungsfall", self.verformung.faelle),
        ]

    def ohne_lastfaelle(self) -> None:
        """
        Jede Lastfallliste leeren -- was bleibt, fragt nicht nach der Belastung.

        Die Bewehrungssuche braucht das fuer ihre Modi ohne Kraefte. Die Regel
        heisst «alle», ohne Ausnahme, und sie steht neben den Feldern: wer
        eine Lastfallliste anfuegt, findet sie hier. Ein Test sucht die Listen
        ueber die Typen der Felder und schlaegt an, wenn eine fehlt -- frueher
        stand diese Aufzaehlung in der Suche, und die quasi-staendigen waeren
        dort beinahe vergessen worden.
        """
        self.kombinationen = []
        self.knickfaelle = []
        self.spannungsfaelle = []
        self.haeufig.faelle = []
        self.quasistaendig.faelle = []
        self.verformung.faelle = []

    def ohne_querkraft(self) -> None:
        """
        Die Querkraft aus jeder Tragsicherheitseinwirkung nehmen: der
        Querkraftnachweis bleibt still, alles andere rechnet wie zuvor. Eine
        Querkraft hat die Platte nur dort (``V_Ed``).

        Die Laengssuche braucht das, wenn die Buegel mitgesucht werden
        (``automatik_querkraft``): die Querkraft tragen dann die Buegel, die
        die Buegelsuche danach findet.
        """
        for k in self.kombinationen:
            k.V_Ed = 0.0

    # -- Ohne Oberflaeche ---------------------------------------------------
    #
    # Wer in Python rechnet, soll eine Einwirkung anfuegen koennen, ohne die
    # Eintragsklasse und die Liste zu kennen, in die sie gehoert. Jede Methode
    # haengt genau einen Eintrag an und gibt ihn zurueck -- er ist derselbe,
    # den die Oberflaeche anlegen wuerde, und laesst sich danach aendern.

    def einwirkung(self, name: str, *, M_Ed: float = 0.0, N_Ed: float = 0.0,
                   V_Ed: float = 0.0) -> KombinationEintrag:
        """Eine Tragsicherheitseinwirkung -- kNm, kN und kN/m, Zug positiv."""
        eintrag = KombinationEintrag(name=name, M_Ed=M_Ed, N_Ed=N_Ed, V_Ed=V_Ed)
        self.kombinationen.append(eintrag)
        return eintrag

    def knickfall(self, name: str, *, N_Ed: float, M_Ed_1: float = 0.0,
                  laenge: float = 3.0,
                  knicklaenge: Optional[float] = None) -> KnickEintrag:
        """Ein Knicknachweis -- N_Ed in kN (Druck negativ), Laengen in m."""
        eintrag = KnickEintrag(
            name=name, N_Ed=N_Ed, M_Ed_1=M_Ed_1, laenge=laenge,
            knicklaenge=laenge if knicklaenge is None else knicklaenge)
        self.knickfaelle.append(eintrag)
        return eintrag

    def verformungsfall(self, name: str, *, w: float, laenge: float,
                        zugseite: Zugseite = Zugseite.UNTEN) -> VerformungsfallEintrag:
        """Ein Verformungsfall -- w in mm, mit E_cm ermittelt; die Spannweite in m."""
        return self.verformung.fall(name, w=w, laenge=laenge, zugseite=zugseite)

    def spannungsfall(self, name: str, *, art: str = "schnittgroessen",
                      **felder: Any) -> SpannungsfallEintrag:
        """
        Eine Spannung-Dehnung-Analyse -- Felder wie im Eintrag, in kN, kNm und
        Promille. Gelesen wie aus einer Datei, also mit denselben Pruefungen:
        ein Feld, eine Art oder ein Betongesetz, das es nicht gibt, meldet
        sich hier.
        """
        eintrag = SpannungsfallEintrag.aus_dict(
            {"name": name, "art": art, **felder}, f"Platte '{self.name}', spannungsfaelle")
        self.spannungsfaelle.append(eintrag)
        return eintrag


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
        Lagen bewehrt, eine Einwirkung zum Anfangen -- ohne Moment, ohne
        Kraft: eine neue Zeile bringt keine Einwirkung mit (Benutzer,
        2026-10-19). Alles Uebrige kommt aus den Vorgabewerten der Felder.
        """
        def lage(d: float) -> LageEintrag:
            return LageEintrag(
                grund=PostenEintrag(durchmesser=d, abstand=150.0),
                # Auch die leere Zulage wird ueber die Teilung gefuehrt --
                # das ist der Regelfall bei Platten.
                zulage=PostenEintrag(durchmesser=0.0, abstand=150.0),
            )

        return cls(
            kennung=kennung,
            name=name,
            beton=beton,
            stahl=stahl,
            # Alle vier Lagen bewehrt. Nachgewiesen wird nur x -- das sind
            # die beiden inneren --, aber die aeusseren y-Lagen liegen
            # darunter und darueber und druecken die statische Hoehe von x
            # nach innen. Sie leer zu lassen hiesse, mit einer Hoehe zu
            # rechnen, die es auf der Baustelle nicht gibt.
            lagen=[lage(durchmesser) for _ in range(LAGENZAHL)],
            querkraftbewehrung=QuerkraftbewehrungEintrag(durchmesser=0.0),
            kombinationen=[KombinationEintrag(name="Einwirkung 1")],
        )
