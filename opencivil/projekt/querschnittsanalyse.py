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
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from opencivil.nachweis.duktilitaet import GRENZE as X_D_MAX
from opencivil.nachweis.rechenwahl import FASERARTEN, FASERSPANNUNGSARTEN, VERFORMUNGSARTEN
from opencivil.querschnitt.geometrie import Linienart
from opencivil.querschnitt.platte import ALPHA_MAX, ALPHA_MIN, K_C
from opencivil.querschnitt import vorlagen
from opencivil.querschnitt.schnittanalyse import Zugseite
from opencivil.projekt.eintraege import (
    BETONGESETZE, HAEUFIG_ANTEIL, QUASISTAENDIG_ANTEIL, WERKSTOFFSAETZE, Beschreibung,
    Gebrauchsliste, KnickEintrag, RechenwahlEintrag, SpannungsfallEintrag, eindeutig,
)
from opencivil.projekt.lesen import RISSANFORDERUNGEN, ProjektFehler, einer_von, nicht_negativ
from opencivil.projekt.netz import Netz, naechste_kennung

#: Schnitte eines Buegels durch eine Schubwand: so viele Schenkel kreuzen sie.
SCHNITTE = range(1, 9)

#: Die Zugseiten eines gezeichneten Querschnitts.
ZUGSEITEN = tuple(z.value for z in Zugseite)


#: Ein Punkt in mm -- oder die Kennung eines Knotens, der dort liegt.
Ort = Union[str, Sequence[float]]


def _punkt(roh: Any, wo: str) -> List[float]:
    """Ein Punkt ``[y, z]`` -- zwei Zahlen, sonst ein Satz, was fehlt."""
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
class KnotenEintrag(Beschreibung):
    """Ein Punkt der Zeichnung, in mm. Die Elemente verweisen mit seiner Kennung auf ihn."""

    kennung: str = ""
    y: float = 0.0
    z: float = 0.0


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


@dataclass
class StabEintrag(Beschreibung):
    """Ein einzelner Bewehrungsstab, an einem Knoten."""

    kennung: str = ""
    knoten: str = ""
    durchmesser: float = 16.0
    stahl: str = ""


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

    art: str = einer_von((a.value for a in Linienart), Linienart.TEILUNG.value)
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

    schnitte: int = einer_von(SCHNITTE, 2)
    """Wie viele Buegelschenkel die Wand kreuzen, 1 bis 8."""

    stahl: str = ""


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


@dataclass
class QAGebrauchsfallEintrag(Beschreibung):
    """
    Ein Lastfall unter Gebrauchslast -- wie ein Lastfall der Tragsicherheit,
    ohne Querkraft und Torsion: begrenzt wird die Stahlspannung, und dafuer
    zaehlen N und die Momente. kN und kNm, Vorzeichen siehe oben.
    """

    name: str
    N_Ed: float = 0.0
    M_y_Ed: float = 0.0
    M_z_Ed: float = 0.0
    aktiv: bool = True


@dataclass
class QAGebrauchsliste(Gebrauchsliste):
    """
    Die Lastfaelle einer Stahlspannung am gezeichneten Querschnitt: dieselbe
    Liste wie bei der Platte, mit N, M_y und M_z je Fall, abgeleitet aus den
    Lastfaellen der Tragsicherheit. Gerechnet wird ueber die Fasern -- eine
    Handrechnung gibt es hier nicht.
    """

    FALL = QAGebrauchsfallEintrag
    ARTEN = FASERSPANNUNGSARTEN
    BAUTEIL = "Querschnitt"

    faelle: List[QAGebrauchsfallEintrag] = field(default_factory=list)


@dataclass
class QAKnickEintrag(KnickEintrag):
    """
    Ein Knicknachweis des gezeichneten Querschnitts -- wie bei der Platte,
    dazu die Zugseite: die Seite, zu der sich der Stab biegt und die das
    Moment 1. Ordnung zieht (:class:`~opencivil.querschnitt.schnittanalyse.Zugseite`).
    """

    richtung: str = einer_von(ZUGSEITEN, Zugseite.UNTEN.value)


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
    satz: str = einer_von(WERKSTOFFSAETZE, WERKSTOFFSAETZE[0])
    betongesetz: str = einer_von(BETONGESETZE, BETONGESETZE[0])


@dataclass
class QASpannungsfallEintrag(SpannungsfallEintrag):
    """
    Eine Spannung-Dehnung-Analyse des gezeichneten Querschnitts -- dieselben
    Felder wie bei der Platte. Die Richtung ist hier die Zugseite: die Seite,
    die ein positives Moment zieht (:class:`~opencivil.querschnitt.schnittanalyse.Zugseite`).
    """

    richtung: str = einer_von(ZUGSEITEN, Zugseite.UNTEN.value)


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

    BEZEICHNUNG = "Querschnitt"

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

    rissanforderung: str = einer_von(RISSANFORDERUNGEN, "normal")
    """Anforderung an die Rissbildung -- ``normal``, ``erhoeht`` oder ``hoch``, wie bei der Platte."""

    zwaengung: bool = False
    """Ob die Zwaengung auf Normalkraft nachgewiesen wird -- am ganzen Querschnitt."""

    zwaengung_begrenzt: bool = False
    """Ob die rissaktive Dicke dabei hoechstens 500 mm betraegt."""

    zwaengung_biegung: bool = False
    """Ob die Zwaengung auf Biegung nachgewiesen wird -- je Richtung."""

    zwaengung_biegung_kriechzahl: float = nicht_negativ(0.0)
    """Die Kriechzahl φ der Zwaengung auf Biegung: der Beton mit ``E_cm/(1+φ)``."""

    quasistaendig: QAGebrauchsliste = field(
        default_factory=lambda: QAGebrauchsliste(anteil=QUASISTAENDIG_ANTEIL))
    """Die quasi-staendigen Lastfaelle -- fuer die Rissbreite."""

    haeufig: QAGebrauchsliste = field(
        default_factory=lambda: QAGebrauchsliste(anteil=HAEUFIG_ANTEIL))
    """Die haeufigen Lastfaelle -- gegen das Fliessen, bei erhoehter und hoher Anforderung."""

    knickfaelle: List[QAKnickEintrag] = field(default_factory=list)
    """Knicknachweise, je in einer Richtung; leer heisst: keiner."""

    knicken_wahl_verformung: RechenwahlEintrag = field(
        default_factory=RechenwahlEintrag.knicken_verformung)
    knicken_wahl_widerstand: RechenwahlEintrag = field(
        default_factory=RechenwahlEintrag.knicken_widerstand)
    """
    Womit das Knicken die Ausmitte e_2d und den Widerstand rechnet -- wie bei
    der Platte: die Verformung immer praezise, der Widerstand mit 0.85·x oder
    praezise.
    """

    spannungsfaelle: List[QASpannungsfallEintrag] = field(default_factory=list)
    """Die Spannung-Dehnung-Analysen -- kein Nachweis, ein Blick in den Querschnitt."""

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
        """
        Was sich schon an der Beschreibung pruefen laesst: eindeutige Namen der
        Faelle, und die Gebrauchslisten pruefen sich selbst, samt Anteil und
        abgeleiteten Namen.
        """
        eindeutig(self.lastfaelle, self.name, "Lastfall", bauteil="Querschnitt")
        eindeutig(self.spannungsfaelle, self.name, "Spannung-Dehnung-Analyse",
                  bauteil="Querschnitt")
        for liste, wort in ((self.haeufig, "häufige"), (self.quasistaendig, "quasi-ständige")):
            liste.pruefen(self.name, self.lastfaelle, wort)
        eindeutig(self.knickfaelle, self.name, "Knicknachweis", bauteil="Querschnitt")
        for wahl, was, arten in ((self.knicken_wahl_verformung, "Verformung", VERFORMUNGSARTEN),
                                 (self.knicken_wahl_widerstand, "Widerstand", FASERARTEN)):
            wahl.pruefen(f"Querschnitt '{self.name}', Knicken, {was}", arten)

    def lastfall(self, name: str, **werte: float) -> QALastfallEintrag:
        """Einen Lastfall anfuegen, ohne Oberflaeche -- kN und kNm."""
        eintrag = QALastfallEintrag(name=name, **werte)
        self.lastfaelle.append(eintrag)
        return eintrag

    def knickfall(self, name: str, *, N_Ed: float, M_Ed_1: float = 0.0,
                  laenge: float = 3.0, knicklaenge: Optional[float] = None,
                  richtung: str = Zugseite.UNTEN.value) -> QAKnickEintrag:
        """Ein Knicknachweis -- N_Ed in kN (Druck negativ), Längen in m, die Zugseite."""
        eintrag = QAKnickEintrag.aus_dict(
            {"name": name, "N_Ed": N_Ed, "M_Ed_1": M_Ed_1, "laenge": laenge,
             "knicklaenge": laenge if knicklaenge is None else knicklaenge,
             "richtung": richtung}, f"Querschnitt '{self.name}', knickfaelle")
        self.knickfaelle.append(eintrag)
        return eintrag

    def spannungsfall(self, name: str, *, art: str = "schnittgroessen",
                      **felder: Any) -> QASpannungsfallEintrag:
        """
        Eine Spannung-Dehnung-Analyse -- Felder wie bei der Platte, die
        Richtung als Zugseite (``unten``, ``oben``, ``links``, ``rechts``).
        Gelesen wie aus einer Datei, also mit denselben Pruefungen.
        """
        eintrag = QASpannungsfallEintrag.aus_dict(
            {"name": name, "art": art, **felder}, f"Querschnitt '{self.name}', spannungsfaelle")
        self.spannungsfaelle.append(eintrag)
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
