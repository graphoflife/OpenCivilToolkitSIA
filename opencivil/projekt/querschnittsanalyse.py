"""
opencivil/projekt/querschnittsanalyse.py -- ein gezeichneter Querschnitt, wie die Oberflaeche ihn beschreibt.

VERANTWORTUNG:
Der :class:`QuerschnittsanalyseEintrag`: Knoten, Polygone mit Material, Staebe
und Stablinien, Schubwaende, Hilfslinien, die Wahl der Werkstoffgesetze, die
Lastfaelle und die Schalter der Nachweise -- als eine speicherbare
Datenklasse, wie die Platte in :mod:`opencivil.projekt.platte`. Dazu die
Vorlage einer frischen Analyse und ein Baukasten, der ohne Oberflaeche
zeichnet (:meth:`QuerschnittsanalyseEintrag.polygon` und folgende).

KNOTEN:
Die Elemente tragen keine eigenen Koordinaten, sie verweisen auf Knoten --
ein Polygon auf seine Ecken, ein Stab auf seine Lage, eine Linie auf Anfang
und Ende. Wer einen Knoten verschiebt, verschiebt alles, was an ihm haengt.
Jedes Element hat eine Kennung, die nie wiederkommt (:mod:`opencivil.projekt.netz`):
K fuer Knoten, F fuer Flaechen, S fuer Staebe, L fuer alle Linien.

Bis 2026-10-08 trugen die Elemente ihre Koordinaten selbst. Eine solche Datei
wird beim Oeffnen umgewandelt: gleiche Koordinaten werden ein Knoten,
Reihenfolge und Namen bleiben -- und damit jede Zahl im Bericht.

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

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from opencivil.nachweis.duktilitaet import GRENZE as X_D_MAX
from opencivil.querschnitt.geometrie import Linienart
from opencivil.querschnitt.platte import ALPHA_MAX, ALPHA_MIN, K_C
from opencivil.querschnitt import vorlagen
from opencivil.projekt.eintraege import Beschreibung, eindeutig
from opencivil.projekt.lesen import ProjektFehler, pflichtfeld, zahl
from opencivil.projekt.netz import Netz, naechste_kennung

#: Wie die Rechenwerte eines Werkstoffs heissen koennen.
WERKSTOFFSAETZE = ("bemessung", "charakteristisch")

#: Welche Spannungs-Dehnungs-Beziehung der Beton haben kann.
BETONGESETZE = ("parabel", "block")

#: Schnitte eines Buegels durch eine Schubwand: so viele Schenkel kreuzen sie.
SCHNITTE = range(1, 9)


#: Ein Punkt in mm -- oder die Kennung eines Knotens, der dort liegt.
Ort = Union[str, Sequence[float]]


def _punkt(roh: Any, wo: str) -> List[float]:
    """Ein Punkt ``[y, z]`` aus der Datei -- zwei Zahlen, sonst ein Satz, was fehlt."""
    try:
        y, z = roh
        return [float(y), float(z)]
    except (TypeError, ValueError):
        raise ProjektFehler(f"{wo}: ein Punkt muss aus zwei Zahlen bestehen, "
                            f"nicht {roh!r}.") from None


def _verweis(d: Mapping[str, Any], feld: str) -> str:
    """Die Kennung eines Knotens -- leer, wenn keine dasteht."""
    return str(d.get(feld) or "")


def _hat_koordinaten(d: Mapping[str, Any], *felder: str) -> bool:
    """Ein Element im alten Format: an der Stelle eines Verweises steht ein Punkt."""
    return any(isinstance(d.get(f), (list, tuple)) for f in felder)


# ===========================================================================
# Die Teile
# ===========================================================================


@dataclass
class KnotenEintrag(Beschreibung):
    """Ein Punkt der Zeichnung, in mm. Die Elemente verweisen mit seiner Kennung auf ihn."""

    kennung: str = ""
    y: float = 0.0
    z: float = 0.0

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "KnotenEintrag":
        return cls(kennung=str(d.get("kennung") or cls.kennung),
                   y=zahl(d, "y", cls.y), z=zahl(d, "z", cls.z))


@dataclass
class FlaecheEintrag(Beschreibung):
    """Ein Polygon des Querschnitts. Ohne Material ist es eine Aussparung."""

    kennung: str = ""
    knoten: List[str] = field(default_factory=list)
    """Die Ecken als Knoten, der Reihe nach; die erste wird am Ende nicht wiederholt."""

    material: str = ""
    """Kennung des Materials; leer heisst Aussparung."""

    @property
    def ist_aussparung(self) -> bool:
        return not self.material

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "FlaecheEintrag":
        return cls(kennung=str(d.get("kennung") or cls.kennung),
                   knoten=[str(k) for k in (d.get("knoten") or [])],
                   material=str(d.get("material") or cls.material))


@dataclass
class StabEintrag(Beschreibung):
    """Ein einzelner Bewehrungsstab, an einem Knoten."""

    kennung: str = ""
    knoten: str = ""
    durchmesser: float = 16.0
    stahl: str = ""

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "StabEintrag":
        return cls(kennung=str(d.get("kennung") or cls.kennung),
                   knoten=_verweis(d, "knoten"),
                   durchmesser=zahl(d, "durchmesser", cls.durchmesser),
                   stahl=str(d.get("stahl") or cls.stahl))


@dataclass
class StablinieEintrag(Beschreibung):
    """
    Eine Linie von Staeben -- oder eine verschmierte Stahlflaeche.

    Je Art ein eigenes Feld fuer die Menge: wer die Art wechselt und wieder
    zurueck, findet seine Zahl noch vor. Welche gilt, sagt ``art``.
    """

    kennung: str = ""
    von: str = ""
    bis: str = ""
    """Anfang und Ende als Knoten."""

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
            kennung=str(d.get("kennung") or cls.kennung),
            von=_verweis(d, "von"), bis=_verweis(d, "bis"),
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

    kennung: str = ""
    von: str = ""
    bis: str = ""
    """Anfang und Ende als Knoten. Die Richtung zaehlt: sie gibt dem Schubfluss sein Vorzeichen."""

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
            kennung=str(d.get("kennung") or cls.kennung),
            von=_verweis(d, "von"), bis=_verweis(d, "bis"),
            dicke=zahl(d, "dicke", cls.dicke),
            durchmesser=zahl(d, "durchmesser", cls.durchmesser),
            teilung=zahl(d, "teilung", cls.teilung),
            schnitte=schnitte,
            stahl=str(d.get("stahl") or cls.stahl),
        )


@dataclass
class HilfslinieEintrag(Beschreibung):
    """
    Eine Linie, die nur der Konstruktion dient: an ihr fangen, an ihr messen.
    Gerechnet wird mit ihr nicht. Geschlossene Hilfslinien lassen sich im
    Zeichenfenster zu einer Flaeche machen.
    """

    kennung: str = ""
    von: str = ""
    bis: str = ""

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "HilfslinieEintrag":
        return cls(kennung=str(d.get("kennung") or cls.kennung),
                   von=_verweis(d, "von"), bis=_verweis(d, "bis"))


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
    Kennung ist die des Elements (``F1``, ``L4``); an ihr erkennt die
    Oberflaeche, welches gemeint ist. Die Namen werden hier vergeben und
    nirgends sonst -- vorher entstanden sie an fuenf Stellen.

    Ein Element, das auf einen Knoten verweist, den es nicht gibt, steht in
    keiner Liste, sondern in ``fehler``. Sein Name bleibt reserviert: die
    Elemente danach heissen weiter so wie vorher.
    """

    polygone: List[dict]
    """Je Polygon ``punkte`` und ``material`` (leer: Aussparung)."""

    staebe: List[dict]
    """Je Stab ``lage``, ``durchmesser`` und ``stahl``."""

    linien: List[dict]
    """Je Stablinie die Felder der Beschreibung, ``von`` und ``bis`` als Punkte."""

    waende: List[dict]
    """Je Schubwand die Felder der Beschreibung, ``von`` und ``bis`` als Punkte."""

    hilfslinien: List[dict] = field(default_factory=list)
    """Je Hilfslinie ``von`` und ``bis`` -- gerechnet wird mit ihnen nichts."""

    fehler: List[dict] = field(default_factory=list)
    """Was sich nicht aufloesen liess: ``text`` und ``elemente`` (Kennungen), wie eine Meldung."""


# ===========================================================================
# Die Analyse
# ===========================================================================


@dataclass
class QuerschnittsanalyseEintrag(Beschreibung):
    """Ein gezeichneter Querschnitt mit Bewehrung, Schubwaenden und Lastfaellen."""

    kennung: str
    name: str
    knoten: List[KnotenEintrag] = field(default_factory=list)
    flaechen: List[FlaecheEintrag] = field(default_factory=list)
    staebe: List[StabEintrag] = field(default_factory=list)
    stablinien: List[StablinieEintrag] = field(default_factory=list)
    schubwaende: List[SchubwandEintrag] = field(default_factory=list)
    hilfslinien: List[HilfslinieEintrag] = field(default_factory=list)
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
        lage: Dict[str, Tuple[float, float]] = {}
        for k in self.knoten:
            lage.setdefault(k.kennung, (k.y, k.z))
        fehler: List[dict] = []
        gesehen: Dict[str, str] = {}

        def benannt(name: str, kennung: str, **felder: Any) -> dict:
            return {"name": name, "kennung": kennung or name, **felder}

        def doppelt(name: str, kennung: str) -> None:
            if not kennung:
                return
            if kennung in gesehen:
                fehler.append({"text": f"{name} und {gesehen[kennung]} haben dieselbe "
                                       f"Kennung '{kennung}'.", "elemente": [kennung]})
            gesehen.setdefault(kennung, name)

        def orte(name: str, kennung: str, *verweise: str) -> Optional[List[Tuple[float, float]]]:
            """Die Lagen der Knoten -- oder ``None`` und ein Satz, welcher fehlt."""
            doppelt(name, kennung)
            for v in verweise:
                if not isinstance(v, str):
                    # Von Hand gebaut, mit einem Punkt statt eines Knotens.
                    fehler.append({"text": f"{name} verweist mit {v!r} statt mit der Kennung "
                                           f"eines Knotens -- gezeichnet wird mit dem "
                                           f"Baukasten (polygon, stab, stablinie, …).",
                                   "elemente": [kennung or name]})
                    return None
                if v not in lage:
                    fehler.append({"text": f"{name}: den Knoten '{v or '?'}' gibt es nicht.",
                                   "elemente": [kennung or name]})
                    return None
            return [lage[v] for v in verweise]

        polygone, staebe, linien, waende, hilfslinien = [], [], [], [], []
        for i, f in enumerate(self.flaechen, start=1):
            name = f"{'Polygon' if f.material else 'Aussparung'} {i}"
            ecken = orte(name, f.kennung, *f.knoten)
            if ecken is not None:
                polygone.append(benannt(name, f.kennung, punkte=tuple(ecken),
                                        material=f.material))
        for i, s in enumerate(self.staebe, start=1):
            name = f"Stab {i}"
            ort = orte(name, s.kennung, s.knoten)
            if ort is not None:
                staebe.append(benannt(name, s.kennung, lage=ort[0],
                                      durchmesser=s.durchmesser, stahl=s.stahl))
        for i, l in enumerate(self.stablinien, start=1):
            name = f"Linie {i}"
            ende = orte(name, l.kennung, l.von, l.bis)
            if ende is not None:
                linien.append(benannt(
                    name, l.kennung, von=ende[0], bis=ende[1], art=l.art,
                    durchmesser=l.durchmesser, flaeche=l.flaeche, anzahl=l.anzahl,
                    teilung=l.teilung, starteisen=l.starteisen, endeisen=l.endeisen,
                    stahl=l.stahl))
        for i, w in enumerate(self.schubwaende, start=1):
            name = f"Wand {i}"
            ende = orte(name, w.kennung, w.von, w.bis)
            if ende is not None:
                waende.append(benannt(
                    name, w.kennung, von=ende[0], bis=ende[1], dicke=w.dicke,
                    durchmesser=w.durchmesser, teilung=w.teilung, schnitte=w.schnitte,
                    stahl=w.stahl))
        for i, h in enumerate(self.hilfslinien, start=1):
            name = f"Hilfslinie {i}"
            ende = orte(name, h.kennung, h.von, h.bis)
            if ende is not None:
                hilfslinien.append(benannt(name, h.kennung, von=ende[0], bis=ende[1]))
        return Elemente(polygone=polygone, staebe=staebe, linien=linien, waende=waende,
                        hilfslinien=hilfslinien, fehler=fehler)

    # -- Zeichnen ohne Oberflaeche -------------------------------------------

    def netz(self) -> Netz:
        """Die Knoten zum Weiterzeichnen: gleiche Koordinaten sind ein Knoten."""
        return Netz(self.knoten, neu=lambda kennung, y, z: KnotenEintrag(kennung, y, z))

    def _knoten(self, netz: Netz, ort: Ort) -> str:
        """Ein Knoten aus einem Punkt ``[y, z]`` -- oder die Kennung, wenn schon eine dasteht."""
        if isinstance(ort, str):
            return ort
        y, z = _punkt(ort, f"Querschnitt '{self.name}'")
        return netz.an(y, z)

    def _kennung(self, vorsilbe: str) -> str:
        """Die naechste Kennung -- alle Linien zaehlen gemeinsam, ob Bewehrung, Wand oder Hilfslinie."""
        listen = {"F": [self.flaechen], "S": [self.staebe],
                  "L": [self.stablinien, self.schubwaende, self.hilfslinien]}[vorsilbe]
        return naechste_kennung((e.kennung for liste in listen for e in liste), vorsilbe)

    def polygon(self, punkte: Sequence[Ort], material: str = "") -> FlaecheEintrag:
        """Ein Polygon aus Ecken ``[y, z]`` in mm; ohne Material eine Aussparung."""
        netz = self.netz()
        eintrag = FlaecheEintrag(kennung=self._kennung("F"),
                                 knoten=[self._knoten(netz, p) for p in punkte],
                                 material=material)
        self.flaechen.append(eintrag)
        return eintrag

    def stab(self, y: float, z: float, **felder: Any) -> StabEintrag:
        """Ein einzelner Stab bei ``(y, z)`` -- ``durchmesser``, ``stahl``."""
        eintrag = StabEintrag(kennung=self._kennung("S"),
                              knoten=self._knoten(self.netz(), (y, z)), **felder)
        self.staebe.append(eintrag)
        return eintrag

    def stablinie(self, von: Ort, bis: Ort, **felder: Any) -> StablinieEintrag:
        """Eine Stablinie; die Felder wie :class:`StablinieEintrag`."""
        netz = self.netz()
        eintrag = StablinieEintrag(kennung=self._kennung("L"), von=self._knoten(netz, von),
                                   bis=self._knoten(netz, bis), **felder)
        self.stablinien.append(eintrag)
        return eintrag

    def schubwand(self, von: Ort, bis: Ort, **felder: Any) -> SchubwandEintrag:
        """Eine Schubwand; die Felder wie :class:`SchubwandEintrag`."""
        netz = self.netz()
        eintrag = SchubwandEintrag(kennung=self._kennung("L"), von=self._knoten(netz, von),
                                   bis=self._knoten(netz, bis), **felder)
        self.schubwaende.append(eintrag)
        return eintrag

    def hilfslinie(self, von: Ort, bis: Ort) -> HilfslinieEintrag:
        """Eine Hilfslinie -- nur zum Konstruieren, gerechnet wird mit ihr nicht."""
        netz = self.netz()
        eintrag = HilfslinieEintrag(kennung=self._kennung("L"), von=self._knoten(netz, von),
                                    bis=self._knoten(netz, bis))
        self.hilfslinien.append(eintrag)
        return eintrag

    def lage(self, kennung: str) -> Optional[Tuple[float, float]]:
        """Wo ein Knoten liegt, in mm -- ``None``, wenn es ihn nicht gibt."""
        return self.netz().lage(kennung)

    def vorlage_einsetzen(self, schluessel: str, *, beton: str, stahl: str,
                          masse: Optional[Mapping[str, float]] = None,
                          randabstand: float = 50.0, bewehrung: bool = True,
                          schubwaende: bool = True,
                          ursprung: Tuple[float, float] = (0.0, 0.0)) -> List[str]:
        """
        Setzt eine Vorlage ein (:mod:`opencivil.querschnitt.vorlagen`) -- dazu,
        nicht anstatt: was schon gezeichnet ist, bleibt, und wo ein Punkt der
        Vorlage genau auf einem Knoten liegt, haengt sie an ihm. ``ursprung``
        ist, wohin ihre Ecke unten links kommt; die Lagen auf einen
        Millionstel Millimeter wie im Zeichenfenster, damit die Summe keinen
        Rundungsrest behaelt. Gibt die Kennungen der neuen Elemente zurueck.
        Passen die Masse nicht zueinander, ein ``ValueError`` mit dem Grund.
        """
        teile = vorlagen.vorlage(schluessel).bauen(masse, randabstand, bewehrung, schubwaende)
        dy, dz = float(ursprung[0]), float(ursprung[1])

        def an(p: Sequence[float]) -> List[float]:
            return [round(p[0] + dy, 6), round(p[1] + dz, 6)]

        neu: List[str] = []
        for f in teile.polygone:
            neu.append(self.polygon([an(p) for p in f["punkte"]],
                                    material="" if f["aussparung"] else beton).kennung)
        for s in teile.staebe:
            neu.append(self.stab(*an(s["lage"]), durchmesser=s["durchmesser"], stahl=stahl).kennung)
        for l in teile.stablinien:
            felder = {k: v for k, v in l.items() if k not in ("von", "bis")}
            neu.append(self.stablinie(an(l["von"]), an(l["bis"]), stahl=stahl, **felder).kennung)
        for w in teile.schubwaende:
            neu.append(self.schubwand(an(w["von"]), an(w["bis"]), dicke=w["dicke"],
                                      stahl=stahl).kennung)
        return neu

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
        a = cls(kennung=kennung, name=name,
                lastfaelle=[QALastfallEintrag(name="Tragsicherheit 1", M_y_Ed=100.0)])
        a.vorlage_einsetzen("rechteck", beton=beton, stahl=stahl, schubwaende=False)
        return a

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "QuerschnittsanalyseEintrag":
        kennung = pflichtfeld(d, "kennung", "Eine Querschnittsanalyse")
        a = cls(
            kennung=kennung,
            name=str(d.get("name") or kennung),
            knoten=[KnotenEintrag.aus_dict(x) for x in (d.get("knoten") or [])],
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
        a._elemente_lesen(d)
        return a

    def _elemente_lesen(self, d: Mapping[str, Any]) -> None:
        """
        Die Elemente aus der Datei -- jedes im heutigen Format mit Verweisen,
        oder im alten mit eigenen Koordinaten. Ein altes wird ueber den
        Baukasten angelegt, wie es heute gezeichnet wuerde: seine Punkte
        werden Knoten, gleiche Koordinaten derselbe. Die Reihenfolge bleibt,
        und mit ihr jeder Name im Bericht.
        """
        for roh in d.get("flaechen") or []:
            if "punkte" in roh:
                self.polygon([_punkt(p, "Ein Polygon") for p in roh.get("punkte") or []],
                             material=str(roh.get("material") or ""))
            else:
                self.flaechen.append(FlaecheEintrag.aus_dict(roh))
        for roh in d.get("staebe") or []:
            if "knoten" not in roh and ("y" in roh or "z" in roh):
                gelesen = StabEintrag.aus_dict(roh)
                self.stab(zahl(roh, "y", 0.0), zahl(roh, "z", 0.0),
                          durchmesser=gelesen.durchmesser, stahl=gelesen.stahl)
            else:
                self.staebe.append(StabEintrag.aus_dict(roh))
        for liste, klasse, anlegen, wo in (
                ("stablinien", StablinieEintrag, self.stablinie, "Eine Stablinie"),
                ("schubwaende", SchubwandEintrag, self.schubwand, "Eine Schubwand"),
                ("hilfslinien", HilfslinieEintrag, self.hilfslinie, "Eine Hilfslinie")):
            for roh in d.get(liste) or []:
                if not _hat_koordinaten(roh, "von", "bis"):
                    getattr(self, liste).append(klasse.aus_dict(roh))
                    continue
                felder = asdict(klasse.aus_dict({**roh, "von": "", "bis": ""}))
                for weg in ("kennung", "von", "bis"):
                    felder.pop(weg)
                anlegen(_punkt(roh.get("von"), wo), _punkt(roh.get("bis"), wo), **felder)
