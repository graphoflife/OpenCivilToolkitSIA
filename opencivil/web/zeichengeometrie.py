"""
opencivil/web/zeichengeometrie.py -- die Zeichnung einer Querschnittsanalyse, wie der Kern sie sieht.

VERANTWORTUNG:
Was das Zeichenfenster einer Querschnittsanalyse vom Kern ueber ihre
Zeichnung erfaehrt (Anfrage ``geometrie``): jede Meldung am Element, das sie
betrifft, die Staebe einer Linie mit ihrer tatsaechlichen Teilung, die
Lage in der Ueberdeckung, der Schwerpunkt, die Zellen der Schubwaende und je
Spannglied seine Werte. Gerechnet wird nur Geometrie -- und die Spannkraft,
aus derselben Herleitung wie im Bericht. Schnell genug fuer jede Aenderung.

Bis 2026-11-26 stand das in :mod:`opencivil.web.api`; mit den Spanngliedern
waere die Datei ueber tausend Zeilen gewachsen.

EINHEITEN:
Wie die Zeichnung: Lagen und Masse in mm, Flaechen in mm², Spannungen in
N/mm², die Vordehnung in Promille, Kraefte in kN.
"""

from __future__ import annotations

import math
from typing import Dict, List, Mapping, NamedTuple, Optional, Sequence

from opencivil.core.protokoll import Abschnitt
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.basis import Baustoff, Baustoffart
from opencivil.material.spannstahl import erzeugnis
from opencivil.projekt.aufbau.kern import baustoff_im_werk, materialgrund
from opencivil.projekt.aufbau.querschnittsanalyse import erzeugnis_grund
from opencivil.querschnitt.analyse import Zeichnung
from opencivil.querschnitt.geometrie import (
    Linienart, aequivalenter_durchmesser, buegelgehalt, linie_in_ueberdeckung, linienflaeche,
    stab_in_ueberdeckung, ueberdeckungspolygon,
)
from opencivil.querschnitt.spannglieder import Spannglied, Spannglieder, aus_glied, grenzen_verletzt


def geometrie(eintrag, projekt) -> dict:
    """
    Die Zeichnung einer Querschnittsanalyse, wie der Kern sie sieht -- in mm.

    Geprueft von :class:`~opencivil.querschnitt.analyse.Zeichnung`, denselben
    Pruefungen, die das Bauteil vor dem Rechnen macht; hier aber alle
    Meldungen auf einmal statt nur der ersten. Die Wahl der Materialien kommt
    dazu, nach derselben Regel wie beim Bauen (:func:`materialgrund`) -- das
    kann nur das Projekt wissen. Ebenso ein Verweis auf einen Knoten, den es
    nicht gibt, und ein Spannglied, dessen Durchmesser es in seiner Sorte
    nicht gibt. ``fehler`` sagt je Meldung, ob etwas nicht stimmt oder nur
    fehlt: ein geloeschter Stahl ist zu ersetzen, kein Widerspruch.

    ``gueltig`` heisst: die Zeichnung rechnet. Eine Spannung ueber der
    Grenze der Norm steht rot am Glied, haelt die Rechnung aber nicht an --
    gerechnet wird mit den Zahlen des Benutzers.
    """
    stoffe = {m.kennung: (m.art, m.anzeigename) for m in projekt.materialien}
    elemente = eintrag.elemente()
    vorab: List[dict] = [{**m, "fehler": True} for m in elemente.fehler]

    def stoff_pruefen(e: dict, feld: str, art: str) -> None:
        gefunden = stoffe.get(e[feld])
        grund = materialgrund(e[feld], gefunden, art)
        if grund:
            vorab.append({"text": f"{e['name']}: {grund.text}.", "elemente": [e["kennung"]],
                          "fehler": grund.falsch})

    for f in elemente.polygone:
        if f["material"]:  # ohne Material eine Aussparung
            stoff_pruefen(f, "material", "beton")
    for e in (*elemente.staebe, *elemente.linien, *elemente.waende):
        stoff_pruefen(e, "stahl", "betonstahl")
    for g in elemente.spannglieder:
        stoff_pruefen(g, "stahl", "spannstahl")
    glieder = _spannglieder(elemente.spannglieder, projekt)
    vorab.extend(glieder.fehlt)
    # Ohne Erzeugnis zeichnet sich ein Glied in seinem Nenndurchmesser.
    gross = {g["kennung"]: (glieder.gebaut[g["kennung"]].durchmesser
                            if g["kennung"] in glieder.gebaut else g["durchmesser"])
             for g in elemente.spannglieder}
    z = Zeichnung(
        polygone=[{**f, "traegt": bool(f["material"])} for f in elemente.polygone],
        staebe=elemente.staebe, linien=elemente.linien, waende=elemente.waende,
        spannglieder=[{**g, "durchmesser": gross[g["kennung"]]} for g in elemente.spannglieder])
    # Die Ueberdeckung, eine Hilfe beim Zeichnen: je Polygon das gerueckte,
    # je Stab, Stablinie und Spannglied, wo sie in ihr laegen -- fuer den
    # Knopf «Überdeckung beachten». Ohne Ueberdeckung jeweils nichts.
    punkte = [f["punkte"] for f in elemente.polygone]
    traegt = [bool(f["material"]) for f in elemente.polygone]
    c = [f["ueberdeckung"] for f in elemente.polygone]

    def als_punkt(p):
        return None if p is None else list(p)

    def als_liste(punkte):
        return None if punkte is None else [list(p) for p in punkte]

    def punkt_ueberdeckt(lage, durchmesser):
        return als_punkt(stab_in_ueberdeckung(lage, durchmesser / 2.0, punkte, traegt, c))

    def linie_ueberdeckt(l):
        # Verschmiert mit der Flaeche von Hand: Staebe mit 150 mm Teilung;
        # aus ⌀ und Teilung: dieser ⌀ (Benutzer, 2026-10-24).
        if l["art"] == Linienart.FLAECHE and l["verschmiert"] != "staebe":
            def radius(laenge):
                return aequivalenter_durchmesser(l["flaeche"], laenge) / 2.0
        else:
            def radius(_laenge):
                return l["durchmesser"] / 2.0
        return als_liste(linie_in_ueberdeckung(l["von"], l["bis"], radius, punkte, traegt, c))

    linien = []
    for l, linie in zip(elemente.linien, z.linien):
        kopf = {"element": l["name"], "kennung": l["kennung"]}
        if linie is None:
            linien.append({**kopf, "punkte": [], "teilung": None,
                           "felder": 0, "flaeche": 0.0, "je_meter": 0.0, "laenge": 0.0,
                           "ueberdeckt": None})
            continue
        flaeche = linienflaeche(l, linie.laenge, len(linie.punkte))
        linien.append({
            **kopf,
            "punkte": [list(p) for p in linie.punkte],
            "teilung": linie.teilung,
            "gewaehlt": l["teilung"] if l["art"] == "teilung" else None,
            "felder": linie.felder,
            "flaeche": flaeche,
            "je_meter": flaeche / linie.laenge * 1000.0,
            "laenge": linie.laenge,
            "ueberdeckt": linie_ueberdeckt(l),
        })
    b = z.brutto
    return {
        "gueltig": z.gueltig and not vorab,
        "meldungen": vorab + [{"text": m.text, "elemente": list(m.elemente),
                               "fehler": m.fehler} for m in z.meldungen] + glieder.grenzen,
        "polygone": [
            {"element": f["name"], "kennung": f["kennung"],
             "eltern": (z.eltern[i] if z.eltern is not None else None),
             "aussparung": not z.traegt[i],
             "ueberdeckung": (als_liste(ueberdeckungspolygon(f["punkte"], c[i], traegt[i]))
                              if c[i] > 0.0 else None)}
            for i, f in enumerate(elemente.polygone)],
        "brutto": None if b is None else {
            "A": b.A, "y_S": b.y_S, "z_S": b.z_S, "I_y": b.I_y, "I_z": b.I_z,
            "I_yz": b.I_yz},
        "staebe": [{"element": s["name"], "kennung": s["kennung"], "im_beton": gut,
                    "ueberdeckt": punkt_ueberdeckt(s["lage"], s["durchmesser"])}
                   for s, gut in zip(elemente.staebe, z.staebe)],
        "linien": linien,
        "waende": [
            {"element": w["name"], "kennung": w["kennung"], "gut": gut,
             "laenge": math.dist(w["von"], w["bis"]),
             # In mm²/m, wie die Liste ihn zeigt.
             "a_sw_s": buegelgehalt(w["schnitte"], w["durchmesser"], w["teilung"]) * 1000.0}
            for w, gut in zip(elemente.waende, z.waende)],
        # Je Glied, wie gross es sich zeichnet -- ein Kreis mit seiner
        # Flaeche --, und was es traegt: ``werte`` fehlen, solange sein
        # Spannstahl oder sein Erzeugnis fehlt.
        "spannglieder": [
            {"element": g["name"], "kennung": g["kennung"], "im_beton": gut,
             "durchmesser": gross[g["kennung"]],
             "ueberdeckt": punkt_ueberdeckt(g["lage"], gross[g["kennung"]]),
             "werte": glieder.werte.get(g["kennung"])}
            for g, gut in zip(elemente.spannglieder, z.spannglieder)],
        "zellen": [{"punkte": [list(p) for p in ecken], "flaeche": flaeche}
                   for ecken, flaeche in z.zellen],
        "hilfslinien": [{"element": h["name"], "kennung": h["kennung"]}
                        for h in elemente.hilfslinien],
        # Die Materialien, auf die die Zeichnung zeigt -- fuer die Werte je
        # Material jeder Rechenwahl der Analyse und eines Balkensystems, das
        # einen Querschnitt aus ihr nimmt. Bis 2026-10-18 zaehlte die
        # Oberflaeche sie ein zweites Mal.
        "materialien": eintrag.materialien(),
    }


class _Glieder(NamedTuple):
    """Was die Zeichnung von ihren Spanngliedern weiss -- siehe :func:`_spannglieder`."""

    gebaut: Dict[str, Spannglied]
    werte: Dict[str, dict]
    fehlt: List[dict]
    """Grau: das Erzeugnis fehlt noch -- die Zeichnung rechnet nicht."""
    grenzen: List[dict]
    """Rot: eine Spannung jenseits der Grenze der Norm -- gerechnet wird trotzdem."""


def _spannglieder(roh: Sequence[Mapping], projekt) -> _Glieder:
    """
    Die Glieder, die rechnen, je Kennung -- und ihre Werte aus derselben
    Herleitung wie im Bericht (:class:`Spannglieder`), mit den Saetzen dazu,
    was an ihren Spannungen die Norm verletzt (:func:`grenzen_verletzt`).
    Dazu die Meldungen zu denen, deren Durchmesser es in der Sorte nicht
    gibt: grau, wie beim Bauen (:func:`erzeugnis_grund`). Ein falsches oder
    fehlendes Material meldet schon :func:`materialgrund`; ein Material, das
    selbst nicht rechnet, sagt es in seinem Fenster.
    """
    materialien = {m.kennung: m for m in projekt.materialien}
    werk = Rechenwerk()
    stoffe: Dict[str, Optional[Baustoff]] = {}
    glieder: Dict[str, Spannglied] = {}
    fehlt: List[dict] = []
    for g in roh:
        m = materialien.get(g["stahl"])
        if m is None or m.art != Baustoffart.SPANNSTAHL:
            continue
        if m.kennung not in stoffe:
            stoffe[m.kennung] = baustoff_im_werk(m, werk)
        stahl = stoffe[m.kennung]
        if stahl is None:
            continue
        gefunden = erzeugnis(stahl.sorte, g["durchmesser"])
        if gefunden is None:
            fehlt.append({"text": f"{g['name']}: "
                                  f"{erzeugnis_grund(stahl.name, stahl.sorte, g['durchmesser'])}.",
                          "elemente": [g["kennung"]], "fehler": False})
            continue
        glieder[g["kennung"]] = aus_glied({**g, "stahl": stahl}, gefunden)
    if not glieder:
        return _Glieder(glieder, {}, fehlt, [])
    herleitung = Spannglieder(list(glieder.values()), basis="zeichnung",
                              abschnitt=Abschnitt("Zeichnung", "zeichnung"))
    werk.registriere(herleitung)
    loesung = werk.loese(herleitung.id)

    def zahl(g: Spannglied, kurz: str) -> float:
        d = herleitung.d[g.kennung][kurz]
        return loesung.groesse(d.id).in_einheit(d.einheit)

    def kennwert(g: Spannglied, kurz: str) -> float:
        return loesung.groesse(g.stahl.id_von(kurz)).in_einheit(g.stahl.definition(kurz).einheit)

    werte, grenzen = {}, []
    for kennung, g in glieder.items():
        je = {kurz: zahl(g, kurz) for kurz in ("A_p", "sigma_p0", "sigma_pinf", "eps_p", "P_inf")}
        grenzen += [{"text": f"{g.name}: {satz}.", "elemente": [kennung], "fehler": True}
                    for satz in grenzen_verletzt(je["sigma_p0"], je["sigma_pinf"],
                                                 kennwert(g, "f_pk"), kennwert(g, "f_p01k"))]
        werte[kennung] = {**je, "erzeugnis": g.erzeugnis.bezeichnung(g.stahl.sorte)}
    return _Glieder(glieder, werte, fehlt, grenzen)
