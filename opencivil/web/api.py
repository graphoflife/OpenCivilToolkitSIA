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
from typing import Any, Dict, List, Optional, Sequence

from opencivil.core.einheiten import KN, KNM
from opencivil.core.protokoll import (
    Block, GleichungBlock, HinweisBlock, Protokoll, TabellenBlock, TextBlock,
    TitelBlock, UnterprotokollBlock,
)
from opencivil.core.rechenwerk import Loesung
from opencivil.core.wert import Wert
from opencivil.material.beton import BETON_VORLAGEN, BETONSORTEN
from opencivil.material.betonstahl import STAHLSORTEN, STAHL_VORLAGEN
from opencivil.nachweis.biegung_normalkraft import Erfuellungsart
from opencivil.projekt import BEIDE_RICHTUNGEN, Aufbau


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
    }


def _vorlage_dict(vorlage) -> dict:
    return {
        "kurzname": vorlage.kurzname,
        "symbol": vorlage.symbol,
        "einheit": vorlage.einheit.name,
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
        "einheit": wert.einheit.name if wert.einheit.name not in ("", "-") else "",
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
        return {"art": "titel", "text": block.text, "ebene": block.ebene}
    if isinstance(block, TextBlock):
        return {"art": "text", "text": block.text}
    if isinstance(block, GleichungBlock):
        eintrag = {
            "art": "gleichung",
            "latex": block.latex,
            "titel": block.titel,
            "referenz": block.referenz,
            "wert_id": block.wert_id,
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
    return [d for d in (block_dict(b) for b in protokoll.bloecke) if d is not None]


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
                    f.definition.einheit.name
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
                "erfuellt": u.erfuellt,
                "ausnutzung": u.ausnutzung.formatiert(3),
                "ausnutzung_zahl": u.ausnutzung.si,
                # Angezeigt wird der Erfuellungsgrad: um welchen Faktor die
                # Einwirkung noch wachsen duerfte. >= 1 heisst erfuellt.
                "erfuellungsgrad": (
                    u.erfuellungsgrad.formatiert(2) if u.erfuellungsgrad else "\u221e"),
                "erfuellungsgrad_zahl": (
                    u.erfuellungsgrad.si if u.erfuellungsgrad else None),
                "begruendung": u.begruendung,
                "einwirkung": wert_dict(u.einwirkung) if u.einwirkung else None,
                "widerstand": wert_dict(u.widerstand) if u.widerstand else None,
            }
            for u in loesung.urteile
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
            kennung: _linie_dict(nachweis)
            for kennung, nachweis in aufbau.nachweise.items()
            if nachweis.linie
        }
        ergebnis["warnungen"] = list(aufbau.warnungen)
        ergebnis["zuordnung"] = zuordnung(aufbau)
    return ergebnis


def _linie_dict(nachweis) -> dict:
    """Die M-N-Interaktionslinie zum Zeichnen -- in kN und kNm."""
    return {
        "richtung": nachweis.richtung.value,
        "querschnitt": nachweis.querschnitt.name,
        "punkte": [
            {"N": p.N / 1e3, "M": p.M / 1e3, "abschnitt": p.abschnitt}
            for p in nachweis.linie
        ],
        "kombinationen": [
            {
                "name": a.schnittgroessen.name,
                "M_Ed": a.schnittgroessen.M_Ed.in_einheit(KNM),
                "N_Ed": a.schnittgroessen.N_Ed.in_einheit(KN),
                "art": a.schnittgroessen.art.value,
                "art_text": a.schnittgroessen.art.beschriftung,
                "innerhalb": a.innerhalb,
                "ausnutzung": a.ausnutzung,
                "erfuellungsgrad": a.erfuellungsgrad,
                "groesse": a.groesse,
                "widerstand": (
                    {"N": a.widerstand[0] / 1e3, "M": a.widerstand[1] / 1e3}
                    if a.widerstand
                    else None
                ),
                "begruendung": a.begruendung,
            }
            for a in nachweis.auswertungen
        ],
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
                "bewehrung": [
                    {
                        "lage": lage.nummer,
                        "art": art.value,
                        "richtung": lage.richtung.value,
                        "stahl": lage.stahl.name if lage.stahl else "",
                        "menge": posten.menge_text(),
                        "a_s_id": as_id,
                        "z_id": z_id,
                    }
                    for lage, art, posten, as_id, z_id in qs.posten_ids
                ],
            }
            for kennung, qs in aufbau.querschnitte.items()
        },
    }
