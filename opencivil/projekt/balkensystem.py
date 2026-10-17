"""
opencivil/projekt/balkensystem.py -- ein 2D-Balkensystem, wie die Oberflaeche es beschreibt.

VERANTWORTUNG:
Der :class:`BalkensystemEintrag`: ein ebener Rahmen aus Knoten und Linien,
Lagern und Lasten, mit seinen Querschnitten, Lastfaellen und Kombinationen
-- als speicherbare Datenklasse wie die Querschnittsanalyse
(:mod:`opencivil.projekt.querschnittsanalyse`). Dazu der Baukasten, der ohne
Oberflaeche zeichnet, und was beim Teilen und Umkehren einer Linie mit ihren
Lasten geschieht. Gerechnet wird in :mod:`opencivil.stabwerk`.

ZUERST GEOMETRIE:
Gezeichnet werden Knoten und Linien. Eine Linie wird zum Stab, sobald sie
Querschnitt und Material hat (``stab``); sie kann daneben -- oder statt dessen
-- ein Linienlager sein, quer und laengs je frei, fest oder federnd. Ein
Knoten wird zum Lager durch ein :class:`LagerEintrag` an ihm, nicht durch ein
Feld am Knoten: das Zeichenfenster fuehrt Knoten zusammen und legt neue an,
und ein Feld daran ginge dabei verloren.

LASTEN AN IHREN ELEMENTEN:
Eine Last auf einem Stab steht an seiner Linie (``lasten``), mit dem
Lastfall, zu dem sie gehoert. So bleibt sie bei der Linie, wenn diese
kopiert, geloescht oder rueckgaengig gemacht wird. Eine Last an einem Knoten
ist -- wie ein Lager -- ein eigener Eintrag an ihm.

KOORDINATEN UND EINHEITEN:
x nach rechts, z nach oben, in m; Stellen auf einem Stab in m ab seinem
Anfang. Querschnittsmasse in mm, A in mm², I in 10⁶ mm⁴. Lasten in kN, kN/m,
kNm und kNm/m; Federn in kN/m und kNm/rad, Bettung in kN/m². Umgerechnet
wird beim Bauen.

VORZEICHEN:
Eine Kraftlast ist positiv in ihrer Richtung: «senkrecht» nach unten,
«waagrecht» nach rechts, «quer» zur gestrichelten Faser, «laengs» vom Anfang
zum Ende. Momente drehen im Gegenuhrzeigersinn (:mod:`opencivil.stabwerk.modell`).
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from opencivil.core.einheiten import (
    KN, KN_PRO_M, KN_PRO_M2, KNM, KNM_PRO_M, KNM_PRO_RAD, Groesse,
)
from opencivil.projekt.eintraege import Beschreibung
from opencivil.projekt.lesen import ProjektFehler, einer_von
from opencivil.projekt.netz import Netz, naechste_kennung
from opencivil.stabwerk import querschnitte as qs
from opencivil.stabwerk.modell import (
    FEST, Kombination, Knoten, Knotenlast, Lager, Lastart, Lastfall, Lastrichtung, Stab,
    Stablast, System,
)
from opencivil.stabwerk.system import Meldung

#: Wie ein Lager oder Linienlager je Richtung haelt.
HALT = ("frei", "fest", "feder")

#: Die Einheit jeder Last in der Beschreibung, nach ihrer Art -- an einem
#: Stab oder Knoten. Umgerechnet wird beim Bauen, mit diesen.
EINHEIT_DER_LAST = {
    Lastart.LINIENLAST: KN_PRO_M, Lastart.EINZELLAST: KN,
    Lastart.MOMENT: KNM, Lastart.LINIENMOMENT: KNM_PRO_M, "kraft": KN,
}

#: Die Einheit jeder Feder, nach ihrem Feld: Lager in kN/m und kNm/rad,
#: Bettung in kN/m je m Stab.
EINHEIT_DER_FEDER = {"k_x": KN_PRO_M, "k_z": KN_PRO_M, "k_phi": KNM_PRO_RAD,
                     "k_quer": KN_PRO_M2, "k_laengs": KN_PRO_M2}

#: Was fuer Lasten an einem Knoten liegen koennen; an einem Stab jede :class:`Lastart`.
KNOTENLASTEN = ("kraft", "moment")

#: Wohin eine Kraft an einem Knoten zeigt -- nur senkrecht oder waagrecht.
KNOTENRICHTUNGEN = (Lastrichtung.SENKRECHT, Lastrichtung.WAAGRECHT)

#: Woher ein Querschnitt kommt.
QUERSCHNITTSARTEN = ("vorlage", "kennwerte", "platte", "analyse")

#: Die Kennwerte eines Querschnitts von Hand: A in mm², I in 10⁶ mm⁴.
KENNWERTE = ("A", "I")

#: Die Vorwahlen eines Lagers -- je Richtung frei oder fest.
LAGERARTEN = {
    "gelenkig": ("fest", "fest", "frei"),
    "verschieblich": ("frei", "fest", "frei"),
    "eingespannt": ("fest", "fest", "fest"),
}

#: Ein Punkt in m -- oder die Kennung eines Knotens, der dort liegt.
Ort = Union[str, Sequence[float]]


def _kennung_von(eintrag: Any) -> str:
    return eintrag if isinstance(eintrag, str) else eintrag.kennung


# ===========================================================================
# Die Teile
# ===========================================================================


@dataclass
class SystemknotenEintrag(Beschreibung):
    """Ein Punkt des Systems, in m."""

    kennung: str = ""
    x: float = 0.0
    z: float = 0.0


@dataclass
class StablastEintrag(Beschreibung):
    """
    Eine Last auf einem Stab, in einem Lastfall -- in der Einheit ihrer Art
    (:data:`EINHEIT_DER_LAST`). ``wert_b`` gilt am Ende des belasteten
    Bereichs, leer: wie ``wert_a``. ``bis`` leer: bis zum Ende des Stabs.
    Einzellast und Einzelmoment stehen bei ``von``.
    """

    lastfall: str = ""
    art: Lastart = Lastart.LINIENLAST
    richtung: Lastrichtung = Lastrichtung.SENKRECHT
    wert_a: float = 10.0
    wert_b: Optional[float] = None
    von: float = 0.0
    bis: Optional[float] = None
    projiziert: bool = False
    """Senkrecht und waagrecht je Meter Projektion statt je Meter Stab."""

    @property
    def verteilt(self) -> bool:
        return self.art.verteilt


@dataclass
class SystemlinieEintrag(Beschreibung):
    """
    Eine Linie des Systems: ein Stab, wenn ``stab``; dazu, oder ohne Stab,
    ein Linienlager quer und laengs.
    """

    kennung: str = ""
    von: str = ""
    bis: str = ""
    stab: bool = False
    querschnitt: str = ""
    """Kennung des Querschnitts im System (``Q1``)."""

    material: str = ""
    """Kennung des Materials im Projekt (``b1``)."""

    gelenk_anfang: bool = False
    gelenk_ende: bool = False
    quer: str = einer_von(HALT, "frei")
    k_quer: float = 0.0
    """Bettung quer, kN/m²."""

    laengs: str = einer_von(HALT, "frei")
    k_laengs: float = 0.0
    lasten: List[StablastEintrag] = field(default_factory=list)


@dataclass
class LagerEintrag(Beschreibung):
    """Ein Lager an einem Knoten: je Richtung frei, fest oder Feder."""

    kennung: str = ""
    knoten: str = ""
    x: str = einer_von(HALT, "fest")
    k_x: float = 0.0
    """kN/m."""

    z: str = einer_von(HALT, "fest")
    k_z: float = 0.0
    phi: str = einer_von(HALT, "frei")
    k_phi: float = 0.0
    """kNm/rad."""


@dataclass
class KnotenlastEintrag(Beschreibung):
    """Eine Last an einem Knoten, in einem Lastfall: eine Kraft mit Richtung oder ein Moment."""

    kennung: str = ""
    knoten: str = ""
    lastfall: str = ""
    art: str = einer_von(KNOTENLASTEN, "kraft")
    richtung: Lastrichtung = einer_von(KNOTENRICHTUNGEN, Lastrichtung.SENKRECHT)
    wert: float = 10.0
    """kN oder kNm."""


@dataclass
class StabquerschnittEintrag(Beschreibung):
    """
    Ein Querschnitt der Staebe: nach Vorlage mit Massen in mm, mit Kennwerten
    von Hand (``A`` in mm², ``I`` in 10⁶ mm⁴), oder aus einer Platte oder
    einer Querschnittsanalyse des Projekts (``bezug``).
    """

    kennung: str = ""
    name: str = ""
    art: str = einer_von(QUERSCHNITTSARTEN, "vorlage")
    vorlage: str = einer_von((v.schluessel for v in qs.VORLAGEN), qs.RECHTECK.schluessel)
    masse: Dict[str, float] = field(default_factory=dict)
    bezug: str = ""

    def stabvorlage(self) -> qs.Stabvorlage:
        return qs.vorlage(self.vorlage)

    def masse_mit_vorgaben(self) -> Dict[str, float]:
        """Die Masse der Vorlage -- was fehlt, mit ihrer Vorgabe."""
        return {**self.stabvorlage().vorgaben(), **self.masse}

    def fehler(self) -> Optional[str]:
        """
        Was an Massen oder Kennwerten nicht geht -- ``None``, wenn alles geht.
        Ein Mass, das die Vorlage nicht kennt, ist ein Tippfehler: bis
        2026-10-16 stand ``B=500`` still da, und gerechnet wurde mit b = 300.
        """
        if self.art == "vorlage":
            vorlage = self.stabvorlage()
            fremd = [k for k in self.masse if k not in vorlage.vorgaben()]
            if fremd:
                return (f"ein Mass «{fremd[0]}» gibt es bei «{vorlage.name}» nicht. "
                        f"Möglich sind: {', '.join(vorlage.vorgaben())}.")
            return vorlage.pruefen(self.masse_mit_vorgaben())
        if self.art == "kennwerte":
            fremd = [k for k in self.masse if k not in KENNWERTE]
            if fremd:
                return (f"einen Kennwert «{fremd[0]}» gibt es nicht. "
                        f"Möglich sind: {', '.join(KENNWERTE)}.")
            if not (self.masse.get("A", 0.0) > 0.0 and self.masse.get("I", 0.0) > 0.0):
                return "A und I müssen grösser als null sein."
        return None


@dataclass
class LastfallEintrag(Beschreibung):
    """Ein Lastfall des Systems: eine Kennung, auf die die Lasten zeigen, und ein Name."""

    kennung: str = ""
    name: str = ""


@dataclass
class LastkombinationEintrag(Beschreibung):
    """Eine Kombination: je Lastfall (Kennung) ein Beiwert, von Hand."""

    kennung: str = ""
    name: str = ""
    faktoren: Dict[str, float] = field(default_factory=dict)


# ===========================================================================
# Das System
# ===========================================================================


@dataclass
class Modell:
    """
    Das Stabwerk der Beschreibung, in N, m und rad -- noch ohne
    Steifigkeiten: ``EA`` und ``EI`` jedes Stabs kommen aus dem Rechenwerk,
    je Paar aus Querschnitt und Material (``paare``). Was sich nicht
    uebersetzen laesst, steht in ``meldungen``, wie die des Rechenkerns.
    """

    system: System
    paare: Dict[str, Tuple[str, str]] = field(default_factory=dict)
    """Je tragenden Stab die Kennungen seines Querschnitts und seines Materials."""

    meldungen: List[Meldung] = field(default_factory=list)

    @property
    def gueltig(self) -> bool:
        return not any(m.fehler for m in self.meldungen)


@dataclass
class BalkensystemEintrag(Beschreibung):
    """
    Ein ebener Rahmen: Knoten, Linien, Lager, Lasten, Querschnitte, Lastfaelle, Kombinationen.

    Ohne Regeln, die das ganze Projekt aufhielten: was an einem System nicht
    stimmt -- auch zwei Faelle gleichen Namens --, steht in seinen Meldungen
    (:meth:`modell`), und die anderen Bauteile rechnen weiter.
    """

    BEZEICHNUNG = "Balkensystem"

    kennung: str
    name: str
    knoten: List[SystemknotenEintrag] = field(default_factory=list)
    linien: List[SystemlinieEintrag] = field(default_factory=list)
    lager: List[LagerEintrag] = field(default_factory=list)
    knotenlasten: List[KnotenlastEintrag] = field(default_factory=list)
    querschnitte: List[StabquerschnittEintrag] = field(default_factory=list)
    lastfaelle: List[LastfallEintrag] = field(default_factory=list)
    kombinationen: List[LastkombinationEintrag] = field(default_factory=list)
    beschreibung: str = ""
    """Freier Text -- geht in keine Rechnung ein."""

    # -- Zugriff -------------------------------------------------------------

    def materialien(self) -> List[str]:
        """
        Jedes Material, auf das eine Linie zeigt. Jeder Verweis zaehlt, auch einer, der gerade nichts traegt: wer das
        Material loescht, liesse ihn ins Leere zeigen, und spaetestens die
        naechste Aenderung machte daraus einen Fehler beim Rechnen.
        Dazu gehoert eine Linie, die gerade kein Stab ist: wird sie wieder einer,
        nimmt sie ihr Material mit.
        """
        gesehen: List[str] = []
        for l in self.linien:
            if l.material and l.material not in gesehen:
                gesehen.append(l.material)
        return gesehen

    def bezuege(self) -> List[str]:
        """Die Platten und Querschnittsanalysen, deren Querschnitt ein Stab nimmt."""
        return sorted({q.bezug for q in self.querschnitte
                       if q.art in ("platte", "analyse") and q.bezug})

    def linie_von(self, kennung: str) -> SystemlinieEintrag:
        for l in self.linien:
            if l.kennung == kennung:
                return l
        raise ProjektFehler(f"Balkensystem '{self.name}': eine Linie «{kennung}» gibt es nicht.")

    def enden(self, linie: SystemlinieEintrag) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Anfang und Ende einer Linie, in m."""
        netz = self.netz()
        a, b = netz.lage(linie.von), netz.lage(linie.bis)
        if a is None or b is None:
            raise ProjektFehler(f"Balkensystem '{self.name}': {linie.kennung} verweist auf "
                                f"einen Knoten, den es nicht gibt.")
        return a, b

    def laenge(self, linie: SystemlinieEintrag) -> float:
        (xa, za), (xb, zb) = self.enden(linie)
        return math.hypot(xb - xa, zb - za)

    def stelle_auf(self, kennung: str, punkt: Sequence[float]) -> float:
        """Wo ein Punkt auf einer Linie liegt, in m ab ihrem Anfang -- auf die Linie gelotet."""
        (xa, za), (xb, zb) = self.enden(self.linie_von(kennung))
        L = math.hypot(xb - xa, zb - za)
        return ((punkt[0] - xa) * (xb - xa) + (punkt[1] - za) * (zb - za)) / L if L else 0.0

    # -- Zum Rechnen ------------------------------------------------------------

    def modell(self) -> Modell:
        """
        Das Stabwerk zum Rechnen, in SI (:mod:`opencivil.stabwerk.modell`).

        Ein Stab ohne Querschnitt oder Material, ein Querschnitt mit
        unmoeglichen Massen und eine Feder ohne Steifigkeit sind Fehler, die
        die Meldungen nennen: gerechnet wird dann nicht -- und nicht etwa mit
        einem Stab weniger. Eine Last, deren Lastfall es nicht gibt, und ein
        Beiwert dafuer bleiben mit einem Hinweis weg.
        """
        meldungen: List[Meldung] = []

        def melden(text: str, *elemente: str, fehler: bool = True) -> None:
            meldungen.append(Meldung(text, tuple(elemente), fehler))

        # Die Faelle werden an ihrem Namen erkannt; zwei gleiche waeren nicht zu
        # unterscheiden. Ein Fehler dieses Systems -- bis 2026-10-15 hielt er
        # das ganze Projekt auf, auch jede Platte.
        lastfaelle = [lf.name for lf in self.lastfaelle]
        kombinationen = [k.name for k in self.kombinationen]
        for was, namen in (("Lastfälle", lastfaelle), ("Kombinationen", kombinationen)):
            for name in sorted({n for n in namen if namen.count(n) > 1}):
                melden(f"Mehrere {was} heissen «{name}» – sie wären nicht zu "
                       f"unterscheiden. Gerechnet wird erst mit verschiedenen Namen.")
        for name in sorted(set(lastfaelle) & set(kombinationen)):
            melden(f"«{name}» heisst ein Lastfall und eine Kombination – die beiden wären "
                   f"nicht zu unterscheiden. Gerechnet wird erst mit verschiedenen Namen.")
        # Je Teil eine Kennung: an ihr haengen Staebe, Lasten und Verweise. Bis
        # 2026-10-16 fiel eine Last bei zwei gleichen Lastfall-Kennungen still
        # in beide.
        for was, liste in (("Knoten", self.knoten), ("Linien", self.linien),
                           ("Lager", self.lager), ("Knotenlasten", self.knotenlasten),
                           ("Querschnitte", self.querschnitte), ("Lastfälle", self.lastfaelle),
                           ("Kombinationen", self.kombinationen)):
            kennungen = [e.kennung for e in liste]
            for kennung in sorted({k for k in kennungen if kennungen.count(k) > 1}):
                melden(f"Mehrere {was} haben die Kennung «{kennung}» – sie wären nicht zu "
                       f"unterscheiden. Gerechnet wird erst mit verschiedenen.", kennung)

        def halt(art: str, k: float, feld: str, wo: str) -> Optional[float]:
            if art == "frei":
                return None
            if art == "fest":
                return FEST
            if k <= 0.0:
                melden(f"{wo}: eine Feder braucht eine Steifigkeit grösser als null.", wo)
                return None
            return Groesse(k, EINHEIT_DER_FEDER[feld]).si

        querschnitte = {q.kennung: q for q in self.querschnitte}
        unmoeglich = set()
        for q in self.querschnitte:
            grund = q.fehler()
            if grund:
                unmoeglich.add(q.kennung)
                melden(f"Querschnitt «{q.name}»: {grund}", q.kennung,
                       *[l.kennung for l in self.linien if l.stab and l.querschnitt == q.kennung])

        staebe, paare = [], {}
        for l in self.linien:
            if l.stab:
                q = querschnitte.get(l.querschnitt)
                if q is None:
                    melden(f"{l.kennung} ist ein Stab, hat aber "
                           + (f"keinen Querschnitt «{l.querschnitt}»." if l.querschnitt
                              else "keinen Querschnitt."), l.kennung)
                elif q.kennung in unmoeglich:
                    pass
                elif not l.material:
                    melden(f"{l.kennung} ist ein Stab, hat aber kein Material.", l.kennung)
                else:
                    paare[l.kennung] = (q.kennung, l.material)
            staebe.append(Stab(
                name=l.kennung, a=l.von, b=l.bis, traegt=l.stab,
                gelenk_a=l.gelenk_anfang, gelenk_b=l.gelenk_ende,
                quer=halt(l.quer, l.k_quer, "k_quer", l.kennung),
                laengs=halt(l.laengs, l.k_laengs, "k_laengs", l.kennung)))

        lager = [Lager(name=a.kennung, knoten=a.knoten,
                       x=halt(a.x, a.k_x, "k_x", a.kennung),
                       z=halt(a.z, a.k_z, "k_z", a.kennung),
                       phi=halt(a.phi, a.k_phi, "k_phi", a.kennung))
                 for a in self.lager]

        name_von = {lf.kennung: lf.name for lf in self.lastfaelle}
        lasten: Dict[str, List[Any]] = {lf.kennung: [] for lf in self.lastfaelle}
        for l in self.linien:
            for last in l.lasten:
                if last.lastfall not in name_von:
                    melden(f"{l.kennung}: eine Last gehört zu keinem Lastfall – sie wird "
                           f"nicht gerechnet.", l.kennung, fehler=False)
                    continue
                einheit = EINHEIT_DER_LAST[last.art]
                lasten[last.lastfall].append(Stablast(
                    stab=l.kennung, art=last.art,
                    wert_a=Groesse(last.wert_a, einheit).si,
                    wert_b=None if last.wert_b is None else Groesse(last.wert_b, einheit).si,
                    richtung=last.richtung, von=last.von, bis=last.bis,
                    projiziert=last.projiziert))
        for p in self.knotenlasten:
            if p.lastfall not in name_von:
                melden(f"{p.kennung}: die Last gehört zu keinem Lastfall – sie wird nicht "
                       f"gerechnet.", p.kennung, fehler=False)
                continue
            wert = Groesse(p.wert, EINHEIT_DER_LAST[p.art]).si
            if p.art == "moment":
                last = Knotenlast(p.knoten, M=wert)
            elif p.richtung is Lastrichtung.WAAGRECHT:
                last = Knotenlast(p.knoten, Fx=wert)
            else:
                last = Knotenlast(p.knoten, Fz=-wert)
            lasten[p.lastfall].append(last)

        kombinationen = []
        for k in self.kombinationen:
            fremd = [lf for lf in k.faktoren if lf not in name_von]
            if fremd:
                melden(f"Kombination «{k.name}»: einen Lastfall «{fremd[0]}» gibt es nicht – "
                       f"sein Beiwert zählt nicht.", fehler=False)
            kombinationen.append(Kombination(k.name, {name_von[lf]: beiwert for lf, beiwert
                                                      in k.faktoren.items() if lf in name_von}))

        system = System(
            knoten=[Knoten(k.kennung, k.x, k.z) for k in self.knoten],
            staebe=staebe, lager=lager,
            lastfaelle=[Lastfall(lf.name, lasten[lf.kennung]) for lf in self.lastfaelle],
            kombinationen=kombinationen)
        return Modell(system=system, paare=paare, meldungen=meldungen)

    # -- Zeichnen ohne Oberflaeche --------------------------------------------

    def netz(self) -> Netz:
        return Netz(self.knoten, neu=lambda kennung, x, z: SystemknotenEintrag(kennung, x, z),
                    achsen=("x", "z"))

    def _knoten(self, netz: Netz, ort: Ort) -> str:
        if isinstance(ort, str):
            return ort
        x, z = ort
        return netz.an(float(x), float(z))

    def _neue_kennung(self, liste: Sequence[Any], vorsilbe: str) -> str:
        return naechste_kennung((e.kennung for e in liste), vorsilbe)

    def linie(self, von: Ort, bis: Ort, *, querschnitt: Any = None, material: Any = None,
              **felder: Any) -> SystemlinieEintrag:
        """
        Eine Linie von ``von`` nach ``bis`` -- ein Stab, sobald ``querschnitt``
        und ``material`` dastehen. Weitere Felder wie :class:`SystemlinieEintrag`.
        """
        netz = self.netz()
        eintrag = SystemlinieEintrag.aus_dict({
            "kennung": self._neue_kennung(self.linien, "L"),
            "von": self._knoten(netz, von), "bis": self._knoten(netz, bis),
            "stab": querschnitt is not None,
            "querschnitt": _kennung_von(querschnitt) if querschnitt is not None else "",
            "material": _kennung_von(material) if material is not None else "", **felder},
            f"Balkensystem '{self.name}', linien")
        self.linien.append(eintrag)
        return eintrag

    def lager_an(self, ort: Ort, art: str = "gelenkig", **felder: Any) -> LagerEintrag:
        """Ein Lager -- ``gelenkig``, ``verschieblich`` oder ``eingespannt``, Felder darueber."""
        if art not in LAGERARTEN:
            raise ProjektFehler(f"Eine Lagerart «{art}» gibt es nicht. Möglich sind: "
                                f"{', '.join(LAGERARTEN)}.")
        x, z, phi = LAGERARTEN[art]
        eintrag = LagerEintrag.aus_dict({
            "kennung": self._neue_kennung(self.lager, "A"),
            "knoten": self._knoten(self.netz(), ort), "x": x, "z": z, "phi": phi, **felder},
            f"Balkensystem '{self.name}', lager")
        self.lager.append(eintrag)
        return eintrag

    def querschnitt(self, name: str, vorlage: str = qs.RECHTECK.schluessel,
                    **masse: float) -> StabquerschnittEintrag:
        """Ein Querschnitt nach Vorlage -- Masse in mm, was fehlt nach ihrer Vorgabe."""
        try:
            qs.vorlage(vorlage)
        except KeyError as fehler:
            raise ProjektFehler(fehler.args[0]) from None
        eintrag = StabquerschnittEintrag(kennung=self._neue_kennung(self.querschnitte, "Q"),
                                         name=name, vorlage=vorlage, masse=dict(masse))
        self.querschnitte.append(eintrag)
        return eintrag

    def querschnitt_aus(self, name: str, art: str, bezug: Any) -> StabquerschnittEintrag:
        """Ein Querschnitt aus einer Platte (``platte``) oder einer Querschnittsanalyse (``analyse``)."""
        if art not in ("platte", "analyse"):
            raise ProjektFehler(f"Ein Querschnitt kommt aus einer «platte» oder einer «analyse», "
                                f"nicht aus «{art}».")
        eintrag = StabquerschnittEintrag(kennung=self._neue_kennung(self.querschnitte, "Q"),
                                         name=name, art=art, bezug=_kennung_von(bezug))
        self.querschnitte.append(eintrag)
        return eintrag

    def querschnitt_mit_kennwerten(self, name: str, *, A: float, I: float) -> StabquerschnittEintrag:
        """Ein Querschnitt mit Kennwerten von Hand -- A in mm², I in 10⁶ mm⁴."""
        eintrag = StabquerschnittEintrag(kennung=self._neue_kennung(self.querschnitte, "Q"),
                                         name=name, art="kennwerte", masse={"A": A, "I": I})
        self.querschnitte.append(eintrag)
        return eintrag

    def lastfall(self, name: str) -> LastfallEintrag:
        eintrag = LastfallEintrag(kennung=self._neue_kennung(self.lastfaelle, "LF"), name=name)
        self.lastfaelle.append(eintrag)
        return eintrag

    def kombination(self, name: str, *faktoren: Tuple[Any, float]) -> LastkombinationEintrag:
        """Eine Kombination -- je Lastfall (Eintrag oder Kennung) ein Beiwert: ``(g, 1.35), (w, 1.5)``."""
        eintrag = LastkombinationEintrag(
            kennung=self._neue_kennung(self.kombinationen, "LK"), name=name,
            faktoren={_kennung_von(lf): float(beiwert) for lf, beiwert in faktoren})
        self.kombinationen.append(eintrag)
        return eintrag

    def stablast(self, lastfall: Any, linie: Any, art: Lastart = Lastart.LINIENLAST,
                 wert: float = 10.0, **felder: Any) -> StablastEintrag:
        """Eine Last auf einer Linie -- ``wert`` ist ``wert_a``; Felder wie :class:`StablastEintrag`."""
        eintrag = StablastEintrag.aus_dict({"lastfall": _kennung_von(lastfall), "art": art,
                                            "wert_a": wert, **felder},
                                           f"Balkensystem '{self.name}', lasten")
        self.linie_von(_kennung_von(linie)).lasten.append(eintrag)
        return eintrag

    def knotenlast(self, lastfall: Any, ort: Ort, wert: float = 10.0, *, art: str = "kraft",
                   richtung: Lastrichtung = Lastrichtung.SENKRECHT) -> KnotenlastEintrag:
        eintrag = KnotenlastEintrag.aus_dict({
            "kennung": self._neue_kennung(self.knotenlasten, "P"),
            "knoten": self._knoten(self.netz(), ort), "lastfall": _kennung_von(lastfall),
            "art": art, "richtung": richtung, "wert": wert},
            f"Balkensystem '{self.name}', knotenlasten")
        self.knotenlasten.append(eintrag)
        return eintrag

    # -- Teilen und Umkehren ----------------------------------------------------

    def teilen(self, kennung: str, stelle: float) -> SystemlinieEintrag:
        """
        Teilt eine Linie bei ``stelle`` m ab ihrem Anfang: sie endet dort, und
        eine neue laeuft weiter zum alten Ende -- mit ihren Eigenschaften. Die
        Lasten gehen mit, je auf ihre Haelfte: eine Strecke ueber den Schnitt
        wird zwei, mit dem Wert an der Schnittstelle; eine Einzellast bleibt
        dort, wo sie steht. Das Gelenk am Ende wandert mit ans neue Ende; an
        der Schnittstelle ist die Linie durchlaufend.
        """
        linie = self.linie_von(kennung)
        (xa, za), (xb, zb) = self.enden(linie)
        L = math.hypot(xb - xa, zb - za)
        if not 0.0 < stelle < L:
            raise ProjektFehler(f"{linie.kennung} ist {L:.3f} m lang -- geteilt werden kann nur "
                                f"dazwischen, nicht bei {stelle:g} m.")
        mitte = self._knoten(self.netz(), (xa + (xb - xa) * stelle / L,
                                           za + (zb - za) * stelle / L))
        zweite = copy.deepcopy(linie)
        zweite.kennung = self._neue_kennung(self.linien, "L")
        zweite.von, zweite.gelenk_anfang = mitte, False
        linie.bis, linie.gelenk_ende = mitte, False
        erste_lasten, zweite_lasten = [], []
        for last in linie.lasten:
            if not last.verteilt:
                if last.von <= stelle:
                    erste_lasten.append(last)
                else:
                    zweite_lasten.append(replace(last, von=last.von - stelle))
                continue
            a, b = last.von, L if last.bis is None else last.bis
            wb = last.wert_a if last.wert_b is None else last.wert_b

            def wert(x: float) -> float:
                return last.wert_a if b == a else last.wert_a + (wb - last.wert_a) * (x - a) / (b - a)

            konstant = last.wert_b is None
            if a < stelle:
                ende = min(b, stelle)
                erste_lasten.append(replace(
                    last, bis=None if ende >= stelle else ende,
                    wert_b=None if konstant else wert(ende)))
            if b > stelle:
                anfang = max(a, stelle)
                zweite_lasten.append(replace(
                    last, von=anfang - stelle, bis=None if last.bis is None else b - stelle,
                    wert_a=wert(anfang), wert_b=None if konstant else wb))
        linie.lasten, zweite.lasten = erste_lasten, zweite_lasten
        self.linien.insert(self.linien.index(linie) + 1, zweite)
        return zweite

    def umkehren(self, kennung: str) -> None:
        """
        Tauscht Anfang und Ende einer Linie. Die gestrichelte Faser liegt
        danach auf der anderen Seite, die Lasten bleiben, wo sie wirken: ihre
        Stellen gespiegelt, Anfangs- und Endwert getauscht, und quer und
        laengs mit umgekehrtem Vorzeichen -- diese Richtungen haengen an der
        Linie. Senkrecht, waagrecht und Momente aendern sich nicht.
        """
        linie = self.linie_von(kennung)
        L = self.laenge(linie)
        linie.von, linie.bis = linie.bis, linie.von
        linie.gelenk_anfang, linie.gelenk_ende = linie.gelenk_ende, linie.gelenk_anfang
        neu = []
        for last in linie.lasten:
            vorzeichen = -1.0 if last.richtung in (Lastrichtung.QUER, Lastrichtung.LAENGS) \
                and last.art.kraft else 1.0
            if not last.verteilt:
                neu.append(replace(last, von=L - last.von, wert_a=vorzeichen * last.wert_a))
                continue
            a, b = last.von, L if last.bis is None else last.bis
            wb = last.wert_a if last.wert_b is None else last.wert_b
            neu.append(replace(
                last, von=L - b, bis=None if a == 0.0 else L - a,
                wert_a=vorzeichen * wb,
                wert_b=None if last.wert_b is None else vorzeichen * last.wert_a))
        linie.lasten = neu

    # -- Die frische Anlage -------------------------------------------------------

    @classmethod
    def neu(cls, kennung: str, name: str, material: str) -> "BalkensystemEintrag":
        """
        Ein frisches System, wie der Benutzer es angelegt bekommt: ein
        Einfeldtraeger von 6 m, Rechteck 300 × 600 mm, links gelenkig, rechts
        verschieblich, ein Lastfall mit 10 kN/m. Zum Anfangen, nicht als
        Vorgabe.
        """
        s = cls(kennung=kennung, name=name)
        q = s.querschnitt("Rechteck 300×600", "rechteck", b=300.0, h=600.0)
        linie = s.linie((0.0, 0.0), (6.0, 0.0), querschnitt=q, material=material)
        s.lager_an((0.0, 0.0), "gelenkig")
        s.lager_an((6.0, 0.0), "verschieblich")
        lf = s.lastfall("Lastfall 1")
        s.stablast(lf, linie, wert=10.0)
        return s
