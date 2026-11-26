"""
opencivil/projekt/aufbau/querschnittsanalyse.py -- ein gezeichneter Querschnitt wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.querschnittsanalyse.QuerschnittsanalyseEintrag`
die :class:`~opencivil.querschnitt.analyse.Querschnittsanalyse` und ihre
Nachweise: Biegung und Normalkraft, Querkraft und Torsion, Duktilitaet,
sproedes Versagen, die Zwaengungen, die Stahlspannungen und das Knicken
(:func:`bauen`) -- dazu die Kennzahlen. Ein Querschnitt aus Stahl hat seine
eigenen (:func:`_stahl`), einer im Verbund (:func:`_verbund`) und einer aus
Holz auch (:func:`_holz`). Eine leere oder fehlerhafte Zeichnung wird kein
Bauteil, nur ein Hinweis.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Mapping, Tuple

from opencivil.core.berechnung import Kennzahlprozedur
from opencivil.material.basis import Baustoff, Baustoffart
from opencivil.material.spannstahl import erzeugnis
from opencivil.projekt.lesen import ProjektFehler, als_groesse, ort_von, stoffe_des_felds
from opencivil.projekt.querschnittsanalyse import (
    QuerschnittsanalyseEintrag, SchubwandEintrag, StabEintrag, StablinieEintrag,
)
from opencivil.projekt.spannglieder import SpanngliedEintrag
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
from opencivil.nachweis.qa_knicken import KnickenQA, QAKnickfall
from opencivil.nachweis.richtungsnachweise import DuktilitaetQA, SproedesVersagenQA
from opencivil.nachweis.schiefe_biegung import SchiefeBiegung
from opencivil.nachweis.schubwandnachweis import Schubwandnachweis, schub_belastet
from opencivil.querschnitt.analyse import Flaechenteil, Lastfall, Querschnittsanalyse
from opencivil.querschnitt.bauweise import Bauweise
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

    Das alles beim Stahlbeton. Ein Querschnitt aus Stahl rechnet nach SIA 263
    (:func:`_stahl`), einer im Verbund nach SIA 264 (:func:`_verbund`), einer
    aus Holz nach SIA 265 (:func:`_holz`). Einer aus mehreren Hoelzern
    rechnet bisher nur seine Werte -- Flaeche, Schwerpunkt,
    Traegheitsmomente --; seine Zusammenfassung sagt, dass die Nachweise
    fehlen (:func:`ohne_nachweise`). Seine Spannung-Dehnung-Analysen rechnet
    er trotzdem. Der Verbund hat noch keine (:func:`ohne_analysen`).

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
    if analyse.bauweise is Bauweise.STAHL:
        return _stahl(eintrag, analyse, teil, aufbau)
    if analyse.bauweise is Bauweise.VERBUND:
        return _verbund(eintrag, analyse, teil, aufbau)
    fehlt = ohne_nachweise(analyse.bauweise, ((s.art, s.name) for s in analyse.baustoffe))
    if fehlt:
        aufbau.ohne_nachweis(teil, ort_von(eintrag), fehlt)
        if not ohne_analysen(analyse.bauweise):
            spannungsfaelle(eintrag, stoffe_von(aufbau, analyse.baustoffe), aufbau)
        return teil
    if analyse.bauweise is Bauweise.HOLZ:
        return _holz(eintrag, analyse, teil, aufbau)
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
    _kennzahlen(KennzahlenQA(analyse), teil, aufbau)
    spannungsfaelle(eintrag, stoffe, aufbau)
    return teil


def _lastfaelle(eintrag: QuerschnittsanalyseEintrag) -> List[Lastfall]:
    """Die eingeschalteten Lastfaelle in SI, aus der Einheit ihrer Felder: N, M_y ... aus N_Ed, M_y_Ed ..."""
    return [Lastfall(name=l.name, **_in_si(l, "N", "M_y", "M_z", "V_y", "V_z", "T"))
            for l in eintrag.lastfaelle if l.aktiv]


def _stahl(eintrag: QuerschnittsanalyseEintrag, analyse: Querschnittsanalyse, teil: Bauteil,
           aufbau: Aufbau) -> Bauteil:
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
    _kennzahlen(kennzahlen, teil, aufbau)
    spannungsfaelle(eintrag, stoffe_von(aufbau, analyse.baustoffe), aufbau)
    return teil


def _verbund(eintrag: QuerschnittsanalyseEintrag, analyse: Querschnittsanalyse, teil: Bauteil,
             aufbau: Aufbau) -> Bauteil:
    """
    Ein Querschnitt aus Baustahl und Beton nach SIA 264
    (:mod:`~opencivil.nachweis.qa_verbund`): je Lastfall Biegung und
    Normalkraft, plastisch, und Querkraft, sobald einer sie hat -- die traegt
    der Stahl allein. Beide lesen den Widerstand gegen Querkraft aus den
    Kennzahlen. Torsion weist er nicht nach; ein Lastfall mit ``T_Ed`` sagt
    es. Verduebelung, Knicken und Kippen fehlen noch, ebenso die
    Spannung-Dehnung-Analysen (:func:`ohne_analysen`).
    """
    kennzahlen = KennzahlenVerbundQA(analyse)
    lastfaelle = _lastfaelle(eintrag)
    if lastfaelle:
        aufbau.eintragen(teil, "qa_verbund", eintrag.kennung,
                         VerbundBiegungQA(analyse, lastfaelle, kennzahlen))
    if any(l.V_z or analyse.biegung.querkraft_y(l.V_y) for l in lastfaelle):
        aufbau.eintragen(teil, "qa_verbund_schub", eintrag.kennung,
                         VerbundQuerkraftQA(analyse, lastfaelle, kennzahlen))
    mit_torsion = [l.name for l in lastfaelle if l.T]
    if mit_torsion:
        aufbau.warnen(teil.raum,
                      f"{ort_von(eintrag)}, {', '.join(mit_torsion)}: {OHNE_TORSION_VERBUND}")
    _kennzahlen(kennzahlen, teil, aufbau)
    return teil


def _holz(eintrag: QuerschnittsanalyseEintrag, analyse: Querschnittsanalyse, teil: Bauteil,
          aufbau: Aufbau) -> Bauteil:
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
    _kennzahlen(KennzahlenHolzQA(analyse, werte), teil, aufbau)
    spannungsfaelle(eintrag, stoffe_von(aufbau, analyse.baustoffe), aufbau)
    return teil


def _stossartig(faelle: Iterable[Any]) -> frozenset:
    """Die Namen der eingeschalteten Faelle, die stossartig sind."""
    return frozenset(f.name for f in faelle if f.aktiv and f.stossartig)


def _kennzahlen(kennzahlen: Kennzahlprozedur, teil: Bauteil, aufbau: Aufbau) -> None:
    """Die Kennzahlen ins Rechenwerk und unter das Bauteil."""
    aufbau.werk.registriere(kennzahlen)
    teil.weitere_ziele.append(kennzahlen.id)
    teil.kennzahlen += kennzahlen.kennzahlen


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
    (:func:`~opencivil.web.zeichengeometrie.geometrie`). Der Verbund rechnet
    seine Nachweise plastisch; seine Linien braeuchten den Riss am ideellen
    Querschnitt, mit ``E_a/E_cm`` gewichtet, und die Werte der Analyse sind
    ungewichtet.
    """
    if bauweise is not Bauweise.VERBUND:
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
