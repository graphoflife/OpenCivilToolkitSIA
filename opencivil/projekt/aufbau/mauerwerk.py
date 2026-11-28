"""
opencivil/projekt/aufbau/mauerwerk.py -- eine Mauerwerkswand wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.mauerwerk.MauerwerkEintrag` die Wand
in SI samt ihren Lasten (:func:`wand_von`) und das Bauteil im Rechenwerk mit
seinen Nachweisen (:func:`bauen`). Ohne Mauerwerk rechnet die Wand nicht,
und der Hinweis sagt es (:meth:`~opencivil.projekt.aufbau.kern.Aufbau.unfertig`);
was ihrer Zeichnung fehlt -- ein Knoten, auf den etwas zeigt --, steht in
ihren Meldungen, und der Rest des Projekts rechnet. Die Regeln der
Lastfälle teilt sie mit Balkensystem und Decke
(:mod:`opencivil.projekt.aufbau.faelle`).

DIE NACHWEISE:
Je Pfeiler und Kombination die Normalkraft, je Sturzauflager und
Kombination die Teilflächenpressung (:mod:`opencivil.mauerwerk.nachweise`).
Wo sie stehen, hängt nur an der Zeichnung; darum werden sie hier gebaut,
sobald die Zeichnung rechnet. Sonst sagt die Zusammenfassung, warum es noch
keinen Nachweis gibt.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Sequence, Tuple

from opencivil.decke.geometrie import Punkt
from opencivil.mauerwerk.lasten import SEITEN
from opencivil.mauerwerk.modell import (
    TOLERANZ, Kombination, Lastfall, Oeffnung, Umriss, Wand, Wandlast, pfeiler,
)
from opencivil.mauerwerk.nachweise import Normalkraft, Stelle, Teilflaechen
from opencivil.mauerwerk.pruefen import lasten_pruefen, pruefen
from opencivil.mauerwerk.werk import VORGABEN, Mauerwerkswand
from opencivil.projekt.lesen import als_groesse, ort_von
from opencivil.projekt.mauerwerk import MauerwerkEintrag, WandlinienlastEintrag
from opencivil.stabwerk.system import Meldung

from opencivil.projekt.aufbau.faelle import (
    beiwerte, doppelte_kennungen, faelle_pruefen, ohne_lastfall,
)
from opencivil.projekt.aufbau.kern import Aufbau, Bauteil, material

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart

#: Warum eine Wand keinen Nachweis führt: ihre Zeichnung rechnet nicht, oder es fehlt
#: eine Kombination.
OHNE_WAND = "noch keine Wand – ihren Umriss im Zeichenfenster zeichnen"
FALSCH_GEZEICHNET = "an der Zeichnung stimmt etwas nicht – siehe die Meldungen der Wand"
OHNE_KOMBINATION = "noch keine Kombination – unter «Lastkombinationen» eine anlegen"


def wand_von(eintrag: MauerwerkEintrag) -> Tuple[Wand, List[Meldung]]:
    """
    Die Wand der Beschreibung in SI: Masse in m, Lasten in N. Ein Teil, das
    auf einen Knoten zeigt, den es nicht gibt, fehlt in der Wand; die Meldung
    sagt es. Eine Last heisst nach ihrer Kennung; eine, deren Lastfall es
    nicht gibt, und ein Beiwert dafür bleiben mit einem Hinweis weg.
    """
    lagen = eintrag.lagen()
    meldungen = faelle_pruefen(eintrag.lastfaelle, eintrag.kombinationen)
    for was, liste in (("Knoten", eintrag.knoten), ("Wände", eintrag.waende),
                       ("Öffnungen", eintrag.oeffnungen),
                       ("Lasten", [*eintrag.linienlasten, *eintrag.punktlasten]),
                       ("Lastfälle", eintrag.lastfaelle), ("Kombinationen", eintrag.kombinationen)):
        meldungen.extend(doppelte_kennungen(was, liste))

    def orte(teil, knoten: Sequence[str]) -> Optional[Tuple[Punkt, ...]]:
        fehlt = [k for k in knoten if k not in lagen]
        if fehlt:
            meldungen.append(Meldung(f"{teil.kennung} zeigt auf {', '.join(fehlt)} – einen solchen "
                                     f"Knoten gibt es nicht.", (teil.kennung,)))
            return None
        return tuple(lagen[k] for k in knoten)

    def linie(l: WandlinienlastEintrag) -> Optional[Wandlast]:
        ab = orte(l, (l.von, l.bis))
        if ab is None:
            return None
        (xa, ya), (xb, yb) = ab
        if abs(ya - yb) > TOLERANZ:
            meldungen.append(Meldung(f"Die Linienlast {l.kennung} liegt nicht waagrecht – das "
                                     f"Werkzeug rechnet nur waagrechte.", (l.kennung,)))
            return None
        if abs(xb - xa) <= TOLERANZ:
            meldungen.append(Meldung(f"Die Linienlast {l.kennung} hat keine Länge.", (l.kennung,)))
            return None
        return Wandlast(l.kennung, min(xa, xb), max(xa, xb), ya, l.si("wert") * abs(xb - xa),
                        l.si("e"))

    lasten = [(l.kennung, l.lastfall, last) for l in eintrag.linienlasten
              if (last := linie(l)) is not None]
    lasten += [(q.kennung, q.lastfall, Wandlast(q.kennung, ort[0][0], ort[0][0], ort[0][1],
                                                q.si("wert"), q.si("e")))
               for q in eintrag.punktlasten if (ort := orte(q, (q.knoten,))) is not None]
    je_fall = {lf.kennung: [] for lf in eintrag.lastfaelle}
    for kennung, lastfall, last in lasten:
        if lastfall in je_fall:
            je_fall[lastfall].append(last)
        else:
            meldungen.append(ohne_lastfall(kennung))
    faktoren, hinweise = beiwerte(eintrag.kombinationen, eintrag.lastfaelle)
    meldungen.extend(hinweise)
    wand = Wand(
        umrisse=tuple(Umriss(w.kennung, ecken) for w in eintrag.waende
                      if (ecken := orte(w, w.knoten)) is not None),
        oeffnungen=tuple(Oeffnung(o.kennung, ecken, sturz=o.sturz, h_St=o.si("h_St"), a=o.si("a"))
                         for o in eintrag.oeffnungen if (ecken := orte(o, o.knoten)) is not None),
        mauerung=eintrag.mauerung, stossfugen=eintrag.stossfugen,
        kopf=eintrag.kopf, fuss=eintrag.fuss, links=eintrag.links, rechts=eintrag.rechts,
        lastfaelle=tuple(Lastfall(lf.name, tuple(je_fall[lf.kennung]), lf.eigengewicht)
                         for lf in eintrag.lastfaelle),
        kombinationen=tuple(Kombination(name, f) for name, f in faktoren))
    return wand, meldungen


def bauen(art: "Bauteilart", eintrag: MauerwerkEintrag, aufbau: Aufbau) -> Bauteil:
    """
    Eine Wand: Mauerwerk, Zeichnung und Lasten, angemeldet im Rechenwerk --
    mit ihren Nachweisen, sobald ihre Zeichnung rechnet und sie eine
    Kombination hat.
    """
    wo = ort_von(eintrag)
    stoff = material(aufbau.baustoffe, eintrag.material, "mauerwerk", wo, "Mauerwerk")
    wand, meldungen = wand_von(eintrag)
    objekt = Mauerwerkswand(
        name=eintrag.name, kennung=eintrag.kennung, praefix=f"{art.raum}.{eintrag.kennung}",
        wand=wand, mauerwerk=stoff, meldungen=meldungen,
        vorgaben={f.kurz: als_groesse(eintrag, f.kurz) for g in VORGABEN for f in g.fuer(eintrag)})
    objekt.ins_rechenwerk(aufbau.werk)
    teil = Bauteil(eintrag, art, objekt, weitere_ziele=objekt.ziele())
    zeichnung = meldungen + pruefen(wand)
    if wand.flaeche is None and not any(m.fehler for m in zeichnung):
        aufbau.ohne_nachweis(teil, wo, OHNE_WAND)
    elif any(m.haelt_an for m in zeichnung + lasten_pruefen(wand)):
        aufbau.ohne_nachweis(teil, wo, FALSCH_GEZEICHNET)
    elif not wand.kombinationen:
        aufbau.ohne_nachweis(teil, wo, OHNE_KOMBINATION)
    else:
        _nachweise(teil, objekt, wand, aufbau)
    return teil


def _nachweise(teil: Bauteil, objekt: Mauerwerkswand, wand: Wand, aufbau: Aufbau) -> None:
    """Je Pfeiler und Kombination die Normalkraft, je Sturzauflager die Teilflächen."""
    kennung, namen = teil.eintrag.kennung, [k.name for k in wand.kombinationen]
    aufbau.eintragen(teil, "mw_normalkraft", kennung, Normalkraft(
        objekt, [Stelle(pf.name, k) for pf in pfeiler(wand.flaeche, wand.oeffnungen)
                 for k in namen]))
    auflager = [f"{o.name} {s}" for o in wand.oeffnungen for s in SEITEN]
    if auflager:
        aufbau.eintragen(teil, "mw_teilflaechen", kennung, Teilflaechen(
            objekt, [Stelle(ort, k) for ort in auflager for k in namen]))
