"""
opencivil/projekt/balkensystem.py -- ein 2D-Balkensystem, wie die Oberflaeche es beschreibt.

VERANTWORTUNG:
Der :class:`BalkensystemEintrag`: ein ebener Rahmen aus Knoten und Linien,
Lagern und Lasten, mit seinen Materialien, Querschnitten, Lastfaellen und
Kombinationen
-- als speicherbare Datenklasse wie die Querschnittsanalyse
(:mod:`opencivil.projekt.querschnittsanalyse`). Dazu der Baukasten, der ohne
Oberflaeche zeichnet, und was beim Teilen und Umkehren einer Linie mit ihren
Lasten geschieht. Gerechnet wird in :mod:`opencivil.stabwerk`.

ZUERST GEOMETRIE:
Gezeichnet werden Knoten und Linien. Eine Linie ist ein Stab, sobald sie
einen Querschnitt hat; sie kann daneben -- oder statt dessen -- ein
Linienlager sein, quer und laengs je frei, fest oder federnd. Ein Knoten
wird zum Lager durch ein :class:`LagerEintrag` an ihm, nicht durch ein Feld
am Knoten: das Zeichenfenster fuehrt Knoten zusammen und legt neue an, und
ein Feld daran ginge dabei verloren.

LASTEN AN IHREN ELEMENTEN:
Eine Last auf einem Stab steht an seiner Linie (``lasten``), mit dem
Lastfall, zu dem sie gehoert. So bleibt sie bei der Linie, wenn diese
kopiert, geteilt, geloescht oder rueckgaengig gemacht wird. Eine Last an
einem Knoten ist -- wie ein Lager -- ein eigener Eintrag an ihm. Jede Last
hat eine eigene Kennung (``P1``): im Zeichenfenster laesst sie sich fuer sich
waehlen und loeschen (Benutzer, 2026-10-23). Eine verteilte Last liegt immer
auf der ganzen Linie, eine Einzellast und ein Einzelmoment an einer Stelle
in Prozent der Linie ab ihrem Anfang.

KOORDINATEN UND EINHEITEN:
x nach rechts, z nach oben, in m; Stellen auf einem Stab in % seiner Laenge
ab seinem Anfang. Querschnittsmasse in mm, A in mm², I in 10⁶ mm⁴. Lasten in kN, kN/m,
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
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from opencivil.core.einheiten import (
    KG_PRO_M3, KN, KN_PRO_M, KN_PRO_M2, KNM, KNM_PRO_M, KNM_PRO_RAD, N_PRO_MM2, PROZENT,
    Groesse,
)
from opencivil.core.wahl import Wahl
from opencivil.nachweis.rechenwahl import FASERARTEN
from opencivil.projekt.eintraege import Beschreibung
from opencivil.querschnitt.gesetzwahl import Rechenart, Rechenwahl, Werkstoffsatz
from opencivil.projekt.lesen import ProjektFehler, bereich, einer_von
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

class Querschnittsart(Wahl):
    """
    Woher ``A`` und ``I`` eines Stabquerschnitts kommen. Aufgeloest wird die
    Art einmal, im Aufbau: je Art eine Klasse
    (:mod:`opencivil.stabwerk.stabquerschnitt`).
    """

    VORLAGE = "vorlage"
    KENNWERTE = "kennwerte"
    PLATTE = "platte"
    ANALYSE = "analyse"

    @property
    def beschriftung(self) -> str:
        return {
            Querschnittsart.VORLAGE: "nach Vorlage",
            Querschnittsart.KENNWERTE: "Kennwerte von Hand",
            Querschnittsart.PLATTE: "aus einer Platte",
            Querschnittsart.ANALYSE: "aus einer Querschnittsanalyse",
        }[self]

    @property
    def kurz(self) -> str:
        """Fuer den Schalter -- der lange Name steht in seinem Titel."""
        return {
            Querschnittsart.VORLAGE: "Vorlage",
            Querschnittsart.KENNWERTE: "Kennwerte",
            Querschnittsart.PLATTE: "Platte",
            Querschnittsart.ANALYSE: "Analyse",
        }[self]

    @property
    def aus_bauteil(self) -> bool:
        """
        Ob er ein Bauteil des Projekts nimmt, eine Platte oder eine
        Querschnittsanalyse. Nur dann bringt er ein Material mit, den Beton
        des Bauteils, und nur dann hat er ein E_eq -- eine
        Momenten-Kruemmungs-Linie mit ihrer Bewehrung, bei einer Platte immer
        in x-Richtung, Zug unten (Benutzer, 2026-10-24). Einer nach Vorlage
        oder von Hand ist nur eine Form.
        """
        return self in (Querschnittsart.PLATTE, Querschnittsart.ANALYSE)

#: Die Kennwerte eines Querschnitts von Hand: A in mm², I in 10⁶ mm⁴.
KENNWERTE = ("A", "I")

#: Was ein Material des Systems ist: ein Beton des Projekts -- E und Dichte
#: von ihm, nicht zu aendern -- oder ein eigenes mit E und Dichte von Hand
#: (Benutzer, 2026-10-24). Betonstahl ist keines: aus ihm ist kein Stab.
STABMATERIALARTEN = ("beton", "eigen")

#: Womit ein Stab rechnet, der das Material seines Querschnitts nimmt: E₀,
#: das E_cm des Betons, den der Querschnitt mitbringt, oder das E_eq der
#: Querschnittsanalyse bei N und M (Benutzer, 2026-10-24). Einen E-Modul von
#: Hand hat ein Querschnitt nicht mehr -- den hat ein eigenes Material.
E_MODULE = ("e0", "e_eq")

#: Das Material einer Linie, das ihr Querschnitt mitbringt: der Beton der
#: Platte oder der Querschnittsanalyse (Benutzer, 2026-10-23). Es kann keine
#: Kennung eines Materials sein -- die beginnen mit «M» und einer Zahl.
MATERIAL_DES_QUERSCHNITTS = "querschnitt"

#: Was ein Diagramm der Statik-Analyse zeigt: je Stab den Verlauf einer
#: Schnittgroesse oder der Verdrehung, das verschobene System oder die
#: Lagerkraefte.
DIAGRAMMGROESSEN = ("M", "V", "N", "verschiebung", "verdrehung", "lagerkraefte")

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
    (:data:`EINHEIT_DER_LAST`). Eine verteilte liegt auf der ganzen Linie:
    ``wert_a`` am Anfang, ``wert_b`` am Ende, leer: wie ``wert_a``.
    Einzellast und Einzelmoment stehen bei ``stelle``, in % der Linie ab
    ihrem Anfang (Benutzer, 2026-10-23).
    """

    kennung: str = ""
    lastfall: str = ""
    art: Lastart = Lastart.LINIENLAST
    richtung: Lastrichtung = Lastrichtung.SENKRECHT
    wert_a: float = 10.0
    wert_b: Optional[float] = None
    stelle: float = bereich(50.0, heisst="Stelle", einheit=PROZENT, ab=0.0, bis=100.0)
    projiziert: bool = False
    """Senkrecht und waagrecht je Meter Projektion statt je Meter Stab."""

    @property
    def verteilt(self) -> bool:
        return self.art.verteilt


@dataclass
class SystemlinieEintrag(Beschreibung):
    """
    Eine Linie des Systems: ein Stab, wenn sie einen Querschnitt hat; dazu,
    oder ohne Stab, ein Linienlager quer und laengs.
    """

    kennung: str = ""
    von: str = ""
    bis: str = ""
    querschnitt: str = ""
    """Kennung des Querschnitts im System (``Q1``); leer: kein Stab, nur eine Linie."""

    material: str = ""
    """
    Kennung eines Materials des Systems (``M1``) -- oder
    :data:`MATERIAL_DES_QUERSCHNITTS`: das Material, das eine Platte oder
    Querschnittsanalyse als Querschnitt mitbringt.
    """

    gelenk_anfang: bool = False
    gelenk_ende: bool = False
    quer: str = einer_von(HALT, "frei")
    k_quer: float = 0.0
    """Bettung quer, kN/m²."""

    laengs: str = einer_von(HALT, "frei")
    k_laengs: float = 0.0
    lasten: List[StablastEintrag] = field(default_factory=list)

    @property
    def stab(self) -> bool:
        """Ob die Linie traegt -- sie hat einen Querschnitt."""
        return bool(self.querschnitt)


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
    """
    Eine Last an einem Knoten, in einem Lastfall: eine Kraft mit Richtung
    oder ein Moment. Ihre Kennung zaehlt mit denen der Stablasten (``P1``).
    """

    kennung: str = ""
    knoten: str = ""
    lastfall: str = ""
    art: str = einer_von(KNOTENLASTEN, "kraft")
    richtung: Lastrichtung = einer_von(KNOTENRICHTUNGEN, Lastrichtung.SENKRECHT)
    wert: float = 10.0
    """kN oder kNm."""


@dataclass
class StabmaterialEintrag(Beschreibung):
    """
    Ein Material der Staebe (Benutzer, 2026-10-24): ein Beton des Projekts
    (``beton``) -- E_cm und die Dichte des Stahlbetons von ihm -- oder ein
    eigenes mit ``E`` und ``rho`` von Hand.
    """

    kennung: str = ""
    art: str = einer_von(STABMATERIALARTEN, "beton")
    beton: str = ""
    """Die Kennung des Betons im Projekt (``b1``) -- nur bei ``beton``."""

    name: str = ""
    """Wie ein eigenes heisst; ein Beton heisst wie im Projekt."""

    E: float = bereich(200000.0, heisst="E-Modul E", einheit=N_PRO_MM2, ueber=0.0)
    """N/mm² -- nur bei ``eigen``."""

    rho: float = bereich(7850.0, heisst="Dichte ρ", einheit=KG_PRO_M3, ab=0.0)
    """kg/m³, fuer das Eigengewicht -- nur bei ``eigen``."""


@dataclass
class ModulEintrag(Beschreibung):
    """
    Wie das E_eq eines Querschnitts aus einer Platte oder Querschnittsanalyse
    entsteht: bei ``N`` und ``M``, Zug positiv und ``M > 0`` mit Zug unten --
    auf der gestrichelten Faser des Stabs; bei einer Platte immer in
    x-Richtung, und ``M`` zieht unten (Benutzer, 2026-10-24). Gerechnet wie
    eine Momenten-Kruemmungs-Linie ihrer Spannung-Dehnung-Analyse, mit
    Kriechzahl, Wertesatz und Rechenart wie dort (Benutzer, 2026-10-23).
    """

    N: float = bereich(0.0, heisst="N für E_eq", einheit=KN)
    M: float = bereich(0.0, heisst="M für E_eq", einheit=KNM)
    kriechzahl: float = bereich(0.0, heisst="Kriechzahl φ", ab=0.0)
    werkstoffsatz: Werkstoffsatz = Werkstoffsatz.BEMESSUNG
    rechenart: Rechenart = einer_von(FASERARTEN, Rechenart.PARABEL)

    @property
    def wahl(self) -> Rechenwahl:
        return Rechenwahl(kriechzahl=self.kriechzahl, satz=self.werkstoffsatz,
                          art=self.rechenart)


@dataclass
class StabquerschnittEintrag(Beschreibung):
    """
    Ein Querschnitt der Staebe: nach Vorlage mit Massen in mm, mit Kennwerten
    von Hand (``A`` in mm², ``I`` in 10⁶ mm⁴), oder aus einer Platte oder
    einer Querschnittsanalyse des Projekts (``bezug``). E kommt vom Material
    des Stabs; nimmt der das Material des Querschnitts, sagt ``e_modul``,
    welches E.
    """

    kennung: str = ""
    name: str = ""
    art: Querschnittsart = einer_von(tuple(Querschnittsart), Querschnittsart.VORLAGE)
    vorlage: str = einer_von((v.schluessel for v in qs.VORLAGEN), qs.RECHTECK.schluessel)
    masse: Dict[str, float] = field(default_factory=dict)
    bezug: str = ""
    e_modul: str = einer_von(E_MODULE, "e0")
    """
    Welches E ein Stab hat, der das Material dieses Querschnitts nimmt:
    ``e0`` -- E_cm seines Betons -- oder ``e_eq``, wie ``eq`` sagt.
    """

    eq: ModulEintrag = field(default_factory=ModulEintrag)
    """Wie das E_eq entsteht -- es gilt nur bei ``e_modul = "e_eq"``."""

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
        if self.e_modul == "e_eq" and not self.art.aus_bauteil:
            return ("ein E_eq gibt es nur bei einem Querschnitt aus einer Platte oder "
                    "Querschnittsanalyse – nur sie haben eine Momenten-Krümmungs-Linie.")
        if self.art is Querschnittsart.VORLAGE:
            vorlage = self.stabvorlage()
            fremd = [k for k in self.masse if k not in vorlage.vorgaben()]
            if fremd:
                return (f"ein Mass «{fremd[0]}» gibt es bei «{vorlage.name}» nicht. "
                        f"Möglich sind: {', '.join(vorlage.vorgaben())}.")
            return vorlage.pruefen(self.masse_mit_vorgaben())
        if self.art is Querschnittsart.KENNWERTE:
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
    eigengewicht: bool = False
    """
    Ob der Lastfall das Eigengewicht aller Staebe bekommt -- von selbst, aus
    Dichte und Flaeche (Benutzer, 2026-10-23). Ein System hat einen davon.
    """


@dataclass
class LastkombinationEintrag(Beschreibung):
    """Eine Kombination: je Lastfall (Kennung) ein Beiwert, von Hand."""

    kennung: str = ""
    name: str = ""
    faktoren: Dict[str, float] = field(default_factory=dict)


@dataclass
class StatikdiagrammEintrag(Beschreibung):
    """
    Ein Diagramm der Statik-Analyse (Benutzer, 2026-10-23): ein Fall und was
    es von ihm zeigt. Gerechnet wird damit nichts -- das System rechnet jeden
    Fall; die Liste sagt nur, welche Diagramme rechts stehen.
    """

    fall: str = ""
    """Die Kennung eines Lastfalls (``LF1``) oder einer Kombination (``LK1``)."""

    groesse: str = einer_von(DIAGRAMMGROESSEN, "M")


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

    eigengewicht: Optional[str] = None
    """Der Name des Lastfalls, der das Eigengewicht der Staebe bekommt -- oder keiner."""

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
    stabmaterialien: List[StabmaterialEintrag] = field(default_factory=list)
    querschnitte: List[StabquerschnittEintrag] = field(default_factory=list)
    lastfaelle: List[LastfallEintrag] = field(default_factory=list)
    kombinationen: List[LastkombinationEintrag] = field(default_factory=list)
    diagramme: List[StatikdiagrammEintrag] = field(default_factory=list)
    beschreibung: str = ""
    """Freier Text -- geht in keine Rechnung ein."""

    # -- Zugriff -------------------------------------------------------------

    def materialien(self) -> List[str]:
        """
        Jeder Beton des Projekts, auf den ein Material des Systems zeigt --
        auch eines, das gerade keinen Stab traegt: wer den Beton loescht,
        liesse es ins Leere zeigen, und spaetestens die naechste Aenderung
        machte daraus einen Fehler beim Rechnen.
        """
        gesehen: List[str] = []
        for m in self.stabmaterialien:
            if m.art == "beton" and m.beton and m.beton not in gesehen:
                gesehen.append(m.beton)
        return gesehen

    def bezuege(self) -> List[str]:
        """Die Platten und Querschnittsanalysen, deren Querschnitt ein Stab nimmt."""
        return sorted({q.bezug for q in self.querschnitte if q.art.aus_bauteil and q.bezug})

    def alle_lasten(self) -> List[Any]:
        """Jede Last des Systems, auf den Linien und an den Knoten -- ihre Kennungen zaehlen zusammen."""
        return [last for l in self.linien for last in l.lasten] + list(self.knotenlasten)

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

        Ein Stab ohne Querschnitt oder Material -- oder mit einem Material,
        das es im System nicht gibt --, ein Querschnitt mit unmoeglichen
        Massen und eine Feder ohne Steifigkeit sind Fehler, die die Meldungen
        nennen: gerechnet wird dann nicht -- und nicht etwa mit einem Stab
        weniger. Ob ein Material traegt, weiss erst der Aufbau: er kennt die
        Betone des Projekts. Eine Last, deren Lastfall es nicht gibt, und ein
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
        eigen = [lf for lf in self.lastfaelle if lf.eigengewicht]
        if len(eigen) > 1:
            melden(f"Das Eigengewicht bekommen {', '.join(f'«{lf.name}»' for lf in eigen)} – "
                   f"es gehört in einen Lastfall.", *[lf.kennung for lf in eigen])
        # Je Teil eine Kennung: an ihr haengen Staebe, Lasten und Verweise. Bis
        # 2026-10-16 fiel eine Last bei zwei gleichen Lastfall-Kennungen still
        # in beide.
        for was, liste in (("Knoten", self.knoten), ("Linien", self.linien),
                           ("Lager", self.lager), ("Lasten", self.alle_lasten()),
                           ("Materialien", self.stabmaterialien),
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
        stoffe = {m.kennung for m in self.stabmaterialien} | {MATERIAL_DES_QUERSCHNITTS}
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
                elif l.material not in stoffe:
                    melden(f"{l.kennung} nimmt das Material «{l.material}», das es im System "
                           f"nicht gibt.", l.kennung)
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
                    melden(f"{last.kennung or l.kennung}: die Last gehört zu keinem Lastfall – "
                           f"sie wird nicht gerechnet.", last.kennung or l.kennung, fehler=False)
                    continue
                einheit = EINHEIT_DER_LAST[last.art]
                # Verteilt ueber die ganze Linie, einzeln an ihrer Stelle.
                von = 0.0 if last.verteilt else last.stelle / 100.0 * self.laenge(l)
                lasten[last.lastfall].append(Stablast(
                    stab=l.kennung, art=last.art,
                    wert_a=Groesse(last.wert_a, einheit).si,
                    wert_b=None if last.wert_b is None else Groesse(last.wert_b, einheit).si,
                    richtung=last.richtung, von=von, bis=None,
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
        return Modell(system=system, paare=paare, meldungen=meldungen,
                      eigengewicht=eigen[0].name if eigen else None)

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
        und ``material`` dastehen: ein Material des Systems (:meth:`beton`,
        :meth:`eigenes_material`) oder :data:`MATERIAL_DES_QUERSCHNITTS`.
        Weitere Felder wie :class:`SystemlinieEintrag`.
        """
        netz = self.netz()
        eintrag = SystemlinieEintrag.aus_dict({
            "kennung": self._neue_kennung(self.linien, "L"),
            "von": self._knoten(netz, von), "bis": self._knoten(netz, bis),
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

    def beton(self, beton: Any) -> StabmaterialEintrag:
        """
        Das Material des Systems aus einem Beton des Projekts (Eintrag oder
        Kennung) -- das schon da ist, sonst ein neues.
        """
        kennung = _kennung_von(beton)
        for m in self.stabmaterialien:
            if m.art == "beton" and m.beton == kennung:
                return m
        eintrag = StabmaterialEintrag(kennung=self._neue_kennung(self.stabmaterialien, "M"),
                                      art="beton", beton=kennung)
        self.stabmaterialien.append(eintrag)
        return eintrag

    def eigenes_material(self, name: str, *, E: float, rho: float) -> StabmaterialEintrag:
        """Ein eigenes Material des Systems -- E in N/mm², die Dichte in kg/m³."""
        eintrag = StabmaterialEintrag.aus_dict({
            "kennung": self._neue_kennung(self.stabmaterialien, "M"), "art": "eigen",
            "name": name, "E": E, "rho": rho}, f"Balkensystem '{self.name}', stabmaterialien")
        self.stabmaterialien.append(eintrag)
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

    def querschnitt_aus(self, name: str, art: str, bezug: Any, *,
                        E_eq: Optional[Mapping[str, Any]] = None) -> StabquerschnittEintrag:
        """
        Ein Querschnitt aus einer Platte (``platte``) oder einer
        Querschnittsanalyse (``analyse``). Bei einer Analyse rechnet ein Stab
        «gemäss Querschnitt» mit ``E_eq`` -- Felder wie :class:`ModulEintrag`,
        etwa ``{"M": 80}`` -- mit ihrem aequivalenten E-Modul.
        """
        if art not in ("platte", "analyse"):
            raise ProjektFehler(f"Ein Querschnitt kommt aus einer «platte» oder einer «analyse», "
                                f"nicht aus «{art}».")
        eintrag = StabquerschnittEintrag(kennung=self._neue_kennung(self.querschnitte, "Q"),
                                         name=name, art=art, bezug=_kennung_von(bezug))
        if E_eq is not None:
            eintrag.e_modul = "e_eq"
            eintrag.eq = ModulEintrag.aus_dict(dict(E_eq), f"Querschnitt '{name}', E_eq")
        self.querschnitte.append(eintrag)
        return eintrag

    def querschnitt_mit_kennwerten(self, name: str, *, A: float,
                                   I: float) -> StabquerschnittEintrag:
        """Ein Querschnitt mit Kennwerten von Hand -- A in mm², I in 10⁶ mm⁴."""
        eintrag = StabquerschnittEintrag(kennung=self._neue_kennung(self.querschnitte, "Q"),
                                         name=name, art="kennwerte", masse={"A": A, "I": I})
        self.querschnitte.append(eintrag)
        return eintrag

    def lastfall(self, name: str, *, eigengewicht: bool = False) -> LastfallEintrag:
        eintrag = LastfallEintrag(kennung=self._neue_kennung(self.lastfaelle, "LF"), name=name,
                                  eigengewicht=eigengewicht)
        self.lastfaelle.append(eintrag)
        return eintrag

    def kombination(self, name: str, *faktoren: Tuple[Any, float]) -> LastkombinationEintrag:
        """Eine Kombination -- je Lastfall (Eintrag oder Kennung) ein Beiwert: ``(g, 1.35), (w, 1.5)``."""
        eintrag = LastkombinationEintrag(
            kennung=self._neue_kennung(self.kombinationen, "LK"), name=name,
            faktoren={_kennung_von(lf): float(beiwert) for lf, beiwert in faktoren})
        self.kombinationen.append(eintrag)
        return eintrag

    def diagramm(self, fall: Any, groesse: str = "M") -> StatikdiagrammEintrag:
        """Ein Diagramm der Statik-Analyse -- ``fall`` ein Lastfall oder eine Kombination."""
        eintrag = StatikdiagrammEintrag.aus_dict(
            {"fall": _kennung_von(fall), "groesse": groesse},
            f"Balkensystem '{self.name}', diagramme")
        self.diagramme.append(eintrag)
        return eintrag

    def stablast(self, lastfall: Any, linie: Any, art: Lastart = Lastart.LINIENLAST,
                 wert: float = 10.0, **felder: Any) -> StablastEintrag:
        """Eine Last auf einer Linie -- ``wert`` ist ``wert_a``; Felder wie :class:`StablastEintrag`."""
        eintrag = StablastEintrag.aus_dict({"kennung": self._neue_kennung(self.alle_lasten(), "P"),
                                            "lastfall": _kennung_von(lastfall), "art": art,
                                            "wert_a": wert, **felder},
                                           f"Balkensystem '{self.name}', lasten")
        self.linie_von(_kennung_von(linie)).lasten.append(eintrag)
        return eintrag

    def knotenlast(self, lastfall: Any, ort: Ort, wert: float = 10.0, *, art: str = "kraft",
                   richtung: Lastrichtung = Lastrichtung.SENKRECHT) -> KnotenlastEintrag:
        eintrag = KnotenlastEintrag.aus_dict({
            "kennung": self._neue_kennung(self.alle_lasten(), "P"),
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
        Lasten gehen mit: eine verteilte liegt danach auf beiden Haelften, mit
        dem Wert an der Schnittstelle, die auf der zweiten mit einer eigenen
        Kennung; eine Einzellast bleibt dort, wo sie steht, ihre Stelle in %
        der neuen Haelfte. Das Gelenk am Ende wandert mit ans neue Ende; an der
        Schnittstelle ist die Linie durchlaufend.
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
        anteil = stelle / L
        vergeben = {last.kennung for last in self.alle_lasten()}
        erste_lasten, zweite_lasten = [], []
        for last in linie.lasten:
            if not last.verteilt:
                if last.stelle <= 100.0 * anteil:
                    erste_lasten.append(replace(last, stelle=last.stelle / anteil))
                else:
                    zweite_lasten.append(replace(
                        last, stelle=(last.stelle - 100.0 * anteil) / (1.0 - anteil)))
                continue
            mitte = None if last.wert_b is None else \
                last.wert_a + (last.wert_b - last.wert_a) * anteil
            kennung = naechste_kennung(vergeben, "P")
            vergeben.add(kennung)
            erste_lasten.append(replace(last, wert_b=mitte))
            zweite_lasten.append(replace(last, kennung=kennung,
                                         wert_a=last.wert_a if mitte is None else mitte))
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
        linie.von, linie.bis = linie.bis, linie.von
        linie.gelenk_anfang, linie.gelenk_ende = linie.gelenk_ende, linie.gelenk_anfang
        neu = []
        for last in linie.lasten:
            vorzeichen = -1.0 if last.richtung in (Lastrichtung.QUER, Lastrichtung.LAENGS) \
                and last.art.kraft else 1.0
            if not last.verteilt:
                neu.append(replace(last, stelle=100.0 - last.stelle,
                                   wert_a=vorzeichen * last.wert_a))
                continue
            wb = last.wert_a if last.wert_b is None else last.wert_b
            neu.append(replace(
                last, wert_a=vorzeichen * wb,
                wert_b=None if last.wert_b is None else vorzeichen * last.wert_a))
        linie.lasten = neu

    # -- Die frische Anlage -------------------------------------------------------

    @classmethod
    def neu(cls, kennung: str, name: str) -> "BalkensystemEintrag":
        """
        Ein frisches System, wie der Benutzer es angelegt bekommt: ohne
        Knoten, Linie, Lager und Querschnitt (Benutzer, 2026-10-19), aber mit
        den Lastfaellen Eigengewicht -- es kommt von selbst --, Auflast und
        Nutzlast, die beiden ohne Last, und den Kombinationen GZT mit 1.35,
        1.35 und 1.5 und GZG mit je 1.0 (Benutzer, 2026-10-23). Dazu die
        Diagramme M, V und N der GZT und die Verschiebung der GZG.
        """
        s = cls(kennung=kennung, name=name)
        g = s.lastfall("Eigengewicht", eigengewicht=True)
        auflast = s.lastfall("Auflast")
        nutzlast = s.lastfall("Nutzlast")
        gzt = s.kombination("GZT", (g, 1.35), (auflast, 1.35), (nutzlast, 1.5))
        gzg = s.kombination("GZG", (g, 1.0), (auflast, 1.0), (nutzlast, 1.0))
        for groesse in ("M", "V", "N"):
            s.diagramm(gzt, groesse)
        s.diagramm(gzg, "verschiebung")
        return s
