"""
opencivil/projekt/blechdecken.py -- eine Blechverbunddecke, wie die Oberflaeche sie beschreibt.

VERANTWORTUNG:
Der :class:`BlechdeckeEintrag` einer Querschnittsanalyse
(:class:`~opencivil.projekt.querschnittsanalyse.QuerschnittsanalyseEintrag`):
ein Streifen Blechverbunddecke an einem Knoten -- ihr Beton und ihr
Profilblech aus Materialien des Projekts, dazu die Masse des Blechs aus
seinem Datenblatt (Plan vom 2026-11-25: einen Katalog der Bleche gibt es
nicht). Was daraus folgt -- die Linie des Blechs, seine Dicke, ``d_p`` --,
rechnet :mod:`opencivil.querschnitt.profilblech`.

DER BETON GEHOERT ZUR DECKE (2026-11-27):
Die Decke ist ein Element mit ihrem Beton, nicht ein Blech unter einem
gezeichneten Polygon: so passen Beton und Blech immer zueinander, und eine
andere Rippe aendert beide. Bewehrung zeichnet man in den Beton der Decke
wie in jedes Polygon aus Beton.

DIE GRENZEN:
Die Rippe ist niedriger als die Decke (``h_p < h``), oben nicht breiter als
ihr Abstand und unten schmaler -- sonst stiessen die Rippen unten
aneinander, und der Beton beruehrte sich selbst. Das weisen schon die
Felder ab. Ob die Rippe oben oder unten breiter ist, ist frei: unten
breiter ist das Blech hinterschnitten.

DIE VORGABEN:
Ein Blech mittlerer Groesse, kein Erzeugnis: fuenf Rippen im Abstand von
200 mm, 60 mm hoch, oben 120 mm und unten 70 mm breit, 1100 mm² je Meter,
unter einer Decke von 140 mm.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from opencivil.core.einheiten import MM, MM2_PRO_M
from opencivil.projekt.eintraege import Beschreibung
from opencivil.projekt.lesen import bereich, materialfeld
from opencivil.querschnitt.profilblech import Blechform

#: Wie viele Rippen eine Decke hoechstens hat -- 20 m bei 200 mm Abstand; so
#: zeichnet ein Tippfehler keine tausend (nach Vorgabe, nicht nachgeschlagen).
RIPPEN_BIS = 100


@dataclass
class BlechdeckeEintrag(Beschreibung):
    """Eine Blechverbunddecke an einem Knoten -- siehe Dateikopf."""

    IM_ORT = "Blechverbunddecke"

    kennung: str = ""
    knoten: str = ""
    """Die Ecke links unten: die Unterkante der Rippen, der linke Rand."""

    beton: str = materialfeld("beton")
    blech: str = materialfeld("profilblech")
    """Kennung des Profilblechstahls."""

    h: float = bereich(140.0, heisst="Dicke h", zeichen="h", einheit=MM, ueber=0.0)
    rippen: int = bereich(5, heisst="Rippen n", zeichen="n", ab=1, bis=RIPPEN_BIS)
    h_p: float = bereich(60.0, heisst="Höhe der Rippe h_p", zeichen="h_p", einheit=MM, ueber=0.0,
                         unter_feld="h")
    b_s: float = bereich(200.0, heisst="Rippenabstand b_s", zeichen="b_s", einheit=MM, ueber=0.0)
    b_o: float = bereich(120.0, heisst="Rippe oben b_o", zeichen="b_o", einheit=MM, ueber=0.0,
                         bis_feld="b_s")
    b_u: float = bereich(70.0, heisst="Rippe unten b_u", zeichen="b_u", einheit=MM, ueber=0.0,
                         unter_feld="b_s")
    A_p: float = bereich(1100.0, heisst="Blech A_p je Meter Breite", zeichen="A_p",
                         einheit=MM2_PRO_M, ueber=0.0)
    """Die Flaeche des Blechs je Meter Breite, aus dem Datenblatt."""

    def form(self, ursprung: Tuple[float, float]) -> Blechform:
        """Die Form des Blechs mit der Ecke links unten bei ``ursprung``, in mm."""
        return Blechform(ursprung=ursprung, rippen=self.rippen, h=self.h, h_p=self.h_p,
                         b_s=self.b_s, b_o=self.b_o, b_u=self.b_u, A_p=self.A_p)
