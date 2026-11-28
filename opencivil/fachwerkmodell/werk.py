"""
opencivil/fachwerkmodell/werk.py -- das Fachwerkmodell im Rechenwerk.

VERANTWORTUNG:
Was ein Fachwerkmodell im Rechenwerk anmeldet: die Zahlen seines
Verfahrens als Vorgaben (:data:`~opencivil.fachwerkmodell.verfahren.VORGABEN`)
und eine Prozedur, die sein Modell prüft
(:mod:`~opencivil.fachwerkmodell.pruefen`), das gefundene Fachwerk
nachrechnet (:mod:`~opencivil.fachwerkmodell.nachrechnung`) und die
Herleitung schreibt (:mod:`~opencivil.fachwerkmodell.herleitung`). Es liest
nichts von aussen -- kein Material, keine Dicke (Plan vom 2026-11-27,
Entscheid 11).

GESUCHT WIRD DANEBEN:
Die Suche läuft nicht hier, sondern Runde um Runde auf Anfrage der Seite
(:func:`~opencivil.fachwerkmodell.suche.runde`, im Verfahren SIMP Schritt
um Schritt, :func:`~opencivil.fachwerkmodell.form.schritte`); was sie
zuletzt fand, steht im Projekt. Hier zählt es nur, wenn sein Abdruck zu Modell und
Verfahren passt -- sonst sagt eine Meldung, dass es zu einem früheren
Stand gehört, und es steht nirgends.

DAS ERGEBNIS:
kommt als Befund in die Lösung (:class:`Fachwerkbefund`); Zeichnung und
Zusammenfassung lesen es dort. Ein Modell, dem etwas fehlt, ist ein Befund
mit Meldung und keine Ausnahme: der Rest des Projekts rechnet weiter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence, Union

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben, Prozedur
from opencivil.core.einheiten import Groesse
from opencivil.core.protokoll import Abschnitt, Protokoll
from opencivil.core.rechenobjekt import Rechenobjekt
from opencivil.core.wert import WertDef
from opencivil.decke.herleitung import als_ort
from opencivil.fachwerkmodell import herleitung
from opencivil.fachwerkmodell.form import Formeinstellung
from opencivil.fachwerkmodell.grundstruktur import liegt_achsparallel
from opencivil.fachwerkmodell.modell import Modell
from opencivil.fachwerkmodell.nachrechnung import Nachrechnung, nachrechnen
from opencivil.fachwerkmodell.pruefen import pruefen
from opencivil.fachwerkmodell.suche import ZUG_ACHSPARALLEL, Einstellung, Suchergebnis, abdruck
from opencivil.fachwerkmodell.verfahren import VORGABEN, Verfahren
from opencivil.stabwerk.system import Meldung

#: Die Zahlen eines der beiden Verfahren -- Ground Structure oder SIMP.
Verfahrenseinstellung = Union[Einstellung, Formeinstellung]

#: Unter welchem Thema seine Herleitung in der Formelsammlung steht.
THEMA = "Fachwerkmodell"

#: Wo die Suche beginnt -- in den Meldungen genannt.
IM_FENSTER = "im Fenster «Verfahren» mit «Fachwerk suchen»"

NOCH_KEINES = f"Noch kein Fachwerk gesucht – {IM_FENSTER}."
VERALTET = (f"Das Fachwerk gehört zu einem früheren Stand: Scheibe, Lager, Lasten oder Verfahren "
            f"haben sich seither geändert – neu suchen {IM_FENSTER}.")
UNLESBAR = f"Das gespeicherte Fachwerk lässt sich nicht lesen – neu suchen {IM_FENSTER}."

#: Was ein angehaltenes Fachwerk ist, je Verfahren -- ``{n}`` die letzte Runde oder der letzte Schritt.
ANGEHALTEN = {
    Verfahren.GROUND_STRUCTURE: "Die Suche wurde nach Runde {n} angehalten: das Fachwerk trägt die "
                                "Lasten, ist aber womöglich nicht das leichteste.",
    Verfahren.SIMP: "Die Form wurde nach Schritt {n} angehalten: das Fachwerk aus ihr trägt die "
                    "Lasten, sie ist aber womöglich noch nicht die steifste.",
}


@dataclass
class Fachwerkbefund:
    """Was die Rechnung fand: das Modell, seine Meldungen und das Fachwerk, mit dem, was dazu zu sagen ist."""

    modell: Modell
    einstellung: Verfahrenseinstellung
    meldungen: List[Meldung]
    """Was das Modell meldet -- die Meldungen der Beschreibung zuerst."""

    bereit: bool
    """Ob sich ein Fachwerk suchen lässt: keine Meldung des Modells hält es auf."""

    abdruck: str = ""
    """Der Abdruck von Modell und Verfahren -- leer, solange das Modell nicht bereit ist."""

    stand: str = ""
    """
    Wie es um das Fachwerk steht: ``keines``, ``veraltet``, ``unlesbar``
    oder ``gefunden`` -- leer, solange das Modell nicht bereit ist.
    """

    zum_fachwerk: List[Meldung] = field(default_factory=list)
    """
    Was zum Fachwerk zu sagen ist: dass noch keines gesucht ist oder es zu
    einem früheren Stand gehört, wo sein Gleichgewicht nicht aufgeht, dass
    die Suche angehalten wurde.
    """

    gefunden: Optional[Suchergebnis] = None
    """Was die Suche fand -- nur, wenn es zu Modell und Verfahren gehört."""

    nachrechnung: Optional[Nachrechnung] = None


def offen_meldungen(n: Nachrechnung, einstellung: Verfahrenseinstellung) -> List[Meldung]:
    """
    Wo das Gleichgewicht nicht aufgeht, rot: je Last, die es nicht ganz
    trägt, eine Meldung -- mit «Zug nur waagrecht und senkrecht» sagt sie
    es, denn ohne geht es oft.
    """
    mit = f" mit {ZUG_ACHSPARALLEL}" if einstellung.zug_achsparallel else ""
    meldungen = []
    for last, ort, betrag in n.offen:
        if last is not None:
            meldungen.append(Meldung(f"Die Last {last.name} lässt sich{mit} nicht ganz zu den "
                                     f"Lagern tragen: {betrag / 1e3:.1f} kN bleiben offen.",
                                     (last.name,)))
        else:
            meldungen.append(Meldung(f"Bei {als_ort(ort)} geht das Gleichgewicht{mit} um "
                                     f"{betrag / 1e3:.1f} kN nicht auf."))
    return meldungen


class FachwerkProzedur(Prozedur):
    """Das ganze Fachwerkmodell, geprüft, nachgerechnet und aufgeschrieben."""

    def __init__(self, system: "Fachwerksystem", **kwargs) -> None:
        super().__init__(**kwargs)
        self.system = system

    def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        return self.system.rechnen_und_schreiben(p)


class Fachwerksystem(Rechenobjekt):
    """Ein Fachwerkmodell, fertig für das Rechenwerk."""

    WAS = "Fachwerkmodell"

    def __init__(self, *, name: str, kennung: str, praefix: str, modell: Modell,
                 meldungen: Sequence[Meldung], einstellung: Verfahrenseinstellung,
                 vorgaben: Mapping[str, Groesse], gefunden: Optional[Suchergebnis],
                 unlesbar: bool = False) -> None:
        """
        ``meldungen`` sind die der Beschreibung: ein Verweis ins Leere, eine
        doppelte Kennung. ``vorgaben`` je Feld des Verfahrens seine Zahl, wie
        sie eingegeben ist; ``gefunden``, was im Projekt steht --
        ``unlesbar``, wenn dort eines steht, das keines ist.
        """
        self.name = name
        self.kennung = kennung
        self.id = praefix
        self.modell = modell
        self.meldungen = list(meldungen)
        self.einstellung = einstellung
        self.verfahren = einstellung.verfahren
        """Unter dem Namen, nach dem sich die Vorgaben richten (:data:`VORGABEN`)."""
        self.abdruck = abdruck(modell, einstellung)
        self.gefunden = gefunden
        self.unlesbar = unlesbar
        self.definitionen: Dict[str, WertDef] = {}
        self.berechnungen = []
        for gruppe in VORGABEN:
            for f in gruppe.fuer(self):
                d, vorgabe = f.vorgabe(self.id, self.abschnitt(), gruppe.titel, vorgaben[f.kurz])
                self.definitionen[f.kurz] = d
                self.berechnungen.append(vorgabe)
        self.rechnung = FachwerkProzedur(
            self, id=f"{self.id}.rechnung", ausgaben=[],
            bezuege=[Eingabebezug(k, d.id) for k, d in self.definitionen.items()],
            titel="Fachwerkmodell", abschnitt=self.abschnitt())
        """Die Prozedur, die das Modell rechnet -- ihr Befund ist der :class:`Fachwerkbefund`."""
        self.berechnungen.append(self.rechnung)

    def abschnitt(self) -> Abschnitt:
        return Abschnitt(f"Fachwerkmodell: {self.name}", self.id, thema=THEMA)

    def ziele(self) -> List[str]:
        """Was ein Lauf rechnen muss: das Modell."""
        return [self.rechnung.id]

    def rechnen_und_schreiben(self, p: Protokoll) -> Ausfuehrung:
        """Das Modell geprüft, das Fachwerk nachgerechnet, die Herleitung geschrieben."""
        meldungen = self.meldungen + pruefen(self.modell)
        bereit = not any(m.haelt_an for m in meldungen)
        befund = Fachwerkbefund(self.modell, self.einstellung, meldungen, bereit)
        if bereit:
            befund.abdruck = self.abdruck
            self._fachwerk(befund)
        herleitung.schreiben(p, befund)
        return Ausfuehrung({}, befund=befund)

    def _fachwerk(self, befund: Fachwerkbefund) -> None:
        """Was im Projekt steht, wenn es zu Modell und Verfahren gehört, nachgerechnet -- sonst warum nicht."""
        if self.unlesbar:
            befund.stand = "unlesbar"
            befund.zum_fachwerk.append(Meldung(UNLESBAR))
        elif self.gefunden is None:
            befund.stand = "keines"
            befund.zum_fachwerk.append(Meldung(NOCH_KEINES, fehler=False))
        elif self.gefunden.abdruck != self.abdruck:
            befund.stand = "veraltet"
            befund.zum_fachwerk.append(Meldung(VERALTET, fehler=False))
        else:
            befund.stand = "gefunden"
            befund.gefunden = self.gefunden
            befund.nachrechnung = nachrechnen(self.modell, self.gefunden.fachwerk, self.einstellung.w_Z)
            befund.zum_fachwerk += offen_meldungen(befund.nachrechnung, self.einstellung)
            befund.zum_fachwerk += self._zum_fachwerk(self.gefunden)

    def _zum_fachwerk(self, gefunden: Suchergebnis) -> List[Meldung]:
        """
        Was sonst am gefundenen Fachwerk zu sagen ist: rot ein geneigter Stab
        auf Zug, wo nur waagrechte und senkrechte Zug tragen -- die Suche gibt
        keinen, nur eine Datei von Hand --, wo die Suche anhielt, was dünn blieb.
        """
        fw = gefunden.fachwerk
        meldungen = []
        if self.einstellung.zug_achsparallel:
            meldungen += [Meldung(f"Stab {i} ist geneigt und trägt Zug, obwohl {ZUG_ACHSPARALLEL} "
                                  f"gilt – neu suchen {IM_FENSTER}.")
                          for i, (a, b, N) in enumerate(fw.staebe, start=1)
                          if N > 0.0 and not liegt_achsparallel(fw.knoten[a], fw.knoten[b])]
        if not gefunden.fertig:
            meldungen.append(Meldung(ANGEHALTEN[self.verfahren].format(n=gefunden.runden), fehler=False))
        kraefte = [abs(N) for _, _, N in fw.staebe]
        if kraefte and min(kraefte) < 0.999 * self.einstellung.N_min * max(kraefte):
            meldungen.append(Meldung(
                "Ohne die Stäbe unter der kleinsten Stabkraft ginge das Gleichgewicht nicht auf – "
                "sie bleiben.", fehler=False))
        return meldungen
