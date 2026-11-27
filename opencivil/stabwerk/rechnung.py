"""
opencivil/stabwerk/rechnung.py -- das Balkensystem im Rechenwerk.

VERANTWORTUNG:
Was ein Balkensystem im Rechenwerk anmeldet: je Querschnitt die Flaeche
``A`` und das Traegheitsmoment ``I``, je Paar aus Querschnitt und Material
die Dehn- und die Biegesteifigkeit ``EA`` und ``EI``, und eine Prozedur, die
das System nach der Steifigkeitsmethode rechnet
(:mod:`~opencivil.stabwerk.system`) und ihre Herleitung schreibt
(:mod:`~opencivil.stabwerk.herleitung`).

EBEN UND IM RAUM:
Das 3D-Balkensystem (:mod:`opencivil.stabwerk3d.rechnung`) tut dasselbe mit
mehr Kennwerten und Steifigkeiten -- ``I_y``, ``I_z`` und ``I_T``, ``EI_y``,
``EI_z`` und ``GI_T`` -- und rechnet im Raum. Was beide gleich tun, steht in
:class:`Stabwerksrechnung`: welche Kennwerte, Steifigkeiten und
Materialkennwerte, sagt je System eine Liste, ob eben oder im Raum seine
Art (:data:`~opencivil.stabwerk.art.EBENE`,
:data:`~opencivil.stabwerk.art.RAUM`) -- gerechnet wird mit demselben
Kern --, wie es sein Eigengewicht ansetzt und seine Herleitung schreibt,
eine Methode.

WOHER A UND I KOMMEN:
sagt jeder Querschnitt selbst (:mod:`~opencivil.stabwerk.stabquerschnitt`):
nach Vorlage, von Hand, aus einer Platte oder aus einer
Querschnittsanalyse.

MATERIALIEN:
Ein Material der Staebe (:class:`Stabmaterial`) ist ein Beton, Baustahl oder Holz
des Projekts oder ein eigenes mit E und Dichte von Hand (Benutzer,
2026-10-24). Ein Stab
kann auch das Material seines Querschnitts nehmen, den Beton einer Platte
oder Querschnittsanalyse.

STEIFIGKEIT -- NACH VORGABE, NICHT NACHGESCHLAGEN:
``E_cm`` eines Betons, ``E_a`` eines Baustahls (:data:`E_MODUL`) oder
E von Hand -- und bei
einem Stab mit dem Material seiner Querschnittsanalyse auf Wunsch deren
E_eq bei N und M (Benutzer, 2026-10-23) --, am ungerissenen
Bruttoquerschnitt, ohne Schubverformung, Gleichgewicht am unverformten
System. Die Herleitung sagt es, das TODO fuehrt es. Findet die Suche nach
E_eq keinen Modul, sagt es eine Meldung, und das System rechnet nicht.

EIGENGEWICHT -- NACH VORGABE DES BENUTZERS (2026-10-23):
Je Paar aus Querschnitt und Material ``g_k = rho · g · A`` in kN/m, mit
``g = 10 m/s²`` und beim Beton der Dichte des Stahlbetons -- ohne den Stahl
noch dazu --, beim Baustahl mit ``rho_a``. Es kommt als Last senkrecht je Meter Stab in den Lastfall, den
die Beschreibung dafuer nennt.

DAS ERGEBNIS:
kommt als Befund in die Loesung (:class:`Systembefund`); Zusammenfassung,
Bilder und Zwischenspeicher lesen es dort. Einen Wert liefert die Prozedur
nicht: sie ist Ziel unter ihrer ID. Ein bewegliches System ist ein Ergebnis
mit Meldung und keine Ausnahme: der Rest des Projekts rechnet weiter.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Ausfuehrung, Befundbezug, Berechnung, Eingabebezug, Eingaben, Formel, Prozedur, Vorgabe,
)
from opencivil.core.einheiten import (
    KG_PRO_M3, KN_PRO_M, KNM2, M_PRO_S2, MN, N_PRO_MM2, Einheit, Groesse,
)
from opencivil.core.protokoll import Abschnitt, Protokoll
from opencivil.core.rechenobjekt import Rechenobjekt
from opencivil.core.wert import Quelle, WertDef
from opencivil.material.basis import Baustoff, Baustoffart, mit_index
from opencivil.stabwerk import herleitung
from opencivil.stabwerk.modell import Lastart, Lastrichtung, Stablast, System
from opencivil.stabwerk.stabquerschnitt import (
    DEVIATIONSMOMENT, EBEN, Kennwert, Stabquerschnitt, keine_hauptachsen,
)
from opencivil.stabwerk.art import EBENE, Art
from opencivil.stabwerk.system import Ergebnis, Fall, Meldung, rechnen
from opencivil.stabwerk.verlauf import Stabverlauf, verlaeufe


@dataclass(frozen=True)
class Materialkennwert:
    """
    Ein Kennwert, den ein Stab von seinem Material nimmt: je Art des
    Baustoffs, welcher es ist, und wie er bei einem eigenen Material von
    Hand heisst -- ``kurzname`` ist auch sein Feld dort.
    """

    kurzname: str
    symbol: str
    einheit: Einheit
    beschreibung: str
    je_stoff: Mapping[Baustoffart, str]


#: Beim Beton ``E_cm`` -- die Analyse rechnet in der Regel ungerissen
#: (SIA 262:2025, 4.1.4.1.3), mit dem Mittelwert --, beim Baustahl ``E_a``,
#: beim Holz der Mittelwert in Faserrichtung (SIA 265:2012, 2.1.5).
E_MODUL = Materialkennwert("E", "E", N_PRO_MM2, "E-Modul",
                           {Baustoffart.BETON: "E_cm", Baustoffart.BAUSTAHL: "E_a",
                            Baustoffart.HOLZ: "E_0_mean"})

#: Fuer das Eigengewicht: beim Beton die Dichte des Stahlbetons (Benutzer,
#: 2026-10-23), beim Holz die aus der mittleren Raumlast nach SIA 261.
DICHTE = Materialkennwert("rho", r"\rho", KG_PRO_M3, "Dichte",
                          {Baustoffart.BETON: "rho_sb", Baustoffart.BAUSTAHL: "rho_a",
                           Baustoffart.HOLZ: "rho_mean"})

#: Fuer die Torsion, nur im Raum: ``G_cm`` des Betons, ``G_a`` des Baustahls,
#: der Mittelwert ``G_mean`` des Holzes.
SCHUBMODUL = Materialkennwert("G", "G", N_PRO_MM2, "Schubmodul",
                              {Baustoffart.BETON: "G_cm", Baustoffart.BAUSTAHL: "G_a",
                               Baustoffart.HOLZ: "G_mean"})


def stoffkennwerte(kennwerte: Sequence[Materialkennwert]) -> Dict[Baustoffart, Dict[str, str]]:
    """Je Art des Baustoffs, welche seiner Kennwerte ein Stab nimmt: ``{BETON: {"E": "E_cm"}}``."""
    return {art: {k.kurzname: k.je_stoff[art] for k in kennwerte}
            for art in kennwerte[0].je_stoff}


#: Welche Kennwerte eines Baustoffs ein Stab in der Ebene aus ihm nimmt.
STABKENNWERTE = stoffkennwerte((E_MODUL, DICHTE))

#: Die Erdbeschleunigung des Eigengewichts -- 10 m/s² nach Vorgabe des
#: Benutzers (2026-10-23): so wiegt Stahlbeton 25 kN/m³.
ERDBESCHLEUNIGUNG = Groesse(10.0, M_PRO_S2)

#: Die Themen der Formelsammlung: was am Querschnitt haengt, und die Rechnung.
QUERSCHNITTE = "Stabquerschnitte"
STEIFIGKEITSMETHODE = "Steifigkeitsmethode"


@dataclass(frozen=True)
class Steifigkeitsformel:
    """
    Eine Steifigkeit eines Stabs: ein Modul seines Materials mal ein
    Kennwert seines Querschnitts. ``kurzname`` heisst auch das Feld des
    Stabs im Rechenkern, ``beschreibung`` auch die Formel.
    """

    kurzname: str
    einheit: Einheit
    beschreibung: str
    modul: str
    """``E`` oder ``G`` -- ein :class:`Materialkennwert`."""

    kennwert: str
    """Ein Kennwert des Querschnitts: ``A``, ``I``, ``I_T`` ..."""


DEHNSTEIFIGKEIT = Steifigkeitsformel("EA", MN, "Dehnsteifigkeit", "E", "A")


@dataclass(frozen=True)
class Stabmaterial:
    """
    Ein Material der Staebe, aufgeloest: ein Beton, Baustahl oder Holz -- seine
    Kennwerte von ihm -- oder ein eigenes mit Kennwerten von Hand.
    """

    kennung: str
    """Im System, ``M1`` -- bei einem Stab mit dem Material seines Querschnitts dessen Zeichen."""

    name: str
    stoff: Optional[Baustoff] = None
    """Der Beton, Baustahl oder das Holz -- ``None`` bei einem eigenen Material."""

    werte: Mapping[str, float] = field(default_factory=dict)
    """Von Hand, je :class:`Materialkennwert` in seiner Einheit -- nur ohne ``stoff``."""

    vom_querschnitt: bool = False
    """Das Material des Querschnitts: dann gilt dessen E_eq, wenn er eines hat."""


@dataclass(frozen=True)
class Steifigkeit:
    """Ein Paar aus Querschnitt und Material und die Wert-IDs seiner Steifigkeiten."""

    querschnitt: str
    material: str
    """Die Kennung des :class:`Stabmaterial`."""

    werte: Mapping[str, str]
    """Je :class:`Steifigkeitsformel` die Wert-ID: ``{"EA": ..., "EI": ...}``."""

    g_k: str = ""
    """Das Eigengewicht je Meter -- leer, wenn kein Lastfall es bekommt."""

    mit_eq: bool = False
    """Ob E das E_eq des Querschnitts ist -- dann fehlen die Steifigkeiten, wo die Suche keines fand."""


@dataclass(frozen=True)
class Lagerkraft:
    """
    Eine Zeile der Lagerkraefte eines Falls, auf das Tragwerk wirkend -- in
    Herleitung und Bildschirm dieselbe.
    """

    wo: str
    """«A1 (K1)», «L2 bei 1.500 m», «L2: Bettung, Summe»."""

    werte: Tuple[float, ...]
    """Wie der Rechenkern sie gibt: ``(R_x, R_z, M)`` in der Ebene, sechs im Raum -- in N und Nm."""

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
        for name, werte in fall.lagerkraefte.items():
            ort = orte[name]
            if ort.knoten:
                wo = (", ".join(lager_an[ort.knoten]) + f" ({ort.knoten})"
                      if ort.knoten in lager_an else ort.knoten)
            else:
                wo = f"{ort.stab} bei {ort.stelle:.3f} m"
            zeilen.append(Lagerkraft(wo, tuple(werte), knoten=ort.knoten))
        for stab, werte in fall.linienlast.items():
            zeilen.append(Lagerkraft(f"{stab}: Lasten geradewegs ins Linienlager",
                                     tuple(werte), summe=True))
        for stab, werte in fall.bettung.items():
            zeilen.append(Lagerkraft(f"{stab}: Bettung, Summe", tuple(werte), summe=True))
        return zeilen


class SteifigkeitsmethodeProzedur(Prozedur):
    """Das ganze System, gerechnet und aufgeschrieben."""

    THEMA = STEIFIGKEITSMETHODE

    def __init__(self, system: "Stabwerksrechnung", **kwargs) -> None:
        super().__init__(**kwargs)
        self.system = system

    def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        return self.system.rechnen_und_schreiben(e, p)


class Stabwerksrechnung(Rechenobjekt):
    """
    Ein Balkensystem, fertig fuer das Rechenwerk -- was die Ebene und der
    Raum gleich tun, siehe Dateikopf. Je System sagen die Klassenattribute,
    welche Kennwerte, Steifigkeiten und Materialkennwerte es hat und wie es
    rechnet, und die Methoden ``_eigenlast`` und ``_schreiben``, wie sein
    Eigengewicht als Last aussieht und wie es seine Herleitung schreibt.
    """

    KENNWERTE: Tuple[Kennwert, ...]
    """Was ein Querschnitt liefert (:mod:`~opencivil.stabwerk.stabquerschnitt`)."""

    STEIFIGKEITEN: Tuple[Steifigkeitsformel, ...]
    MATERIALKENNWERTE: Tuple[Materialkennwert, ...]
    ART: Art
    """Eben oder im Raum (:mod:`~opencivil.stabwerk.art`)."""

    def __init__(self, *, name: str, kennung: str, praefix: str, system: Any,
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
        self.flaechen: Dict[str, Dict[str, str]] = {}
        """Je Querschnitt die Wert-IDs seiner :attr:`KENNWERTE` -- eine Analyse im Raum mit ``I_yz``."""

        self.module: Dict[str, str] = {}
        """Je Querschnitt mit E_eq die Wert-ID dieses E."""

        self.modulsuchen: Dict[str, str] = {}
        """Je Querschnitt mit E_eq die ID der Suche -- ihr Befund sagt, ob sie einen fand."""

        self.materialwerte: Dict[str, Dict[str, str]] = {}
        """Je eigenes Material die Wert-IDs seiner :attr:`MATERIALKENNWERTE`."""

        self.steifigkeiten: List[Steifigkeit] = []
        self._aufbauen()

    # -- Rechenwerk ------------------------------------------------------------

    def abschnitt(self, thema: str = STEIFIGKEITSMETHODE) -> Abschnitt:
        """Ein Abschnitt fuer alles -- das Thema sagt nur, wo die Formeln gesammelt stehen."""
        return Abschnitt(f"{self.WAS}: {self.name}", self.id, thema=thema)

    def _def(self, kurzname: str, symbol: str, einheit, beschreibung: str,
             stellen: int) -> WertDef:
        d = WertDef(id=f"{self.id}.{kurzname}", symbol=symbol, einheit=einheit,
                    beschreibung=beschreibung, stellen=stellen)
        self.definitionen[kurzname] = d
        return d

    def _aufbauen(self) -> None:
        index = len(self.querschnitte) > 1
        for q in self.querschnitte:
            if not q.fehler:
                berechnungen, werte = q.flaechenwerte(self._def, self.abschnitt(QUERSCHNITTE),
                                                      q.kennung if index else "",
                                                      kennwerte=self.KENNWERTE)
                self.berechnungen += berechnungen
                self.flaechen[q.kennung] = werte
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

        # Mit E_eq fehlen die Steifigkeiten, wo die Suche keinen Modul fand:
        # dann liest die Rechnung ihren Befund und sagt es.
        bezuege = []
        for i, s in enumerate(self.steifigkeiten):
            bezuege += [Eingabebezug(f"{k}_{i}", wert, optional=s.mit_eq)
                        for k, wert in s.werte.items()]
            if s.g_k:
                bezuege.append(Eingabebezug(f"g_k_{i}", s.g_k))
        # Wo ein Querschnitt I_yz mitbringt, prueft die Rechnung die Hauptachsen.
        for q, werte in self.flaechen.items():
            if DEVIATIONSMOMENT.kurzname in werte:
                bezuege += [Eingabebezug(f"{k}_{q}", werte[k]) for k in ("I_y", "I_z", "I_yz")]
        self.rechnung = SteifigkeitsmethodeProzedur(
            self, id=f"{self.id}.rechnung", ausgaben=[], bezuege=bezuege,
            befunde=[Befundbezug(f"modul_{q}", suche) for q, suche in self.modulsuchen.items()],
            titel="Steifigkeitsmethode", abschnitt=self.abschnitt())
        """Die Prozedur, die das System rechnet -- ihr Befund ist der :class:`Systembefund`."""
        self.berechnungen.append(self.rechnung)

    def _kennwerte(self, m: Stabmaterial) -> Dict[str, str]:
        """
        Die Wert-IDs der :attr:`MATERIALKENNWERTE` eines Materials: die
        seines Baustoffs -- oder bei einem eigenen Vorgaben von Hand, einmal
        je Material.
        """
        if m.stoff is not None:
            return {k.kurzname: m.stoff.id_von(k.je_stoff[m.stoff.art])
                    for k in self.MATERIALKENNWERTE}
        if m.kennung not in self.materialwerte:
            ids = {}
            for k in self.MATERIALKENNWERTE:
                d = self._def(f"{m.kennung}.{k.kurzname}", mit_index(k.symbol, m.name),
                              k.einheit, f"{k.beschreibung}, {m.name}", 0)
                self.berechnungen.append(Vorgabe(
                    id=d.id, ausgabe=d, groesse=Groesse(m.werte[k.kurzname], k.einheit),
                    quelle=Quelle.EINGABE, titel=f"{k.beschreibung}, «{m.name}» (von Hand)",
                    abschnitt=self.abschnitt(QUERSCHNITTE)))
                ids[k.kurzname] = d.id
            self.materialwerte[m.kennung] = ids
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
        Die :attr:`STEIFIGKEITEN` eines Paars aus Querschnitt und Material --
        mit ``g`` dazu sein Eigengewicht. Module und Dichte kommen vom
        Material; nimmt der Stab das Material seines Querschnitts und hat der
        ein E_eq, gilt dieses.
        """
        abschnitt = self.abschnitt(QUERSCHNITTE)
        modul = self._kennwerte(m)
        mit_eq = m.vom_querschnitt and q in self.module
        if mit_eq:
            modul = {**modul, "E": self.module[q]}
        womit = "mit E_eq" if mit_eq else f"aus {m.name}"
        kennwerte = self.flaechen[q]
        name = next(x.name for x in self.querschnitte if x.kennung == q)
        wo = f"{q}.{m.kennung}."
        werte = {}
        for s in self.STEIFIGKEITEN:
            d = self._def(wo + s.kurzname, mit_index(s.kurzname, index), s.einheit,
                          f"{s.beschreibung}, {name}, {m.name}", 0)
            self.berechnungen.append(Formel(
                id=d.id, ausgabe=d, funktion=_modul_mal_kennwert,
                vorlage=rf"@{s.modul} \cdot @{s.kennwert}",
                eingaben={s.modul: modul[s.modul], s.kennwert: kennwerte[s.kennwert]},
                titel=f"{s.beschreibung}, «{name}» {womit}", name=s.beschreibung,
                abschnitt=abschnitt))
            werte[s.kurzname] = d.id
        if g is None:
            return Steifigkeit(querschnitt=q, material=m.kennung, werte=werte, mit_eq=mit_eq)
        d_g = self._def(wo + "g_k", mit_index("g_k", index), KN_PRO_M,
                        f"Eigengewicht je Meter, {name}, {m.name}", 2)
        self.berechnungen.append(Formel(
            id=d_g.id, ausgabe=d_g, funktion=_gewicht_je_meter,
            vorlage=r"@rho \cdot @g \cdot @A",
            eingaben={"rho": modul["rho"], "g": g, "A": kennwerte["A"]},
            titel=f"Eigengewicht, «{name}» aus {m.name}", name="Eigengewicht eines Stabs",
            abschnitt=abschnitt))
        return Steifigkeit(querschnitt=q, material=m.kennung, werte=werte, g_k=d_g.id,
                           mit_eq=mit_eq)

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

    @property
    def baustoffe(self) -> List[Baustoff]:
        """Die Betone der Stäbe, jeder einmal -- eigene Materialien bringen ihre Werte selbst."""
        return list({id(m.stoff): m.stoff for _, m in self.paare.values()
                     if m.stoff is not None}.values())

    def ziele(self) -> List[str]:
        """
        Was ein Lauf rechnen muss: jeder Querschnitt -- auch einer, den kein
        Stab nimmt -- und das System. Von einem E_eq die Suche, nicht E: das
        fehlt, wo sie keinen Modul fand.
        """
        return ([i for werte in self.flaechen.values() for i in werte.values()]
                + list(self.modulsuchen.values()) + [self.rechnung.id])

    # -- Rechnen ----------------------------------------------------------------

    def rechnen_und_schreiben(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        """
        Die Steifigkeiten in die Staebe, das System gerechnet, die Herleitung
        geschrieben. Haelt eine Meldung der Beschreibung die Rechnung auf --
        oder ein E_eq, das es nicht gibt --, bleibt es bei ihr.
        """
        meldungen = list(self.meldungen) + self._ohne_modul(e) + self._keine_hauptachsen(e)
        steif = {(s.querschnitt, s.material): {k: e.g(f"{k}_{i}").si for k in s.werte}
                 for i, s in enumerate(self.steifigkeiten)
                 if all(e.hat(f"{k}_{i}") for k in s.werte)}
        staebe = []
        for stab in self.system.staebe:
            q, m = self.paare.get(stab.name, ("", None))
            if m is not None and (q, m.kennung) in steif:
                stab = replace(stab, **steif[q, m.kennung])
            staebe.append(stab)
        eigen = self._eigengewicht(e)
        gerechnet = replace(self.system, staebe=staebe, lastfaelle=[
            replace(lf, lasten=[*(self._eigenlast(stab, g) for stab, g in eigen.items()),
                                *lf.lasten])
            if lf.name == self.eigengewicht else lf
            for lf in self.system.lastfaelle])
        if any(m.haelt_an for m in meldungen):
            ergebnis = Ergebnis(self.ART, meldungen=meldungen)
        else:
            ergebnis = rechnen(gerechnet, self.ART)
            ergebnis.meldungen[:0] = meldungen
        befund = Systembefund(gerechnet, ergebnis, eigengewicht=eigen)
        self._schreiben(p, befund)
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

    def _keine_hauptachsen(self, e: Eingaben) -> List[Meldung]:
        """
        Je Querschnitt mit ``I_yz``, den ein Stab nimmt und dessen y und z
        merklich keine Hauptachsen sind (:func:`keine_hauptachsen`), ein Hinweis --
        er haelt die Rechnung nicht auf.
        """
        meldungen = []
        for q in self.querschnitte:
            if DEVIATIONSMOMENT.kurzname not in self.flaechen.get(q.kennung, {}):
                continue
            staebe = [stab for stab, (quer, _) in self.paare.items() if quer == q.kennung]
            if not staebe:
                continue
            text = keine_hauptachsen(f"Querschnitt «{q.name}»", *(
                e.g(f"{k}_{q.kennung}").si for k in ("I_y", "I_z", "I_yz")))
            if text is not None:
                meldungen.append(Meldung(text, (q.kennung, *staebe), False))
        return meldungen

    # -- Je System ----------------------------------------------------------------

    def _eigenlast(self, stab: str, g: float) -> Any:
        """Das Eigengewicht eines Stabs als Last seines Systems: senkrecht, ``g`` in N/m."""
        raise NotImplementedError

    def _schreiben(self, p: Protokoll, befund: Systembefund) -> None:
        """Die Herleitung."""
        raise NotImplementedError


class Balkensystem(Stabwerksrechnung):
    """Ein ebenes Balkensystem, fertig fuer das Rechenwerk."""

    WAS = "Balkensystem"
    KENNWERTE = EBEN
    STEIFIGKEITEN = (DEHNSTEIFIGKEIT, Steifigkeitsformel("EI", KNM2, "Biegesteifigkeit", "E", "I"))
    MATERIALKENNWERTE = (E_MODUL, DICHTE)
    ART = EBENE

    def _eigenlast(self, stab: str, g: float) -> Stablast:
        return Stablast(stab=stab, art=Lastart.LINIENLAST, wert_a=g,
                        richtung=Lastrichtung.SENKRECHT)

    def _schreiben(self, p: Protokoll, befund: Systembefund) -> None:
        herleitung.schreiben(p, self, befund)


def _gewicht_je_meter(rho: Groesse, g: Groesse, A: Groesse) -> Groesse:
    """Das Eigengewicht eines Stabs je Meter: Dichte mal g mal Flaeche."""
    return rho * g * A


def _modul_mal_kennwert(**faktoren: Groesse) -> Groesse:
    """Modul mal Kennwert (:class:`Steifigkeitsformel`)."""
    modul, kennwert = faktoren.values()
    return modul * kennwert
