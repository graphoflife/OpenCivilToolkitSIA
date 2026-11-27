"""
opencivil/web/zeichengeometrie.py -- die Zeichnung einer Querschnittsanalyse, wie der Kern sie sieht.

VERANTWORTUNG:
Was das Zeichenfenster einer Querschnittsanalyse vom Kern ueber ihre
Zeichnung erfaehrt (Anfrage ``geometrie``): jede Meldung am Element, das sie
betrifft, die Staebe einer Linie mit ihrer tatsaechlichen Teilung, die
Lage in der Ueberdeckung, der Schwerpunkt, die Zellen der Schubwaende, je
Spannglied seine Werte, je Stahlprofil sein Umriss und je
Blechverbunddecke ihr Beton und ihr Blech. Gerechnet wird nur Geometrie --
und die Spannkraft, aus derselben Herleitung wie im Bericht.
Schnell genug fuer jede Aenderung.

Bis 2026-11-26 stand das in :mod:`opencivil.web.api`; mit den Spanngliedern
waere die Datei ueber tausend Zeilen gewachsen.

EINHEITEN:
Wie die Zeichnung: Lagen und Masse in mm, Flaechen in mm², Spannungen in
N/mm², die Vordehnung in Promille, Kraefte in kN.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Mapping, NamedTuple, Optional, Sequence, Tuple

from opencivil.core.protokoll import Abschnitt
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.basis import Baustoff, Baustoffart
from opencivil.material.spannstahl import erzeugnis
from opencivil.projekt.aufbau.kern import baustoff_im_werk, materialgrund
from opencivil.projekt.aufbau.querschnittsanalyse import (
    erzeugnis_grund, ohne_analysen, ohne_nachweise,
)
from opencivil.projekt.blechdecken import BlechdeckeEintrag
from opencivil.projekt.lesen import stoffe_des_felds
from opencivil.projekt.querschnittsanalyse import (
    SchubwandEintrag, StabEintrag, StablinieEintrag,
)
from opencivil.projekt.spannglieder import SpanngliedEintrag
from opencivil.stahlprofile import lage as profillage
from opencivil.querschnitt.analyse import Zeichnung
from opencivil.querschnitt.bauweise import BEWEHRT, Mischung, bauweise
from opencivil.querschnitt.profilblech import rippenskizze
from opencivil.querschnitt.geometrie import (
    Linienart, aequivalenter_durchmesser, buegelgehalt, flaeche, linie_in_ueberdeckung,
    linienflaeche, stab_in_ueberdeckung, ueberdeckungspolygon,
)
from opencivil.querschnitt.spannglieder import (
    Spannglied, Spannglieder, aus_glied, geneigt, grenzen_verletzt, lotrecht,
)
from opencivil.stahlbau import stabilitaet


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
    fehlt: ein geloeschter Stahl ist zu ersetzen, kein Widerspruch. Sind die
    Materialien zusammen keine Bauweise (:func:`bauweise`), sagt es eine
    Meldung ohne Element, grau.

    ``bauweise`` ist die Bauweise (:class:`~opencivil.querschnitt.bauweise.Bauweise`),
    leer ohne. ``ohne_nachweise`` ist der Satz, warum ein Querschnitt dieser
    Bauweise keinen Nachweis hat -- leer beim Stahlbeton, beim Stahl und ohne
    Bauweise --, ``ohne_analysen`` derselbe fuer die
    Spannung-Dehnung-Analysen, leer ausser im Verbund und in der
    Blechverbunddecke. Danach zeigt die
    Analyse ihre Kacheln (:func:`ohne_nachweise`, :func:`ohne_analysen`).
    ``knickkurven`` sagt je Achse die Knickspannungskurve, die Figur 7 dem
    einzigen Profil des Querschnitts zuweist, ``knickkurven_fehlen``, welche
    einem Stabilitaetsnachweis fehlt (:func:`_knickkurven`).
    ``laengsschub_fehlt`` sagt fuer die Kachel «Längsschub» einer
    Blechverbunddecke, was ihm noch fehlt, «m und k fehlen» -- leer, wo
    nichts fehlt oder keine Decke gezeichnet ist
    (:attr:`~opencivil.verbund.blechdecke.Laengsschub.fehlt_kurz`).

    ``gueltig`` heisst: die Zeichnung rechnet. Eine Spannung ueber der
    Grenze der Norm steht rot am Glied, haelt die Rechnung aber nicht an --
    gerechnet wird mit den Zahlen des Benutzers.
    """
    stoffe = {m.kennung: (m.art, m.anzeigename) for m in projekt.materialien}
    elemente = eintrag.elemente()
    flaechen = elemente.flaechen
    vorab: List[dict] = [{**m, "fehler": True} for m in elemente.fehler]
    passend: List[Tuple[str, str]] = []

    def stoff_pruefen(e: dict, kennung: str, arten: Sequence[str]) -> None:
        gefunden = stoffe.get(kennung)
        grund = materialgrund(kennung, gefunden, arten)
        if grund:
            vorab.append({"text": f"{e['name']}: {grund.text}.", "elemente": [e["kennung"]],
                          "fehler": grund.falsch})
        else:
            passend.append(gefunden)

    # Der Beton einer Blechverbunddecke ist eine Flaeche wie jede, ihr Blech
    # meldet sich unter seinem eigenen Namen: «Blechverbunddecke 1, Blech».
    for f in flaechen:
        if not f["aussparung"]:
            stoff_pruefen(f, f["material"], f["stoffe"])
    for d in elemente.blechdecken:
        stoff_pruefen({**d, "name": d["namen"]["blech"]}, d["blech"],
                      stoffe_des_felds(BlechdeckeEintrag, "blech"))
    for klasse, liste in ((StabEintrag, elemente.staebe), (StablinieEintrag, elemente.linien),
                          (SchubwandEintrag, elemente.waende),
                          (SpanngliedEintrag, elemente.spannglieder)):
        for e in liste:
            stoff_pruefen(e, e["stahl"], stoffe_des_felds(klasse, "stahl"))
    try:
        art = bauweise(passend)
    except Mischung as mischung:
        art = None
        vorab.append({"text": str(mischung), "elemente": [], "fehler": False})
    glieder = _spannglieder(elemente.spannglieder, projekt)
    vorab.extend(glieder.fehlt)
    # Ohne Erzeugnis zeichnet sich ein Glied in seinem Nenndurchmesser.
    gross = {g["kennung"]: (glieder.gebaut[g["kennung"]].durchmesser
                            if g["kennung"] in glieder.gebaut else g["durchmesser"])
             for g in elemente.spannglieder}
    # Bewehrung liegt nur im Beton -- nicht in Holz, nicht in Baustahl, nicht
    # in einer Aussparung. Ein Material, das fehlt oder nicht passt, meldet
    # sich selbst; bis es ersetzt ist, gilt seine Flaeche als Beton, wenn sie
    # Beton sein darf -- sonst kaeme zu seiner Meldung eine an jedem Stab in
    # ihr. Ein Profil ist nie Beton.
    def im_beton(f: Mapping) -> bool:
        if f["aussparung"] or BEWEHRT.value not in f["stoffe"]:
            return False
        return stoffe.get(f["material"], ("",))[0] not in set(f["stoffe"]) - {BEWEHRT.value}

    beton = [im_beton(f) for f in flaechen]
    z = Zeichnung(
        polygone=[{**f, "traegt": not f["aussparung"], "beton": b}
                  for f, b in zip(flaechen, beton)],
        staebe=elemente.staebe, linien=elemente.linien, waende=elemente.waende,
        spannglieder=[{**g, "durchmesser": gross[g["kennung"]]} for g in elemente.spannglieder])
    # Die Ueberdeckung, eine Hilfe beim Zeichnen: je Polygon das gerueckte,
    # je Stab, Stablinie und Spannglied, wo sie in ihr laegen -- fuer den
    # Knopf «Überdeckung beachten». Ohne Ueberdeckung jeweils nichts. Fuer die
    # Bewehrung ist jede Flaeche ohne Beton wie eine Aussparung: von ihrem
    # Rand haelt sie Abstand, etwa im Verbund vom Stahlprofil.
    punkte = [f["punkte"] for f in flaechen]
    c = [f["ueberdeckung"] for f in flaechen]
    tiefe = _tiefen(z.eltern, [f["kennung"] for f in flaechen])

    def als_punkt(p):
        return None if p is None else list(p)

    def als_liste(punkte):
        return None if punkte is None else [list(p) for p in punkte]

    def punkt_ueberdeckt(lage, durchmesser):
        return als_punkt(stab_in_ueberdeckung(lage, durchmesser / 2.0, punkte, beton, c))

    def linie_ueberdeckt(l):
        # Verschmiert mit der Flaeche von Hand: Staebe mit 150 mm Teilung;
        # aus ⌀ und Teilung: dieser ⌀ (Benutzer, 2026-10-24).
        if l["art"] == Linienart.FLAECHE and l["verschmiert"] != "staebe":
            def radius(laenge):
                return aequivalenter_durchmesser(l["flaeche"], laenge) / 2.0
        else:
            def radius(_laenge):
                return l["durchmesser"] / 2.0
        return als_liste(linie_in_ueberdeckung(l["von"], l["bis"], radius, punkte, beton, c))

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
            {"element": f["name"], "kennung": f["kennung"], "tiefe": tiefe.get(f["kennung"], 0),
             "aussparung": not z.traegt[i],
             "ueberdeckung": (als_liste(ueberdeckungspolygon(f["punkte"], c[i], beton[i]))
                              if c[i] > 0.0 else None)}
            for i, f in enumerate(elemente.polygone)],
        "profile": [_profil(p, tiefe.get(p["kennung"], 0)) for p in elemente.profile],
        "blechdecken": [_blechdecke(d, tiefe.get(d["kennung"], 0)) for d in elemente.blechdecken],
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
        "bauweise": art.value if art is not None else "",
        "ohne_nachweise": _als_satz(ohne_nachweise(art, passend)) if art is not None else "",
        "ohne_analysen": ohne_analysen(art) if art is not None else "",
        **_knickkurven(eintrag, flaechen, b),
        "laengsschub_fehlt": eintrag.laengsschub.fehlt_kurz if elemente.blechdecken else "",
    }


def _knickkurven(eintrag, flaechen: Sequence[Mapping], brutto) -> Dict[str, Any]:
    """
    ``knickkurven``: je Achse die Knickspannungskurve des einzigen Profils,
    ``kurve`` und ``grund`` -- ``None``, wo der Querschnitt nicht aus einem
    einzigen Profil besteht (:func:`~opencivil.stahlbau.stabilitaet.einzelprofil`):
    dann waehlt der Benutzer sie. ``knickkurven_fehlen``: der Satz, welche
    Kurve den Faellen von Knicken und Kippen dann fehlt -- derselbe wie im
    Fall (:func:`~opencivil.stahlbau.stabilitaet.fehlende_kurven`), leer,
    wo keine fehlt.
    """
    if brutto is None:
        return {"knickkurven": None, "knickkurven_fehlen": ""}
    profil = stabilitaet.einzelprofil((f["kennung"], f["profil"]) for f in flaechen)
    I = {"y": brutto.I_y, "z": brutto.I_z}
    eigene = stabilitaet.kurven_des_profils(profil, I) if profil is not None else None
    kurven = stabilitaet.rechenkurven(eintrag.knickkurven, profil, I)
    return {
        "knickkurven": eigene and {a: {"kurve": k, "grund": grund}
                                   for a, (k, grund) in eigene.items()},
        "knickkurven_fehlen": stabilitaet.fehlende_kurven(kurven, eintrag.stabfaelle()),
    }


def _tiefen(eltern: Optional[Sequence[Optional[int]]], kennungen: Sequence[str]) -> Dict[str, int]:
    """
    Wie tief jedes Element verschachtelt ist, je Kennung -- 0 fuer eines, das
    in keinem liegt: so zeichnet das Fenster die aeusseren zuerst. Ein Profil
    zaehlt mit seinem Umriss, nicht mit seinem Loch. Ohne gueltige
    Verschachtelung alle 0.
    """
    tiefen: Dict[str, int] = {}
    for i, kennung in enumerate(kennungen):
        t, j = 0, (eltern[i] if eltern is not None else None)
        while j is not None:
            t, j = t + 1, eltern[j]
        tiefen[kennung] = min(t, tiefen.get(kennung, t))
    return tiefen


def _profil(p: Mapping, tiefe: int) -> dict:
    """
    Ein Stahlprofil, wie das Fenster es zeichnet: seine Umrisse und die Mitte,
    zu der sie gehoeren -- haengt sie an einem Knoten, der eben verschoben
    wird, schiebt das Fenster das Bild mit, bis die naechste Antwort da ist.
    Dazu, was es ist, seine Flaeche aus dem Umriss, die Masse von aussen und
    die Punkte zum Fangen; ob Drehen und Spiegeln es aendern, sagt, ob das
    Fenster die Schalter dafuer zeigt.
    """
    aussen, *loecher = p["umrisse"]
    ys, zs = [q[0] for q in aussen], [q[1] for q in aussen]
    return {
        "element": p["name"], "kennung": p["kennung"], "tiefe": tiefe,
        "lage": list(p["lage"]), "umriss": [[list(q) for q in teil] for teil in p["umrisse"]],
        "beschreibung": p["beschreibung"],
        "A": abs(flaeche(aussen)) - sum(abs(flaeche(l)) for l in loecher),
        "breite": max(ys) - min(ys), "hoehe": max(zs) - min(zs),
        "fang": [list(q) for q in profillage.fangpunkte(p["umrisse"])],
        "drehbar": profillage.drehbar(p["profil"]),
        "spiegelbar": profillage.spiegelbar(p["profil"]),
    }


def _blechdecke(d: Mapping, tiefe: int) -> dict:
    """
    Eine Blechverbunddecke, wie das Fenster sie zeichnet: der Umriss ihres
    Betons und die Linie ihres Blechs zur Ecke links unten, an der sie haengt
    -- wie beim Profil schiebt das Fenster beides mit dem Knoten mit, bis die
    naechste Antwort da ist. Gefangen wird an jeder Ecke des Betons. Dazu,
    was aus den Massen folgt, aus derselben Form wie in der Herleitung
    (:class:`~opencivil.querschnitt.profilblech.Blechform`): die Breite ``b``,
    die Dicke ``t`` des Blechs, sein Schwerpunkt ``e`` ueber der Unterkante,
    ``d_p``, ``b_0`` und die Flaeche ``A`` des Blechs ueber die ganze Breite.
    Und eine Rippe mit ihren Massen als Bild: es sagt im Fenster, was die
    Zeichen der Felder meinen (:func:`~opencivil.querschnitt.profilblech.rippenskizze`).
    """
    f = d["form"]
    beton = [list(p) for p in f.beton]
    return {
        "element": d["name"], "kennung": d["kennung"], "tiefe": tiefe, "lage": list(d["lage"]),
        "umriss": [beton], "blech": [list(p) for p in f.linie], "fang": beton,
        "hinterschnitten": f.hinterschnitten,
        "werte": {"b": f.breite, "t": f.t, "e": f.e, "d_p": f.d_p, "b_0": f.b_0, "A": f.flaeche},
        "rippe": rippenskizze(f).als_dict(),
    }


def _als_satz(teil: str) -> str:
    """Ein Satzteil als Satz: gross beginnend, mit Punkt -- leer bleibt leer."""
    return f"{teil[0].upper()}{teil[1:]}." if teil else ""


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
        if geneigt(g):
            # Was es von einem gleich gerichteten V_z traegt (Gleichung (50)).
            werte[kennung]["V_p"] = lotrecht(je["P_inf"], g.neigung)
    return _Glieder(glieder, werte, fehlt, grenzen)
