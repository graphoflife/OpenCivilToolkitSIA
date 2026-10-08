"""
opencivil/projekt/querschnittsanalyse.py -- ein gezeichneter Querschnitt, wie die Oberflaeche ihn beschreibt.

VERANTWORTUNG:
Der :class:`QuerschnittsanalyseEintrag`: Polygone mit Material, Staebe und
Stablinien, Schubwaende, die Wahl der Werkstoffgesetze, die Lastfaelle und die
Schalter der Nachweise -- als eine speicherbare Datenklasse, wie die Platte in
:mod:`opencivil.projekt.platte`. Dazu die Vorlage einer frischen Analyse.

KOORDINATEN UND EINHEITEN:
y nach rechts, z nach oben, alles in Millimetern -- so, wie gezeichnet und
eingetippt wird. Schnittgroessen in kN und kNm. Umgerechnet wird beim Bauen.

VORZEICHEN DER LASTFAELLE:
N > 0 Zug. Ein positives Moment zieht auf der negativen Seite seiner Achse:
M_y > 0 unten (wie bei der Platte), M_z > 0 links. V_y und V_z wirken in
Achsrichtung, T im Gegenuhrzeigersinn.

WAS HIER NICHT GEPRUEFT WIRD:
Ob die Polygone sich ueberlappen, ob ein Stab im Beton liegt: das prueft der
Aufbau. Eine abgelegte Analyse mit einem verunglueckten Polygon soll sich
oeffnen und korrigieren lassen -- dasselbe Vorgehen wie bei den Abmessungen
der Platte (:meth:`QuerschnittEintrag.masse_pruefen`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Mapping

from opencivil.nachweis.duktilitaet import GRENZE as X_D_MAX
from opencivil.querschnitt.geometrie import Linienart
from opencivil.querschnitt.platte import ALPHA_MAX, ALPHA_MIN, K_C
from opencivil.projekt.eintraege import Beschreibung, eindeutig
from opencivil.projekt.lesen import ProjektFehler, pflichtfeld, vorgabe, zahl

#: Wie die Rechenwerte eines Werkstoffs heissen koennen.
WERKSTOFFSAETZE = ("bemessung", "charakteristisch")

#: Welche Spannungs-Dehnungs-Beziehung der Beton haben kann.
BETONGESETZE = ("parabel", "block")

#: Schnitte eines Buegels durch eine Schubwand: so viele Schenkel kreuzen sie.
SCHNITTE = range(1, 9)


def _punkt(roh: Any, wo: str) -> List[float]:
    """Ein Punkt ``[y, z]`` aus der Datei -- zwei Zahlen, sonst ein Satz, was fehlt."""
    try:
        y, z = roh
        return [float(y), float(z)]
    except (TypeError, ValueError):
        raise ProjektFehler(f"{wo}: ein Punkt muss aus zwei Zahlen bestehen, "
                            f"nicht {roh!r}.") from None


# ===========================================================================
# Die Teile
# ===========================================================================


@dataclass
class FlaecheEintrag(Beschreibung):
    """Ein Polygon des Querschnitts. Ohne Material ist es eine Aussparung."""

    punkte: List[List[float]] = field(default_factory=list)
    """Die Ecken ``[y, z]`` in mm, die erste wird am Ende nicht wiederholt."""

    material: str = ""
    """Kennung des Materials; leer heisst Aussparung."""

    @property
    def ist_aussparung(self) -> bool:
        return not self.material

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "FlaecheEintrag":
        return cls(punkte=[_punkt(p, "Ein Polygon") for p in (d.get("punkte") or [])],
                   material=str(d.get("material") or cls.material))


@dataclass
class StabEintrag(Beschreibung):
    """Ein einzelner Bewehrungsstab."""

    y: float = 0.0
    z: float = 0.0
    durchmesser: float = 16.0
    stahl: str = ""

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "StabEintrag":
        return cls(y=zahl(d, "y", cls.y), z=zahl(d, "z", cls.z),
                   durchmesser=zahl(d, "durchmesser", cls.durchmesser),
                   stahl=str(d.get("stahl") or cls.stahl))


@dataclass
class StablinieEintrag(Beschreibung):
    """
    Eine Linie von Staeben -- oder eine verschmierte Stahlflaeche.

    Je Art ein eigenes Feld fuer die Menge: wer die Art wechselt und wieder
    zurueck, findet seine Zahl noch vor. Welche gilt, sagt ``art``.
    """

    von: List[float] = field(default_factory=lambda: [0.0, 0.0])
    bis: List[float] = field(default_factory=lambda: [1000.0, 0.0])
    art: str = Linienart.TEILUNG.value
    durchmesser: float = 16.0
    """Bei Anzahl und Teilung der Stabdurchmesser in mm."""

    flaeche: float = 1000.0
    """Bei Art «Fläche» die ganze Stahlflaeche der Linie in mm²."""

    anzahl: float = 5.0
    teilung: float = 150.0
    """Bei Art «Teilung» der Wunschabstand in mm -- gerundet auf einen, der aufgeht."""

    starteisen: bool = True
    endeisen: bool = True
    stahl: str = ""

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "StablinieEintrag":
        art = str(d.get("art") or cls.art)
        if art not in {a.value for a in Linienart}:
            raise ProjektFehler(
                f"Unbekannte Art einer Stablinie '{art}'. Möglich sind: "
                f"{', '.join(a.value for a in Linienart)}.")
        return cls(
            von=_punkt(d.get("von") or vorgabe(cls, "von"), "Eine Stablinie"),
            bis=_punkt(d.get("bis") or vorgabe(cls, "bis"), "Eine Stablinie"),
            art=art,
            durchmesser=zahl(d, "durchmesser", cls.durchmesser),
            flaeche=zahl(d, "flaeche", cls.flaeche),
            anzahl=zahl(d, "anzahl", cls.anzahl),
            teilung=zahl(d, "teilung", cls.teilung),
            starteisen=bool(d.get("starteisen", cls.starteisen)),
            endeisen=bool(d.get("endeisen", cls.endeisen)),
            stahl=str(d.get("stahl") or cls.stahl),
        )


@dataclass
class SchubwandEintrag(Beschreibung):
    """
    Eine Schubwand: eine Linie ueber dem Querschnitt, mit Dicke und Buegeln.

    Ihre Laenge ist der Hebelarm des Fachwerks -- gezeichnet wird sie darum
    von Gurt zu Gurt. Die Teilung ``s`` gilt in Laengsrichtung des Bauteils;
    im Schnitt ist sie nicht zu sehen.
    """

    von: List[float] = field(default_factory=lambda: [0.0, 0.0])
    bis: List[float] = field(default_factory=lambda: [0.0, 500.0])
    dicke: float = 200.0
    """``b_w`` in mm."""

    durchmesser: float = 10.0
    """Buegeldurchmesser in mm."""

    teilung: float = 150.0
    """Buegelteilung in Laengsrichtung in mm."""

    schnitte: int = 2
    """Wie viele Buegelschenkel die Wand kreuzen, 1 bis 8."""

    stahl: str = ""

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "SchubwandEintrag":
        schnitte = int(zahl(d, "schnitte", cls.schnitte))
        if schnitte not in SCHNITTE:
            raise ProjektFehler(
                f"Eine Schubwand hat {schnitte} Schnitte. Möglich sind "
                f"{SCHNITTE.start} bis {SCHNITTE.stop - 1}.")
        return cls(
            von=_punkt(d.get("von") or vorgabe(cls, "von"), "Eine Schubwand"),
            bis=_punkt(d.get("bis") or vorgabe(cls, "bis"), "Eine Schubwand"),
            dicke=zahl(d, "dicke", cls.dicke),
            durchmesser=zahl(d, "durchmesser", cls.durchmesser),
            teilung=zahl(d, "teilung", cls.teilung),
            schnitte=schnitte,
            stahl=str(d.get("stahl") or cls.stahl),
        )


@dataclass
class QALastfallEintrag(Beschreibung):
    """Ein Lastfall der Querschnittsanalyse -- kN und kNm, Vorzeichen siehe oben."""

    name: str
    N_Ed: float = 0.0
    M_y_Ed: float = 0.0
    M_z_Ed: float = 0.0
    V_y_Ed: float = 0.0
    V_z_Ed: float = 0.0
    T_Ed: float = 0.0
    aktiv: bool = True

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "QALastfallEintrag":
        return cls(
            name=pflichtfeld(d, "name", "Ein Lastfall"),
            N_Ed=zahl(d, "N_Ed", cls.N_Ed),
            M_y_Ed=zahl(d, "M_y_Ed", cls.M_y_Ed),
            M_z_Ed=zahl(d, "M_z_Ed", cls.M_z_Ed),
            V_y_Ed=zahl(d, "V_y_Ed", cls.V_y_Ed),
            V_z_Ed=zahl(d, "V_z_Ed", cls.V_z_Ed),
            T_Ed=zahl(d, "T_Ed", cls.T_Ed),
            aktiv=bool(d.get("aktiv", cls.aktiv)),
        )


@dataclass
class WerkstoffwahlEintrag(Beschreibung):
    """
    Mit welchen Werten ein Material in dieser Analyse rechnet.

    ``satz``: Bemessungs- oder charakteristische Werte -- das legt fest, wo
    die Plateaus liegen (``f_cd`` oder ``f_ck``, ``f_yd`` oder ``f_yk``).
    ``betongesetz``: beim Beton die Parabel-Rechteck-Beziehung oder der
    vereinfachte Spannungsblock 0.85·x.
    """

    material: str
    satz: str = WERKSTOFFSAETZE[0]
    betongesetz: str = BETONGESETZE[0]

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "WerkstoffwahlEintrag":
        satz = str(d.get("satz") or cls.satz)
        gesetz = str(d.get("betongesetz") or cls.betongesetz)
        if satz not in WERKSTOFFSAETZE:
            raise ProjektFehler(f"Unbekannte Rechenwerte '{satz}'. Möglich sind: "
                                f"{', '.join(WERKSTOFFSAETZE)}.")
        if gesetz not in BETONGESETZE:
            raise ProjektFehler(f"Unbekanntes Betongesetz '{gesetz}'. Möglich sind: "
                                f"{', '.join(BETONGESETZE)}.")
        return cls(material=pflichtfeld(d, "material", "Eine Werkstoffwahl"),
                   satz=satz, betongesetz=gesetz)


# ===========================================================================
# Die Elemente, wie der Kern sie sieht
# ===========================================================================


@dataclass(frozen=True)
class Elemente:
    """
    Die Elemente einer Analyse, so wie der Kern sie prueft und rechnet:
    Koordinaten in mm, und je Element ``name`` und ``kennung``.

    Der Name zaehlt je Art ab 1 -- «Polygon 1», «Aussparung 2», «Stab 1»,
    «Linie 1», «Wand 3» -- und steht so in Berichten und Meldungen. Die
    Kennung sagt der Oberflaeche, welches Element gemeint ist; bis die
    Elemente eigene Kennungen tragen, ist sie der Name. Vergeben werden beide
    hier und nirgends sonst -- vorher entstanden die Namen an fuenf Stellen.
    """

    polygone: List[dict]
    """Je Polygon ``punkte`` und ``material`` (leer: Aussparung)."""

    staebe: List[dict]
    """Je Stab ``lage``, ``durchmesser`` und ``stahl``."""

    linien: List[dict]
    """Je Stablinie die Felder der Beschreibung, ``von`` und ``bis`` als Punkte."""

    waende: List[dict]
    """Je Schubwand die Felder der Beschreibung, ``von`` und ``bis`` als Punkte."""


# ===========================================================================
# Die Analyse
# ===========================================================================


@dataclass
class QuerschnittsanalyseEintrag(Beschreibung):
    """Ein gezeichneter Querschnitt mit Bewehrung, Schubwaenden und Lastfaellen."""

    kennung: str
    name: str
    flaechen: List[FlaecheEintrag] = field(default_factory=list)
    staebe: List[StabEintrag] = field(default_factory=list)
    stablinien: List[StablinieEintrag] = field(default_factory=list)
    schubwaende: List[SchubwandEintrag] = field(default_factory=list)
    werkstoffwahl: List[WerkstoffwahlEintrag] = field(default_factory=list)
    """Je Material eine Wahl; fehlt eine, gelten die Vorgaben."""

    lastfaelle: List[QALastfallEintrag] = field(default_factory=list)

    einachsig: bool = False
    """
    Nur Biegung um y: die Nulllinie bleibt waagrecht, M_z und V_y zaehlen
    nicht, und Duktilitaet und sproedes Versagen gibt es nur in y. Torsion
    bleibt. Bei einem unsymmetrischen Querschnitt ist das eine Naeherung --
    dasselbe, was die Platte immer tut.
    """

    alpha_min: int = ALPHA_MIN
    alpha_max: int = ALPHA_MAX
    k_c: float = K_C
    """Grenzen der Druckfeldneigung und Abminderung der Druckdiagonalen -- wie bei der Platte."""

    laengszugkraft: bool = False
    """
    Ob die Laengszugkraft aus Querkraft und Torsion in den M-N-Nachweis
    eingeht: das Druckfeld jeder Schubwand braucht in Laengsrichtung Zug.
    """

    duktilitaet: bool = False
    x_d_max: float = X_D_MAX
    sproede: bool = False

    beschreibung: str = ""
    """Freier Text -- geht in keine Rechnung ein, wie bei der Platte."""

    def wahl(self, material: str) -> WerkstoffwahlEintrag:
        """Die Wahl fuer dieses Material -- die Vorgaben, wenn keine dasteht."""
        for w in self.werkstoffwahl:
            if w.material == material:
                return w
        return WerkstoffwahlEintrag(material=material)

    def materialien(self) -> List[str]:
        """Jedes Material, das die Analyse benutzt, in der Reihenfolge des ersten Auftretens."""
        gesehen: List[str] = []
        for kennung in ([f.material for f in self.flaechen]
                        + [s.stahl for s in self.staebe]
                        + [l.stahl for l in self.stablinien]
                        + [w.stahl for w in self.schubwaende]):
            if kennung and kennung not in gesehen:
                gesehen.append(kennung)
        return gesehen

    def elemente(self) -> Elemente:
        """Die Elemente mit Name und Kennung, Koordinaten in mm -- siehe :class:`Elemente`."""
        def benannt(name: str, **felder: Any) -> dict:
            return {"name": name, "kennung": name, **felder}

        return Elemente(
            polygone=[benannt(f"{'Polygon' if f.material else 'Aussparung'} {i}",
                              punkte=tuple(tuple(p) for p in f.punkte), material=f.material)
                      for i, f in enumerate(self.flaechen, start=1)],
            staebe=[benannt(f"Stab {i}", lage=(s.y, s.z), durchmesser=s.durchmesser,
                            stahl=s.stahl)
                    for i, s in enumerate(self.staebe, start=1)],
            linien=[benannt(f"Linie {i}", von=tuple(l.von), bis=tuple(l.bis), art=l.art,
                            durchmesser=l.durchmesser, flaeche=l.flaeche, anzahl=l.anzahl,
                            teilung=l.teilung, starteisen=l.starteisen, endeisen=l.endeisen,
                            stahl=l.stahl)
                    for i, l in enumerate(self.stablinien, start=1)],
            waende=[benannt(f"Wand {i}", von=tuple(w.von), bis=tuple(w.bis), dicke=w.dicke,
                            durchmesser=w.durchmesser, teilung=w.teilung,
                            schnitte=w.schnitte, stahl=w.stahl)
                    for i, w in enumerate(self.schubwaende, start=1)],
        )

    def pruefen(self) -> None:
        """Was sich schon an der Beschreibung pruefen laesst: eindeutige Lastfallnamen."""
        eindeutig(self.lastfaelle, self.name, "Lastfall", bauteil="Querschnitt")

    def lastfall(self, name: str, **werte: float) -> QALastfallEintrag:
        """Einen Lastfall anfuegen, ohne Oberflaeche -- kN und kNm."""
        eintrag = QALastfallEintrag(name=name, **werte)
        self.lastfaelle.append(eintrag)
        return eintrag

    @classmethod
    def neu(cls, kennung: str, name: str, beton: str, stahl: str) -> "QuerschnittsanalyseEintrag":
        """
        Eine frische Analyse, wie der Benutzer sie angelegt bekommt.

        Ein Rechteck 300 × 600 mm, unten drei, oben zwei Staebe, und ein
        Lastfall mit Feldmoment. Zum Anfangen, nicht als Vorgabe: gezeichnet
        wird danach, was man braucht.
        """
        return cls(
            kennung=kennung,
            name=name,
            flaechen=[FlaecheEintrag(
                punkte=[[0.0, 0.0], [300.0, 0.0], [300.0, 600.0], [0.0, 600.0]],
                material=beton)],
            stablinien=[
                StablinieEintrag(von=[50.0, 50.0], bis=[250.0, 50.0],
                                 art=Linienart.ANZAHL.value, durchmesser=20.0,
                                 anzahl=3.0, stahl=stahl),
                StablinieEintrag(von=[50.0, 550.0], bis=[250.0, 550.0],
                                 art=Linienart.ANZAHL.value, durchmesser=12.0,
                                 anzahl=2.0, stahl=stahl),
            ],
            lastfaelle=[QALastfallEintrag(name="Tragsicherheit 1", M_y_Ed=100.0)],
        )

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "QuerschnittsanalyseEintrag":
        kennung = pflichtfeld(d, "kennung", "Eine Querschnittsanalyse")
        return cls(
            kennung=kennung,
            name=str(d.get("name") or kennung),
            flaechen=[FlaecheEintrag.aus_dict(x) for x in (d.get("flaechen") or [])],
            staebe=[StabEintrag.aus_dict(x) for x in (d.get("staebe") or [])],
            stablinien=[StablinieEintrag.aus_dict(x) for x in (d.get("stablinien") or [])],
            schubwaende=[SchubwandEintrag.aus_dict(x) for x in (d.get("schubwaende") or [])],
            werkstoffwahl=[WerkstoffwahlEintrag.aus_dict(x)
                           for x in (d.get("werkstoffwahl") or [])],
            lastfaelle=[QALastfallEintrag.aus_dict(x) for x in (d.get("lastfaelle") or [])],
            einachsig=bool(d.get("einachsig", cls.einachsig)),
            alpha_min=int(zahl(d, "alpha_min", cls.alpha_min)),
            alpha_max=int(zahl(d, "alpha_max", cls.alpha_max)),
            k_c=zahl(d, "k_c", cls.k_c),
            laengszugkraft=bool(d.get("laengszugkraft", cls.laengszugkraft)),
            duktilitaet=bool(d.get("duktilitaet", cls.duktilitaet)),
            x_d_max=zahl(d, "x_d_max", cls.x_d_max),
            sproede=bool(d.get("sproede", cls.sproede)),
            beschreibung=str(d.get("beschreibung") or cls.beschreibung),
        )
