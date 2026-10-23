"""
opencivil/stabwerk/rechnung.py -- das Balkensystem im Rechenwerk.

VERANTWORTUNG:
Was ein Balkensystem im Rechenwerk anmeldet: je Querschnitt die Flaeche
``A`` und das Traegheitsmoment ``I``, je Paar aus Querschnitt und Material
die Dehn- und die Biegesteifigkeit ``EA`` und ``EI``, und eine Prozedur, die
das System nach der Steifigkeitsmethode rechnet
(:mod:`~opencivil.stabwerk.system`) und ihre Herleitung schreibt
(:mod:`~opencivil.stabwerk.herleitung`).

WOHER A UND I KOMMEN:
* nach Vorlage -- die Formeln der Vorlage
  (:mod:`~opencivil.stabwerk.querschnitte`), die Masse als Vorgaben;
* von Hand -- A und I als Eingaben;
* aus einer Platte -- die Formeln des Rechtecks mit ``b`` und ``h`` der
  Platte;
* aus einer Querschnittsanalyse -- ``A`` und ``I_y`` ihres
  Bruttoquerschnitts.

Ueber die Werte der Platte und der Analyse haengt das System im Rechengraph
an ihnen: aendert sich deren Dicke, rechnet es neu.

STEIFIGKEIT -- NACH VORGABE, NICHT NACHGESCHLAGEN:
``E_cm`` fuer Beton und ``E_s`` fuer Betonstahl (:data:`E_MODUL`), am
ungerissenen Bruttoquerschnitt, ohne Schubverformung, Gleichgewicht am
unverformten System. Die Herleitung sagt es, das TODO fuehrt es.

EIGENGEWICHT -- NACH VORGABE DES BENUTZERS (2026-10-23):
Je Paar aus Querschnitt und Material ``g_k = rho · g · A`` in kN/m, mit
``g = 10 m/s²`` und beim Beton der Dichte des Stahlbetons (:data:`DICHTE`)
-- ohne den Stahl noch dazu. Es kommt als Last senkrecht je Meter Stab in den
Lastfall, den die Beschreibung dafuer nennt.

DAS ERGEBNIS:
kommt als Befund in die Loesung (:class:`Systembefund`); Zusammenfassung,
Bilder und Zwischenspeicher lesen es dort. Einen Wert liefert die Prozedur
nicht: sie ist Ziel unter ihrer ID. Ein bewegliches System ist ein Ergebnis
mit Meldung und keine Ausnahme: der Rest des Projekts rechnet weiter.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Ausfuehrung, Berechnung, Eingabebezug, Eingaben, Formel, Prozedur, Vorgabe,
)
from opencivil.core.einheiten import KN_PRO_M, KNM2, M_PRO_S2, MIO_MM4, MM, MM2, MN, Groesse
from opencivil.core.latex import platzhalter_namen
from opencivil.core.protokoll import Abschnitt, Protokoll
from opencivil.core.wert import Quelle, WertDef
from opencivil.material.basis import Baustoff, mit_index
from opencivil.stabwerk import herleitung
from opencivil.stabwerk.modell import Lastart, Lastrichtung, Stablast, System
from opencivil.stabwerk.querschnitte import RECHTECK, Stabvorlage
from opencivil.stabwerk.system import Ergebnis, Fall, Meldung, rechnen
from opencivil.stabwerk.verlauf import Stabverlauf, verlaeufe

#: Welcher E-Modul in die Steifigkeit eingeht, je Art des Materials -- nach
#: Vorgabe, nicht nachgeschlagen.
E_MODUL = {"beton": "E_cm", "betonstahl": "E_s"}

#: Welche Dichte ins Eigengewicht eingeht, je Art des Materials -- beim Beton
#: die des Stahlbetons (Benutzer, 2026-10-23).
DICHTE = {"beton": "rho_sb", "betonstahl": "rho_s"}

#: Die Erdbeschleunigung des Eigengewichts -- 10 m/s² nach Vorgabe des
#: Benutzers (2026-10-23): so wiegt Stahlbeton 25 kN/m³.
ERDBESCHLEUNIGUNG = Groesse(10.0, M_PRO_S2)

#: Die Themen der Formelsammlung: was am Querschnitt haengt, und die Rechnung.
QUERSCHNITTE = "Stabquerschnitte"
STEIFIGKEITSMETHODE = "Steifigkeitsmethode"


@dataclass(frozen=True)
class Stabquerschnitt:
    """Ein Querschnitt der Staebe, aufgeloest: woher ``A`` und ``I`` kommen."""

    kennung: str
    name: str
    art: str
    """``vorlage``, ``kennwerte``, ``platte`` oder ``analyse``."""

    vorlage: Optional[Stabvorlage] = None
    masse: Mapping[str, float] = field(default_factory=dict)
    """Die Masse der Vorlage in mm -- bei Kennwerten ``A`` in mm² und ``I`` in 10⁶ mm⁴."""

    quelle: Mapping[str, str] = field(default_factory=dict)
    """Die Wert-IDs, aus denen er rechnet: ``b`` und ``h`` einer Platte, ``A`` und ``I`` einer Analyse."""

    bezug: str = ""
    """Die Kennung der Platte oder Analyse, aus der er kommt."""

    herkunft: str = ""
    """Woher, in Worten -- «Rechteck», «von Hand», «Platte «Decke»»."""

    fehler: str = ""
    """Was an seinen Massen nicht geht -- dann rechnet er nicht, und kein Stab mit ihm."""


@dataclass(frozen=True)
class Steifigkeit:
    """Ein Paar aus Querschnitt und Material und die Wert-IDs seiner Steifigkeiten."""

    querschnitt: str
    material: str
    """Die Kennung des Materials im Projekt."""

    EA: str
    EI: str
    g_k: str = ""
    """Das Eigengewicht je Meter -- leer, wenn kein Lastfall es bekommt."""


@dataclass(frozen=True)
class Lagerkraft:
    """
    Eine Zeile der Lagerkraefte eines Falls, auf das Tragwerk wirkend -- in
    Herleitung und Bildschirm dieselbe.
    """

    wo: str
    """«A1 (K1)», «L2 bei 1.500 m», «L2: Bettung, Summe»."""

    R_x: float
    R_z: float
    M: float
    knoten: str = ""
    """Der Knoten, an dem sie angreift -- leer auf einem Stab und bei einer Summe."""

    summe: bool = False
    """Die Summe ueber einen Stab, mit dem Moment um den Ursprung (siehe ``SUMMEN``)."""


@dataclass
class Systembefund:
    """
    Was die Steifigkeitsmethode im Lauf fand: das System mit seinen
    Steifigkeiten, wie es gerechnet wurde, und sein Ergebnis -- Meldungen,
    Faelle mit Verschiebungen und Lagerkraeften, in SI. Die Verlaeufe eines
    Falls rechnet :meth:`verlaeufe` einmal, wenn jemand sie braucht.
    """

    gerechnet: System
    ergebnis: Ergebnis
    eigengewicht: Dict[str, float] = field(default_factory=dict)
    """Je tragenden Stab sein Eigengewicht in N/m -- leer, wenn kein Lastfall es bekommt."""

    _verlaeufe: Dict[str, Dict[str, Stabverlauf]] = field(default_factory=dict, repr=False)

    def verlaeufe(self, fall: str) -> Dict[str, Stabverlauf]:
        """Je Stab der Verlauf der Schnittgroessen und der Biegelinie in einem Fall -- einmal gerechnet."""
        if fall not in self._verlaeufe:
            self._verlaeufe[fall] = verlaeufe(self.ergebnis.fall(fall))
        return self._verlaeufe[fall]

    def lagerkraefte(self, fall: Fall) -> List[Lagerkraft]:
        """
        Die Lagerkraefte eines Falls, Zeile fuer Zeile: die Lager an Knoten,
        gehaltene Stellen auf Staeben und je Stab die Summe dessen, was ein
        festes Linienlager und die Bettung aufnehmen. Zusammen halten sie den
        Lasten das Gleichgewicht -- darum fehlt keine davon, weder in der
        Herleitung noch am Bildschirm.
        """
        orte = self.ergebnis.orte
        lager_an: Dict[str, List[str]] = {}
        for l in self.gerechnet.lager:
            lager_an.setdefault(l.knoten, []).append(l.name)
        zeilen = []
        for name, (rx, rz, rm) in fall.lagerkraefte.items():
            ort = orte[name]
            if ort.knoten:
                wo = (", ".join(lager_an[ort.knoten]) + f" ({ort.knoten})"
                      if ort.knoten in lager_an else ort.knoten)
            else:
                wo = f"{ort.stab} bei {ort.stelle:.3f} m"
            zeilen.append(Lagerkraft(wo, rx, rz, rm, knoten=ort.knoten))
        for stab, (fx, fz, m) in fall.linienlast.items():
            zeilen.append(Lagerkraft(f"{stab}: Lasten geradewegs ins Linienlager",
                                     fx, fz, m, summe=True))
        for stab, (fx, fz, m) in fall.bettung.items():
            zeilen.append(Lagerkraft(f"{stab}: Bettung, Summe", fx, fz, m, summe=True))
        return zeilen


class SteifigkeitsmethodeProzedur(Prozedur):
    """Das ganze System, gerechnet und aufgeschrieben."""

    THEMA = STEIFIGKEITSMETHODE

    def __init__(self, system: "Balkensystem", **kwargs) -> None:
        super().__init__(**kwargs)
        self.system = system

    def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        return self.system.rechnen_und_schreiben(e, p)


class Balkensystem:
    """Ein Balkensystem, fertig fuer das Rechenwerk."""

    def __init__(self, *, name: str, kennung: str, praefix: str, system: System,
                 paare: Mapping[str, Tuple[str, str]], meldungen: Sequence[Meldung],
                 querschnitte: Sequence[Stabquerschnitt],
                 stoffe: Mapping[str, Baustoff], eigengewicht: Optional[str] = None) -> None:
        """
        ``system`` ohne Steifigkeiten, wie die Beschreibung es baut;
        ``paare`` je tragenden Stab Querschnitt und Material, ``stoffe`` die
        Baustoffe dieser Materialien; ``eigengewicht`` der Lastfall, der das
        Eigengewicht der Staebe bekommt.
        """
        self.name = name
        self.kennung = kennung
        self.id = praefix
        self.system = system
        self.paare = dict(paare)
        self.meldungen = list(meldungen)
        self.querschnitte = list(querschnitte)
        self.stoffe = dict(stoffe)
        self.eigengewicht = eigengewicht
        self.definitionen: Dict[str, WertDef] = {}
        self.berechnungen: List[Berechnung] = []
        self.flaechen: Dict[str, Tuple[str, str]] = {}
        """Je Querschnitt die Wert-IDs von ``A`` und ``I``."""

        self.steifigkeiten: List[Steifigkeit] = []
        self._aufbauen()

    # -- Rechenwerk ------------------------------------------------------------

    def abschnitt(self, thema: str = STEIFIGKEITSMETHODE) -> Abschnitt:
        """Ein Abschnitt fuer alles -- das Thema sagt nur, wo die Formeln gesammelt stehen."""
        return Abschnitt(f"Balkensystem: {self.name}", self.id, thema=thema)

    def _def(self, kurzname: str, symbol: str, einheit, beschreibung: str,
             stellen: int) -> WertDef:
        d = WertDef(id=f"{self.id}.{kurzname}", symbol=symbol, einheit=einheit,
                    beschreibung=beschreibung, stellen=stellen)
        self.definitionen[kurzname] = d
        return d

    @property
    def bezuege(self) -> List[str]:
        """Die Platten und Analysen, deren Werte das System liest."""
        return sorted({q.bezug for q in self.querschnitte if q.bezug})

    def _aufbauen(self) -> None:
        index = len(self.querschnitte) > 1
        for q in self.querschnitte:
            if not q.fehler:
                self.flaechen[q.kennung] = self._querschnitt(q, q.kennung if index else "")

        # Ein Querschnitt, der erst beim Aufbau scheitert -- er nimmt eine
        # Querschnittsanalyse, die noch leer ist --, steht noch in den Paaren:
        # das Modell kannte nur die Fehler seiner Masse. Seine Staebe haben
        # keine Steifigkeit; die Meldung sagt es, und das System rechnet nicht.
        gestrichen: Dict[str, List[str]] = {}
        for stab, (q, _) in list(self.paare.items()):
            if q not in self.flaechen:
                del self.paare[stab]
                gestrichen.setdefault(q, []).append(stab)
        for q in self.querschnitte:
            if q.kennung in gestrichen:
                self.meldungen.append(Meldung(f"Querschnitt «{q.name}»: {q.fehler}",
                                              (q.kennung, *gestrichen[q.kennung]), True))

        benutzt: List[Tuple[str, str]] = []
        for paar in self.paare.values():
            if paar not in benutzt:
                benutzt.append(paar)
        mehrere_stoffe = len({m for _, m in benutzt}) > 1
        g = self._erdbeschleunigung() if self.eigengewicht and benutzt else None
        for q, m in benutzt:
            teile = [q] if index else []
            if mehrere_stoffe:
                teile.append(self.stoffe[m].name)
            self.steifigkeiten.append(self._steifigkeit(q, m, ",".join(teile), g))

        groessen = ("EA", "EI", "g_k") if g else ("EA", "EI")
        self.rechnung = SteifigkeitsmethodeProzedur(
            self, id=f"{self.id}.rechnung", ausgaben=[],
            bezuege=[Eingabebezug(f"{groesse}_{i}", getattr(s, groesse))
                     for i, s in enumerate(self.steifigkeiten) for groesse in groessen],
            titel="Steifigkeitsmethode", abschnitt=self.abschnitt())
        """Die Prozedur, die das System rechnet -- ihr Befund ist der :class:`Systembefund`."""
        self.berechnungen.append(self.rechnung)

    def _querschnitt(self, q: Stabquerschnitt, index: str) -> Tuple[str, str]:
        """Die Berechnungen fuer A und I eines Querschnitts -- und ihre Wert-IDs."""
        abschnitt = self.abschnitt(QUERSCHNITTE)
        wo = f"{q.kennung}."
        if q.art == "kennwerte":
            ids = []
            for kurz, einheit, stellen, beschreibung in (
                    ("A", MM2, 0, "Querschnittsfläche"),
                    ("I", MIO_MM4, 2, "Flächenträgheitsmoment")):
                d = self._def(wo + kurz, mit_index(kurz, index), einheit,
                              f"{beschreibung}, {q.name}", stellen)
                self.berechnungen.append(Vorgabe(
                    id=d.id, ausgabe=d, groesse=Groesse(q.masse.get(kurz, 0.0), einheit),
                    quelle=Quelle.EINGABE, titel=f"{beschreibung}, «{q.name}» (von Hand)",
                    abschnitt=abschnitt))
                ids.append(d.id)
            return ids[0], ids[1]
        if q.art == "analyse":
            ids = []
            for kurz, einheit, stellen, beschreibung in (
                    ("A", MM2, 0, "Querschnittsfläche"),
                    ("I", MIO_MM4, 2, "Flächenträgheitsmoment")):
                d = self._def(wo + kurz, mit_index(kurz, index), einheit,
                              f"{beschreibung}, {q.name}", stellen)
                self.berechnungen.append(Formel(
                    id=d.id, ausgabe=d, funktion=_derselbe, eingaben={"wert": q.quelle[kurz]},
                    titel=f"{beschreibung}, «{q.name}» (Bruttoquerschnitt der {q.herkunft})",
                    abschnitt=abschnitt))
                ids.append(d.id)
            return ids[0], ids[1]

        # Nach Vorlage oder aus einer Platte: die Formeln der Vorlage.
        vorlage = q.vorlage if q.art == "vorlage" else RECHTECK
        quellen = dict(q.quelle)
        if q.art == "vorlage":
            for mass in vorlage.masse:
                wert = q.masse[mass.schluessel]
                d = self._def(wo + mass.schluessel, mit_index(mass.symbol, index), MM,
                              f"{mass.beschriftung}, {q.name}",
                              0 if float(wert).is_integer() else 1)
                self.berechnungen.append(Vorgabe(
                    id=d.id, ausgabe=d, groesse=Groesse(wert, MM), abschnitt=abschnitt,
                    stumm=True))
                quellen[mass.schluessel] = d.id
        for f in vorlage.formeln:
            d = self._def(wo + f.kurzname, mit_index(f.symbol, index), f.einheit,
                          f"{f.beschreibung}, {q.name}", f.stellen)
            self.berechnungen.append(Formel(
                id=d.id, ausgabe=d, funktion=f.funktion, vorlage=f.vorlage,
                eingaben={n: quellen[n] for n in platzhalter_namen(f.vorlage)},
                titel=f"{f.beschreibung}, «{q.name}» ({q.herkunft})", name=f.name,
                abschnitt=abschnitt))
            quellen[f.kurzname] = d.id
        return quellen["A"], quellen["I"]

    def _erdbeschleunigung(self) -> str:
        """``g`` als Vorgabe des Systems -- seine Wert-ID."""
        d = self._def("g", "g", M_PRO_S2, "Erdbeschleunigung", 0)
        self.berechnungen.append(Vorgabe(
            id=d.id, ausgabe=d, groesse=ERDBESCHLEUNIGUNG, abschnitt=self.abschnitt(QUERSCHNITTE),
            titel="Erdbeschleunigung für das Eigengewicht (nach Vorgabe des Benutzers)"))
        return d.id

    def _steifigkeit(self, q: str, material: str, index: str,
                     g: Optional[str] = None) -> Steifigkeit:
        """EA und EI eines Paars aus Querschnitt und Material -- mit ``g`` dazu sein Eigengewicht."""
        abschnitt = self.abschnitt(QUERSCHNITTE)
        stoff = self.stoffe[material]
        modul = stoff.id_von(E_MODUL[stoff.art.value])
        A, I = self.flaechen[q]
        name = next(x.name for x in self.querschnitte if x.kennung == q)
        wo = f"{q}.{material}."
        d_EA = self._def(wo + "EA", mit_index("EA", index), MN,
                         f"Dehnsteifigkeit, {name}, {stoff.name}", 0)
        d_EI = self._def(wo + "EI", mit_index("EI", index), KNM2,
                         f"Biegesteifigkeit, {name}, {stoff.name}", 0)
        self.berechnungen += [
            Formel(id=d_EA.id, ausgabe=d_EA, funktion=_dehnsteifigkeit,
                   vorlage=r"@E \cdot @A", eingaben={"E": modul, "A": A},
                   titel=f"Dehnsteifigkeit, «{name}» aus {stoff.name}", name="Dehnsteifigkeit",
                   abschnitt=abschnitt),
            Formel(id=d_EI.id, ausgabe=d_EI, funktion=_biegesteifigkeit,
                   vorlage=r"@E \cdot @I", eingaben={"E": modul, "I": I},
                   titel=f"Biegesteifigkeit, «{name}» aus {stoff.name}", name="Biegesteifigkeit",
                   abschnitt=abschnitt),
        ]
        if g is None:
            return Steifigkeit(querschnitt=q, material=material, EA=d_EA.id, EI=d_EI.id)
        d_g = self._def(wo + "g_k", mit_index("g_k", index), KN_PRO_M,
                        f"Eigengewicht je Meter, {name}, {stoff.name}", 2)
        self.berechnungen.append(Formel(
            id=d_g.id, ausgabe=d_g, funktion=_eigengewicht,
            vorlage=r"@rho \cdot @g \cdot @A",
            eingaben={"rho": stoff.id_von(DICHTE[stoff.art.value]), "g": g, "A": A},
            titel=f"Eigengewicht, «{name}» aus {stoff.name}", name="Eigengewicht eines Stabs",
            abschnitt=abschnitt))
        return Steifigkeit(querschnitt=q, material=material, EA=d_EA.id, EI=d_EI.id, g_k=d_g.id)

    def _eigengewicht(self, e: Eingaben) -> Dict[str, float]:
        """
        Je tragenden Stab ``g_k`` in N/m -- es kommt senkrecht ueber seine
        ganze Laenge in den Lastfall des Eigengewichts, je Meter Stab und
        nicht je Meter Projektion. Leer ohne diesen Lastfall.
        """
        if not self.eigengewicht:
            return {}
        g_k = {(s.querschnitt, s.material): e.g(f"g_k_{i}").si
               for i, s in enumerate(self.steifigkeiten)}
        return {stab.name: g_k[self.paare[stab.name]]
                for stab in self.system.staebe if stab.name in self.paare}

    def ins_rechenwerk(self, werk) -> "Balkensystem":
        for stoff in self.stoffe.values():
            stoff.ins_rechenwerk(werk)
        werk.definiere(*self.definitionen.values())
        werk.registriere(*self.berechnungen)
        return self

    def ziele(self) -> List[str]:
        """Was ein Lauf rechnen muss: jeder Querschnitt -- auch einer, den kein Stab nimmt -- und das System."""
        return [i for paar in self.flaechen.values() for i in paar] + [self.rechnung.id]

    # -- Rechnen ----------------------------------------------------------------

    def rechnen_und_schreiben(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        """
        Die Steifigkeiten in die Staebe, das System gerechnet, die Herleitung
        geschrieben. Haelt eine Meldung der Beschreibung die Rechnung auf,
        bleibt es bei ihr.
        """
        steif = {(s.querschnitt, s.material): (e.g(f"EA_{i}").si, e.g(f"EI_{i}").si)
                 for i, s in enumerate(self.steifigkeiten)}
        staebe = []
        for stab in self.system.staebe:
            paar = self.paare.get(stab.name)
            if paar is not None:
                EA, EI = steif[paar]
                stab = replace(stab, EA=EA, EI=EI)
            staebe.append(stab)
        eigen = self._eigengewicht(e)
        gerechnet = replace(self.system, staebe=staebe, lastfaelle=[
            replace(lf, lasten=[*(Stablast(stab=stab, art=Lastart.LINIENLAST, wert_a=g,
                                           richtung=Lastrichtung.SENKRECHT)
                                  for stab, g in eigen.items()), *lf.lasten])
            if lf.name == self.eigengewicht else lf
            for lf in self.system.lastfaelle])
        if any(m.fehler for m in self.meldungen):
            ergebnis = Ergebnis(meldungen=list(self.meldungen))
        else:
            ergebnis = rechnen(gerechnet)
            ergebnis.meldungen[:0] = self.meldungen
        befund = Systembefund(gerechnet, ergebnis, eigengewicht=eigen)
        herleitung.schreiben(p, self, befund)
        return Ausfuehrung({}, befund=befund)


def _derselbe(wert: Groesse) -> Groesse:
    return wert


def _eigengewicht(rho: Groesse, g: Groesse, A: Groesse) -> Groesse:
    return rho * g * A


def _dehnsteifigkeit(E: Groesse, A: Groesse) -> Groesse:
    return E * A


def _biegesteifigkeit(E: Groesse, I: Groesse) -> Groesse:
    return E * I
