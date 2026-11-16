"""
opencivil/core/kurzform.py -- ein Nachweis in zwei, drei Formeln.

VERANTWORTUNG:
Das Auge in der Zusammenfassung zeigt einen Nachweis mit allem, was er
braucht: Baustoffe, Bewehrung, jeden Zwischenschritt. Fuer den Bericht in
Word will man meist nur die Formeln, die ihn fuehren --
``M_Rd = A_s f_yd (d - A_s f_yd / (2 b f_cd))`` und den Erfuellungsgrad. Die
Kurzform baut sie aus der Mitschrift: vom Ergebnis des Nachweises aus
rueckwaerts, je Platzhalter die Zeile, die seinen Wert rechnet.

Was eine Zeile dort ist, sagt die Berechnung, die sie schreibt
(:class:`~opencivil.core.protokoll.Kurz`)::

    EINSETZEN  ihre Formel geht in die ein, die ihren Wert braucht -- solange
               diese nicht breiter wird als KURZBREITE und kein Bruch dabei in
               Zaehler oder Nenner eines anderen geraet, wo er klein gesetzt
               wird; sonst steht sie als eigene Zeile davor
    ZEILE      steht als eigene Zeile davor

Jeder andere Wert bleibt ein Symbol mit seiner Zahl. Eine Zeile, die einen
Wert nur weitergibt (``M_Rd = M_Rd(N_Ed=0)``), wird uebersprungen; die Zeile
dahinter steht dann unter dem Symbol, unter dem der Wert gebraucht wird.

Jede eingesetzte Formel wird nachgerechnet (:func:`formelbaum.rechnen`):
gibt sie nicht das Ergebnis ihrer Zeile, bleibt es bei den einzelnen Zeilen.
Die Kurzform rechnet also nichts Neues -- sie schreibt dieselbe Rechnung
kuerzer auf.
"""

from __future__ import annotations

import math
from dataclasses import replace
from typing import Dict, Iterable, List, Optional, Set, Tuple

from opencivil.core.formelbaum import (
    Ausdruck, Blatt, Unlesbar, blaetter, einsetzen, empirische, lesen, numerisch,
    rechnen, symbolisch,
)
from opencivil.core.latex import bruchtiefe, einheitenhinweis, sichtbare_breite
from opencivil.core.protokoll import GleichungBlock, Kurz, Protokoll
from opencivil.core.wert import Wert

#: Wie breit eine Formel mit Symbolen hoechstens werden darf, wenn eine andere
#: in sie eingesetzt wird -- in Zeichen, wie :func:`sichtbare_breite` sie
#: zaehlt. Breiter liest sie sich nicht mehr auf einen Blick.
KURZBREITE = 40.0


def kurzform(protokoll: Protokoll, ziel: str) -> List[GleichungBlock]:
    """
    Die Kurzform des Nachweises, dessen Ergebnis der Wert ``ziel`` ist -- leer,
    wenn sie nur die Zeile waere, die ihn ohnehin abschliesst.
    """
    zeilen: Dict[str, GleichungBlock] = {}
    for block in protokoll.gleichungen():
        if block.wert_id and block.formelzeile is not None and block.formelzeile.vorlage:
            zeilen.setdefault(block.wert_id, block)
    wurzel = zeilen.get(ziel)
    if wurzel is None:
        return []
    heraus: List[GleichungBlock] = []
    _Bau(zeilen).anfuegen(wurzel, wurzel.formelzeile.symbol, heraus)
    return [] if len(heraus) == 1 and heraus[0] is wurzel else heraus


class _Bau:
    """Die Zeilen der Mitschrift, nach dem Wert, den sie rechnen."""

    def __init__(self, zeilen: Dict[str, GleichungBlock]) -> None:
        self.zeilen = zeilen
        self.unterwegs: Set[str] = set()

    def anfuegen(self, block: GleichungBlock, symbol: str,
                 heraus: List[GleichungBlock]) -> None:
        """Die Zeile von ``block`` unter ``symbol`` ans Ende -- nach dem, was sie braucht."""
        if _schon(heraus, block):
            return
        davor: List[GleichungBlock] = []
        try:
            baum, eingesetzt = self.ausgebaut(block, davor)
        except Unlesbar:
            heraus.append(_unter(block, symbol))
            return
        for vorher in davor:
            if not _schon(heraus, vorher):
                heraus.append(vorher)
        heraus.append(_gesetzt(block, baum, eingesetzt, symbol) if eingesetzt
                      else _unter(block, symbol))

    def ausgebaut(self, block: GleichungBlock, davor: List[GleichungBlock]
                  ) -> Tuple[Ausdruck, List[GleichungBlock]]:
        """
        Der Baum von ``block`` mit allem, was in ihn eingesetzt werden darf,
        und die Zeilen, die eingesetzt sind. Was als eigene Zeile vor ihm
        steht, kommt nach ``davor``. :class:`Unlesbar`, wenn er es selbst ist.
        """
        baum = lesen(block.formelzeile)
        eingesetzt: List[GleichungBlock] = []
        self.unterwegs.add(block.wert_id)
        try:
            for blatt in blaetter(baum):
                quelle, weitergegeben = self.quelle(blatt)
                if quelle is None or quelle.kurz is None or quelle.wert_id in self.unterwegs:
                    continue
                if quelle.kurz is Kurz.EINSETZEN and blatt.empirisch is None:
                    versuch = self.versuch(baum, blatt, quelle, block.formelzeile.resultat)
                    if versuch is not None:
                        baum, teile, vorher = versuch
                        eingesetzt += teile
                        davor += vorher
                        continue
                symbol = blatt.wert.symbol if weitergegeben else quelle.formelzeile.symbol
                self.anfuegen(quelle, symbol, davor)
        finally:
            self.unterwegs.discard(block.wert_id)
        return baum, eingesetzt

    def versuch(self, baum: Ausdruck, blatt: Blatt, quelle: GleichungBlock,
                resultat: Optional[Wert]
                ) -> Optional[Tuple[Ausdruck, List[GleichungBlock], List[GleichungBlock]]]:
        """
        ``baum`` mit der Formel von ``quelle`` fuer ``blatt`` -- samt den
        eingesetzten Zeilen und denen, die davor stehen muessen. None, wenn
        er zu breit wuerde, einen Bruch im Bruch bekaeme oder nicht mehr
        ``resultat`` ergaebe.
        """
        vorher: List[GleichungBlock] = []
        try:
            teil, eingesetzt = self.ausgebaut(quelle, vorher)
        except Unlesbar:
            return None
        neu = einsetzen(baum, blatt.kennung, teil)
        text = symbolisch(neu)
        if (sichtbare_breite(text) > KURZBREITE or bruchtiefe(text) > 1
                or not _stimmt(neu, resultat)):
            return None
        return neu, [quelle, *eingesetzt], vorher

    def quelle(self, blatt: Blatt) -> Tuple[Optional[GleichungBlock], bool]:
        """
        Die Zeile, die den Wert eines Blatts rechnet -- ueber Zeilen hinweg,
        die ihn nur weitergeben, solange die Zahl dieselbe bleibt; und ob es
        solche gab.
        """
        block = self.zeilen.get(blatt.kennung)
        weitergegeben = False
        while block is not None:
            try:
                baum = lesen(block.formelzeile)
            except Unlesbar:
                break
            naechste = self.zeilen.get(baum.kennung) if isinstance(baum, Blatt) else None
            if (naechste is None or naechste is block or baum.empirisch is not None
                    or not _stimmt(baum, block.formelzeile.resultat)):
                break
            block, weitergegeben = naechste, True
        return block, weitergegeben


def _schon(heraus: List[GleichungBlock], block: GleichungBlock) -> bool:
    return any(b.wert_id == block.wert_id for b in heraus)


def _stimmt(baum: Ausdruck, resultat: Optional[Wert]) -> bool:
    """Ergibt der Baum genau das Ergebnis der Zeile?"""
    return resultat is not None and math.isclose(
        rechnen(baum), resultat.groesse.si, rel_tol=1e-9, abs_tol=1e-12)


def _unter(block: GleichungBlock, symbol: str) -> GleichungBlock:
    """Der Block, wie er ist -- unter dem Symbol, unter dem sein Wert gebraucht wird."""
    if symbol == block.formelzeile.symbol:
        return block
    zeile = replace(block.formelzeile, symbol=symbol)
    return replace(block, latex=zeile.darstellen(), formelzeile=zeile)


def _gesetzt(block: GleichungBlock, baum: Ausdruck, eingesetzt: List[GleichungBlock],
             symbol: str) -> GleichungBlock:
    """
    Die Zeile von ``block`` mit den eingesetzten Formeln. Sie hat keine
    Vorlage mehr -- eine solche Formel steht nicht in der Formelsammlung --,
    dafuer die Normstellen aller Zeilen, die in ihr aufgingen.
    """
    zeile = replace(
        block.formelzeile, symbol=symbol, analytisch=symbolisch(baum),
        numerisch=numerisch(baum), einheiten=einheitenhinweis(empirische(baum)),
        vorlage=None, eingaben=(), empirisch=())
    return replace(block, latex=zeile.darstellen(), formelzeile=zeile,
                   referenz=normstellen(b.referenz for b in (block, *eingesetzt)))


def normstellen(referenzen: Iterable[str]) -> str:
    """
    Die Normstellen mehrerer Zeilen in einer, jede einmal und die Norm nicht
    wiederholt: ``SIA 262:2025, 4.3.3.2.1, (35); 4.3.3.2.3, (41)``. Die Norm
    ist, was vor dem ersten Komma steht.
    """
    teile: List[str] = []
    norm = ""
    for referenz in referenzen:
        for stelle in filter(None, (s.strip() for s in referenz.split(";"))):
            kopf, _, rest = stelle.partition(", ")
            if rest and kopf == norm:
                stelle = rest
            elif rest:
                norm = kopf
            if stelle not in teile:
                teile.append(stelle)
    return "; ".join(teile)
