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
from typing import Any, List, Mapping, Optional

from opencivil.nachweis.duktilitaet import GRENZE as X_D_MAX, HOECHSTENS as X_D_HOECHSTENS
from opencivil.querschnitt.platte import K_C, KRIECHZAHL, LAGENZAHL, Richtung
from opencivil.projekt.eintraege import (
    HAEUFIG_ANTEIL, QUASISTAENDIG_ANTEIL, Beschreibung, Gebrauchsliste,
    KnickEintrag, KombinationEintrag, LageEintrag, ObergrenzeEintrag,
    PostenEintrag, QuerkraftbewehrungEintrag, SpannungsfallEintrag, eindeutig,
)
from opencivil.projekt.lesen import (
    ProjektFehler, gebrauchsliste_roh, lagen_aus_altem_format, pflichtfeld,
    rissanforderung_aus, schalter_aus, teilungen_aus, zahl,
)


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

    haeufig: Gebrauchsliste = field(
        default_factory=lambda: Gebrauchsliste(anteil=HAEUFIG_ANTEIL))
    """Die haeufigen Lastfaelle -- fuer den Nachweis gegen Fliessen."""

    quasistaendig: Gebrauchsliste = field(
        default_factory=lambda: Gebrauchsliste(anteil=QUASISTAENDIG_ANTEIL))
    """Die quasi-staendigen Lastfaelle -- fuer die Rissbreite."""

    knickfaelle: List[KnickEintrag] = field(default_factory=list)
    """Knicknachweise; leer heisst: keiner."""

    spannungsfaelle: List[SpannungsfallEintrag] = field(default_factory=list)
    """Auswertungen am Querschnitt -- Bilder, keine Nachweise."""

    automatik_modus: str = "grund_ohne_zulage_mit"
    """Wonach das Bewehrungswerkzeug sucht -- siehe ``bewehrungssuche.Suchmodus``."""

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

    # -- Pruefen und Leeren -------------------------------------------------

    def pruefen(self) -> None:
        """
        Was an dieser Platte nicht stimmen kann, bevor daraus gerechnet wird.

        Lastfallnamen eindeutig je Liste (siehe :func:`eintraege.eindeutig`);
        die Gebrauchslisten pruefen sich selbst, samt Anteil und abgeleiteten
        Namen. Laeuft auch beim Oeffnen einer Datei -- darum hier nichts, was
        eine gespeicherte Platte unoeffenbar machte (siehe
        :meth:`masse_pruefen`).
        """
        eindeutig(self.kombinationen, self.name, "Tragsicherheitseinwirkung")
        eindeutig(self.knickfaelle, self.name, "Knicknachweis")
        eindeutig(self.spannungsfaelle, self.name, "Spannung-Dehnung-Analyse")
        for liste, wort in ((self.haeufig, "häufige"),
                            (self.quasistaendig, "quasi-ständige")):
            liste.pruefen(self.name, self.kombinationen, wort)

    def masse_pruefen(self) -> None:
        """
        Haelt unmoegliche Abmessungen auf, bevor daraus Zahlen werden.

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

        # Keine Abmessung, aber aus demselben Grund hier und nicht beim
        # Oeffnen: eine abgelegte Platte mit einer zu hohen Grenze soll sich
        # oeffnen und korrigieren lassen.
        if not 0.0 < self.x_d_max <= X_D_HOECHSTENS:
            raise ProjektFehler(
                f"Platte '{name}': max. x/d muss grösser als null und höchstens "
                f"{X_D_HOECHSTENS:g} sein, angegeben ist {self.x_d_max:g}.")

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

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "QuerschnittEintrag":
        lagen = d.get("lagen")
        if lagen is None and ("lagen_unten" in d or "lagen_oben" in d):
            lagen = lagen_aus_altem_format(d)
        kennung = pflichtfeld(d, "kennung", "Ein Querschnitt")
        return cls(
            kennung=kennung,
            name=str(d.get("name") or kennung),
            beton=pflichtfeld(d, "beton", f"Der Querschnitt '{kennung}'"),
            h=zahl(d, "h", 300.0),
            b=zahl(d, "b", 1000.0),
            ueberdeckung_unten=zahl(d, "ueberdeckung_unten", 30.0),
            ueberdeckung_oben=zahl(d, "ueberdeckung_oben", 30.0),
            d_max=zahl(d, "d_max", 32.0),
            einlagenhoehe=zahl(d, "einlagenhoehe", 0.0),
            k_c=zahl(d, "k_c", K_C),
            querkraftbewehrung=QuerkraftbewehrungEintrag.aus_dict(
                d.get("querkraftbewehrung") or {}),
            duktilitaet=schalter_aus(d.get("duktilitaet")),
            automatik_modus=str(d.get("automatik_modus")
                                 or "grund_ohne_zulage_mit"),
            automatik_y_wie_x=bool(d.get("automatik_y_wie_x", False)),
            automatik_teilungen=teilungen_aus(d.get("automatik_teilungen"),
                                               (150.0,)),
            automatik_mindestdurchmesser=zahl(
                d, "automatik_mindestdurchmesser", 10.0),
            automatik_grenze=ObergrenzeEintrag.aus_dict(d.get("automatik_grenze") or {}),
            automatik_mindestdicke=zahl(d, "automatik_mindestdicke", 150.0),
            automatik_querkraft=bool(d.get("automatik_querkraft", False)),
            automatik_querkraft_teilungen=teilungen_aus(
                d.get("automatik_querkraft_teilungen"), (100.0, 150.0, 200.0)),
            sproede=schalter_aus(d.get("sproede"), d.get("sproede_lagen")),
            zwaengung_biegung=schalter_aus(
                d.get("zwaengung_biegung"), d.get("zwaengung_biegung_lagen")),
            rissanforderung=rissanforderung_aus(d.get("rissanforderung")),
            beschreibung=str(d.get("beschreibung") or ""),
            kriechzahl=zahl(d, "kriechzahl", KRIECHZAHL),
            x_d_max=zahl(d, "x_d_max", X_D_MAX),
            # Aus x und y wird einer: nachgewiesen wird nur noch x.
            zwaengung=schalter_aus(d.get("zwaengung"), d.get("zwaengung_x"),
                                    d.get("zwaengung_y")),
            zwaengung_begrenzt=bool(d.get("zwaengung_begrenzt", False)),
            haeufig=Gebrauchsliste.aus_dict(
                gebrauchsliste_roh(d, "haeufig", "haeufige"),
                wort="häufige", vorgabe=HAEUFIG_ANTEIL),
            quasistaendig=Gebrauchsliste.aus_dict(
                gebrauchsliste_roh(d, "quasistaendig", "quasistaendige"),
                wort="quasi-ständige", vorgabe=QUASISTAENDIG_ANTEIL),
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


