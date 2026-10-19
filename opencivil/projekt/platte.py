"""
opencivil/projekt/platte.py -- eine Platte, wie die Oberflaeche sie beschreibt.

VERANTWORTUNG:
Der :class:`QuerschnittEintrag`: Abmessungen, vier Bewehrungslagen, die
Schalter der Nachweise und die Lastfaelle -- alles, was zu einer Platte
gehoert, als eine speicherbare Datenklasse. Dazu die Vorlage einer frischen
Platte (:meth:`QuerschnittEintrag.neu`) und die Methoden, mit denen man ohne
Oberflaeche Lastfaelle anfuegt.

Was daraus gerechnet wird, steht in :mod:`opencivil.projekt.aufbau`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from opencivil.bewehrungssuche.laengs import Suchmodus
from opencivil.core.einheiten import MM
from opencivil.querschnitt.platte import LAGENZAHL, Richtung
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.projekt.eintraege import (
    HAEUFIG_ANTEIL, QUASISTAENDIG_ANTEIL, Gebrauchsliste, KnickEintrag, KombinationEintrag,
    LageEintrag, ObergrenzeEintrag, PostenEintrag, QuerkraftbewehrungEintrag,
    Querschnittsangaben, RechenwahlEintrag, SpannungsfallEintrag, VerformungEintrag,
    VerformungsfallEintrag, eindeutig,
)
from opencivil.projekt.lesen import ProjektFehler, bereich


@dataclass
class QuerschnittEintrag(Querschnittsangaben):
    """
    Eine Stahlbeton-Platte mit genau vier Bewehrungslagen. Was sie mit dem
    gezeichneten Querschnitt gleich angibt, steht in der Grundlage
    (:class:`~opencivil.projekt.eintraege.Querschnittsangaben`).
    """

    BEZEICHNUNG = "Platte"

    beton: str
    h: float = bereich(300.0, heisst="Dicke h", einheit=MM, ueber=0.0)
    b: float = bereich(1000.0, heisst="Breite b", einheit=MM, ueber=0.0)
    ueberdeckung_unten: float = bereich(30.0, heisst="Überdeckung unten", einheit=MM, ab=0.0)
    ueberdeckung_oben: float = bereich(30.0, heisst="Überdeckung oben", einheit=MM, ab=0.0)
    d_max: float = bereich(32.0, heisst="Grösstkorn D_max", einheit=MM, ueber=0.0)
    """Grösstkorndurchmesser in mm."""

    einlagenhoehe: float = bereich(0.0, heisst="Einlagenhöhe", einheit=MM, ab=0.0)
    """Höhe einer Einlage in mm."""

    querkraftbewehrung: QuerkraftbewehrungEintrag = field(
        default_factory=QuerkraftbewehrungEintrag)
    """Bügel; ohne Durchmesser heisst: keine."""

    haeufig: Gebrauchsliste = field(
        default_factory=lambda: Gebrauchsliste(anteil=HAEUFIG_ANTEIL))
    """Die haeufigen Lastfaelle -- fuer den Nachweis gegen Fliessen."""

    quasistaendig: Gebrauchsliste = field(
        default_factory=lambda: Gebrauchsliste(anteil=QUASISTAENDIG_ANTEIL))
    """Die quasi-staendigen Lastfaelle -- fuer die Rissbreite."""

    verformung: VerformungEintrag = field(default_factory=VerformungEintrag)
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

    automatik_teilungen: List[float] = field(default_factory=lambda: [150.0])
    """
    Teilungen, die es versucht. Grundbewehrung und Zulage teilen sich eine.

    Vorgabe ist die eine uebliche. Wer mehrere angibt, bekommt die mit der
    kleinsten Stahlflaeche -- das kostet aber je Teilung einen ganzen
    Suchlauf, und meistens steht die Teilung ohnehin fest.
    """

    automatik_mindestdurchmesser: float = 10.0
    """
    Duennster Stab, den die Suche einbaut -- in mm. Die Grundbewehrung jeder
    Lage hat ihn mindestens, in x wie in y; die Zulage darf fehlen.

    Null heisst: kein Mindestdurchmesser, eine Lage darf auch leer bleiben.
    """

    automatik_grenze: ObergrenzeEintrag = field(default_factory=ObergrenzeEintrag)
    """
    Mehr Querschnitt bekommt keine x-Lage von der Suche -- in allen Modi,
    auch beim Optimieren der Plattendicke. Vorgabe ⌀30@150, 4712 mm²/m.
    """

    automatik_mindestdicke: float = 150.0
    """Duenner sucht die Dickenoptimierung keine Platte -- in mm."""

    automatik_querkraft: bool = False
    """Ob auch die Buegel gesucht werden."""

    automatik_querkraft_teilungen: List[float] = field(
        default_factory=lambda: [100.0, 150.0, 200.0])

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

    tragsicherheit_wahl: RechenwahlEintrag = field(default_factory=RechenwahlEintrag)
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
                f"Platte '{self.name}': {len(self.lagen)} Lagen angegeben, eine "
                f"Platte hat genau {LAGENZAHL}.")
        while len(self.lagen) < LAGENZAHL:
            self.lagen.append(LageEintrag())

    def richtung_von(self, nummer: int) -> Richtung:
        """Richtung der Lage 1..4 -- die Paare (1,2) und (3,4) sind gekoppelt."""
        eins, vier = self.richtung_lage1, self.richtung_lage4
        return {1: eins, 2: eins.gegenrichtung, 3: vier.gegenrichtung, 4: vier}[nummer]

    def materialien(self) -> List[str]:
        """
        Jedes Material, auf das die Platte zeigt -- Beton, Stahl jeder Lage,
        Buegelstahl --, je einmal. Jeder Verweis zaehlt, auch einer, der gerade nichts traegt: wer das
        Material loescht, liesse ihn ins Leere zeigen, und spaetestens die
        naechste Aenderung machte daraus einen Fehler beim Rechnen.
        Bis 2026-10-17 kannte der Loeschschutz der Oberflaeche den Buegelstahl
        nicht.
        """
        gesehen: List[str] = []
        for kennung in (self.beton, *(l.stahl for l in self.lagen),
                        self.querkraftbewehrung.stahl):
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
        wird vor dem Rechnen (:func:`~opencivil.projekt.lesen.inhalt_pruefen`).
        Ebenso die Namen der Faelle (:func:`~opencivil.projekt.eintraege.eindeutig`),
        die der Tragsicherheit zuerst: aus ihnen leiten sich die
        Gebrauchslisten ab.
        """
        eindeutig((k.name for k in self.kombinationen), wo, "Tragsicherheitseinwirkung")
        for liste, wort in ((self.haeufig, "häufige"),
                            (self.quasistaendig, "quasi-ständige")):
            liste.namen_pruefen(wo, self.kombinationen, wort)
        eindeutig((k.name for k in self.knickfaelle), wo, "Knicknachweis")
        eindeutig((f.name for f in self.spannungsfaelle), wo, "Spannung-Dehnung-Analyse")
        eindeutig((f.name for f in self.verformung.faelle), wo, "Verformungsfall")

        zusammen = self.ueberdeckung_unten + self.ueberdeckung_oben
        if zusammen >= self.h:
            raise ProjektFehler(
                f"{wo}: die Überdeckungen ergeben zusammen {zusammen:g} mm "
                f"und lassen in einer {self.h:g} mm dicken Platte keinen Platz für "
                f"Bewehrung.")

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
            kombinationen=[KombinationEintrag(name="Tragsicherheit 1")],
        )
