"""
opencivil/mauerwerk/pruefen.py -- was einer Wand fehlt oder an ihr nicht stimmt.

VERANTWORTUNG:
Die Meldungen der Zeichnung einer Wand, in dieser Folge:

- ein Umriss, aus dem sich nicht rechnen lässt -- zu wenig Ecken, sich
  selbst kreuzend, ohne Fläche: rot;
- noch keine Wand: grau; mehr als ein Umriss der Wand, eine Wand oder
  Öffnung, die kein Rechteck mit waagrechten und senkrechten Seiten ist: rot;
- eine Öffnung, die über die Wand hinaus reicht, zwei, die sich
  überschneiden: rot;
- ein Sturz, der über die Wand hinaus oder in eine andere Öffnung reicht,
  zwei Stürze, die sich überschneiden: rot;
- eine unübliche Dicke: ein Hinweis (:func:`dickenhinweis`).

Wo die Lasten liegen, prüft :func:`lasten_pruefen`, sobald die Zeichnung
rechnet: eine Last neben der Wand oder in einer Öffnung ist rot.

Was nur fehlt, steht grau und hält die Rechnung an; was falsch ist, steht
rot (Benutzer, 2026-11-19).

ÜBLICHE DICKEN (nach Vorgabe, nicht nachgeschlagen):
Je Art der Steine die Masse, in denen sie üblich gehandelt werden
(:data:`UEBLICHE_DICKEN`) -- die Norm nennt keine. Eine andere Dicke
rechnet das Werkzeug gleich; der Hinweis sagt nur, dass sie unüblich ist.
"""

from __future__ import annotations

from itertools import combinations
from typing import Dict, List, Optional, Tuple

from opencivil.core.sprache import aufgezaehlt
from opencivil.material.mauerwerk import MAUERWERKSSORTEN
from opencivil.mauerwerk.modell import TOLERANZ, Oeffnung, Rechteck, Umriss, Wand, Wandlast
from opencivil.querschnitt.geometrie import GeometrieFehler, polygon_pruefen
from opencivil.stabwerk.system import Meldung

#: In welchen Dicken die Steine einer Sorte üblich sind, in mm -- siehe Dateikopf.
UEBLICHE_DICKEN: Dict[str, Tuple[int, ...]] = {
    "MB": (100, 125, 150, 175, 200, 250, 300),
    "MBL": (100, 125, 150, 175, 200, 250, 300),
    "MC": (100, 120, 150, 175, 200, 250),
    "MCL": (100, 120, 150, 175, 200, 250),
    "MK": (100, 120, 150, 175, 200, 250),
    "MP": (100, 125, 150, 175, 200, 240, 250, 300, 365),
    "MPL": (100, 125, 150, 175, 200, 240, 250, 300, 365),
}

KEIN_RECHTECK = "ist kein Rechteck mit waagrechten und senkrechten Seiten"


def pruefen(wand: Wand) -> List[Meldung]:
    """Siehe Dateikopf -- leer, wenn sich die Wand rechnen lässt."""
    meldungen = [m for u in (*wand.umrisse, *wand.oeffnungen) if (m := _umriss(u)) is not None]
    if meldungen:
        return meldungen
    if not wand.umrisse:
        return [Meldung("Noch keine Wand – ihren Umriss mit dem Werkzeug «Wand» zeichnen.",
                        fehler=False, unfertig=True)]
    meldungen += [Meldung(f"Eine Wand hat einen Umriss: {u.name} ist einer zu viel.", (u.name,))
                  for u in wand.umrisse[1:]]
    erste = wand.umrisse[0]
    if erste.rechteck is None:
        meldungen.append(Meldung(f"Die Wand {erste.name} {KEIN_RECHTECK} – eine schräge Krone, "
                                 f"etwa die eines Giebels, rechnet das Werkzeug noch nicht.",
                                 (erste.name,)))
    meldungen += [Meldung(f"Die Öffnung {o.name} {KEIN_RECHTECK}.", (o.name,))
                  for o in wand.oeffnungen if o.rechteck is None]
    flaeche = wand.flaeche
    if flaeche is not None and not meldungen:
        meldungen += _oeffnungen(flaeche, wand.oeffnungen)
    return meldungen


def _umriss(u: Umriss) -> Optional[Meldung]:
    """Was an einem Umriss nicht stimmt -- rot, mit seinem Namen."""
    try:
        polygon_pruefen(u.ecken, u.name)
    except GeometrieFehler as fehler:
        return Meldung(str(fehler), (u.name,))
    return None


def _oeffnungen(wand: Rechteck, oeffnungen: Tuple[Oeffnung, ...]) -> List[Meldung]:
    """Was an Öffnungen und Stürzen einer rechteckigen Wand nicht stimmt -- alle sind Rechtecke."""
    meldungen = [Meldung(f"Die Öffnung {o.name} reicht über die Wand hinaus.", (o.name,))
                 for o in oeffnungen if not wand.enthaelt(o.rechteck)]
    meldungen += [Meldung(f"Die Öffnungen {a.name} und {b.name} überschneiden sich.",
                          (a.name, b.name))
                  for a, b in combinations(oeffnungen, 2) if a.rechteck.ueberlappt(b.rechteck)]
    if meldungen:
        return meldungen
    for o in oeffnungen:
        sturz = o.sturzflaeche()
        if not wand.enthaelt(sturz):
            meldungen.append(Meldung(f"Der Sturz über {o.name} reicht über die Wand hinaus: "
                                     f"{_wohin(wand, sturz)}.", (o.name,)))
        meldungen += [Meldung(f"Der Sturz über {o.name} reicht in die Öffnung {x.name}.",
                              (o.name, x.name))
                      for x in oeffnungen if x is not o and sturz.ueberlappt(x.rechteck)]
    meldungen += [Meldung(f"Die Stürze über {a.name} und {b.name} überschneiden sich.",
                          (a.name, b.name))
                  for a, b in combinations(oeffnungen, 2)
                  if a.sturzflaeche().ueberlappt(b.sturzflaeche())]
    return meldungen


def lasten_pruefen(wand: Wand) -> List[Meldung]:
    """
    Je Last, die nicht ganz auf der Wand oder in einer Öffnung liegt, eine
    rote Meldung -- nur für eine Wand, deren Zeichnung rechnet. Auf dem Rand
    einer Öffnung zählt nicht: oben liegt die Last am Sturz, unten auf der
    Brüstung.
    """
    flaeche = wand.flaeche
    meldungen: List[Meldung] = []
    for last in (x for lf in wand.lastfaelle for x in lf.lasten):
        if not flaeche.enthaelt(Rechteck(last.x0, last.y, last.x1, last.y)):
            meldungen.append(Meldung(f"Die Last {last.name} liegt nicht ganz auf der Wand.",
                                     (last.name,)))
            continue
        meldungen += [Meldung(f"Die Last {last.name} liegt in der Öffnung {o.name}.",
                              (last.name, o.name))
                      for o in wand.oeffnungen if _in_oeffnung(last, o.rechteck)]
    return meldungen


def _in_oeffnung(last: Wandlast, r: Rechteck) -> bool:
    """Ob eine Last ins Innere der Öffnung ``r`` reicht -- auf ihrem Rand nicht."""
    if not r.y0 + TOLERANZ < last.y < r.y1 - TOLERANZ:
        return False
    if last.x1 - last.x0 <= TOLERANZ:
        return r.x0 + TOLERANZ < last.x0 < r.x1 - TOLERANZ
    return min(last.x1, r.x1) - max(last.x0, r.x0) > TOLERANZ


def _wohin(wand: Rechteck, sturz: Rechteck) -> str:
    """Wo ein Sturz über die Wand hinaus reicht, als Satzteil: «oben und links»."""
    seiten = [wort for wort, aussen in (("oben", sturz.y1 > wand.y1),
                                        ("links", sturz.x0 < wand.x0),
                                        ("rechts", sturz.x1 > wand.x1)) if aussen]
    return aufgezaehlt(seiten) if seiten else "unten"


def dickenhinweis(sorte: str, t_mm: float) -> Optional[Meldung]:
    """
    Ein Hinweis, wenn ``t_mm`` keine übliche Dicke der Steine der Sorte
    ``sorte`` ist -- ``None``, wenn sie es ist oder die Sorte keine Liste hat.
    """
    dicken = UEBLICHE_DICKEN.get(sorte)
    if dicken is None or any(abs(t_mm - d) < 0.5 for d in dicken):
        return None
    steine = MAUERWERKSSORTEN[sorte].steine
    liste = aufgezaehlt([str(d) for d in dicken], "oder")
    return Meldung(f"{steine} sind meist {liste} mm dick – eine Wand von {t_mm:g} mm ist "
                   f"unüblich.", fehler=False)
