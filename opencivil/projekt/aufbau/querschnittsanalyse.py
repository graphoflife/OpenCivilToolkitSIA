"""
opencivil/projekt/aufbau/querschnittsanalyse.py -- ein gezeichneter Querschnitt wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.querschnittsanalyse.QuerschnittsanalyseEintrag`
die :class:`~opencivil.querschnitt.analyse.Querschnittsanalyse` und ihre
Nachweise: Biegung und Normalkraft, Querkraft und Torsion, Duktilitaet,
sproedes Versagen, die Zwaengungen, die Stahlspannungen und das Knicken
(:func:`bauen`) -- dazu die Kennzahlen. Eine leere oder fehlerhafte
Zeichnung wird kein Bauteil, nur ein Hinweis.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Mapping

from opencivil.material.basis import Baustoff
from opencivil.material.spannstahl import erzeugnis
from opencivil.projekt.lesen import ProjektFehler, als_groesse, ort_von
from opencivil.projekt.querschnittsanalyse import QuerschnittsanalyseEintrag
from opencivil.nachweis.qa_gebrauch import AnalyseStellen, RissnormalkraftQA, ZwaengungBiegungQA
from opencivil.nachweis.qa_kennzahlen import KennzahlenQA
from opencivil.nachweis.qa_knicken import KnickenQA, QAKnickfall
from opencivil.nachweis.richtungsnachweise import DuktilitaetQA, SproedesVersagenQA
from opencivil.nachweis.schiefe_biegung import SchiefeBiegung
from opencivil.nachweis.schubwandnachweis import Schubwandnachweis, schub_belastet
from opencivil.querschnitt.analyse import Flaechenteil, Lastfall, Querschnittsanalyse
from opencivil.querschnitt.biegung import EINACHSIG, SCHIEF
from opencivil.querschnitt.geometrie import GeometrieFehler
from opencivil.querschnitt.spannglieder import Spannglied, aus_glied

from opencivil.projekt.aufbau.kern import (
    Aufbau, Bauteil, knickfall, material, spannungsfaelle, spannungsnachweise, stoffe_von,
)

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart


def bauen(art: "Bauteilart", eintrag: QuerschnittsanalyseEintrag,
          aufbau: Aufbau) -> Bauteil:
    """
    Ein gezeichneter Querschnitt: das Bauteil und seine Nachweise.

    Biegung und Normalkraft immer -- ihre Eckwerte gehoeren dem Querschnitt.
    Querkraft und Torsion, sobald ein Lastfall sie hat oder die
    Laengszugkraft zaehlt. Duktilitaet, sproedes Versagen und die Zwaengungen
    immer, still, wenn ausgeschaltet -- wie bei der Platte. Ebenso die
    Stahlspannungen, sobald es Lastfaelle gibt
    (:func:`~opencivil.projekt.aufbau.kern.spannungsnachweise`), und das
    Knicken, sobald ein Fall eingeschaltet ist.

    Ist noch nichts gezeichnet (:attr:`QuerschnittsanalyseEintrag.leer`), gibt
    es nichts zu rechnen und kein Bauteil -- aber auch keinen Fehler, der das
    ganze Projekt aufhielte: so beginnt jede neue Analyse (Benutzer,
    2026-10-19). Ebenso eine Zeichnung, die sich noch nicht rechnen laesst,
    etwa Bewehrung ohne Polygon darum: die Zeichnung sagt, was nicht
    stimmt, und der Rest rechnet weiter (:meth:`Aufbau.unfertig`).
    """
    if eintrag.leer:
        raise ProjektFehler("noch nichts gezeichnet.", wo=ort_von(eintrag))
    try:
        analyse = _analyse(eintrag, aufbau.baustoffe, praefix=f"{art.raum}.{eintrag.kennung}")
    except GeometrieFehler as fehler:
        raise ProjektFehler(str(fehler), wo=ort_von(eintrag)) from None
    analyse.ins_rechenwerk(aufbau.werk)
    teil = Bauteil(eintrag, art, analyse)
    stoffe = stoffe_von(aufbau, analyse.baustoffe)

    # Die Lastfaelle in SI, aus der Einheit ihrer Felder: N, M_y ... aus
    # N_Ed, M_y_Ed ...
    lastfaelle = [Lastfall(name=l.name, **_in_si(l, "N", "M_y", "M_z", "V_y", "V_z", "T"))
                  for l in eintrag.lastfaelle if l.aktiv]

    schub = None
    if any(schub_belastet(analyse.biegung, l) for l in lastfaelle) \
            or (eintrag.laengszugkraft and lastfaelle):
        schub = Schubwandnachweis(analyse, lastfaelle, mit_laengszug=eintrag.laengszugkraft)
        aufbau.eintragen(teil, "qa_schub", eintrag.kennung, schub)
    aufbau.eintragen(teil, "qa_biegung", eintrag.kennung, SchiefeBiegung(
        analyse, lastfaelle, laengszug=schub if eintrag.laengszugkraft else None))

    duktilitaet = DuktilitaetQA(analyse, beiwert=eintrag.x_d_max)
    duktilitaet.still = not eintrag.duktilitaet
    aufbau.eintragen(teil, "qa_duktilitaet", eintrag.kennung, duktilitaet)
    sproede = SproedesVersagenQA(analyse)
    sproede.still = not eintrag.sproede
    aufbau.eintragen(teil, "qa_sproede", eintrag.kennung, sproede)

    zwang = RissnormalkraftQA(analyse, anforderung=eintrag.rissanforderung,
                              begrenzt=eintrag.zwaengung_begrenzt)
    zwang.still = not eintrag.zwaengung
    aufbau.eintragen(teil, "qa_rissnormalkraft", eintrag.kennung, zwang)
    biegung = ZwaengungBiegungQA(analyse, anforderung=eintrag.rissanforderung,
                                 kriechzahl=eintrag.zwaengung_biegung_kriechzahl)
    biegung.still = not eintrag.zwaengung_biegung
    aufbau.eintragen(teil, "qa_zwaengung_biegung", eintrag.kennung, biegung)
    spannungsnachweise(
        eintrag, AnalyseStellen(analyse), eintrag.lastfaelle,
        lambda name, l, faktor: Lastfall(name=name, **{
            k: faktor * v for k, v in _in_si(l, "N", "M_y", "M_z").items()}),
        praefix="qa_", kennung=eintrag.kennung, aufbau=aufbau, teil=teil)

    knickfaelle = [k for k in eintrag.knickfaelle if k.aktiv]
    if knickfaelle:
        aufbau.eintragen(teil, "qa_knicken", eintrag.kennung, KnickenQA(
            analyse, [knickfall(k, QAKnickfall, richtung=k.richtung)
                      for k in knickfaelle],
            verformung=eintrag.knicken_wahl_verformung.wahl(stoffe),
            widerstand=eintrag.knicken_wahl_widerstand.wahl(stoffe), schnell=aufbau.schnell))

    # Was der Querschnitt aufnimmt, ohne Einwirkung -- immer, wie bei der
    # Platte (Benutzer, 2026-10-23). Am Ende, nach seinen Nachweisen.
    kennzahlen = KennzahlenQA(analyse)
    aufbau.werk.registriere(kennzahlen)
    teil.weitere_ziele.append(kennzahlen.id)
    teil.kennzahlen += kennzahlen.kennzahlen

    spannungsfaelle(eintrag, stoffe, aufbau)
    return teil


def _in_si(fall: Any, *groessen: str) -> Dict[str, float]:
    """
    Je Groesse ``N``, ``M_y`` ... die Zahl ihres Feldes ``N_Ed``, ``M_y_Ed``
    ... in SI, aus der Einheit des Feldes.
    """
    return {g: als_groesse(fall, f"{g}_Ed").si for g in groessen}


def _analyse(eintrag: QuerschnittsanalyseEintrag, baustoffe: Mapping[str, Baustoff],
             *, praefix: str) -> Querschnittsanalyse:
    """
    Aus der Beschreibung das Bauteil. Laesst sich die Zeichnung nicht
    rechnen, ein :class:`GeometrieFehler` mit dem ersten Grund.
    """
    wo = ort_von(eintrag)

    def stoff(kennung: str, was: str, art: str) -> Baustoff:
        return material(baustoffe, kennung, art, wo, was)

    elemente = eintrag.elemente()
    if elemente.fehler:
        # Ein Element ohne Lage laesst sich nicht rechnen -- und es still
        # wegzulassen hiesse, mit einem anderen Querschnitt zu rechnen.
        raise GeometrieFehler(elemente.fehler[0]["text"])
    flaechen = [Flaechenteil(name=f["name"], kennung=f["kennung"], punkte=f["punkte"],
                             stoff=stoff(f["material"], f["name"], "beton")
                             if f["material"] else None)
                for f in elemente.polygone]
    staebe = [{**s, "stahl": stoff(s["stahl"], s["name"], "betonstahl")}
              for s in elemente.staebe]
    linien = [{**l, "stahl": stoff(l["stahl"], l["name"], "betonstahl")}
              for l in elemente.linien]
    waende = [{**w, "stahl": stoff(w["stahl"], w["name"], "betonstahl")
               if w["durchmesser"] > 0 else None}
              for w in elemente.waende]
    glieder = [_glied(g, stoff(g["stahl"], g["name"], "spannstahl"), wo)
               for g in elemente.spannglieder]
    # Jeder Baustoff bekommt seine Wahl, auch wer keine eigene hat: so steht
    # die Vorgabe nur an der Beschreibung.
    wahl = eintrag.wahl({k: baustoffe[k] for k in eintrag.materialien() if k in baustoffe})
    return Querschnittsanalyse(
        name=eintrag.name, praefix=praefix,
        flaechen=flaechen, staebe=staebe, linien=linien, waende=waende,
        alpha_min=eintrag.alpha_min, alpha_max=eintrag.alpha_max, k_c=eintrag.k_c,
        wahl=wahl, biegung=EINACHSIG if eintrag.einachsig else SCHIEF, spannglieder=glieder)


def _glied(g: Mapping, stahl: Baustoff, wo: str) -> Spannglied:
    """
    Ein Spannglied mit seinem Spannstahl -- und dem Erzeugnis, das sein
    Durchmesser in der Sorte waehlt. Nennt Tabelle 7 keines, fehlt die Wahl
    noch (:func:`erzeugnis_grund`).
    """
    gefunden = erzeugnis(stahl.sorte, g["durchmesser"])
    if gefunden is None:
        raise ProjektFehler(f"{g['name']}: {erzeugnis_grund(stahl.name, stahl.sorte, g['durchmesser'])}.",
                            wo=wo)
    return aus_glied({**g, "stahl": stahl}, gefunden)


def erzeugnis_grund(name: str, sorte: str, durchmesser: float) -> str:
    """
    Warum ein Spannglied noch kein Erzeugnis hat -- die eine Stelle fuer den
    Aufbau und das Zeichenfenster (:mod:`opencivil.web.zeichengeometrie`). Es
    fehlt nur eine Wahl, etwa nach dem Wechsel zu einer Sorte, die es nur in
    Staeben gibt.
    """
    nennt = f" (Sorte {sorte})" if sorte and sorte != name else ""
    return (f"{name}{nennt} gibt es nicht mit ⌀{durchmesser:g} mm (Tabelle 7) – "
            f"einen Durchmesser wählen")
