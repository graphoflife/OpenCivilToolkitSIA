"""
opencivil/projekt/aufbau/querschnittsanalyse.py -- ein gezeichneter Querschnitt wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.querschnittsanalyse.QuerschnittsanalyseEintrag`
die :class:`~opencivil.querschnitt.analyse.Querschnittsanalyse` und ihre
Nachweise: Biegung und Normalkraft, Querkraft und Torsion, Duktilitaet,
sproedes Versagen, die Zwaengungen, die Stahlspannungen und das Knicken
(:func:`bauen`) -- dazu die Kennzahlen. Ein Querschnitt aus Stahl hat seine
eigenen (:func:`_stahl`), einer im Verbund (:func:`_verbund`), eine
Blechverbunddecke (:func:`_blechverbund`) und einer aus Holz auch
(:func:`_holz`). Jede Bauweise rechnet den Schubfluss in den Schnitten
(:func:`_schubfluss`). Eine leere oder fehlerhafte Zeichnung wird kein
Bauteil, nur ein Hinweis.

ZWEI GAENGE:
:func:`bauen` macht die Analyse und meldet ihre Werte an -- ein Balkensystem
nimmt sie als Querschnitt. Ihre Nachweise baut :func:`danach`, wenn alle
Bauteile gebaut sind: ihre Lastfaelle koennen Stellen eines Balkensystems
sein (:mod:`~opencivil.projekt.aufbau.aus_system`).
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, List, Mapping, Tuple

from opencivil.material.basis import Baustoff, Baustoffart
from opencivil.projekt.lesen import ProjektFehler, als_groesse, ort_von, stoffe_des_felds
from opencivil.projekt.querschnittsanalyse import (
    QuerschnittsanalyseEintrag, SchubwandEintrag, StabEintrag, StablinieEintrag,
)
from opencivil.projekt.blechdecken import BlechdeckeEintrag
from opencivil.projekt.spannglieder import SpanngliedEintrag
from opencivil.nachweis.qa_blechverbund import (
    EINE_RICHTUNG, BlechBiegungQA, BlechSchubQA, KennzahlenBlechQA,
)
from opencivil.nachweis.qa_gebrauch import AnalyseStellen, RissnormalkraftQA, ZwaengungBiegungQA
from opencivil.nachweis.qa_holz import HolzBiegungQA, HolzSchubQA
from opencivil.nachweis.qa_holz_kennzahlen import KennzahlenHolzQA
from opencivil.nachweis.qa_holz_stabilitaet import HolzStabilitaetQA
from opencivil.nachweis.qa_holz_werte import HolzwerteQA
from opencivil.nachweis.qa_kennzahlen import KennzahlenQA
from opencivil.nachweis.qa_stahl import OHNE_TORSION, StahlBiegungQA, StahlQuerkraftQA
from opencivil.nachweis.qa_stahl_kennzahlen import KennzahlenStahlQA
from opencivil.nachweis.qa_stahl_stabilitaet import StahlStabilitaetQA
from opencivil.nachweis.qa_verbund import OHNE_TORSION as OHNE_TORSION_VERBUND
from opencivil.nachweis.qa_verbund import VerbundBiegungQA, VerbundQuerkraftQA
from opencivil.nachweis.qa_verbund_kennzahlen import KennzahlenVerbundQA
from opencivil.nachweis.qa_verbund_stuetze import VerbundStuetzeQA
from opencivil.nachweis.qa_knicken import KnickenQA, QAKnickfall
from opencivil.nachweis.qa_schubfluss import Schubflussfall, SchubflussQA
from opencivil.nachweis.richtungsnachweise import DuktilitaetQA, SproedesVersagenQA
from opencivil.nachweis.schiefe_biegung import SchiefeBiegung
from opencivil.nachweis.schubwandnachweis import Schubwandnachweis, schub_belastet
from opencivil.querschnitt.abtrennen import aus_schnitt
from opencivil.querschnitt.analyse import Flaechenteil, Lastfall, Querschnittsanalyse
from opencivil.querschnitt.bauweise import Bauweise
from opencivil.querschnitt.biegung import EINACHSIG, SCHIEF
from opencivil.querschnitt.geometrie import GeometrieFehler
from opencivil.querschnitt.profilblech import aus_form
from opencivil.querschnitt.spannglieder import Spannglied, aus_glied, was_fehlt
from opencivil.verbund import duebel as vd

from opencivil.projekt.aufbau.aus_system import aus_dem_system
from opencivil.projekt.aufbau.kern import (
    Aufbau, Bauteil, knickfall, material, spannungsfaelle, spannungsnachweise, stoffe_von,
)

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart


def bauen(art: "Bauteilart", eintrag: QuerschnittsanalyseEintrag,
          aufbau: Aufbau) -> Bauteil:
    """
    Ein gezeichneter Querschnitt: das Bauteil mit seinen Werten, angemeldet
    im Werk. Nachweise, Kennzahlen und Schubfluss baut :func:`danach`.

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
    if analyse.bauweise is not Bauweise.STAHLBETON:
        # Die Werte des Querschnitts rechnet jede Bauweise -- der Bericht
        # zeigt sie, ein Stab im Balkensystem nimmt sie.
        teil.weitere_ziele += [d.id for d in (*analyse.d_brutto.values(), analyse.d_torsion)]
    return teil


def danach(art: "Bauteilart", eintrag: QuerschnittsanalyseEintrag, teil: Bauteil,
           aufbau: Aufbau) -> None:
    """
    Wenn alle Bauteile gebaut sind: die Nachweise und Kennzahlen nach der
    Bauweise (:func:`_nachweise`) und der Schubfluss in den Schnitten
    (:func:`_schubfluss`). Nimmt die Analyse Stellen eines Balkensystems
    (:func:`~opencivil.projekt.aufbau.aus_system.aus_dem_system`), sind sie
    Lastfaelle nach ihren eigenen -- fuer jeden Nachweis, wie von Hand
    eingegeben --, und ihre Herleitung steht vor den Nachweisen.
    """
    analyse = teil.objekt
    aus = aus_dem_system(eintrag, aufbau)
    if aus is not None:
        teil.aus_system = aus
        herleitung = aus.herleitung(f"{analyse.id}.aus_system", abschnitt=analyse.abschnitt,
                                    schwerpunkt=(analyse.id_von("y_S"), analyse.id_von("z_S")))
        aufbau.werk.registriere(herleitung)
        teil.vorab.append(herleitung.id)
        for satz in aus.hinweise:
            aufbau.warnen(teil.raum, f"{ort_von(eintrag)}: {satz}")
        eintrag = replace(eintrag, lastfaelle=[*eintrag.lastfaelle, *aus.lastfaelle])
    _nachweise(eintrag, analyse, teil, aufbau)
    _schubfluss(eintrag, analyse, teil, aufbau)


def _nachweise(eintrag: QuerschnittsanalyseEintrag, analyse: Querschnittsanalyse,
               teil: Bauteil, aufbau: Aufbau) -> None:
    """
    Die Nachweise und Kennzahlen nach der Bauweise: beim Stahlbeton nach
    SIA 262 (:func:`_stahlbeton`), aus Stahl nach SIA 263 (:func:`_stahl`),
    im Verbund nach SIA 264 (:func:`_verbund`), eine Blechverbunddecke auch
    (:func:`_blechverbund`), aus Holz nach SIA 265 (:func:`_holz`). Einer
    aus mehreren Hoelzern rechnet bisher nur seine Werte -- Flaeche,
    Schwerpunkt, Traegheitsmomente --; seine Zusammenfassung sagt, dass die
    Nachweise fehlen (:func:`ohne_nachweise`). Seine
    Spannung-Dehnung-Analysen rechnet er trotzdem. Der Verbund und die
    Blechverbunddecke haben noch keine (:func:`ohne_analysen`).
    """
    fehlt = ohne_nachweise(analyse.bauweise, ((s.art, s.name) for s in analyse.baustoffe))
    if fehlt:
        aufbau.ohne_nachweis(teil, ort_von(eintrag), fehlt)
        if not ohne_analysen(analyse.bauweise):
            spannungsfaelle(eintrag, stoffe_von(aufbau, analyse.baustoffe), aufbau)
        return
    _NACH_BAUWEISE[analyse.bauweise](eintrag, analyse, teil, aufbau)


def _stahlbeton(eintrag: QuerschnittsanalyseEintrag, analyse: Querschnittsanalyse,
                teil: Bauteil, aufbau: Aufbau) -> None:
    """
    Ein Querschnitt aus Stahlbeton nach SIA 262. Biegung und Normalkraft
    immer -- ihre Eckwerte gehoeren dem Querschnitt. Querkraft und Torsion,
    sobald ein Lastfall sie hat oder die Laengszugkraft zaehlt. Duktilitaet,
    sproedes Versagen und die Zwaengungen immer, still, wenn ausgeschaltet
    -- wie bei der Platte. Ebenso die Stahlspannungen, sobald es Lastfaelle
    gibt (:func:`~opencivil.projekt.aufbau.kern.spannungsnachweise`), und
    das Knicken, sobald ein Fall eingeschaltet ist.
    """
    stoffe = stoffe_von(aufbau, analyse.baustoffe)
    lastfaelle = _lastfaelle(eintrag)

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
    aufbau.kennzahlen_eintragen(teil, KennzahlenQA(analyse))
    spannungsfaelle(eintrag, stoffe, aufbau)


def _lastfaelle(eintrag: QuerschnittsanalyseEintrag) -> List[Lastfall]:
    """Die eingeschalteten Lastfaelle in SI, aus der Einheit ihrer Felder: N, M_y ... aus N_Ed, M_y_Ed ..."""
    return [Lastfall(name=l.name, **_in_si(l, "N", "M_y", "M_z", "V_y", "V_z", "T"))
            for l in eintrag.lastfaelle if l.aktiv]


def _stahl(eintrag: QuerschnittsanalyseEintrag, analyse: Querschnittsanalyse, teil: Bauteil,
           aufbau: Aufbau) -> None:
    """
    Ein Querschnitt aus Stahl nach SIA 263 (:mod:`~opencivil.nachweis.qa_stahl`):
    je Lastfall Biegung und Normalkraft, Querkraft, sobald einer sie hat --
    beide lesen den Widerstand gegen Querkraft aus den Kennzahlen. Torsion
    weist er nicht nach; ein Lastfall mit ``T_Ed`` sagt es. Knicken und
    Kippen, sobald ein Fall eingeschaltet ist
    (:mod:`~opencivil.nachweis.qa_stahl_stabilitaet`). Die Kennzahlen
    stehen in der Herleitung vor den Nachweisen, die aus ihnen lesen.
    """
    kennzahlen = KennzahlenStahlQA(analyse)
    lastfaelle = _lastfaelle(eintrag)
    if lastfaelle:
        aufbau.eintragen(teil, "qa_stahl", eintrag.kennung,
                         StahlBiegungQA(analyse, lastfaelle, kennzahlen))
    if any(l.V_z or analyse.biegung.querkraft_y(l.V_y) for l in lastfaelle):
        aufbau.eintragen(teil, "qa_stahl_schub", eintrag.kennung,
                         StahlQuerkraftQA(analyse, lastfaelle, kennzahlen))
    mit_torsion = [l.name for l in lastfaelle if l.T]
    if mit_torsion:
        aufbau.warnen(teil.raum, f"{ort_von(eintrag)}, {', '.join(mit_torsion)}: {OHNE_TORSION}")
    stabfaelle = eintrag.stabfaelle()
    if stabfaelle:
        aufbau.eintragen(teil, "qa_stahl_stabilitaet", eintrag.kennung,
                         StahlStabilitaetQA(analyse, stabfaelle, eintrag.knickkurven))
    aufbau.kennzahlen_eintragen(teil, kennzahlen)
    spannungsfaelle(eintrag, stoffe_von(aufbau, analyse.baustoffe), aufbau)


def _verbund(eintrag: QuerschnittsanalyseEintrag, analyse: Querschnittsanalyse, teil: Bauteil,
             aufbau: Aufbau) -> None:
    """
    Ein Querschnitt aus Baustahl und Beton nach SIA 264
    (:mod:`~opencivil.nachweis.qa_verbund`): je Lastfall Biegung und
    Normalkraft, plastisch, und Querkraft, sobald einer sie hat -- die traegt
    der Stahl allein. Beide lesen den Widerstand gegen Querkraft aus den
    Kennzahlen. Mit Kopfbolzenduebeln steht ihr ``P_Rd`` in den Kennzahlen,
    und je Lastfall die Verduebelung bei Biegung und Normalkraft, mit seiner
    Zahl der Duebel. Torsion weist er nicht nach; ein Lastfall mit ``T_Ed``
    sagt es. Sobald ein Stabilitaetsfall eingeschaltet ist, die
    Verbundstuetze (:mod:`~opencivil.nachweis.qa_verbund_stuetze`); das
    Kippen des Verbundtraegers fehlt noch, ebenso die
    Spannung-Dehnung-Analysen (:func:`ohne_analysen`).
    """
    duebel = None
    abschnitte: Dict[str, vd.Abschnitt] = {}
    if eintrag.verduebelung is vd.Verduebelung.KOPFBOLZEN:
        duebel = vd.Kopfbolzen(eintrag.duebel_d, eintrag.duebel_h, eintrag.duebel_f_u)
        abschnitte = {l.name: vd.Abschnitt(l.duebelzahl, l.L_e)
                      for l in eintrag.lastfaelle if l.aktiv}
    kennzahlen = KennzahlenVerbundQA(analyse, duebel)
    lastfaelle = _lastfaelle(eintrag)
    if lastfaelle:
        aufbau.eintragen(teil, "qa_verbund", eintrag.kennung,
                         VerbundBiegungQA(analyse, lastfaelle, kennzahlen, abschnitte))
    if any(l.V_z or analyse.biegung.querkraft_y(l.V_y) for l in lastfaelle):
        aufbau.eintragen(teil, "qa_verbund_schub", eintrag.kennung,
                         VerbundQuerkraftQA(analyse, lastfaelle, kennzahlen))
    mit_torsion = [l.name for l in lastfaelle if l.T]
    if mit_torsion:
        aufbau.warnen(teil.raum,
                      f"{ort_von(eintrag)}, {', '.join(mit_torsion)}: {OHNE_TORSION_VERBUND}")
    stabfaelle = eintrag.stabfaelle()
    if stabfaelle:
        aufbau.eintragen(teil, "qa_verbund_stuetze", eintrag.kennung,
                         VerbundStuetzeQA(analyse, stabfaelle, eintrag.stuetze_kriechzahl))
    aufbau.kennzahlen_eintragen(teil, kennzahlen)


def _blechverbund(eintrag: QuerschnittsanalyseEintrag, analyse: Querschnittsanalyse,
                  teil: Bauteil, aufbau: Aufbau) -> None:
    """
    Eine Blechverbunddecke nach SIA 264, 5.4
    (:mod:`~opencivil.nachweis.qa_blechverbund`): je Lastfall Biegung und
    Normalkraft, plastisch, und Querkraft und Laengsschub, sobald einer
    ``V_z`` hat -- beide lesen ihre Widerstaende aus den Kennzahlen. Die
    Decke traegt in einer Richtung: ein Lastfall mit ``M_z``, ``V_y`` oder
    ``T`` sagt, dass sie nicht nachgewiesen werden. Eine Analyse rechnet
    eine Decke (:meth:`QuerschnittsanalyseEintrag.elemente`).
    """
    kennzahlen = KennzahlenBlechQA(analyse, analyse.bleche[0], eintrag.laengsschub)
    lastfaelle = _lastfaelle(eintrag)
    if lastfaelle:
        aufbau.eintragen(teil, "qa_blech", eintrag.kennung,
                         BlechBiegungQA(analyse, lastfaelle, kennzahlen))
    if any(l.V_z for l in lastfaelle):
        aufbau.eintragen(teil, "qa_blech_schub", eintrag.kennung,
                         BlechSchubQA(analyse, lastfaelle, kennzahlen))
    quer = [l.name for l in lastfaelle if l.M_z or l.V_y or l.T]
    if quer:
        aufbau.warnen(teil.raum, f"{ort_von(eintrag)}, {', '.join(quer)}: {EINE_RICHTUNG}")
    aufbau.kennzahlen_eintragen(teil, kennzahlen)


def _holz(eintrag: QuerschnittsanalyseEintrag, analyse: Querschnittsanalyse, teil: Bauteil,
          aufbau: Aufbau) -> None:
    """
    Ein Querschnitt aus einem einzigen Holz nach SIA 265: seine Werte fuer die
    Feuchteklasse der Analyse (:mod:`~opencivil.nachweis.qa_holz_werte`), je
    Lastfall Biegung und Normalkraft, Schub und Torsion, sobald einer sie hat
    (:mod:`~opencivil.nachweis.qa_holz`), Knicken und Kippen, sobald ein Fall
    eingeschaltet ist (:mod:`~opencivil.nachweis.qa_holz_stabilitaet`). Alle
    lesen aus den Werten; «stossartig» gilt je Fall.
    """
    werte = HolzwerteQA(analyse, eintrag.feuchteklasse)
    aufbau.werk.registriere(werte)
    teil.weitere_ziele.append(werte.id)
    lastfaelle = _lastfaelle(eintrag)
    stoesse = _stossartig(eintrag.lastfaelle)
    if lastfaelle:
        aufbau.eintragen(teil, "qa_holz", eintrag.kennung,
                         HolzBiegungQA(analyse, lastfaelle, werte, stoesse))
    if any(l.V_z or analyse.biegung.querkraft_y(l.V_y) or l.T for l in lastfaelle):
        aufbau.eintragen(teil, "qa_holz_schub", eintrag.kennung,
                         HolzSchubQA(analyse, lastfaelle, werte, stoesse))
    stabfaelle = eintrag.stabfaelle()
    if stabfaelle:
        aufbau.eintragen(teil, "qa_holz_stabilitaet", eintrag.kennung, HolzStabilitaetQA(
            analyse, stabfaelle, werte, _stossartig(eintrag.stabilitaetsfaelle)))
    aufbau.kennzahlen_eintragen(teil, KennzahlenHolzQA(analyse, werte))
    spannungsfaelle(eintrag, stoffe_von(aufbau, analyse.baustoffe), aufbau)


#: Je Bauweise, wer ihre Nachweise und Kennzahlen anmeldet -- eine Stelle statt einer
#: Kette von Abfragen.
_NACH_BAUWEISE: Dict[Bauweise, Callable[..., None]] = {
    Bauweise.STAHLBETON: _stahlbeton, Bauweise.STAHL: _stahl, Bauweise.VERBUND: _verbund,
    Bauweise.BLECHVERBUND: _blechverbund, Bauweise.HOLZ: _holz,
}


def _schubfluss(eintrag: QuerschnittsanalyseEintrag, analyse: Querschnittsanalyse,
                teil: Bauteil, aufbau: Aufbau) -> None:
    """
    Der Schubfluss in den Schnitten (:mod:`~opencivil.nachweis.qa_schubfluss`),
    sobald es einen Schnitt und einen eingeschalteten Fall gibt -- in jeder
    Bauweise, auch ohne Nachweise: er ist keiner. Jeder Fall rechnet mit
    seiner Wahl am Bauteil.
    """
    faelle = [f for f in eintrag.schubflussfaelle if f.aktiv]
    schnitte = eintrag.elemente().schnitte
    if not (faelle and schnitte):
        return
    stoffe = stoffe_von(aufbau, analyse.baustoffe)
    prozedur = SchubflussQA(analyse, [aus_schnitt(s) for s in schnitte], [
        Schubflussfall(name=f.name, N=si["N"], V=si["V_z"], M=si["M_y"], wahl=f.wahl(stoffe))
        for f, si in ((f, _in_si(f, "N", "V_z", "M_y")) for f in faelle)])
    aufbau.werk.registriere(prozedur)
    teil.weitere_ziele.append(prozedur.id)
    teil.schubfluss = prozedur


def _stossartig(faelle: Iterable[Any]) -> frozenset:
    """Die Namen der eingeschalteten Faelle, die stossartig sind."""
    return frozenset(f.name for f in faelle if f.aktiv and f.stossartig)


def ohne_nachweise(bauweise: Bauweise, stoffe: Iterable[Tuple[Baustoffart, str]]) -> str:
    """
    Warum ein Querschnitt dieser Bauweise keinen Nachweis hat -- leer bei
    jeder Bauweise (Stahl, Holz und Verbund seit 2026-11-26) ausser beim
    Holz aus mehreren Hoelzern: es braeuchte einen nach ihren Steifigkeiten
    gewichteten Querschnitt, den das Werkzeug nicht rechnet (nach Vorgabe,
    nicht nachgeschlagen). ``stoffe``: Art und Name jedes Baustoffs, wie fuer
    :func:`~opencivil.querschnitt.bauweise.bauweise`. Ein Satzteil ohne
    Punkt, fuer die Zusammenfassung
    (:meth:`~opencivil.projekt.aufbau.kern.Aufbau.ohne_nachweis`) und fuer die
    Zeichnung (:func:`~opencivil.web.zeichengeometrie.geometrie`).
    """
    hoelzer = list(dict.fromkeys(name for _, name in stoffe))
    if bauweise is not Bauweise.HOLZ or len(hoelzer) < 2:
        return ""
    return (f"einen {bauweise.querschnitt} aus mehreren Hölzern "
            f"({', '.join(f'«{h}»' for h in hoelzer)}) weist das Werkzeug nach "
            f"{bauweise.norm} noch nicht nach")


def ohne_diagramm(bauweise: Bauweise, stoffe: Iterable[Tuple[Baustoffart, str]]) -> str:
    """
    Warum ein Querschnitt dieser Bauweise kein Interaktionsdiagramm hat --
    leer beim Stahlbeton, dem einzigen mit einer Widerstandsflaeche. Ein
    Satz mit Punkt, fuer die Diagramme
    (:func:`~opencivil.web.diagrammdaten.analyse_diagramme`); ``stoffe`` wie
    bei :func:`ohne_nachweise`.
    """
    if bauweise is Bauweise.STAHLBETON:
        return ""
    fehlt = ohne_nachweise(bauweise, stoffe)
    if fehlt:
        return f"Kein Interaktionsdiagramm: {fehlt}."
    return (f"Kein Interaktionsdiagramm: für einen {bauweise.querschnitt} zeichnet das Werkzeug "
            f"noch keines. Seine Lastfälle weist es trotzdem nach.")


def ohne_analysen(bauweise: Bauweise) -> str:
    """
    Warum ein Querschnitt dieser Bauweise keine Spannung-Dehnung-Analyse hat
    -- leer, wo er eine hat. Ein Satz mit Punkt, fuer die Zeichnung
    (:func:`~opencivil.web.zeichengeometrie.geometrie`). Der Verbund und die
    Blechverbunddecke rechnen ihre Nachweise plastisch; ihre Linien
    braeuchten den Riss am ideellen Querschnitt, mit ``E_a/E_cm`` gewichtet,
    und die Werte der Analyse sind ungewichtet.
    """
    if bauweise not in (Bauweise.VERBUND, Bauweise.BLECHVERBUND):
        return ""
    return f"Einen {bauweise.querschnitt} rechnen die Spannung-Dehnung-Analysen noch nicht."


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

    def stoff(element: Mapping, feld: str, klasse: type) -> Baustoff:
        """Das Material im Feld ``feld`` eines Elements -- von einer Art, die das Feld nimmt."""
        return material(baustoffe, element[feld], stoffe_des_felds(klasse, feld), wo,
                        element["name"])

    elemente = eintrag.elemente()
    if elemente.fehler:
        # Ein Element ohne Lage laesst sich nicht rechnen -- und es still
        # wegzulassen hiesse, mit einem anderen Querschnitt zu rechnen.
        raise GeometrieFehler(elemente.fehler[0]["text"])
    # Ein Profil ist eine Flaeche aus Baustahl, ein Rohr dazu sein Loch.
    flaechen = [Flaechenteil(name=f["name"], kennung=f["kennung"], punkte=f["punkte"],
                             stoff=(None if f["aussparung"] else
                                    material(baustoffe, f["material"], f["stoffe"], wo, f["name"])),
                             profil=f["profil"])
                for f in elemente.flaechen]
    staebe = [{**s, "stahl": stoff(s, "stahl", StabEintrag)} for s in elemente.staebe]
    linien = [{**l, "stahl": stoff(l, "stahl", StablinieEintrag)} for l in elemente.linien]
    waende = [{**w, "stahl": stoff(w, "stahl", SchubwandEintrag) if w["durchmesser"] > 0 else None}
              for w in elemente.waende]
    glieder = [_glied(g, stoff(g, "stahl", SpanngliedEintrag), wo)
               for g in elemente.spannglieder]
    bleche = [aus_form(d["namen"]["blech"], d["kennung"],
                       material(baustoffe, d["blech"], stoffe_des_felds(BlechdeckeEintrag, "blech"),
                                wo, d["namen"]["blech"]), d["form"])
              for d in elemente.blechdecken]
    # Jeder Baustoff bekommt seine Wahl, auch wer keine eigene hat: so steht
    # die Vorgabe nur an der Beschreibung.
    wahl = eintrag.wahl({k: baustoffe[k] for k in eintrag.materialien() if k in baustoffe})
    return Querschnittsanalyse(
        name=eintrag.name, praefix=praefix,
        flaechen=flaechen, staebe=staebe, linien=linien, waende=waende,
        alpha_min=eintrag.alpha_min, alpha_max=eintrag.alpha_max, k_c=eintrag.k_c,
        # Eine Blechverbunddecke traegt in einer Richtung (SIA 264:2014, 5.4.1.1).
        wahl=wahl, biegung=EINACHSIG if eintrag.einachsig or bleche else SCHIEF,
        spannglieder=glieder, bleche=bleche)


def _glied(g: Mapping, stahl: Baustoff, wo: str) -> Spannglied:
    """
    Ein Spannglied mit seinem Spannstahl. Nennt Tabelle 7 sein Erzeugnis oder
    seine Art fuer die Sorte nicht, fehlt die Wahl noch (:func:`was_fehlt`).
    """
    mit_stahl = {**g, "stahl": stahl}
    grund = was_fehlt(mit_stahl)
    if grund:
        raise ProjektFehler(f"{g['name']}: {grund}.", wo=wo)
    return aus_glied(mit_stahl)
