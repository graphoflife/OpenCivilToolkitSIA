"""
opencivil/projekt/gleichungen.py -- ein Blatt analytischer Gleichungen, wie es
gespeichert wird.

VERANTWORTUNG:
Die Beschreibung eines Blatts: Kennung, Name und die Zeilen. Gerechnet wird in
:mod:`opencivil.gleichungen.blatt`; hier steht nur, was in der Datei steht.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Mapping

from opencivil.projekt.eintraege import Beschreibung
from opencivil.projekt.lesen import ProjektFehler, pflichtfeld

#: Was eine Zeile sein kann.
ZEILENARTEN = ("formel", "projektwert", "text")


@dataclass
class GleichungszeileEintrag(Beschreibung):
    """
    Eine Zeile des Blatts.

    * ``formel``: ``latex`` wie der Editor es schreibt -- eine Definition
      (``b = 2a + 1\\,\\mathrm{m}``) oder eine Auswertung (``a \\cdot b =``);
      ``einheit`` die gewuenschte Einheit des Ergebnisses, leer heisst frei.
    * ``projektwert``: ein gerechneter Wert des Projekts (``wert_id``), im
      Blatt unter ``name`` (LaTeX, etwa ``f_{cd}``).
    * ``text``: ein Satz dazwischen.
    """

    art: str = "formel"
    latex: str = ""
    einheit: str = ""
    name: str = ""
    wert_id: str = ""
    text: str = ""

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "GleichungszeileEintrag":
        art = str(d.get("art") or cls.art)
        if art not in ZEILENARTEN:
            raise ProjektFehler(
                f"Eine Gleichungszeile der Art '{art}' gibt es nicht "
                f"(möglich: {', '.join(ZEILENARTEN)}).")
        return cls(art=art,
                   **{f: str(d.get(f) or getattr(cls, f))
                      for f in ("latex", "einheit", "name", "wert_id", "text")})


@dataclass
class GleichungsblattEintrag(Beschreibung):
    """Ein Blatt: Zeile fuer Zeile Gleichungen, Projektwerte, Text."""

    kennung: str
    name: str
    zeilen: List[GleichungszeileEintrag] = field(default_factory=list)

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "GleichungsblattEintrag":
        kennung = pflichtfeld(d, "kennung", "Ein Gleichungsblatt")
        return cls(
            kennung=kennung,
            name=str(d.get("name") or kennung),
            zeilen=[GleichungszeileEintrag.aus_dict(z) for z in (d.get("zeilen") or [])],
        )
