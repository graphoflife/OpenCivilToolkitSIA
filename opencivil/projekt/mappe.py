"""
opencivil/projekt/mappe.py -- mehrere Projekte in einer Datei.

VERANTWORTUNG:
Die :class:`Mappe` haelt die Projekte, die zusammen gespeichert und geoeffnet
werden -- «Wohnhaus», «Halle». Gerechnet wird je Projekt, jedes fuer sich;
die Mappe prueft nur, was zwischen ihnen gilt: es gibt mindestens eines, und
jedes heisst anders. Am Namen erkennt man ein Projekt in der Oberflaeche, in
Meldungen und im Zwischenspeicher des Dienstes (:mod:`opencivil.web.speicher`).

EINE DATEI, ZWEI FORMEN:
Seit 2026-11-20 schreibt die Oberflaeche ``{"projekte": [...]}``. Eine Datei
mit einem einzelnen Projekt, wie sie bis dahin geschrieben wurde, oeffnet als
Mappe mit diesem einen. Umgeschrieben werden muss dafuer nichts: jedes
Projekt steht in der Mappe so da wie vorher allein.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Mapping

from opencivil.projekt.aufbau import BAUTEILE
from opencivil.projekt.lesen import ProjektFehler, ort
from opencivil.projekt.projekt import Projekt

#: Woran ein Projekt in einer Datei zu erkennen ist -- mindestens eines davon
#: muss dastehen. Jedes Feld eines Projekts hat eine Vorgabe, ``{}`` liest
#: sich darum als leeres Projekt: wer beim Oeffnen eine falsche Datei
#: erwischte, bekaeme wortlos ein leeres und haette seine Arbeit verloren.
KENNFELDER = ("name", "materialien", *(art.liste for art in BAUTEILE))


def projekt_aus_datei(roh: Any) -> Projekt:
    """
    Ein Projekt, wie es in einer Datei steht: erkannt (:data:`KENNFELDER`),
    gelesen und geprueft -- durch denselben Leser wie alles andere
    (:mod:`opencivil.projekt.lesen`), nicht durch eine zweite Pruefung in
    JavaScript. Alte Formate liest er nicht; eine solche Datei nennt das
    erste Feld, das er nicht kennt.
    """
    if not isinstance(roh, Mapping):
        raise ProjektFehler("Die Beschreibung muss ein JSON-Objekt sein.")
    if not any(feld in roh for feld in KENNFELDER):
        raise ProjektFehler("Das sieht nicht nach einem Projekt aus – keines der Felder "
                            + ", ".join(KENNFELDER) + " ist vorhanden.")
    projekt = Projekt.aus_dict(roh)
    projekt.pruefen()
    return projekt


def _wer(roh: Any, i: int) -> str:
    """Wie das Projekt an Stelle ``i`` in Meldungen heisst: «Projekt 'Halle'», ohne Namen «Projekt 2»."""
    benannt = ort(Projekt, roh)
    return benannt if benannt != "Projekt" else f"Projekt {i + 1}"


@contextmanager
def _im(wer: str) -> Iterator[None]:
    """
    Ein Fehler darin nennt sein Projekt zuerst -- «Projekt 'Halle', Platte
    'Decke': …»: in einer Mappe steht eine Platte 'Decke' vielleicht in
    jedem Projekt. Wo der Ort schon das Projekt ist, steht es einmal.
    """
    try:
        yield
    except ProjektFehler as fehler:
        wo = fehler.wo
        for eigen in (wer, "Projekt"):
            if wo == eigen or wo.startswith(f"{eigen}, "):
                raise ProjektFehler(fehler.grund, wo=wer + wo[len(eigen):]) from None
        raise ProjektFehler(fehler.grund, wo=f"{wer}, {wo}" if wo else wer) from None


@dataclass
class Mappe:
    """Die Projekte einer Datei, in der Reihenfolge, in der die Oberflaeche sie zeigt."""

    projekte: List[Projekt] = field(default_factory=list)

    # -- Pruefung -----------------------------------------------------------

    def pruefen(self) -> None:
        """Prueft jedes Projekt (:meth:`Projekt.pruefen`) und was zwischen ihnen gilt."""
        for i, projekt in enumerate(self.projekte):
            with _im(_wer({"name": projekt.name}, i)):
                projekt.pruefen()
        self._zwischen_pruefen()

    def _zwischen_pruefen(self) -> None:
        """
        Mindestens ein Projekt, und jedes mit eigenem Namen: an ihm waehlt man
        es aus. Ein leerer Name hiesse in der Oberflaeche ein leerer Knopf.
        """
        if not self.projekte:
            raise ProjektFehler("Darin steht kein Projekt – es braucht mindestens eines.")
        gesehen: Dict[str, int] = {}
        for i, projekt in enumerate(self.projekte):
            if not projekt.name.strip():
                raise ProjektFehler("ein Projekt braucht einen Namen.", wo=f"Projekt {i + 1}")
            if projekt.name in gesehen:
                raise ProjektFehler(
                    f"Das {gesehen[projekt.name] + 1}. und das {i + 1}. Projekt heissen beide "
                    f"'{projekt.name}'. Jedes Projekt braucht seinen eigenen Namen.")
            gesehen[projekt.name] = i

    # -- Datei --------------------------------------------------------------

    def als_dict(self) -> Dict[str, Any]:
        return {"projekte": [p.als_dict() for p in self.projekte]}

    @classmethod
    def aus_dict(cls, roh: Any) -> "Mappe":
        """
        Eine Mappe aus der Datei, gelesen und geprueft. Ohne ``projekte`` ist
        es ein einzelnes Projekt, wie bis 2026-11-20 gespeichert -- die Mappe
        hat dann dieses eine, und seine Meldungen lauten wie damals.
        """
        if not (isinstance(roh, Mapping) and "projekte" in roh):
            return cls([projekt_aus_datei(roh)])
        for schluessel in roh:
            if schluessel != "projekte":
                raise ProjektFehler(f"Neben der Liste 'projekte' steht nichts, "
                                    f"auch kein Feld '{schluessel}'.")
        if not isinstance(roh["projekte"], list):
            raise ProjektFehler("'projekte' muss eine Liste von Projekten sein.")
        projekte = []
        for i, eintrag in enumerate(roh["projekte"]):
            with _im(_wer(eintrag, i)):
                projekte.append(projekt_aus_datei(eintrag))
        mappe = cls(projekte)
        mappe._zwischen_pruefen()
        return mappe
