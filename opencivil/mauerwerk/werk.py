"""
opencivil/mauerwerk/werk.py -- eine Mauerwerkswand im Rechenwerk.

VERANTWORTUNG:
Was eine Wand im Rechenwerk anmeldet: ihre Vorgaben (:data:`VORGABEN`) --
in der Maske die Kachel «Mauerwerk», in der Herleitung ein Kasten -- und
eine Prozedur, die ihre Zeichnung prüft (:mod:`~opencivil.mauerwerk.pruefen`),
die Werte ihres Mauerwerks liest, an den Mindestwerten misst und nach ihrer Wahl umrechnet
(:mod:`~opencivil.mauerwerk.kennwerte`), die Pfeiler bestimmt
(:func:`~opencivil.mauerwerk.modell.pfeiler`) und die Herleitung schreibt
(:mod:`~opencivil.mauerwerk.herleitung`).

DAS ERGEBNIS:
kommt als Befund in die Lösung (:class:`Wandbefund`); Zeichnung und
Zusammenfassung lesen es dort. Eine Wand, der etwas fehlt, ist ein Befund
mit Meldung und keine Ausnahme: der Rest des Projekts rechnet weiter.

NOCH OHNE LASTEN:
Lastfälle und Nachweise kommen in den nächsten Schritten (Plan vom
2026-11-27, Schritt 14 b–e). Bis dahin rechnet die Wand ihre Form und ihre
Werte.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Sequence

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben, Prozedur
from opencivil.core.einheiten import MM, Groesse
from opencivil.core.protokoll import Abschnitt, Protokoll
from opencivil.core.rechenobjekt import Rechenobjekt
from opencivil.core.vorgaben import Feld, Gruppe
from opencivil.core.wert import WertDef
from opencivil.material.basis import Baustoff
from opencivil.mauerwerk import herleitung
from opencivil.mauerwerk.kennwerte import GELESEN, Wandwerte, unter_mindestwerten, wandwerte
from opencivil.mauerwerk.modell import Pfeiler, Wand, pfeiler
from opencivil.mauerwerk.pruefen import dickenhinweis, pruefen
from opencivil.stabwerk.system import Meldung

#: Unter welchem Thema ihre Herleitung in der Formelsammlung steht.
THEMA = "Mauerwerk"

#: Was die Wand aus ihrer Beschreibung liest (:mod:`opencivil.core.vorgaben`).
VORGABEN = (Gruppe("Mauerwerk", lambda: (
    Feld("t", "t_w", MM, "Dicke der Wand", stellen=0, schritt=5,
         hinweis="Meist so dick, wie die Steine der Sorte sind – eine andere Dicke geht auch."),)),)


@dataclass
class Wandbefund:
    """Was die Rechnung fand: die Wand, ihr Mauerwerk, ihre Meldungen, Werte und Pfeiler."""

    wand: Wand
    mauerwerk: str
    """Der Name ihres Mauerwerks."""

    material: Dict[str, float]
    """Je Kurzname, was die Wand von ihrem Mauerwerk liest (:data:`.kennwerte.GELESEN`)."""

    werte: Wandwerte
    t: float
    """Ihre Dicke, in m."""

    meldungen: List[Meldung]
    """Was an der Zeichnung falsch ist oder fehlt -- die der Beschreibung zuerst."""

    zum_mauerwerk: List[Meldung] = field(default_factory=list)
    """
    Was zu Mauerwerk und Dicke zu sagen ist: Werte unter den Mindestwerten
    deklarierten Mauerwerks, eine unübliche Dicke -- in der Maske bei ihren
    Feldern.
    """

    gezeichnet: bool = False
    """Ob ihre Zeichnung rechnet: keine Meldung zu Umriss, Öffnungen oder Stürzen hält sie auf."""

    pfeiler: List[Pfeiler] = field(default_factory=list)
    """Leer, solange sie nicht :attr:`gezeichnet` ist."""

    @property
    def alle_meldungen(self) -> List[Meldung]:
        """Was zur Zeichnung zu sagen ist, dann was zu Mauerwerk und Dicke."""
        return self.meldungen + self.zum_mauerwerk

    @property
    def bereit(self) -> bool:
        """Ob die Wand rechnet: keine Meldung hält sie auf."""
        return not any(m.haelt_an for m in self.alle_meldungen)


class WandProzedur(Prozedur):
    """Die ganze Wand, geprüft, umgerechnet und aufgeschrieben."""

    def __init__(self, wand: "Mauerwerkswand", **kwargs) -> None:
        super().__init__(**kwargs)
        self.wand = wand

    def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        return self.wand.rechnen_und_schreiben(e, p)


class Mauerwerkswand(Rechenobjekt):
    """Eine Wand aus Mauerwerk, fertig für das Rechenwerk."""

    WAS = "Mauerwerk"

    def __init__(self, *, name: str, kennung: str, praefix: str, wand: Wand, mauerwerk: Baustoff,
                 vorgaben: Mapping[str, Groesse], meldungen: Sequence[Meldung] = ()) -> None:
        """
        ``vorgaben`` je Feld der :data:`VORGABEN` seine Zahl, wie sie
        eingegeben ist; ``meldungen`` sind die der Beschreibung: ein Verweis
        ins Leere, eine doppelte Kennung.
        """
        self.name = name
        self.kennung = kennung
        self.id = praefix
        self.wand = wand
        self.mauerwerk = mauerwerk
        self.meldungen = list(meldungen)
        self.definitionen: Dict[str, WertDef] = {}
        self.berechnungen = []
        for gruppe in VORGABEN:
            for f in gruppe.fuer(self):
                d, vorgabe = f.vorgabe(self.id, self.abschnitt(), gruppe.titel, vorgaben[f.kurz])
                self.definitionen[f.kurz] = d
                self.berechnungen.append(vorgabe)
        self.rechnung = WandProzedur(
            self, id=f"{self.id}.rechnung", ausgaben=[],
            bezuege=[*(Eingabebezug(k, mauerwerk.id_von(k)) for k in GELESEN),
                     *(Eingabebezug(k, d.id) for k, d in self.definitionen.items())],
            titel="Mauerwerkswand", abschnitt=self.abschnitt())
        """Die Prozedur, die die Wand rechnet -- ihr Befund ist der :class:`Wandbefund`."""
        self.berechnungen.append(self.rechnung)

    @property
    def baustoffe(self) -> Sequence[Baustoff]:
        return (self.mauerwerk,)

    def abschnitt(self) -> Abschnitt:
        return Abschnitt(f"Mauerwerk: {self.name}", self.id, thema=THEMA)

    def ziele(self) -> List[str]:
        """Was ein Lauf rechnen muss: die Wand."""
        return [self.rechnung.id]

    def rechnen_und_schreiben(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        """Die Wand geprüft, ihre Werte umgerechnet, Pfeiler bestimmt, Herleitung geschrieben."""
        material = {k: e.g(k).zahl for k in GELESEN}
        t_mm = e.g("t").in_einheit(MM)
        w = self.wand
        meldungen = self.meldungen + pruefen(w)
        flaeche = w.flaeche
        # Die Pfeiler hängen nur an der Zeichnung: taugt das Mauerwerk nicht, stehen sie trotzdem.
        gezeichnet = flaeche is not None and not any(m.haelt_an for m in meldungen)
        zum_mauerwerk = unter_mindestwerten(material, self.mauerwerk.name)
        hinweis = dickenhinweis(self.mauerwerk.sorte, t_mm)
        if hinweis is not None:
            zum_mauerwerk.append(hinweis)
        befund = Wandbefund(w, self.mauerwerk.name, material,
                            wandwerte(material, w.verband, w.vollfugig), t_mm / 1e3, meldungen,
                            zum_mauerwerk, gezeichnet,
                            pfeiler(flaeche, w.oeffnungen) if gezeichnet else [])
        herleitung.schreiben(p, befund)
        return Ausfuehrung({}, befund=befund)
