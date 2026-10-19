"""
opencivil/projekt/aufbau/querschnittsanalyse.py -- ein gezeichneter Querschnitt wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.querschnittsanalyse.QuerschnittsanalyseEintrag`
die :class:`~opencivil.querschnitt.analyse.Querschnittsanalyse` -- jeder Fehler
der Zeichnung als Satz, der sie nennt -- und ihre Nachweise: Biegung und
Normalkraft, Querkraft und Torsion, Duktilitaet, sproedes Versagen, die
Zwaengungen, die Stahlspannungen und das Knicken (:func:`bauen`).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, Optional

from opencivil.material.basis import Baustoff
from opencivil.projekt.lesen import ProjektFehler
from opencivil.projekt.querschnittsanalyse import QuerschnittsanalyseEintrag
from opencivil.nachweis.qa_gebrauch import AnalyseStellen, RissnormalkraftQA, ZwaengungBiegungQA
from opencivil.nachweis.qa_knicken import KnickenQA, QAKnickfall
from opencivil.nachweis.richtungsnachweise import DuktilitaetQA, SproedesVersagenQA
from opencivil.nachweis.schiefe_biegung import SchiefeBiegung
from opencivil.nachweis.schubwandnachweis import Schubwandnachweis
from opencivil.querschnitt.analyse import Flaechenteil, Lastfall, Querschnittsanalyse
from opencivil.querschnitt.geometrie import GeometrieFehler

from opencivil.projekt.aufbau.kern import Aufbau, Bauteil, knickfall, material, spannungsnachweise

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart


def bauen(art: "Bauteilart", eintrag: QuerschnittsanalyseEintrag,
          aufbau: Aufbau) -> Optional[Bauteil]:
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
    2026-10-19).
    """
    if eintrag.leer:
        aufbau.leere_analysen[eintrag.kennung] = eintrag.name
        aufbau.warnungen.append(
            f"Querschnittsanalyse '{eintrag.name}': noch nichts gezeichnet → nichts zu rechnen.")
        return None
    analyse = _analyse(eintrag, aufbau.baustoffe, praefix=f"{art.raum}.{eintrag.kennung}")
    aufbau.querschnittsanalysen[eintrag.kennung] = analyse
    analyse.ins_rechenwerk(aufbau.werk)
    teil = Bauteil(eintrag.kennung, eintrag.name, art, analyse)

    kN, kNm = 1e3, 1e3
    lastfaelle = [
        Lastfall(name=l.name, N=l.N_Ed * kN, M_y=l.M_y_Ed * kNm, M_z=l.M_z_Ed * kNm,
                 V_y=l.V_y_Ed * kN, V_z=l.V_z_Ed * kN, T=l.T_Ed * kNm)
        for l in eintrag.lastfaelle if l.aktiv]

    schub = None
    if any(l.V_z or l.T or (l.V_y and not analyse.einachsig) for l in lastfaelle) \
            or (eintrag.laengszugkraft and lastfaelle):
        schub = Schubwandnachweis(analyse, lastfaelle, mit_laengszug=eintrag.laengszugkraft)
        aufbau.eintragen(teil, "qa_schub", eintrag.kennung, schub)
    aufbau.eintragen(teil, "qa_biegung", eintrag.kennung, SchiefeBiegung(
        analyse, lastfaelle, laengszug=schub if eintrag.laengszugkraft else None))

    duktilitaet = DuktilitaetQA(analyse, grenze=eintrag.x_d_max)
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
    kN = 1e3
    spannungsnachweise(
        eintrag, AnalyseStellen(analyse), eintrag.lastfaelle,
        lambda name, l, faktor: Lastfall(name=name, N=faktor * l.N_Ed * kN,
                                         M_y=faktor * l.M_y_Ed * kN, M_z=faktor * l.M_z_Ed * kN),
        praefix="qa_", kennung=eintrag.kennung, aufbau=aufbau, teil=teil)

    knickfaelle = [k for k in eintrag.knickfaelle if k.aktiv]
    if knickfaelle:
        aufbau.eintragen(teil, "qa_knicken", eintrag.kennung, KnickenQA(
            analyse, [knickfall(k, QAKnickfall, richtung=k.richtung)
                      for k in knickfaelle],
            verformung=eintrag.knicken_wahl_verformung.wahl,
            widerstand=eintrag.knicken_wahl_widerstand.wahl, schnell=aufbau.schnell))

    aktive = [s for s in eintrag.spannungsfaelle if s.aktiv]
    if aktive:
        aufbau.spannungsfaelle[eintrag.kennung] = aktive
    return teil


def _analyse(eintrag: QuerschnittsanalyseEintrag, baustoffe: Mapping[str, Baustoff],
             *, praefix: str) -> Querschnittsanalyse:
    """
    Aus der Beschreibung das Bauteil -- und aus jedem Fehler der Zeichnung
    einen Satz, der die Analyse nennt.
    """
    wo = f"Querschnittsanalyse '{eintrag.name}'"

    def stoff(kennung: str, was: str, art: str) -> Baustoff:
        return material(baustoffe, kennung, art, f"{wo}: {was}")

    elemente = eintrag.elemente()
    if elemente.fehler:
        # Ein Element ohne Lage laesst sich nicht rechnen -- und es still
        # wegzulassen hiesse, mit einem anderen Querschnitt zu rechnen.
        raise ProjektFehler(f"{wo}: {elemente.fehler[0]['text']}")
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
    # Jeder Baustoff bekommt seine Wahl, auch wer keine eigene hat: so steht
    # die Vorgabe nur an der Beschreibung.
    wahl = {b.id: eintrag.wahl(kennung).rechenwahl for kennung, b in baustoffe.items()}
    try:
        return Querschnittsanalyse(
            name=eintrag.name, praefix=praefix,
            flaechen=flaechen, staebe=staebe, linien=linien, waende=waende,
            alpha_min=eintrag.alpha_min, alpha_max=eintrag.alpha_max, k_c=eintrag.k_c,
            wahl=wahl, einachsig=eintrag.einachsig)
    except GeometrieFehler as fehler:
        raise ProjektFehler(f"{wo}: {fehler}") from None
