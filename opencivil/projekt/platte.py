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
from opencivil.nachweis.duktilitaet import GRENZE as X_D_MAX
from opencivil.nachweis.rechenwahl import FASERARTEN, VERFORMUNGSARTEN
from opencivil.querschnitt.platte import K_C, LAGENZAHL, Richtung
from opencivil.projekt.eintraege import (
    HAEUFIG_ANTEIL, QUASISTAENDIG_ANTEIL, Beschreibung, Gebrauchsliste,
    KnickEintrag, KombinationEintrag, LageEintrag, ObergrenzeEintrag,
    PostenEintrag, QuerkraftbewehrungEintrag, RechenwahlEintrag, SpannungsfallEintrag,
    VerformungEintrag, VerformungsfallEintrag, eindeutig, x_d_max_pruefen,
)
from opencivil.nachweis.rissanforderung import RISSANFORDERUNGEN
from opencivil.projekt.lesen import ProjektFehler, einer_von, nicht_negativ

#: Die Richtungen einer Lage.
RICHTUNGEN = tuple(r.value for r in Richtung)


@dataclass
class QuerschnittEintrag(Beschreibung):
    """Eine Stahlbeton-Platte mit genau vier Bewehrungslagen."""

    BEZEICHNUNG = "Platte"

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

    rissanforderung: str = einer_von(RISSANFORDERUNGEN, "normal")
    """Anforderung an die Rissbildung -- ``normal``, ``erhoeht`` oder ``hoch``."""

    beschreibung: str = ""
    """
    Freier Text zur Platte -- was sonst nirgends hinpasst.

    Wo sie liegt, woher die Schnittgroessen stammen, was noch zu klaeren ist.
    Geht in keine Rechnung ein und steht in keinem Nachweis; sie wird
    gespeichert und wieder angezeigt, mehr nicht. Genau dafuer gibt es sie:
    ohne ein solches Feld landen solche Saetze im Namen der Platte.
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

    knicken_wahl_verformung: RechenwahlEintrag = field(
        default_factory=RechenwahlEintrag.knicken_verformung)
    """
    Womit die Ausmitte e_2d gerechnet wird -- immer praezise ohne
    Vereinfachung (:data:`~opencivil.nachweis.rechenwahl.VERFORMUNGSARTEN`),
    Vorgabe Bemessungswerte.
    """

    knicken_wahl_widerstand: RechenwahlEintrag = field(
        default_factory=RechenwahlEintrag.knicken_widerstand)
    """
    Womit N_Rd(M_Ed = N_Ed·e_tot) gerechnet wird -- Vorgabe die
    0.85·x-Vereinfachung, ohne Handrechnung. Mit derselben Wahl wie die
    Tragsicherheit ist es deren Linie.
    """

    spannungsfaelle: List[SpannungsfallEintrag] = field(default_factory=list)
    """Auswertungen am Querschnitt -- Bilder, keine Nachweise."""

    automatik_modus: str = einer_von((m.value for m in Suchmodus),
                                     Suchmodus.GRUND_OHNE_ZULAGE_MIT.value)
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

    sproede: bool = False
    """Ob der Nachweis gegen sproedes Versagen gefuehrt wird."""

    zwaengung_biegung: bool = False
    """Ob die Zwaengung auf Biegung nachgewiesen wird."""

    zwaengung_biegung_kriechzahl: float = nicht_negativ(0.0)
    """Die Kriechzahl phi der Zwaengung auf Biegung: ``n = (E_s/E_cm)*(1+phi)``."""

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

    x_d_max: float = X_D_MAX
    """
    Grenze der bezogenen Druckzonenhoehe im Duktilitaetsnachweis.

    Vorgabe 0.35, hoechstens 0.5 -- die Zahlen stehen beim Nachweis
    (``duktilitaet.GRENZE``, ``duktilitaet.HOECHSTENS``).
    """

    lagen: List[LageEintrag] = field(default_factory=list)
    """Genau vier, Index 0 = 1. Lage (unterste). Fehlen welche, sind sie leer."""

    richtung_lage1: str = einer_von(RICHTUNGEN, Richtung.Y.value)
    """
    Richtung der 1. Lage; die 2. bekommt die Gegenrichtung.

    Vorgabe y, damit x auf der 2. und 3. Lage liegt -- innen. Das ist der
    unguenstigere Fall und der haeufigere: die Tragrichtung liegt selten zu
    unterst, weil die Querrichtung darunter durchlaeuft. Wer es anders
    verlegt, stellt es um.
    """

    richtung_lage4: str = einer_von(RICHTUNGEN, Richtung.Y.value)
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
        eins = Richtung(self.richtung_lage1)
        vier = Richtung(self.richtung_lage4)
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

    def pruefen(self) -> None:
        """
        Was an dieser Platte nicht stimmen kann, bevor daraus gerechnet wird.

        Lastfallnamen eindeutig je Liste (siehe :func:`eintraege.eindeutig`);
        die Gebrauchslisten pruefen sich selbst, samt Anteil und abgeleiteten
        Namen. Laeuft auch beim Oeffnen einer Datei -- darum hier nichts, was
        eine gespeicherte Platte unoeffenbar machte (siehe
        :meth:`zahlen_pruefen`).
        """
        eindeutig(self.kombinationen, self.name, "Tragsicherheitseinwirkung")
        eindeutig(self.knickfaelle, self.name, "Knicknachweis")
        eindeutig(self.spannungsfaelle, self.name, "Spannung-Dehnung-Analyse")
        for liste, wort in ((self.haeufig, "häufige"),
                            (self.quasistaendig, "quasi-ständige")):
            liste.pruefen(self.name, self.kombinationen, wort)
        self.verformung.pruefen(self.name)
        self.tragsicherheit_wahl.pruefen(f"Platte '{self.name}', Tragsicherheit")
        self.knicken_wahl_verformung.pruefen(f"Platte '{self.name}', Knicken, Verformung",
                                             VERFORMUNGSARTEN)
        self.knicken_wahl_widerstand.pruefen(f"Platte '{self.name}', Knicken, Widerstand",
                                             FASERARTEN)

    def zahlen_pruefen(self) -> None:
        """
        Haelt unmoegliche Abmessungen und Zahlen auf, bevor daraus ein
        Widerstand wird.

        Bis hierher lief jede Geometrie durch: eine Platte mit ``h = -300`` wurde
        gerechnet, eine mit beidseitiger Ueberdeckung groesser als die Dicke auch.
        Heraus kamen Zahlen, die aussahen wie ein Ergebnis. Ein Tragwerksnachweis
        darf an so etwas nicht vorbeirechnen -- er muss sagen, was nicht stimmt.

        Geprueft wird nur, was geometrisch unmoeglich ist, nicht was unueblich
        waere. Ob 20 mm Ueberdeckung fuer die Expositionsklasse genuegen,
        entscheidet der Ingenieur.

        **Nicht in :meth:`pruefen`.** Das laeuft auch beim Oeffnen einer Datei;
        eine abgelegte Platte mit ``h = 0`` liesse sich dann nicht mehr oeffnen
        -- und damit nicht mehr korrigieren. Gefragt wird erst beim Bauen.
        """
        name = self.name
        for feld, wert, wie in (
            ("Dicke h", self.h, "grösser als null"),
            ("Breite b", self.b, "grösser als null"),
            ("Grösstkorn D_max", self.d_max, "grösser als null"),
        ):
            if wert <= 0.0:
                raise ProjektFehler(
                    f"Platte '{name}': {feld} muss {wie} sein, angegeben ist {wert:g} mm.")

        for feld, wert in (("Überdeckung unten", self.ueberdeckung_unten),
                           ("Überdeckung oben", self.ueberdeckung_oben),
                           ("Einlagenhöhe", self.einlagenhoehe)):
            if wert < 0.0:
                raise ProjektFehler(
                    f"Platte '{name}': {feld} kann nicht negativ sein "
                    f"({wert:g} mm).")

        zusammen = self.ueberdeckung_unten + self.ueberdeckung_oben
        if zusammen >= self.h:
            raise ProjektFehler(
                f"Platte '{name}': die Überdeckungen ergeben zusammen {zusammen:g} mm "
                f"und lassen in einer {self.h:g} mm dicken Platte keinen Platz für "
                f"Bewehrung.")

        # Keine Abmessungen, aber aus demselben Grund hier und nicht beim
        # Oeffnen: eine abgelegte Platte mit einer zu hohen Grenze soll sich
        # oeffnen und korrigieren lassen.
        x_d_max_pruefen(self.x_d_max, f"Platte '{name}'")
        for nummer, lage in enumerate(self.lagen, start=1):
            lage.grund.pruefen(f"Platte '{name}', {nummer}. Lage, Grundbewehrung")
            lage.zulage.pruefen(f"Platte '{name}', {nummer}. Lage, Zulage")
        for fall in self.knickfaelle:
            fall.zahlen_pruefen(f"Platte '{name}'")
        for fall in self.verformung.faelle:
            fall.zahlen_pruefen(f"Platte '{name}'")

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
                        zugseite: str = "unten") -> VerformungsfallEintrag:
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
            kombinationen=[KombinationEintrag(name="Tragsicherheit 1", M_Ed=30.0)],
        )
