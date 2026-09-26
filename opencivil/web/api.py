"""
opencivil/web/api.py -- Uebersetzung der Rechenergebnisse nach JSON.

VERANTWORTUNG:
Bildet :class:`Loesung`, Protokoll, Zusammenfassung und Katalogdaten auf
schlichte JSON-Strukturen ab. Zusammen mit :mod:`opencivil.web.diagrammdaten`,
das die Punktfolgen der Diagramme liefert, ist das die einzige Stelle, die
beide Welten kennt.

Wichtig: hier wird nichts gerechnet und nichts formatiert, was der Rechenkern
nicht schon bestimmt hat. Die Oberflaeche bekommt fertige LaTeX-Zeichenketten
und fertig formatierte Zahlen -- sie soll die Darstellung nicht ein zweites Mal
erfinden, sonst laufen Bericht und Bildschirm auseinander.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from opencivil.bewehrungssuche import Suchmodus
from opencivil.core.einheiten import MM
from opencivil.bericht.formelsammlung import Thema
from opencivil.bericht.markdown import block_markdown
from opencivil.bericht.zusammenfassung import (
    GRAD_SPALTE, STAPEL_SPALTEN, bewehrungsuebersicht, hinweise, nachweistabelle,
    plattenangaben, stiller_hinweis, zusammenfassen,
)
from opencivil.core.latex import Mathe, Zelle
from opencivil.core.protokoll import (
    GleichungBlock, HinweisBlock, Protokoll, TabellenBlock, Tafel, TextBlock,
    TitelBlock, UnterprotokollBlock, darstellen,
)
from opencivil.core.rechenwerk import Loesung
from opencivil.core.wert import Wert
from opencivil.gleichungen.ausdruck import EINHEITENNAMEN, blattname
from opencivil.material.beton import BETON_VORLAGEN, BETONSORTEN
from opencivil.material.betonstahl import STAHLSORTEN, STAHL_VORLAGEN
from opencivil.nachweis.biegung_normalkraft import Erfuellungsart
from opencivil.nachweis.duktilitaet import HOECHSTENS as DUKTILITAET_HOECHSTENS
from opencivil.nachweis.spannungsbegrenzung import GrenzeGegenFliessen
from opencivil.projekt import (
    BEIDE_RICHTUNGEN, RISSANFORDERUNGEN, Aufbau, QuerschnittEintrag,
)
from opencivil.projekt.gleichungen import GleichungszeileEintrag
from opencivil.web import diagrammdaten


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
        # `fliessnachweis` sagt, ob diese Anforderung den Nachweis gegen
        # das Fliessen unter haeufiger Einwirkung ueberhaupt verlangt -- bei
        # normaler steht in Tabelle 17 ein Strich. Die Oberflaeche braucht
        # das, um die eingetragenen Lastfaelle nicht stillschweigend
        # wegzurechnen; die Regel selbst bleibt bei der Grenze. Der
        # quasi-staendige Nachweis aus der Rissbreite laeuft immer.
        "rissanforderungen": [
            {"wert": wert, "beschriftung": text,
             "fliessnachweis": GrenzeGegenFliessen.gilt_bei(wert)}
            for wert, text in RISSANFORDERUNGEN.items()
        ],
        "suchmodi": [
            {"wert": m.value, "beschriftung": m.beschriftung}
            for m in Suchmodus
        ],
        # Wie weit sich die Grenze x/d hoechstens setzen laesst -- fuer das
        # Feld; geprueft wird beim Bauen der Platte.
        "duktilitaet": {"hoechstens": DUKTILITAET_HOECHSTENS},
        # Fuer das Blatt: die leere Zeile wie die frische Platte oben, und die
        # Einheiten, die der Leser in \mathrm{...} versteht.
        "neue_gleichungszeile": GleichungszeileEintrag().als_dict(),
        "einheiten": sorted(EINHEITENNAMEN),
    }


def obergrenzen(projekt) -> Dict[str, str]:
    """
    Je Platte die Obergrenze der automatischen Bewehrung, fertig als Text --
    «4712 mm²/m» oder «keine». Die Oberflaeche zeigt sie neben den Eingaben,
    ohne selbst zu rechnen.
    """
    def text(grenze: float) -> str:
        return f"{grenze:.0f} mm²/m" if math.isfinite(grenze) else "keine"

    return {q.kennung: text(q.automatik_grenze.je_meter) for q in projekt.querschnitte}


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
        # Unter welchem Namen der Wert in einem Blatt steht -- der Vorschlag,
        # wenn ihn jemand dort als Projektwert waehlt. Leer: kein gueltiger Name.
        "blattname": blattname(wert.symbol),
    }


def _titel_dict(block: TitelBlock, tiefe: int) -> dict:
    return {"art": "titel", "text": block.text, "ebene": block.ebene,
            "raum": block.raum}


def _text_dict(block: TextBlock, tiefe: int) -> dict:
    return {"art": "text", "text": block.text}


def _gleichung_dict(block: GleichungBlock, tiefe: int) -> dict:
    eintrag = {
        "art": "gleichung",
        "latex": block.latex,
        # Fuer die Kopierknoepfe: der Block, wie er im Markdown-Bericht steht.
        "markdown": block_markdown(block),
        "titel": block.titel,
        "referenz": block.referenz,
        "wert_id": block.wert_id,
        "gruppe": block.gruppe,
    }
    return eintrag


def _tabelle_dict(block: TabellenBlock, tiefe: int) -> dict:
    return {
        "art": "tabelle",
        "titel": block.titel,
        "kopf": [zelle_dict(z) for z in block.kopf],
        "zeilen": [[zelle_dict(z) for z in zeile] for zeile in block.zeilen],
        "ausrichtung": block.ausrichtung,
        "latex": block.als_latex(),
        "markdown": block_markdown(block),
    }


def _hinweis_dict(block: HinweisBlock, tiefe: int) -> dict:
    return {
        "art": "hinweis",
        "text": block.text,
        "hinweisart": block.art.value,
        "beschriftung": block.art.beschriftung,
    }


def _unterprotokoll_dict(block: UnterprotokollBlock, tiefe: int) -> dict:
    return {
        "art": "unterprotokoll",
        "titel": block.titel,
        "bloecke": darstellen(block.protokoll, TAFEL, tiefe + 1),
    }


#: Je Blockart, wie die Oberflaeche sie bekommt -- jede als JSON-Objekt.
TAFEL: Tafel[dict] = {
    TitelBlock: _titel_dict,
    TextBlock: _text_dict,
    GleichungBlock: _gleichung_dict,
    TabellenBlock: _tabelle_dict,
    HinweisBlock: _hinweis_dict,
    UnterprotokollBlock: _unterprotokoll_dict,
}


def zelle_dict(zelle: Zelle) -> dict:
    """
    Eine Tabellenzelle fuer die Oberflaeche: ``{"text": ...}`` oder
    ``{"mathe": ...}``. Die Oberflaeche setzt nur Formeln mit KaTeX -- Text
    aus LaTeX zurueckzulesen, wie sie es frueher musste, entfaellt.
    """
    if isinstance(zelle, Mathe):
        return {"mathe": zelle.latex}
    return {"text": zelle}


def protokoll_liste(protokoll: Protokoll) -> List[dict]:
    return darstellen(protokoll, TAFEL)


def formelsammlung_liste(themen: List[Thema]) -> List[dict]:
    """
    Je Thema die Bloecke wie im Bericht, als Bloecke derselben Tafel -- und
    der Bestandteil, zu dem es gehoert: danach grenzt die Oberflaeche ein.
    """
    return [
        {"thema": thema.name, "art": thema.art,
         "bloecke": [TAFEL[type(b)](b, 0) for b in thema.bloecke]}
        for thema in themen
    ]


# ===========================================================================
# Loesung
# ===========================================================================


def loesung_dict(loesung: Loesung, aufbau: Optional[Aufbau] = None) -> dict:
    """Vollstaendige Abbildung eines Rechenlaufs."""
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
    }
    if aufbau is not None:
        ergebnis["linien"] = diagrammdaten.linien(aufbau)
        ergebnis["werkstoffgesetze"] = diagrammdaten.werkstoffgesetze(aufbau, loesung)
        ergebnis["querkraftkurven"] = diagrammdaten.querkraftkurven(aufbau)
        ergebnis["neigungskurven"] = diagrammdaten.neigungskurven(aufbau)
        ergebnis["spannungsanalysen"] = diagrammdaten.spannungsanalysen(aufbau, loesung)
        ergebnis["zusammenfassungen"] = zusammenfassungen(loesung, aufbau)
        ergebnis["warnungen"] = list(aufbau.warnungen)
        ergebnis["zuordnung"] = zuordnung(aufbau)
        # Je Blatt und Zeile, was neben der Zeile steht -- gesetzt vom Kern.
        ergebnis["gleichungen"] = {
            kennung: [{"ergebnis": r.ergebnis, "fehler": r.fehler}
                      for r in blatt.ergebnisse]
            for kennung, blatt in aufbau.blaetter.items()
        }
    return ergebnis


def zusammenfassungen(loesung: Loesung, aufbau: Aufbau) -> dict:
    """
    Je Platte die Nachweistabelle -- Zeilen **und** ihr LaTeX.

    Was darin steht, darueber und darunter, baut
    :mod:`opencivil.bericht.zusammenfassung` -- dieselben Stuecke, die auch
    im Bericht stehen. Hier werden sie nur abgebildet; die Oberflaeche faerbt
    ein, was ``erfuellt`` sagt, und haengt die Begruendung als Tooltip an die
    Zeile.
    """
    ergebnis: Dict[str, Any] = {}
    for platte in zusammenfassen(aufbau, loesung).platten:
        # Eine Platte ohne jedes Urteil bekommt keine Tabelle -- die
        # Oberflaeche zeigt dafuer ihren eigenen Leerzustand, der Bericht
        # «Kein Nachweis geführt».
        if platte.leer:
            continue
        qs = aufbau.querschnitte[platte.kennung]
        tabelle = nachweistabelle(platte)
        ergebnis[platte.kennung] = {
            "kopf": [zelle_dict(k) for k in tabelle.kopf],
            "zeilen": [
                {
                    "zellen": [zelle_dict(c) for c in zellen],
                    "erfuellt": z.urteil.erfuellt,
                    "begruendung": z.urteil.begruendung,
                    # Nur was die Pruefung ausdruecklich meldet -- siehe
                    # NachweisUrteil.hinweis.
                    "hinweis": z.urteil.hinweis,
                    # Womit sich genau dieser Nachweis nachrechnen laesst --
                    # und wie er dann heisst.
                    "ziel": z.urteil.ziel,
                    "bezeichnung": z.bezeichnung,
                }
                for z, zellen in zip(platte.zeilen, tabelle.zeilen)
            ],
            "grad_spalte": GRAD_SPALTE,
            "stapel_spalten": list(STAPEL_SPALTEN),
            "ausrichtung": tabelle.ausrichtung,
            "latex": tabelle.als_latex(),
            "markdown": block_markdown(tabelle),
            "hinweise": hinweise(platte),
            "angaben": _gleichung_dict(plattenangaben(qs), 0),
            "bewehrung": _tabelle_dict(bewehrungsuebersicht(qs), 0),
            # Der Grad kommt fertig gesetzt: welche Stelle noetig ist, damit
            # er dem Wort «nicht erfuellt» nicht widerspricht, weiss hier
            # dieselbe Stelle wie fuer die Tabelle.
            "stille": [
                {"nachweis": z.nachweis, "fall": z.fall,
                 "grad": z.urteil.gradtext(), "begruendung": z.urteil.begruendung,
                 "text": stiller_hinweis(z)}
                for z in platte.stille
            ],
        }
    return ergebnis


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
