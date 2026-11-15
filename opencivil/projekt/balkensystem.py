"""
opencivil/projekt/balkensystem.py -- ein 2D-Balkensystem, wie die Oberflaeche es beschreibt.

VERANTWORTUNG:
Der :class:`BalkensystemEintrag`: ein ebener Rahmen aus Knoten und Linien,
Lagern und Lasten, mit seinen Materialien, Querschnitten, Lastfaellen und
Kombinationen
-- als speicherbare Datenklasse wie die Querschnittsanalyse
(:mod:`opencivil.projekt.querschnittsanalyse`). Was es mit dem
3D-Balkensystem teilt -- zeichnen ohne Oberflaeche, teilen, umkehren, die
Felder eines Querschnitts --, steht in :mod:`opencivil.projekt.staebe`.
Gerechnet wird in :mod:`opencivil.stabwerk`.

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

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional

from opencivil.core.einheiten import (
    KG_PRO_M3, KN, KN_PRO_M, KN_PRO_M2, KNM, KNM_PRO_M, KNM_PRO_RAD, N_PRO_MM2, PROZENT,
)
from opencivil.core.wahl import Wahl
from opencivil.nachweis.rechenwahl import FASERARTEN
from opencivil.projekt.eintraege import BauteilEintrag, Beschreibung
from opencivil.projekt.faelle import LastfallEintrag, LastkombinationEintrag, MitFaellen, kennung_von
from opencivil.querschnitt.gesetzwahl import Rechenart, Rechenwahl, Werkstoffsatz
from opencivil.projekt.lesen import ProjektFehler, bereich, einer_von
from opencivil.projekt.staebe import MitStaeben, Querschnittsart, StabquerschnittBasis
from opencivil.stabwerk.modell import Lastart, Lastrichtung
from opencivil.stabwerk.rechnung import STABKENNWERTE
from opencivil.stabwerk.stabquerschnitt import EBEN

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

#: Die Kennwerte eines Querschnitts von Hand: A in mm², I in 10⁶ mm⁴ -- wie die Rechnung sie nimmt.
KENNWERTE = tuple(k.kurzname for k in EBEN)


class Profilachse(Wahl):
    """
    Um welche Achse ein Stahlprofil sich im Rahmen biegt: um ``y``, die
    starke -- der Steg liegt in der Ebene des Rahmens --, oder um ``z``.
    """

    Y = "y"
    Z = "z"

    @property
    def beschriftung(self) -> str:
        return "um y, die starke Achse" if self is Profilachse.Y else "um z, die schwache Achse"

    @property
    def kurz(self) -> str:
        """Fuer den Schalter -- der lange Name steht in seinem Titel."""
        return "um y – stark" if self is Profilachse.Y else "um z – schwach"

    @property
    def traegheit(self) -> str:
        """Der Kurzname des Traegheitsmoments der Profilform, das dann ``I`` ist."""
        return f"I_{self.value}"

#: Was ein Material des Systems ist: ein Beton oder Baustahl des Projekts --
#: E und Dichte von ihm, nicht zu aendern -- oder ein eigenes mit E und
#: Dichte von Hand (Benutzer, 2026-10-24; Baustahl seit 2026-11-15).
#: Betonstahl ist keines: aus ihm ist kein Stab. Welche Arten des Projekts
#: es gibt, sagen die Kennwerte, die ein Stab aus ihnen nimmt.
STABMATERIALARTEN = (*(art.value for art in STABKENNWERTE), "eigen")

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
    Ein Material der Staebe (Benutzer, 2026-10-24): ein Beton oder Baustahl
    des Projekts (``stoff``) -- E und Dichte von ihm, siehe
    :data:`~opencivil.stabwerk.rechnung.STABKENNWERTE` -- oder ein eigenes
    mit ``E`` und ``rho`` von Hand.
    """

    kennung: str = ""
    art: str = einer_von(STABMATERIALARTEN, "beton")
    stoff: str = ""
    """Die Kennung des Betons oder Baustahls im Projekt (``b1``, ``st1``) -- nicht bei ``eigen``."""

    name: str = ""
    """Wie ein eigenes heisst; ein Beton oder Baustahl heisst wie im Projekt."""

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
class StabquerschnittEintrag(StabquerschnittBasis):
    """
    Ein Querschnitt der Staebe in der Ebene: dazu aus einer Platte oder
    einer Querschnittsanalyse des Projekts (``bezug``), ein Stahlprofil
    gebogen um ``achse``. E kommt vom Material des Stabs; nimmt der das
    Material des Querschnitts, sagt ``e_modul``, welches E.
    """

    KENNWERTE = KENNWERTE

    achse: Profilachse = Profilachse.Y
    bezug: str = ""
    e_modul: str = einer_von(E_MODULE, "e0")
    """
    Welches E ein Stab hat, der das Material dieses Querschnitts nimmt:
    ``e0`` -- E_cm seines Betons -- oder ``e_eq``, wie ``eq`` sagt.
    """

    eq: ModulEintrag = field(default_factory=ModulEintrag)
    """Wie das E_eq entsteht -- es gilt nur bei ``e_modul = "e_eq"``."""

    def fehler(self) -> Optional[str]:
        if self.e_modul == "e_eq" and not self.art.aus_bauteil:
            return ("ein E_eq gibt es nur bei einem Querschnitt aus einer Platte oder "
                    "Querschnittsanalyse – nur sie haben eine Momenten-Krümmungs-Linie.")
        return super().fehler()


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
class BalkensystemEintrag(MitStaeben, MitFaellen, BauteilEintrag):
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

    ACHSEN = ("x", "z")
    LAGERFELDER = ("x", "z", "phi")
    LINIENLAGER = ("quer", "laengs")
    LAGERARTEN = LAGERARTEN
    NEUE_DIAGRAMME = ("M", "V", "N")
    KNOTEN = SystemknotenEintrag
    LINIE = SystemlinieEintrag
    LAGER = LagerEintrag
    STABLAST = StablastEintrag
    KNOTENLAST = KnotenlastEintrag
    MATERIAL = StabmaterialEintrag
    QUERSCHNITT = StabquerschnittEintrag
    DIAGRAMM = StatikdiagrammEintrag

    def bezuege(self) -> List[str]:
        """Die Platten und Querschnittsanalysen, deren Querschnitt ein Stab nimmt."""
        return sorted({q.bezug for q in self.querschnitte if q.art.aus_bauteil and q.bezug})

    def _kehrt_um(self, last: StablastEintrag) -> bool:
        """
        Die gestrichelte Faser liegt nach dem Umkehren auf der anderen Seite:
        eine Kraft quer oder laengs kehrt mit ihr um. Senkrecht, waagrecht und
        Momente -- sie drehen im Gegenuhrzeigersinn -- aendern sich nicht.
        """
        return last.richtung in (Lastrichtung.QUER, Lastrichtung.LAENGS) and last.art.kraft

    def stahlprofil(self, name: str, profil: str, achse: str = "y") -> StabquerschnittEintrag:
        """Ein Stahlprofil aus der Tabelle, «HEB 300» -- gebogen um ``achse``, y die starke."""
        return super().stahlprofil(name, profil, achse=achse)

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
                                         name=name, art=art, bezug=kennung_von(bezug))
        if E_eq is not None:
            eintrag.e_modul = "e_eq"
            eintrag.eq = ModulEintrag.aus_dict(dict(E_eq), f"Querschnitt '{name}', E_eq")
        self.querschnitte.append(eintrag)
        return eintrag
