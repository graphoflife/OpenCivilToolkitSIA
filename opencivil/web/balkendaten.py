"""
opencivil/web/balkendaten.py -- was die Oberflaeche von einem Balkensystem zeigt.

VERANTWORTUNG:
Aus dem Befund eines gerechneten Systems, eben oder im Raum
(:class:`~opencivil.stabwerk.rechnung.Systembefund`), die Daten fuer die
Oberflaeche, in den Einheiten der Anzeige -- kN, kNm, mm, mrad, Stellen in m:

* mit jeder Rechnung eine knappe Uebersicht (:func:`uebersicht`): die
  Meldungen mit den Elementen, die sie betreffen, die Knoten ohne
  Drehsteifigkeit, und je Fall die Extremwerte und die Lagerkraefte;
* auf Anfrage die Verlaeufe eines Falls fuer die Bilder (:func:`verlauf`):
  je Stab seine Lage und Proben der Schnittgroessen und der Verschiebung,
  je Knoten seine Verschiebung und Drehung -- oder dass seine Drehung nicht
  bestimmbar ist;
* je Querschnitt sein Umriss fuer das Bildchen in seiner Zeile
  (:func:`umrisse`);
* im Raum je Linie ihre Achsen (:func:`stabachsen`), fuer die gestrichelte
  Faser und die Lasten in den Richtungen des Stabs.

EBEN UND IM RAUM IN EINER FORM:
Was sich unterscheidet -- die Achsen, die Groessen, die Lagerkraefte --,
steht je einmal in einer :class:`Darstellung` (:data:`EBEN`, :data:`RAUM`);
welche gilt, sagt die Art des Befunds. Eine Lage oder Verschiebung ist eine
Liste mit einer Zahl je Achse des Systems -- ``[x, z]`` in der Ebene,
``[x, y, z]`` im Raum --, die Drehung eines Knotens eine Liste mit einer Zahl
je Drehachse. Ein Stab hat seine Achsen im System: ``x`` laengs, ``z`` zur
gestrichelten Faser, im Raum dazu ``y`` (:mod:`opencivil.stabwerk3d.stab`) --
dorthin traegt ein Bild einen positiven Wert auf.

Die Verlaeufe sind gross; mit jeder Rechnung mitgeliefert, machten sie jede
Eingabe langsamer, auch wenn niemand die Bilder ansieht -- dasselbe wie bei
den Diagrammen der Querschnittsanalyse. Gerechnet wird hier nichts, nur
umgerechnet und in Listen gelegt.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from opencivil.core.einheiten import KN, KNM, KN_PRO_M, MM, MRAD
from opencivil.stabwerk.rechnung import Stabwerksrechnung, Systembefund
from opencivil.stabwerk.system import SUMMEN, TOLERANZ, UNBESTIMMT, Fall
from opencivil.stabwerk3d import stab as st3
from opencivil.stabwerk3d.modell import System as Raumsystem
from opencivil.stabwerk3d.rechnung import Raumbefund
from opencivil.web.anzeige import Anzeigegroesse, zahl

#: Wie viele Stuecke ein Stab im Bild mindestens hat -- dazu jede Grenze und jeder Extremwert.
PROBEN_JE_STAB = 24


@dataclass(frozen=True)
class Darstellung:
    """Was eben und im Raum verschieden ist -- die Form der Daten bleibt dieselbe."""

    achsen: Tuple[str, ...]
    """Die Achsen des Systems, in der Folge der Koordinaten."""

    drehachsen: Tuple[Optional[str], ...]
    """
    Um welche Achse sich ein Knoten dreht, in der Folge des Rechenkerns --
    in der Ebene um keine, die einen Namen hat: die Drehung liegt in ihr.
    """

    groessen: Dict[str, Anzeigegroesse]
    """
    Was die Proben eines Stabs je Stelle tragen, ausser ``x`` und der
    Verschiebung -- und wovon die Uebersicht je Stab und Fall den kleinsten
    und den groessten Wert hat.
    """

    schnittgroessen: Tuple[str, ...]
    """Welche der ``groessen`` Schnittgroessen sind -- die Zusammenfassung zeigt sie."""

    durchbiegungen: Tuple[Tuple[str, str], ...]
    """Die Durchbiegungen gegen die Sehne, je mit der Achse des Stabs, in die sie positiv zeigt."""

    lage: Callable[[Any], Dict[str, Any]]
    """Anfang und Achsen eines Stabs im System, aus seinem Verlauf."""

    @property
    def drehungen(self) -> Tuple[str, ...]:
        """Wie die Drehungen eines Knotens heissen: ``φ``, im Raum ``φ_x``, ``φ_y``, ``φ_z``."""
        return tuple("φ" if a is None else f"φ_{a}" for a in self.drehachsen)

    def _lagerwerte(self):
        """
        Je Wert einer Lagerkraft, in der Folge des Rechenkerns, seine
        Groesse, seine Achse und ob er ein Moment ist: erst je Achse eine
        Kraft, dann je Drehachse ein Moment.
        """
        for a in self.achsen:
            yield Anzeigegroesse(f"R_{a}", KN), a, False
        for a in self.drehachsen:
            yield Anzeigegroesse("M" if a is None else f"M_{a}", KNM), a, True

    @property
    def lagerkraefte(self) -> Tuple[Anzeigegroesse, ...]:
        """Die Werte einer Lagerkraft, in der Folge des Rechenkerns."""
        return tuple(g for g, _, _ in self._lagerwerte())

    def als_dict(self) -> Dict[str, Any]:
        """Fuer den Katalog: Namen, Zeichen, Einheiten und Stellen."""
        return {"achsen": list(self.achsen),
                "groessen": {feld: g.als_dict() for feld, g in self.groessen.items()},
                "schnittgroessen": list(self.schnittgroessen),
                "durchbiegungen": [{"feld": feld, "achse": achse}
                                   for feld, achse in self.durchbiegungen],
                "drehungen": list(self.drehungen),
                # Je Wert dazu, wohin er im Bild zeigt: eine Kraft entlang
                # ihrer Achse, ein Moment um seine -- in der Ebene ohne.
                "lagerkraefte": [{**g.als_dict(), "achse": achse, "moment": moment}
                                 for g, achse, moment in self._lagerwerte()]}


def _lage_eben(v: Any) -> Dict[str, Any]:
    # Die gestrichelte Faser liegt rechts des Stabs (Lastrichtung.QUER).
    return {"anfang": [v.x_a, v.z_a], "achsen": {"x": [v.c, v.s], "z": [v.s, -v.c]}}


def _lage_im_raum(v: Any) -> Dict[str, Any]:
    return {"anfang": list(v.anfang), "achsen": dict(zip("xyz", map(list, v.achsen)))}


#: Das 2D-Balkensystem.
EBEN = Darstellung(
    achsen=("x", "z"),
    drehachsen=(None,),
    groessen={"N": Anzeigegroesse("N", KN), "V": Anzeigegroesse("V", KN),
              "M": Anzeigegroesse("M", KNM), "w": Anzeigegroesse("w", MM, stellen=2),
              "phi": Anzeigegroesse("φ", MRAD, r"\varphi", 2)},
    schnittgroessen=("N", "V", "M"),
    durchbiegungen=(("w", "z"),),
    lage=_lage_eben,
)

#: Das 3D-Balkensystem.
RAUM = Darstellung(
    achsen=("x", "y", "z"),
    drehachsen=("x", "y", "z"),
    groessen={**{g: Anzeigegroesse(g, KN) for g in ("N", "V_y", "V_z")},
              **{g: Anzeigegroesse(g, KNM) for g in ("T", "M_y", "M_z")},
              **{g: Anzeigegroesse(g, MM, stellen=2) for g in ("f_y", "f_z")}},
    schnittgroessen=("N", "V_y", "V_z", "T", "M_y", "M_z"),
    durchbiegungen=(("f_y", "y"), ("f_z", "z")),
    lage=_lage_im_raum,
)

#: Welche Darstellung zu welchem Befund gehoert -- nach seiner Klasse.
_DARSTELLUNGEN = {Systembefund: EBEN, Raumbefund: RAUM}


def _darstellung(befund: Systembefund) -> Darstellung:
    return _DARSTELLUNGEN[type(befund)]


def uebersicht(befund: Optional[Systembefund]) -> Dict[str, Any]:
    """
    Was die Oberflaeche nach jeder Rechnung von einem System weiss -- ohne
    die Verlaeufe. Ohne Befund lief es nicht, etwa weil ein Baustoff fehlt.
    """
    if befund is None:
        return {"gerechnet": False}
    e = befund.ergebnis
    d = _darstellung(befund)
    return {
        "gerechnet": True,
        "gueltig": e.gueltig,
        "meldungen": [{"text": m.text, "elemente": list(m.elemente), "fehler": m.fehler}
                      for m in e.meldungen],
        "unbestimmt": e.unbestimmt(),
        "unbestimmt_text": UNBESTIMMT,
        "summen_text": SUMMEN,
        "beweglich": list(e.beweglich),
        "unbekannte": len(e.unbekannte),
        "faelle": [_fall(befund, d, f) for f in e.faelle],
        # Das Eigengewicht je Stab in kN/m -- das Zeichenfenster zeigt es im
        # Lastfall, der es bekommt; gewaehlt und geloescht wird es nicht.
        "eigengewicht": {stab: zahl(g, KN_PRO_M) for stab, g in befund.eigengewicht.items()},
    }


def _fall(befund: Systembefund, d: Darstellung, fall: Fall) -> Dict[str, Any]:
    staebe = {}
    for name, v in befund.verlaeufe(fall.name).items():
        extrem = {}
        for groesse, anzeige in d.groessen.items():
            e = v.extrem(groesse)
            extrem[groesse] = {"kleinst": [e.kleinst[0], anzeige.zahl(e.kleinst[1])],
                               "groesst": [e.groesst[0], anzeige.zahl(e.groesst[1])]}
        staebe[name] = extrem
    return {
        "name": fall.name,
        "kombination": fall.kombination,
        "staebe": staebe,
        # Dieselben Zeilen wie in der Herleitung -- mit den Summen von
        # Linienlager und Bettung, sonst gingen die Kraefte nicht auf.
        "lagerkraefte": [
            {"wo": k.wo, "knoten": k.knoten, "summe": k.summe,
             **{g.zeichen: g.zahl(w) for g, w in zip(d.lagerkraefte, k.werte)}}
            for k in befund.lagerkraefte(fall)],
    }


def verlauf(befund: Systembefund, name: str) -> Dict[str, Any]:
    """Die Bilder eines Falls: je Stab die Proben, je Knoten Verschiebung und Drehung."""
    d = _darstellung(befund)
    fall = befund.ergebnis.fall(name)
    staebe = {}
    for stab, v in befund.verlaeufe(name).items():
        staebe[stab] = {
            "L": v.L, **d.lage(v),
            "proben": [{"x": w["x"], **{g: a.zahl(w[g]) for g, a in d.groessen.items()},
                        "u": [zahl(w[f"u{achse}"], MM) for achse in d.achsen]}
                       for w in v.proben(PROBEN_JE_STAB)],
        }
    unbestimmt = set(befund.ergebnis.unbestimmt())
    n = len(d.achsen)
    knoten = {}
    for ort in befund.ergebnis.orte.values():
        if not ort.knoten:
            continue
        werte = fall.verschiebungen[ort.name]
        offen = ort.knoten in unbestimmt
        knoten[ort.knoten] = {"lage": [getattr(ort, achse) for achse in d.achsen],
                              "u": [zahl(u, MM) for u in werte[:n]],
                              "phi": None if offen else [zahl(p, MRAD) for p in werte[n:]],
                              "unbestimmt": offen}
    return {"fall": name, "kombination": fall.kombination, "staebe": staebe,
            "knoten": knoten, "unbestimmt_text": UNBESTIMMT}


def faelle(befund: Optional[Systembefund]) -> List[str]:
    """Die Namen der gerechneten Faelle, Lastfaelle zuerst."""
    return [f.name for f in befund.ergebnis.faelle] if befund is not None else []


def umrisse(system: Stabwerksrechnung, loesung: Any) -> Dict[str, List[List[List[float]]]]:
    """
    Je Querschnitt eines Systems sein Umriss in mm, fuer das Bildchen in
    seiner Zeile (Benutzer, 2026-10-24) -- ihn kennt jeder Querschnitt selbst
    (:meth:`~opencivil.stabwerk.stabquerschnitt.Stabquerschnitt.umriss`).
    Ein Querschnitt, der nicht geht, hat keinen.
    """
    return {q.kennung: [[[round(y, 1), round(z, 1)] for y, z in p]
                        for p in ([] if q.fehler else q.umriss(loesung))]
            for q in system.querschnitte}


def stabachsen(system: Raumsystem) -> Dict[str, Dict[str, List[float]]]:
    """
    Je Linie eines Systems im Raum ihre Achsen ``x``, ``y`` und ``z`` im
    System -- wie der Rechenkern sie legt (:func:`~opencivil.stabwerk3d.stab.achsen`),
    auch ohne Rechnung. Eine Linie ohne Laenge hat keine.
    """
    knoten = {k.name: k for k in system.knoten}
    heraus = {}
    for s in system.staebe:
        a, b = knoten.get(s.a), knoten.get(s.b)
        if a is None or b is None or math.dist((a.x, a.y, a.z), (b.x, b.y, b.z)) <= TOLERANZ:
            continue
        heraus[s.name] = dict(zip("xyz", map(list, st3.achsen(a, b, s.drehung)[1])))
    return heraus
