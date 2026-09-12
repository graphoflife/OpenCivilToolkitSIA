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

from opencivil.core.einheiten import KN, KNM, MM
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
                "erfuellt": u.erfuellt,
                # Einzige Kennzahl: Widerstand/Einwirkung, ab 1 erfuellt.
                "erfuellungsgrad": u.erfuellungsgrad.formatiert(2),
                "erfuellungsgrad_zahl": u.erfuellungsgrad.si,
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
        ergebnis["werkstoffgesetze"] = werkstoffgesetze(aufbau, loesung)
        ergebnis["warnungen"] = list(aufbau.warnungen)
        ergebnis["zuordnung"] = zuordnung(aufbau)
    return ergebnis


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


def _linie_dict(nachweis) -> dict:
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
