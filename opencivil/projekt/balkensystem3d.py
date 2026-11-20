"""
opencivil/projekt/balkensystem3d.py -- ein 3D-Balkensystem, wie die Oberflaeche es beschreibt.

VERANTWORTUNG:
Der :class:`Balkensystem3dEintrag`: ein Rahmen im Raum aus Knoten und
Linien, Lagern und Lasten, mit seinen Materialien, Querschnitten,
Lastfaellen und Kombinationen -- wie das 2D-Balkensystem
(:mod:`opencivil.projekt.balkensystem`), mit dessen Baukasten
(:mod:`opencivil.projekt.staebe`). Was dort ueber Geometrie und Lasten an
ihren Elementen steht, gilt hier genauso. Gerechnet wird in
:mod:`opencivil.stabwerk3d`.

WAS DER RAUM ANDERS MACHT:
Ein Knoten hat x, y und z; ein Lager haelt je Verschiebung und Drehung
um die drei Achsen. Eine Linie hat den Drehwinkel β ihres Querschnitts um
ihre Achse und Linienlager laengs und quer in y und z des Querschnitts.
Eine Last zeigt senkrecht, in x, y oder z des Systems oder laengs und quer
in y oder z des Stabs (:class:`~opencivil.stabwerk3d.modell.Richtung`),
eine an einem Knoten nur in eine Richtung des Systems. Ein Querschnitt ist
nach Vorlage, ein Stahlprofil -- y die starke Achse, gedreht wird mit β --,
von Hand mit I_y, I_z und I_T oder aus einer Platte oder
Querschnittsanalyse, wie in der Ebene (Benutzer, 2026-11-18): der Streifen
b × h mit den Formeln des Rechtecks, b waagrecht, wenn β null ist; die
Analyse mit A, I_y und I_z ihres Bruttoquerschnitts und einem I_T, das sie
dafuer numerisch rechnet (:mod:`~opencivil.querschnitt.torsion`). Ein Stab
«gemäss Querschnitt» nimmt deren Beton, mit G_cm fuer die Torsion; ein
E_eq gilt fuer EA, EI_y und EI_z (nach Vorgabe, nicht nachgeschlagen).
Ein eigenes Material hat dazu seinen Schubmodul G.

KOORDINATEN UND EINHEITEN:
x und y waagrecht, z nach oben, in m; Stellen auf einem Stab in % seiner
Laenge ab seinem Anfang, der Drehwinkel in Grad. Querschnittsmasse in mm,
A in mm², I_y, I_z und I_T in 10⁶ mm⁴. Lasten in kN, kN/m, kNm und kNm/m;
Federn in kN/m und kNm/rad, Bettung in kN/m². Umgerechnet wird beim Bauen.

VORZEICHEN:
Eine Kraftlast ist positiv in ihrer Richtung, eine Momentlast dreht im
Rechtssinn um sie (:mod:`opencivil.stabwerk3d.modell`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from opencivil.core.einheiten import GRAD, KN_PRO_M, KN_PRO_M2, KNM_PRO_RAD, M, N_PRO_MM2
from opencivil.projekt.balkensystem import (
    EIGENES_MATERIAL, HALT, KnotenlastEintrag, StablastEintrag, StabmaterialEintrag, StatikdiagrammEintrag,
    federfeld,
)
from opencivil.projekt.eintraege import BauteilEintrag, Beschreibung
from opencivil.projekt.faelle import LastfallEintrag, LastkombinationEintrag, MitFaellen
from opencivil.projekt.lesen import bereich, einer_von
from opencivil.projekt.staebe import MitStaeben, StabquerschnittBasis
from opencivil.stabwerk.stabquerschnitt import RAEUMLICH
from opencivil.stabwerk3d.modell import Richtung
from opencivil.stabwerk3d.raum import minus
from opencivil.stabwerk3d.stab import drehung_umgekehrt

#: Wohin eine Last an einem Knoten zeigt -- in die Richtungen des Systems.
KNOTENRICHTUNGEN = tuple(r for r in Richtung if r.im_system)

#: Was ein Diagramm zeigt: je Stab den Verlauf einer Schnittgroesse, das
#: verschobene System oder die Lagerkraefte.
DIAGRAMMGROESSEN = ("N", "V_y", "V_z", "T", "M_y", "M_z", "verschiebung", "lagerkraefte")

#: Die Vorwahlen eines Lagers -- je Richtung frei oder fest, in der Folge
#: x, y, z, φ_x, φ_y, φ_z. Gelenkig haelt jede Verschiebung, verschieblich
#: nur die lotrechte.
LAGERARTEN = {
    "gelenkig": ("fest", "fest", "fest", "frei", "frei", "frei"),
    "verschieblich": ("frei", "frei", "fest", "frei", "frei", "frei"),
    "eingespannt": ("fest",) * 6,
}


# ===========================================================================
# Die Teile
# ===========================================================================


@dataclass
class RaumknotenEintrag(Beschreibung):
    """Ein Punkt des Systems, in m."""

    kennung: str = ""
    x: float = bereich(0.0, heisst="x", einheit=M)
    y: float = bereich(0.0, heisst="y", einheit=M)
    z: float = bereich(0.0, heisst="z", einheit=M)


@dataclass
class RaumstablastEintrag(StablastEintrag):
    """Eine Last auf einem Stab -- wie in der Ebene, mit einer Richtung des Raums."""

    richtung: Richtung = Richtung.SENKRECHT


@dataclass
class RaumlinieEintrag(Beschreibung):
    """
    Eine Linie des Systems: ein Stab, wenn sie einen Querschnitt hat; dazu,
    oder ohne Stab, ein Linienlager laengs und quer in y und z.
    """

    kennung: str = ""
    von: str = ""
    bis: str = ""
    querschnitt: str = ""
    """Kennung des Querschnitts im System (``Q1``); leer: kein Stab, nur eine Linie."""

    material: str = ""
    """
    Kennung eines Materials des Systems (``M1``) -- oder
    :data:`~opencivil.projekt.staebe.MATERIAL_DES_QUERSCHNITTS`: der Beton,
    den eine Platte oder Querschnittsanalyse als Querschnitt mitbringt.
    """

    drehung: float = bereich(0.0, heisst="Drehwinkel β", einheit=GRAD)
    """Wie weit der Querschnitt um die Achse des Stabs gedreht ist (:mod:`opencivil.stabwerk3d.stab`)."""

    gelenk_anfang: bool = False
    gelenk_ende: bool = False
    quer_y: str = einer_von(HALT, "frei")
    k_quer_y: float = federfeld("Bettung quer in y", KN_PRO_M2)
    quer_z: str = einer_von(HALT, "frei")
    k_quer_z: float = federfeld("Bettung quer in z", KN_PRO_M2)
    laengs: str = einer_von(HALT, "frei")
    k_laengs: float = federfeld("Bettung längs", KN_PRO_M2)
    lasten: List[RaumstablastEintrag] = field(default_factory=list)

    @property
    def stab(self) -> bool:
        """Ob die Linie traegt -- sie hat einen Querschnitt."""
        return bool(self.querschnitt)


@dataclass
class RaumlagerEintrag(Beschreibung):
    """Ein Lager an einem Knoten: je Richtung des Systems frei, fest oder Feder."""

    kennung: str = ""
    knoten: str = ""
    x: str = einer_von(HALT, "fest")
    k_x: float = federfeld("Federsteifigkeit k_x", KN_PRO_M)
    y: str = einer_von(HALT, "fest")
    k_y: float = federfeld("Federsteifigkeit k_y", KN_PRO_M)
    z: str = einer_von(HALT, "fest")
    k_z: float = federfeld("Federsteifigkeit k_z", KN_PRO_M)
    phi_x: str = einer_von(HALT, "frei")
    k_phi_x: float = federfeld("Federsteifigkeit k_φx", KNM_PRO_RAD)
    phi_y: str = einer_von(HALT, "frei")
    k_phi_y: float = federfeld("Federsteifigkeit k_φy", KNM_PRO_RAD)
    phi_z: str = einer_von(HALT, "frei")
    k_phi_z: float = federfeld("Federsteifigkeit k_φz", KNM_PRO_RAD)


@dataclass
class RaumknotenlastEintrag(KnotenlastEintrag):
    """Eine Last an einem Knoten -- eine Kraft in ihre Richtung oder ein Moment um sie."""

    richtung: Richtung = einer_von(KNOTENRICHTUNGEN, Richtung.SENKRECHT)


@dataclass
class RaummaterialEintrag(StabmaterialEintrag):
    """Ein Material der Staebe -- wie in der Ebene, ein eigenes dazu mit seinem Schubmodul."""

    G: float = bereich(EIGENES_MATERIAL["G"], heisst="Schubmodul G", einheit=N_PRO_MM2, ueber=0.0)
    """N/mm² -- nur bei ``eigen``; zu Beginn G_cm des ersten Betons (:data:`EIGENES_MATERIAL`)."""


@dataclass
class RaumquerschnittEintrag(StabquerschnittBasis):
    """Ein Querschnitt der Staebe im Raum -- siehe Dateikopf."""

    KENNWERTE = RAEUMLICH


@dataclass
class RaumdiagrammEintrag(StatikdiagrammEintrag):
    """Ein Diagramm des Systems: ein Fall und was es von ihm zeigt."""

    groesse: str = einer_von(DIAGRAMMGROESSEN, "M_y")


# ===========================================================================
# Das System
# ===========================================================================


@dataclass
class Balkensystem3dEintrag(MitStaeben, MitFaellen, BauteilEintrag):
    """
    Ein Rahmen im Raum: Knoten, Linien, Lager, Lasten, Querschnitte,
    Lastfaelle, Kombinationen -- was nicht stimmt, steht wie beim
    2D-Balkensystem in seinen Meldungen.
    """

    BEZEICHNUNG = "3D-Balkensystem"
    ACHSEN = ("x", "y", "z")
    LAGERFELDER = ("x", "y", "z", "phi_x", "phi_y", "phi_z")
    LINIENLAGER = ("quer_y", "quer_z", "laengs")
    LAGERARTEN = LAGERARTEN
    NEUE_DIAGRAMME = ("M_y", "M_z", "N")
    #: Keine: eine neue Linie laeuft, wie sie gezeichnet ist -- ihre Faser legt der Drehwinkel β.
    LAUFRICHTUNGEN = ()
    KNOTEN = RaumknotenEintrag
    LINIE = RaumlinieEintrag
    LAGER = RaumlagerEintrag
    STABLAST = RaumstablastEintrag
    KNOTENLAST = RaumknotenlastEintrag
    MATERIAL = RaummaterialEintrag
    QUERSCHNITT = RaumquerschnittEintrag
    DIAGRAMM = RaumdiagrammEintrag

    kennung: str
    name: str
    knoten: List[RaumknotenEintrag] = field(default_factory=list)
    linien: List[RaumlinieEintrag] = field(default_factory=list)
    lager: List[RaumlagerEintrag] = field(default_factory=list)
    knotenlasten: List[RaumknotenlastEintrag] = field(default_factory=list)
    stabmaterialien: List[RaummaterialEintrag] = field(default_factory=list)
    querschnitte: List[RaumquerschnittEintrag] = field(default_factory=list)
    lastfaelle: List[LastfallEintrag] = field(default_factory=list)
    kombinationen: List[LastkombinationEintrag] = field(default_factory=list)
    diagramme: List[RaumdiagrammEintrag] = field(default_factory=list)
    beschreibung: str = ""
    """Freier Text -- geht in keine Rechnung ein."""

    def _kehrt_um(self, last: RaumstablastEintrag) -> bool:
        """
        Umgekehrt zeigen x und y des Stabs in die Gegenrichtung, z bleibt
        (:func:`~opencivil.stabwerk3d.stab.drehung_umgekehrt`): eine Kraft
        laengs oder quer in y kehrt um, ein Moment um diese Achsen ebenso.
        """
        return last.richtung in (Richtung.LAENGS, Richtung.QUER_Y)

    def umkehren(self, kennung: str) -> None:
        """Wie in der Ebene -- und der Drehwinkel so, dass der Querschnitt steht wie vorher."""
        linie = self.linie_von(kennung)
        a, b = self.enden(linie)
        super().umkehren(kennung)
        linie.drehung = drehung_umgekehrt(minus(b, a), linie.drehung, 180.0)
