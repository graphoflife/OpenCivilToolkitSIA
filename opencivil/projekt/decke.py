"""
opencivil/projekt/decke.py -- eine Stahlbetondecke, wie die Oberflaeche sie beschreibt.

VERANTWORTUNG:
Der :class:`DeckeEintrag`: Platten, Linienlager, Stuetzen, versteckte
Unterzuege und Zonen der Lastaufteilung, gezeichnet aus Knoten im Grundriss
-- als speicherbare Datenklasse wie das Balkensystem
(:mod:`opencivil.projekt.balkensystem`). Dazu der Baukasten, der ohne
Oberflaeche zeichnet. Gerechnet wird nach der Streifenmethode, in
:mod:`opencivil.decke`.

ALLES HAENGT AN KNOTEN:
Eine Platte und eine Zone sind Umrisse aus Knoten, ein Linienlager und ein
Unterzug laufen von einem Knoten zum anderen, eine Stuetze steht an einem.
Wo zwei Platten oder eine Platte und eine Wand sich eine Ecke teilen,
teilen sie den Knoten -- wer ihn verschiebt, verschiebt sie beide, und es
entsteht keine Fuge, die niemand gezeichnet hat.

KOORDINATEN UND EINHEITEN:
x nach rechts, y nach oben, in m -- ebenso die Breite eines Unterzugs, der
Stuetzenbereich und die Streifenbreite. Die Dicke einer Platte und der
Querschnitt einer Stuetze in mm, Anteile in %, die Richtungen der Streifen
in Grad gegen x, im Gegenuhrzeigersinn. Umgerechnet wird beim Bauen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Sequence, Union

from opencivil.core.einheiten import GRAD, M, MM, PROZENT
from opencivil.decke.modell import Aufteilung
from opencivil.projekt.eintraege import BauteilEintrag, Beschreibung
from opencivil.projekt.lesen import bereich, lesen
from opencivil.projekt.netz import Netz, naechste_kennung

#: Ein Ort im Baukasten: die Kennung eines Knotens oder ``(x, y)`` in m.
Ort = Union[str, Sequence[float]]

#: Womit die Kennungen der Teile einer Decke beginnen.
VORSILBEN = {"platten": "P", "linienlager": "L", "stuetzen": "S", "unterzuege": "U",
             "zonen": "Z"}


@dataclass
class DeckenknotenEintrag(Beschreibung):
    """Ein Punkt des Grundrisses, in m."""

    kennung: str = ""
    x: float = 0.0
    y: float = 0.0


@dataclass
class DeckenplatteEintrag(Beschreibung):
    """
    Eine Platte: ihr Umriss, ihre Dicke und ihr Beton -- E_cm und die Dichte
    des Stahlbetons von ihm, wie bei einem Stab des Balkensystems -- und die
    zwei Richtungen, in denen ihre Streifen tragen.
    """

    kennung: str = ""
    knoten: List[str] = field(default_factory=list)
    h: float = bereich(240.0, heisst="Dicke h", einheit=MM, ueber=0.0)
    beton: str = ""
    """Die Kennung des Betons im Projekt (``b1``)."""

    richtung_1: float = bereich(0.0, heisst="Richtung 1", einheit=GRAD, ab=-180.0, bis=180.0)
    richtung_2: float = bereich(90.0, heisst="Richtung 2", einheit=GRAD, ab=-180.0, bis=180.0)


@dataclass
class LinienlagerEintrag(Beschreibung):
    """
    Ein Linienlager -- eine Wand, ein Rand auf einem Träger: vertikal
    gehalten oder nicht, eingespannt oder nicht. Eingespannt ohne vertikalen
    Halt hält es nur die Drehung, wie an einer Symmetrieachse.
    """

    kennung: str = ""
    von: str = ""
    bis: str = ""
    vertikal: bool = True
    eingespannt: bool = False


@dataclass
class StuetzeEintrag(Beschreibung):
    """
    Eine Stütze unter der Decke, ``b_x × b_y``. Die Streifen geben ihre
    Last über den Stützenbereich ``l_x × l_y`` ab (Folie 39) -- von Hand
    oder, ohne Angabe, so gross wie die Stütze oder der breiteste Unterzug
    über ihr (:func:`opencivil.decke.streifen.stuetzenbereich`).
    """

    kennung: str = ""
    knoten: str = ""
    b_x: float = bereich(300.0, heisst="Breite b_x", einheit=MM, ueber=0.0)
    b_y: float = bereich(300.0, heisst="Breite b_y", einheit=MM, ueber=0.0)
    bereich_von_hand: bool = False
    l_x: float = bereich(1.0, heisst="Stützenbereich l_x", einheit=M, ueber=0.0)
    """Nur mit ``bereich_von_hand``."""

    l_y: float = bereich(1.0, heisst="Stützenbereich l_y", einheit=M, ueber=0.0)


@dataclass
class UnterzugEintrag(Beschreibung):
    """
    Ein versteckter Unterzug, ein starker Streifen in der Platte (Folie 33):
    so breit wie ``breite``, liegend auf Linienlagern, Stützen und den
    Unterzügen höherer ``stufe``, die ihn kreuzen.
    """

    kennung: str = ""
    von: str = ""
    bis: str = ""
    breite: float = bereich(1.0, heisst="Breite b", einheit=M, ueber=0.0)
    stufe: int = bereich(1, heisst="Stufe", ab=1)


@dataclass
class ZoneEintrag(Beschreibung):
    """
    Eine Zone der Lastaufteilung: in ihrem Umriss geht ``anteil`` der Last
    in die Richtung 1 der Platte, der Rest in die Richtung 2 -- statt der
    Aufteilung der Decke.
    """

    kennung: str = ""
    knoten: List[str] = field(default_factory=list)
    anteil: float = bereich(50.0, heisst="Anteil in Richtung 1", einheit=PROZENT, ab=0.0, bis=100.0)


@dataclass
class DeckeEintrag(BauteilEintrag):
    """
    Eine Decke aus Platten auf Linienlagern und Stützen, mit versteckten
    Unterzügen und Zonen. Wie die Last aufgeteilt wird, gilt für die ganze
    Decke: automatisch nach Folie 31 oder ``anteil`` in die Richtung 1 --
    in einer Zone deren Anteil.

    Ohne Regeln, die das ganze Projekt aufhielten: was an einer Decke nicht
    stimmt, steht in ihren Meldungen, und die anderen Bauteile rechnen weiter.
    """

    BEZEICHNUNG = "Decke"

    kennung: str
    name: str
    knoten: List[DeckenknotenEintrag] = field(default_factory=list)
    platten: List[DeckenplatteEintrag] = field(default_factory=list)
    linienlager: List[LinienlagerEintrag] = field(default_factory=list)
    stuetzen: List[StuetzeEintrag] = field(default_factory=list)
    unterzuege: List[UnterzugEintrag] = field(default_factory=list)
    zonen: List[ZoneEintrag] = field(default_factory=list)
    streifenbreite: float = bereich(0.25, heisst="Streifenbreite", einheit=M, ueber=0.0)
    aufteilung: Aufteilung = Aufteilung.AUTOMATISCH
    anteil: float = bereich(50.0, heisst="Anteil in Richtung 1", einheit=PROZENT, ab=0.0, bis=100.0)
    """Nur bei fester Aufteilung."""

    beschreibung: str = ""
    """Freier Text -- geht in keine Rechnung ein."""

    def materialien(self) -> List[str]:
        """Jeder Beton des Projekts, auf den eine Platte zeigt -- jeder einmal."""
        return list(dict.fromkeys(p.beton for p in self.platten if p.beton))

    def lagen(self) -> dict:
        """Kennung -> ``(x, y)`` jedes Knotens, in m."""
        return {k.kennung: (k.x, k.y) for k in self.knoten}

    # -- Zeichnen ohne Oberflaeche --------------------------------------------

    def netz(self) -> Netz:
        return Netz(self.knoten, neu=lambda kennung, x, y: DeckenknotenEintrag(kennung, x, y),
                    achsen=("x", "y"))

    def _knoten(self, netz: Netz, ort: Ort) -> str:
        return ort if isinstance(ort, str) else netz.an(float(ort[0]), float(ort[1]))

    def _anlegen(self, liste: str, cls: type, felder: dict, wo: str) -> Any:
        eintrag = lesen(cls, felder, f"Decke '{self.name}': {wo}",
                        cls(kennung=naechste_kennung((e.kennung for e in getattr(self, liste)),
                                                     VORSILBEN[liste])))
        getattr(self, liste).append(eintrag)
        return eintrag

    def platte(self, ecken: Sequence[Ort], *, beton: Any, **felder: Any) -> DeckenplatteEintrag:
        """Eine Platte mit diesen Ecken und dem Beton ``beton`` (Eintrag oder Kennung)."""
        netz = self.netz()
        knoten = [self._knoten(netz, e) for e in ecken]
        beton = beton if isinstance(beton, str) else beton.kennung
        return self._anlegen("platten", DeckenplatteEintrag,
                             {"knoten": knoten, "beton": beton, **felder}, "Platte")

    def lager(self, von: Ort, bis: Ort, **felder: Any) -> LinienlagerEintrag:
        """Ein Linienlager von ``von`` nach ``bis`` -- heisst so, weil die Liste ``linienlager`` heisst."""
        netz = self.netz()
        return self._anlegen("linienlager", LinienlagerEintrag,
                             {"von": self._knoten(netz, von), "bis": self._knoten(netz, bis), **felder},
                             "Linienlager")

    def stuetze(self, ort: Ort, **felder: Any) -> StuetzeEintrag:
        return self._anlegen("stuetzen", StuetzeEintrag,
                             {"knoten": self._knoten(self.netz(), ort), **felder}, "Stütze")

    def unterzug(self, von: Ort, bis: Ort, **felder: Any) -> UnterzugEintrag:
        netz = self.netz()
        return self._anlegen("unterzuege", UnterzugEintrag,
                             {"von": self._knoten(netz, von), "bis": self._knoten(netz, bis), **felder},
                             "Unterzug")

    def zone(self, ecken: Sequence[Ort], **felder: Any) -> ZoneEintrag:
        netz = self.netz()
        return self._anlegen("zonen", ZoneEintrag,
                             {"knoten": [self._knoten(netz, e) for e in ecken], **felder}, "Zone")

    # -- Die frische Anlage -------------------------------------------------------

    @classmethod
    def neu(cls, kennung: str, name: str) -> "DeckeEintrag":
        """Eine leere Decke, wie der Benutzer sie angelegt bekommt."""
        return cls(kennung=kennung, name=name)

