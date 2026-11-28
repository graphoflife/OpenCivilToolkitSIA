"""
opencivil/durchstanzen/kennwerte.py -- was die Zusammenfassung einer
Durchstanzstelle über ihrer Tabelle und in ihr zeigt.

VERANTWORTUNG:
Die Angaben zur Stelle -- Lage, Platte, Beton und die Masse, wie gerechnet
-- und die Tabelle der Grössen, aus denen der Widerstand entsteht, aus dem
Befund des Nachweises (:class:`.nachweis.Durchstanzbefund`). Bis 2026-11-28
standen beide am Ende von :mod:`.nachweis`; die Datei wurde zu lang.
"""

from __future__ import annotations

from typing import Dict

from opencivil.core.latex import Mathe, als_text, angabe
from opencivil.core.protokoll import GleichungBlock, TabellenBlock
from opencivil.core.wert import Wert
from opencivil.durchstanzen import weg
from opencivil.durchstanzen.nachweis import Durchstanzbefund
from opencivil.durchstanzen.pruefung import Leistenpruefung
from opencivil.durchstanzen.stelle import Durchstanzstelle


def angaben(stelle: Durchstanzstelle, werte: Dict[str, Wert]) -> GleichungBlock:
    """Was über der Tabelle steht: Lage, Platte, Beton und die Masse, wie gerechnet."""
    teile = [als_text(f"{stelle.flaeche.lage.beschriftung}, {stelle.plattenart.beschriftung}, "
                      f"Beton {stelle.beton.name}")]
    teile += [angabe(werte[stelle.id_von(n)]) for n in ("h", *stelle.flaeche.masse)
              if stelle.id_von(n) in werte]
    return GleichungBlock(latex=r" \qquad ".join(teile), titel="Angaben zur Durchstanzstelle")


def kennwerttabelle(befund: Durchstanzbefund) -> TabellenBlock:
    """
    Die Grössen, aus denen der Widerstand entsteht -- eine Zeile je Grösse. Mit
    Stahlpilz und Durchstanzbewehrung dazu, was sie sind und was sie tragen,
    auch die Leisten an den Stufen der Bereiche.
    Ohne Einwirkung nur der Schnitt: ψ = 0 und k_r = 2 gälten nur ohne Last;
    was die Stelle trägt, sagt die Kennzahl (:mod:`.kennzahl`). Bis 2026-11-27
    stand dort V_Rd,c = 866.7 kN, wo die Kennzahl 503.6 kN sagt.
    """
    innen = befund.innen
    zeilen = [
        _zeile("Wirksame statische Höhe", "d_v", f"{innen.d_v * 1e3:.0f}", "mm"),
        _zeile("Nachweisschnitt, wirksam", "u", f"{innen.u * 1e3:.0f}", "mm"),
        _zeile("Momentenübertragung", "k_e", f"{innen.k_e:.3f}", "–"),
    ]
    if not befund.ohne_einwirkung:
        zeilen += [
            _zeile("Plattenrotation", r"\psi", f"{befund.psi:.4f}", "–"),
            _zeile("Beiwert", "k_r", f"{befund.k_r:.3f}", "–"),
            _zeile("Querkraft im Schnitt", "V_d", _kraft(innen.V_d_red), "kN"),
            _zeile("Widerstand ohne Durchstanzbewehrung", "V_{Rd,c}", _kraft(befund.V_Rd_c), "kN"),
        ]
        for x in befund.stufen:
            if x.V_Rd_c is None:
                continue
            b = x.stufe.bereich
            zeilen += [
                _zeile(f"Querkraft an der Stufe von {b.titel}", f"V_{{d,{b.name}}}",
                       _kraft(x.stufe.pruefung.V_d_red), "kN"),
                _zeile(f"Widerstand an der Stufe von {b.titel}", f"V_{{Rd,c,{b.name}}}",
                       _kraft(x.V_Rd_c), "kN"),
            ]
        if befund.weg is not None:
            zeilen += [
                _zeile(f"Querkraft im Schnitt {weg.NAME}", "V_{d,W}",
                       _kraft(befund.weg.schnitt.last.V_d_red), "kN"),
                _zeile(f"Widerstand am Schnitt {weg.NAME}", "V_{Rd,c,W}",
                       _kraft(befund.weg.V_Rd_c), "kN"),
            ]
    pilz, leisten = befund.pilz, befund.leisten
    if pilz is not None:
        zeilen += [
            ["Stahlpilz", "", pilz.pilz.name, ""],
            _zeile("Querkraft um den Stahlpilz", "V_{d,P}", _kraft(pilz.pruefung.V_d_red), "kN"),
            _zeile("Widerstand um den Stahlpilz", "V_{Rd,c,P}", _kraft(pilz.V_Rd_c), "kN"),
        ]
    if leisten is not None:
        zeilen += _leistenzeilen(leisten, "Durchstanzbewehrung",
                                 "Abstände ab Stütze" if pilz is None else "Abstände ab Pilz")
    for x in befund.stufen:
        if x.leisten is not None:
            b = x.stufe.bereich
            zeilen += _leistenzeilen(x.leisten, f"Durchstanzbewehrung an der Stufe von {b.titel}",
                                     "Abstände ab Stufe", f",{b.name}")
    return TabellenBlock(kopf=["Grösse", "Zeichen", "Wert", "Einheit"], zeilen=zeilen,
                         titel="Durchstanzen", ausrichtung="llrl")


def _leistenzeilen(leisten: Leistenpruefung, titel: str, abstaende: str, ix: str = "") -> list:
    """Die Zeilen einer Durchstanzbewehrung -- ``ix`` hängt an den Zeichen, «,B1» an einer Stufe."""
    v = leisten.vorschlag
    return [
        [titel, "", v.name, ""],
        _zeile(abstaende, "s", " / ".join(f"{a * 1e3:.0f}" for a in v.abstaende), "mm"),
        _zeile("Beitrag der Bewehrung", f"V_{{Rd,s{ix}}}", _kraft(leisten.V_Rd_s), "kN"),
        _zeile("Erste Betondruckdiagonale", f"V_{{Rd,max{ix}}}", _kraft(leisten.V_Rd_max), "kN"),
        _zeile("Querkraft ausserhalb", f"V_{{d,out{ix}}}", _kraft(leisten.aussen.V_d_red), "kN"),
        _zeile("Widerstand ausserhalb", f"V_{{Rd,c,out{ix}}}", _kraft(leisten.V_Rd_c_aussen),
               "kN"),
    ]


def _zeile(text: str, zeichen: str, wert: str, einheit: str) -> list:
    """Eine Zeile der Tabelle: Text, Zeichen und Wert als Formel, Einheit."""
    return [text, Mathe(zeichen), Mathe(wert), einheit]


def _kraft(x: float) -> str:
    """Eine Kraft der Tabelle: kN mit einer Stelle."""
    return f"{x / 1e3:.1f}"
