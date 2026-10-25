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
sagt jeder Querschnitt selbst (:mod:`~opencivil.stabwerk.stabquerschnitt`):
nach Vorlage, von Hand, aus einer Platte oder aus einer
Querschnittsanalyse.

MATERIALIEN:
Ein Material der Staebe (:class:`Stabmaterial`) ist ein Beton des Projekts
oder ein eigenes mit E und Dichte von Hand (Benutzer, 2026-10-24). Ein Stab
kann auch das Material seines Querschnitts nehmen, den Beton einer Platte
oder Querschnittsanalyse.

STEIFIGKEIT -- NACH VORGABE, NICHT NACHGESCHLAGEN:
``E_cm`` eines Betons (:data:`BETONKENNWERTE`) oder E von Hand -- und bei
einem Stab mit dem Material seiner Querschnittsanalyse auf Wunsch deren
E_eq bei N und M (Benutzer, 2026-10-23) --, am ungerissenen
Bruttoquerschnitt, ohne Schubverformung, Gleichgewicht am unverformten
System. Die Herleitung sagt es, das TODO fuehrt es. Findet die Suche nach
E_eq keinen Modul, sagt es eine Meldung, und das System rechnet nicht.

EIGENGEWICHT -- NACH VORGABE DES BENUTZERS (2026-10-23):
Je Paar aus Querschnitt und Material ``g_k = rho · g · A`` in kN/m, mit
``g = 10 m/s²`` und beim Beton der Dichte des Stahlbetons -- ohne den Stahl
noch dazu. Es kommt als Last senkrecht je Meter Stab in den Lastfall, den
die Beschreibung dafuer nennt.

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
    Ausfuehrung, Befundbezug, Berechnung, Eingabebezug, Eingaben, Formel, Prozedur, Vorgabe,
)
from opencivil.core.einheiten import (
    KG_PRO_M3, KN_PRO_M, KNM2, M_PRO_S2, MN, N_PRO_MM2, Groesse,
)
from opencivil.core.protokoll import Abschnitt, Protokoll
from opencivil.core.wert import Quelle, WertDef
from opencivil.material.basis import Baustoff, mit_index
from opencivil.stabwerk import herleitung
from opencivil.stabwerk.modell import Lastart, Lastrichtung, Stablast, System
from opencivil.stabwerk.stabquerschnitt import Stabquerschnitt
from opencivil.stabwerk.system import Ergebnis, Fall, Meldung, rechnen
from opencivil.stabwerk.verlauf import Stabverlauf, verlaeufe

#: Welche Kennwerte eines Betons ein Stab aus ihm nimmt: ``E_cm`` -- nach
#: Vorgabe, nicht nachgeschlagen -- und die Dichte des Stahlbetons
#: (Benutzer, 2026-10-23).
BETONKENNWERTE = {"E": "E_cm", "rho": "rho_sb"}

#: Die Erdbeschleunigung des Eigengewichts -- 10 m/s² nach Vorgabe des
#: Benutzers (2026-10-23): so wiegt Stahlbeton 25 kN/m³.
ERDBESCHLEUNIGUNG = Groesse(10.0, M_PRO_S2)

#: Die Themen der Formelsammlung: was am Querschnitt haengt, und die Rechnung.
QUERSCHNITTE = "Stabquerschnitte"
STEIFIGKEITSMETHODE = "Steifigkeitsmethode"


@dataclass(frozen=True)
class Stabmaterial:
    """
    Ein Material der Staebe, aufgeloest: ein Beton -- E und Dichte von ihm --
    oder ein eigenes mit E und Dichte von Hand.
    """

    kennung: str
    """Im System, ``M1`` -- bei einem Stab mit dem Material seines Querschnitts dessen Zeichen."""

    name: str
    stoff: Optional[Baustoff] = None
    """Der Beton -- ``None`` bei einem eigenen Material."""

    E: float = 0.0
    """Von Hand, N/mm² -- nur ohne ``stoff``."""

    rho: float = 0.0
    """Von Hand, kg/m³ -- nur ohne ``stoff``."""

    vom_querschnitt: bool = False
    """Das Material des Querschnitts: dann gilt dessen E_eq, wenn er eines hat."""


@dataclass(frozen=True)
class Steifigkeit:
    """Ein Paar aus Querschnitt und Material und die Wert-IDs seiner Steifigkeiten."""

    querschnitt: str
    material: str
    """Die Kennung des :class:`Stabmaterial`."""

    EA: str
    EI: str
    g_k: str = ""
    """Das Eigengewicht je Meter -- leer, wenn kein Lastfall es bekommt."""

    mit_eq: bool = False
    """Ob E das E_eq des Querschnitts ist -- dann fehlen EA und EI, wo die Suche keines fand."""


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
                 paare: Mapping[str, Tuple[str, Stabmaterial]], meldungen: Sequence[Meldung],
                 querschnitte: Sequence[Stabquerschnitt],
                 eigengewicht: Optional[str] = None) -> None:
        """
        ``system`` ohne Steifigkeiten, wie die Beschreibung es baut;
        ``paare`` je tragenden Stab die Kennung seines Querschnitts und sein
        Material; ``eigengewicht`` der Lastfall, der das Eigengewicht der
        Staebe bekommt.
        """
        self.name = name
        self.kennung = kennung
        self.id = praefix
        self.system = system
        self.paare = dict(paare)
        self.meldungen = list(meldungen)
        self.querschnitte = list(querschnitte)
        self.eigengewicht = eigengewicht
        self.definitionen: Dict[str, WertDef] = {}
        self.berechnungen: List[Berechnung] = []
        self.flaechen: Dict[str, Tuple[str, str]] = {}
        """Je Querschnitt die Wert-IDs von ``A`` und ``I``."""

        self.module: Dict[str, str] = {}
        """Je Querschnitt mit E_eq die Wert-ID dieses E."""

        self.modulsuchen: Dict[str, str] = {}
        """Je Querschnitt mit E_eq die ID der Suche -- ihr Befund sagt, ob sie einen fand."""

        self.materialwerte: Dict[str, Tuple[str, str]] = {}
        """Je eigenes Material die Wert-IDs von E und Dichte."""

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
        return sorted({q.bauteil for q in self.querschnitte if q.bauteil})

    def _aufbauen(self) -> None:
        index = len(self.querschnitte) > 1
        for q in self.querschnitte:
            if not q.fehler:
                berechnungen, A, I = q.flaechenwerte(self._def, self.abschnitt(QUERSCHNITTE),
                                                     q.kennung if index else "")
                self.berechnungen += berechnungen
                self.flaechen[q.kennung] = (A, I)
                if q.modulfrage is not None:
                    berechnungen, E, suche = q.modulfrage.einbauen(
                        self._def, wo=f"{q.kennung}.", index=q.kennung if index else "",
                        name=q.name, abschnitt=self.abschnitt(QUERSCHNITTE))
                    self.berechnungen += berechnungen
                    self.module[q.kennung] = E
                    self.modulsuchen[q.kennung] = suche

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

        benutzt: Dict[Tuple[str, str], Stabmaterial] = {}
        for q, m in self.paare.values():
            benutzt.setdefault((q, m.kennung), m)
        mehrere_stoffe = len({m for _, m in benutzt}) > 1
        g = self._erdbeschleunigung() if self.eigengewicht and benutzt else None
        for (q, _), m in benutzt.items():
            # Das Material des Querschnitts traegt keinen Index: je
            # Querschnitt gibt es davon eines, und es kann wie ein Material
            # des Systems heissen -- mit Index stuenden zwei gleiche Zeichen da.
            teile = [q] if index else []
            if mehrere_stoffe and not m.vom_querschnitt:
                teile.append(m.name)
            self.steifigkeiten.append(self._steifigkeit(q, m, ",".join(teile), g))

        # Mit E_eq fehlen EA und EI, wo die Suche keinen Modul fand: dann
        # liest die Rechnung ihren Befund und sagt es.
        groessen = ("EA", "EI", "g_k") if g else ("EA", "EI")
        self.rechnung = SteifigkeitsmethodeProzedur(
            self, id=f"{self.id}.rechnung", ausgaben=[],
            bezuege=[Eingabebezug(f"{groesse}_{i}", getattr(s, groesse),
                                  optional=groesse != "g_k" and s.mit_eq)
                     for i, s in enumerate(self.steifigkeiten) for groesse in groessen],
            befunde=[Befundbezug(f"modul_{q}", suche) for q, suche in self.modulsuchen.items()],
            titel="Steifigkeitsmethode", abschnitt=self.abschnitt())
        """Die Prozedur, die das System rechnet -- ihr Befund ist der :class:`Systembefund`."""
        self.berechnungen.append(self.rechnung)

    def _kennwerte(self, m: Stabmaterial) -> Tuple[str, str]:
        """
        Die Wert-IDs von E und Dichte eines Materials: die seines Betons --
        oder bei einem eigenen Vorgaben von Hand, einmal je Material.
        """
        if m.stoff is not None:
            return m.stoff.id_von(BETONKENNWERTE["E"]), m.stoff.id_von(BETONKENNWERTE["rho"])
        if m.kennung not in self.materialwerte:
            ids = []
            for kurz, symbol, einheit, wert, beschreibung in (
                    ("E", "E", N_PRO_MM2, m.E, "E-Modul"),
                    ("rho", r"\rho", KG_PRO_M3, m.rho, "Dichte")):
                d = self._def(f"{m.kennung}.{kurz}", mit_index(symbol, m.name), einheit,
                              f"{beschreibung}, {m.name}", 0)
                self.berechnungen.append(Vorgabe(
                    id=d.id, ausgabe=d, groesse=Groesse(wert, einheit), quelle=Quelle.EINGABE,
                    titel=f"{beschreibung}, «{m.name}» (von Hand)",
                    abschnitt=self.abschnitt(QUERSCHNITTE)))
                ids.append(d.id)
            self.materialwerte[m.kennung] = (ids[0], ids[1])
        return self.materialwerte[m.kennung]

    def _erdbeschleunigung(self) -> str:
        """``g`` als Vorgabe des Systems -- seine Wert-ID."""
        d = self._def("g", "g", M_PRO_S2, "Erdbeschleunigung", 0)
        self.berechnungen.append(Vorgabe(
            id=d.id, ausgabe=d, groesse=ERDBESCHLEUNIGUNG, abschnitt=self.abschnitt(QUERSCHNITTE),
            titel="Erdbeschleunigung für das Eigengewicht (nach Vorgabe des Benutzers)"))
        return d.id

    def _steifigkeit(self, q: str, m: Stabmaterial, index: str,
                     g: Optional[str] = None) -> Steifigkeit:
        """
        EA und EI eines Paars aus Querschnitt und Material -- mit ``g`` dazu
        sein Eigengewicht. E und Dichte kommen vom Material; nimmt der Stab
        das Material seines Querschnitts und hat der ein E_eq, gilt dieses.
        """
        abschnitt = self.abschnitt(QUERSCHNITTE)
        modul, dichte = self._kennwerte(m)
        mit_eq = m.vom_querschnitt and q in self.module
        if mit_eq:
            modul = self.module[q]
        womit = "mit E_eq" if mit_eq else f"aus {m.name}"
        A, I = self.flaechen[q]
        name = next(x.name for x in self.querschnitte if x.kennung == q)
        wo = f"{q}.{m.kennung}."
        d_EA = self._def(wo + "EA", mit_index("EA", index), MN,
                         f"Dehnsteifigkeit, {name}, {m.name}", 0)
        d_EI = self._def(wo + "EI", mit_index("EI", index), KNM2,
                         f"Biegesteifigkeit, {name}, {m.name}", 0)
        self.berechnungen += [
            Formel(id=d_EA.id, ausgabe=d_EA, funktion=_dehnsteifigkeit,
                   vorlage=r"@E \cdot @A", eingaben={"E": modul, "A": A},
                   titel=f"Dehnsteifigkeit, «{name}» {womit}", name="Dehnsteifigkeit",
                   abschnitt=abschnitt),
            Formel(id=d_EI.id, ausgabe=d_EI, funktion=_biegesteifigkeit,
                   vorlage=r"@E \cdot @I", eingaben={"E": modul, "I": I},
                   titel=f"Biegesteifigkeit, «{name}» {womit}", name="Biegesteifigkeit",
                   abschnitt=abschnitt),
        ]
        if g is None:
            return Steifigkeit(querschnitt=q, material=m.kennung, EA=d_EA.id, EI=d_EI.id,
                               mit_eq=mit_eq)
        d_g = self._def(wo + "g_k", mit_index("g_k", index), KN_PRO_M,
                        f"Eigengewicht je Meter, {name}, {m.name}", 2)
        self.berechnungen.append(Formel(
            id=d_g.id, ausgabe=d_g, funktion=_eigengewicht,
            vorlage=r"@rho \cdot @g \cdot @A", eingaben={"rho": dichte, "g": g, "A": A},
            titel=f"Eigengewicht, «{name}» aus {m.name}", name="Eigengewicht eines Stabs",
            abschnitt=abschnitt))
        return Steifigkeit(querschnitt=q, material=m.kennung, EA=d_EA.id, EI=d_EI.id,
                           g_k=d_g.id, mit_eq=mit_eq)

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
        return {stab: g_k[q, m.kennung] for stab, (q, m) in self.paare.items()}

    def ins_rechenwerk(self, werk) -> "Balkensystem":
        betone = {id(m.stoff): m.stoff for _, m in self.paare.values() if m.stoff is not None}
        for stoff in betone.values():
            stoff.ins_rechenwerk(werk)
        werk.definiere(*self.definitionen.values())
        werk.registriere(*self.berechnungen)
        return self

    def ziele(self) -> List[str]:
        """
        Was ein Lauf rechnen muss: jeder Querschnitt -- auch einer, den kein
        Stab nimmt -- und das System. Von einem E_eq die Suche, nicht E: das
        fehlt, wo sie keinen Modul fand.
        """
        return ([i for paar in self.flaechen.values() for i in paar]
                + list(self.modulsuchen.values()) + [self.rechnung.id])

    # -- Rechnen ----------------------------------------------------------------

    def rechnen_und_schreiben(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        """
        Die Steifigkeiten in die Staebe, das System gerechnet, die Herleitung
        geschrieben. Haelt eine Meldung der Beschreibung die Rechnung auf --
        oder ein E_eq, das es nicht gibt --, bleibt es bei ihr.
        """
        meldungen = list(self.meldungen) + self._ohne_modul(e)
        steif = {(s.querschnitt, s.material): (e.g(f"EA_{i}").si, e.g(f"EI_{i}").si)
                 for i, s in enumerate(self.steifigkeiten) if e.hat(f"EA_{i}")}
        staebe = []
        for stab in self.system.staebe:
            q, m = self.paare.get(stab.name, ("", None))
            if m is not None and (q, m.kennung) in steif:
                EA, EI = steif[q, m.kennung]
                stab = replace(stab, EA=EA, EI=EI)
            staebe.append(stab)
        eigen = self._eigengewicht(e)
        gerechnet = replace(self.system, staebe=staebe, lastfaelle=[
            replace(lf, lasten=[*(Stablast(stab=stab, art=Lastart.LINIENLAST, wert_a=g,
                                           richtung=Lastrichtung.SENKRECHT)
                                  for stab, g in eigen.items()), *lf.lasten])
            if lf.name == self.eigengewicht else lf
            for lf in self.system.lastfaelle])
        if any(m.fehler for m in meldungen):
            ergebnis = Ergebnis(meldungen=meldungen)
        else:
            ergebnis = rechnen(gerechnet)
            ergebnis.meldungen[:0] = meldungen
        befund = Systembefund(gerechnet, ergebnis, eigengewicht=eigen)
        herleitung.schreiben(p, self, befund)
        return Ausfuehrung({}, befund=befund)

    def _ohne_modul(self, e: Eingaben) -> List[Meldung]:
        """
        Je Querschnitt, dessen Suche kein E_eq fand und den ein Stab mit
        seinem Material nimmt, eine Meldung.
        """
        meldungen = []
        for q in self.modulsuchen:
            befund = e.befund(f"modul_{q}")
            staebe = [stab for stab, (quer, m) in self.paare.items()
                      if quer == q and m.vom_querschnitt]
            if befund.stelle is None and staebe:
                name = next(x.name for x in self.querschnitte if x.kennung == q)
                meldungen.append(Meldung(f"Querschnitt «{name}»: kein E_eq – {befund.grund}",
                                         (q, *staebe), True))
        return meldungen


def _eigengewicht(rho: Groesse, g: Groesse, A: Groesse) -> Groesse:
    return rho * g * A


def _dehnsteifigkeit(E: Groesse, A: Groesse) -> Groesse:
    return E * A


def _biegesteifigkeit(E: Groesse, I: Groesse) -> Groesse:
    return E * I
