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
    Stahlpilz und Durchstanzbewehrung dazu, was sie sind und was sie tragen.
    Ohne Einwirkung nur der Schnitt: ψ = 0 und k_r = 2 gälten nur ohne Last;
    was die Stelle trägt, sagt die Kennzahl (:mod:`.kennzahl`). Bis 2026-11-27
    stand dort V_Rd,c = 866.7 kN, wo die Kennzahl 503.6 kN sagt.
    """
    def zeile(text: str, zeichen: str, wert: str, einheit: str) -> list:
        return [text, Mathe(zeichen), Mathe(wert), einheit]

    def kraft(x: float) -> str:
        return f"{x / 1e3:.1f}"

    innen = befund.innen
    zeilen = [
        zeile("Wirksame statische Höhe", "d_v", f"{innen.d_v * 1e3:.0f}", "mm"),
        zeile("Nachweisschnitt, wirksam", "u", f"{innen.u * 1e3:.0f}", "mm"),
        zeile("Momentenübertragung", "k_e", f"{innen.k_e:.3f}", "–"),
    ]
    if not befund.ohne_einwirkung:
        zeilen += [
            zeile("Plattenrotation", r"\psi", f"{befund.psi:.4f}", "–"),
            zeile("Beiwert", "k_r", f"{befund.k_r:.3f}", "–"),
            zeile("Querkraft im Schnitt", "V_d", kraft(innen.V_d_red), "kN"),
            zeile("Widerstand ohne Durchstanzbewehrung", "V_{Rd,c}", kraft(befund.V_Rd_c), "kN"),
        ]
        for x in befund.stufen:
            if x.V_Rd_c is None:
                continue
            b = x.stufe.bereich
            zeilen += [
                zeile(f"Querkraft an der Stufe von {b.titel}", f"V_{{d,{b.name}}}",
                      kraft(x.stufe.pruefung.V_d_red), "kN"),
                zeile(f"Widerstand an der Stufe von {b.titel}", f"V_{{Rd,c,{b.name}}}",
                      kraft(x.V_Rd_c), "kN"),
            ]
        if befund.weg is not None:
            zeilen += [
                zeile(f"Querkraft im Schnitt {weg.NAME}", "V_{d,W}",
                      kraft(befund.weg.schnitt.last.V_d_red), "kN"),
                zeile(f"Widerstand am Schnitt {weg.NAME}", "V_{Rd,c,W}",
                      kraft(befund.weg.V_Rd_c), "kN"),
            ]
    pilz, leisten = befund.pilz, befund.leisten
    if pilz is not None:
        zeilen += [
            ["Stahlpilz", "", pilz.pilz.name, ""],
            zeile("Querkraft um den Stahlpilz", "V_{d,P}", kraft(pilz.pruefung.V_d_red), "kN"),
            zeile("Widerstand um den Stahlpilz", "V_{Rd,c,P}", kraft(pilz.V_Rd_c), "kN"),
        ]
    if leisten is not None:
        v = leisten.vorschlag
        zeilen += [
            ["Durchstanzbewehrung", "", v.name, ""],
            zeile("Abstände ab Stütze" if pilz is None else "Abstände ab Pilz", "s",
                  " / ".join(f"{a * 1e3:.0f}" for a in v.abstaende), "mm"),
            zeile("Beitrag der Bewehrung", "V_{Rd,s}", kraft(leisten.V_Rd_s), "kN"),
            zeile("Erste Betondruckdiagonale", "V_{Rd,max}", kraft(leisten.V_Rd_max), "kN"),
            zeile("Querkraft ausserhalb", "V_{d,out}", kraft(leisten.aussen.V_d_red), "kN"),
            zeile("Widerstand ausserhalb", "V_{Rd,c,out}", kraft(leisten.V_Rd_c_aussen), "kN"),
        ]
    return TabellenBlock(kopf=["Grösse", "Zeichen", "Wert", "Einheit"], zeilen=zeilen,
                         titel="Durchstanzen", ausrichtung="llrl")
