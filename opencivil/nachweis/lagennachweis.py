"""
opencivil/nachweis/lagennachweis.py -- ein Nachweis je Platte, ein Urteil je Bewehrungslage.

VERANTWORTUNG:
Die Schablone (:class:`Lagennachweis`) der Nachweise, die jede Lage einer
Platte fuer sich ansehen -- Duktilitaet, sproedes Versagen, Zwaengung auf
Biegung und auf Normalkraft. Hier steht einmal, was sie teilen: welche
Lagen und ihre Posten, je Lage ein Erfuellungsgrad mit derselben Kennung,
demselben Zeichen und derselben Benennung, die Bezuege auf Posten und
Staehle, die Schleife ueber die Lagen mit Befund und Urteil und die
Begruendung einer Lage ohne Stahl. Was je Nachweis anders ist, geben seine
Methoden: was alle Lagen brauchen (:meth:`Lagennachweis.ansatz`), die eine
Lage (:meth:`~Lagennachweis.eine_lage`) und ihre Herleitung
(:meth:`~Lagennachweis.protokoll_lage`).

LAGEN OHNE STAHL:
Sproedes Versagen, Zwaengung auf Biegung und Duktilitaet lassen eine Lage
ohne Stahl weg (Benutzer, 2026-10-19) -- der Aufbau gibt sie ihnen nicht.
Bekommen sie trotzdem eine, ist das ein Fehler des Aufbaus und meldet sich
(``NUR_MIT_STAHL``). Nur die Zwaengung auf Normalkraft prueft jede Lage,
auch die leere: gerade sie faellt durch und soll es sichtbar tun.

Bis 2026-11-10 stand das viermal da, je mit eigener Lagenwahl,
Stahl-Entdoppelung, Gradkennung und Sammelschleife; der allgemeine Nachweis
trug ``ohne_bewehrung`` mit, und in drei der vier lief dieser Zweig nie.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Dict, List, Mapping, Optional, Sequence

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben
from opencivil.core.einheiten import Groesse
from opencivil.core.nachweis import Fallbefund, Nachweis, NachweisUrteil, grad_def
from opencivil.core.protokoll import Protokoll
from opencivil.core.wert import WertDef
from opencivil.querschnitt.platte import Bewehrungslage, Richtung


class Lagennachweis(Nachweis):
    """Ein Nachweis je Platte, ein Urteil je Lage -- siehe Dateikopf."""

    KUERZEL: str = ""
    """Im Zeichen des Grads: α_eff,D,2 -- «D»."""

    BENENNUNG: str = ""
    """Im Text des Grads: «Erfüllungsgrad Duktilität – 2. Lage» -- «Duktilität»."""

    REFERENZ: str = ""

    NUR_MIT_STAHL: bool = True
    """Ob er nur Lagen mit Stahl bekommt -- siehe Dateikopf."""

    def __init__(self, querschnitt, lagen: Sequence[Bewehrungslage], *, basis: str,
                 titel: str, bezuege: Sequence[Eingabebezug],
                 richtung: Optional[Richtung] = None, posten: Sequence[str] = (),
                 stahl: Sequence[str] = (), weitere_ausgaben: Sequence[WertDef] = ()) -> None:
        """
        ``bezuege`` sind die des Nachweises selbst; dazu kommen je Posten
        einer Lage seine Werte ``posten`` (``a_s``, ``z`` ...) und je Stahl
        seine Kennwerte ``stahl``. ``richtung`` steht im Zeichen und im Namen
        der Grade, wo der Nachweis eine hat.
        """
        leer = [l.nummer for l in lagen if not l.vorhanden]
        if self.NUR_MIT_STAHL and leer:
            raise ValueError(
                f"Querschnitt '{querschnitt.name}': {self.THEMA} bekommt nur Lagen mit Stahl, "
                f"die {', '.join(f'{n}.' for n in leer)} Lage hat keinen.")
        self.querschnitt = querschnitt
        self.richtung = richtung
        self.lagen = list(lagen)
        self.posten_je_lage = {l.nummer: querschnitt.posten_der_lage(l) for l in self.lagen}
        r = richtung.value if richtung is not None else ""
        self.d_ausnutzung: Dict[int, WertDef] = {
            l.nummer: grad_def(
                f"{basis}.lage{l.nummer}.erfuellungsgrad",
                rf"\alpha_{{eff,{self.KUERZEL},{l.nummer}{',' + r if r else ''}}}",
                f"Erfüllungsgrad {self.BENENNUNG} – {l.nummer}. Lage{' ' + r if r else ''}",
                self.REFERENZ)
            for l in self.lagen}
        alle = list(bezuege)
        if posten:
            for liste in self.posten_je_lage.values():
                for q in liste:
                    alle += q.bezuege(*posten)
        for s in {l.stahl.id: l.stahl for l in self.lagen if l.stahl}.values():
            alle += [s.bezug(k) for k in stahl]
        super().__init__(basis, ausgaben=[*self.d_ausnutzung.values(), *weitere_ausgaben],
                         bezuege=alle, titel=titel, referenz=self.REFERENZ,
                         abschnitt=querschnitt.abschnitt)

    @staticmethod
    def lagen_waehlen(querschnitt, richtung: Richtung, nummern: Sequence[int]) -> List[Bewehrungslage]:
        """Die gewaehlten Lagen einer Richtung -- keine ist ein Fehler des Aufbaus."""
        gewaehlt = set(nummern)
        lagen = [l for l in querschnitt.lagen if l.richtung is richtung and l.nummer in gewaehlt]
        if not lagen:
            raise ValueError(f"Querschnitt '{querschnitt.name}': in {richtung.beschriftung} "
                             f"ist keine der gewählten Lagen vorhanden.")
        return lagen

    @staticmethod
    def ohne_bewehrung(nummer: int) -> str:
        """Die Begruendung einer Lage ohne Stahl."""
        return f"{nummer}. Lage ohne Bewehrung → kein Nachweis."

    # -- Rechnen ------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        ansatz = self.ansatz(e, p)
        ausgaben: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        befund = Fallbefund()
        for lage in self.lagen:
            erg = self.eine_lage(e, lage, ansatz)
            befund.ergebnisse.append(erg)
            self.protokoll_lage(p, e, erg, ansatz)
            ausgaben.update(self.ausgaben_der_lage(erg))
            urteile.append(self.urteil(self.d_ausnutzung[lage.nummer], f"{lage.nummer}. Lage",
                                       erg.ausgang, erg.begruendung))
        self.protokoll_massgebend(p, urteile)
        return Ausfuehrung(ausgaben, self.teilurteile(urteile), befund)

    @abstractmethod
    def ansatz(self, e: Eingaben, p: Protokoll) -> Any:
        """Was alle Lagen brauchen, mit seiner Herleitung -- es geht an jede Lage weiter."""

    @abstractmethod
    def eine_lage(self, e: Eingaben, lage: Bewehrungslage, ansatz: Any) -> Any:
        """Das Ergebnis einer Lage, mit ``ausgang`` und ``begruendung``."""

    @abstractmethod
    def protokoll_lage(self, p: Protokoll, e: Eingaben, erg: Any, ansatz: Any) -> None:
        """Die Herleitung einer Lage."""

    def ausgaben_der_lage(self, erg: Any) -> Mapping[str, Groesse]:
        """Was eine Lage ausser ihrem Grad ausgibt -- meist nichts."""
        return {}
