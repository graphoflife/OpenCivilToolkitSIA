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
der Platte (:meth:`QuerschnittEintrag.regeln`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from opencivil.querschnitt.gesetzwahl import Rechenart, Werkstoffsatz
from opencivil.nachweis.rechenwahl import FASERARTEN
from opencivil.querschnitt.geometrie import VERSCHMIERT, Linienart
from opencivil.querschnitt import vorlagen
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.projekt.eintraege import (
    HAEUFIG_ANTEIL, QUASISTAENDIG_ANTEIL, Beschreibung, Gebrauchsliste, Gebrauchswahl,
    JeMaterial, KnickEintrag, Querschnittsangaben, SpannungsfallEintrag, groesste_neigung,
    kleinste_neigung, spannungsfallnamen,
)
from opencivil.projekt.fallnamen import Fallnamen
from opencivil.core.einheiten import KN, KNM, MM, MM2
from opencivil.projekt.lesen import (
    ProjektFehler, bereich, einer_von, je_material, ort_von, teil,
)
from opencivil.projekt.netz import Netz, neue_kennung

#: Schnitte eines Buegels durch eine Schubwand: so viele Schenkel kreuzen sie.
SCHNITTE = range(1, 9)

#: Ein Punkt in mm -- oder die Kennung eines Knotens, der dort liegt.
Ort = Union[str, Sequence[float]]


def _punkt(roh: Any, wo: str) -> List[float]:
    """Ein Punkt ``[y, z]`` -- zwei Zahlen, sonst ein Satz, was fehlt."""
    try:
        y, z = roh
        return [float(y), float(z)]
    except (TypeError, ValueError):
        raise ProjektFehler(f"ein Punkt muss aus zwei Zahlen bestehen, "
                            f"nicht {roh!r}.", wo=wo) from None


# ===========================================================================
# Die Teile
# ===========================================================================


@dataclass
class KnotenEintrag(Beschreibung):
    """Ein Punkt der Zeichnung, in mm. Die Elemente verweisen mit seiner Kennung auf ihn."""

    IM_ORT = "Knoten"

    kennung: str = ""
    y: float = bereich(0.0, heisst="y", einheit=MM)
    z: float = bereich(0.0, heisst="z", einheit=MM)


@dataclass
class FlaecheEintrag(Beschreibung):
    """Ein Polygon des Querschnitts. Ohne Material ist es eine Aussparung."""

    IM_ORT = "Polygon"
    """In der Zeichnung heisst eines ohne Material «Aussparung» (:meth:`QuerschnittsanalyseEintrag.elemente`)."""

    kennung: str = ""
    knoten: List[str] = field(default_factory=list)
    """Die Ecken als Knoten, der Reihe nach; die erste wird am Ende nicht wiederholt."""

    material: str = ""
    """Kennung des Materials; leer heisst Aussparung."""

    ueberdeckung: float = bereich(0.0, heisst="Überdeckung c", einheit=MM, ab=0.0)
    """
    Die Ueberdeckung der Bewehrung in mm, eine Hilfe beim Zeichnen: ueber null
    zeigt das Zeichenfenster das Polygon so weit nach innen gerueckt -- bei
    einer Aussparung nach aussen -- und «Überdeckung beachten» schiebt
    Bewehrung hinein (:func:`~opencivil.querschnitt.geometrie.stab_in_ueberdeckung`).
    Gerechnet wird mit ihr nicht.
    """

    @property
    def ist_aussparung(self) -> bool:
        return not self.material


@dataclass
class StabEintrag(Beschreibung):
    """Ein einzelner Bewehrungsstab, an einem Knoten."""

    IM_ORT = "Stab"

    kennung: str = ""
    knoten: str = ""
    durchmesser: float = bereich(16.0, heisst="Durchmesser", einheit=MM, ueber=0.0)
    stahl: str = ""


@dataclass
class StablinieEintrag(Beschreibung):
    """
    Eine Linie von Staeben -- oder eine verschmierte Stahlflaeche.

    Je Art ein eigenes Feld fuer die Menge: wer die Art wechselt und wieder
    zurueck, findet seine Zahl noch vor. Welche gilt, sagt ``art``.
    """

    IM_ORT = "Linie"

    kennung: str = ""
    von: str = ""
    bis: str = ""
    """Anfang und Ende als Knoten."""

    art: Linienart = Linienart.TEILUNG
    durchmesser: float = bereich(16.0, heisst="Durchmesser", einheit=MM, ueber=0.0)
    """Bei Anzahl und Teilung -- und bei verschmierten Staeben -- der Stabdurchmesser in mm."""

    flaeche: float = bereich(1000.0, heisst="Stahlfläche", einheit=MM2, ueber=0.0)
    """Bei Art «Fläche» die ganze Stahlflaeche der Linie in mm² -- von Hand."""

    verschmiert: str = einer_von(VERSCHMIERT, "flaeche")
    """
    Bei Art «Fläche», wie die Stahlflaeche angegeben ist: ``flaeche`` von Hand
    -- oder ``staebe``: Staebe ``durchmesser`` im Abstand ``teilung`` ueber
    ``laenge``, verschmiert (Benutzer, 2026-10-24).
    """

    laenge: Optional[float] = bereich(None, heisst="Länge", einheit=MM, ueber=0.0)
    """Bei verschmierten Staeben die Laenge in mm, ueber die sie liegen -- leer: die der Linie."""

    anzahl: float = bereich(5.0, heisst="Stabzahl", ab=1.0)
    teilung: float = bereich(150.0, heisst="Teilung", einheit=MM, ueber=0.0)
    """
    Bei Art «Teilung» der Wunschabstand in mm -- gerundet auf einen, der
    aufgeht; bei verschmierten Staeben ihr Abstand, wie er ist.
    """

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

    IM_ORT = "Wand"

    kennung: str = ""
    von: str = ""
    bis: str = ""
    """Anfang und Ende als Knoten. Die Richtung zaehlt: sie gibt dem Schubfluss sein Vorzeichen."""

    dicke: float = bereich(200.0, heisst="Dicke b_w", einheit=MM, ueber=0.0)
    durchmesser: float = bereich(10.0, heisst="Bügeldurchmesser", einheit=MM, ab=0.0)
    """Null: ohne Buegel."""

    teilung: float = bereich(150.0, heisst="Bügelteilung", einheit=MM, ueber=0.0)
    """In Laengsrichtung."""

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

    IM_ORT = "Hilfslinie"

    kennung: str = ""
    von: str = ""
    bis: str = ""


@dataclass
class QALastfallEintrag(Beschreibung):
    """Ein Lastfall der Querschnittsanalyse -- kN und kNm, Vorzeichen siehe oben."""

    IM_ORT = "Lastfall"

    name: str
    N_Ed: float = bereich(0.0, heisst="Normalkraft N_Ed", einheit=KN)
    M_y_Ed: float = bereich(0.0, heisst="Moment M_y,Ed", einheit=KNM)
    M_z_Ed: float = bereich(0.0, heisst="Moment M_z,Ed", einheit=KNM)
    V_y_Ed: float = bereich(0.0, heisst="Querkraft V_y,Ed", einheit=KN)
    V_z_Ed: float = bereich(0.0, heisst="Querkraft V_z,Ed", einheit=KN)
    T_Ed: float = bereich(0.0, heisst="Torsion T_Ed", einheit=KNM)
    aktiv: bool = True


@dataclass
class QAGebrauchsfallEintrag(Beschreibung):
    """
    Ein Lastfall unter Gebrauchslast -- wie ein Lastfall der Tragsicherheit,
    ohne Querkraft und Torsion: begrenzt wird die Stahlspannung, und dafuer
    zaehlen N und die Momente. kN und kNm, Vorzeichen siehe oben.
    """

    IM_ORT = "Lastfall"

    name: str
    N_Ed: float = bereich(0.0, heisst="Normalkraft N_Ed", einheit=KN)
    M_y_Ed: float = bereich(0.0, heisst="Moment M_y,Ed", einheit=KNM)
    M_z_Ed: float = bereich(0.0, heisst="Moment M_z,Ed", einheit=KNM)
    aktiv: bool = True


@dataclass
class QAGebrauchswahl(Gebrauchswahl):
    """Die Stahlspannungen am gezeichneten Querschnitt: nur ueber die Fasern, ohne Handrechnung."""

    rechenarten: Dict[str, Rechenart] = je_material(Rechenart.PARABEL, FASERARTEN)


@dataclass
class QAGebrauchsliste(Gebrauchsliste):
    """
    Die Lastfaelle einer Stahlspannung am gezeichneten Querschnitt: dieselbe
    Liste wie bei der Platte, mit N, M_y und M_z je Fall, abgeleitet aus den
    Lastfaellen der Tragsicherheit. Gerechnet wird ueber die Fasern -- eine
    Handrechnung gibt es hier nicht.
    """

    FALL = QAGebrauchsfallEintrag
    BAUTEIL = "Querschnitt"

    faelle: List[QAGebrauchsfallEintrag] = field(default_factory=list)
    wahl: QAGebrauchswahl = teil(QAGebrauchswahl, heisst="Rechenwahl")


@dataclass
class QAKnickEintrag(KnickEintrag):
    """
    Ein Knicknachweis des gezeichneten Querschnitts -- wie bei der Platte,
    dazu die Zugseite: die Seite, zu der sich der Stab biegt und die das
    Moment 1. Ordnung zieht (:class:`~opencivil.querschnitt.zugseite.Zugseite`).
    """

    richtung: Zugseite = Zugseite.UNTEN


@dataclass
class QASpannungsfallEintrag(SpannungsfallEintrag):
    """
    Eine Spannung-Dehnung-Analyse des gezeichneten Querschnitts -- dieselben
    Felder wie bei der Platte. Die Richtung ist hier die Zugseite: die Seite,
    die ein positives Moment zieht (:class:`~opencivil.querschnitt.zugseite.Zugseite`).
    """

    richtung: Zugseite = Zugseite.UNTEN


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
    """Je Polygon ``punkte``, ``material`` (leer: Aussparung) und ``ueberdeckung``."""

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
class QuerschnittsanalyseEintrag(Querschnittsangaben, JeMaterial):
    """
    Ein gezeichneter Querschnitt mit Bewehrung, Schubwaenden und Lastfaellen.
    Was er mit der Platte gleich angibt, steht in der Grundlage
    (:class:`~opencivil.projekt.eintraege.Querschnittsangaben`).
    """

    BEZEICHNUNG = "Querschnittsanalyse"
    STAMM = "Querschnitt"

    knoten: List[KnotenEintrag] = field(default_factory=list)
    flaechen: List[FlaecheEintrag] = field(default_factory=list)
    staebe: List[StabEintrag] = field(default_factory=list)
    stablinien: List[StablinieEintrag] = field(default_factory=list)
    schubwaende: List[SchubwandEintrag] = field(default_factory=list)
    hilfslinien: List[HilfslinieEintrag] = field(default_factory=list)
    werkstoffsaetze: Dict[str, Werkstoffsatz] = je_material(Werkstoffsatz.BEMESSUNG)
    """
    Je Material die Werte der Tragsicherheit: Bemessungs- oder
    charakteristische -- das legt fest, wo die Plateaus liegen (``f_cd`` oder
    ``f_ck``, ``f_yd`` oder ``f_yk``). Duktilitaet und sproedes Versagen
    rechnen am selben Querschnitt.
    """

    rechenarten: Dict[str, Rechenart] = je_material(Rechenart.PARABEL, FASERARTEN)
    """
    Je Beton die Rechenart der Tragsicherheit: praezise mit der
    Parabel-Rechteck-Beziehung oder mit dem vereinfachten Spannungsblock
    0.85·x. Bis 2026-11-25 hiess das Feld ``betongesetze``, als einziges
    je Beton.
    """

    #: Die Tragsicherheit rechnet ohne Kriechen (:meth:`JeMaterial.wahl`).
    kriechzahl: ClassVar[float] = 0.0

    lastfaelle: List[QALastfallEintrag] = field(default_factory=list)

    einachsig: bool = False
    """
    Nur Biegung um y: die Nulllinie bleibt waagrecht, M_z und V_y zaehlen
    nicht, und Duktilitaet und sproedes Versagen gibt es nur in y. Torsion
    bleibt. Bei einem unsymmetrischen Querschnitt ist das eine Naeherung --
    dasselbe, was die Platte immer tut.
    """

    alpha_min: int = kleinste_neigung()
    alpha_max: int = groesste_neigung()
    """Die Grenzen der Druckfeldneigung in den Schubwaenden -- wie bei den Buegeln der Platte."""

    laengszugkraft: bool = False
    """
    Ob die Laengszugkraft aus Querkraft und Torsion in den M-N-Nachweis
    eingeht: das Druckfeld jeder Schubwand braucht in Laengsrichtung Zug.
    """

    quasistaendig: QAGebrauchsliste = teil(
        lambda: QAGebrauchsliste(anteil=QUASISTAENDIG_ANTEIL), heisst="Stahlspannung quasi-ständig")
    """Die quasi-staendigen Lastfaelle -- fuer die Rissbreite."""

    haeufig: QAGebrauchsliste = teil(lambda: QAGebrauchsliste(anteil=HAEUFIG_ANTEIL),
                                     heisst="Fliessen häufig")
    """Die haeufigen Lastfaelle -- gegen das Fliessen, bei erhoehter und hoher Anforderung."""

    knickfaelle: List[QAKnickEintrag] = field(default_factory=list)
    """Knicknachweise, je in einer Richtung; leer heisst: keiner."""

    spannungsfaelle: List[QASpannungsfallEintrag] = field(default_factory=list)
    """Die Spannung-Dehnung-Analysen -- kein Nachweis, ein Blick in den Querschnitt."""

    def materialien(self) -> List[str]:
        """
        Jedes Material, auf das die Analyse zeigt, in der Reihenfolge des
        ersten Auftretens. Jeder Verweis zaehlt, auch einer, der gerade nichts traegt: wer das
        Material loescht, liesse ihn ins Leere zeigen, und spaetestens die
        naechste Aenderung machte daraus einen Fehler beim Rechnen.
        """
        gesehen: List[str] = []
        for kennung in ([f.material for f in self.flaechen]
                        + [s.stahl for s in self.staebe]
                        + [l.stahl for l in self.stablinien]
                        + [w.stahl for w in self.schubwaende]):
            if kennung and kennung not in gesehen:
                gesehen.append(kennung)
        return gesehen

    @property
    def leer(self) -> bool:
        """
        Ob noch nichts gezeichnet ist, was traegt: keine Flaeche, kein Stab,
        keine Stablinie, keine Schubwand. Knoten und Hilfslinien allein sind
        Bauhilfen. So beginnt eine neue Analyse (Benutzer, 2026-10-19), und
        so gibt es nichts zu rechnen -- aber auch keinen Fehler.
        """
        return not (self.flaechen or self.staebe or self.stablinien or self.schubwaende)

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
                                           f"eines Knotens – gezeichnet wird mit dem "
                                           f"Baukasten (polygon, stab, stablinie, …).",
                                   "elemente": [kennung or name]})
                    return None
                if v not in lage:
                    fehler.append({"text": f"{name}: den Knoten '{v or '?'}' gibt es nicht.",
                                   "elemente": [kennung or name]})
                    return None
            return [lage[v] for v in verweise]

        polygone, staebe, linien, waende, hilfslinien = [], [], [], [], []
        # Je Element sein Wort und seine Nummer, wie in Meldungen ueber seine
        # Felder (``IM_ORT``); ein Polygon ohne Material ist eine Aussparung.
        for i, f in enumerate(self.flaechen, start=1):
            name = f"{f.IM_ORT if f.material else 'Aussparung'} {i}"
            ecken = orte(name, f.kennung, *f.knoten)
            if ecken is not None:
                polygone.append(benannt(name, f.kennung, punkte=tuple(ecken),
                                        material=f.material, ueberdeckung=f.ueberdeckung))
        for i, s in enumerate(self.staebe, start=1):
            name = f"{s.IM_ORT} {i}"
            ort = orte(name, s.kennung, s.knoten)
            if ort is not None:
                staebe.append(benannt(name, s.kennung, lage=ort[0],
                                      durchmesser=s.durchmesser, stahl=s.stahl))
        for i, l in enumerate(self.stablinien, start=1):
            name = f"{l.IM_ORT} {i}"
            ende = orte(name, l.kennung, l.von, l.bis)
            if ende is not None:
                linien.append(benannt(
                    name, l.kennung, von=ende[0], bis=ende[1], art=l.art,
                    durchmesser=l.durchmesser, flaeche=l.flaeche, verschmiert=l.verschmiert,
                    laenge=l.laenge, anzahl=l.anzahl, teilung=l.teilung,
                    starteisen=l.starteisen, endeisen=l.endeisen, stahl=l.stahl))
        for i, w in enumerate(self.schubwaende, start=1):
            name = f"{w.IM_ORT} {i}"
            ende = orte(name, w.kennung, w.von, w.bis)
            if ende is not None:
                waende.append(benannt(
                    name, w.kennung, von=ende[0], bis=ende[1], dicke=w.dicke,
                    durchmesser=w.durchmesser, teilung=w.teilung, schnitte=w.schnitte,
                    stahl=w.stahl))
        for i, h in enumerate(self.hilfslinien, start=1):
            name = f"{h.IM_ORT} {i}"
            ende = orte(name, h.kennung, h.von, h.bis)
            if ende is not None:
                hilfslinien.append(benannt(name, h.kennung, von=ende[0], bis=ende[1]))
        return Elemente(polygone=polygone, staebe=staebe, linien=linien, waende=waende,
                        hilfslinien=hilfslinien, fehler=fehler)

    # -- Zeichnen ohne Oberflaeche -------------------------------------------

    def netz(self) -> Netz:
        """Die Knoten zum Weiterzeichnen: gleiche Koordinaten sind ein Knoten."""
        return Netz(self, neu=lambda kennung, y, z: KnotenEintrag(kennung, y, z))

    def _knoten(self, netz: Netz, ort: Ort) -> str:
        """Ein Knoten aus einem Punkt ``[y, z]`` -- oder die Kennung, wenn schon eine dasteht."""
        if isinstance(ort, str):
            return ort
        y, z = _punkt(ort, ort_von(self))
        return netz.an(y, z)

    def _kennung(self, vorsilbe: str) -> str:
        """Die naechste Kennung -- alle Linien zaehlen gemeinsam, ob Bewehrung, Wand oder Hilfslinie."""
        listen = {"F": [self.flaechen], "S": [self.staebe],
                  "L": [self.stablinien, self.schubwaende, self.hilfslinien]}[vorsilbe]
        return neue_kennung(self, vorsilbe, (e.kennung for liste in listen for e in liste))

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
        eintrag = StabEintrag.aus_dict(
            {"kennung": self._kennung("S"), "knoten": self._knoten(self.netz(), (y, z)),
             **felder}, f"{ort_von(self)}, staebe")
        self.staebe.append(eintrag)
        return eintrag

    def stablinie(self, von: Ort, bis: Ort, **felder: Any) -> StablinieEintrag:
        """Eine Stablinie; die Felder wie :class:`StablinieEintrag`."""
        netz = self.netz()
        eintrag = StablinieEintrag.aus_dict(
            {"kennung": self._kennung("L"), "von": self._knoten(netz, von),
             "bis": self._knoten(netz, bis), **felder}, f"{ort_von(self)}, stablinien")
        self.stablinien.append(eintrag)
        return eintrag

    def schubwand(self, von: Ort, bis: Ort, **felder: Any) -> SchubwandEintrag:
        """Eine Schubwand; die Felder wie :class:`SchubwandEintrag`."""
        netz = self.netz()
        eintrag = SchubwandEintrag.aus_dict(
            {"kennung": self._kennung("L"), "von": self._knoten(netz, von),
             "bis": self._knoten(netz, bis), **felder}, f"{ort_von(self)}, schubwaende")
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
                          randabstand: float = vorlagen.RANDABSTAND.vorgabe,
                          bewehrung: bool = True,
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

    def fallnamen(self) -> List[Fallnamen]:
        """Die Listen, deren Namen sich unterscheiden muessen -- wie bei der Platte."""
        return [
            Fallnamen.aus("lastfaelle", "Lastfall", self.lastfaelle),
            self.haeufig.namensliste("haeufig", self.lastfaelle, "häufige"),
            self.quasistaendig.namensliste("quasistaendig", self.lastfaelle, "quasi-ständige"),
            spannungsfallnamen(self.spannungsfaelle),
            Fallnamen.aus("knickfaelle", "Knicknachweis", self.knickfaelle),
        ]

    def lastfall(self, name: str, **werte: float) -> QALastfallEintrag:
        """Einen Lastfall anfuegen, ohne Oberflaeche -- kN und kNm."""
        eintrag = QALastfallEintrag.aus_dict({"name": name, **werte},
                                             f"{ort_von(self)}, lastfaelle")
        self.lastfaelle.append(eintrag)
        return eintrag

    def knickfall(self, name: str, *, N_Ed: float, M_Ed_1: float = 0.0,
                  laenge: float = 3.0, knicklaenge: Optional[float] = None,
                  richtung: str = Zugseite.UNTEN.value) -> QAKnickEintrag:
        """Ein Knicknachweis -- N_Ed in kN (Druck negativ), Längen in m, die Zugseite."""
        eintrag = QAKnickEintrag.aus_dict(
            {"name": name, "N_Ed": N_Ed, "M_Ed_1": M_Ed_1, "laenge": laenge,
             "knicklaenge": laenge if knicklaenge is None else knicklaenge,
             "richtung": richtung}, f"{ort_von(self)}, knickfaelle")
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
            {"name": name, "art": art, **felder}, f"{ort_von(self)}, spannungsfaelle")
        self.spannungsfaelle.append(eintrag)
        return eintrag

    @classmethod
    def neu(cls, kennung: str, name: str) -> "QuerschnittsanalyseEintrag":
        """
        Eine frische Analyse, wie der Benutzer sie angelegt bekommt: leer,
        nichts gezeichnet und kein Lastfall (Benutzer, 2026-10-19). Bis dahin
        kam sie als Rechteck 300 × 600 mm mit fuenf Staeben und einem
        Feldmoment; das Rechteck gibt es als Vorlage im Zeichenfenster.
        """
        return cls(kennung=kennung, name=name)
