"""
opencivil/nachweis/qa_knicken.py -- Knicken am gezeichneten Querschnitt.

VERANTWORTUNG:
Der Knicknachweis der Platte am gezeichneten Querschnitt, je Knickfall in
einer Richtung: der Zugseite, zu der sich der Stab biegt -- unten, oben,
links oder rechts, wie bei den Spannung-Dehnung-Analysen
(:class:`~opencivil.querschnitt.zugseite.Zugseite`). Das Verfahren ist
dasselbe (:class:`~opencivil.nachweis.knicken.Knickverfahren`: Ausmitten-
Iteration, Grenzkraft N_Rd); hier steht nur, woher der Stab kommt
(:class:`~opencivil.nachweis.knicken.Knickstab`):

* die Verformung aus den Fasern in dieser Richtung, mit den Gesetzen der
  Wahl «Verformung» (:meth:`~opencivil.querschnitt.analyse.Querschnittsanalyse.querschnitt`);
* der Widerstand aus dem Bruchzustand bei der Druckkraft in dieser Richtung,
  mit den Gesetzen der Wahl «Widerstand» -- das Moment in Biegerichtung;
* die statische Hoehe vom gedrueckten Rand bis zum entferntesten Stab in
  Zugrichtung, fuer die Mindestausmitte ``d/30``.

DIE NULLLINIE BLEIBT PARALLEL ZUR ACHSE:
wie in der einachsigen Tragsicherheit und den Analysen. Das Moment um die
andere Achse, das ein unsymmetrischer Querschnitt dabei weckt, zaehlt nicht;
um beide Achsen zugleich knickt hier kein Stab -- je Richtung ein Fall.
Nach Vorgabe, nicht nachgeschlagen (``notizbuch/Notizen/TODO.md``).

WAS ES KOSTET:
Jede Probekraft der Suche nach N_Rd ist eine ganze Ausmitten-Iteration, jede
Iteration ein paar Ebenen. Gesucht werden sie mit Illinois
(:class:`~opencivil.nachweis.querschnittsloeser.FaserloeserIllinois`), wie
unter Gebrauchslast.

EINHEITEN:
SI-Basis; die Zeichnung in mm.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from opencivil.core.berechnung import Ausfuehrung, Eingaben, NachweisUrteil, grad_def
from opencivil.core.einheiten import EINHEITSLOS, Groesse
from opencivil.core.latex import als_text
from opencivil.core.protokoll import Protokoll
from opencivil.nachweis.knicken import (
    VERFORMUNG, VERFORMUNG_NACH_WAHL, WIDERSTAND, Knickfall, Knickstab, Knickverfahren,
)
from opencivil.nachweis.querschnittsloeser import FaserloeserIllinois
from opencivil.nachweis.rechenwahl import protokoll_rechenwahl
from opencivil.querschnitt.gesetzwahl import Rechenwahl
from opencivil.querschnitt.analyse import Querschnittsanalyse
from opencivil.querschnitt.interaktion import Querschnitt
from opencivil.querschnitt.schnittanalyse import protokoll_gesetze_nach_wahl
from opencivil.querschnitt.zugseite import Zugseite


@dataclass(frozen=True)
class QAKnickfall(Knickfall):
    """Ein Knickfall des gezeichneten Querschnitts -- mit der Seite, zu der er sich biegt."""

    richtung: Zugseite = Zugseite.UNTEN


def knickstab(verformung: Querschnitt, widerstand: Querschnitt, seite: Zugseite) -> Knickstab:
    """
    Der Stab in einer Richtung: die Fasern des einen Querschnitts fuer die
    Verformung, der Bruchzustand des anderen fuer den Widerstand.
    """
    r = verformung.richtung(seite.psi)

    def moment_bei(N: float, positiv: bool) -> Optional[float]:
        # Das Moment in Biegerichtung: M = -(n_z·M_y + n_y·M_z), die Umkehrung
        # von Richtung.momente -- auf der Gegenseite mit gedrehter Richtung.
        psi = seite.psi if positiv else seite.psi + math.pi
        punkt = widerstand.bei_normalkraft(psi, -N)
        if punkt is None:
            return None
        return -(math.sin(psi) * punkt.M_y + math.cos(psi) * punkt.M_z)

    gedrueckt = r.beton[0]
    return Knickstab(loeser=FaserloeserIllinois(querschnitt=r.fasern, grenzen=r.grenzen),
                     moment_bei=moment_bei,
                     d=max(r.staebe_v, default=r.beton[1]) - gedrueckt)


class KnickenQA(Knickverfahren):
    """Nachweis am verformten System, je Knickfall in seiner Richtung."""

    def __init__(self, analyse: Querschnittsanalyse, faelle: Sequence[QAKnickfall], *,
                 verformung: Rechenwahl = VERFORMUNG,
                 widerstand: Rechenwahl = WIDERSTAND, schnell: bool = False) -> None:
        """``schnell`` wie bei der Platte: ohne die Suche nach N_Rd, dasselbe Urteil."""
        if not faelle:
            raise ValueError("Der Knicknachweis braucht mindestens einen Fall.")
        self.analyse = analyse
        self.faelle = list(faelle)
        self.verformung = verformung
        self.widerstand = widerstand
        self.schnell = schnell
        basis = f"{analyse.id}.nachweis.knicken"
        self.d_ausnutzung = {
            f.name: grad_def(f"{basis}.{f.kennung}.erfuellungsgrad",
                             rf"\alpha_{{eff,K,{als_text(f.name)}}}",
                             f"Erfüllungsgrad Knicken – {f.name}", "SIA 262:2025, 4.3.7")
            for f in self.faelle}
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()),
                         bezuege=analyse.grundbezuege(),
                         titel=f"Knicknachweis – {analyse.name}",
                         referenz="SIA 262:2025, 4.3.7", abschnitt=analyse.abschnitt)

    def _falltitel(self, fall: QAKnickfall) -> str:
        return f"Knicken – {fall.name}, {fall.richtung.beschriftung}"

    def pruefe(self, e: Eingaben, p: Protokoll):
        wert = e.si_nach_id()
        q_verformung, _, _ = self.analyse.querschnitt(wert, self.verformung)
        q_widerstand, _, _ = self.analyse.querschnitt(wert, self.widerstand)
        self._protokoll_ansatz(p, e)

        staebe: Dict[Zugseite, Knickstab] = {}
        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        for fall in self.faelle:
            if fall.richtung not in staebe:
                staebe[fall.richtung] = knickstab(q_verformung, q_widerstand, fall.richtung)
            erg = self._einen_fall(staebe[fall.richtung], fall)
            self._protokoll_fall(p, erg)
            ergebnis[self.d_ausnutzung[fall.name].id] = Groesse(erg.erfuellungsgrad,
                                                                EINHEITSLOS)
            urteile.append(self._urteil(erg))
        return Ausfuehrung(ergebnis, urteile)

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben) -> None:
        self._protokoll_verfahren(p)
        p.erklaerung(
            "Am gezeichneten Querschnitt gilt jeder Knickfall in einer Richtung: der "
            "Zugseite, zu der sich der Stab biegt. Die Nulllinie bleibt dabei parallel "
            "zur Achse; das Moment um die andere Achse, das ein unsymmetrischer "
            "Querschnitt weckt, zählt nicht. d reicht vom gedrückten Rand bis zum "
            "entferntesten Stab in Zugrichtung.")
        for titel, wahl, teil in (("Verformung (e_2d)", self.verformung, "verformung"),
                                  ("Widerstand (N_Rd)", self.widerstand, "widerstand")):
            p.titel(titel.split(" ")[0], ebene=3)
            basis = f"{self.id}.{teil}"
            protokoll_rechenwahl(p, wahl, basis, titel=f"Rechenwahl – {titel}")
            protokoll_gesetze_nach_wahl(p, e, self.analyse, wahl, basis,
                                        titel=f"Werkstoffgesetze – {titel.split(' ')[0]}")
        p.erklaerung(VERFORMUNG_NACH_WAHL)
        p.erklaerung(
            "Der Momentenwiderstand bei einer Druckkraft ist der Bruchzustand des "
            "Querschnitts in Biegerichtung, mit den Gesetzen des Widerstands – wie in "
            "der Tragsicherheit, mit der Nulllinie parallel zur Achse.")
        p.erklaerung(
            "Die Dehnung wächst linear in Zugrichtung, ε = ε_m + χ·v mit v ab dem "
            "Schwerpunkt. Zu jeder Druckkraft und jedem Moment finden zwei "
            "geschachtelte Suchen ε_m und χ, wie bei der Platte. Die "
            "Ausmitten-Iteration darüber steht vollständig da, Durchlauf für "
            "Durchlauf: sie ist das Verfahren selbst, und dass sie einläuft, ist die "
            "Aussage des Nachweises.")
