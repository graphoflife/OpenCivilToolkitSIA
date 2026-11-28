"""
opencivil/fachwerkmodell/verfahren.py -- wie ein Fachwerk gesucht wird.

VERANTWORTUNG:
Die zwei Verfahren eines Fachwerkmodells (:class:`Verfahren`) und ihre
Zahlen (:data:`VORGABEN`) -- in der Maske die Kachel «Verfahren», in der
Herleitung ein Kasten:

- Ground Structure (:mod:`~opencivil.fachwerkmodell.suche`): Knoten in
  einem Raster, je zwei ein möglicher Stab; eine lineare Optimierung wählt
  das leichteste Fachwerk im Gleichgewicht, Runde um Runde mit mehr Stäben.
- SIMP (:mod:`~opencivil.fachwerkmodell.form`): das Material verteilt sich
  Schritt um Schritt zur steifsten Form; aus ihr liest das Werkzeug ein
  Fachwerk, dessen Kräfte dieselbe Optimierung bestimmt.

Beide teilen das Gewicht des Zugs gegenüber dem Druck und die kleinste
Stabkraft, die stehen bleibt.
"""

from __future__ import annotations

from typing import Tuple

from opencivil.core.einheiten import EINHEITSLOS, M, PROZENT
from opencivil.core.vorgaben import Feld, Gruppe
from opencivil.core.wahl import Wahl
from opencivil.fachwerkmodell.grundstruktur import HOECHSTENS_KNOTEN
from opencivil.fachwerkmodell.simp import HOECHSTENS_ELEMENTE


class Verfahren(Wahl):
    """Wie ein Fachwerk gesucht wird -- siehe Dateikopf."""

    GROUND_STRUCTURE = "ground_structure"
    SIMP = "simp"

    @property
    def beschriftung(self) -> str:
        return {Verfahren.GROUND_STRUCTURE: "Ground Structure", Verfahren.SIMP: "SIMP"}[self]

    @property
    def erklaerung(self) -> str:
        return {
            Verfahren.GROUND_STRUCTURE: "Knoten in einem Raster, je zwei ein möglicher Stab – eine "
                                        "lineare Optimierung wählt das leichteste Fachwerk",
            Verfahren.SIMP: "Das Material verteilt sich zur steifsten Form – aus ihr liest das "
                            "Werkzeug ein Fachwerk",
        }[self]


def _felder(verfahren: Verfahren) -> Tuple[Feld, ...]:
    """Die Zahlen des Verfahrens: zuerst, was nur es hat, dann, was beide teilen."""
    if verfahren is Verfahren.SIMP:
        eigene = (
            Feld("netzweite", "h", M, "Seite eines Elements", 2, beschriftung="Netzweite",
                 schritt=0.05, hinweis=f"feiner gibt eine klarere Form und rechnet länger – mehr "
                                       f"als {HOECHSTENS_ELEMENTE} Elemente rechnet das Werkzeug "
                                       f"nicht"),
            Feld("volumen", r"\bar{\rho}", PROZENT, "Anteil des Materials an der Fläche der Scheibe",
                 0, beschriftung="Anteil Material", schritt=5,
                 hinweis="so viel der Scheibe bekommt die Form – weniger gibt schlankere Stäbe"),
        )
    else:
        eigene = (
            Feld("rasterweite", "h", M, "Abstand der Knoten im Raster", 2, beschriftung="Rasterweite",
                 schritt=0.05, hinweis=f"feiner sucht genauer und länger – mehr als "
                                       f"{HOECHSTENS_KNOTEN} Knoten sucht das Werkzeug nicht"),
        )
    return (*eigene,
            Feld("w_Z", "w_Z", EINHEITSLOS, "Gewicht des Zugs gegenüber dem Druck", 2,
                 beschriftung="Zug : Druck", schritt=0.1,
                 hinweis="1: beide zählen gleich – grösser: das Fachwerk meidet Zug, kleiner: Druck"),
            Feld("N_min", "N_{min}", PROZENT, "Kleinste Stabkraft, bezogen auf die grösste", 1,
                 beschriftung="Kleinste Stabkraft", schritt=0.5,
                 hinweis="dünnere Stäbe fallen weg, dann sucht die Optimierung das Gleichgewicht "
                         "neu"))


#: Die Zahlen der Verfahren, in der Maske eine Kachel, in der Herleitung ein Kasten.
VORGABEN = (Gruppe("Verfahren", _felder, nach=("verfahren",)),)
