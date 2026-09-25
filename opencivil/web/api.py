"""
opencivil/web/api.py -- Uebersetzung der Rechenergebnisse nach JSON.

VERANTWORTUNG:
Bildet :class:`Loesung`, Protokoll und Katalogdaten auf schlichte JSON-Strukturen
ab. Das ist die einzige Stelle, die beide Welten kennt.

Wichtig: hier wird nichts gerechnet und nichts formatiert, was der Rechenkern
nicht schon bestimmt hat. Die Oberflaeche bekommt fertige LaTeX-Zeichenketten
und fertig formatierte Zahlen -- sie soll die Darstellung nicht ein zweites Mal
erfinden, sonst laufen Bericht und Bildschirm auseinander.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

from opencivil.core.einheiten import KN, KNM, KN_PRO_M, MM, Groesse
from opencivil import spannungsanalyse
from opencivil.nachweis.querschnittsloeser import (
    Querschnittsloeser, Stahllage, beton_nichtlinear, stahl_bilinear)
from opencivil.nachweis.sproedes_versagen import rissmoment
from opencivil.querschnitt.platte import BREITE_Y_MM, Richtung
from opencivil.bericht.zusammenfassung import zusammenfassen
from opencivil.core.berechnung import grad_als_text
from opencivil.core.latex import als_text, tabelle, text_latex
from opencivil.core.protokoll import (
    Block, GleichungBlock, HinweisBlock, Protokoll, TabellenBlock, TextBlock,
    TitelBlock, UnterprotokollBlock,
)
from opencivil.core.rechenwerk import Loesung
from opencivil.core.wert import Wert
from opencivil.material.beton import BETON_VORLAGEN, BETONSORTEN
from opencivil.material.betonstahl import STAHLSORTEN, STAHL_VORLAGEN
from opencivil.nachweis.biegung_normalkraft import Erfuellungsart
from opencivil.nachweis.spannungsbegrenzung import GEFORDERT
from opencivil.projekt import (
    BEIDE_RICHTUNGEN, RISSANFORDERUNGEN, Aufbau, QuerschnittEintrag,
)


def endlich(daten: Any) -> Any:
    """
    Ersetzt unendliche und undefinierte Zahlen durch ``None``.

    ``json.dumps`` schreibt dafuer sonst ``Infinity`` bzw. ``NaN`` -- eine
    Erweiterung, die Python selbst wieder liest, ``JSON.parse`` im Browser aber
    ablehnt. Die Antwort kaeme mit Status 200 an und waere dennoch unbrauchbar.

    Solche Werte entstehen ganz regulaer: ein Erfuellungsgrad ist unendlich,
    wenn die Einwirkung null ist. In JSON wird daraus ``null``, und die
    Oberflaeche zeigt dafuer das Unendlichkeitszeichen.
    """
    if isinstance(daten, float):
        return daten if math.isfinite(daten) else None
    if isinstance(daten, dict):
        return {k: endlich(v) for k, v in daten.items()}
    if isinstance(daten, (list, tuple)):
        return [endlich(v) for v in daten]
    return daten


# ===========================================================================
# Katalog
# ===========================================================================


def katalog() -> dict:
    """Alles, was die Oberflaeche zum Aufbau ihrer Auswahlfelder braucht."""
    return {
        "betonsorten": [
            {"sorte": sorte, "f_ck": f_ck, "f_ctm": f_ctm}
            for sorte, (f_ck, f_ctm) in BETONSORTEN.items()
        ],
        "stahlsorten": [
            {
                "sorte": sorte,
                "f_yk": s.f_yk,
                "f_yk_druck": s.f_yk_druck,
                "eps_uk": s.eps_uk,
                "eps_ud": s.eps_ud,
            }
            for sorte, s in STAHLSORTEN.items()
        ],
        "kennwerte": {
            "beton": [_vorlage_dict(v) for v in BETON_VORLAGEN],
            "betonstahl": [_vorlage_dict(v) for v in STAHL_VORLAGEN],
        },
        "erfuellungsarten": [
            {"wert": a.value, "beschriftung": a.beschriftung} for a in Erfuellungsart
        ],
        "richtungen": [
            {"wert": "x", "beschriftung": "nur x-Richtung"},
            {"wert": "y", "beschriftung": "nur y-Richtung"},
            {"wert": BEIDE_RICHTUNGEN, "beschriftung": "beide Richtungen"},
        ],
        # Die frische Platte kommt aus dem Kern. Die Oberflaeche trug sie
        # einmal selbst -- zwanzig Felder, die jemand von Hand mit den
        # Vorgaben gleichhalten musste, und beim ersten Mal, als sich die
        # Vorgaben aenderten, lief das auseinander. Gesetzt werden dort jetzt
        # nur noch Kennung, Name und die beiden Materialien.
        "neue_platte": QuerschnittEintrag.neu(
            kennung="", name="", beton="", stahl="").als_dict(),
        # `spannungsnachweis` sagt, ob diese Anforderung den Nachweis gegen
        # das Fliessen unter haeufiger Einwirkung ueberhaupt verlangt -- bei
        # normaler steht in Tabelle 17 ein Strich. Die Oberflaeche braucht
        # das, um die eingetragenen Lastfaelle nicht stillschweigend
        # wegzurechnen; die Regel selbst bleibt im Kern. Nur dieser eine
        # Nachweis -- der quasi-staendige aus der Rissbreite laeuft immer.
        "rissanforderungen": [
            {"wert": wert, "beschriftung": text,
             "spannungsnachweis": wert in GEFORDERT}
            for wert, text in RISSANFORDERUNGEN.items()
        ],
    }


def _vorlage_dict(vorlage) -> dict:
    return {
        "kurzname": vorlage.kurzname,
        "symbol": vorlage.symbol,
        "einheit": vorlage.einheit.beschriftung,
        "einheit_latex": vorlage.einheit.latex or "",
        "beschreibung": vorlage.beschreibung,
        "referenz": vorlage.referenz,
        "stellen": vorlage.stellen,
        "berechnet": vorlage.ist_berechnet,
        "aus_sorte": not vorlage.ist_berechnet and not vorlage.ist_festwert,
    }


# ===========================================================================
# Werte und Protokoll
# ===========================================================================


def wert_dict(wert: Wert) -> dict:
    return {
        "id": wert.id,
        "kurzname": wert.definition.kurzname,
        "symbol": wert.symbol,
        "wert": wert.formatiert(),
        "zahl": wert.groesse.in_einheit(wert.einheit),
        # Rohzahl und Stellenzahl getrennt, damit eine Tabellenspalte feste
        # Nachkommastellen setzen kann. 'wert' streicht nachlaufende Nullen --
        # im Fliesstext richtig, in einer Zahlenkolonne nicht: dort stuende
        # sonst 205 neben 224.5.
        "stellen": wert.definition.stellen,
        "einheit": wert.einheit.beschriftung if wert.einheit.name not in ("", "-") else "",
        "einheit_latex": wert.einheit.latex or "",
        "beschreibung": wert.beschreibung,
        "referenz": wert.referenz,
        "quelle": wert.quelle.value,
        "quelle_text": wert.quelle.beschriftung,
        "herkunft": wert.herkunft or "",
        "latex": wert.zahl_latex(),
    }


def block_dict(block: Block) -> Optional[dict]:
    """Bildet einen Protokollbaustein ab. None fuer Unbekanntes."""
    if isinstance(block, TitelBlock):
        return {"art": "titel", "text": block.text, "ebene": block.ebene,
                "raum": block.raum}
    if isinstance(block, TextBlock):
        return {"art": "text", "text": block.text}
    if isinstance(block, GleichungBlock):
        eintrag = {
            "art": "gleichung",
            "latex": block.latex,
            "titel": block.titel,
            "referenz": block.referenz,
            "wert_id": block.wert_id,
            "gruppe": block.gruppe,
        }
        if block.formelzeile is not None:
            # Beide Fassungen mitgeben: die Oberflaeche kann die lange Form
            # umbrechen oder auf eine Zeile legen, ohne neu zu rechnen.
            eintrag["einzeilig"] = block.formelzeile.einzeilig()
            eintrag["mehrzeilig"] = block.formelzeile.mehrzeilig()
        return eintrag
    if isinstance(block, TabellenBlock):
        return {
            "art": "tabelle",
            "titel": block.titel,
            "kopf": list(block.kopf),
            "zeilen": [list(z) for z in block.zeilen],
            "latex": block.als_latex(),
        }
    if isinstance(block, HinweisBlock):
        return {
            "art": "hinweis",
            "text": block.text,
            "hinweisart": block.art.value,
            "beschriftung": block.art.beschriftung,
        }
    if isinstance(block, UnterprotokollBlock):
        return {
            "art": "unterprotokoll",
            "titel": block.titel,
            "bloecke": protokoll_liste(block.protokoll),
        }
    return None


def protokoll_liste(protokoll: Protokoll) -> List[dict]:
    return [d for d in (block_dict(b) for b in protokoll.nach_abschnitten()) if d is not None]


# ===========================================================================
# Loesung
# ===========================================================================


def loesung_dict(
    loesung: Loesung,
    aufbau: Optional[Aufbau] = None,
    ziele: Sequence[str] = (),
) -> dict:
    """
    Vollstaendige Abbildung eines Rechenlaufs.

    ``ketten`` enthaelt fuer jedes angeforderte Ziel die Rueckverfolgung -- genau
    die Berechnungen und Werte, die die Oberflaeche hervorheben soll.
    """
    ergebnis: Dict[str, Any] = {
        "werte": {wid: wert_dict(w) for wid, w in loesung.werte.items()},
        "protokoll": protokoll_liste(loesung.protokoll),
        "reihenfolge": list(loesung.reihenfolge),
        "vollstaendig": loesung.vollstaendig,
        "fehlende": [
            {
                "id": f.id,
                "beschreibung": f.beschreibung,
                "benoetigt_von": f.benoetigt_von,
                "pfad": list(f.pfad),
                "einheit": (
                    f.definition.einheit.beschriftung
                    if f.definition and f.definition.einheit.name not in ("", "-")
                    else ""
                ),
            }
            for f in loesung.fehlende
        ],
        "nicht_berechenbar": [
            {
                "ziel": s.ziel,
                "verworfene_varianten": [
                    {"berechnung": bid, "grund": grund}
                    for bid, grund in s.verworfene_varianten
                ],
            }
            for s in loesung.nicht_berechenbar.values()
        ],
        "urteile": [
            {
                "name": u.name,
                # Namensraum des Nachweises -- danach gruppiert die Oberflaeche
                # die Zusammenfassung nach Platten.
                "raum": u.raum,
                "art": u.art,
                "fall": u.fall,
                "erfuellt": u.erfuellt,
                # Einzige Kennzahl: Widerstand/Einwirkung, ab 1 erfuellt.
                "erfuellungsgrad": u.gradtext(),
                "erfuellungsgrad_zahl": u.erfuellungsgrad.si,
                "begruendung": u.begruendung,
                "hinweis": u.hinweis,
                "einwirkung": wert_dict(u.einwirkung) if u.einwirkung else None,
                "widerstand": wert_dict(u.widerstand) if u.widerstand else None,
            }
            # Die gefuehrten: diese Liste sagt, welche Nachweise gefuehrt
            # wurden, und danach zaehlt die Anzeige oben rechts. Ein stiller
            # Nachweis stuende dort als «nicht erfuellt», waere aber in keiner
            # Tabelle zu finden. Wo er hingehoert, steht er: unter der
            # Zusammenfassung seiner Platte, als Hinweis.
            for u in loesung.gefuehrte_urteile
        ],
        "alle_nachweise_erfuellt": loesung.alle_nachweise_erfuellt,
        "ketten": {
            ziel: {
                "berechnungen": loesung.kette(ziel),
                "werte": loesung.benoetigte_werte(ziel),
            }
            for ziel in ziele
            if loesung.hat(ziel)
        },
    }
    if aufbau is not None:
        ergebnis["linien"] = {
            kennung: _linie_dict(nachweis, aufbau)
            for kennung, nachweis in aufbau.nachweise.items()
            if nachweis.linie
        }
        ergebnis["werkstoffgesetze"] = werkstoffgesetze(aufbau, loesung)
        ergebnis["querkraftkurven"] = querkraftkurven(aufbau)
        ergebnis["neigungskurven"] = neigungskurven(aufbau)
        ergebnis["spannungsanalysen"] = spannungsanalysen(aufbau, loesung)
        ergebnis["zusammenfassungen"] = zusammenfassungen(loesung, aufbau)
        ergebnis["warnungen"] = list(aufbau.warnungen)
        ergebnis["zuordnung"] = zuordnung(aufbau)
    return ergebnis


def querkraftkurven(
    aufbau: Aufbau, gewaehlt: Optional[Mapping[str, float]] = None
) -> dict:
    """
    Der Querkraftwiderstand ueber dem Moment -- eine Kurve je Tragrichtung.

    Hoechstens zwei je Platte, x und y, und nur wo ein Querkraftnachweis
    gefuehrt wurde. Die Waagrechte ist vorzeichenbehaftet: rechts das positive
    Moment (Zug unten), links das negative (Zug oben). Beide Aeste im selben
    Bild, weil sie dieselbe Platte beschreiben.

    Einen Ast gibt es nur, wo auf der gezogenen Seite Bewehrung liegt. Fehlt
    sie, gibt es kein ``d`` -- und ohne ``d`` keinen Widerstand.

    ``v_Rd`` haengt ueber ``m_Rd(N_Ed)`` von der Normalkraft ab. Welche gilt,
    waehlt der Benutzer unter dem Diagramm; ``gewaehlt`` bildet die Kennung auf
    diese Normalkraft in kN ab. Ohne Angabe gilt die des ersten Falls dieser
    Richtung -- dann liegen dessen Punkte auf der Kurve.

    Einheiten wie in den anderen Diagrammen: kNm und kN/m.
    """
    gewaehlt = gewaehlt or {}
    kurven: Dict[str, Any] = {}

    for kennung, nachweis in aufbau.querkraft.items():
        if not nachweis.ergebnisse:
            continue
        # Mit Buegeln haengt der Widerstand nicht mehr am Moment, sondern an
        # der Neigung der Druckdiagonalen. Dann steht dort das andere Bild --
        # siehe neigungskurven().
        if nachweis.buegel is not None:
            continue
        querschnitt_kennung = kennung.split(".", 1)[0]
        querschnitt = aufbau.querschnitte.get(querschnitt_kennung)

        n_ed = gewaehlt.get(kennung)
        if n_ed is None:
            n_ed = nachweis.ergebnisse[0].fall.N_Ed.in_einheit(KN)
        kurve = nachweis.kurve(n_ed * 1e3)

        kurven[kennung] = {
            "querschnitt": querschnitt_kennung,
            "namensraum": querschnitt.id if querschnitt else "",
            "name": querschnitt.name if querschnitt else querschnitt_kennung,
            "richtung": nachweis.richtung.value,
            "N_Ed": n_ed,
            "aeste": [
                {
                    "moment_positiv": ast["moment_positiv"],
                    "zugseite": "unten" if ast["moment_positiv"] else "oben",
                    "m_Rd": ast["m_Rd"] / 1e3,
                    "d": ast["d"] * 1e3,
                    "punkte": [
                        {"M_Ed": M / 1e3, "v_Rd": v / 1e3, "plastisch": pl}
                        for M, v, pl in ast["punkte"]
                    ],
                }
                for ast in kurve["aeste"]
            ],
            # Moment vorzeichenbehaftet -- der Fall gehoert auf die Seite, auf
            # der er wirkt. Die Querkraft dagegen als Betrag: ihr Vorzeichen
            # spielt keine Rolle, gerechnet wird ohnehin mit |V_Ed|.
            "faelle": [
                {
                    "name": erg.fall.name,
                    "M_Ed": erg.fall.M_Ed.in_einheit(KNM),
                    "N_Ed": erg.fall.N_Ed.in_einheit(KN),
                    "V_Ed": abs(erg.fall.V_Ed.in_einheit(KN_PRO_M)),
                    "v_Rd": erg.v_Rd / 1e3,
                    "erfuellt": erg.erfuellt,
                    "plastisch": erg.plastisch,
                    "begruendung": erg.begruendung,
                }
                for erg in nachweis.ergebnisse
            ],
        }
    return kurven


#: Wie weit die Neigungskurve mindestens reicht, in Grad. Die beiden Grenzen
#: des Benutzers liegen normalerweise darin; gehen sie darueber hinaus, waechst
#: die Achse mit -- ein abgeschnittener Ast waere schlimmer als eine breite
#: Achse.
NEIGUNG_VON = 25
NEIGUNG_BIS = 45


def neigungskurven(aufbau: Aufbau) -> dict:
    """
    Der Querkraftwiderstand ueber der Neigung der Druckdiagonalen.

    Nur wo Buegel liegen -- sonst haengt der Widerstand am Moment und das
    andere Diagramm gilt.

    **Ein Bild je statischer Hoehe und Neigungsbereich.** Beides haengt am
    einzelnen Fall: ``d`` am Vorzeichen des Moments, der Bereich am Vorzeichen
    der Normalkraft. Faelle, die darin uebereinstimmen, liegen auf derselben
    Kurve und kommen ins selbe Bild; die anderen bekommen ihr eigenes.

    Gezeichnet wird ueber den ganzen Achsenbereich, auch ausserhalb der beiden
    Grenzen -- dort blass. Die Oberflaeche entscheidet das an ``gewaehlt``,
    gerechnet wird beides hier.
    """
    kurven: Dict[str, Any] = {}

    for kennung, nachweis in aufbau.querkraft.items():
        if nachweis.buegel is None or not nachweis.ergebnisse:
            continue
        querschnitt_kennung = kennung.split(".", 1)[0]
        querschnitt = aufbau.querschnitte.get(querschnitt_kennung)

        # Nach (statischer Hoehe, Grenzen) gruppieren -- in dieser Reihenfolge
        # gefunden, damit die Bilder in der Reihenfolge der Faelle stehen.
        gruppen: Dict[tuple, List[Any]] = {}
        for erg in nachweis.ergebnisse:
            if erg.massgebend is None:
                continue
            gruppen.setdefault(
                (round(erg.d, 9), erg.alpha_min, erg.alpha_max), []).append(erg)

        for nummer, ((d, a_min, a_max), gruppe) in enumerate(gruppen.items(), start=1):
            von = min(NEIGUNG_VON, a_min)
            bis = max(NEIGUNG_BIS, a_max)
            punkte = nachweis.neigungsverlauf(d, von, bis)
            kurven[f"{kennung}.{nummer}"] = {
                "querschnitt": querschnitt_kennung,
                "namensraum": querschnitt.id if querschnitt else "",
                "name": querschnitt.name if querschnitt else querschnitt_kennung,
                "richtung": nachweis.richtung.value,
                "d": d * 1e3,
                "alpha_min": a_min,
                "alpha_max": a_max,
                "zug": gruppe[0].zug_hebt_alpha,
                "punkte": [
                    {"alpha": q.alpha,
                     "V_Rd_s": q.V_Rd_s / 1e3,
                     "V_Rd_c": q.V_Rd_c / 1e3,
                     "V_Rd": q.V_Rd / 1e3,
                     "im_bereich": a_min <= q.alpha <= a_max}
                    for q in punkte
                ],
                "faelle": [
                    {
                        "name": erg.fall.name,
                        "V_Ed": abs(erg.fall.V_Ed.in_einheit(KN_PRO_M)),
                        "alpha": erg.massgebend.alpha,
                        "V_Rd": erg.v_Rd / 1e3,
                        "erfuellt": erg.erfuellt,
                        "begruendung": erg.begruendung,
                    }
                    for erg in gruppe
                ],
            }
    return kurven


def _loeserpaar(qs, richtung, wert) -> Optional[Tuple[Querschnittsloeser,
                                                      Querschnittsloeser, float]]:
    """
    Die beiden Querschnittsloeser einer Tragrichtung -- gerissen und nicht.

    Sie unterscheiden sich in genau einem Stueck, dem Betongesetz. Alles
    andere -- Hoehe, Breite, Lagen, Stahlgesetz, Suchfenster -- ist dasselbe,
    und das muss es sein: sonst verglichen die beiden Zustaende zwei
    verschiedene Querschnitte.

    Dazu das Rissmoment, denn zwischen den beiden wird darueber interpoliert.
    ``None``, wenn in dieser Richtung keine Bewehrung liegt.
    """
    posten = qs.posten_in_richtung(richtung)
    if not posten:
        return None
    lagen = [Stahllage(a_s=wert(as_id), z=wert(z_id), nummer=lage.nummer)
             for lage, _, _, as_id, z_id in posten]
    stahl = posten[0][0].stahl
    E_c_eff = wert(qs.beton.id_von("E_cm")) / (1.0 + wert(qs.id_von("kriechzahl")))
    gemeinsam = dict(
        h=wert(qs.id_von("h")), b=wert(qs.id_breite(richtung)), lagen=lagen,
        stahl=stahl_bilinear(E_s=wert(stahl.id_von("E_s")),
                             f_sd=wert(stahl.id_von("f_yd")),
                             eps_ud=wert(stahl.id_von("eps_ud"))),
        eps_druck=wert(qs.beton.id_von("eps_c2d")),
        eps_zug=wert(stahl.id_von("eps_ud")))
    gerissen = Querschnittsloeser(
        beton=beton_nichtlinear(f_cd=wert(qs.beton.id_von("f_cd")), E_c=E_c_eff,
                                eps_c1d=wert(qs.beton.id_von("eps_c1d")),
                                eps_c2d=wert(qs.beton.id_von("eps_c2d"))),
        **gemeinsam)
    ungerissen = Querschnittsloeser(
        beton=spannungsanalyse.beton_ungerissen(E_c=E_c_eff), **gemeinsam)
    M_Riss = rissmoment(h=gemeinsam["h"], b=gemeinsam["b"],
                        f_ctm=wert(qs.beton.id_von("f_ctm"))).M_Riss
    return gerissen, ungerissen, M_Riss


def _bild_dict(bild, h: float) -> dict:
    """Ein Querschnittsbild in Zeichengroessen: mm, Promille, N/mm², kN."""
    return {
        "eps_m": bild.eps_m * 1e3, "chi": bild.chi,
        "N": bild.N / 1e3, "M": bild.M / 1e3,
        "h": h * 1e3,
        "nulllinie": (bild.nulllinie * 1e3
                      if bild.nulllinie is not None else None),
        "beton": [{"z": f.z * 1e3, "eps": f.eps * 1e3, "sigma": f.sigma / 1e6}
                  for f in bild.beton],
        "stahl": [{"z": s.z * 1e3, "eps": s.eps * 1e3, "sigma": s.sigma / 1e6,
                   "nummer": s.nummer, "a_s": s.a_s * 1e6, "kraft": s.kraft / 1e3}
                  for s in bild.stahl],
        "konvergiert": bild.konvergiert, "hinweis": bild.hinweis,
    }


def spannungsanalysen(aufbau: Aufbau, loesung: Loesung) -> dict:
    """
    Die Auswertungen am Querschnitt, je Platte -- fertig zum Zeichnen.

    Kein Nachweis: hier steht kein Erfuellungsgrad und kein Urteil, sondern
    eine Antwort auf die Frage, was im Querschnitt geschieht. Gerechnet wird
    trotzdem mit demselben Faserintegral und denselben Werkstoffgesetzen wie
    in den Nachweisen -- ein zweites Modell daneben waere eine zweite
    Wahrheit ueber denselben Querschnitt.
    """
    ergebnis: Dict[str, list] = {}
    for kennung, eintrag in aufbau.spannungsfaelle.items():
        qs = aufbau.querschnitte.get(kennung)
        if qs is None:
            continue

        def wert(kid: str) -> float:
            return loesung.werte[kid].groesse.si

        faelle = []
        paare: Dict[str, Any] = {}
        for fall in eintrag:
            try:
                richtung = Richtung(fall.richtung)
            except ValueError:
                richtung = Richtung.X
            if richtung.value not in paare:
                try:
                    paare[richtung.value] = _loeserpaar(qs, richtung, wert)
                except KeyError:
                    paare[richtung.value] = None
            paar = paare[richtung.value]
            kopf = {"name": fall.name, "art": fall.art,
                    "richtung": richtung.value,
                    "titel": spannungsanalyse.Analyseart(fall.art).beschriftung}
            if paar is None:
                faelle.append({**kopf, "moeglich": False, "hinweis": (
                    f"In {richtung.beschriftung} liegt keine Bewehrung – ohne "
                    f"sie gibt es keinen Querschnitt zum Auswerten.")})
                continue
            gerissen, ungerissen, M_Riss = paar
            faelle.append({**kopf, "moeglich": True,
                           **_auswertung(fall, gerissen, ungerissen, M_Riss)})
        ergebnis[kennung] = faelle
    return ergebnis


def _auswertung(fall, gerissen, ungerissen, M_Riss: float) -> dict:
    """Die eine der drei Fragen stellen, die dieser Fall stellt."""
    art = spannungsanalyse.Analyseart(fall.art)
    if art is spannungsanalyse.Analyseart.DEHNUNGEN:
        bild = spannungsanalyse.aus_dehnungen(
            gerissen, eps_oben=fall.eps_oben / 1e3, eps_unten=fall.eps_unten / 1e3)
        return {"bild": _bild_dict(bild, gerissen.h)}
    if art is spannungsanalyse.Analyseart.MOMENT_KRUEMMUNG:
        kurve = spannungsanalyse.moment_kruemmung(
            gerissen, ungerissen, N=fall.N_Ed * 1e3, M_Riss=M_Riss)
        return {"kurve": {
            "N": kurve.N / 1e3, "M_Riss": kurve.M_Riss / 1e3,
            "M_Rd": kurve.M_Rd / 1e3, "hinweis": kurve.hinweis,
            "punkte": [{"M": p.M / 1e3, "chi": p.chi, "zeta": p.zeta,
                        "chi_I": p.chi_I, "chi_II": p.chi_II}
                       for p in kurve.punkte]}}
    bild = spannungsanalyse.aus_schnittgroessen(
        gerissen, N=fall.N_Ed * 1e3, M=fall.M_Ed * 1e3)
    return {"bild": _bild_dict(bild, gerissen.h)}


def werkstoffgesetze(aufbau: Aufbau, loesung: Loesung) -> dict:
    """
    Punktfolgen der Spannungs-Dehnungs-Beziehungen, je Material.

    Gerechnet wird mit denselben Gesetzen wie im Nachweis -- die Kurve zeigt
    also genau das, was der Querschnittsintegration zugrunde liegt, und nicht
    eine zweite, nachgebaute Fassung.

    Vorzeichen wie im ganzen Werkzeug: Zug positiv. Der Beton liegt damit im
    dritten Quadranten, der Stahl spannt sich ueber beide.
    """
    ergebnis: Dict[str, dict] = {}

    for kennung, stoff in aufbau.baustoffe.items():
        def wert(kurzname: str) -> Optional[float]:
            eintrag = loesung.werte.get(stoff.definitionen[kurzname].id)
            return eintrag.groesse.si if eintrag else None

        try:
            if stoff.art.value == "beton":
                eintrag = _betonkurve(stoff, wert)
            else:
                eintrag = _stahlkurve(stoff, wert)
        except (KeyError, TypeError):
            continue  # Kennwerte noch nicht gerechnet
        if eintrag:
            eintrag["name"] = stoff.name
            eintrag["art"] = stoff.art.value
            ergebnis[kennung] = eintrag
    return ergebnis


#: Anteil der Druckzonenhoehe, ueber den der Spannungsblock wirkt. Daraus folgt
#: der Knick des vereinfachten Verlaufs bei (1 - 0.85) * eps_c2d: bei linearem
#: Dehnungsverlauf mit eps_c2d an der Randfaser herrscht in der Tiefe 0.85x
#: gerade die Dehnung 0.15 * eps_c2d.
BLOCKANTEIL = 0.85


def _betonkurve(stoff, wert, schritte: int = 80) -> Optional[dict]:
    """Parabel-Rechteck-Beziehung, von null bis zur Bruchdehnung."""
    from opencivil.querschnitt.werkstoffgesetz import Betongesetz

    f_cd, eps_c1d = wert("f_cd"), wert("eps_c1d")
    eps_c2d, k_sigma = wert("eps_c2d"), wert("k_sigma")
    if None in (f_cd, eps_c1d, eps_c2d, k_sigma):
        return None

    gesetz = Betongesetz(f_cd=abs(f_cd), eps_c1d=abs(eps_c1d),
                         eps_c2d=abs(eps_c2d), k_sigma=k_sigma)
    punkte = []
    for i in range(schritte + 1):
        eps = -abs(eps_c2d) * i / schritte
        punkte.append({"eps": eps * 1e3, "sigma": gesetz.spannung(eps) / 1e6})

    return {
        "punkte": punkte,
        "x_titel": "ε [‰]",
        "y_titel": "σ [N/mm²]",
        "titel": "Beton – Parabel-Rechteck-Beziehung",
        "referenz": "SIA 262:2025, 4.2.1.6",
        "marken": [
            {"eps": -abs(eps_c1d) * 1e3, "sigma": -abs(f_cd) / 1e6, "text": "ε_c1d"},
            {"eps": -abs(eps_c2d) * 1e3, "sigma": -abs(f_cd) / 1e6, "text": "ε_c2d"},
        ],
        "vereinfacht": _spannungsblock(abs(f_cd), abs(eps_c2d)),
    }


def _spannungsblock(f_cd: float, eps_c2d: float) -> dict:
    """
    Der vereinfachte, rechteckige Spannungsverlauf.

    Unterhalb von ``(1 - 0.85) * eps_c2d`` wird keine Spannung angesetzt,
    darueber durchgehend ``f_cd``. Das ist dieselbe Vereinfachung, die auch der
    Handrechnung zugrunde liegt -- dort als Druckzone der Hoehe ``0.85 x``.
    Beide Bilder gehoeren zusammen, und genau deshalb steht die Stufe hier neben
    der Parabel: man sieht, was man aufgibt, wenn man von Hand rechnet.
    """
    eps_knick = (1.0 - BLOCKANTEIL) * eps_c2d
    ecken = [
        (0.0, 0.0),
        (-eps_knick, 0.0),
        (-eps_knick, -f_cd),
        (-eps_c2d, -f_cd),
    ]
    return {
        "punkte": [{"eps": e * 1e3, "sigma": s / 1e6} for e, s in ecken],
        "titel": "vereinfacht (Spannungsblock)",
        "beschreibung": (
            f"σ = 0 bis {1 - BLOCKANTEIL:.2f}·ε_c2d, darüber f_cd. "
            f"Entspricht der Druckzone {BLOCKANTEIL}·x der Handrechnung."
        ),
    }


def _stahlkurve(stoff, wert) -> Optional[dict]:
    """
    Bilineare Beziehung ohne Verfestigung.

    Fuenf Eckpunkte genuegen -- dazwischen ist sie gerade, und mehr Punkte
    wuerden nur vortaeuschen, dass etwas gekruemmt waere.
    """
    E_s, f_yd = wert("E_s"), wert("f_yd")
    f_yd_druck, eps_ud = wert("f_yd_druck"), wert("eps_ud")
    if None in (E_s, f_yd, f_yd_druck, eps_ud):
        return None

    eps_yd, eps_yd_druck = f_yd / E_s, abs(f_yd_druck) / E_s
    ecken = [
        (-abs(eps_ud), -abs(f_yd_druck)),
        (-eps_yd_druck, -abs(f_yd_druck)),
        (0.0, 0.0),
        (eps_yd, f_yd),
        (abs(eps_ud), f_yd),
    ]
    return {
        "punkte": [{"eps": e * 1e3, "sigma": s / 1e6} for e, s in ecken],
        "x_titel": "ε [‰]",
        "y_titel": "σ [N/mm²]",
        "titel": "Betonstahl – bilineare Beziehung",
        "referenz": "SIA 262:2025, 4.2.2.4",
        "marken": [
            {"eps": eps_yd * 1e3, "sigma": f_yd / 1e6, "text": "ε_yd"},
            {"eps": abs(eps_ud) * 1e3, "sigma": f_yd / 1e6, "text": "ε_ud"},
        ],
    }


def _knickpunkte(aufbau, nachweis) -> list:
    """
    Die Knicknachweise als Punktepaare fuer das M-N-Diagramm.

    Zu jedem Fall zwei Punkte auf derselben Hoehe N_Ed: das Moment 1. Ordnung
    und das am verformten System. Die Strecke dazwischen ist der Zuwachs aus
    Schiefstellung und Verformung -- im Diagramm sieht man sofort, ob er den
    Punkt ueber die Linie schiebt.

    Nur in x-Richtung, denn nur dort gibt es einen Knicknachweis.
    """
    if nachweis.richtung is not Richtung.X:
        return []
    kennung = nachweis.querschnitt.id.rsplit(".", 1)[-1]
    knicken = (aufbau.knicken or {}).get(kennung)
    if knicken is None:
        return []
    punkte = []
    for erg in knicken.ergebnisse:
        if erg.fall.N_Ed.si >= 0.0:
            continue
        punkte.append({
            "name": erg.fall.name,
            "N_Ed": erg.fall.N_Ed.in_einheit(KN),
            "M_Ed_1": abs(erg.fall.M_Ed_1.in_einheit(KNM)),
            "M_Ed_II": abs(erg.M_ges) / 1e3,
            "N_Rd": erg.N_Rd / 1e3,
            "M_bei_N_Rd": erg.M_bei_N_Rd / 1e3,
            "erfuellungsgrad": erg.erfuellungsgrad,
            "grad_text": grad_als_text(erg.erfuellungsgrad, erg.erfuellt),
            "erfuellt": erg.erfuellt,
            "stabil": erg.stabil,
            "begruendung": erg.begruendung,
        })
    return punkte


def _linie_dict(nachweis, aufbau=None) -> dict:
    """
    Die M-N-Interaktionslinien zum Zeichnen -- in kN und kNm.

    Zwei Linien: die genaue aus Dehnungsebenen (``punkte``) und das Polygon aus
    der Handrechnung (``handpunkte``). Nachgewiesen wird gegen das Polygon; die
    genaue Linie steht daneben, damit man sieht, wie viel die Vereinfachung
    kostet.
    """
    return {
        "richtung": nachweis.richtung.value,
        "querschnitt": nachweis.querschnitt.name,
        "punkte": [
            {"N": p.N / 1e3, "M": p.M / 1e3, "abschnitt": p.abschnitt}
            for p in nachweis.linie
        ],
        "handpunkte": [
            {"N": p.N / 1e3, "M": p.M / 1e3, "name": p.name}
            for p in getattr(nachweis, "handlinie", [])
        ],
        "kombinationen": [
            {
                "name": a.schnittgroessen.name,
                "M_Ed": a.schnittgroessen.M_Ed.in_einheit(KNM),
                "N_Ed": a.schnittgroessen.N_Ed.in_einheit(KN),
                "art": a.schnittgroessen.art.value,
                "art_text": a.schnittgroessen.art.beschriftung,
                "innerhalb": a.innerhalb,
                "erfuellungsgrad": a.erfuellungsgrad,
                "grad_text": grad_als_text(a.erfuellungsgrad, a.innerhalb),
                "groesse": a.achse.name,
                "massstab": a.massstab.value,
                "massstab_text": a.massstab.beschriftung,
                "widerstand": (
                    {"N": a.widerstand[0] / 1e3, "M": a.widerstand[1] / 1e3}
                    if a.widerstand
                    else None
                ),
                "begruendung": a.begruendung,
            }
            for a in nachweis.auswertungen
        ],
        # Die Knickfaelle gehoeren in dasselbe Bild: sie tragen dieselbe
        # Normalkraft gegen dieselbe Linie, nur mit einem groesseren Moment.
        "knickfaelle": _knickpunkte(aufbau, nachweis) if aufbau else [],
    }


#: Welche Spalte der Zusammenfassung den Erfuellungsgrad traegt. Die
#: Oberflaeche hinterlegt genau sie -- zaehlen statt raten, sonst haenge die
#: Einfaerbung an der Reihenfolge der Kopfzeile.
GRAD_SPALTE = 4

#: Ausrichtung der Spalten, in der Schreibweise von LaTeX. Sie geht auch an
#: die Oberflaeche: dort richtet sich der Textsatz danach, statt aus dem
#: Spaltenindex zu erraten, was Zahl ist und was nicht.
AUSRICHTUNG = "llrrr"


def zusammenfassungen(loesung: Loesung, aufbau: Aufbau) -> dict:
    """
    Je Platte die Nachweistabelle -- Zeilen **und** ihr LaTeX.

    Gebaut wird sie hier und nicht in der Oberflaeche: sonst gaebe es sie
    zweimal, einmal als HTML und einmal fuer den Kopierknopf, und die beiden
    liefen auseinander. Die Oberflaeche faerbt nur noch ein, was ``erfuellt``
    sagt.

    Dazu die beiden Angaben ueber der Tabelle: was die Platte ist
    (``angaben``) und wie sie bewehrt ist (``bewehrung``). Beide tragen
    fertiges LaTeX und werden in der Oberflaeche als gewoehnliche Gleichung
    bzw. Tabelle gezeichnet -- mit denselben Kopierknoepfen wie alles andere.

    Eine Spalte *Urteil* gibt es nicht mehr: sie stand neben dem
    Erfuellungsgrad und sagte dasselbe noch einmal. Erfuellt oder nicht zeigt
    jetzt die Hinterlegung des Grads.

    *Nachweis* und *Bezeichnung* stehen dagegen getrennt. Vorher stand dort
    ``M-N: Feld``, und zwei Kombinationen gleichen Namens in x und y ergaben
    zweimal dieselbe Zeile. Jetzt sagt die erste Spalte, was fuer ein Nachweis
    es ist -- ausgeschrieben, mit Richtung -- und die zweite, wie der Fall
    heisst.
    """
    kopf = [r"\text{Nachweis}", r"\text{Bezeichnung}", r"\text{Widerstand}",
            r"\text{Einwirkung}", r"\alpha_{eff}"]

    def zelle(wert) -> str:
        """Feste Stellenzahl -- in einer Spalte steht immer dieselbe Groesse."""
        if wert is None:
            return r"\text{--}"
        zahl = wert.groesse.in_einheit(wert.einheit)
        return (rf"{wert.symbol} = {zahl:.{wert.definition.stellen}f}"
                rf"{wert.einheit.als_latex()}")

    ergebnis: Dict[str, Any] = {}
    for platte in zusammenfassen(aufbau, loesung).platten:
        # Eine Platte ohne jedes Urteil bekommt keine Tabelle -- die
        # Oberflaeche zeigt dafuer ihren eigenen Leerzustand. Die Konsole
        # schreibt an dieser Stelle «Kein Nachweis gefuehrt».
        if platte.leer:
            continue
        qs = aufbau.querschnitte[platte.kennung]
        zeilen = [
            {
                "zellen": [
                    als_text(z.nachweis),
                    als_text(z.fall) if z.fall else r"\text{--}",
                    zelle(z.widerstand),
                    zelle(z.einwirkung),
                    z.urteil.gradtext(latex=True),
                ],
                "erfuellt": z.urteil.erfuellt,
                "begruendung": z.urteil.begruendung,
                # Nur was die Pruefung ausdruecklich meldet -- siehe
                # NachweisUrteil.hinweis.
                "hinweis": z.urteil.hinweis,
            }
            for z in platte.zeilen
        ]
        ergebnis[platte.kennung] = {
            "kopf": kopf,
            "zeilen": zeilen,
            "grad_spalte": GRAD_SPALTE,
            "ausrichtung": AUSRICHTUNG,
            "latex": tabelle(kopf, [z["zellen"] for z in zeilen], AUSRICHTUNG),
            "angaben": _plattenangaben(qs),
            "bewehrung": _bewehrungsuebersicht(qs),
            # Der Grad kommt fertig gesetzt: welche Stelle noetig ist, damit
            # er dem Wort «nicht erfuellt» nicht widerspricht, weiss hier
            # dieselbe Stelle wie fuer die Tabelle.
            "stille": [
                {"nachweis": z.nachweis, "fall": z.fall,
                 "grad": z.urteil.gradtext(), "begruendung": z.urteil.begruendung}
                for z in platte.stille
            ],
        }
    return ergebnis


def _plattenangaben(qs) -> dict:
    """
    Beton, Dicke und betrachtete Breite -- eine Zeile ueber der Tabelle.

    Die Breite in y steht nur da, wenn sie von der eingegebenen abweicht.
    Sonst waere es bei jeder Platte dieselbe Zahl zweimal.
    """
    latex = (rf"{als_text('Beton ' + qs.beton.name)} \qquad "
             rf"h = {qs.h.als_latex(0, MM)} \qquad "
             rf"b_x = {qs.b.als_latex(0, MM)}")
    if abs(qs.b.si - BREITE_Y_MM / 1000.0) > 1e-9:
        latex += rf" \qquad b_y = {Groesse(BREITE_Y_MM, MM).als_latex(0, MM)}"
    return {"latex": latex, "titel": "Angaben zur Platte"}


def _bewehrungsuebersicht(qs) -> dict:
    """
    Überdeckungen und Lagen, wie man die Platte im Schnitt sieht.

    Von oben nach unten gelesen: obere Überdeckung, 4. bis 1. Lage, untere
    Überdeckung. Dieselbe Folge wie in der Eingabemaske -- wer beides
    nebeneinander hat, soll nicht umdenken müssen.

    Grundbewehrung und Zulage stehen in einer Zeile, getrennt durch ``+`` --
    die Lage ist eine Lage, auch wenn sie aus zwei Posten besteht.
    """
    kopf = [r"\text{Lage}", r"\text{Richtung}", r"\text{Bewehrung}",
            r"\text{Stahl}"]
    strich = r"\text{--}"

    def menge(posten) -> str:
        if not posten.vorhanden:
            return ""
        durchmesser = rf"\varnothing {posten.durchmesser.formatiert(0)}"
        if posten.ueber_abstand:
            return rf"{durchmesser}@{posten.abstand.formatiert(0)}"
        return rf"{posten.anzahl:g} \times {durchmesser}"

    zeilen = [[als_text("Überdeckung oben"), strich,
               qs.ueberdeckung_oben.als_latex(0, MM), strich]]
    for lage in reversed(qs.lagen):
        posten = [menge(lage.grund), menge(lage.zulage)]
        vorhanden = [t for t in posten if t]
        zeilen.append([
            als_text(f"{lage.nummer}. Lage"),
            als_text(lage.richtung.value),
            " + ".join(vorhanden) if vorhanden else strich,
            als_text(lage.stahl.name) if (vorhanden and lage.stahl) else strich,
        ])
    zeilen.append([als_text("Überdeckung unten"), strich,
                   qs.ueberdeckung_unten.als_latex(0, MM), strich])

    # Die Bügel stehen am Ende und nicht in der Stapelfolge: sie sitzen über
    # die ganze Höhe und haben darin keinen Platz.
    if qs.hat_buegel:
        b = qs.querkraftbewehrung
        # Kurzform wie bei den Lagen: Durchmesser und die beiden Teilungen,
        # sonst nichts. Der Bügelquerschnitt steht in der Herleitung, wo er
        # auch hergeleitet wird -- in einer Übersicht ist er nur Ballast.
        menge_y = (b.abstand_y.formatiert(0) if b.ueber_abstand_y
                   else rf"{b.anzahl_y:g}\,\text{{Stk}}")
        zeilen.append([
            als_text("Querkraftbewehrung"),
            als_text("x/y"),
            (rf"\varnothing {b.durchmesser.formatiert(0)}"
             rf"@{b.abstand_x.formatiert(0)}@{menge_y}"),
            als_text(b.stahl.name) if b.stahl else strich,
        ])

    return {
        "kopf": kopf,
        "zeilen": zeilen,
        "titel": "Bewehrung von oben nach unten",
        "latex": tabelle(kopf, zeilen, "llll"),
    }


def zuordnung(aufbau: Aufbau) -> dict:
    """Verbindet die Kennungen der Oberflaeche mit den Wert-IDs des Rechenwerks."""
    return {
        "materialien": {
            kennung: {
                "namensraum": stoff.id,
                "name": stoff.name,
                "art": stoff.art.value,
                "kennwerte": {
                    kurzname: definition.id
                    for kurzname, definition in stoff.definitionen.items()
                },
            }
            for kennung, stoff in aufbau.baustoffe.items()
        },
        "querschnitte": {
            kennung: {
                "namensraum": qs.id,
                "name": qs.name,
                # Der Beton gehoert zur Platte und steht darum bei ihren
                # Abmessungen, nicht nur in der Materialliste.
                "beton": qs.beton.name,
                "werte": {
                    kurzname: definition.id
                    for kurzname, definition in qs.definitionen.items()
                },
                "nachweise": {
                    schluessel.split(".", 1)[1]: {
                        "ziele": {n: d.id for n, d in nw.d_ausnutzung.items()},
                        "eckwerte": {n: d.id for n, d in nw.d_eckwerte.items()},
                    }
                    for schluessel, nw in aufbau.nachweise.items()
                    if schluessel.split(".", 1)[0] == kennung
                },
                # Durchmesser, Teilung und Stabzahl als Zahlen, nicht nur als
                # Text: das Querschnittsbild soll die tatsaechliche Teilung
                # zeichnen und nicht eine erfundene Stabzahl.
                "bewehrung": [
                    {
                        "lage": lage.nummer,
                        "art": art.value,
                        "richtung": lage.richtung.value,
                        "stahl": lage.stahl.name if lage.stahl else "",
                        "menge": posten.menge_text(),
                        "phi": posten.durchmesser.in_einheit(MM),
                        "abstand": (posten.abstand.in_einheit(MM)
                                    if posten.abstand is not None else None),
                        # anzahl ist eine blanke Zahl, keine Groesse -- Staebe
                        # haben keine Einheit.
                        "anzahl": posten.anzahl,
                        "a_s_id": as_id,
                        "z_id": z_id,
                    }
                    for lage, art, posten, as_id, z_id in qs.posten_ids
                ],
            }
            for kennung, qs in aufbau.querschnitte.items()
        },
    }
